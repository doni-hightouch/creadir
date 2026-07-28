import json
import os
import sys
from http.server import BaseHTTPRequestHandler

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import _lib


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            code, out = 200, _lib.gallery()
        except Exception as e:
            code, out = 502, {"error": str(e)}
        data = json.dumps(out).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)
