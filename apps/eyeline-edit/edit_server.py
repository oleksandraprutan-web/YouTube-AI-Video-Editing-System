# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "soundfile", "imageio-ffmpeg"]
# ///
"""Eyeline Edit: review and fine-tune the cut of an Eyeline project, then export it. macOS and Windows.

    uv run edit_server.py [project folder] [port]      then open http://localhost:5320

Without a project folder it opens the last one, or shows a picker.
"""
import hashlib, math, json, re, subprocess, sys, threading, time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

import numpy as np, soundfile as sf

import project as P

ROOT = Path(__file__).resolve().parent
args = [a for a in sys.argv[1:] if not a.isdigit()]
PORT = next((int(a) for a in sys.argv[1:] if a.isdigit()), 5320)

state = {"project": None, "audio": {}, "words": {}}
lock = threading.Lock()


def plan_snapshot(proj):
    path = proj.edit / "plan.json"
    raw = path.read_bytes() if path.exists() else b"[]"
    revision = '"' + hashlib.sha256(str(proj.path).encode() + raw).hexdigest() + '"'
    return raw, revision


def valid_plan(data, proj):
    if not isinstance(data, list):
        return False
    for c in data:
        if not isinstance(c, dict) or c.get("take") not in proj.takes:
            return False
        a, b = c.get("cutIn"), c.get("cutOut")
        if any(not isinstance(v, (float, int)) or isinstance(v, bool) or not math.isfinite(v) for v in (a, b)):
            return False
        if not 0 <= a < b <= sf.info(str(proj.take_audio(c["take"]))).duration + 0.05:
            return False
    return True


def open_project(path):
    proj = P.Project(path)
    audio, words = {}, {}
    for k in proj.takes:
        audio[k] = load16k(proj, k)
        words[k] = proj.words(k)
    with lock:
        state.update(project=proj, audio=audio, words=words)
    return proj


def load16k(proj, take):
    """The take's audio at 16 kHz for waveforms and envelopes, cached on this machine."""
    src = proj.take_audio(take)
    cache = proj.cache / f"{take}.16k.npy"
    if cache.exists() and cache.stat().st_mtime >= src.stat().st_mtime:
        return np.load(cache)
    x, sr = sf.read(src, dtype="float32")
    x = x if x.ndim == 1 else x.mean(1)
    f = max(1, sr // 16000)
    x = x[: len(x) // f * f].reshape(-1, f).mean(1).astype(np.float32)
    np.save(cache, x)
    return x


render_state = {"running": False, "log": "", "out": None, "started": None, "done": None, "error": None}


def runner(script):
    """Run a helper script with this Python if it has what the script needs, else through uv (which installs it)."""
    import importlib.util, shutil
    if script == "edit_transcribe.py" and not (importlib.util.find_spec("mlx_whisper") or importlib.util.find_spec("faster_whisper")):
        uv = shutil.which("uv")
        if uv:
            return [uv, "run", "--script", str(ROOT / script)]
    return [sys.executable, str(ROOT / script)]


def run_transcribe(proj, wav):
    """Transcript of the final cut's audio. Exports the audio first when it is missing or older than the cut."""
    if not wav.exists() or wav.stat().st_mtime < (proj.edit / "plan.json").stat().st_mtime:
        run_render(proj, wav, audio_only=True)
        if render_state["error"]:
            return
    render_state.update(running=True, log=render_state["log"] + "\n", out=str(wav.with_suffix("")) + " script.txt", started=time.time(), done=None, error=None)
    p = subprocess.Popen(runner("edit_transcribe.py") + [str(proj.path), str(wav)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=ROOT)
    for line in p.stdout:
        render_state["log"] = (render_state["log"] + line)[-4000:]
    p.wait()
    render_state.update(running=False, done=time.time(), error=None if p.returncode == 0 else f"transcript failed ({p.returncode})")


def run_render(proj, out_path, audio_only=False):
    plan_path = proj.cache / "plan.render.json"
    P.write_json(plan_path, P.normalize(proj.plan(), proj))
    render_state.update(running=True, log="", out=str(out_path), started=time.time(), done=None, error=None)
    cmd = [sys.executable, str(ROOT / "edit_render.py"), str(proj.path), str(plan_path), str(out_path)] + (["--audio-only"] if audio_only else [])
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=ROOT)
    for line in p.stdout:
        render_state["log"] = (render_state["log"] + line)[-4000:]
    p.wait()
    render_state.update(running=False, done=time.time(), error=None if p.returncode == 0 else f"export failed ({p.returncode})")


class H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(ROOT / "app"), **k)

    def log_message(self, *a):
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def js(self, obj, status=200, revision=None):
        b = json.dumps(obj).encode()
        self.send_response(status)
        if revision:
            self.send_header("ETag", revision)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def file(self, path, ctype):
        size = path.stat().st_size
        rng = self.headers.get("Range")
        start, end = 0, size - 1
        if rng:
            m = re.fullmatch(r"bytes=(\d*)-(\d*)", rng)
            if not m or not any(m.groups()):
                return self.send_error(416)
            if m.group(1):
                start = int(m.group(1))
                end = min(int(m.group(2)), size - 1) if m.group(2) else size - 1
            else:
                start = max(0, size - int(m.group(2)))
            if start > end or start >= size:
                return self.send_error(416)
        length = end - start + 1
        self.send_response(206 if rng else 200)
        self.send_header("Content-Type", ctype)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(length))
        if rng:
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.end_headers()
        with open(path, "rb") as f:
            f.seek(start)
            left = length
            try:
                while left > 0:
                    chunk = f.read(min(1 << 20, left))
                    if not chunk: break
                    self.wfile.write(chunk)
                    left -= len(chunk)
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                pass

    def do_GET(self):
        if urlparse("http://" + self.headers.get("Host", "")).hostname not in ("localhost", "127.0.0.1", "::1"):
            return self.send_error(403)
        u = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        proj = state["project"]
        if u.path == "/api/projects":
            return self.js({"current": str(proj.path) if proj else None, "recent": P.config().get("recent", [])})
        if not proj and u.path.startswith(("/api/", "/media/", "/sprites/")):
            return self.js({"error": "no project open"}, 409)
        if u.path.startswith("/media/"):
            f = proj.proxy(Path(unquote(u.path)).stem)
            return self.file(f, "video/mp4") if f.exists() else self.send_error(404)
        if u.path.startswith("/sprites/"):
            parts = unquote(u.path).split("/")[2:]
            f = proj.edit / "sprites" / parts[0] / parts[1] if len(parts) == 2 and ".." not in parts else None
            return self.file(f, "image/jpeg") if f and f.exists() else self.send_error(404)
        if u.path == "/api/plan":
            with lock:
                raw, revision = plan_snapshot(proj)
                return self.js(json.loads(raw), revision=revision)
        if u.path == "/api/original":
            return self.js(P.read_json(proj.edit / "plan.original.json", proj.plan()))
        if u.path == "/api/meta":
            plan = proj.plan()
            return self.js({"project": proj.name, "path": str(proj.path), "fps": P.FPS,
                            "takes": {k: len(a) / 16000 for k, a in state["audio"].items()},
                            "previews": [k for k in proj.takes if proj.proxy(k).exists()],
                            "flags": P.read_json(proj.edit / "flags.json", []),
                            "defaultOut": str(proj.renders_dir() / f"{proj.name} - final cut.mp4"),
                            "missingFootage": proj.missing_footage(plan) if plan else [],
                            "messages": len(proj.messages())})
        if u.path == "/api/peaks":
            t = q["take"]; x = state["audio"][t]
            a = max(0.0, float(q["from"])); b = min(len(x) / 16000, float(q["to"])); n = max(1, int(q.get("n", 800)))
            y = x[int(a * 16000):int(b * 16000)]
            if len(y) < n:
                return self.js({"from": a, "to": b, "peaks": []})
            m = len(y) // n; y = y[:m * n].reshape(n, m)
            return self.js({"from": a, "to": b, "peaks": np.round(np.stack([y.min(1), y.max(1)], 1), 4).tolist()})
        if u.path == "/api/words":
            t = q["take"]; a, b = float(q["from"]), float(q["to"])
            return self.js([w for w in state["words"][t] if w[1] >= a and w[0] <= b])
        if u.path == "/api/env":   # loudness envelope for the timeline strip: one byte per 10 ms
            x = state["audio"][q["take"]]; n = len(x) // 160
            e = np.abs(x[:n * 160].reshape(n, 160)).max(1)
            e = np.sqrt(e / (np.percentile(e, 99.5) + 1e-9)).clip(0, 1)
            b = (e * 255).astype(np.uint8).tobytes()
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)
            return
        if u.path == "/api/messages":
            return self.js(proj.messages())
        if u.path == "/api/render":
            return self.js(render_state)
        return super().do_GET()

    def do_POST(self):
        if urlparse("http://" + self.headers.get("Host", "")).hostname not in ("localhost", "127.0.0.1", "::1"):
            return self.send_error(403)
        origin = self.headers.get("Origin")
        if origin and origin != "http://" + self.headers.get("Host", ""):
            return self.js({"error": "cross-origin writes disabled"}, 403)
        u = urlparse(self.path)
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)) or 0)
        try:
            data = json.loads(body or b"{}")
        except ValueError:
            return self.js({"error": "invalid JSON"}, 400)
        if u.path == "/api/open":
            try:
                proj = open_project(data["path"])
            except (KeyError, ValueError, OSError) as e:
                return self.js({"error": str(e)}, 400)
            return self.js({"ok": True, "project": proj.name})
        proj = state["project"]
        if not proj:
            return self.js({"error": "no project open"}, 409)
        if u.path == "/api/plan":
            if not valid_plan(data, proj):
                return self.js({"error": "invalid source intervals or take"}, 400)
            with lock:
                if state["project"] is not proj or self.headers.get("If-Match") != plan_snapshot(proj)[1]:
                    return self.js({"error": "Plan changed elsewhere. Reload before editing; your changes were not saved."}, 409)
                saved = proj.save_plan(data)
                return self.js({"ok": True, "plan": saved}, revision=plan_snapshot(proj)[1])
        if u.path == "/api/relink":
            found = proj.relink(data.get("folder", ""))
            return self.js({"found": found, "missing": proj.missing_footage(proj.plan())})
        if u.path == "/api/render":
            if render_state["running"]:
                return self.js({"error": "already exporting"}, 409)
            missing = proj.missing_footage(proj.plan())
            if missing and not data.get("audioOnly"):
                return self.js({"error": "Camera files not found on this computer: " + ", ".join(missing)}, 409)
            out = Path(data.get("out") or (proj.renders_dir() / f"{proj.name} - final cut.mp4")).expanduser()
            threading.Thread(target=run_render, args=(proj, out, bool(data.get("audioOnly"))), daemon=True).start()
            return self.js({"ok": True, "out": str(out)})
        if u.path == "/api/transcribe":
            if render_state["running"]:
                return self.js({"error": "already exporting"}, 409)
            base = Path(data.get("out") or (proj.renders_dir() / f"{proj.name} - final cut.mp4")).expanduser()
            wav = base.with_suffix(".wav")
            threading.Thread(target=run_transcribe, args=(proj, wav), daemon=True).start()
            return self.js({"ok": True, "wav": str(wav)})
        if u.path == "/api/message":
            mid = proj.send_message(data.get("type", "note"), data.get("to", "recording"), data.get("title", "Note"),
                                    data.get("body", ""), **({"lines": data["lines"]} if data.get("lines") else {}))
            return self.js({"ok": True, "id": mid})
        if u.path == "/api/reveal":
            P.reveal(data.get("path") or proj.path)
            return self.js({"ok": True})
        self.send_error(404)


if __name__ == "__main__":
    start = args[0] if args else next((p for p in P.config().get("recent", []) if Path(p, "takes").is_dir()), None)
    if start:
        try:
            print("Opening", open_project(start).path)
        except ValueError as e:
            print(e)
    print(f"Eyeline Edit: http://localhost:{PORT}")
    ThreadingHTTPServer.daemon_threads = True
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
