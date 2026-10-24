import numpy as np, subprocess, sys, os
sys.argv = sys.argv[:1]; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render
SR = 48000
def load(f):
    return np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout, dtype=np.float32).reshape(-1, 2).copy()
if render.STEMS:
    v = load(os.path.join(render.STEMS, 'vocals.wav')); mu = load(os.path.join(render.STEMS, 'no_vocals.wav'))
    n = min(len(v), len(mu)); voice = (v[:n] + mu[:n] * 10 ** (render.MUSIC_GAIN_DB / 20))[:int(render.DUR * SR)]
    vonly = v[:int(render.DUR * SR)]
else:
    voice = load(render.SRC)[:int(render.DUR * SR)]; vonly = voice
out = voice.copy()
def place(f, t, peak_db, align='start'):
    s = load('sfx/' + f); pk = np.abs(s).max() + 1e-9; s *= 10 ** (peak_db / 20) / pk
    off = int(np.argmax(np.abs(s).max(1))) if align == 'peak' else 0
    i = int(t * SR) - off; a = max(0, -i); i = max(0, i); n = min(len(s) - a, len(out) - i)
    if n > 0: out[i:i + n] += s[a:a + n]
for e in render.SFX: place(*e)
# typing sound under every word typed on the navy background (very quiet)
if render.CIRCLES and os.path.exists('sfx/typing.mp3'):
    typ = load('sfx/typing.mp3')[int(2.45 * SR):int(8.9 * SR)]
    vrms = np.sqrt(np.mean(vonly[np.abs(vonly).max(1) > 0.02] ** 2)); typ *= 0.1 * vrms / np.sqrt(np.mean(typ ** 2))
    pos = 0
    for c in render.CIRCLES:
        for w in render.words:
            if c[2][0] - 0.01 <= w['s'] < c[1]:
                n = int((w['e'] - w['s']) * SR); i = int(w['s'] * SR)
                if pos + n > len(typ): pos = 0
                seg = typ[pos:pos + n].copy(); pos += n
                f = min(len(seg) // 4, int(0.015 * SR)); ramp = np.linspace(0, 1, f)[:, None]
                if f > 0: seg[:f] *= ramp; seg[-f:] *= ramp[::-1]
                out[i:i + len(seg)] += seg[:len(out) - i]
os.makedirs('out', exist_ok=True)
out.astype(np.float32).tofile('out/mix.f32')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', 'out/mix.f32', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', str(SR), 'out/mix.wav'])
