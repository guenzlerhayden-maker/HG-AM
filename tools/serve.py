"""
Local dev server that refuses to let the browser cache anything.

WHY THIS EXISTS: python -m http.server sends no cache headers at all. With
nothing to go on, browsers fall back to heuristic caching from Last-Modified
and will happily keep serving a stylesheet from memory after it has changed on
disk. That produced the same confusing failure repeatedly during this build -
markup updating while CSS did not, so the page rendered as unstyled fragments
and looked broken when the files were in fact correct.

It is a dev-only concern. GitHub Pages sends proper validators, so the shipped
site caches normally; this only changes what happens on localhost.

Usage:  python tools/serve.py [port]
"""
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer


class NoCacheHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def guess_type(self, path):
        # http.server's table predates webp on some Windows installs and hands
        # it back as application/octet-stream. Browsers sniff it anyway, but a
        # correct type keeps local behaviour matching production.
        if str(path).endswith('.webp'):
            return 'image/webp'
        # State the charset. A linked stylesheet served as bare "text/css" is
        # decoded by browser fallback rather than by declaration, and a single
        # non-ASCII byte in a comment was enough to stop the parser halfway
        # through this file - every rule after it silently vanished while the
        # file itself was perfectly valid.
        t = super().guess_type(path)
        if isinstance(t, str) and t.startswith(('text/', 'application/javascript')):
            return t + '; charset=utf-8'
        return t

    def log_message(self, fmt, *args):
        pass  # quiet; the preview pane is the interesting output


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    print('serving with no-store on http://localhost:%d' % port)
    ThreadingHTTPServer(('127.0.0.1', port), partial(NoCacheHandler)).serve_forever()
