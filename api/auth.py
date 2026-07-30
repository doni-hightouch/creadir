import json
import os
import sys
from http.server import BaseHTTPRequestHandler

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import _lib


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        cookie = None
        try:
            body = json.loads(self.rfile.read(length).decode())
            if body.get("action") == "signout":
                code, out = 200, {"authenticated": False}
                cookie = _lib.clear_cookie()
            else:
                res = _lib.sign_in(body)
                cookie = _lib.cookie_header(res.pop("session"))
                code, out = 200, {"authenticated": True, **res}
        except Exception as e:
            code, out = 403, {"error": str(e)}
        data = json.dumps(out).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        if cookie:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()
        self.wfile.write(data)
