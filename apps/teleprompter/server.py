#!/usr/bin/env python3
"""Eyeline local server.

Serves the teleprompter, relays sync messages between devices on the same Wi-Fi
(the Mac listens and controls, an iPad shows the words, an iPhone monitors), and
keeps one folder per video project: its script, its takes (audio, captions, edit
data) and an edit plan an AI agent can cut from. Standard library only.

    python3 server.py [port]
"""
import os
import json
import queue
import re
import shutil
import socket
import struct
import subprocess
import sys
import threading
import time
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlparse

PORT = next((int(a) for a in sys.argv[1:] if a.isdigit()), 5317)
BIND = "0.0.0.0" if "--lan" in sys.argv else "127.0.0.1"
ROOT = Path(__file__).resolve().parent          # the app
HOME = Path(os.environ.get("EYELINE_DATA", Path.home() / "Eyeline")).expanduser().resolve()
HOME.mkdir(parents=True, exist_ok=True)
# HOME = ROOT.parent                               # the folder with your scripts
PROJECTS = HOME / "Projects"                     # one folder per video
LOG = HOME / "connections.log"                   # who connected from the network, for troubleshooting
SCRIPT_EXT = {".md", ".markdown", ".txt"}
TAKE_FILES = {"transcript.srt", "script-captions.srt", "flubs.srt", "take.json",
              "take-report.md", "youtube-chapters.txt", "script.txt"}
PROJECT_FILES = {"edit-plan.json", "edit-plan.md"}

clients = {}   # id -> {"q": Queue, "name": str, "role": str}
latest = {}    # last "session", "display" and "view" from the Mac, replayed to devices that join late
lock = threading.Lock()


def app_version():
    """Changes whenever index.html is saved, so open pages know to reload."""
    try:
        return int((ROOT / "index.html").stat().st_mtime * 1000)
    except OSError:
        return 0


def lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))  # no packet is sent; this just picks the outgoing interface
        return s.getsockname()[0]
    except OSError:
        return None
    finally:
        s.close()


def wav_header(rate, data_bytes):
    return (b"RIFF" + struct.pack("<I", 36 + data_bytes) + b"WAVE"
            + b"fmt " + struct.pack("<IHHIIHH", 16, 1, 1, rate, rate * 2, 2, 16)
            + b"data" + struct.pack("<I", data_bytes))


def clean_name(name):
    name = re.sub(r"[^\w .,'()&+-]+", " ", name or "").strip(" .")
    return re.sub(r"\s+", " ", name)[:60]


def project_dir(name):
    name = unquote(name or "")
    if not name or "/" in name or "\\" in name or name.startswith("."):
        return None
    p = PROJECTS / name
    return p if p.is_dir() and PROJECTS.resolve() in p.resolve().parents else None


def take_number(folder):
    m = re.match(r"Take (\d+)", folder.name)
    return int(m.group(1)) if m else 0


def install_guide(project):
    guide = ROOT / "AGENTS-project.md"
    if guide.exists():
        shutil.copyfile(guide, project / "AGENTS.md")


def take_dir(tid):
    """Take ids are the take folder's path inside Projects, so saving survives a server restart."""
    p = (PROJECTS / unquote(tid)).resolve()
    if PROJECTS.resolve() not in p.parents or not (p / "audio.wav").exists():
        return None
    return p


def broadcast(msg, skip=None):
    data = json.dumps(msg)
    with lock:
        for cid, c in clients.items():
            if cid != skip:
                c["q"].put(data)


def peers_msg():
    with lock:
        return {"type": "peers",
                "peers": [{"id": cid, "name": c["name"], "role": c["role"]} for cid, c in clients.items()]}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, fmt, *args):
        if not self.is_local():   # only log other devices, to help when an iPad or iPhone can't connect
            try:
                with open(LOG, "a") as f:
                    f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} {self.client_address[0]} {fmt % args}\n")
            except OSError:
                pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def is_local(self):
        return self.client_address[0] in ("127.0.0.1", "::1", "::ffff:127.0.0.1")

    def send_json(self, obj, status=200):
        data = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_text(self, text):
        data = text.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def ok(self):
        self.send_response(204)
        self.end_headers()

    # ---------- GET ----------
    def do_GET(self):
        url = urlparse(self.path)
        path = url.path
        if path == "/info":
            ip = lan_ip()
            return self.send_json({"sync": True, "port": PORT, "takes": True, "projects": True,
                                   "lan": f"http://{ip}:{PORT}/" if ip else None})
        if path == "/events":
            return self.stream_events(parse_qs(url.query))
        if path == "/scripts" or path.startswith("/scripts/") or path.startswith("/projects"):
            if not self.is_local() or urlparse("http://" + self.headers.get("Host", "")).hostname not in ("localhost", "127.0.0.1", "::1"):
                return self.send_error(403)
            if path == "/scripts":
                return self.send_json([{"name": p.name} for p in self.script_files()])
            if path.startswith("/scripts/"):
                match = next((p for p in self.script_files() if p.name == unquote(path[9:])), None)
                return self.send_text(match.read_text(errors="replace")) if match else self.send_error(404)
            return self.get_project(path)
        if path not in ("/", "/index.html"):
            return self.send_error(404)
        return super().do_GET()

    def script_files(self):
        return sorted((p for p in HOME.iterdir() if p.is_file() and p.suffix.lower() in SCRIPT_EXT),
                      key=lambda p: p.stat().st_mtime, reverse=True)

    def get_project(self, path):
        parts = path.strip("/").split("/")
        if parts == ["projects"]:
            out = []
            if PROJECTS.is_dir():
                for p in PROJECTS.iterdir():
                    if not p.is_dir() or p.name.startswith("."):
                        continue
                    takes = [t for t in (p / "takes").glob("Take *") if t.is_dir()]
                    stamps = [f.stat().st_mtime for f in [p, p / "script.md", *takes] if f.exists()]
                    out.append({"name": p.name, "takes": len(takes), "modified": int(max(stamps) * 1000)})
            return self.send_json(sorted(out, key=lambda x: x["modified"], reverse=True))
        if len(parts) != 3:
            return self.send_error(404)
        proj = project_dir(parts[1])
        if not proj:
            return self.send_error(404)
        if parts[2] == "script":
            f = proj / "script.md"
            return self.send_text(f.read_text(errors="replace") if f.exists() else "")
        if parts[2] == "takes":   # every saved take's edit map, oldest first
            out = []
            for t in sorted((proj / "takes").glob("Take *"), key=take_number):
                j = t / "take.json"
                if j.exists():
                    try:
                        out.append({"folder": t.name, "number": take_number(t), "take": json.loads(j.read_text())})
                    except ValueError:
                        pass
            return self.send_json(out)
        return self.send_error(404)

    # ---------- POST ----------
    def do_POST(self):
        origin = self.headers.get("Origin")
        if origin and origin != "http://" + self.headers.get("Host", ""):
            return self.send_error(403, "Cross-origin writes are disabled")
        url = urlparse(self.path)
        length = int(self.headers.get("Content-Length") or 0)
        if length > 16_000_000:
            return self.send_error(413)
        body = self.rfile.read(length)
        if url.path == "/send":
            return self.relay(body)
        if not self.is_local() or urlparse("http://" + self.headers.get("Host", "")).hostname not in ("localhost", "127.0.0.1", "::1"):
            return self.send_error(403)
        if url.path.startswith("/projects"):
            return self.post_project(url, body)
        if url.path.startswith("/take/"):
            return self.take(url, body)
        return self.send_error(404)

    def relay(self, body):
        try:
            data = json.loads(body)
        except ValueError:
            return self.send_error(400)
        msg = data.get("msg") if isinstance(data, dict) else None
        if not isinstance(msg, dict):
            return self.send_error(400)
        if msg.get("type") in ("session", "display", "view"):
            latest[msg["type"]] = msg
        broadcast(msg, skip=data.get("from"))
        self.ok()

    def post_project(self, url, body):
        parts = url.path.strip("/").split("/")
        if parts == ["projects"]:            # create
            try:
                info = json.loads(body or b"{}")
            except ValueError:
                return self.send_error(400)
            base = clean_name(info.get("name")) or f"Video {datetime.now():%Y-%m-%d}"
            PROJECTS.mkdir(exist_ok=True)
            name, n = base, 2
            while (PROJECTS / name).exists():
                name, n = f"{base} {n}", n + 1
            proj = PROJECTS / name
            (proj / "takes").mkdir(parents=True)
            (proj / "footage").mkdir()
            (proj / "script.md").write_text(info.get("script") or "")
            (proj / "project.json").write_text(json.dumps({"eyeline": 2, "name": name,
                                                           "created": datetime.now().isoformat(timespec="seconds")}, indent=1))
            install_guide(proj)
            return self.send_json({"name": name})
        if len(parts) != 3:
            return self.send_error(404)
        proj = project_dir(parts[1])
        if not proj:
            return self.send_error(404)
        action = parts[2]
        if action == "script":
            (proj / "script.md").write_bytes(body)
        elif action == "file":
            name = (parse_qs(url.query).get("name") or [""])[0]
            if name not in PROJECT_FILES:
                return self.send_error(400)
            (proj / name).write_bytes(body)
        elif action == "reveal":
            subprocess.run((["open", str(proj)] if sys.platform == "darwin" else ["explorer", str(proj)] if os.name == "nt" else ["xdg-open", str(proj)]), check=False)
        elif action == "rename":
            try:
                to = clean_name(json.loads(body or b"{}").get("name"))
            except ValueError:
                return self.send_error(400)
            if not to:
                return self.send_error(400)
            if (PROJECTS / to).exists() and to != proj.name:
                return self.send_json({"error": "exists"}, 409)
            proj.rename(PROJECTS / to)
            return self.send_json({"name": to})
        else:
            return self.send_error(404)
        self.ok()

    def take(self, url, body):
        parts = url.path.strip("/").split("/")   # ["take", "start"] or ["take", id, action]
        if parts == ["take", "start"]:
            try:
                info = json.loads(body or b"{}")
            except ValueError:
                return self.send_error(400)
            proj = project_dir(info.get("project"))
            if not proj:
                return self.send_error(404)
            takes = proj / "takes"
            takes.mkdir(exist_ok=True)
            number = max([take_number(t) for t in takes.glob("Take *")] + [0]) + 1
            folder = takes / f"Take {number:02d} · {datetime.now():%Y-%m-%d %H.%M}"
            folder.mkdir()
            rate = int(info.get("rate") or 48000)
            (folder / "audio.wav").write_bytes(wav_header(rate, 0))
            install_guide(proj)
            rel = folder.relative_to(PROJECTS)
            return self.send_json({"id": quote(rel.as_posix(), safe=""), "number": number,
                                   "folder": str(folder.relative_to(HOME))})
        if len(parts) != 3:
            return self.send_error(404)
        folder = take_dir(parts[1])
        if not folder:
            return self.send_error(404)
        action, wav = parts[2], folder / "audio.wav"
        if action == "audio":
            with open(wav, "r+b") as f:   # append samples, then fix the sizes so the file is always playable
                f.seek(24)
                rate = struct.unpack("<I", f.read(4))[0]
                f.seek(0, 2)
                f.write(body)
                size = f.tell() - 44
                f.seek(0)
                f.write(wav_header(rate, size))
        elif action == "file":
            name = (parse_qs(url.query).get("name") or [""])[0]
            if name not in TAKE_FILES:
                return self.send_error(400)
            (folder / name).write_bytes(body)
        elif action == "reveal":
            subprocess.run(["open", "-R", str(wav)], check=False)
        elif action == "discard":
            shutil.rmtree(folder, ignore_errors=True)
        else:
            return self.send_error(404)
        self.ok()

    def stream_events(self, qs):
        cid = (qs.get("id") or [""])[0][:40] or str(time.time())
        me = {"q": queue.Queue(),
              "name": (qs.get("name") or ["Device"])[0][:30],
              "role": (qs.get("role") or ["screen"])[0][:10]}
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.end_headers()
        with lock:
            clients[cid] = me
        version = app_version()
        me["q"].put(json.dumps({"type": "hello", "version": version}))
        for kind in ("session", "display", "view"):
            if kind in latest:
                me["q"].put(json.dumps(latest[kind]))
        broadcast(peers_msg())
        idle = 0
        try:
            while True:
                try:
                    self.wfile.write(f"data: {me['q'].get(timeout=2)}\n\n".encode())
                    idle = 0
                except queue.Empty:
                    idle += 2
                    if app_version() != version:
                        version = app_version()
                        me["q"].put(json.dumps({"type": "hello", "version": version}))
                    if idle >= 14:
                        self.wfile.write(b": ping\n\n")
                        idle = 0
                self.wfile.flush()
        except OSError:
            pass
        finally:
            with lock:
                if clients.get(cid) is me:
                    del clients[cid]
            broadcast(peers_msg())


if __name__ == "__main__":
    ThreadingHTTPServer.daemon_threads = True
    server = ThreadingHTTPServer((BIND, PORT), Handler)
    ip = lan_ip()
    print(f"Eyeline on this computer:  http://localhost:{PORT}/")
    if ip and BIND == "0.0.0.0":
        print(f"On your iPad/iPhone:  http://{ip}:{PORT}/  (same Wi-Fi)")
    print(f"Projects are saved in: {PROJECTS}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
