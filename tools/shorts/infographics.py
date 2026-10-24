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
        y = 1160 + 20 * (1 - ke)
        d.text((W / 2, y), f"{_num(cfg['asset'])} − {_num(cfg['debt'])}", font=font(50), fill=(255, 255, 255, int(255 * ke)), anchor='mm')
        d.text((W / 2, y + 80), f"= {_num(cfg['asset'] - cfg['debt'])}", font=font(66), fill=GREEN + (int(255 * ke),), anchor='mm')
    kv = ease(t, cfg['t_verdict'], 0.25)
    if kv > 0:
        f = font(60); tw = d.textlength(cfg['verdict'], font=f); w = tw + 150; y = 1370
        sc = 0.8 + 0.2 * kv
        d.rounded_rectangle((W / 2 - w / 2 * sc, y - 60 * sc, W / 2 + w / 2 * sc, y + 60 * sc), int(60 * sc), fill=GREEN + (int(255 * kv),))
        cx0 = W / 2 - w / 2 * sc + 55
        d.line([(cx0 - 18, y), (cx0 - 4, y + 16), (cx0 + 22, y - 16)], fill=(255, 255, 255, int(255 * kv)), width=9, joint='curve')
        d.text((W / 2 + 30, y + 2), cfg['verdict'], font=f, fill=(255, 255, 255, int(255 * kv)), anchor='mm')
    return lay


def _phone(lay, cx, cy, w, h, k, bubbles, t):
    d = ImageDraw.Draw(lay)
    x0, y0 = cx - w / 2, cy - h / 2
    d.rounded_rectangle((x0 - 14, y0 - 14, x0 + w + 14, y0 + h + 14), 60, fill=(15, 18, 40, int(255 * k)))
    d.rounded_rectangle((x0, y0, x0 + w, y0 + h), 48, fill=(245, 246, 250, int(255 * k)))
    d.rounded_rectangle((cx - 60, y0 + 14, cx + 60, y0 + 40), 13, fill=(15, 18, 40, int(255 * k)))
    for i, (bt, side) in enumerate(bubbles):
        kb = ease(t, bt, 0.25)
        if kb <= 0: continue
        by = y0 + 90 + i * 120; bw = w * 0.62
        bx = x0 + 26 if side == 'L' else x0 + w - 26 - bw
        bx += (-40 if side == 'L' else 40) * (1 - kb)
        col = (225, 228, 238) if side == 'L' else (60, 110, 230)
        d.rounded_rectangle((bx, by, bx + bw, by + 90), 34, fill=col + (int(255 * kb * k),))
        lc = (120, 125, 140) if side == 'L' else (230, 236, 255)
        d.rounded_rectangle((bx + 26, by + 26, bx + bw - 40, by + 40), 7, fill=lc + (int(255 * kb * k),))
        d.rounded_rectangle((bx + 26, by + 52, bx + bw * 0.6, by + 66), 7, fill=lc + (int(255 * kb * k),))


def scene_evidence(t, e, font):
    """navy animation: messages appear in a phone, screenshot flash, then a documentation checklist ticks"""
    t0, t1, cfg = e
    lay = Image.new('RGBA', (W, H), NAVY + (255,))
    glow = Image.new('RGBA', (W, H)); g = ImageDraw.Draw(glow)
    for i, (bx, by, br, col) in enumerate([(250, 500, 420, (40, 70, 200)), (850, 1350, 520, (30, 50, 170)), (650, 800, 300, (244, 122, 58))]):
        ph = (t - t0) * 0.35 + i * 2.1
        x = bx + 60 * math.sin(ph); y = by + 50 * math.cos(ph * 0.8)
        g.ellipse((x - br, y - br, x + br, y + br), fill=col + (60 if i < 2 else 24,))
    lay.alpha_composite(glow.filter(ImageFilter.GaussianBlur(120)))
    d = ImageDraw.Draw(lay)
    k = ease(t, t0, 0.3)
    f = font(56); tw = d.textlength(cfg['title'], font=f); y = 190 - 30 * (1 - k)
    d.rounded_rectangle((W / 2 - tw / 2 - 40, y - 52, W / 2 + tw / 2 + 40, y + 52), 52, fill=ORANGE + (int(255 * k),))
    d.text((W / 2, y + 2), cfg['title'], font=f, fill=(255, 255, 255, int(255 * k)), anchor='mm')
    # phone: shrinks/moves up when the checklist arrives
    kc = ease(t, cfg['t_list'], 0.6)
    pw, ph_ = 430 - 110 * kc, 760 - 160 * kc
    pcx, pcy = W / 2 - 330 * kc, 960 + 10 * kc
    _phone(lay, pcx, pcy, pw, ph_, ease(t, t0 + 0.1, 0.4), [(b, s) for b, s in cfg['bubbles']], t)
    d = ImageDraw.Draw(lay)
    # screenshot: white flash over phone + 'ZRZUT EKRANU' label + corner brackets
    ts = cfg['t_shot']
    fl = max(0, 1 - abs(t - ts) / 0.15) if t >= ts - 0.15 else 0
    if fl > 0:
        x0, y0 = pcx - pw / 2, pcy - ph_ / 2
        d.rounded_rectangle((x0, y0, x0 + pw, y0 + ph_), 48, fill=(255, 255, 255, int(230 * fl)))
    ksh = ease(t, ts, 0.3)
    if ksh > 0 and t < cfg['t_list'] + 0.2:
        a = ksh * (1 - ease(t, cfg['t_list'] - 0.2, 0.4))
        x0, y0, x1, y1 = pcx - pw / 2 - 40, pcy - ph_ / 2 - 40, pcx + pw / 2 + 40, pcy + ph_ / 2 + 40
        L = 70
        for (cx, cy, sx, sy) in [(x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)]:
            d.line([(cx, cy + sy * L), (cx, cy), (cx + sx * L, cy)], fill=ORANGE + (int(255 * a),), width=12, joint='curve')
        f2 = font(44); lbl = cfg['shot_label']; tw2 = d.textlength(lbl, font=f2); ly = y1 + 70
        d.rounded_rectangle((W / 2 - tw2 / 2 - 30, ly - 38, W / 2 + tw2 / 2 + 30, ly + 38), 38, fill=(255, 255, 255, int(240 * a)))
        d.text((W / 2, ly + 2), lbl, font=f2, fill=NAVY + (int(255 * a),), anchor='mm')
    # checklist card on the right/below
    if kc > 0:
        x0, y0, x1 = 400, 640, W - 40
        items = cfg['items']; y1 = y0 + 150 + 170 * len(items)
        d.rounded_rectangle((x0, y0 + 40 * (1 - kc), x1, y1 + 40 * (1 - kc)), 30, fill=(255, 255, 255, int(245 * kc)))
        d.text(((x0 + x1) / 2, y0 + 72 + 40 * (1 - kc)), cfg['list_title'], font=font(54), fill=NAVY + (int(255 * kc),), anchor='mm')
        for i, (it, txt) in enumerate(items):
            ki = ease(t, it, 0.3)
            yy = y0 + 220 + i * 170 + 40 * (1 - kc)
            bx = x0 + 40
            d.rounded_rectangle((bx, yy - 40, bx + 80, yy + 40), 18, outline=(200, 205, 220, int(255 * kc)), width=5)
            if ki > 0:
                d.rounded_rectangle((bx, yy - 40, bx + 80, yy + 40), 18, fill=GREEN + (int(255 * ki),))
                d.line([(bx + 18, yy + 2), (bx + 35, yy + 20), (bx + 63, yy - 18)], fill=(255, 255, 255, int(255 * ki)), width=10, joint='curve')
            lines = txt.split('\n')
            for j, ln in enumerate(lines):
                d.text((bx + 110, yy + (j - (len(lines) - 1) / 2) * 54), ln, font=font(46), fill=(20, 20, 30, int(255 * max(ki, 0.35) * kc)), anchor='lm')
    return lay


def strike(t, e, font):
    """dark glass pill with a word that gets struck through by a red pen line"""
    t0, t1, text, t_strike, (cx, cy) = e
    a = min(1, (t1 - t) / 0.2) * ease(t, t0, 0.3)
    f = font(76); tw = ImageDraw.Draw(Image.new('RGB', (1, 1))).textlength(text, font=f)
    w, h = tw + 120, 150; x0, y0 = cx - w / 2, cy - h / 2
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    _glass(d, (x0, y0, x0 + w, y0 + h), h // 2, a)
    ks = ease(t, t_strike, 0.35)
    d.text((cx, cy + 3), text, font=f, fill=(255, 255, 255, int(255 * a * (1 - 0.45 * ks))), anchor='mm')
    if ks > 0:
        xs, xe = x0 + 30, x0 + 30 + (w - 60) * ks
        d.line((xs, cy + 10, xe, cy - 6), fill=RED + (int(255 * a),), width=16)
    return _shadow(lay)


def doc_card(t, e, font):
    """white document card at chest level: icon + 3 lines appearing with the words"""
    t0, t1, lines, cy = e
    a = min(1, (t1 - t) / 0.25) * ease(t, t0, 0.35)
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    x0, x1 = 170, W - 170; h = 250; y0 = cy - h / 2 + 40 * (1 - ease(t, t0, 0.35))
    d.rounded_rectangle((x0, y0, x1, y0 + h), 26, fill=(255, 255, 255, int(248 * a)))
    d.rectangle((x0 + 40, y0 - 20, x0 + 96, y0 + 20), fill=ORANGE + (int(255 * a),))
    ix, iy = x0 + 40, y0 + 55
    d.rounded_rectangle((ix, iy, ix + 115, iy + 150), 14, fill=NAVY + (int(255 * a),))
    for j in range(4):
        d.rounded_rectangle((ix + 20, iy + 30 + j * 28, ix + 95 - (24 if j == 3 else 0), iy + 41 + j * 28), 6, fill=(255, 255, 255, int(220 * a)))
    tx = ix + 150
    sizes = [30, 42, 28]; ys = [y0 + 72, y0 + 125, y0 + 182]
    cols = [(110, 115, 135), NAVY, ORANGE]
    for (lt, txt), sz, yy, col in zip(lines, sizes, ys, cols):
        k = ease(t, lt, 0.3)
        if k > 0:
            d.text((tx - 20 * (1 - k), yy), txt, font=font(sz), fill=col + (int(255 * a * k),), anchor='lm')
    return _shadow(lay, 16, 0.5, 8)


def checklist(t, e, font):
    """dark glass card with rows that tick green one by one"""
    t0, t1, items, cy = e
    a = min(1, (t1 - t) / 0.25) * ease(t, t0, 0.3)
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    rh = 112; h = 60 + rh * len(items); x0, x1 = 170, W - 170; y0 = cy - h / 2
    _glass(d, (x0, y0, x1, y0 + h), 34, a)
    for i, (it, txt) in enumerate(items):
        k = ease(t, it, 0.3); yy = y0 + 30 + rh * i + rh / 2; bx = x0 + 45
        d.rounded_rectangle((bx, yy - 36, bx + 72, yy + 36), 16, outline=(255, 255, 255, int(120 * a)), width=4)
        if k > 0:
            d.rounded_rectangle((bx, yy - 36, bx + 72, yy + 36), 16, fill=GREEN + (int(255 * a * k),))
            d.line([(bx + 16, yy + 2), (bx + 31, yy + 18), (bx + 57, yy - 16)], fill=(255, 255, 255, int(255 * a * k)), width=9, joint='curve')
        d.text((bx + 105, yy + 2), txt, font=font(54), fill=(255, 255, 255, int(255 * a * max(k, 0.3))), anchor='lm')
    return _shadow(lay)


def words(t, e, font):
    """simple: words stack one by one, white with an orange dot, no background"""
    t0, t1, items, cy = e
    a = min(1, (t1 - t) / 0.25)
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    lh = 80; y0 = cy - lh * (len(items) - 1) / 2
    for i, (it, txt) in enumerate(items):
        k = ease(t, it, 0.25)
        if k <= 0: continue
        f = font(60); tw = d.textlength(txt, font=f); y = y0 + i * lh + 18 * (1 - k)
        x = W / 2 - tw / 2 + 22
        d.ellipse((x - 52, y - 12, x - 28, y + 12), fill=ORANGE + (int(255 * a * k),))
        d.text((x, y + 2), txt, font=f, fill=(255, 255, 255, int(255 * a * k)), anchor='lm')
    return _shadow(lay, 10, 0.6, 5)


def income(t, e, font):
    """two income bars (RODZIC A / B) + result pill"""
    t0, t1, t_bars, ratio, t_res, res_text, res_col, cy = e
    a = min(1, (t - t0) / 0.25, (t1 - t) / 0.25)
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    x0, x1 = 110, W - 110
    _glass(d, (x0 - 30, cy - 170, x1 + 30, cy + 110), 34, a)
    d.text((W / 2, cy - 125), 'ZAROBKI RODZICÓW', font=font(40), fill=(255, 255, 255, int(255 * a)), anchor='mm')
    bx = x0 + 230; full = x1 - bx
    for i, (lbl, frac, col) in enumerate([('RODZIC A', 1.0, ORANGE), ('RODZIC B', ratio, (255, 255, 255))]):
        y = cy - 50 + i * 95
        k = ease(t, t_bars + i * 0.15, 0.9)
        d.text((x0, y), lbl, font=font(36), fill=(255, 255, 255, int(255 * a)), anchor='lm')
        d.rounded_rectangle((bx, y - 26, x1, y + 26), 26, fill=(255, 255, 255, int(35 * a)))
        w = full * frac * k
        if w > 30: d.rounded_rectangle((bx, y - 26, bx + w, y + 26), 26, fill=col + (int(240 * a),))
    kr = ease(t, t_res, 0.3)
    if kr > 0:
        f = font(44); tw = d.textlength(res_text, font=f); y = cy + 175 - 15 * (1 - kr)
        d.rounded_rectangle((W / 2 - tw / 2 - 34, y - 42, W / 2 + tw / 2 + 34, y + 42), 42, fill=res_col + (int(255 * a * kr),))
        d.text((W / 2, y + 2), res_text, font=f, fill=(255, 255, 255, int(255 * a * kr)), anchor='mm')
    return _shadow(lay)


def scene_two_homes(t, e, font):
    """navy animation: two houses with living-standard bars that even out"""
    t0, t1, cfg = e
    lay = Image.new('RGBA', (W, H), NAVY + (255,))
    glow = Image.new('RGBA', (W, H)); g = ImageDraw.Draw(glow)
    for i, (bx, by, br, col) in enumerate([(250, 500, 420, (40, 70, 200)), (850, 1350, 520, (30, 50, 170)), (600, 900, 300, (244, 122, 58))]):
        ph = (t - t0) * 0.35 + i * 2.1
        g.ellipse((bx + 60 * math.sin(ph) - br, by + 50 * math.cos(ph * .8) - br, bx + 60 * math.sin(ph) + br, by + 50 * math.cos(ph * .8) + br), fill=col + (60 if i < 2 else 24,))
    lay.alpha_composite(glow.filter(ImageFilter.GaussianBlur(120)))
    d = ImageDraw.Draw(lay)
    k = ease(t, t0, 0.3)
    f = font(60); tw = d.textlength(cfg['title'], font=f); y = 230 - 30 * (1 - k)
    d.rounded_rectangle((W / 2 - tw / 2 - 44, y - 56, W / 2 + tw / 2 + 44, y + 56), 56, fill=ORANGE + (int(255 * k),))
    d.text((W / 2, y + 2), cfg['title'], font=f, fill=(255, 255, 255, int(255 * k)), anchor='mm')
    kh = ease(t, cfg['t_homes'], 0.4)
    keq = ease(t, cfg['t_equal'], 0.9)
    base = 1250; maxh = 420
    for i, (cx, start) in enumerate([(300, 0.9), (780, 0.35)]):
        if kh <= 0: break
        lvl = start + (0.75 - start) * keq
        _house(d, cx, 640, 120 * (0.6 + 0.4 * kh), (255, 255, 255, int(255 * kh)))
        d.text((cx, 820), f'DOM {i + 1}', font=font(44), fill=(255, 255, 255, int(255 * kh)), anchor='mm')
        d.rounded_rectangle((cx - 70, base - maxh, cx + 70, base), 22, fill=(255, 255, 255, int(40 * kh)))
        hh = maxh * lvl * ease(t, cfg['t_homes'] + 0.2, 0.7)
        col = ORANGE if keq < 0.5 else GREEN
        if hh > 10: d.rounded_rectangle((cx - 70, base - hh, cx + 70, base), 22, fill=col + (int(255 * kh),))
    if kh > 0:
        d.text((W / 2, base + 70), 'POZIOM ŻYCIA DZIECKA', font=font(42), fill=(255, 255, 255, int(255 * kh)), anchor='mm')
    kv = ease(t, cfg['t_verdict'], 0.3)
    if kv > 0:
        f = font(54); tw = d.textlength(cfg['verdict'], font=f); y = 1500
        d.rounded_rectangle((W / 2 - tw / 2 - 50, y - 56, W / 2 + tw / 2 + 50, y + 56), 56, fill=GREEN + (int(255 * kv),))
        d.text((W / 2, y + 2), cfg['verdict'], font=f, fill=(255, 255, 255, int(255 * kv)), anchor='mm')
    return lay


def donut(t, e, font):
    """50/50 donut that fills in two halves + centre label; optional question line below"""
    t0, t1, t_a, t_b, centre, t_q, q_text, cy = e
    a = min(1, (t - t0) / 0.25, (t1 - t) / 0.25)
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    r, wd = 150, 46; cx = W / 2
    _glass(d, (90, cy - r - 40, W - 90, cy + r + 40), 40, a)
    box = (cx - r, cy - r, cx + r, cy + r)
    d.ellipse(box, outline=(255, 255, 255, int(70 * a)), width=wd)
    ka, kb = ease(t, t_a, 0.6), ease(t, t_b, 0.6)
    if ka > 0: d.arc(box, -90, -90 + 180 * ka, fill=ORANGE + (int(255 * a),), width=wd)
    if kb > 0: d.arc(box, 90, 90 + 180 * kb, fill=(255, 255, 255, int(255 * a)), width=wd)
    d.text((cx, cy + 4), centre, font=font(70), fill=(255, 255, 255, int(255 * a)), anchor='mm')
    for x, lbl, col, k in [(cx - r - 120, 'MAMA', ORANGE, ka), (cx + r + 120, 'TATA', (255, 255, 255), kb)]:
        d.text((x, cy), lbl, font=font(42), fill=col + (int(255 * a * k),), anchor='mm')
    kq = ease(t, t_q, 0.3)
    if kq > 0:
        f = font(46); tw = d.textlength(q_text, font=f); y = cy + r + 85
        _glass(d, (cx - tw / 2 - 34, y - 42, cx + tw / 2 + 34, y + 42), 42, a * kq)
        d.text((cx, y + 2), q_text, font=f, fill=(255, 255, 255, int(255 * a * kq)), anchor='mm')
    return _shadow(lay)


def warn(t, e, font):
    """red warning triangle that pops in with a label"""
    t0, t1, label, cy = e
    k = ease(t, t0, 0.25); a = min(1, (t1 - t) / 0.2)
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    s = 120 * (0.5 + 0.5 * k); cx = W / 2
    d.polygon([(cx, cy - s), (cx - s * 1.1, cy + s * 0.8), (cx + s * 1.1, cy + s * 0.8)], fill=RED + (int(255 * a * k),))
    d.text((cx, cy + s * 0.15), '!', font=font(int(130 * (0.5 + 0.5 * k))), fill=(255, 255, 255, int(255 * a * k)), anchor='mm')
    if label:
        d.text((cx, cy + 170), label, font=font(60), fill=(255, 255, 255, int(255 * a * k)), anchor='mm')
    return _shadow(lay, 12, 0.5, 6)


def headline(t, e, font):
    """big white lines (no background) + red stamp slammed over them"""
    t0, t1, lines, t_stamp, stamp_text, cy = e
    a = min(1, (t - t0) / 0.25, (t1 - t) / 0.25)
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    lh = 86
    _glass(d, (110, cy - lh / 2 * len(lines) - 40, W - 110, cy + lh / 2 * len(lines) + 40), 34, a)
    for i, ln in enumerate(lines):
        k = ease(t, t0 + i * 0.12, 0.3)
        d.text((W / 2, cy - lh / 2 * (len(lines) - 1) + i * lh + 15 * (1 - k)), ln, font=font(70), fill=(255, 255, 255, int(255 * a * k)), anchor='mm')
    lay = _shadow(lay)
    if t >= t_stamp:
        lay.alpha_composite(stamp(t, (t_stamp, t1, stamp_text, (W / 2 + 160, cy + lh / 2 * len(lines) + 40)), font))
    return lay


def split_costs(t, e, font):
    """expenses split 50/50 between parents (rows tick in), then '+ ALIMENTY WYRÓWNAWCZE' pill"""
    t0, t1, rows, t_plus, plus_text, cy = e
    a = min(1, (t - t0) / 0.25, (t1 - t) / 0.25)
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    x0, x1 = 90, W - 90; rh = 100; top = cy - 130
    _glass(d, (x0, top - 70, x1, top + 60 + rh * len(rows)), 34, a)
    d.text((x0 + 280, top - 22), 'RODZIC A', font=font(30), fill=ORANGE + (int(255 * a),), anchor='mm')
    d.text((x1 - 170, top - 22), 'RODZIC B', font=font(30), fill=(255, 255, 255, int(255 * a)), anchor='mm')
    for i, (rt, lbl) in enumerate(rows):
        k = ease(t, rt, 0.5); y = top + 50 + i * rh
        d.text((x0 + 30, y), lbl, font=font(38), fill=(255, 255, 255, int(255 * a * max(k, .3))), anchor='lm')
        bx0, bx1 = x0 + 330, x1 - 30; mid = (bx0 + bx1) / 2
        d.rounded_rectangle((bx0, y - 24, bx1, y + 24), 24, fill=(255, 255, 255, int(35 * a)))
        if k > 0:
            d.rounded_rectangle((mid - (mid - bx0) * k, y - 24, mid, y + 24), 24, fill=ORANGE + (int(240 * a),))
            d.rounded_rectangle((mid, y - 24, mid + (bx1 - mid) * k, y + 24), 24, fill=(255, 255, 255, int(235 * a)))
            d.text((mid - 70, y + 1), '50%', font=font(28), fill=(255, 255, 255, int(255 * a * k)), anchor='mm')
            d.text((mid + 70, y + 1), '50%', font=font(28), fill=NAVY + (int(255 * a * k),), anchor='mm')
    kp = ease(t, t_plus, 0.3)
    if kp > 0:
        f = font(44); tw = d.textlength(plus_text, font=f); y = top + 60 + rh * len(rows) + 70 - 15 * (1 - kp)
        d.rounded_rectangle((W / 2 - tw / 2 - 34, y - 42, W / 2 + tw / 2 + 34, y + 42), 42, fill=ORANGE + (int(255 * a * kp),))
        d.text((W / 2, y + 2), plus_text, font=f, fill=(255, 255, 255, int(255 * a * kp)), anchor='mm')
    return _shadow(lay)


def not_equal(t, e, font):
    """'A' ≠ 'B' takeaway: left text, big orange ≠, right text appear with the words"""
    t0, t1, (ta, txa), (tn, sym), (tb, txb), cy = e
    a = min(1, (t1 - t) / 0.25)
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    _glass(d, (110, cy - 190, W - 110, cy + 190), 34, a * ease(t, ta - 0.1, 0.3))
    for (tt, txt, y, sz, col) in [(ta, txa, cy - 120, 64, (255, 255, 255)), (tn, sym, cy, 120, ORANGE), (tb, txb, cy + 120, 64, (255, 255, 255))]:
        k = ease(t, tt, 0.3)
        if k > 0:
            f = font(int(sz * (0.8 + 0.2 * k)))
            d.text((W / 2, y + 15 * (1 - k)), txt, font=f, fill=col + (int(255 * a * k),), anchor='mm')
    return _shadow(lay, 10, 0.7, 5)
