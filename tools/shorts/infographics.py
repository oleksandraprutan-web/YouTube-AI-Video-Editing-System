"""Infographic overlays for the shorts renderer (all 1080x1920 RGBA layers, Montserrat).

Each draw_* takes the time t and one timeline entry and returns a full-frame RGBA layer.
Placement keeps the head clear: overlays live in the top band (y < ~430) or on the chest.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 1080, 1920
NAVY = (2, 6, 74)
ORANGE = (244, 122, 58)
GREEN = (46, 196, 110)
RED = (225, 25, 30)


def ease(t, t0, d=0.3):
    x = min(1, max(0, (t - t0) / d))
    return 1 - (1 - x) ** 3


def _alpha(lay, a):
    if a >= 0.999: return lay
    r, g, b, al = lay.split()
    return Image.merge('RGBA', (r, g, b, al.point(lambda v: int(v * a))))


def _shadow(lay, blur=14, a=0.55, dy=8):
    sh = Image.new('RGBA', (W, H)); sh.alpha_composite(_alpha(lay.filter(ImageFilter.GaussianBlur(blur)), a), (0, dy))
    k = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    r, g, b, al = sh.split(); black = Image.merge('RGBA', (r.point(lambda v: 0), g.point(lambda v: 0), b.point(lambda v: 0), al))
    k.alpha_composite(black); k.alpha_composite(lay); return k


def _glass(d, box, r, a=1.0):
    d.rounded_rectangle(box, r, fill=NAVY + (int(205 * a),), outline=(255, 255, 255, int(70 * a)), width=3)


def calendar(t, e, font):
    """two-week alternating custody: row1 'U CIEBIE' (orange cells), row2 'Z MATKĄ' (white cells)"""
    t0, t1, l1, r1t, l2, r2t = e
    a = min(1, (t - t0) / 0.25, (t1 - t) / 0.25)
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    x0, y0, cw, gap = 70, 130, 84, 10
    _glass(d, (x0 - 30, y0 - 30, W - x0 + 30, y0 + 2 * (cw + 26) + 4), 34, a)
    for row, (label, rt, col) in enumerate([(l1, r1t, ORANGE), (l2, r2t, (255, 255, 255))]):
        y = y0 + row * (cw + 26)
        ka = ease(t, rt - 0.15, 0.3)
        d.text((x0, y + cw / 2), label, font=font(40), fill=(255, 255, 255, int(255 * a * ka)), anchor='lm')
        for i in range(7):
            cx = x0 + 300 + i * (cw + gap)
            kc = ease(t, rt + i * 0.07, 0.22)
            d.rounded_rectangle((cx, y, cx + cw, y + cw), 14, outline=(255, 255, 255, int(90 * a)), width=3)
            if kc > 0:
                s = cw * (0.5 + 0.5 * kc); o = (cw - s) / 2
                d.rounded_rectangle((cx + o, y + o, cx + o + s, y + o + s), 14, fill=col + (int(255 * a * kc),))
    return lay


def stamp(t, e, font):
    """red rubber stamp slammed on screen (rotated outline box + text)"""
    t0, t1, text, (cx, cy) = e
    k = ease(t, t0, 0.18); a = min(1, (t1 - t) / 0.2)
    f = font(84); tw = ImageDraw.Draw(Image.new('RGB', (1, 1))).textlength(text, font=f)
    w, h = int(tw + 90), 150
    s = Image.new('RGBA', (w + 40, h + 40)); d = ImageDraw.Draw(s)
    d.rounded_rectangle((20, 20, 20 + w, 20 + h), 22, outline=RED + (255,), width=12)
    d.text(((w + 40) / 2, (h + 40) / 2 + 4), text, font=f, fill=RED + (255,), anchor='mm')
    sc = 1.7 - 0.7 * k
    s = s.rotate(8, resample=Image.BICUBIC, expand=True)
    s = s.resize((max(1, int(s.width * sc)), max(1, int(s.height * sc))), Image.BICUBIC)
    lay = Image.new('RGBA', (W, H)); lay.alpha_composite(_alpha(s, min(1, k * 1.5) * a), (int(cx - s.width / 2), int(cy - s.height / 2)))
    return _shadow(lay, 10, 0.4, 6)


def check(t, e, font):
    """green circle with a tick that draws itself"""
    t0, t1, (cx, cy), r = e
    a = min(1, (t1 - t) / 0.2); k = ease(t, t0, 0.22); p = ease(t, t0 + 0.12, 0.35)
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    rr = r * (0.6 + 0.4 * k)
    d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=GREEN + (int(255 * a * k),))
    pts = [(cx - 0.45 * r, cy + 0.02 * r), (cx - 0.12 * r, cy + 0.32 * r), (cx + 0.48 * r, cy - 0.3 * r)]
    if p > 0:
        segs = [(pts[0], pts[1]), (pts[1], pts[2])]; L = [math.dist(*s) for s in segs]; tot = sum(L) * p
        path = [pts[0]]
        for (p0, p1), l in zip(segs, L):
            q = min(1, tot / l); path.append((p0[0] + (p1[0] - p0[0]) * q, p0[1] + (p1[1] - p0[1]) * q)); tot -= l
            if tot <= 0: break
        d.line(path, fill=(255, 255, 255, int(255 * a)), width=int(r * 0.2), joint='curve')
        for q in (path[0], path[-1]):
            w = r * 0.1; d.ellipse((q[0] - w, q[1] - w, q[0] + w, q[1] + w), fill=(255, 255, 255, int(255 * a)))
    return _shadow(lay, 16, 0.45, 8)


def badge(t, e, font):
    """warning pill: orange '!' circle + text, slides down from the top"""
    t0, t1, text, cy = e
    k = ease(t, t0, 0.3); a = min(1, (t1 - t) / 0.2) * k
    f = font(52); tw = ImageDraw.Draw(Image.new('RGB', (1, 1))).textlength(text, font=f)
    h = 120; w = int(tw + h + 70); x = (W - w) // 2; y = int(cy - h / 2 - 40 * (1 - k))
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    _glass(d, (x, y, x + w, y + h), h // 2, a)
    d.ellipse((x + 14, y + 14, x + h - 14, y + h - 14), fill=ORANGE + (int(255 * a),))
    d.text((x + h / 2, y + h / 2 + 2), '!', font=font(66), fill=(255, 255, 255, int(255 * a)), anchor='mm')
    d.text((x + h + 20, y + h / 2 + 2), text, font=f, fill=(255, 255, 255, int(255 * a)), anchor='lm')
    return _shadow(lay)


def link(t, e, font):
    """two parties connected by an orange line that draws; label pops on the line"""
    t0, t1, left, right, label, t_line, t_label, cy = e
    a = min(1, (t - t0) / 0.25, (t1 - t) / 0.25)
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    r = 95; xl, xr = 170, W - 170
    pl = ease(t, t_line, 0.7)
    if pl > 0:
        xe = xl + r + (xr - xl - 2 * r) * pl
        d.line((xl + r, cy, xe, cy), fill=ORANGE + (int(255 * a),), width=10)
    for i, (x, txt) in enumerate([(xl, left), (xr, right)]):
        k = ease(t, t0 + i * 0.15, 0.3); rr = r * (0.7 + 0.3 * k)
        d.ellipse((x - rr, cy - rr, x + rr, cy + rr), fill=NAVY + (int(230 * a * k),), outline=ORANGE + (int(255 * a * k),), width=8)
        d.text((x, cy + 2), txt, font=font(38 if len(txt) > 3 else 52), fill=(255, 255, 255, int(255 * a * k)), anchor='mm')
    kl = ease(t, t_label, 0.25)
    if kl > 0:
        f = font(46); tw = d.textlength(label, font=f); w, h = tw + 60, 84
        y = cy - 125 - 20 * (1 - kl)
        d.rounded_rectangle((W / 2 - w / 2, y - h / 2, W / 2 + w / 2, y + h / 2), h // 2, fill=ORANGE + (int(255 * a * kl),))
        d.text((W / 2, y + 2), label, font=f, fill=(255, 255, 255, int(255 * a * kl)), anchor='mm')
    return _shadow(lay)


def plan_card(t, e, font):
    """white document card on navy: title + checklist items that tick in"""
    title, title_t, items = e['title'], e['title_t'], e['items']
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    k = ease(t, e['t0'] + 0.05, 0.35)
    x0, y0, x1 = 110, int(110 + 60 * (1 - k)), W - 110
    y1 = y0 + 150 + 108 * len(items)
    d.rounded_rectangle((x0, y0, x1, y1), 30, fill=(255, 255, 255, int(250 * k)))
    d.rectangle((x0 + 50, y0 - 26, x0 + 120, y0 + 26), fill=ORANGE + (int(255 * k),))
    kt = ease(t, title_t, 0.3)
    d.text(((x0 + x1) / 2, y0 + 82), title, font=font(54), fill=NAVY + (int(255 * kt),), anchor='mm')
    d.line((x0 + 60, y0 + 136, x1 - 60, y0 + 136), fill=(220, 222, 235, int(255 * kt)), width=3)
    for i, (it, txt) in enumerate(items):
        ki = ease(t, it, 0.3); y = y0 + 200 + i * 108
        if ki <= 0: continue
        bx = x0 + 70
        d.rounded_rectangle((bx, y - 30, bx + 60, y + 30), 12, fill=GREEN + (int(255 * ki),))
        d.line([(bx + 14, y + 2), (bx + 26, y + 15), (bx + 47, y - 13)], fill=(255, 255, 255, int(255 * ki)), width=8, joint='curve')
        d.text((bx + 95 - 20 * (1 - ki), y + 2), txt, font=font(48), fill=(20, 20, 30, int(255 * ki)), anchor='lm')
    return _shadow(lay, 18, 0.5, 10)


def months(t, e, font):
    """row of N month dots filling one by one + label (e.g. '6 MIESIĘCY')"""
    t0, t1, n, label, t_fill, cy = e
    a = min(1, (t - t0) / 0.25, (t1 - t) / 0.25)
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    r, gap = 46, 30; total = n * 2 * r + (n - 1) * gap; x0 = (W - total) / 2
    _glass(d, (x0 - 50, cy - 150, x0 + total + 50, cy + r + 40), 34, a)
    kl = ease(t, t0, 0.3)
    d.text((W / 2, cy - 92), label, font=font(56), fill=(255, 255, 255, int(255 * a * kl)), anchor='mm')
    for i in range(n):
        cx = x0 + r + i * (2 * r + gap)
        k = ease(t, t_fill + i * 0.22, 0.25)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(255, 255, 255, int(110 * a)), width=4)
        if k > 0:
            rr = r * k
            d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=ORANGE + (int(255 * a),))
            d.text((cx, cy + 2), str(i + 1), font=font(36), fill=(255, 255, 255, int(255 * a * k)), anchor='mm')
    return _shadow(lay)


def cap_bar(t, e, font):
    """liability capped: red 'DŁUGI' bar grows, stops at an orange limit line 'AKTYWA SPADKU'"""
    t0, t1, t_bar, t_cap, cy = e
    a = min(1, (t - t0) / 0.25, (t1 - t) / 0.25)
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    x0, x1 = 90, W - 90; lim = x0 + (x1 - x0) * 0.58
    _glass(d, (x0 - 30, cy - 150, x1 + 30, cy + 175), 34, a)
    d.text((x0, cy - 100), 'TWOJA ODPOWIEDZIALNOŚĆ', font=font(40), fill=(255, 255, 255, int(255 * a)), anchor='lm')
    kc = ease(t, t_cap, 0.4)
    grow = ease(t, t_bar, 1.4)
    want = x0 + (x1 - x0) * 0.95 * grow
    end = min(want, lim) if kc > 0 else want
    d.rounded_rectangle((x0, cy - 30, x1, cy + 30), 30, fill=(255, 255, 255, int(40 * a)))
    if end > x0 + 10:
        d.rounded_rectangle((x0, cy - 30, end, cy + 30), 30, fill=RED + (int(235 * a),))
        d.text((x0 + 24, cy + 1), 'DŁUGI', font=font(34), fill=(255, 255, 255, int(255 * a)), anchor='lm')
    if kc > 0:
        ly = int(52 * kc)
        d.line((lim, cy - ly, lim, cy + ly), fill=ORANGE + (int(255 * a),), width=10)
        f = font(40); lbl = 'LIMIT = AKTYWA SPADKU'; tw = d.textlength(lbl, font=f)
        px = min(max(lim, x0 + tw / 2 + 30), x1 - tw / 2 - 30); py = cy + 112
        d.rounded_rectangle((px - tw / 2 - 28, py - 34, px + tw / 2 + 28, py + 34), 34, fill=ORANGE + (int(255 * a * kc),))
        d.text((px, py + 2), lbl, font=f, fill=(255, 255, 255, int(255 * a * kc)), anchor='mm')
    return _shadow(lay)


def _house(d, cx, cy, s, col):
    d.polygon([(cx - s, cy - 0.1 * s), (cx, cy - s), (cx + s, cy - 0.1 * s)], fill=col)
    d.rectangle((cx - 0.75 * s, cy - 0.1 * s, cx + 0.75 * s, cy + 0.8 * s), fill=col)
    d.rectangle((cx - 0.2 * s, cy + 0.3 * s, cx + 0.2 * s, cy + 0.8 * s), fill=NAVY + (255,))


def _card(d, cx, cy, s, col):
    d.rounded_rectangle((cx - s, cy - 0.65 * s, cx + s, cy + 0.65 * s), int(0.18 * s), fill=col)
    d.rectangle((cx - s, cy - 0.35 * s, cx + s, cy - 0.12 * s), fill=NAVY + (255,))
    d.text((cx + 0.45 * s, cy + 0.32 * s), '%', font=None, fill=NAVY + (255,))


def _num(v):
    return f'{int(round(v)):,}'.replace(',', ' ') + ' zł'


def scene_inheritance(t, e, font):
    """full-frame animated example on navy: balance of assets vs debts, counters, verdict"""
    t0, t1, cfg = e
    lay = Image.new('RGBA', (W, H), NAVY + (255,)); d = ImageDraw.Draw(lay)
    # slow drifting light blobs
    glow = Image.new('RGBA', (W, H)); g = ImageDraw.Draw(glow)
    for i, (bx, by, br, col) in enumerate([(250, 500, 420, (40, 70, 200)), (850, 1300, 520, (30, 50, 170)), (600, 900, 300, (244, 122, 58))]):
        ph = (t - t0) * 0.35 + i * 2.1
        x = bx + 60 * math.sin(ph); y = by + 50 * math.cos(ph * 0.8)
        g.ellipse((x - br, y - br, x + br, y + br), fill=col + (60 if i < 2 else 26,))
    lay.alpha_composite(glow.filter(ImageFilter.GaussianBlur(120)))
    d = ImageDraw.Draw(lay)
    # title pill
    k = ease(t, cfg['t_title'], 0.3)
    if k > 0:
        f = font(54); tw = d.textlength(cfg['title'], font=f)
        y = 230 - 30 * (1 - k)
        d.rounded_rectangle((W / 2 - tw / 2 - 40, y - 52, W / 2 + tw / 2 + 40, y + 52), 52, fill=ORANGE + (int(255 * k),))
        d.text((W / 2, y + 2), cfg['title'], font=f, fill=(255, 255, 255, int(255 * k)), anchor='mm')
    # balance
    ka = ease(t, cfg['t_asset'], 0.4); kd = ease(t, cfg['t_debt'], 0.4)
    wa = cfg['asset'] * ease(t, cfg['t_asset_num'], 1.2); wd = cfg['debt'] * ease(t, cfg['t_debt_num'], 1.0)
    tilt = 0.0 if wa + wd == 0 else 9 * (wa - wd) / max(cfg['asset'], 1)
    piv = (W / 2, 520); L = 380
    ang = math.radians(tilt)
    lx, ly = piv[0] - L * math.cos(ang), piv[1] + L * math.sin(ang)
    rx, ry = piv[0] + L * math.cos(ang), piv[1] - L * math.sin(ang)
    kb = ease(t, t0, 0.4)
    wcol = (255, 255, 255, int(235 * kb))
    d.polygon([(piv[0], piv[1] + 10), (piv[0] - 70, piv[1] + 520), (piv[0] + 70, piv[1] + 520)], fill=(255, 255, 255, int(40 * kb)))
    d.rounded_rectangle((piv[0] - 160, piv[1] + 515, piv[0] + 160, piv[1] + 545), 15, fill=wcol)
    d.line((lx, ly, rx, ry), fill=wcol, width=14)
    d.ellipse((piv[0] - 22, piv[1] - 22, piv[0] + 22, piv[1] + 22), fill=ORANGE + (int(255 * kb),))
    for (px, py, kk, lbl, val, col, icon) in [(lx, ly, ka, cfg['asset_label'], wa, GREEN, 'house'), (rx, ry, kd, cfg['debt_label'], wd, RED, 'card')]:
        hy = py + 210
        d.line((px - 120, hy - 40, px, py), fill=(255, 255, 255, int(160 * kb)), width=4)
        d.line((px + 120, hy - 40, px, py), fill=(255, 255, 255, int(160 * kb)), width=4)
        d.chord((px - 160, hy - 120, px + 160, hy + 40), 0, 180, fill=(255, 255, 255, int(230 * kb)))
        if kk > 0:
            s = 70 * (0.6 + 0.4 * kk)
            if icon == 'house': _house(d, px, hy - 70 - s * 0.2, s, col + (int(255 * kk),))
            else: _card(d, px, hy - 90, s, col + (int(255 * kk),))
            d.text((px, hy + 90), lbl, font=font(40), fill=(255, 255, 255, int(255 * kk)), anchor='mm')
            d.text((px, hy + 150), _num(val), font=font(56), fill=col + (int(255 * kk),), anchor='mm')
    # equation + verdict
    ke = ease(t, cfg['t_eq'], 0.35)
    if ke > 0:
        y = 1430 + 20 * (1 - ke)
        d.text((W / 2, y), f"{_num(cfg['asset'])} − {_num(cfg['debt'])}", font=font(50), fill=(255, 255, 255, int(255 * ke)), anchor='mm')
        d.text((W / 2, y + 80), f"= {_num(cfg['asset'] - cfg['debt'])}", font=font(66), fill=GREEN + (int(255 * ke),), anchor='mm')
    kv = ease(t, cfg['t_verdict'], 0.25)
    if kv > 0:
        f = font(60); tw = d.textlength(cfg['verdict'], font=f); w = tw + 150; y = 1660
        sc = 0.8 + 0.2 * kv
        d.rounded_rectangle((W / 2 - w / 2 * sc, y - 60 * sc, W / 2 + w / 2 * sc, y + 60 * sc), int(60 * sc), fill=GREEN + (int(255 * kv),))
        cx0 = W / 2 - w / 2 * sc + 55
        d.line([(cx0 - 18, y), (cx0 - 4, y + 16), (cx0 + 22, y - 16)], fill=(255, 255, 255, int(255 * kv)), width=9, joint='curve')
        d.text((W / 2 + 30, y + 2), cfg['verdict'], font=f, fill=(255, 255, 255, int(255 * kv)), anchor='mm')
    return lay
