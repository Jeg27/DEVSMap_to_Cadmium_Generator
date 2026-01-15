#!/usr/bin/env python3
import json
import os
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from generate_experiment_json_from_gui_data import build_experiment_json, save_experiment

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
INPUT_ROOT = os.path.join(REPO_ROOT, "input")
INIT_ROOT = os.path.join(INPUT_ROOT, "inits")
MODEL_ROOT = os.path.join(INPUT_ROOT, "models")

MODEL_RE = re.compile(r".*_(atomic|coupled)\.json$", re.IGNORECASE)
INIT_RE  = re.compile(r".*_init_state.*\.json$", re.IGNORECASE) 

def list_files(dir_path: str):
    if not os.path.isdir(dir_path):
        return []
    return sorted(os.listdir(dir_path))

def model_items():
    items = []
    for f in list_files(MODEL_ROOT):
        if MODEL_RE.match(f):
            items.append({"id": f, "name": f[:-5]})  # strip .json for display
    return items

def init_items():
    items = []
    for f in list_files(INIT_ROOT):
        if INIT_RE.match(f):
            items.append({"id": f, "name": f[:-5]})
    return items

def read_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_ports_from_model(model_path: str) -> dict:
    """
    Your schema:
    {
      "<top_name>": {
        "x": { "<in_port>": "<type>", ... },
        "y": { "<out_port>": "<type>", ... },
        ...
      },
      "include_sets": [...]
    }

    Returns: {"inputs": [...], "outputs": [...]}
    """
    j = read_json(model_path)

    if not isinstance(j, dict) or not j:
        return {"inputs": [], "outputs": []}

    # Find the top model key (ignore include_sets or other metadata keys)
    top_key = None
    for k, v in j.items():
        if k != "include_sets" and isinstance(v, dict):
            top_key = k
            break

    if top_key is None:
        return {"inputs": [], "outputs": []}

    top = j[top_key]

    x = top.get("x", {})
    y = top.get("y", {})

    inputs = list(x.keys()) if isinstance(x, dict) else []
    outputs = list(y.keys()) if isinstance(y, dict) else []

    return {"inputs": inputs, "outputs": outputs}

class Handler(BaseHTTPRequestHandler):
    def _send_json(self, obj, status=200):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
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
        
        if path == "/api/ports":
            qs = parse_qs(parsed.query)
            model = (qs.get("model", [""])[0] or "").strip()

            if not model:
                self._send_json({"error": "Missing ?model=filename.json"}, status=400)
                return

            # IMPORTANT: models live in input/
            model_path = os.path.join(MODEL_ROOT, model)

            if not os.path.isfile(model_path):
                self._send_json({"error": f"Model not found: {model}"}, status=404)
                return

            ports = extract_ports_from_model(model_path)
            self._send_json(ports)
            return

        self._send_json({"error": f"Not found: {path}"}, status=404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/experiment":
            try:
                length = int(self.headers.get("Content-Length", "0"))
                raw = self.rfile.read(length).decode("utf-8") if length else "{}"
                payload = json.loads(raw)
            except Exception as e:
                self._send_json({"error": f"Bad JSON: {e}"}, status=400)
                return
            
            # 1) Build the experiment.json dict
            experiment = build_experiment_json(payload)

            # 2) Save it into input/experiments
            exp_name = payload.get("expName", "experiment")
            out_path = save_experiment(REPO_ROOT, exp_name, experiment)

            # 3) Return experiment.json and it's saved location
            self._send_json(
                {
                    "experiment": experiment,
                    "saved_to": out_path
                }
            )
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


