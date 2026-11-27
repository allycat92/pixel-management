#!/usr/bin/env python3
"""Local static server for the game that always revalidates files (Cache-Control: no-cache).

Usage: python3 tools/serve.py [port=8000]   (run from anywhere; serves the repo root)
Sheet PNGs are overwritten in place, so a plain `python3 -m http.server` lets the browser keep an old PNG.
"""
import functools, http.server, os, sys


class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache')
        super().end_headers()


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    handler = functools.partial(NoCacheHandler, directory=root)
    print(f'http://localhost:{port}  (serving {root}, no-cache)')
    http.server.ThreadingHTTPServer(('', port), handler).serve_forever()
