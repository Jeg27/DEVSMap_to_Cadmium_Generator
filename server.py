#!/usr/bin/env python3
import json
import os
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
INPUT_ROOT = os.path.join(REPO_ROOT, "input")
INIT_ROOT = os.path.join(INPUT_ROOT, "init")

# Your naming rules:
MODEL_RE = re.compile(r".*_(atomic|coupled)\.json$", re.IGNORECASE)
INIT_RE  = re.compile(r".*_init_state.*\.json$", re.IGNORECASE) 

def list_files(dir_path: str):
    if not os.path.isdir(dir_path):
        return []
    return sorted(os.listdir(dir_path))

def model_items():
    items = []
    for f in list_files(INPUT_ROOT):
        if MODEL_RE.match(f):
            items.append({"id": f, "name": f[:-5]})  # strip .json for display
    return items

def init_items():
    items = []
    for f in list_files(INIT_ROOT):
        if INIT_RE.match(f):
            items.append({"id": f, "name": f[:-5]})
    return items

class Handler(BaseHTTPRequestHandler):
    def _send_json(self, obj, status=200):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)

        # GET /api/models
        # returns everything in input/ that ends with _atomic.json or _coupled.json
        if path == "/api/models":
            self._send_json({"items": model_items()})
            return

        # GET /api/inits
        # returns everything in input/init that matches init_state*.json
        if path == "/api/inits":
            self._send_json({"items": init_items()})
            return

        self._send_json({"error": f"Not found: {path}"}, status=404)

def main():
    port = int(os.environ.get("PORT", "3001"))
    host = "0.0.0.0"
    print(f"Backend running on http://{host}:{port}")
    print(f"Models from: {INPUT_ROOT} (matches *_atomic.json / *_coupled.json)")
    print(f"Inits  from: {INIT_ROOT} (matches init_state*.json)")
    HTTPServer((host, port), Handler).serve_forever()

if __name__ == "__main__":
    main()