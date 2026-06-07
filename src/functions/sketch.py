import json
import os
import signal
import socket
import sys
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from threading import Thread

from .init import get_workspace_path
from .core import _ts

SKETCH_EXT = ".excalidraw"


def _sketch_dir(container_type=None, container_name=None):
    ws = get_workspace_path()
    if container_type == "project" and container_name:
        d = ws / "projects" / container_name
    elif container_type == "domain" and container_name:
        d = ws / "domains" / container_name
    elif container_type == "journal":
        d = ws / "journal"
    else:
        d = ws / "sketches"
    d.mkdir(parents=True, exist_ok=True)
    return d


def create_sketch(name="", container_type=None, container_name=None):
    d = _sketch_dir(container_type, container_name)
    name = name or _ts()
    path = d / f"{name}{SKETCH_EXT}"
    if not path.exists():
        path.write_text(
            json.dumps(
                {
                    "type": "excalidraw",
                    "version": 2,
                    "elements": [],
                    "appState": {"gridSize": None, "viewBackgroundColor": "#0d0d0d"},
                }
            )
        )
    return path


def list_sketches(container_type=None, container_name=None):
    d = (
        get_workspace_path() / "sketches"
        if not container_type
        else _sketch_dir(container_type, container_name)
    )
    if not d.exists():
        return []
    sketches = []
    for f in sorted(d.glob(f"*{SKETCH_EXT}"), reverse=True):
        stat = f.stat()
        sketches.append(
            {
                "path": str(f),
                "name": f.stem,
                "mtime": stat.st_mtime,
            }
        )
    return sketches


HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>northh sketch</title>
<style>
  *{margin:0;padding:0;box-sizing:border-box}
  html,body,#root,#excalidraw-wrapper{height:100vh;width:100vw;overflow:hidden}
  body{background:#0d0d0d;color:#e5e5e5;font-family:sans-serif}
  #save-bar{position:fixed;bottom:16px;left:50%;transform:translateX(-50%);
    z-index:999;display:flex;gap:12px;align-items:center;
    background:#1a1a1a;border:1px solid #333;border-radius:8px;padding:8px 16px}
  #save-bar button{background:#f59e0b;color:#0d0d0d;border:none;
    border-radius:4px;padding:6px 16px;cursor:pointer;font-weight:600}
  #save-bar button:hover{background:#d97706}
  #save-bar .status{color:#888;font-size:13px}
  #save-bar .sketch-name{color:#f59e0b;font-size:13px}
</style>
</head>
<body>
<div id="root"><div id="excalidraw-wrapper"></div></div>
<div id="save-bar">
  <span class="sketch-name">SKETCH_NAME</span>
  <button id="save-btn">Save to northh</button>
  <span id="save-status" class="status">ready</span>
</div>
<script type="module">
import * as ExcalidrawLib from "https://esm.sh/@excalidraw/excalidraw@0.18.0";
import React from "https://esm.sh/react@19";
import ReactDOM from "https://esm.sh/react-dom@19/client";

const {Excalidraw, serializeAsJSON, restoreElements, restoreAppState, exportToBlob} = ExcalidrawLib;
const API_ROOT = "http://localhost:PORT";
let api = null;

async function loadScene() {
  const r = await fetch(API_ROOT + "/load");
  if (!r.ok) return;
  const data = await r.json();
  return data;
}

async function saveScene(elements, appState, files) {
  document.getElementById("save-status").textContent = "saving...";
  const data = JSON.stringify({
    type: "excalidraw",
    version: 2,
    elements: elements,
    appState: appState,
    files: files || {},
  });
  const r = await fetch(API_ROOT + "/save", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: data,
  });
  if (r.ok) {
    document.getElementById("save-status").textContent = "saved at " + new Date().toLocaleTimeString();
  } else {
    document.getElementById("save-status").textContent = "save failed!";
  }
}

async function exportSVG(elements, appState, files) {
  try {
    const blob = await exportToBlob({
      elements, appState, files,
      exportPadding: 20,
      backgroundColor: "#0d0d0d",
    });
    const reader = new FileReader();
    reader.onload = function() {
      const base64 = reader.result.split(",")[1];
      fetch(API_ROOT + "/export-svg", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({svg: base64}),
      });
    };
    reader.readAsDataURL(blob);
  } catch(e) {
    console.log("SVG export:", e.message);
  }
}

const root = ReactDOM.createRoot(document.getElementById("excalidraw-wrapper"));

loadScene().then((saved) => {
  let initial = null;
  if (saved && saved.elements && saved.elements.length > 0) {
    initial = {
      elements: restoreElements(saved.elements, null),
      appState: restoreAppState(saved.appState || {}, null),
      files: saved.files || {},
    };
  }

  root.render(React.createElement(Excalidraw, {
    initialData: initial,
    onChange: (elements, appState, files) => {
      if (elements.length > 0) {
        document.getElementById("save-status").textContent = "unsaved changes";
      }
    },
    onPointerUp: (e) => {
      const api = document.querySelector("excalidraw")?.__excalidraw_api;
      if (api && api.getSceneElements().length > 0) {
      }
    },
    theme: "dark",
    viewModeEnabled: false,
    zenModeEnabled: false,
    gridModeEnabled: false,
    name: "SKETCH_NAME",
  }));
});

document.getElementById("save-btn").addEventListener("click", async () => {
  const el = document.querySelector("excalidraw");
  if (!el || !el.__excalidraw_api) return;
  const api = el.__excalidraw_api;
  const elements = api.getSceneElements();
  const appState = api.getAppState();
  const files = api.getFiles();
  await saveScene(elements, appState, files);
  await exportSVG(elements, appState, files);
});
</script>
</body>
</html>"""


class SketchHandler(BaseHTTPRequestHandler):
    sketch_path = None
    server_ref = None

    def log_message(self, fmt, *args):
        pass

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _send_html(self, html):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode())

    def do_GET(self):
        if self.path == "/load":
            if self.sketch_path and Path(self.sketch_path).exists():
                data = json.loads(Path(self.sketch_path).read_text())
                self._send_json(data)
            else:
                self._send_json({"elements": [], "appState": {}})
        elif self.path == "/":
            html = HTML_PAGE.replace("PORT", str(self.server.server_port))
            html = html.replace(
                "SKETCH_NAME",
                Path(self.sketch_path).stem if self.sketch_path else "untitled",
            )
            self._send_html(html)
        else:
            self._send_json({"error": "not found"}, 404)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode()

        if self.path == "/save":
            Path(self.sketch_path).write_text(body)
            self._send_json({"status": "ok"})

            try:
                data = json.loads(body)
                self._export_svg(data)
            except Exception:
                pass
        elif self.path == "/export-svg":
            try:
                data = json.loads(body)
                svg_path = Path(self.sketch_path).with_suffix(".svg")
                import base64

                svg_data = base64.b64decode(data.get("svg", ""))
                svg_path.write_bytes(svg_data)
            except Exception:
                pass
            self._send_json({"status": "ok"})
        else:
            self._send_json({"error": "not found"}, 404)

    def _export_svg(self, data):
        pass


def _find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def open_sketch(path=None, container_type=None, container_name=None, sketch_name=None):
    if path:
        path = Path(path)
    else:
        path = create_sketch(sketch_name, container_type, container_name)

    port = _find_free_port()

    def make_handler(*args):
        handler = SketchHandler
        handler.sketch_path = str(path)
        return handler(*args)

    server = HTTPServer(("127.0.0.1", port), make_handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    url = f"http://127.0.0.1:{port}/"
    print(f"\n  sketch: {path.name}")
    print(f"  open:   {url}")
    print(f"  path:   {path}")
    print()
    print("  draw in the browser, click 'Save to northh',")
    print("  then press Enter here to return.")
    print()

    webbrowser.open(url)

    try:
        input()
    except (KeyboardInterrupt, EOFError):
        print()

    server.shutdown()

    if Path(path).exists():
        try:
            data = json.loads(Path(path).read_text())
            n = len(data.get("elements", []))
            print(f"  saved sketch with {n} elements")
        except Exception:
            print(f"  sketch saved at {path}")
