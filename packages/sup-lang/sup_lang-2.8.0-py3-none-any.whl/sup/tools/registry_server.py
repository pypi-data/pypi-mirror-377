from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs


class Registry(BaseHTTPRequestHandler):
    # Very simple file-backed registry:
    # - GET /resolve?name=&version= -> { name, version, source }
    #   Loads <data_dir>/<name>.sup as source; ignores version resolution (demo only)
    # - POST /upload { name, version, sha256 } -> 200 OK (no storage)

    def _send(self, code: int, payload: dict) -> None:
        data = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:  # noqa: N802
        u = urlparse(self.path)
        if u.path != "/resolve":
            self._send(404, {"error": "not found"})
            return
        q = parse_qs(u.query)
        name = (q.get("name") or [""])[0]
        if not name:
            self._send(400, {"error": "missing name"})
            return
        data_dir = os.environ.get("REGISTRY_DIR", os.getcwd())
        cand = os.path.join(data_dir, f"{name}.sup")
        if not os.path.exists(cand):
            self._send(404, {"error": "module not found"})
            return
        src = open(cand, encoding="utf-8").read()
        self._send(200, {"name": name, "version": (q.get("version") or ["*"])[0], "source": src})

    def do_POST(self) -> None:  # noqa: N802
        u = urlparse(self.path)
        if u.path != "/upload":
            self._send(404, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length)
            _ = json.loads(body.decode("utf-8"))
        except Exception:
            self._send(400, {"error": "invalid json"})
            return
        self._send(200, {"ok": True})


def main() -> None:
    host = os.environ.get("REGISTRY_HOST", "127.0.0.1")
    port = int(os.environ.get("REGISTRY_PORT", "8080"))
    server = HTTPServer((host, port), Registry)
    print(f"Registry listening on http://{host}:{port} (REGISTRY_DIR={os.environ.get('REGISTRY_DIR', os.getcwd())})")
    server.serve_forever()


if __name__ == "__main__":
    main()


