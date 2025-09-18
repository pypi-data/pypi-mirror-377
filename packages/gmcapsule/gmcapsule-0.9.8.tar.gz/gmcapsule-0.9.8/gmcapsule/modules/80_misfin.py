# Copyright (c) 2024 Jaakko Keränen <jaakko.keranen@iki.fi>
# License: BSD-2-Clause

"""Misfin-to-Email Forwarding"""

import gmcapsule
import hashlib
import re
import subprocess
from pathlib import Path
from OpenSSL import SSL, crypto


CHECK_NOTFOUND, CHECK_FOUND, CHECK_MISMATCH = range(3)


def get_fingerprint(x509_cert):
    h = hashlib.sha256()
    h.update(crypto.dump_certificate(crypto.FILETYPE_ASN1, x509_cert))
    return h.hexdigest()


class Identity:
    def __init__(self, cert):
        self.cert = cert
        self.fingerprint = get_fingerprint(cert)

        host = None
        comps = {}
        for (comp, value) in cert.get_subject().get_components():
            comps[comp.decode('utf-8')] = value.decode('utf-8')
        i = 0
        while i < cert.get_extension_count():
            ext = cert.get_extension(i)
            if ext.get_short_name() == b'subjectAltName':
                host = str(ext)
                if not host.startswith('DNS:'):
                    raise Exception(f"{cert}: subject alternative name must specify a DNS hostname")
                host = host[4:]
                # Remove additional DNS names.
                if ', ' in host:
                    host = host[:host.index(', ')]
                break
            i += 1
        if not host:
            raise Exception(f"{cert}: subject alternative name not specified")

        self.uid = comps['UID']
        self.host = host
        self.blurb = comps['CN']

    def address(self):
        return f'{self.uid}@{self.host}'


def check_file(path, ident):
    try:
        address = ident.address()
        for line in open(path, 'rt').readlines():
            m = re.match(r'([0-9a-f]{64}) ([^\s]+) .*', line)
            if m:
                if m[1] == ident.fingerprint:
                    return True
                if m[2] == address:
                    return CHECK_FOUND if m[1] == ident.fingerprint else CHECK_MISMATCH
    except FileNotFoundError:
        pass
    return CHECK_NOTFOUND


def append_file(path, ident):
    print(f"{ident.fingerprint} {ident.address()} {ident.blurb}",
          file=open(path, 'at'))


class Recipient:
    # Note: Generating a recipient certificate:
    # openssl req -x509 -key misfin.key -outform PEM -out misfin.pem -sha256 -days 100000 -addext 'subjectAltName=DNS:example.com' -subj '/CN=blurb/UID=mailbox'

    def __init__(self, name, cert, key, email):
        self.name = name
        self.email = email

        if not cert:
            raise Exception(self.name + ': recipient certificate not specified')
        if not key:
            raise Exception(self.name + ': recipient private key not specified')

        self.cert = crypto.load_certificate(crypto.FILETYPE_PEM, open(cert, 'rb').read())
        self.key = crypto.load_privatekey(crypto.FILETYPE_PEM, open(key, 'rb').read())

        if not self.cert:
            raise Exception(cert + ": invalid certificate")
        if not self.key:
            raise Exception(key + ": invalid private key")

        self.fingerprint = get_fingerprint(self.cert)

        self.ident = Identity(self.cert)
        if self.ident.uid != self.name:
            raise Exception(f"{cert}: certificate user ID must match mailbox name ({name})")


class MisfinError (Exception):
    def __init__(self, status, meta):
        self.status = status
        self.meta = meta

    def __str__(self):
        return f'{self.status} {self.meta}'


class MisfinHandler:
    def __init__(self, context):
        cfg = context.config().section('misfin')

        self.context = context
        self.email_cmd = cfg.get('email.cmd', fallback='/usr/sbin/sendmail')
        self.email_from = cfg.get('email.from', fallback=None)
        self.email_uriformat = cfg.getint('email.uriformat', fallback=0)
        self.trust_file = Path.home() / '.misfin-known-senders'
        self.reject = cfg.get('reject', fallback='').split()
        self.always_trust = set()
        self.recipients = {}

        # Configure.
        cfg = context.config()
        for section in cfg.prefixed_sections('misfin.').values():
            name = section.name[7:]
            cert = section.get('cert', fallback=None)
            key = section.get('key', fallback=None)
            email = section.get('email', fallback=None)
            if not email:
                raise Exception("Misfin recipients must have an email forwarding address")
            recp = Recipient(name, cert, key, email)
            self.always_trust.add(recp.fingerprint)
            self.recipients[name] = recp

    def check_sender(self, sender: Identity):
        fp = sender.fingerprint

        if fp in self.always_trust:
            return True
        if fp in self.reject:
            return False

        if re.search(r'\s', sender.uid):
            raise MisfinError(62, 'Invalid sender mailbox')
        if re.search(r'\s', sender.host):
            raise MisfinError(62, 'Invalid sender hostname')

        result = check_file(self.trust_file, sender)
        if result == CHECK_FOUND:
            return True
        elif result == CHECK_MISMATCH:
            raise MisfinError(63, 'Certificate does not match known identity')

        # TODO: Never seen this before, so verify by asking the sender first if this
        # is a valid/live mailbox.

        # TOFU.
        append_file(self.trust_file, sender)

        return True

    def __call__(self, request_data):
        try:
            if not request_data.identity:
                raise MisfinError(60, 'Certificate required')
            try:
                sender = Identity(crypto.load_certificate(crypto.FILETYPE_ASN1,
                                                          request_data.identity.cert))
            except:
                raise MisfinError(62, 'Invalid Misfin certificate')
            request = request_data.request

            # Parse the request, first trying Misfin(B).
            m = re.match(r'misfin://([^@]+)@([^@\s]+) (.*)', request, re.DOTALL)
            if m:
                message = m[3]
            else:
                # Perhaps Misfin(C), then.
                m = re.match(r'misfin://([^@]+)@([^@\s]+)\t(\d+)', request)
                if not m:
                    raise MisfinError(59, "Bad request")
                if not request_data.receive_data(int(m[3])):
                    raise MisfinError(59, 'Invalid content length')
                message = request_data.buffered_data.decode('utf-8')
            is_empty_message = len(message.strip()) == 0
            mailbox = m[1]
            host = m[2]
            if ':' in host:
                # Not interested in the port number.
                host = host[:host.index(':')]

            if mailbox not in self.recipients:
                raise MisfinError(51, 'Mailbox not found')

            recp = self.recipients[mailbox]

            if host != recp.ident.host:
                raise MisfinError(53, 'Domain not serviced')

            resp_status = 20
            resp_meta   = recp.fingerprint

            if not is_empty_message:
                # If we've seen this before, check that the fingerprint is the same.
                if not self.check_sender(sender):
                    raise MisfinError(61, 'Unauthorized sender')

                # Forward as email.
                try:
                    subject = f"[misfin] Message from {sender.address()}"

                    scheme = "misfin:" if self.email_uriformat == 0 else "misfin://"

                    msg = f'From: {self.email_from}\n' + \
                        f'To: {recp.email}\n' + \
                        f'Subject: {subject}\n\n' + \
                        message.rstrip() + "\n\n" + \
                            f"=> {scheme}{sender.address()} {sender.blurb}\n"

                    args = [self.email_cmd, '-i', recp.email]
                    if self.email_cmd == 'stdout':
                        print(args, msg)
                    else:
                        subprocess.check_output(args, input=msg, encoding='utf-8')
                except Exception as x:
                    self.context.print('[misfin] Error sending email:', x)
                    raise MisfinError(42, 'Internal error')
            else:
                self.context.print(f'[misfin] Fingerprint queried by {sender.address()}')

        except MisfinError as er:
            resp_status = er.status
            resp_meta = er.meta

        except Exception as er:
            self.context.print('[misfin] Unexpected error:', er)
            resp_status = 42
            resp_meta = 'CGI error'

        return f'{resp_status} {resp_meta}\r\n'.encode('utf-8')


def init(context):
    if context.config().prefixed_sections('misfin.').values():
        context.add_protocol('misfin', MisfinHandler(context))
