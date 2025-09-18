# Copyright (c) 2021-2022 Jaakko Keränen <jaakko.keranen@iki.fi>
# License: BSD-2-Clause

import fnmatch
import hashlib
import importlib
import os.path
import select
import socket
import ipaddress
import multiprocessing as mp
import subprocess
import threading
import queue
import re
import signal
import time
from pathlib import Path
from urllib.parse import urlparse

import OpenSSL.crypto
from OpenSSL import SSL, crypto


class GeminiError(Exception):
    def __init__(self, status, msg):
        Exception.__init__(self, msg)
        self.status = status


class AbortedIOError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


def wait_for_read(stream, timeout):
    fno = stream._socket.fileno()
    r, _, x = select.select([fno], [], [fno], timeout)
    if len(x):
        raise AbortedIOError('recv: socket in error state')
    if len(r) == 0:
        raise socket.timeout('stalled: not ready for reading')


def wait_for_write(stream, timeout):
    fno = stream._socket.fileno()
    _, w, x = select.select([], [fno], [fno], timeout)
    if len(x):
        raise AbortedIOError('send: socket in error state')
    if len(w) == 0:
        raise socket.timeout('stalled: not ready for writing')


def safe_recv(stream, max_len, stall_timeout=10):
    data = bytearray()
    remain = max_len
    while remain > 0:
        try:
            incoming = stream.recv(remain)
            remain -= len(incoming)
            data += bytearray(incoming)

            if len(data):
                # Got something, return it asap.
                break

            # Wait until reading is possible.
            wait_for_read(stream, stall_timeout)

        except OpenSSL.SSL.WantReadError:
            wait_for_read(stream, stall_timeout)
        except OpenSSL.SSL.WantWriteError:
            pass
        except OpenSSL.SSL.WantX509LookupError:
            pass
    return data


def is_bytes(data):
    return type(data) == bytes or type(data) == bytearray


def safe_sendall(stream, data, stall_timeout=30):
    """
    Send data over an SSL connection, accounting for stalls and retries
    required by OpenSSL.

    Args:
        stream (OpenSSL.SSL.Connection): Network stream.
        data (bytes or file-like): Data to sent. If not a bytes/bytearray,
            ``read()`` will be called to get more data.
        stall_timeout (float): Number of seconds to wait until
            terminating a stalled send.
    """
    try:
        BUF_LEN = 32768

        if is_bytes(data):
            streaming = False
        elif isinstance(data, subprocess.Popen):
            streaming = True
            proc = data
            data = proc.stdout
            BUF_LEN = 1
        else:
            streaming = True
            if isinstance(data, Path):
                data = open(data, 'rb')

        # We may need to retry sending with the exact same buffer,
        # so keep it around until successful.
        if streaming:
            send_buf = data.read(BUF_LEN)
        else:
            send_buf = data[:BUF_LEN]

        last_time = time.time()
        pos = 0
        while len(send_buf) > 0:
            try:
                if time.time() - last_time > stall_timeout:
                    raise AbortedIOError('stalled')
                sent = stream.send(send_buf)
                if sent < 0:
                    raise AbortedIOError('failed to send')
                pos += sent
                if streaming:
                    send_buf = send_buf[sent:]
                    if len(send_buf) <= int(BUF_LEN / 2):
                        send_buf += data.read(BUF_LEN)
                else:
                    send_buf = data[pos : pos + BUF_LEN]
                if sent > 0:
                    last_time = time.time()
                else:
                    wait_for_write(stream, stall_timeout)
            except OpenSSL.SSL.WantReadError:
                pass
            except OpenSSL.SSL.WantWriteError:
                # Wait until the socket is ready for writing.
                wait_for_write(stream, stall_timeout)
            except OpenSSL.SSL.WantX509LookupError:
                pass

    finally:
        # Close resources and handles.
        if data and hasattr(data, 'close'):
            data.close()


def safe_close(stream):
    if not stream:
        return
    try:
        stream.shutdown()
    except Exception as er:
        print('stream shutdown error:', er)
    try:
        stream.close()
    except Exception as er:
        print('stream close error:', er)


def report_error(stream, code, msg):
    print(time.strftime('%Y-%m-%d %H:%M:%S'), f'   ', '--', code, msg)
    #stream.sendall(f'{code} {msg}\r\n'.encode('utf-8'))
    safe_sendall(stream, f'{code} {msg}\r\n'.encode('utf-8'))
    safe_close(stream)


def cert_subject(cert):
    comps = {}
    for name, value in cert.get_subject().get_components():
        comps[name.decode()] = value.decode()
    return comps

def cert_issuer(cert):
    comps = {}
    for name, value in cert.get_issuer().get_components():
        comps[name.decode()] = value.decode()
    return comps


class Identity:
    """
    Client certificate.

    SHA-256 hashes are calculated automatically for the whole certificate and
    just for the public key.

    Attributes:
        cert (bytes): Certificate (DER format).
        pubkey (bytes): Public key (DER format).
        fp_cert (str): SHA-256 hash of the certificate.
        fp_pubkey (str): SHA-256 hash of the public key.
    """
    def __init__(self, cert):
        self._subject = cert_subject(cert)
        self._issuer = cert_issuer(cert)
        self.cert = crypto.dump_certificate(crypto.FILETYPE_ASN1, cert)
        m = hashlib.sha256()
        m.update(self.cert)
        self.fp_cert = m.hexdigest()
        self.pubkey = crypto.dump_publickey(crypto.FILETYPE_ASN1, cert.get_pubkey())
        m = hashlib.sha256()
        m.update(self.pubkey)
        self.fp_pubkey = m.hexdigest()

    def __str__(self):
        return f"{self.fp_cert};{self.fp_pubkey}"

    def subject(self):
        """
        Returns:
            dict: Name components of the certificate subject, e.g.: ``{'CN': 'Name'}``.
        """
        return self._subject

    def issuer(self):
        """
        Returns:
            dict: Name components of the certificate issuer, e.g.: ``{'CN': 'Name'}``.
        """
        return self._issuer


class Request:
    """
    Request received from a client.

    Request objects are used to pass information to entry points handlers.
    One does not need to construct them directly.

    Attributes:
        remote_address (str): IP address of the client.
        scheme (str): Request protocol scheme. Either ``gemini`` or ``titan``.
        identity (gmcapsule.gemini.Identity): Client certificate.
            May be ``None``.
        hostname (str): Hostname.
        path (str): URL path. Always begins with a ``/``.
        query (str): Encoded query string. You can use `urllib.parse.unquote()
            <https://docs.python.org/3/library/urllib.parse.html#urllib.parse.unquote>`_
            to decode the percent-coding. ``None`` if the URL does not have a query
            string.
        content_token (str): Encoded token specified in Titan URLs.
            May be ``None``.
        content_mime (str): MIME type specified in Titan URls. May be ``None``.
        content (bytes): Content uploaded by the client in a Titan request.
            May be ``None``.
        is_titan_edit (bool): Is this a Titan edit request? Handler may need to
            activate an edit lock.
    """
    def __init__(self, identity=None, scheme='gemini', hostname='', path='', query=None,
                 remote_address=None, content_token=None, content_mime=None, content=None,
                 worker_id=None, is_titan_edit=False):
        self.remote_address = remote_address
        self.scheme = scheme
        self.identity = identity
        self.hostname = hostname
        self.path = path
        self.query = query
        self.content_token = content_token
        self.content_mime = content_mime
        self.content = content
        self.worker_id = worker_id
        self.is_titan_edit = is_titan_edit

    def url(self):
        return f'{self.scheme}://{self.hostname}{self.path}{"?" + self.query if self.query else ""}'


def verify_callback(connection, cert, err_num, err_depth, ret_code):
    #print("verify_callback:", connection, cert, ret_code)
    return True


class Cache:
    """
    Response cache base class.

    Derived classes are expected to override the save() and try_load()
    methods to save and load response content as appropriate.

    The server will not try to load or save cached content when a request
    includes a query string or a client certificate is provided. When multiple
    Cache objects have been installed, the save/load operation is attempted
    on each in turn until one cache succeeds in saving or loading content.

    Each server worker thread constructs their own Cache objects. If there
    is a shared backing store like a file system or a database, proper care
    should be taken to synchronize access to it from the Cache objects.

    The mapping from URLs to cache paths is::

        gemini://example.com/path/file.gmi
         ↓
        /example.com/path/file.gmi

    """

    def __init__(self):
        pass

    def save(self, path, media_type, content):
        """
        Save content to the cache.

        Args:
            path (str): URL path being loaded with the hostname prepended as
                the top-level directory.
            media_type (str): MIME type, e.g., "text/plain".
            content (bytes): Content to save.

        Returns:
            bool: True if successfully saved.
        """
        return False

    def try_load(self, path):
        """
        Load content from the cache.

        Args:
            path (str): URL path being loaded with the hostname prepended as
                the top-level directory.

        Returns:
            tuple(str, bytes): Content MIME type and data. Returns
            (None, None) if nothing is cached for the given path.
        """
        return None, None


def handle_gemini_or_titan_request(request_data):
    worker = request_data.worker
    stream = request_data.stream
    data = request_data.buffered_data
    from_addr = request_data.from_addr
    identity = request_data.identity
    request = request_data.request
    expected_size = None
    req_token = None
    req_mime = None
    is_titan_edit = False

    if request.startswith('titan:'):
        if identity is None and worker.cfg.require_upload_identity():
            report_error(stream, 60, "Client certificate required for upload")
            return
        # Read the rest of the data.
        url = urlparse(request)
        parms = url.path.split(';')
        if len(parms) > 1:
            # all parameters are removed from the request URL
            request = request[:request.index(';')]
            if len(url.query):
                request += '?' + url.query
            parms = parms[1:]
            for p in parms:
                if p.startswith('size='):
                    expected_size = int(p[5:])
                elif p.startswith('token='):
                    req_token = p[6:]
                elif p.startswith('mime='):
                    req_mime = p[5:]
                elif p == 'edit':
                    if len(parms) > 1:
                        report_error(stream, 59, "Too many parameters")
                    # Handle this like it was a Gemini request for the specified resource.
                    is_titan_edit = True
                    request = 'gemini' + request[5:]
                else:
                    report_error(stream, 59, "Invalid parameter")

        if not is_titan_edit:
            if expected_size is None:
                report_error(stream, 59, "Unspecified content length") # Size is required.

            worker.log(f'Receiving Titan content: {expected_size}')
            max_upload_size = worker.cfg.max_upload_size()
            if expected_size > max_upload_size and max_upload_size > 0:
                report_error(stream, 59, "Maximum content length exceeded")
                return
            if not request_data.receive_data(expected_size):
                report_error(stream, 59, "Invalid content length")
                return
            data = request_data.buffered_data
        else:
            # Edit requests do not contain data.
            if len(data):
                report_error(stream, 59, "Bad request")
                return
    else:
        # No Payload in Gemini.
        if len(data):
            report_error(stream, 59, "Bad request")
            return

    url = urlparse(request)
    path = url.path
    if path == '':
        path = '/'
    hostname = url.hostname

    if url.port != None and url.port != worker.port:
        report_error(stream, 59, "Invalid port number")
        return
    if not stream.get_servername():
        # The hostname may be a literal IPv4/IPv6 address.
        try:
            ipaddress.ip_address(hostname)
            # No error during parsing, looks like a literal address.
        except ValueError:
            # Server name indication is required.
            report_error(stream, 59, "Missing TLS server name indication")
            return
    else:
        sni_name = stream.get_servername().decode()
        if sni_name != hostname:
            # SNI servername does not match the hostname in the URL. Misbehaving client?
            report_error(stream, 53, "Proxy request refused")
            return
        if sni_name not in worker.cfg.hostnames():
            report_error(stream, 53, f"Proxy request refused (domain \"{sni_name}\")")
            return

    try:
        status, meta, body, from_cache = worker.context.call_entrypoint(Request(
            identity,
            remote_address=from_addr,
            scheme=url.scheme,
            hostname=hostname,
            path=path,
            query=url.query if '?' in request else None,
            content_token=req_token,
            content_mime=req_mime,
            content=data if len(data) else None,
            worker_id=request_data.worker.id,
            is_titan_edit=is_titan_edit
        ))

        output = f'{status} {meta}\r\n'.encode('utf-8')
        if is_bytes(body):
            safe_sendall(stream, output + body)
        else:
            # `body` is some sort of streamable data, cannot send in one call.
            safe_sendall(stream, output)
            safe_sendall(stream, body)

        # Save to cache.
        if not from_cache and status == 20 and is_bytes(body):
            for cache in worker.context.caches:
                if cache.save(hostname + path, meta, body):
                    break

    except GeminiError as error:
        report_error(stream, error.status, str(error))
        return


def unpack_response(response):
    if type(response) == tuple:
        if len(response) == 2:
            status, meta = response
            response = ''
        else:
            status, meta, response = response
    else:
        status = 20
        meta = 'text/gemini; charset=utf-8'

    if response == None:
        body = b''
    elif type(response) == str:
        body = response.encode('utf-8')
    else:
        body = response

    return status, meta, body


class Context:
    def __init__(self, cfg, allow_extension_workers=False, handler_queue=None,
                 response_queues=None):
        self.cfg = cfg
        self.is_quiet = True
        self.allow_extension_workers = allow_extension_workers
        if allow_extension_workers:
            self.shutdown = threading.Event()
        self.hostnames = cfg.hostnames()
        self.entrypoints = {'gemini': {}, 'titan': {}}
        for proto in ['gemini', 'titan']:
            self.entrypoints[proto] = {}
            for hostname in self.hostnames:
                self.entrypoints[proto][hostname] = []
        self.caches = []
        self.protocols = {}
        self.add_protocol('gemini', handle_gemini_or_titan_request)
        self.add_protocol('titan', handle_gemini_or_titan_request)
        # Queue for pending handler jobs.
        self.job_lock = threading.Lock()
        self.job_id = 0
        self.handler_queue = handler_queue
        self.response_queues = response_queues

    def config(self):
        return self.cfg

    def is_background_work_allowed(self):
        """
        Determines whether extension modules are allowed to start workers.
        """
        return self.allow_extension_workers

    def shutdown_event(self):
        """
        Returns:
            threading.Event: Extension modules must check this to be notified
            when the server is being shut down.
        """
        if not self.is_background_work_allowed():
            raise Exception("background work not allowed")
        # This is used in a parser thread that is allowed to launch workers.
        return self.shutdown

    def set_quiet(self, is_quiet):
        self.is_quiet = is_quiet

    def print(self, *args):
        if not self.is_quiet:
            print(*args)

    def add_entrypoint(self, protocol, hostname, path_pattern, entrypoint):
        self.entrypoints[protocol][hostname].append((path_pattern, entrypoint))

    def __setitem__(self, key, value):
        for hostname in self.hostnames:
            self.add_entrypoint('gemini', hostname, key, value)

    def add_cache(self, cache):
        """
        Install a cache.

        All installed caches will attempt to save and load content until one
        succeeds. The caches installed first get precedence.

        Args:
            cache (Cache): Cache instance.
        """
        self.caches.append(cache)

    def add_protocol(self, scheme, handler):
        """
        Registers a new protocol handler.

        Args:
            scheme (str): URL scheme of the protocol.
            handler (callable): Handler to be called when a request with the
                specified scheme is received. The handler must return the
                response to be sent to the client (bytes).
        """
        self.protocols[scheme] = handler

    def add(self, path, entrypoint, hostname=None, protocol='gemini'):
        """
        Register a URL entry point.

        Extension modules must call this to become visible in the server's
        path hierarchy. Entry points are looked up in the order the modules
        were loaded, with earlier modules getting precedence.

        Args:
            path (str): URL path. Must begin with a slash (``/``). Asterisk
                wildcards (``*``) are supported. Note that if the path
                ``/*`` is registered, it will match any requested URL.
            entrypoint (callable): Function or other callable object that
                gets called when a request is processed with a matching
                URL path. A :class:`~gmcapsule.gemini.Request` is passed in as the
                only argument.
            hostname (str): Hostname for the entry point. If omitted,
                the entry point applies to all configured hostnames.
            protocol (str): Protocol for the entry point.
        """
        if hostname:
            self.add_entrypoint(protocol, hostname, path, entrypoint)
        else:
            for hostname in self.cfg.hostnames():
                if not hostname:
                    raise Exception(f'invalid hostname: "{hostname}"')
                self.add_entrypoint(protocol, hostname, path, entrypoint)

    def load_modules(self):
        # The configuration can override default priorities.
        mod_priority = {}
        if 'priority' in self.cfg.ini:
            for name, priority in self.cfg.section('priority').items():
                mod_priority[name] = int(priority)

        # We will load all recognized modules.
        name_pattern = re.compile(r'([0-9][0-9])_(.*)\.py')
        dirs = []
        for user_dir in self.cfg.mod_dirs():
            if user_dir not in dirs:
                dirs.append(user_dir)
        dirs += [Path(__file__).parent.resolve() / 'modules']
        mods = []
        for mdir in dirs:
            for mod_file in sorted(os.listdir(mdir)):
                m = name_pattern.match(mod_file)
                if m:
                    path = (mdir / mod_file).resolve()
                    name = m.group(2)
                    loader = importlib.machinery.SourceFileLoader(name, str(path))
                    spec = importlib.util.spec_from_loader(name, loader)
                    mod = importlib.util.module_from_spec(spec)
                    loader.exec_module(mod)
                    if name in mod_priority:
                        priority = mod_priority[name]
                    else:
                        priority = int(m.group(1))
                    mods.append((priority, name, mod))

        # Initialize in priority order.
        for _, name, mod in sorted(mods):
            self.print(f'Init:', mod.__doc__ if mod.__doc__ else name)
            mod.init(self)

    def find_entrypoint(self, protocol, hostname, path):
        try:
            for entry in self.entrypoints[protocol][hostname]:
                path_pattern, handler = entry
                if handler != None:
                    # A path string, possibly with wildcards.
                    if len(path_pattern) == 0 or fnmatch.fnmatch(path, path_pattern):
                        return handler
                else:
                    # A callable generic path matcher.
                    handler = path_pattern(path)
                    if handler:
                        return handler
        except Exception as x:
            print(x)
            return None

        return None

    def call_entrypoint(self, request):
        """
        Calls the registered entry point for a request.

        Args:
            request (Request): Request object.

        Returns:
            tuple: (status, meta, body, cache). The type of body can be bytes,
            bytearray, or pathlib.Path. Returning a pathlib.Path means that
            the body will be read from the referenced file. The cache is None
            if the data was not read from a cache.
        """
        entrypoint = self.find_entrypoint(request.scheme, request.hostname, request.path)

        caches = self.caches if (request.scheme == 'gemini' and
                                 not request.identity and
                                 not request.query) else []
        from_cache = None

        if entrypoint:
            # Check the caches first.
            for cache in caches:
                media, content = cache.try_load(request.hostname + request.path)
                if not media is None:
                    if hasattr(content, '__len__'):
                        self.print('%d bytes from cache, %s' % (len(content), media))
                    else:
                        self.print('stream from cache,', media)
                    return 20, media, content, cache

            # Process the request normally if there is nothing cached.
            if not from_cache:
                try:
                    if not self.handler_queue:
                        # Handle in the same thread/process synchronously. This is probably
                        # running under a RequestHandler process.
                        response = entrypoint(request)
                    else:
                        # Put it in the handler queue and wait for completion. Parser threads use
                        # this to hand work off to the handler processes.
                        with self.job_lock:
                            # The job ID is for verifying we are getting the right response.
                            self.job_id += 1
                            job_id = self.job_id

                        self.handler_queue.put((job_id, request, request.worker_id))
                        result_id, response = self.response_queues[request.worker_id].get()

                        if result_id != job_id:
                            raise Exception('response queue out of sync: request handler returned wrong job ID')
                        if isinstance(response, Exception):
                            raise response

                    status, meta, body = unpack_response(response)

                    return status, meta, body, None

                except Exception as x:
                    import traceback
                    traceback.print_exception(x)
                    raise GeminiError(40, 'Temporary failure')

        raise GeminiError(50, 'Permanent failure')


class RequestData:
    """Encapsules data about an incoming request, before it has been fully parsed."""

    def __init__(self, worker, stream, buffered_data, from_addr, identity, request):
        self.worker = worker
        self.stream = stream
        self.buffered_data = buffered_data
        self.from_addr = from_addr
        self.identity = identity
        self.request = request

    def receive_data(self, expected_size):
        while len(self.buffered_data) < expected_size:
            incoming = safe_recv(self.stream, 65536)
            if len(incoming) == 0:
                break
            self.buffered_data += incoming
        if len(self.buffered_data) != expected_size:
            return False
        return True


class RequestParser(threading.Thread):
    """Thread that parses incoming requests from clients."""

    def __init__(self, id, context, job_queue):
        super().__init__()
        self.id = id
        self.context = context
        self.cfg = context.cfg
        self.port = self.cfg.port()
        self.jobs = job_queue

    def run(self):
        try:
            while True:
                stream, from_addr = self.jobs.get()
                if stream is None:
                    break
                try:
                    self.process_request(stream, from_addr)
                except OpenSSL.SSL.SysCallError as error:
                    self.log(f'OpenSSL error: ' + str(error))
                except AbortedIOError as error:
                    self.log(f'Send aborted: ' + str(error))
                except Exception as error:
                    self.log(f'Problem: ' + str(error))
                    # Some unexpected problem...
                    #import traceback
                    #traceback.print_exc()
                    # try:
                    #     report_error(stream, 42, str(error))
                    # except:
                    #     pass
                safe_close(stream)
                stream, from_addr = None, None
        except KeyboardInterrupt:
            pass

    def log(self, *args):
        print(time.strftime('%Y-%m-%d %H:%M:%S'), f'[{self.id}]', '--', *args)

    def process_request(self, stream, from_addr):
        data = bytes()
        MAX_LEN = 1024          # applies only to Gemini and Titan
        MAX_RECV = MAX_LEN + 2  # includes terminator "\r\n"
        MAX_RECV_ANY_PROTOCOL = 65536
        request = None
        incoming = safe_recv(stream, MAX_RECV)

        def is_gemini_based(data):
            return data.startswith(b'gemini:') or data.startswith(b'titan:')

        if not is_gemini_based(data):
            MAX_RECV = MAX_RECV_ANY_PROTOCOL

        try:
            while len(data) < MAX_RECV:
                data += incoming
                crlf_pos = data.find(b'\r\n')
                if crlf_pos >= 0:
                    request = data[:crlf_pos].decode('utf-8')
                    data = data[crlf_pos + 2:]
                    break
                elif len(data) > MAX_LEN and is_gemini_based(data):
                    # At this point we should have received the line terminator.
                    self.log(from_addr, 'sent a malformed request')
                    report_error(stream, 59, "Request exceeds maximum length")
                    return
                incoming = safe_recv(stream, MAX_RECV - len(data))
                if len(incoming) <= 0:
                    break
        except UnicodeDecodeError:
            report_error(stream, 59, "Request contains malformed UTF-8")
            return

        if not request or len(data) > MAX_RECV:
            report_error(stream, 59, "Bad request")
            return

        cl_cert = stream.get_peer_certificate()
        identity = Identity(cl_cert) if cl_cert else None

        for scheme, handler in self.context.protocols.items():
            if request.startswith(scheme + ':'):
                self.log(request)
                response = handler(RequestData(self, stream, data, from_addr, identity, request))
                if not response is None:
                    safe_sendall(stream, response)
                return

        report_error(stream, 59, "Unsupported protocol")


class ServerRestarter:
    def __init__(self, server):
        self.server = server

    def __call__(self, signum, frame):
        if signum == signal.SIGHUP:
            print('--- SIGHUP ---')
            self.server.restart_workers()


class RequestHandler(mp.Process):
    def __init__(self, id, cfg, job_queue, result_queues):
        super().__init__(target=RequestHandler._run, args=(self,))
        self.id = id
        self.cfg = cfg
        self.jobs = job_queue
        self.results = result_queues
        self.context = None

    def _run(self):
        self.context = Context(self.cfg)
        self.context.load_modules()
        self.context.set_quiet(False)

        # Wait for request processing jobs.
        try:
            while True:
                job_id, request, queue_id = self.jobs.get()
                if job_id is None:
                    break
                result_queue = self.results[queue_id]
                entrypoint = self.context.find_entrypoint(request.scheme, request.hostname, request.path)
                if not entrypoint:
                    result_queue.put((job_id, Exception("Missing entrypoint: " + request.url())))
                    continue
                try:
                    response = unpack_response(entrypoint(request))
                    result_queue.put((job_id, response))

                except Exception as error:
                    result_queue.put((job_id, error))

        except KeyboardInterrupt:
            pass


class Server:
    def __init__(self, cfg):
        mp.set_start_method('spawn')

        self.cfg     = cfg
        self.address = cfg.address()
        self.port    = cfg.port()

        self.main_context = None
        self.contexts     = {}
        session_id = f'GmCapsule:{cfg.port()}'.encode('utf-8')

        for host in cfg.hostnames():
            ctx = SSL.Context(SSL.TLS_SERVER_METHOD)
            ctx.set_verify(SSL.VERIFY_PEER, verify_callback)
            ctx.set_session_id(session_id)
            self.contexts[host] = ctx

            if not self.main_context:
                self.main_context = ctx

            keys_found = False

            # Try the domain-specific certificates first.
            cert_path = cfg.certs_dir() / host / 'cert.pem'
            key_path  = cfg.certs_dir() / host / 'key.pem'
            if cert_path.exists() and key_path.exists():
                print(f'Host "{host}": Using certificate {cert_path}')
                ctx.use_certificate_file(str(cert_path))
                ctx.use_privatekey_file(str(key_path))
                keys_found = True

            if not keys_found:
                cert_path = cfg.certs_dir() / 'cert.pem'
                key_path  = cfg.certs_dir() / 'key.pem'
                if os.path.exists(cert_path) and os.path.exists(key_path):
                    print(f'Host "{host}": Using default certificate {cert_path}')
                    ctx.use_certificate_file(str(cert_path))
                    ctx.use_privatekey_file(str(key_path))
                    keys_found = True

            if not keys_found:
                raise Exception(f"certificate not found for host '{host}'; check {str(cfg.certs_dir())}")

        def _select_ssl_context(conn):
            name = conn.get_servername().decode('utf-8')
            ctx = self.main_context
            if name in self.contexts:
                ctx = self.contexts[name]
            conn.set_context(ctx)

        self.main_context.set_tlsext_servername_callback(_select_ssl_context)

        # Spawn the worker threads.
        self.parser_queue = queue.Queue()
        self.handler_queue = mp.Queue()
        self.init_parser_context()
        self.parsers = []
        self.handlers = []
        self.create_workers(cfg)

        self.sock = None
        self.sv_conn = None

    def run(self):
        attempts = 60
        print(f'Opening port {self.port}...')
        while True:
            try:
                self.sock = socket.socket()
                self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.sock.bind((self.address, self.port))
                self.sock.listen(5)
                self.sv_conn = SSL.Connection(self.main_context, self.sock)
                self.sv_conn.set_accept_state()
                break
            except:
                attempts -= 1
                if attempts == 0:
                    raise Exception(f'Failed to open port {self.port} for listening')
                time.sleep(2.0)
                print('...')
        print(f'Server started on port {self.port}')

        self.start_workers()

        try:
            signal.signal(signal.SIGHUP, ServerRestarter(self))
        except AttributeError:
            print('Restarting with SIGHUP not supported')

        while True:
            stream = None
            try:
                stream, from_addr = self.sv_conn.accept()
                stream._socket.settimeout(10)
                self.parser_queue.put((stream, from_addr))
                del stream
                del from_addr
            except KeyboardInterrupt:
                print('\nStopping the server...')
                break
            except Exception as ex:
                #import traceback
                #traceback.print_exc()
                print(ex)

        # Close the server socket.
        self.sv_conn = None
        self.sock.close()
        self.sock = None

        # Stop all workers.
        self.stop_workers()

        print('Done')

    def init_parser_context(self):
        self.handler_results = []
        if self.is_using_handler_processes():
            for _ in range(max(self.cfg.num_threads(), 1)):
                # Handler processes put results in these queues.
                self.handler_results.append(mp.Queue())
        self.parser_context = Context(self.cfg,
                                      allow_extension_workers=True,
                                      handler_queue=self.handler_queue if self.is_using_handler_processes() else None,
                                      response_queues=self.handler_results if self.is_using_handler_processes() else None)
        self.parser_context.set_quiet(False)
        self.parser_context.load_modules()

    def restart_workers(self):
        """
        Restarts workers with an updated configuration. The server socket or
        TLS configuration are not modified, even if the values have changed
        in the configuration file.
        """
        self.stop_workers()
        self.cfg.reload()
        self.init_parser_context()
        self.create_workers(self.cfg)
        self.start_workers()

    def is_using_handler_processes(self):
        return self.cfg.num_processes() > 0

    def create_workers(self, cfg):
        for proc_id in range(max(cfg.num_processes(), 0)):
            proc = RequestHandler(proc_id, cfg, self.handler_queue, self.handler_results)
            self.handlers.append(proc)

        for parser_id in range(max(cfg.num_threads(), 1)):
            # Threads share one context (note: GIL).
            parser = RequestParser(parser_id, self.parser_context, self.parser_queue)
            self.parsers.append(parser)

    def start_workers(self):
        for handler in self.handlers:
            handler.start()
        for parser in self.parsers:
            parser.start()

        print(len(self.parsers), 'parser(s) and', len(self.handlers), 'handler(s) started')

    def stop_workers(self):
        self.parser_context.shutdown.set()

        # Stop parsers first so all ongoing handler processes get to finish, and no new
        # requests can come in.
        for _ in range(len(self.parsers)):
            self.parser_queue.put((None, None))
        for _ in range(len(self.handlers)):
            self.handler_queue.put((None, None, None))

        for p in self.parsers:
            p.join()
        for h in self.handlers:
            h.join()

        print(len(self.parsers), 'parser(s) and', len(self.handlers), 'handler(s) stopped')
        self.parsers = []
        self.handlers = []
        self.parser_context.shutdown.clear()
