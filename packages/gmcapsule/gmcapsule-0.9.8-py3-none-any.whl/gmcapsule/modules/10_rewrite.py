# Copyright (c) 2023 Jaakko Keränen <jaakko.keranen@iki.fi>
# License: BSD-2-Clause

"""Rewriter"""

import re


class PathRewriteHandler:
    def __init__(self, context, rewritten_path):
        self.context = context
        self.rewritten_path = rewritten_path

    def __call__(self, req):
        old_path = req.path
        req.path = self.rewritten_path

        # Don't allow rewriting the same request too many times.
        if hasattr(req, 'num_rewrites'):
            req.num_rewrites += 1
        else:
            req.num_rewrites = 1
        if req.num_rewrites == 100:
            return 40, "Stuck in rewrite loop: " + req.url()

        self.context.print("[rewrite]", old_path, "->", req.path)
        status, meta, path, _ = self.context.call_entrypoint(req)

        return (status, meta, path)


class Responder:
    def __init__(self, code, meta):
        self.code = code
        self.meta = meta

    def __call__(self, req):
        meta = self.meta.replace('${QUERY_STRING}', f'?{req.query}' if req.query != None else '')
        return self.code, meta


class Rewriter:
    def __init__(self, context, protocol, host, src_path, dst_path, status):
        self.context = context
        self.protocol = protocol
        self.host = host
        self.src_path = src_path
        self.dst_path = dst_path
        self.status = status

    def __call__(self, path):
        # If path matches a rewritten URL, return the handler object that calls the
        # correct handler for the updated URL.
        if self.dst_path:
            new_path = self.src_path.sub(self.dst_path, path)
            if new_path != path:
                return PathRewriteHandler(self.context, new_path)

        elif self.status:
            m = self.src_path.match(path)
            if m:
                status = self.status
                for i in range(self.src_path.groups + 1):
                    cap = m[i]
                    if cap:
                        status = status.replace(f'\\{i}', cap)
                code, meta = status.split()
                self.context.print("[rewrite]", code, meta)
                return Responder(int(code), meta)

        return None


def init(context):
    cfg = context.config()
    for section in cfg.prefixed_sections('rewrite.').values():
        protocol = section.get('protocol', None)
        host = section.get('host', cfg.hostnames()[0])
        src_path = re.compile(section.get('path'))
        dst_path = section.get('repl', None)
        status = section.get('status', None)
        for proto in [protocol] if protocol else ['gemini', 'titan']:
            context.add(Rewriter(context, proto, host, src_path, dst_path, status),
                        None, # `Rewriter` will return a suitable handler callback.
                        host,
                        proto)
