import json
import os
import sys
from http.server import BaseHTTPRequestHandler

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import _lib


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        gate = _lib.auth_gate(self.headers)
        if gate:
            code, out = gate
        else:
            email = _lib.current_user(self.headers)
            budget = _lib.budget_gate(email)
            if budget:
                code, out = budget
            else:
                length = int(self.headers.get("Content-Length", 0))
                try:
                    body = json.loads(self.rfile.read(length).decode())
                    _lib.meter_reset()
                    code, out = 200, _lib.generate(body)
                except Exception as e:
                    code, out = 502, {"error": str(e)}
                finally:
                    # bank what was actually spent, even on a partial failure
                    _lib.record_usage(email, "generate")
        data = json.dumps(out).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)
