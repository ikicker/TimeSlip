# -*- coding: utf-8 -*-
"""Local HTTP backend + static frontend for TimeSlip."""
from __future__ import print_function

import json
import os
import sys
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FRONTEND = os.path.join(ROOT, "frontend")

if HERE not in sys.path:
    sys.path.insert(0, HERE)

from storage import (  # noqa: E402
    clear_sessions,
    delete_session,
    dump_state,
    get_rate,
    init_db,
    list_sessions,
    set_rate,
    start_session,
    stop_session,
    update_session,
)
from xlsx_export import sessions_to_xlsx  # noqa: E402

HOST = "127.0.0.1"
PORT = 8765

MIME = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".json": "application/json",
    ".ico": "image/x-icon",
}


def _read_json(handler):
    length = int(handler.headers.get("Content-Length") or 0)
    raw = handler.rfile.read(length) if length else b"{}"
    if not raw:
        return {}
    return json.loads(raw.decode("utf-8"))


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        sys.stderr.write("[TimeSlip] " + (fmt % args) + "\n")

    def _send(self, code, body, content_type="application/json; charset=utf-8"):
        if not isinstance(body, bytes):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code, obj):
        self._send(code, json.dumps(obj))

    def _error(self, code, message):
        self._json(code, {"error": message})

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        try:
            parsed = urlparse(self.path)
            path = parsed.path
            if path == "/api/state":
                self._json(200, dump_state())
                return
            if path == "/api/sessions":
                self._json(200, {"sessions": list_sessions(), "rate": get_rate()})
                return
            if path == "/api/export.xlsx":
                self._export(parsed.query)
                return
            self._static(path)
        except Exception as exc:
            traceback.print_exc()
            self._error(500, str(exc))

    def do_POST(self):
        try:
            parsed = urlparse(self.path)
            path = parsed.path
            data = _read_json(self)
            if path == "/api/sessions/start":
                self._json(200, {"running": start_session(data.get("comment", ""))})
                return
            if path == "/api/sessions/stop":
                self._json(200, {"session": stop_session()})
                return
            if path == "/api/sessions/clear":
                clear_sessions()
                self._json(200, {"ok": True})
                return
            if path == "/api/settings":
                rate = set_rate(data.get("rate", 0))
                self._json(200, {"rate": rate})
                return
            self._error(404, "Not found")
        except ValueError as exc:
            self._error(400, str(exc))
        except Exception as exc:
            traceback.print_exc()
            self._error(500, str(exc))

    def do_PUT(self):
        try:
            parsed = urlparse(self.path)
            parts = [p for p in parsed.path.split("/") if p]
            data = _read_json(self)
            if len(parts) == 3 and parts[0] == "api" and parts[1] == "sessions":
                session = update_session(
                    parts[2],
                    data.get("comment"),
                    data.get("startMs"),
                    data.get("endMs"),
                )
                self._json(200, {"session": session})
                return
            self._error(404, "Not found")
        except ValueError as exc:
            self._error(400, str(exc))
        except Exception as exc:
            traceback.print_exc()
            self._error(500, str(exc))

    def do_DELETE(self):
        try:
            parsed = urlparse(self.path)
            parts = [p for p in parsed.path.split("/") if p]
            if len(parts) == 3 and parts[0] == "api" and parts[1] == "sessions":
                delete_session(parts[2])
                self._json(200, {"ok": True})
                return
            self._error(404, "Not found")
        except Exception as exc:
            traceback.print_exc()
            self._error(500, str(exc))

    def _export(self, query):
        params = parse_qs(query or "")
        sessions = list_sessions()
        from_ms = int(params.get("from", [0])[0] or 0)
        to_ms = int(params.get("to", [0])[0] or 0)
        if from_ms:
            sessions = [s for s in sessions if s["startMs"] >= from_ms]
        if to_ms:
            sessions = [s for s in sessions if s["startMs"] <= to_ms]
        sessions = list(reversed(sessions))
        if not sessions:
            self._error(400, "No sessions in that date range")
            return
        rate = get_rate()
        blob = sessions_to_xlsx(sessions, rate)
        stamp = __import__("datetime").datetime.now().strftime("%Y-%m-%d")
        filename = "TimeSlip-report-%s.xlsx" % stamp
        self.send_response(200)
        self.send_header(
            "Content-Type",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        self.send_header("Content-Disposition", 'attachment; filename="%s"' % filename)
        self.send_header("Content-Length", str(len(blob)))
        self.end_headers()
        self.wfile.write(blob)

    def _static(self, path):
        if path == "/":
            path = "/index.html"
        rel = path.lstrip("/")
        full = os.path.normpath(os.path.join(FRONTEND, rel))
        if not full.startswith(os.path.abspath(FRONTEND)):
            self._error(403, "Forbidden")
            return
        if not os.path.isfile(full):
            self._error(404, "Not found")
            return
        ext = os.path.splitext(full)[1].lower()
        content_type = MIME.get(ext, "application/octet-stream")
        with open(full, "rb") as handle:
            self._send(200, handle.read(), content_type)


def make_server(host=HOST, port=PORT):
    init_db()
    # ThreadingHTTPServer is 3.7+
    try:
        httpd = ThreadingHTTPServer((host, port), Handler)
    except NameError:
        from http.server import HTTPServer

        httpd = HTTPServer((host, port), Handler)
    return httpd


def main():
    init_db()
    httpd = make_server()
    print("TimeSlip running at http://%s:%s" % (HOST, PORT))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping TimeSlip")
        httpd.server_close()


if __name__ == "__main__":
    main()
