"""Creadir — local dev server. Same logic as the Vercel deployment: all core
behavior lives in api/_lib.py; this file just serves it on localhost."""

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
PUBLIC = os.path.join(ROOT, "public")
sys.path.insert(0, os.path.join(ROOT, "api"))

import _lib  # noqa: E402

PORT = 8787
MIME = {".html": "text/html", ".css": "text/css", ".js": "text/javascript",
        ".svg": "image/svg+xml", ".png": "image/png"}


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        print("%s %s" % (self.command, self.path))

    def _send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/api/status":
            self._send(200, _lib.status())
            return
        if path == "/api/gallery":
            try:
                self._send(200, _lib.gallery())
            except Exception as e:
                self._send(502, {"error": str(e)})
            return
        if path == "/":
            path = "/index.html"
        fp = os.path.normpath(os.path.join(PUBLIC, path.lstrip("/")))
        if fp.startswith(PUBLIC) and os.path.isfile(fp):
            ext = os.path.splitext(fp)[1]
            with open(fp, "rb") as f:
                self._send(200, f.read(), MIME.get(ext, "application/octet-stream"))
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        if length > 40 * 1024 * 1024:
            self._send(413, {"error": "image too large (40MB max)"})
            return
        try:
            body = json.loads(self.rfile.read(length).decode())
        except Exception:
            self._send(400, {"error": "invalid JSON body"})
            return
        summary = {
            k: (v[:80] if isinstance(v, str) and not v.startswith("data:") else
                ("<image %dkb>" % (len(v) // 1024) if isinstance(v, str) else v))
            for k, v in body.items()
        }
        print("POST %s %s" % (self.path, json.dumps(summary)))
        try:
            if self.path == "/api/analyze":
                self._send(200, _lib.analyze(body.get("images") or body["image"], body.get("context"), body.get("force_category")))
            elif self.path == "/api/fetch":
                self._send(200, _lib.fetch_creative(body.get("url", "")))
            elif self.path == "/api/compile":
                self._send(200, _lib.compile_prompt(body.get("fragments", []), body.get("extra", "")))
            elif self.path == "/api/generate":
                self._send(200, _lib.generate(body))
            elif self.path == "/api/feedback":
                self._send(200, _lib.feedback(body.get("message", "")))
            elif self.path == "/api/save":
                self._send(200, _lib.save_analysis(body, body.get("id")))
            else:
                self._send(404, {"error": "not found"})
        except Exception as e:
            self._send(502, {"error": str(e)})


if __name__ == "__main__":
    if not _lib.key("OPENAI_API_KEY"):
        print("WARNING: OPENAI_API_KEY is empty — API calls will fail")
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print("Creadir running on http://127.0.0.1:%d (critic: %s)" % (
        PORT, "claude" if _lib.key("ANTHROPIC_API_KEY") else "openai"))
    server.serve_forever()
