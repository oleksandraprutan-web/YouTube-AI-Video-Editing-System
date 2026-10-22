import json, subprocess, os, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
SRC = 'src/1022.mp4'
FONT = os.path.expanduser('~/.fonts/Montserrat-Black.ttf')
NAVY = (2, 6, 74)
ORANGE = (244, 122, 58)
FACE = (560, 680)  # zoom anchor (face) in source pixels
PREVIEW = '--preview' in sys.argv

words = json.load(open('words.json'))
DUR = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', SRC], capture_output=True, text=True).stdout)

# ---------------- timeline ----------------
ZOOMS = [(0, 1.0), (3.08, 1.2), (5.5, 1.05), (8.74, 1.4), (9.54, 1.1), (16.76, 1.0), (17.94, 1.25),
         (19.08, 1.08), (20.80, 1.22), (22.74, 1.0), (30.72, 1.18), (39.06, 1.05)]
CIRCLES = [  # start, end, phrase split times (typed text = spoken words)
    (11.50, 16.62, [11.66, 13.80, 14.94]),
    (33.40, 38.98, [33.56, 35.92, 37.36]),
]
TINT = (23.6, 30.62)
PILLS = [  # time, text, row, slot (0 left,1 right, None centered)
    (25.42, 'LECZENIE', 0, 0), (26.44, 'SZKOŁA', 0, 1),
    (27.42, 'ZAJĘCIA POZALEKCYJNE', 1, None), (29.26, 'CODZIENNA OPIEKA', 2, None)]
BIGTEXT = [(17.50, 19.05, '1 WARUNEK')]
TOPTITLE = [(39.06, DUR, 'ZAOBSERWUJ')]
ARROWS = [(39.35, DUR, (540, 1215))]  # neon arrow pointing down (CTA)

def arrow_layer(scale=1.0):
    S = 2  # supersample
    cx, cy, R1, R2 = 0, 0, 95 * S, 175 * S
    def P(r, th): return (cx + r * math.cos(math.radians(th)), cy - r * math.sin(math.radians(th)))
    a0, a1 = 125, 0
    outer = [P(R2, a0 - (a0 - a1) * i / 40) for i in range(41)]
    inner = [P(R1, a1 + (a0 - a1) * i / 40) for i in range(41)]
    th = math.radians(a1); tx, ty = math.sin(th), math.cos(th)  # screen tangent (clockwise)
    bo, bi = P(R2 + 60 * S, a1), P(R1 - 60 * S, a1)
    mid = P((R1 + R2) / 2, a1); tip = (mid[0] + tx * 140 * S, mid[1] + ty * 140 * S)
    poly = outer + [bo, tip, bi] + inner
    xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
    ox, oy = -min(xs) + 40 * S, -min(ys) + 40 * S
    poly = [(x + ox, y + oy) for x, y in poly]
    w, h = int(max(xs) - min(xs) + 80 * S), int(max(ys) - min(ys) + 80 * S)
    glow = Image.new('RGBA', (w, h)); ImageDraw.Draw(glow).line(poly + [poly[0]], fill=(255, 140, 20, 255), width=26 * S, joint='curve')
    glow = glow.filter(ImageFilter.GaussianBlur(16 * S))
    core = Image.new('RGBA', (w, h)); ImageDraw.Draw(core).line(poly + [poly[0]], fill=(255, 225, 140, 255), width=9 * S, joint='curve')
    glow.alpha_composite(glow); glow.alpha_composite(core)
    k = 0.5 * scale / S
    return glow.resize((max(1, int(w * k)), max(1, int(h * k))), Image.LANCZOS)
_ARROW = None

def zoom_at(t):
    s = ZOOMS[0][1]; prev = s; t0 = 0
    for zt, zs in ZOOMS:
        if t >= zt: prev, s, t0 = s, zs, zt
    e = min(1, (t - t0) / 0.18)  # quick eased punch
    e = 1 - (1 - e) ** 3
    base = prev + (s - prev) * e
    return base * (1 + 0.012 * (t - t0))  # slow push

def ease_pop(t, t0, d=0.22):
    x = min(1, max(0, (t - t0) / d))
    return x, 1 - (1 - x) ** 3

# ---------------- drawing helpers ----------------
_fonts = {}
def font(sz):
    if sz not in _fonts: _fonts[sz] = ImageFont.truetype(FONT, sz)
    return _fonts[sz]

def text_layer(lines, sz, fill, cy, shadow=True, extrude=0, align_cx=W // 2):
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    f = font(sz); lh = int(sz * 1.12)
    y0 = cy - lh * len(lines) // 2
    sh = Image.new('RGBA', (W, H)); ds = ImageDraw.Draw(sh)
    for i, ln in enumerate(lines):
        w = d.textlength(ln, font=f); x = align_cx - w / 2; y = y0 + i * lh
        for k in range(extrude, 0, -1):
            g = 150 - k * 6
            d.text((x + k * 0.6, y + k), ln, font=f, fill=(g, g, g, 255))
        d.text((x, y), ln, font=f, fill=fill)
        ds.text((x + 3, y + 6), ln, font=f, fill=(0, 0, 0, 170))
    if shadow:
        sh = sh.filter(ImageFilter.GaussianBlur(8))
        sh.alpha_composite(lay); return sh
    return lay

def scale_layer(lay, k, cx, cy):
    if k >= 0.999: return lay
    k = max(k, 0.01)
    small = lay.resize((max(1, int(W * k)), max(1, int(H * k))), Image.BILINEAR)
    out = Image.new('RGBA', (W, H))
    out.alpha_composite(small, (int(cx - cx * k), int(cy - cy * k)))
    return out

def fade(lay, a):
    if a >= 0.999: return lay
    r, g, b, al = lay.split()
    al = al.point(lambda v: int(v * a))
    return Image.merge('RGBA', (r, g, b, al))

def zoom_frame(img, z, anchor=FACE):
    cw, ch = W / z, H / z
    x0 = min(max(anchor[0] - anchor[0] / z, 0), W - cw)
    y0 = min(max(anchor[1] - anchor[1] / z, 0), H - ch)
    return img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))

# ---------------- static layers ----------------
tint = np.zeros((H, W, 4), np.uint8); tint[..., :3] = NAVY
ys = np.arange(H)[:, None]
tint[..., 3] = (np.clip(1 - ys / (H * 0.42), 0, 1) ** 1.3 * 215).astype(np.uint8)
TINT_L = Image.fromarray(tint, 'RGBA')

def pill_geom(row, slot, text):
    f = font(60); w = int(ImageDraw.Draw(Image.new('RGB', (1, 1))).textlength(text, font=f)) + 110
    h = 124; y = 120 + row * 150
    if slot is None: x = (W - w) // 2
    elif slot == 0: x = W // 2 - 20 - w
    else: x = W // 2 + 20
    return x, y, w, h

def draw_pill(base, text, row, slot, k, a):
    x, y, w, h = pill_geom(row, slot, text)
    cx, cy = x + w / 2, y + h / 2
    w2, h2 = w * (0.85 + 0.15 * k), h * (0.85 + 0.15 * k)
    x, y = int(cx - w2 / 2), int(cy - h2 / 2); w2, h2 = int(w2), int(h2)
    if w2 < 4: return
    mask = Image.new('L', (w2, h2)); ImageDraw.Draw(mask).rounded_rectangle((0, 0, w2 - 1, h2 - 1), h2 // 2, fill=int(255 * a))
    region = base.crop((x, y, x + w2, y + h2)).filter(ImageFilter.GaussianBlur(14))
    glass = Image.new('RGBA', (w2, h2), (255, 255, 255, 0))
    gl = Image.new('RGBA', (w2, h2)); gd = ImageDraw.Draw(gl)
    gd.rounded_rectangle((0, 0, w2 - 1, h2 - 1), h2 // 2, fill=(255, 255, 255, int(45 * a)), outline=(255, 255, 255, int(200 * a)), width=4)
    gd.rounded_rectangle((h2 // 3, 6, w2 - h2 // 3, h2 // 2.6), h2 // 5, fill=(255, 255, 255, int(40 * a)))
    base.paste(region, (x, y), mask)
    base.alpha_composite(gl, (x, y))
    t = text_layer([text], int(60 * (0.85 + 0.15 * k)), (255, 255, 255, int(255 * a)), int(cy), shadow=False, align_cx=int(cx))
    base.alpha_composite(t)

def wrap(text, f, maxw=940):
    lines, cur = [], ''
    d = ImageDraw.Draw(Image.new('RGB', (1, 1)))
    for w in text.split(' '):
        nxt = (cur + ' ' + w).strip()
        if d.textlength(nxt + '_', font=f) > maxw and cur: lines.append(cur); cur = w
        else: cur = nxt
    lines.append(cur); return lines

def typed_text(t, c):
    """text typed so far in circle c at time t, letter by letter in sync with speech"""
    t0, t1, splits = c
    bounds = splits + [t1]
    for i in range(len(splits)):
        if bounds[i] <= t < bounds[i + 1]:
            ws = [w for w in words if bounds[i] - 0.01 <= w['s'] < bounds[i + 1] - 0.01]
            out = []
            for w in ws:
                txt = w['w'].strip(' ,.?!').upper()
                if t >= w['e']: out.append(txt)
                elif t >= w['s']:
                    out.append(txt[:max(1, int(len(txt) * (t - w['s']) / max(0.05, w['e'] - w['s'])) + 1)])
            return ' '.join(out)
    return ''

def type_events():
    ev = []
    for c in CIRCLES:
        prev = ''
        for n in range(int(c[0] * FPS), int(c[1] * FPS)):
            cur = typed_text(n / FPS, c)
            if len(cur.replace(' ', '')) > len(prev.replace(' ', '')) and cur.startswith(prev[:len(cur)]): ev.append(n / FPS)
            elif len(cur) > 0 and not cur.startswith(prev[:1]): ev.append(n / FPS)
            prev = cur
    return ev

def circle_frame(src, t, c):
    out = Image.new('RGBA', (W, H), NAVY + (255,))
    ccx, ccy, r = 540, 690, 420
    vid = zoom_frame(src, 1.3 + 0.01 * (t - c[0]))
    m = Image.new('L', (W, H)); ImageDraw.Draw(m).ellipse((ccx - r, ccy - r, ccx + r, ccy + r), fill=255)
    layer = Image.new('RGBA', (W, H)); layer.paste(vid, (ccx - FACE[0], ccy - FACE[1] - 30))
    out.paste(layer, (0, 0), m)
    txt = typed_text(t, c)
    f = font(58); lines = wrap(txt, f) if txt else ['']
    blink = int(t * 2.5) % 2 == 0
    lines[-1] = lines[-1] + ('_' if (blink or (txt and not txt.endswith(' '))) else ' ')
    d = ImageDraw.Draw(out); lh = 66; y0 = 1310
    for i, ln in enumerate(lines):
        full = d.textlength(ln.rstrip('_ ') + '_', font=f)
        d.text(((W - full) / 2, y0 + i * lh), ln, font=f, fill=ORANGE + (255,))
    return out

def light_leak(a, b, k):
    """a->b crossfade with warm light flash; k in 0..1"""
    mix = Image.blend(a, b, min(1, max(0, (k - 0.35) / 0.3)))
    g = math.sin(math.pi * k)
    arr = np.asarray(mix).astype(np.float32)
    yy, xx = np.mgrid[0:H:8, 0:W:8]
    leak = np.exp(-(((xx - W * 0.3) / (W * 0.7)) ** 2 + ((yy - H * 0.35) / (H * 0.6)) ** 2))
    leak = np.asarray(Image.fromarray((leak * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)).astype(np.float32) / 255
    col = np.array([255, 170, 70], np.float32)
    arr = arr + (col - arr * 0.3) * (leak[..., None] * g * 0.95)
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

def zoom_blur(img, k):
    acc = np.zeros((H, W, 3), np.float32); n = 8
    for i in range(n):
        z = 1 + 0.12 * k * i / (n - 1)
        acc += np.asarray(zoom_frame(img, z, (W // 2, H // 2)), np.float32)
    return Image.fromarray((acc / n).astype(np.uint8))

# ---------------- subtitles ----------------
def clean(w): return w.strip(' ,.?!:;').upper()
SUBS = []
for i, w in enumerate(words):
    nxt = words[i + 1]['s'] if i + 1 < len(words) else w['e'] + 0.4
    SUBS.append((w['s'], min(nxt, w['e'] + 0.35), clean(w['w'])))
_sub_cache = {}
def sub_layer(txt):
    if txt not in _sub_cache: _sub_cache[txt] = text_layer([txt], 70, (255, 255, 255, 255), 1480)
    return _sub_cache[txt]

# ---------------- render ----------------
def render_frame(src, t):
    for c in CIRCLES:
        if c[1] - 0.25 <= t < c[1] + 0.25:
            k = (t - (c[1] - 0.25)) / 0.5
            return light_leak(base_frame(src, t, c), base_frame(src, t, None), k)
    circ = next((c for c in CIRCLES if c[0] <= t < c[1]), None)
    out = base_frame(src, t, circ)
    for b in WHIPS:
        k = 1 - abs(t - b) / 0.12
        if k > 0: out = whip(out, k)
    for b in ZBLUR:
        k = 1 - abs(t - b) / 0.1
        if k > 0: out = zoom_blur(out, k)
    return out

ZBLUR = [8.74]

def base_frame(src, t, circ):
    if circ:
        out = circle_frame(src, t, circ)
    else:
        out = zoom_frame(src, zoom_at(t)).convert('RGBA')
        if TINT[0] <= t < TINT[1]:
            a = min(1, (t - TINT[0]) / 0.3, (TINT[1] - t) / 0.3)
            out.alpha_composite(fade(TINT_L, a))
            for pt, txt, row, slot in PILLS:
                if t >= pt:
                    a2, k = ease_pop(t, pt)
                    draw_pill(out, txt, row, slot, k, a2 * min(1, (TINT[1] - t) / 0.3))
        for t0, t1, txt in BIGTEXT:
            if t0 <= t < t1:
                _, k = ease_pop(t, t0, 0.25)
                out.alpha_composite(fade(scale_layer(text_layer([txt], 150, (255, 255, 255, 255), 300, extrude=10), 0.7 + 0.3 * k, 540, 300), k))
        for t0, t1, pos in ARROWS:
            if t0 <= t < t1:
                global _ARROW
                if _ARROW is None: _ARROW = arrow_layer(1.45)
                a, k = ease_pop(t, t0, 0.25)
                im = _ARROW.resize((max(1, int(_ARROW.width * (0.6 + 0.4 * k))), max(1, int(_ARROW.height * (0.6 + 0.4 * k)))))
                bob = int(14 * math.sin(2 * math.pi * 1.6 * (t - t0)))
                out.alpha_composite(fade(im, a), (pos[0] - im.width // 2, pos[1] - im.height // 2 + bob))
        for t0, t1, txt in TOPTITLE:
            if t0 <= t < t1:
                _, k = ease_pop(t, t0, 0.25)
                out.alpha_composite(fade(scale_layer(text_layer([txt], 110, ORANGE + (255,), 300), 0.7 + 0.3 * k, 540, 300), k))
    s = next((s for s in SUBS if s[0] <= t < s[1]), None)
    if s and not circ: out.alpha_composite(sub_layer(s[2]))
    return out.convert('RGB')

WHIPS = [c[0] for c in CIRCLES]
def whip(img, k):
    a = np.asarray(img).astype(np.float32); shift = int(160 * k); n = 10
    acc = np.zeros_like(a)
    for i in range(n): acc += np.roll(a, int(shift * i / (n - 1)) - shift // 2, axis=1)
    return Image.fromarray((acc / n).astype(np.uint8))

if __name__ == '__main__':
    if PREVIEW:
        for t in [1, 4, 9, 13, 18, 21, 26, 28.5, 30, 35, 40]:
            raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(t), '-i', SRC, '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
            render_frame(Image.frombytes('RGB', (W, H), raw), t).resize((360, 640)).save(f'prev/{t:05.1f}.jpg')
        sys.exit()
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', SRC, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-r', str(FPS), '-'], stdout=subprocess.PIPE)
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-i', 'out/mix.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '19',
                            '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', 'out/preview.mp4'], stdin=subprocess.PIPE)
    n = 0
    while True:
        raw = dec.stdout.read(W * H * 3)
        if len(raw) < W * H * 3: break
        enc.stdin.write(render_frame(Image.frombytes('RGB', (W, H), raw), n / FPS).tobytes()); n += 1
        if n % 150 == 0: print(n, flush=True)
    enc.stdin.close(); enc.wait(); print('frames', n)
