import http.server, os, sys, urllib.parse
ROOT = sys.argv[1]
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k): super().__init__(*a, directory=ROOT, **k)
    def do_POST(self):
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        name = os.path.basename(q['name'][0])
        out = os.path.join(ROOT, 'compare', 'out'); os.makedirs(out, exist_ok=True)
        data = self.rfile.read(int(self.headers['Content-Length']))
        open(os.path.join(out, name), 'wb').write(data)
        self.send_response(200); self.end_headers(); self.wfile.write(b'ok')
    def log_message(self, *a): pass
http.server.ThreadingHTTPServer(('127.0.0.1', 8932), H).serve_forever()
