import json, subprocess, os, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import infographics as ig

W, H, FPS = 1080, 1920, 30
SRC = 'src/video.mp4'  # overridden by timeline.py
FONT = os.path.expanduser('~/.fonts/Montserrat-Black.ttf')
NAVY = (2, 6, 74)
ORANGE = (244, 122, 58)
FACE = (560, 680)  # zoom anchor (face) in source pixels
PREVIEW = '--preview' in sys.argv
FINAL = '--final' in sys.argv  # high-quality export for download

words = json.load(open('words.json'))
DUR0 = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', SRC], capture_output=True, text=True).stdout)
DUR = DUR0

# ---------------- timeline (defaults; per-video values live in ./timeline.py) ----------------
END = None          # trim (seconds), e.g. black tail
ZOOMS = [(0, 1.0)]
CIRCLES = []        # (start, end, [phrase split times], centre_y)
TINT = (0, 0)
PILLS = []          # (time, text, row, slot)
BIGTEXT = []        # (t0, t1, text)
HEADINGS = []       # (t0, t1, number, title)
XMARKS = []         # (t0, t1, (x, y))
TOPTITLE = []       # (t0, t1, text with \n)
ARROWS = []         # (t0, t1, (x, y))
ZBLUR = []          # zoom-blur transition times (hard cuts, punches)
SPECS = []          # (t0, t1, n): HF2-style list, rows 1..n shown, row n active
SPEC_ROWS = []      # [(label, value)]
PILL_END = None     # end of pills when there is no TINT
PILL_Y = 120        # top of first pill row (move down to chest to keep the head clear)
QUOTES = []         # (t0, t1, text) white quote card with orange quote mark, top of frame
BROLL = []          # (t0, t1) cutaways: frame stays still (no zoom, no push, centre anchor)
CUTS = []           # hard cut times; the zoom anchor is constant within each shot/zoom segment
CALENDARS = []      # (t0, t1, label1, row1_t, label2, row2_t)
STAMPS = []         # (t0, t1, text, (x, y))
CHECKS = []         # (t0, t1, (x, y), radius)
BADGES = []         # (t0, t1, text, centre_y)
LINKS = []          # (t0, t1, left, right, label, t_line, t_label, centre_y)
PLANS = []          # navy layout: {'t0','t1','title','title_t','items':[(t, text)],'cy'} card on top, soft oval below
SFX = []            # (file, time, peak_db, 'start'|'peak')
FIXES = {}          # word index -> corrected text (ASR fixes)
MERGE = []          # (index, text): merge word index with next into text
sys.path.insert(0, os.getcwd())
from timeline import *  # noqa
for i, txt in FIXES.items(): words[i]['w'] = txt  # indices = original words.json
for i, txt in sorted(MERGE, reverse=True):
    words[i] = dict(words[i], w=txt, e=words[i + 1]['e']); del words[i + 1]
DUR = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', SRC], capture_output=True, text=True).stdout)
if END: DUR = min(DUR, END)

_faces = json.load(open('faces.json')) if os.path.exists('faces.json') else None
def in_broll(t): return any(a <= t < b for a, b in BROLL)

_anchor = {}
def face_at(t):
    """constant face anchor per (shot x zoom segment): no frame-to-frame jitter; centre on B-roll"""
    if in_broll(t) or not _faces: return (W // 2, H // 2) if _faces else FACE
    marks = sorted({0.0, DUR} | {z for z, _ in ZOOMS} | set(CUTS) | {x for ab in BROLL for x in ab})
    a = max(m for m in marks if m <= t); b = min([m for m in marks if m > t] or [DUR])
    if (a, b) not in _anchor:
        pts = [(x, y) for ft, x, y, w in _faces if a <= ft < b and x is not None]
        _anchor[(a, b)] = (int(np.median([p[0] for p in pts])), int(np.median([p[1] for p in pts]))) if len(pts) >= 3 else (W // 2, H // 2)
    return _anchor[(a, b)]

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
    if in_broll(t): return 1.0
    s = ZOOMS[0][1]; prev = s; t0 = 0
    for zt, zs in ZOOMS:
        if t >= zt: prev, s, t0 = s, zs, zt
    e = min(1, (t - t0) / 0.18)  # quick eased punch
    e = 1 - (1 - e) ** 3
    base = prev + (s - prev) * e
    tp = max([t0] + [c for c in CUTS if c <= t] + [b for a, b in BROLL if b <= t])
    return base * (1 + min(0.04, 0.012 * (t - tp)))  # slow push, restarts after each cut, capped

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

def zoom_frame(img, z, anchor=None):
    anchor = anchor or FACE
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
    h = 124; y = PILL_Y + row * 150
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
    gd.rounded_rectangle((0, 0, w2 - 1, h2 - 1), h2 // 2, fill=(2, 6, 74, int(150 * a)) if PILL_Y > 600 else (255, 255, 255, int(45 * a)), outline=(255, 255, 255, int(200 * a)), width=4)
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
    t0, t1, splits = c[:3]
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

OVAL = (470, 500)        # soft oval radii (x, y)
_masks = {}
def soft_mask(ccy):
    if ccy not in _masks:
        m = Image.new('L', (W, H)); rx, ry = OVAL
        ImageDraw.Draw(m).ellipse((540 - rx + 60, ccy - ry + 60, 540 + rx - 60, ccy + ry - 60), fill=255)
        _masks[ccy] = m.filter(ImageFilter.GaussianBlur(55))
    return _masks[ccy]

def circle_frame(src, t, c):
    out = Image.new('RGBA', (W, H), NAVY + (255,))
    ccx, ccy = 540, c[3]
    f0 = face_at(t)
    vid = zoom_frame(src, 1.3 + 0.01 * (t - c[0]), f0)
    m = soft_mask(ccy)
    layer = Image.new('RGBA', (W, H)); layer.paste(vid, (ccx - f0[0], ccy - f0[1] - 30))
    out.paste(layer, (0, 0), m)
    txt = typed_text(t, c)
    f = font(58); lines = wrap(txt, f) if txt else ['']
    blink = int(t * 2.5) % 2 == 0
    lines[-1] = lines[-1] + ('_' if (blink or (txt and not txt.endswith(' '))) else ' ')
    d = ImageDraw.Draw(out); lh = 66; y0 = ccy + OVAL[1] + 30
    for i, ln in enumerate(lines):
        full = d.textlength(ln.rstrip('_ ') + '_', font=f)
        d.text(((W - full) / 2, y0 + i * lh), ln, font=f, fill=ORANGE + (255,))
    return out

_glow = {}
def glow_text(txt, sz, cy):
    if (txt, sz, cy) not in _glow:
        core = text_layer([txt], sz, ORANGE + (255,), cy, shadow=False)
        g = text_layer([txt], sz, (255, 150, 40, 255), cy, shadow=False).filter(ImageFilter.GaussianBlur(18))
        g.alpha_composite(g); g.alpha_composite(core); _glow[(txt, sz, cy)] = g
    return _glow[(txt, sz, cy)]

MED = os.path.expanduser('~/.fonts/Montserrat-Medium.ttf')
_med = {}
def med(sz):
    if sz not in _med: _med[sz] = ImageFont.truetype(MED, sz)
    return _med[sz]

def specs_layer(t, t0, t1, n):
    """HF2 (mk-specs-list) look: navy top scrim, rows slide in, orange underline draws; earlier rows dimmed"""
    a_all = min(1, (t - t0) / 0.3, (t1 - t) / 0.3)
    lay = Image.new('RGBA', (W, H))
    lay.alpha_composite(fade(TINT_L, a_all * 0.95))
    d = ImageDraw.Draw(lay); x = 80; y0 = 95; rh = 104
    for i in range(n):
        label, value = SPEC_ROWS[i]
        active = i == n - 1
        if active:
            a, k = ease_pop(t, t0 + 0.1, 0.5); dx = int(-36 * (1 - k))
        else:
            a, dx = 1.0, 0
        al = int(255 * a * a_all * (1.0 if active else 0.55))
        y = y0 + i * rh
        d.text((x + dx, y), label, font=font(56), fill=(255, 255, 255, al))
        lw = d.textlength(label, font=font(56))
        d.text((x + dx + lw + 18, y + 11), value, font=med(46), fill=(220, 222, 235, al))
        ly = y + 74
        d.rectangle((x, ly, x + 760, ly + 3), fill=(255, 255, 255, int(46 * a_all)))
        if active:
            _, kk = ease_pop(t, t0 + 0.25, 0.8); fw = int(760 * kk)
        else:
            fw = 760
        if fw > 0: d.rectangle((x, ly, x + fw, ly + 4), fill=ORANGE + (int(255 * a_all * (1 if active else 0.6)),))
    return lay

_quotes = {}
def quote_layer(txt, cy=300):
    if txt in _quotes: return _quotes[txt]
    f = font(52); lines = wrap(txt.upper(), f, 840); lh = 62
    h = lh * len(lines) + 70; w = 960; x0, y0 = (W - w) // 2, cy - h // 2
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    sh = Image.new('RGBA', (W, H)); ImageDraw.Draw(sh).rounded_rectangle((x0, y0 + 10, x0 + w, y0 + h + 10), 26, fill=(0, 0, 0, 120))
    lay.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)))
    d.rounded_rectangle((x0, y0, x0 + w, y0 + h), 26, fill=(255, 255, 255, 250))
    d.rectangle((x0 + 30, y0 - 38, x0 + 108, y0 + 40), fill=ORANGE + (255,))
    d.text((x0 + 69, y0 + 18), '\u201c', font=font(96), fill=(255, 255, 255, 255), anchor='mm')
    for i, ln in enumerate(lines):
        d.text((W // 2, y0 + 38 + i * lh + lh // 2), ln, font=f, fill=(20, 20, 24, 255), anchor='mm')
    _quotes[txt] = lay; return lay

def xmark_layer(p, pos, size=150):
    """red hand-drawn X; p = draw progress 0..1"""
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    x, y = pos; s = size / 2
    strokes = [((x - s, y - s), (x + s, y + s)), ((x + s, y - s), (x - s, y + s))]
    for i, (p0, p1) in enumerate(strokes):
        q = min(1, max(0, p * 2 - i))
        if q <= 0: continue
        e = (p0[0] + (p1[0] - p0[0]) * q, p0[1] + (p1[1] - p0[1]) * q)
        d.line([p0, e], fill=(225, 25, 30, 255), width=30)
        d.ellipse((p0[0] - 15, p0[1] - 15, p0[0] + 15, p0[1] + 15), fill=(225, 25, 30, 255))
        d.ellipse((e[0] - 15, e[1] - 15, e[0] + 15, e[1] + 15), fill=(225, 25, 30, 255))
    sh = lay.filter(ImageFilter.GaussianBlur(10)); sh2 = Image.new('RGBA', (W, H)); sh2.alpha_composite(fade(sh, 0.6), (0, 6))
    sh2.alpha_composite(lay); return sh2

def plan_frame(src, t, p):
    out = Image.new('RGBA', (W, H), NAVY + (255,))
    ccy = p['cy']; f0 = face_at(t)
    vid = zoom_frame(src, 1.25, f0)
    layer = Image.new('RGBA', (W, H)); layer.paste(vid, (540 - f0[0], ccy - f0[1] - 30))
    out.paste(layer, (0, 0), soft_mask(ccy))
    out.alpha_composite(ig.plan_card(t, p, font))
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
    for c in CIRCLES + [(p['t0'], p['t1'], p) for p in PLANS]:
        if c[1] - 0.25 <= t < c[1] + 0.25:
            k = (t - (c[1] - 0.25)) / 0.5
            cc = c if t < c[1] else None
            return light_leak(base_frame(src, t, c), base_frame(src, t, None), k)
    circ = next((c for c in CIRCLES + [(p['t0'], p['t1'], p) for p in PLANS] if c[0] <= t < c[1]), None)
    out = base_frame(src, t, circ)
    for b in WHIPS:
        k = 1 - abs(t - b) / 0.12
        if k > 0: out = whip(out, k)
    for b in ZBLUR:
        k = 1 - abs(t - b) / 0.1
        if k > 0: out = zoom_blur(out, k)
    return out

def base_frame(src, t, circ):
    if circ and isinstance(circ[2], dict):
        out = plan_frame(src, t, circ[2])
    elif circ:
        out = circle_frame(src, t, circ)
    else:
        out = zoom_frame(src, zoom_at(t), face_at(t)).convert('RGBA')
        if TINT[0] <= t < TINT[1]:
            a = min(1, (t - TINT[0]) / 0.3, (TINT[1] - t) / 0.3)
            out.alpha_composite(fade(TINT_L, a))
        pend = PILL_END or TINT[1]
        if PILLS and PILLS[0][0] <= t < pend:
            for pt, txt, row, slot in PILLS:
                if t >= pt:
                    a2, k = ease_pop(t, pt)
                    draw_pill(out, txt, row, slot, k, a2 * min(1, (pend - t) / 0.3))
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
                out.alpha_composite(fade(scale_layer(text_layer(txt.split('\n'), 74, ORANGE + (255,), 250), 0.7 + 0.3 * k, 540, 250), k))
        for t0, t1, num, title in HEADINGS:
            if t0 <= t < t1:
                _, k = ease_pop(t, t0, 0.25); _, k2 = ease_pop(t, t0 + 0.12, 0.25)
                a = min(1, (t1 - t) / 0.2)
                out.alpha_composite(fade(scale_layer(glow_text(str(num), 150, 150), 0.6 + 0.4 * k, 540, 150), k * a))
                out.alpha_composite(fade(scale_layer(text_layer(title.split('\n'), 66, (255, 255, 255, 255), 290), 0.8 + 0.2 * k2, 540, 290), k2 * a))
        for t0, t1, n in SPECS:
            if t0 <= t < t1:
                out.alpha_composite(specs_layer(t, t0, t1, n))
        for e in CALENDARS:
            if e[0] <= t < e[1]: out.alpha_composite(ig.calendar(t, e, font))
        for e in STAMPS:
            if e[0] <= t < e[1]: out.alpha_composite(ig.stamp(t, e, font))
        for e in CHECKS:
            if e[0] <= t < e[1]: out.alpha_composite(ig.check(t, e, font))
        for e in BADGES:
            if e[0] <= t < e[1]: out.alpha_composite(ig.badge(t, e, font))
        for e in LINKS:
            if e[0] <= t < e[1]: out.alpha_composite(ig.link(t, e, font))
        for t0, t1, txt in QUOTES:
            if t0 <= t < t1:
                a, k = ease_pop(t, t0, 0.3)
                a = min(a, (t1 - t) / 0.2)
                out.alpha_composite(fade(scale_layer(quote_layer(txt), 0.85 + 0.15 * k, 540, 300), a))
        for t0, t1, pos in XMARKS:
            if t0 <= t < t1:
                out.alpha_composite(xmark_layer(min(1, (t - t0) / 0.3), pos))
    s = next((s for s in SUBS if s[0] <= t < s[1]), None)
    if s and not circ: out.alpha_composite(sub_layer(s[2]))
    return out.convert('RGB')

WHIPS = [c[0] for c in CIRCLES] + [p['t0'] for p in PLANS]
def whip(img, k):
    a = np.asarray(img).astype(np.float32); shift = int(160 * k); n = 10
    acc = np.zeros_like(a)
    for i in range(n): acc += np.roll(a, int(shift * i / (n - 1)) - shift // 2, axis=1)
    return Image.fromarray((acc / n).astype(np.uint8))

if __name__ == '__main__':
    if PREVIEW:
        os.makedirs('prev', exist_ok=True)
        for t in [float(x) for x in sys.argv[2:]] or [1, 4, 9, 13, 18, 21, 26, 28.5, 30, 35, 40]:
            raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(t), '-i', SRC, '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
            render_frame(Image.frombytes('RGB', (W, H), raw), t).resize((360, 640)).save(f'prev/{t:05.1f}.jpg')
        sys.exit()
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', SRC, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-r', str(FPS), '-'], stdout=subprocess.PIPE)
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-i', 'out/mix.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'slow' if FINAL else 'medium', '-crf', '14' if FINAL else '19', '-profile:v', 'high',
                            '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '320k' if FINAL else '192k', '-shortest', '-movflags', '+faststart', 'out/final.mp4' if FINAL else 'out/preview.mp4'], stdin=subprocess.PIPE)
    n = 0
    while True:
        raw = dec.stdout.read(W * H * 3)
        if len(raw) < W * H * 3 or n / FPS >= DUR: break
        enc.stdin.write(render_frame(Image.frombytes('RGB', (W, H), raw), n / FPS).tobytes()); n += 1
        if n % 150 == 0: print(n, flush=True)
    dec.kill(); enc.stdin.close(); enc.wait(); print('frames', n)
