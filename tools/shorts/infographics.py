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
    t0, t1, text, (cx, cy) = e[:4]; ss = e[4] if len(e) > 4 else 1.0
    k = ease(t, t0, 0.18); a = min(1, (t1 - t) / 0.2)
    f = font(int(84 * ss)); tw = ImageDraw.Draw(Image.new('RGB', (1, 1))).textlength(text, font=f)
    w, h = int(tw + 90 * ss), int(150 * ss)
    s = Image.new('RGBA', (w + 40, h + 40)); d = ImageDraw.Draw(s)
    d.rounded_rectangle((20, 20, 20 + w, 20 + h), 22, outline=RED + (255,), width=max(5, int(12 * ss)))
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
    """rows that tick green one by one; style 'glass' (card) or 'dim' (no card, soft dark shade behind)"""
    t0, t1, items, cy = e[:4]; style = e[4] if len(e) > 4 else 'glass'
    a = min(1, (t1 - t) / 0.25) * ease(t, t0, 0.3)
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    fs = 54 if style == 'glass' else 44; bs = 72 if style == 'glass' else 58; rh = 112 if style == 'glass' else 88
    tw = max(d.textlength(txt, font=font(fs)) for _, txt in items)
    gw = bs + 33 + tw; x0 = (W - gw) / 2; h = 60 + rh * len(items); y0 = cy - h / 2
    if style == 'glass':
        _glass(d, (x0 - 45, y0, x0 + gw + 45, y0 + h), 34, a)
    else:
        sh = Image.new('L', (W, H)); ImageDraw.Draw(sh).rounded_rectangle((x0 - 70, y0 - 20, x0 + gw + 70, y0 + h + 20), 80, fill=int(170 * a))
        sh = sh.filter(ImageFilter.GaussianBlur(45))
        dark = Image.new('RGBA', (W, H), (0, 0, 10, 255)); dark.putalpha(sh); lay.alpha_composite(dark); d = ImageDraw.Draw(lay)
    for i, (it, txt) in enumerate(items):
        k = ease(t, it, 0.3); yy = y0 + 30 + rh * i + rh / 2; bx = x0
        d.rounded_rectangle((bx, yy - bs / 2, bx + bs, yy + bs / 2), int(bs * .22), outline=(255, 255, 255, int(140 * a)), width=4)
        if k > 0:
            d.rounded_rectangle((bx, yy - bs / 2, bx + bs, yy + bs / 2), int(bs * .22), fill=GREEN + (int(255 * a * k),))
            q = bs / 72
            d.line([(bx + 16 * q, yy + 2 * q), (bx + 31 * q, yy + 18 * q), (bx + 57 * q, yy - 16 * q)], fill=(255, 255, 255, int(255 * a * k)), width=max(6, int(9 * q)), joint='curve')
        d.text((bx + bs + 33, yy + 2), txt, font=font(fs), fill=(255, 255, 255, int(255 * a * max(k, 0.3))), anchor='lm')
    return _shadow(lay, 10, 0.6, 5) if style == 'dim' else _shadow(lay)


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
    t0, t1, lines, t_stamp, stamp_text, cy = e[:6]; sc = e[6] if len(e) > 6 else 1.0
    a = min(1, (t - t0) / 0.25, (t1 - t) / 0.25)
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    lh = 86 * sc; hw = max(430 * sc, max(d.textlength(ln, font=font(int(70 * sc))) for ln in lines) / 2 + 45 * sc)
    _glass(d, (W / 2 - hw, cy - lh / 2 * len(lines) - 40 * sc, W / 2 + hw, cy + lh / 2 * len(lines) + 40 * sc), int(34 * sc), a)
    for i, ln in enumerate(lines):
        k = ease(t, t0 + i * 0.12, 0.3)
        d.text((W / 2, cy - lh / 2 * (len(lines) - 1) + i * lh + 15 * (1 - k)), ln, font=font(int(70 * sc)), fill=(255, 255, 255, int(255 * a * k)), anchor='mm')
    lay = _shadow(lay)
    if t >= t_stamp:
        lay.alpha_composite(stamp(t, (t_stamp, t1, stamp_text, (W / 2 + 160 * sc, cy + lh / 2 * len(lines) + 95 * sc), sc), font))
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
            fz = sz
            while fz > 30 and d.textlength(txt, font=font(fz)) > W - 300: fz -= 2
            f = font(int(fz * (0.8 + 0.2 * k)))
            d.text((W / 2, y + 15 * (1 - k)), txt, font=f, fill=col + (int(255 * a * k),), anchor='mm')
    return _shadow(lay, 10, 0.7, 5)


def result_pill(t, e, font):
    """single coloured result pill that pops in"""
    t0, t1, text, col, cy = e
    k = ease(t, t0, 0.3); a = min(1, (t1 - t) / 0.2) * k
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    fz = 52
    while fz > 30 and d.textlength(text, font=font(fz)) > W - 220: fz -= 2
    f = font(int(fz * (0.85 + 0.15 * k))); tw = d.textlength(text, font=f); h = 110
    d.rounded_rectangle((W / 2 - tw / 2 - 44, cy - h / 2, W / 2 + tw / 2 + 44, cy + h / 2), h // 2, fill=tuple(col) + (int(255 * a),))
    d.text((W / 2, cy + 2), text, font=f, fill=(255, 255, 255, int(255 * a)), anchor='mm')
    return _shadow(lay)


def _envelope(d, cx, cy, s, a):
    d.rounded_rectangle((cx - s, cy - 0.65 * s, cx + s, cy + 0.65 * s), int(0.12 * s), fill=(255, 255, 255, int(255 * a)))
    d.line([(cx - s, cy - 0.65 * s), (cx, cy + 0.1 * s), (cx + s, cy - 0.65 * s)], fill=NAVY + (int(255 * a),), width=max(3, int(s * 0.08)))


def _clock(d, cx, cy, r, a, p):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 255, 255, int(255 * a)))
    d.ellipse((cx - r * .82, cy - r * .82, cx + r * .82, cy + r * .82), outline=NAVY + (int(255 * a),), width=max(3, int(r * .08)))
    ang = -math.pi / 2 + 2 * math.pi * p
    d.line((cx, cy, cx + r * .62 * math.cos(ang), cy + r * .62 * math.sin(ang)), fill=ORANGE + (int(255 * a),), width=max(4, int(r * .1)))
    d.line((cx, cy, cx, cy - r * .45), fill=NAVY + (int(255 * a),), width=max(4, int(r * .1)))


def scene_rent_steps(t, e, font):
    """navy animation: 3 unpaid months crossed out, then step 1 (written notice) and step 2 (extra deadline)"""
    t0, t1, cfg = e
    lay = Image.new('RGBA', (W, H), NAVY + (255,))
    glow = Image.new('RGBA', (W, H)); g = ImageDraw.Draw(glow)
    for i, (bx, by, br, col) in enumerate([(250, 500, 420, (40, 70, 200)), (850, 1350, 520, (30, 50, 170)), (600, 900, 300, (244, 122, 58))]):
        ph = (t - t0) * 0.35 + i * 2.1
        g.ellipse((bx + 60 * math.sin(ph) - br, by + 50 * math.cos(ph * .8) - br, bx + 60 * math.sin(ph) + br, by + 50 * math.cos(ph * .8) + br), fill=col + (60 if i < 2 else 24,))
    lay.alpha_composite(glow.filter(ImageFilter.GaussianBlur(120)))
    d = ImageDraw.Draw(lay)
    k = ease(t, t0, 0.3)
    f = font(56); tw = d.textlength(cfg['title'], font=f); y = 220 - 30 * (1 - k)
    d.rounded_rectangle((W / 2 - tw / 2 - 44, y - 54, W / 2 + tw / 2 + 44, y + 54), 54, fill=ORANGE + (int(255 * k),))
    d.text((W / 2, y + 2), cfg['title'], font=f, fill=(255, 255, 255, int(255 * k)), anchor='mm')
    # months row
    km = ease(t, cfg['t_months'], 0.4)
    if km > 0:
        d.text((W / 2, 440), cfg['months_label'], font=font(46), fill=(255, 255, 255, int(255 * km)), anchor='mm')
        cw, gap = 260, 40; x0 = W / 2 - (3 * cw + 2 * gap) / 2
        for i in range(3):
            x = x0 + i * (cw + gap); y0 = 500
            d.rounded_rectangle((x, y0, x + cw, y0 + 200), 24, fill=(255, 255, 255, int(235 * km)))
            d.rounded_rectangle((x, y0, x + cw, y0 + 54), 24, fill=ORANGE + (int(255 * km),))
            d.rectangle((x, y0 + 30, x + cw, y0 + 54), fill=ORANGE + (int(255 * km),))
            d.text((x + cw / 2, y0 + 130), 'CZYNSZ', font=font(38), fill=NAVY + (int(255 * km),), anchor='mm')
            kx = ease(t, cfg['t_x'][i], 0.25)
            if kx > 0:
                s = 70; cx, cy = x + cw / 2, y0 + 120
                for (p0, p1) in [((cx - s, cy - s), (cx + s, cy + s)), ((cx + s, cy - s), (cx - s, cy + s))]:
                    e2 = (p0[0] + (p1[0] - p0[0]) * kx, p0[1] + (p1[1] - p0[1]) * kx)
                    d.line([p0, e2], fill=RED + (255,), width=18)
    # steps
    for j, (ts, num, txt, icon) in enumerate(cfg['steps']):
        ks = ease(t, ts, 0.4)
        if ks <= 0: continue
        y0 = 860 + j * 330 + 40 * (1 - ks); x0, x1 = 90, W - 90
        card = Image.new('RGBA', (W, H)); ImageDraw.Draw(card).rounded_rectangle((x0, y0, x1, y0 + 270), 30, fill=(255, 255, 255, int(30 * ks)), outline=(255, 255, 255, int(110 * ks)), width=3)
        lay.alpha_composite(card); d = ImageDraw.Draw(lay)
        d.ellipse((x0 + 40, y0 + 85, x0 + 140, y0 + 185), fill=ORANGE + (int(255 * ks),))
        d.text((x0 + 90, y0 + 137), str(num), font=font(58), fill=(255, 255, 255, int(255 * ks)), anchor='mm')
        if icon == 'envelope': _envelope(d, x1 - 110, y0 + 135, 70, ks)
        else: _clock(d, x1 - 110, y0 + 135, 68, ks, ease(t, ts, 2.0))
        lines = txt.split('\n')
        for li, ln in enumerate(lines):
            d.text((x0 + 180, y0 + 135 + (li - (len(lines) - 1) / 2) * 62), ln, font=font(44), fill=(255, 255, 255, int(255 * ks)), anchor='lm')
    return lay


# ---------- animated set (short 7) ----------
def debt_counter(t, e, font):
    """red number counting down into minus with a shake, label above"""
    t0, t1, label, value, t_count, cy = e
    a = min(1, (t - t0) / 0.25, (t1 - t) / 0.25)
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    _glass(d, (170, cy - 150, W - 170, cy + 120), 40, a)
    d.text((W / 2, cy - 92), label, font=font(42), fill=(255, 255, 255, int(255 * a)), anchor='mm')
    k = ease(t, t_count, 1.1)
    v = int(round(value * k / 1000.0)) * 1000
    shake = 6 * math.sin((t - t0) * 60) * max(0, 1 - abs(t - t_count - 1.1) / 0.3)
    txt = '−' + f'{v:,}'.replace(',', ' ') + ' zł'
    d.text((W / 2 + shake, cy + 20), txt, font=font(96), fill=RED + (int(255 * a),), anchor='mm')
    return _shadow(lay)


def dissolve_word(t, e, font):
    """word that breaks into particles flying up (t_dis), then snaps back (t_back)"""
    t0, t1, text, t_dis, t_back, cy = e
    a = min(1, (t - t0) / 0.25, (t1 - t) / 0.2)
    f = font(110)
    txt = Image.new('L', (W, 260)); ImageDraw.Draw(txt).text((W / 2, 130), text, font=f, fill=255, anchor='mm')
    m = np.asarray(txt)
    lay = Image.new('RGBA', (W, H))
    if t < t_dis or t >= t_back + 0.35:
        k = ease(t, t_back, 0.35) if t >= t_back else 1
        col = ORANGE if t >= t_back else (255, 255, 255)
        L = Image.new('RGBA', (W, 260), col + (0,)); L.putalpha(Image.fromarray((m * a).astype(np.uint8)))
        lay.alpha_composite(L, (0, int(cy - 130)))
        return _shadow(lay, 10, 0.6, 5)
    p = ease(t, t_dis, 0.9) if t < t_back else 1 - ease(t, t_back, 0.35)
    ys, xs = np.nonzero(m[::5, ::5]); ys = ys * 5; xs = xs * 5
    rng = np.random.default_rng(5)
    dx = rng.normal(0, 90, len(xs)); dy = -rng.uniform(40, 300, len(xs)); ph = rng.uniform(0, 1, len(xs))
    d = ImageDraw.Draw(lay)
    for x, y, ddx, ddy, q in zip(xs, ys, dx, dy, ph):
        pp = min(1, p * (1 + q))
        X = x + ddx * pp; Y = cy - 130 + y + ddy * pp
        al = int(255 * a * (1 - pp * 0.6))
        sz = 7 - 3 * pp
        d.rectangle((X, Y, X + sz, Y + sz), fill=(255, 255, 255, al))
    return lay


def ring_timer(t, e, font):
    """6-month ring: sweep fills month by month, centre label"""
    t0, t1, n, centre, sub, t_fill, cy = e[:7]; R = e[7] if len(e) > 7 else 165
    a = min(1, (t - t0) / 0.25, (t1 - t) / 0.25)
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    r = R; sc = R / 165; cx = W / 2; box = (cx - r, cy - r, cx + r, cy + r)
    _glass(d, (cx - r - 50 * sc, cy - r - 50 * sc, cx + r + 50 * sc, cy + r + 50 * sc), r + 50 * sc, a)
    d.ellipse(box, outline=(255, 255, 255, int(60 * a)), width=int(34 * sc))
    k = ease(t, t_fill, 2.2)
    if k > 0: d.arc(box, -90, -90 + 360 * k, fill=ORANGE + (int(255 * a),), width=int(34 * sc))
    for i in range(n):
        ang = math.radians(-90 + 360 * (i + 0.5) / n)
        x, y = cx + (r + 0) * math.cos(ang), cy + (r + 0) * math.sin(ang)
        on = k >= (i + 1) / n - 1e-3
        d.ellipse((x - 14 * sc, y - 14 * sc, x + 14 * sc, y + 14 * sc), fill=((255, 255, 255) if on else (120, 125, 160)) + (int(255 * a),))
    d.text((cx, cy - 18 * sc), centre, font=font(int(110 * sc)), fill=(255, 255, 255, int(255 * a)), anchor='mm')
    d.text((cx, cy + 62 * sc), sub, font=font(int(40 * sc)), fill=ORANGE + (int(255 * a),), anchor='mm')
    return _shadow(lay)


def flip_cards(t, e, font):
    """two cards flip in (scale-x) with 'LUB' between"""
    t0, t1, cards, cy = e
    a = min(1, (t1 - t) / 0.25)
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    cw, ch = 360, 230
    for i, (ct, label, icon) in enumerate(cards):
        k = ease(t, ct, 0.45)
        if k <= 0: continue
        cx = W / 2 + (-235 if i == 0 else 235)
        sx = abs(math.cos(math.pi * (1 - k) / 2 * 1.0)) if k < 1 else 1
        sx = max(0.04, 1 - (1 - k) ** 2) if k < 1 else 1
        w2 = cw * sx
        d.rounded_rectangle((cx - w2 / 2, cy - ch / 2, cx + w2 / 2, cy + ch / 2), 28, fill=(255, 255, 255, int(250 * a)))
        if sx > 0.6:
            q = int(255 * a * (sx - 0.6) / 0.4)
            if icon == 'gavel':
                d.rounded_rectangle((cx - 60, cy - 80, cx + 30, cy - 40), 10, fill=NAVY + (q,))
                d.line((cx - 15, cy - 40, cx + 45, cy + 5), fill=NAVY + (q,), width=14)
                d.rectangle((cx - 70, cy + 5, cx + 70, cy + 20), fill=ORANGE + (q,))
            else:
                d.ellipse((cx - 50, cy - 90, cx + 50, cy + 10), outline=ORANGE + (q,), width=10)
                d.line((cx - 25, cy - 40, cx + 25, cy - 40), fill=NAVY + (q,), width=8)
                d.line((cx, cy - 65, cx, cy - 15), fill=NAVY + (q,), width=8)
            d.text((cx, cy + 70), label, font=font(42), fill=NAVY + (q,), anchor='mm')
    kl = ease(t, cards[1][0] - 0.2, 0.3)
    if kl > 0:
        d.ellipse((W / 2 - 50, cy - 50, W / 2 + 50, cy + 50), fill=ORANGE + (int(255 * a * kl),))
        d.text((W / 2, cy + 2), 'LUB', font=font(34), fill=(255, 255, 255, int(255 * a * kl)), anchor='mm')
    return _shadow(lay)


def two_tiles(t, e, font):
    """tiles that resolve: (label, t, verdict 'x'|'ok')"""
    t0, t1, tiles, cy = e
    a = min(1, (t - t0) / 0.25, (t1 - t) / 0.25)
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    tw, th = 420, 150
    for i, (label, tt, verdict, caption) in enumerate(tiles):
        cx = W / 2 + (-230 if i == 0 else 230); k = ease(t, tt, 0.35)
        _glass(d, (cx - tw / 2, cy - th / 2, cx + tw / 2, cy + th / 2), 30, a)
        fs = 50
        while fs > 26 and d.textlength(label, font=font(fs)) > tw - 60: fs -= 2
        d.text((cx, cy - 18), label, font=font(fs), fill=(255, 255, 255, int(255 * a * (1 - 0.4 * k))), anchor='mm')
        if k > 0:
            col = RED if verdict == 'x' else GREEN
            d.text((cx, cy + 42), caption, font=font(30), fill=col + (int(255 * a * k),), anchor='mm')
            bx, by = cx + tw / 2 - 20, cy - th / 2 + 10
            rr = 36 * (0.5 + 0.5 * k)
            d.ellipse((bx - rr, by - rr, bx + rr, by + rr), fill=col + (int(255 * a * k),))
            if verdict == 'x':
                s = rr * .45; d.line((bx - s, by - s, bx + s, by + s), fill=(255, 255, 255, int(255 * a * k)), width=7); d.line((bx + s, by - s, bx - s, by + s), fill=(255, 255, 255, int(255 * a * k)), width=7)
            else:
                d.line([(bx - rr * .45, by), (bx - rr * .1, by + rr * .35), (bx + rr * .5, by - rr * .35)], fill=(255, 255, 255, int(255 * a * k)), width=7, joint='curve')
    return _shadow(lay)


def pulse_alert(t, e, font):
    """orange '!' circle with expanding pulse rings + text"""
    t0, t1, text, cy = e
    k = ease(t, t0, 0.3); a = min(1, (t1 - t) / 0.2)
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    cx = W / 2; r = 70 * (0.6 + 0.4 * k)
    for j in range(3):
        ph = ((t - t0) * 0.9 + j / 3) % 1
        rr = r + 150 * ph
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=ORANGE + (int(200 * a * (1 - ph)),), width=6)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=ORANGE + (int(255 * a * k),))
    d.text((cx, cy + 4), '!', font=font(int(110 * (0.6 + 0.4 * k))), fill=(255, 255, 255, int(255 * a * k)), anchor='mm')
    d.text((cx, cy + 150), text, font=font(46), fill=(255, 255, 255, int(255 * a * k)), anchor='mm')
    return _shadow(lay, 10, 0.6, 5)


def family_chain(t, e, font):
    """RODZIC → TY (crossed) → DZIECI lighting up; caption"""
    t0, t1, t_you_x, t_kids, caption, t_cap, cy = e[:7]; sc = e[7] if len(e) > 7 else 1.0
    a = min(1, (t - t0) / 0.25, (t1 - t) / 0.25)
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    xs = [540 - 350 * sc, 540, 540 + 350 * sc]; r = 95 * sc
    _glass(d, (540 - 480 * sc, cy - 150 * sc, 540 + 480 * sc, cy + 175 * sc), int(40 * sc), a)
    kk = ease(t, t_kids, 0.5)
    for i in range(2):
        x0, x1 = xs[i] + r + 10, xs[i + 1] - r - 10
        prog = 1 if i == 0 else kk
        if prog > 0:
            xe = x0 + (x1 - x0) * prog
            d.line((x0, cy, xe, cy), fill=(ORANGE if i == 1 else (255, 255, 255)) + (int(230 * a),), width=int(10 * sc))
            if prog > 0.95: d.polygon([(x1, cy), (x1 - 26 * sc, cy - 18 * sc), (x1 - 26 * sc, cy + 18 * sc)], fill=(ORANGE if i == 1 else (255, 255, 255)) + (int(230 * a),))
    for i, (x, lbl) in enumerate(zip(xs, ['RODZIC', 'TY', 'DZIECI'])):
        on = i < 2 or kk > 0.5
        col = ORANGE if (i == 2 and on) else (255, 255, 255)
        fillc = (ORANGE if (i == 2 and on) else NAVY) + (int(240 * a),)
        d.ellipse((x - r, cy - r, x + r, cy + r), fill=fillc, outline=col + (int(255 * a),), width=max(3, int(6 * sc)))
        d.text((x, cy + 2), lbl, font=font(int((40 if len(lbl) > 3 else 52) * sc)), fill=(255, 255, 255, int(255 * a * (1 if on else .4))), anchor='mm')
    kx = ease(t, t_you_x, 0.3)
    if kx > 0:
        s = 70 * sc; x = xs[1]
        for (p0, p1) in [((x - s, cy - s), (x + s, cy + s)), ((x + s, cy - s), (x - s, cy + s))]:
            e2 = (p0[0] + (p1[0] - p0[0]) * kx, p0[1] + (p1[1] - p0[1]) * kx)
            d.line([p0, e2], fill=RED + (int(255 * a),), width=int(14 * sc))
    kc = ease(t, t_cap, 0.3)
    if kc > 0:
        d.text((W / 2, cy + 135 * sc), caption, font=font(int(38 * sc)), fill=ORANGE + (int(255 * a * kc),), anchor='mm')
    return _shadow(lay)


def follow_button(t, e, font):
    """'OBSERWUJ' button, cursor taps it, turns into 'OBSERWUJESZ ✓'"""
    t0, t1, t_tap, cy = e
    k = ease(t, t0, 0.3); a = min(1, (t1 - t) / 0.2) * k
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    tapped = t >= t_tap
    press = max(0, 1 - abs(t - t_tap) / 0.12)
    sc = 1 - 0.08 * press
    txt = 'OBSERWUJESZ ✓' if tapped else 'OBSERWUJ'
    f = font(int(56 * sc)); tw = d.textlength('OBSERWUJESZ  ', font=f)
    w, h = (tw + (190 if tapped else 90)) * sc, 120 * sc
    col = (255, 255, 255) if tapped else ORANGE
    d.rounded_rectangle((W / 2 - w / 2, cy - h / 2, W / 2 + w / 2, cy + h / 2), int(h / 2), fill=col + (int(255 * a),))
    d.text((W / 2 - (40 if tapped else 0), cy + 2), txt.replace(' ✓', ''), font=f, fill=(NAVY if tapped else (255, 255, 255)) + (int(255 * a),), anchor='mm')
    if tapped:
        bx = W / 2 + w / 2 - 60
        d.ellipse((bx - 30, cy - 30, bx + 30, cy + 30), fill=GREEN + (int(255 * a),))
        d.line([(bx - 13, cy), (bx - 3, cy + 11), (bx + 15, cy - 11)], fill=(255, 255, 255, int(255 * a)), width=6, joint='curve')
    # cursor
    kc = ease(t, t_tap - 0.6, 0.55)
    if t < t_tap + 0.6:
        cx = W / 2 + 280 - 180 * kc; cyy = cy + 240 - 200 * kc
        ca = a * min(1, (t_tap + 0.6 - t) / 0.3)
        pts = [(cx, cyy), (cx, cyy + 70), (cx + 18, cyy + 54), (cx + 32, cyy + 84), (cx + 44, cyy + 78), (cx + 30, cyy + 50), (cx + 52, cyy + 48)]
        d.polygon(pts, fill=(255, 255, 255, int(255 * ca)), outline=(20, 20, 30, int(255 * ca)))
        if press > 0:
            d.ellipse((cx - 40 * press - 10, cyy - 40 * press - 10, cx + 40 * press + 10, cyy + 40 * press + 10), outline=(255, 255, 255, int(200 * press * ca)), width=4)
    return _shadow(lay)


def toggle(t, e, font):
    """bank-transfer card with a switch flipping ON -> OFF"""
    t0, t1, title, sub, t_off, cy = e
    k = ease(t, t0, 0.3); a = min(1, (t1 - t) / 0.25) * k
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    x0, x1, h = 150, W - 150, 170
    d.rounded_rectangle((x0, cy - h / 2, x1, cy + h / 2), 34, fill=(255, 255, 255, int(248 * a)))
    d.text((x0 + 40, cy - 28), title, font=font(46), fill=NAVY + (int(255 * a),), anchor='lm')
    ko = ease(t, t_off, 0.3)
    st = sub[1] if ko > 0.5 else sub[0]
    d.text((x0 + 40, cy + 32), st, font=font(32), fill=(RED if ko > 0.5 else GREEN) + (int(255 * a),), anchor='lm')
    sw, sh = 150, 76; sx = x1 - 40 - sw
    col = tuple(int(GREEN[i] + (200 - GREEN[i]) * ko) for i in range(3))
    d.rounded_rectangle((sx, cy - sh / 2, sx + sw, cy + sh / 2), sh // 2, fill=col + (int(255 * a),))
    kx = sx + sw - sh / 2 - (sw - sh) * ko
    d.ellipse((kx - sh / 2 + 7, cy - sh / 2 + 7, kx + sh / 2 - 7, cy + sh / 2 - 7), fill=(255, 255, 255, int(255 * a)))
    return _shadow(lay)


def _person(d, cx, cy, s, col):
    d.ellipse((cx - .32 * s, cy - s, cx + .32 * s, cy - .36 * s), fill=col)
    d.rounded_rectangle((cx - .55 * s, cy - .28 * s, cx + .55 * s, cy + .6 * s), int(.4 * s), fill=col)


def people_row(t, e, font):
    """row of people turning red one by one + label (many parents make the same mistake)"""
    t0, t1, n, t_red, label, cy = e
    a = min(1, (t - t0) / 0.25, (t1 - t) / 0.25)
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    _glass(d, (110, cy - 120, W - 110, cy + 150), 40, a)
    s = 52; gap = 140; x0 = W / 2 - gap * (n - 1) / 2
    for i in range(n):
        k = ease(t, t_red + i * 0.12, 0.25)
        col = tuple(int(255 + (RED[j] - 255) * k) for j in range(3))
        _person(d, x0 + i * gap, cy + 10, s, col + (int(255 * a),))
    d.text((W / 2, cy + 105), label, font=font(42), fill=(255, 255, 255, int(255 * a)), anchor='mm')
    return _shadow(lay)


def scene_milestones(t, e, font):
    """orange-placeholder animation: 3 milestones tick, then 'transfer' arrow breaks + question"""
    t0, t1, cfg = e
    lay = Image.new('RGBA', (W, H), NAVY + (255,))
    glow = Image.new('RGBA', (W, H)); g = ImageDraw.Draw(glow)
    for i, (bx, by, br, col) in enumerate([(250, 500, 420, (40, 70, 200)), (850, 1350, 520, (30, 50, 170)), (600, 900, 300, (244, 122, 58))]):
        ph = (t - t0) * 0.35 + i * 2.1
        g.ellipse((bx + 60 * math.sin(ph) - br, by + 50 * math.cos(ph * .8) - br, bx + 60 * math.sin(ph) + br, by + 50 * math.cos(ph * .8) + br), fill=col + (60 if i < 2 else 24,))
    lay.alpha_composite(glow.filter(ImageFilter.GaussianBlur(120)))
    d = ImageDraw.Draw(lay)
    k = ease(t, t0, 0.3)
    f = font(54); tw = d.textlength(cfg['title'], font=f); y = 220 - 30 * (1 - k)
    d.rounded_rectangle((W / 2 - tw / 2 - 44, y - 54, W / 2 + tw / 2 + 44, y + 54), 54, fill=ORANGE + (int(255 * k),))
    d.text((W / 2, y + 2), cfg['title'], font=f, fill=(255, 255, 255, int(255 * k)), anchor='mm')
    # milestones as a vertical path, centred and large
    ys = [520, 760, 1000]; R = 74; fm = font(66)
    tw = max(d.textlength(lbl, font=fm) for _, lbl in cfg['items'])
    gx = (W - (2 * R + 40 + tw)) / 2 + R
    for i, (tm, lbl) in enumerate(cfg['items']):
        km = ease(t, tm, 0.35)
        if km <= 0: continue
        y = ys[i]
        if i > 0: d.line((gx, ys[i - 1] + R + 6, gx, y - R - 6), fill=(255, 255, 255, int(120 * km)), width=7)
        d.ellipse((gx - R, y - R, gx + R, y + R), fill=GREEN + (int(255 * km),))
        d.line([(gx - 28, y + 3), (gx - 7, y + 25), (gx + 32, y - 22)], fill=(255, 255, 255, int(255 * km)), width=13, joint='curve')
        d.text((gx + R + 40 - 20 * (1 - km), y + 3), lbl, font=fm, fill=(255, 255, 255, int(255 * km)), anchor='lm')
    # transfer card that stops
    kt = ease(t, cfg['t_transfer'], 0.4)
    if kt > 0:
        y0 = 1230 + 40 * (1 - kt)
        d.rounded_rectangle((120, y0, W - 120, y0 + 220), 32, fill=(255, 255, 255, int(245 * kt)))
        d.text((170, y0 + 70), 'PRZELEW', font=font(36), fill=(110, 115, 135, int(255 * kt)), anchor='lm')
        d.text((170, y0 + 140), 'ALIMENTY', font=font(58), fill=NAVY + (int(255 * kt),), anchor='lm')
        ks = ease(t, cfg['t_stop'], 0.25)
        bx, by = W - 230, y0 + 110
        if ks > 0:
            r = 70 * (0.6 + 0.4 * ks)
            pts = [(bx + r * math.cos(math.radians(22.5 + 45 * j)), by + r * math.sin(math.radians(22.5 + 45 * j))) for j in range(8)]
            d.polygon(pts, fill=RED + (int(255 * ks),))
            d.text((bx, by + 2), 'STOP', font=font(int(34 * (0.6 + 0.4 * ks))), fill=(255, 255, 255, int(255 * ks)), anchor='mm')
        else:
            ph = ((t - cfg['t_transfer']) * 1.5) % 1
            d.text((bx - 30 + 60 * ph, by + 2), '→', font=font(70), fill=GREEN + (int(255 * kt),), anchor='mm')
    kq = ease(t, cfg['t_q'], 0.3)
    if kq > 0:
        f = font(70); tw = d.textlength(cfg['q'], font=f); y = 1580
        d.text((W / 2, y + 20 * (1 - kq)), cfg['q'], font=f, fill=ORANGE + (int(255 * kq),), anchor='mm')
    return lay


# ---------- side / depth set (short 9) ----------
def bubbles(t, e, font):
    """speech bubbles popping at the sides of the person (not above the head)"""
    t0, t1, items = e
    a = min(1, (t1 - t) / 0.25)
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    for (bt, txt, (cx, cy), side) in items:
        k = ease(t, bt, 0.28)
        if k <= 0: continue
        f = font(int(46 * (0.7 + 0.3 * k))); tw = d.textlength(txt, font=f)
        w, h = tw + 70, 100 * (0.7 + 0.3 * k)
        x0, y0 = cx - w / 2, cy - h / 2
        d.rounded_rectangle((x0, y0, x0 + w, y0 + h), int(h / 2), fill=(255, 255, 255, int(250 * a * k)))
        tx = x0 + 60 if side == 'L' else x0 + w - 60
        d.polygon([(tx - 18, y0 + h - 4), (tx + 18, y0 + h - 4), (tx + (24 if side == 'L' else -24), y0 + h + 30)], fill=(255, 255, 255, int(250 * a * k)))
        d.text((cx, cy + 2), txt, font=f, fill=NAVY + (int(255 * a * k),), anchor='mm')
    return _shadow(lay)


def side_cards(t, e, font):
    """cards flying in from alternating sides at chest level, stacking"""
    t0, t1, items, y0 = e
    a = min(1, (t1 - t) / 0.25)
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    for i, (ct, txt, side) in enumerate(items):
        k = ease(t, ct, 0.4)
        if k <= 0: continue
        f = font(46); tw = d.textlength(txt, font=f); w, h = tw + 110, 104
        y = y0 + i * 124
        tx = 60 if side == 'L' else W - 60 - w
        x = tx + (-(w + 80) if side == 'L' else (w + 80)) * (1 - k)
        d.rounded_rectangle((x, y, x + w, y + h), 26, fill=NAVY + (int(235 * a),), outline=(255, 255, 255, int(110 * a)), width=3)
        d.rounded_rectangle((x, y, x + 14, y + h), 7, fill=ORANGE + (int(255 * a),))
        d.text((x + 50, y + h / 2 + 2), txt, font=f, fill=(255, 255, 255, int(255 * a)), anchor='lm')
    return _shadow(lay)


def behind_text(t, e, font):
    """huge text layer meant to sit BEHIND the person (composited under the matte)"""
    t0, t1, lines, cy, col = e[:5]; sz = e[5] if len(e) > 5 else 250
    k = ease(t, t0, 0.35); a = min(1, (t1 - t) / 0.2)
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    lh = int(sz * 0.92)
    for i, ln in enumerate(lines):
        f = font(int(sz * (0.85 + 0.15 * k)))
        y = cy - lh * (len(lines) - 1) / 2 + i * lh + 60 * (1 - k)
        d.text((W / 2 + 6, y + 10), ln, font=f, fill=(0, 0, 0, int(90 * a * k)), anchor='mm')
        d.text((W / 2, y), ln, font=f, fill=tuple(col) + (int(255 * a * k),), anchor='mm')
    return lay


def court_doc(t, e, font):
    """top-half panel for picture-in-picture: court decision document + question"""
    t0, t1, title, q, t_q = e[:5]; seal = e[5] if len(e) > 5 else 'SĄD'
    k = ease(t, t0 + 0.15, 0.4)
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    x0, y0, x1, y1 = 150, 120 + 50 * (1 - k), W - 150, 740 + 50 * (1 - k)
    d.rounded_rectangle((x0, y0, x1, y1), 30, fill=(255, 255, 255, int(250 * k)))
    d.rectangle((x0 + 50, y0 - 24, x0 + 120, y0 + 24), fill=ORANGE + (int(255 * k),))
    d.text(((x0 + x1) / 2, y0 + 90), title, font=font(52), fill=NAVY + (int(255 * k),), anchor='mm')
    d.line((x0 + 60, y0 + 150, x1 - 60, y0 + 150), fill=(220, 222, 235, int(255 * k)), width=4)
    for j in range(5):
        kl = ease(t, t0 + 0.4 + j * 0.15, 0.3)
        ww = (x1 - x0 - 120) * (0.6 if j == 4 else 1) * kl
        d.rounded_rectangle((x0 + 60, y0 + 200 + j * 60, x0 + 60 + ww, y0 + 222 + j * 60), 11, fill=(205, 208, 222, int(255 * k)))
    # seal
    sx, sy = x1 - 130, y1 - 100
    d.ellipse((sx - 60, sy - 60, sx + 60, sy + 60), outline=RED + (int(220 * k),), width=8)
    d.text((sx, sy + 2), seal, font=font(34 if len(seal) <= 3 else 22), fill=RED + (int(220 * k),), anchor='mm')
    kq = ease(t, t_q, 0.3)
    if kq > 0:
        f = font(58); tw = d.textlength(q, font=f); y = y1 + 85
        d.rounded_rectangle((W / 2 - tw / 2 - 40, y - 52, W / 2 + tw / 2 + 40, y + 52), 52, fill=ORANGE + (int(255 * kq),))
        d.text((W / 2, y + 2), q, font=f, fill=(255, 255, 255, int(255 * kq)), anchor='mm')
    return _shadow(lay)


def _moon(d, cx, cy, r, a):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 220, 120, int(255 * a)))
    d.ellipse((cx - r + r * .55, cy - r - r * .15, cx + r + r * .55, cy + r - r * .15), fill=NAVY + (255,))


def _eye(d, cx, cy, r, a):
    d.ellipse((cx - r, cy - r * .55, cx + r, cy + r * .55), fill=(255, 255, 255, int(255 * a)))
    d.ellipse((cx - r * .38, cy - r * .38, cx + r * .38, cy + r * .38), fill=NAVY + (int(255 * a),))
    d.ellipse((cx - r * .14, cy - r * .3, cx + r * .1, cy - r * .06), fill=(255, 255, 255, int(255 * a)))


def scene_contacts(t, e, font):
    """blue-placeholder animation: real fears -> court -> 3 options cards with icons"""
    t0, t1, cfg = e
    lay = Image.new('RGBA', (W, H), NAVY + (255,))
    glow = Image.new('RGBA', (W, H)); g = ImageDraw.Draw(glow)
    for i, (bx, by, br, col) in enumerate([(250, 500, 420, (40, 70, 200)), (850, 1350, 520, (30, 50, 170)), (600, 900, 300, (244, 122, 58))]):
        ph = (t - t0) * 0.35 + i * 2.1
        g.ellipse((bx + 60 * math.sin(ph) - br, by + 50 * math.cos(ph * .8) - br, bx + 60 * math.sin(ph) + br, by + 50 * math.cos(ph * .8) + br), fill=col + (60 if i < 2 else 24,))
    lay.alpha_composite(glow.filter(ImageFilter.GaussianBlur(120)))
    d = ImageDraw.Draw(lay)
    # step 1: fears -> court (arrow)
    k1 = ease(t, t0 + 0.1, 0.35); k2 = ease(t, cfg['t_court'], 0.4)
    CY = 560
    for (txt, x, k, col) in [('RZECZYWISTE\nOBAWY', 290, k1, (255, 255, 255)), ('SĄD', 810, k2, ORANGE)]:
        if k <= 0: continue
        r = 165
        ring = Image.new('RGBA', (W, H)); ImageDraw.Draw(ring).ellipse((x - r, CY - r, x + r, CY + r), fill=(255, 255, 255, int(30 * k)), outline=col + (int(255 * k),), width=7)
        lay.alpha_composite(ring); d = ImageDraw.Draw(lay)
        for j, ln in enumerate(txt.split('\n')):
            d.text((x, CY + (j - (len(txt.split('\n')) - 1) / 2) * 52), ln, font=font(36 if '\n' in txt else 70), fill=col + (int(255 * k),), anchor='mm')
    if k2 > 0:
        xe = 465 + (635 - 465) * k2
        d.line((465, CY, xe, CY), fill=ORANGE + (255,), width=12)
        if k2 > 0.95: d.polygon([(645, CY), (615, CY - 20), (615, CY + 20)], fill=ORANGE + (255,))
    kt = ease(t, cfg['t_title'], 0.35)
    if kt > 0:
        f = font(54); tw = d.textlength(cfg['title'], font=f); y = 860
        d.rounded_rectangle((W / 2 - tw / 2 - 44, y - 54, W / 2 + tw / 2 + 44, y + 54), 54, fill=ORANGE + (int(255 * kt),))
        d.text((W / 2, y + 2), cfg['title'], font=f, fill=(255, 255, 255, int(255 * kt)), anchor='mm')
    # options cards
    for i, (ct, lbl, icon) in enumerate(cfg['options']):
        k = ease(t, ct, 0.4)
        if k <= 0: continue
        cw, ch = 310, 440; gap = 25; x0 = (W - 3 * cw - 2 * gap) / 2 + i * (cw + gap)
        y0 = 1000 + 80 * (1 - k)
        d.rounded_rectangle((x0, y0, x0 + cw, y0 + ch), 30, fill=(255, 255, 255, int(250 * k)))
        cx, cy = x0 + cw / 2, y0 + 160
        if icon == 'clock':
            d.ellipse((cx - 80, cy - 80, cx + 80, cy + 80), fill=NAVY + (int(255 * k),))
            frac = 1 - 0.5 * ease(t, ct + 0.3, 1.0)
            d.pieslice((cx - 66, cy - 66, cx + 66, cy + 66), -90, -90 + 360 * frac, fill=ORANGE + (int(255 * k),))
        elif icon == 'moon':
            d.ellipse((cx - 80, cy - 80, cx + 80, cy + 80), fill=NAVY + (int(255 * k),))
            _moon(d, cx, cy, 48, k)
            kx = ease(t, ct + 0.35, 0.3)
            if kx > 0:
                s = 70 * kx; d.line((cx - 70, cy - 70, cx - 70 + 140 * kx, cy - 70 + 140 * kx), fill=RED + (255,), width=12)
        else:
            d.ellipse((cx - 80, cy - 80, cx + 80, cy + 80), fill=NAVY + (int(255 * k),))
            _eye(d, cx, cy, 58, k)
        for j, ln in enumerate(lbl.split('\n')):
            d.text((cx, y0 + 315 + j * 52), ln, font=font(42), fill=NAVY + (int(255 * k),), anchor='mm')
    return lay


def shield_q(t, e, font):
    """top panel for PIP: shield + 'MELDUNEK' + big question mark"""
    t0, t1, label, t_q = e
    k = ease(t, t0 + 0.15, 0.4)
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    cx, cy, s = W / 2, 420 + 40 * (1 - k), 230
    pts = [(cx - s, cy - s * .9), (cx, cy - s * 1.15), (cx + s, cy - s * .9), (cx + s * .85, cy + s * .25), (cx, cy + s * 1.05), (cx - s * .85, cy + s * .25)]
    d.polygon(pts, fill=(255, 255, 255, int(250 * k)))
    inner = [(cx + (x - cx) * .82, cy + (y - cy) * .82) for x, y in pts]
    d.polygon(inner, fill=NAVY + (int(255 * k),))
    d.text((cx, cy - 20), label, font=font(52), fill=(255, 255, 255, int(255 * k)), anchor='mm')
    kq = ease(t, t_q, 0.3)
    if kq > 0:
        d.text((cx, cy + 90 + 20 * (1 - kq)), '?', font=font(int(150 * (0.7 + 0.3 * kq))), fill=ORANGE + (int(255 * kq),), anchor='mm')
    return _shadow(lay)


def _house_person(d, cx, cy, s, a, person=True):
    d.polygon([(cx - s, cy - 0.1 * s), (cx, cy - s), (cx + s, cy - 0.1 * s)], fill=(255, 255, 255, int(255 * a)))
    d.rectangle((cx - 0.8 * s, cy - 0.1 * s, cx + 0.8 * s, cy + 0.85 * s), fill=(255, 255, 255, int(255 * a)))
    if person:
        _person(d, cx, cy + 0.45 * s, 0.38 * s, ORANGE + (int(255 * a),))


def scene_eviction(t, e, font):
    """blue-placeholder animation: contract terminated/expired -> tenant still inside -> court -> 'POZEW O EKSMISJĘ'"""
    t0, t1, cfg = e
    lay = Image.new('RGBA', (W, H), NAVY + (255,))
    glow = Image.new('RGBA', (W, H)); g = ImageDraw.Draw(glow)
    for i, (bx, by, br, col) in enumerate([(250, 500, 420, (40, 70, 200)), (850, 1350, 520, (30, 50, 170)), (600, 900, 300, (244, 122, 58))]):
        ph = (t - t0) * 0.35 + i * 2.1
        g.ellipse((bx + 60 * math.sin(ph) - br, by + 50 * math.cos(ph * .8) - br, bx + 60 * math.sin(ph) + br, by + 50 * math.cos(ph * .8) + br), fill=col + (60 if i < 2 else 24,))
    lay.alpha_composite(glow.filter(ImageFilter.GaussianBlur(120)))
    d = ImageDraw.Draw(lay)
    # contract
    kc = ease(t, t0 + 0.1, 0.4)
    x0, y0 = 80, 300 + 40 * (1 - kc); cw, ch = 440, 560
    d.rounded_rectangle((x0, y0, x0 + cw, y0 + ch), 26, fill=(255, 255, 255, int(250 * kc)))
    d.text((x0 + cw / 2, y0 + 80), 'UMOWA', font=font(54), fill=NAVY + (int(255 * kc),), anchor='mm')
    d.text((x0 + cw / 2, y0 + 140), 'NAJMU', font=font(42), fill=(110, 115, 135, int(255 * kc)), anchor='mm')
    for j in range(5):
        d.rounded_rectangle((x0 + 45, y0 + 210 + j * 58, x0 + cw - 45 - (70 if j == 4 else 0), y0 + 230 + j * 58), 10, fill=(205, 208, 222, int(255 * kc)))
    for (ts, txt, dy) in [(cfg['t_terminated'], 'WYPOWIEDZIANA', 0), (cfg['t_expired'], 'WYGASŁA', 150)]:
        if t >= ts:
            lay.alpha_composite(stamp(t, (ts, t1, txt, (x0 + cw / 2, y0 + 290 + dy), 0.55), font)); d = ImageDraw.Draw(lay)
    # house with tenant still inside
    kh = ease(t, cfg['t_tenant'], 0.4)
    if kh > 0:
        _house_person(d, 800, 520, 220 * (0.7 + 0.3 * kh), kh)
        d.text((800, 790), 'LOKATOR NADAL', font=font(42), fill=(255, 255, 255, int(255 * kh)), anchor='mm')
        d.text((800, 845), 'ZAJMUJE MIESZKANIE', font=font(38), fill=ORANGE + (int(255 * kh),), anchor='mm')
    # arrow down to court
    ka = ease(t, cfg['t_court'], 0.5)
    if ka > 0:
        ys, ye = 950, 950 + 230 * ka
        d.line((540, ys, 540, ye), fill=ORANGE + (255,), width=14)
        if ka > 0.95: d.polygon([(540, 1195), (512, 1157), (568, 1157)], fill=ORANGE + (255,))
    kg = ease(t, cfg['t_court'] + 0.4, 0.4)
    if kg > 0:
        cx, cy = 540, 1350
        d.rounded_rectangle((cx - 120, cy - 70, cx + 40, cy - 10), 14, fill=(255, 255, 255, int(255 * kg)))
        d.line((cx - 20, cy - 10, cx + 70, cy + 70), fill=(255, 255, 255, int(255 * kg)), width=22)
        d.rectangle((cx - 170, cy + 80, cx + 170, cy + 100), fill=ORANGE + (int(255 * kg),))
        d.text((cx, cy + 160), 'SĄD', font=font(60), fill=(255, 255, 255, int(255 * kg)), anchor='mm')
    kp = ease(t, cfg['t_pozew'], 0.35)
    if kp > 0:
        f = font(60); tw = d.textlength(cfg['pozew'], font=f); y = 1670
        d.rounded_rectangle((W / 2 - tw / 2 - 46, y - 58, W / 2 + tw / 2 + 46, y + 58), 58, fill=ORANGE + (int(255 * kp),))
        d.text((W / 2, y + 2), cfg['pozew'], font=f, fill=(255, 255, 255, int(255 * kp)), anchor='mm')
    return lay


def separate(t, e, font):
    """two overlapping circles that slide apart at t_split ('two separate issues')"""
    t0, t1, la, lb, t_split, cap, cy = e
    a = min(1, (t - t0) / 0.3, (t1 - t) / 0.25)
    lay = Image.new('RGBA', (W, H))
    ks = ease(t, t_split, 0.7); r = 190
    for (lbl, col, sgn) in [(la, ORANGE, -1), (lb, (255, 255, 255), 1)]:
        cx = W / 2 + sgn * (110 + 160 * ks)
        c = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(c)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=NAVY + (int(215 * a),), outline=col + (int(255 * a),), width=8)
        for j, ln in enumerate(lbl.split('\n')):
            d.text((cx + sgn * 30 * (1 - ks), cy + (j - (len(lbl.split('\n')) - 1) / 2) * 50), ln, font=font(34), fill=col + (int(255 * a),), anchor='mm')
        lay.alpha_composite(c)
    kc = ease(t, t_split + 0.3, 0.3)
    if kc > 0:
        d = ImageDraw.Draw(lay); f = font(44); tw = d.textlength(cap, font=f); y = cy + r + 70
        d.rounded_rectangle((W / 2 - tw / 2 - 34, y - 42, W / 2 + tw / 2 + 34, y + 42), 42, fill=ORANGE + (int(255 * a * kc),))
        d.text((W / 2, y + 2), cap, font=f, fill=(255, 255, 255, int(255 * a * kc)), anchor='mm')
    return _shadow(lay)


def ladder(t, e, font):
    """escalating steps (left→right, rising): each lights up at its time; last is red"""
    t0, t1, steps, cy = e
    a = min(1, (t - t0) / 0.3, (t1 - t) / 0.25)
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    n = len(steps); bw = 250; gap = 22; x0 = (W - n * bw - (n - 1) * gap) / 2
    for i, (st, lbl, col) in enumerate(steps):
        k = ease(t, st, 0.35)
        h = 120 + i * 65; x = x0 + i * (bw + gap); yb = cy + 150
        on = k > 0
        fillc = (tuple(col) + (int(240 * a),)) if on else (255, 255, 255, int(40 * a))
        card = Image.new('RGBA', (W, H)); cd = ImageDraw.Draw(card)
        hh = h * (0.85 + 0.15 * k) if on else h
        cd.rounded_rectangle((x, yb - hh, x + bw, yb), 24, fill=fillc, outline=(255, 255, 255, int(120 * a)), width=3)
        lay.alpha_composite(card); d = ImageDraw.Draw(lay)
        fs = 34
        while fs > 20 and max(d.textlength(ln, font=font(fs)) for ln in lbl.split('\n')) > bw - 30: fs -= 2
        for j, ln in enumerate(lbl.split('\n')):
            d.text((x + bw / 2, yb - hh / 2 + (j - (len(lbl.split('\n')) - 1) / 2) * (fs + 8)), ln, font=font(fs), fill=(255, 255, 255, int(255 * a * (1 if on else .45))), anchor='mm')
    return _shadow(lay)


def scale_compare(t, e, font):
    """D: two weights on a horizontal line — 'władza' half-filled bar vs 'kontakt' bar staying full"""
    t0, t1, t_b, cy = e
    a = min(1, (t - t0) / 0.3, (t1 - t) / 0.25)
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    x0, x1 = 140, W - 140
    for i, (lbl, frac_end, col, tt) in enumerate([('WŁADZA RODZICIELSKA', 0.45, ORANGE, t0 + 0.1), ('KONTAKT Z DZIECKIEM', 1.0, GREEN, t_b)]):
        k = ease(t, tt, 0.4); y = cy + i * 150
        if k <= 0: continue
        d.text((x0, y - 45), lbl, font=font(38), fill=(255, 255, 255, int(255 * a * k)), anchor='lm')
        d.rounded_rectangle((x0, y, x1, y + 46), 23, fill=(255, 255, 255, int(45 * a * k)))
        fr = 1.0 - (1.0 - frac_end) * ease(t, tt + 0.4, 0.8)
        d.rounded_rectangle((x0, y, x0 + (x1 - x0) * fr * k, y + 46), 23, fill=col + (int(240 * a),))
        tag = 'OGRANICZONA' if i == 0 else 'ZOSTAJE'
        d.text((x1, y - 45), tag, font=font(32), fill=col + (int(255 * a * ease(t, tt + 0.8, 0.3)),), anchor='rm')
    return _shadow(lay)


def two_doors(t, e, font):
    """E: two doors side by side; left opens partially (ograniczenie), right stays open (kontakt)"""
    t0, t1, t_b, cy = e
    a = min(1, (t - t0) / 0.3, (t1 - t) / 0.25)
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    for i, (cx, lbl, tt, lock) in enumerate([(330, 'WŁADZA', t0 + 0.1, True), (750, 'KONTAKT', t_b, False)]):
        k = ease(t, tt, 0.4)
        if k <= 0: continue
        w, h = 230, 320; x0, y0 = cx - w / 2, cy - h / 2
        d.rounded_rectangle((x0 - 14, y0 - 14, x0 + w + 14, y0 + h + 10), 20, fill=NAVY + (int(230 * a * k),), outline=(255, 255, 255, int(150 * a * k)), width=4)
        op = 0.25 if lock else 0.85
        ow = w * (1 - op * ease(t, tt + 0.3, 0.7))
        d.rectangle((x0, y0, x0 + ow, y0 + h), fill=(ORANGE if lock else GREEN) + (int(245 * a * k),))
        d.ellipse((x0 + ow - 30, y0 + h / 2 - 10, x0 + ow - 10, y0 + h / 2 + 10), fill=(255, 255, 255, int(255 * a * k)))
        if lock:
            lx, ly = x0 + w / 2 - 20, y0 + h / 2
            d.arc((lx - 26, ly - 50, lx + 26, ly + 2), 180, 360, fill=(255, 255, 255, int(255 * a * k)), width=8)
            d.rounded_rectangle((lx - 34, ly - 22, lx + 34, ly + 34), 8, fill=(255, 255, 255, int(255 * a * k)))
        d.text((cx, y0 + h + 55), lbl, font=font(42), fill=(255, 255, 255, int(255 * a * k)), anchor='mm')
    return _shadow(lay)


def question_flip(t, e, font):
    """F: big question pill 'OGRANICZENIE = ZAKAZ?' then the '=' gets struck and becomes '≠' with 'NIE!'"""
    t0, t1, t_no, cy = e
    a = min(1, (t - t0) / 0.3, (t1 - t) / 0.25)
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    kn = ease(t, t_no, 0.25)
    rows = ['OGRANICZENIE', '=' if kn < 0.5 else '≠', 'ZAKAZ KONTAKTU?' if kn < 0.5 else 'ZAKAZ KONTAKTU']
    _glass(d, (150, cy - 190, W - 150, cy + 190), 40, a)
    for i, r in enumerate(rows):
        col = ORANGE if i == 1 else (255, 255, 255)
        sz = 110 if i == 1 else 56
        d.text((W / 2, cy - 120 + i * 120), r, font=font(sz), fill=col + (int(255 * a),), anchor='mm')
    if kn > 0:
        f = font(int(44 * (0.7 + 0.3 * kn))); x = W / 2 + 370; y = cy - 190
        d.ellipse((x - 70, y - 70, x + 70, y + 70), fill=RED + (int(255 * a * kn),))
        d.text((x, y + 2), 'NIE', font=f, fill=(255, 255, 255, int(255 * a * kn)), anchor='mm')
    return _shadow(lay)


def options3(t, e, font):
    """three option cards in a row with risk colour + caption"""
    t0, t1, opts, t_cap, cap, cy = e
    a = min(1, (t - t0) / 0.3, (t1 - t) / 0.25)
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    cw, ch, gap = 330, 260, 12; x0 = (W - 3 * cw - 2 * gap) / 2
    for i, (ot, lbl, sub, col) in enumerate(opts):
        k = ease(t, ot, 0.35)
        if k <= 0: continue
        x = x0 + i * (cw + gap); y = cy - ch / 2 + 50 * (1 - k)
        card = Image.new('RGBA', (W, H)); cd = ImageDraw.Draw(card)
        cd.rounded_rectangle((x, y, x + cw, y + ch), 26, fill=(255, 255, 255, int(248 * a)))
        cd.rounded_rectangle((x, y, x + cw, y + 18), 9, fill=tuple(col) + (int(255 * a),))
        lay.alpha_composite(card); d = ImageDraw.Draw(lay)
        lines = lbl.split('\n')
        fs = 44
        while fs > 22 and max(d.textlength(l, font=font(fs)) for l in lines) > cw - 30: fs -= 2
        for j, l in enumerate(lines):
            d.text((x + cw / 2, y + 95 + (j - (len(lines) - 1) / 2) * (fs + 8)), l, font=font(fs), fill=NAVY + (int(255 * a),), anchor='mm')
        d.rounded_rectangle((x + 25, y + ch - 70, x + cw - 25, y + ch - 22), 24, fill=tuple(col) + (int(255 * a),))
        d.text((x + cw / 2, y + ch - 46), sub, font=font(26), fill=(255, 255, 255, int(255 * a)), anchor='mm')
    kc = ease(t, t_cap, 0.3)
    if kc > 0:
        f = font(42); tw = d.textlength(cap, font=f); y = cy + ch / 2 + 75
        d.rounded_rectangle((W / 2 - tw / 2 - 34, y - 40, W / 2 + tw / 2 + 34, y + 40), 40, fill=ORANGE + (int(255 * a * kc),))
        d.text((W / 2, y + 2), cap, font=f, fill=(255, 255, 255, int(255 * a * kc)), anchor='mm')
    return _shadow(lay)


def insurance(t, e, font):
    """shield 'POLISA' + debt bar draining to zero, green check at the end"""
    t0, t1, t_drain, t_ok, cy = e
    a = min(1, (t - t0) / 0.3, (t1 - t) / 0.25)
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    _glass(d, (90, cy - 150, W - 90, cy + 150), 40, a)
    sx, sy, s = 230, cy, 95
    pts = [(sx - s, sy - s * .9), (sx, sy - s * 1.15), (sx + s, sy - s * .9), (sx + s * .85, sy + s * .25), (sx, sy + s * 1.05), (sx - s * .85, sy + s * .25)]
    d.polygon(pts, fill=GREEN + (int(255 * a),))
    d.text((sx, sy - 5), 'POLISA', font=font(30), fill=(255, 255, 255, int(255 * a)), anchor='mm')
    bx0, bx1 = 380, W - 140
    d.text((bx0, cy - 60), 'ZADŁUŻENIE', font=font(38), fill=(255, 255, 255, int(255 * a)), anchor='lm')
    d.rounded_rectangle((bx0, cy - 10, bx1, cy + 40), 25, fill=(255, 255, 255, int(45 * a)))
    fr = 1 - ease(t, t_drain, 1.6)
    if fr > 0.02: d.rounded_rectangle((bx0, cy - 10, bx0 + (bx1 - bx0) * fr, cy + 40), 25, fill=RED + (int(240 * a),))
    ko = ease(t, t_ok, 0.3)
    if ko > 0:
        d.text((bx1, cy - 60), 'SPŁACONE', font=font(36), fill=GREEN + (int(255 * a * ko),), anchor='rm')
        cx, cyy, r = bx1 - 30, cy + 95, 30 * (0.5 + 0.5 * ko)
    return _shadow(lay)


def scene_kinship(t, e, font):
    """blue-placeholder animation: MAMA —(pokrewieństwo)— TY; BANK sends a claim arrow to TY which gets blocked"""
    t0, t1, cfg = e
    lay = Image.new('RGBA', (W, H), NAVY + (255,))
    glow = Image.new('RGBA', (W, H)); g = ImageDraw.Draw(glow)
    for i, (bx, by, br, col) in enumerate([(250, 500, 420, (40, 70, 200)), (850, 1350, 520, (30, 50, 170)), (600, 900, 300, (244, 122, 58))]):
        ph = (t - t0) * 0.35 + i * 2.1
        g.ellipse((bx + 60 * math.sin(ph) - br, by + 50 * math.cos(ph * .8) - br, bx + 60 * math.sin(ph) + br, by + 50 * math.cos(ph * .8) + br), fill=col + (60 if i < 2 else 24,))
    lay.alpha_composite(glow.filter(ImageFilter.GaussianBlur(120)))
    d = ImageDraw.Draw(lay)
    # family link
    km = ease(t, t0 + 0.1, 0.4); kl = ease(t, cfg['t_link'], 0.6)
    for (x, lbl, k) in [(230, 'MAMA', km), (850, 'TY', km)]:
        if k <= 0: continue
        _person(d, x, 640, 150 * (0.7 + 0.3 * k), (255, 255, 255, int(255 * k)))
        d.text((x, 840), lbl, font=font(56), fill=(255, 255, 255, int(255 * k)), anchor='mm')
    if kl > 0:
        xe = 360 + (720 - 360) * kl
        d.line((360, 640, xe, 640), fill=ORANGE + (255,), width=12)
        d.text((540, 480), 'POKREWIEŃSTWO', font=font(40), fill=ORANGE + (int(255 * kl),), anchor='mm')
    # bank
    kb = ease(t, cfg['t_bank'], 0.4)
    if kb > 0:
        bx, by = 300, 1240
        d.polygon([(bx - 170, by - 60), (bx, by - 150), (bx + 170, by - 60)], fill=(255, 255, 255, int(255 * kb)))
        for c in range(4):
            cx = bx - 120 + c * 80
            d.rectangle((cx - 18, by - 45, cx + 18, by + 80), fill=(255, 255, 255, int(255 * kb)))
        d.rectangle((bx - 175, by + 85, bx + 175, by + 110), fill=(255, 255, 255, int(255 * kb)))
        d.text((bx, by + 165), 'BANK', font=font(52), fill=(255, 255, 255, int(255 * kb)), anchor='mm')
    # claim arrow from bank to TY
    ka = ease(t, cfg['t_claim'], 0.6)
    if ka > 0:
        x0, y0, x1, y1 = 420, 1080, 820, 900
        xe, ye = x0 + (x1 - x0) * ka, y0 + (y1 - y0) * ka
        d.line((x0, y0, xe, ye), fill=RED + (255,), width=12)
        d.text((770, 1080), 'SPŁATA?', font=font(48), fill=RED + (int(255 * ka),), anchor='mm')
    kx = ease(t, cfg['t_block'], 0.25)
    if kx > 0:
        cx, cy, s = 630, 985, 60
        d.ellipse((cx - s - 10, cy - s - 10, cx + s + 10, cy + s + 10), fill=(255, 255, 255, int(255 * kx)))
        d.line((cx - s * .6, cy - s * .6, cx + s * .6, cy + s * .6), fill=RED + (int(255 * kx),), width=14)
        d.line((cx + s * .6, cy - s * .6, cx - s * .6, cy + s * .6), fill=RED + (int(255 * kx),), width=14)
        f = font(50); tw = d.textlength(cfg['verdict'], font=f); y = 1560
        d.rounded_rectangle((W / 2 - tw / 2 - 44, y - 54, W / 2 + tw / 2 + 44, y + 54), 54, fill=ORANGE + (int(255 * kx),))
        d.text((W / 2, y + 2), cfg['verdict'], font=f, fill=(255, 255, 255, int(255 * kx)), anchor='mm')
    return lay


def notification(t, e, font):
    """iOS-style push notification sliding down from the top"""
    t0, t1, app, title, body, cy = e
    k = ease(t, t0, 0.35); a = min(1, (t1 - t) / 0.25)
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    x0, x1, h = 60, W - 60, 190; y0 = cy - h / 2 - 160 * (1 - k)
    card = Image.new('RGBA', (W, H)); cd = ImageDraw.Draw(card)
    cd.rounded_rectangle((x0, y0, x1, y0 + h), 40, fill=(245, 246, 250, int(245 * a)))
    lay.alpha_composite(card); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((x0 + 30, y0 + 30, x0 + 100, y0 + 100), 18, fill=RED + (int(255 * a),))
    d.text((x0 + 65, y0 + 66), '!', font=font(50), fill=(255, 255, 255, int(255 * a)), anchor='mm')
    d.text((x0 + 125, y0 + 50), app, font=font(30), fill=(120, 125, 140, int(255 * a)), anchor='lm')
    d.text((x1 - 35, y0 + 50), 'teraz', font=font(26), fill=(150, 155, 170, int(255 * a)), anchor='rm')
    d.text((x0 + 125, y0 + 100), title, font=font(40), fill=(20, 20, 30, int(255 * a)), anchor='lm')
    d.text((x0 + 125, y0 + 148), body, font=font(32), fill=RED + (int(255 * a),), anchor='lm')
    return _shadow(lay)


def tug(t, e, font):
    """child in the middle, two parents pulling; at t_pull the child is dragged to one side"""
    t0, t1, t_pull, label, cy = e
    a = min(1, (t - t0) / 0.3, (t1 - t) / 0.25)
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    _glass(d, (90, cy - 180, W - 90, cy + 170), 40, a)
    kp = ease(t, t_pull, 0.6)
    wob = 12 * math.sin((t - t0) * 9) * (1 - kp)
    cxc = W / 2 + wob - 150 * kp
    for x in (230, 850):
        _person(d, x, cy, 95, (255, 255, 255, int(255 * a)))
    d.line((300, cy - 10, cxc - 50, cy - 10), fill=ORANGE + (int(255 * a),), width=8)
    d.line((cxc + 50, cy - 10, 780, cy - 10), fill=ORANGE + (int(255 * a),), width=8)
    _person(d, cxc, cy + 15, 62, ORANGE + (int(255 * a),))
    d.text((W / 2, cy + 120), label, font=font(38), fill=(255, 255, 255, int(255 * a)), anchor='mm')
    return _shadow(lay)


def scene_label(t, e, font):
    """orange-placeholder animation: person with 'NARCYZ' tag, magnifier inspects tag, tag gets crossed; message pill"""
    t0, t1, cfg = e
    lay = Image.new('RGBA', (W, H), NAVY + (255,))
    glow = Image.new('RGBA', (W, H)); g = ImageDraw.Draw(glow)
    for i, (bx, by, br, col) in enumerate([(250, 500, 420, (40, 70, 200)), (850, 1350, 520, (30, 50, 170)), (600, 900, 300, (244, 122, 58))]):
        ph = (t - t0) * 0.35 + i * 2.1
        g.ellipse((bx + 60 * math.sin(ph) - br, by + 50 * math.cos(ph * .8) - br, bx + 60 * math.sin(ph) + br, by + 50 * math.cos(ph * .8) + br), fill=col + (60 if i < 2 else 24,))
    lay.alpha_composite(glow.filter(ImageFilter.GaussianBlur(120)))
    d = ImageDraw.Draw(lay)
    kpill = ease(t, cfg['t_msg'], 0.35)
    if kpill > 0:
        f = font(66); y = 330
        for j, ln in enumerate(cfg['msg']):
            tw = d.textlength(ln, font=f)
            d.text((W / 2, y + j * 84), ln, font=f, fill=(255, 255, 255, int(255 * kpill)), anchor='mm')
    k = ease(t, t0 + 0.1, 0.4)
    _person(d, 360, 1000, 260 * (0.8 + 0.2 * k), (255, 255, 255, int(255 * k)))
    # tag on a string
    kt = ease(t, t0 + 0.4, 0.4)
    if kt > 0:
        tx, ty = 760, 1150 + 25 * math.sin((t - t0) * 2.5)
        d.line((470, 960, tx, ty - 60), fill=(255, 255, 255, int(200 * kt)), width=4)
        f = font(64); tw = d.textlength(cfg['tag'], font=f)
        d.rounded_rectangle((tx - tw / 2 - 36, ty - 60, tx + tw / 2 + 36, ty + 60), 20, fill=ORANGE + (int(255 * kt),))
        d.text((tx, ty + 2), cfg['tag'], font=f, fill=(255, 255, 255, int(255 * kt)), anchor='mm')
        km = ease(t, cfg['t_lens'], 0.5)
        if km > 0:
            lx, ly = tx - 40 + 40 * km + 25 * math.sin((t - t0) * 3), ty - 260 + 60 * km
            d.ellipse((lx - 110, ly - 110, lx + 110, ly + 110), outline=(255, 255, 255, int(255 * km)), width=12)
            d.line((lx + 78, ly + 78, lx + 150, ly + 150), fill=(255, 255, 255, int(255 * km)), width=22)
        kx = ease(t, cfg['t_x'], 0.25)
        if kx > 0:
            s = 85
            for (p0, p1) in [((tx - s, ty - s), (tx + s, ty + s)), ((tx + s, ty - s), (tx - s, ty + s))]:
                e2 = (p0[0] + (p1[0] - p0[0]) * kx, p0[1] + (p1[1] - p0[1]) * kx)
                d.line([p0, e2], fill=RED + (255,), width=16)
    return lay


def scene_loyalty(t, e, font):
    """blue-placeholder animation: child shuttles between TATA and MAMA houses; bad words, fear, messages"""
    t0, t1, cfg = e
    lay = Image.new('RGBA', (W, H), NAVY + (255,))
    glow = Image.new('RGBA', (W, H)); g = ImageDraw.Draw(glow)
    for i, (bx, by, br, col) in enumerate([(250, 500, 420, (40, 70, 200)), (850, 1350, 520, (30, 50, 170)), (600, 900, 300, (244, 122, 58))]):
        ph = (t - t0) * 0.35 + i * 2.1
        g.ellipse((bx + 60 * math.sin(ph) - br, by + 50 * math.cos(ph * .8) - br, bx + 60 * math.sin(ph) + br, by + 50 * math.cos(ph * .8) + br), fill=col + (60 if i < 2 else 24,))
    lay.alpha_composite(glow.filter(ImageFilter.GaussianBlur(120)))
    d = ImageDraw.Draw(lay)
    k = ease(t, t0, 0.3)
    f = font(54); tw = d.textlength(cfg['title'], font=f); y = 250 - 30 * (1 - k)
    d.rounded_rectangle((W / 2 - tw / 2 - 44, y - 54, W / 2 + tw / 2 + 44, y + 54), 54, fill=ORANGE + (int(255 * k),))
    d.text((W / 2, y + 2), cfg['title'], font=f, fill=(255, 255, 255, int(255 * k)), anchor='mm')
    hy = 900; xs = {'TATA': 260, 'MAMA': 820}
    kh = ease(t, t0 + 0.3, 0.4)
    for lbl, x in xs.items():
        _house(d, x, hy, 200 * (0.7 + 0.3 * kh), (255, 255, 255, int(255 * kh)))
        d.text((x, hy + 230), lbl, font=font(60), fill=(255, 255, 255, int(255 * kh)), anchor='mm')
    # child position: at TATA, moves to MAMA at t_move, then shuttles with message
    km = ease(t, cfg['t_move'], 1.0)
    cx = xs['TATA'] + (xs['MAMA'] - xs['TATA']) * km
    if t >= cfg['t_msg']:
        ph = (t - cfg['t_msg']) * 0.9
        cx = W / 2 + (xs['MAMA'] - W / 2) * math.cos(ph * math.pi)
    cy = hy + 470
    _person(d, cx, cy, 120 * kh, ORANGE + (int(255 * kh),))
    # bad words bubble from TATA
    kb = ease(t, cfg['t_bad'], 0.3) * (1 - ease(t, cfg['t_move'], 0.3))
    if kb > 0:
        bx, by = xs['TATA'] + 80, hy - 330
        d.rounded_rectangle((bx - 150, by - 65, bx + 150, by + 65), 40, fill=(255, 255, 255, int(250 * kb)))
        d.polygon([(bx - 60, by + 60), (bx - 20, by + 60), (bx - 90, by + 120)], fill=(255, 255, 255, int(250 * kb)))
        d.text((bx, by + 2), '#@%!', font=font(60), fill=RED + (int(255 * kb),), anchor='mm')
    # fear: sealed lips label at MAMA
    kf = ease(t, cfg['t_fear'], 0.3) * (1 - ease(t, cfg['t_msg'], 0.3))
    if kf > 0:
        bx, by = xs['MAMA'] - 80, hy - 330
        d.rounded_rectangle((bx - 170, by - 65, bx + 170, by + 65), 40, fill=(255, 255, 255, int(250 * kf)))
        d.text((bx, by + 2), cfg['fear'], font=font(44), fill=NAVY + (int(255 * kf),), anchor='mm')
    # messages: envelope travelling with the child
    if t >= cfg['t_msg']:
        ke = ease(t, cfg['t_msg'], 0.3)
        _envelope(d, cx + 150, cy - 30, 60, ke)
        f2 = font(52); lbl = cfg['msg']; tw2 = d.textlength(lbl, font=f2)
        d.text((W / 2, 1680), lbl, font=f2, fill=ORANGE + (int(255 * ke),), anchor='mm')
    return lay


def _plane(d, x, y, s, ang, col):
    pts = [(1.0, 0), (0.85, -0.1), (0.15, -0.12), (-0.35, -0.75), (-0.55, -0.75), (-0.25, -0.12), (-0.8, -0.12), (-1.0, -0.4), (-1.12, -0.4), (-1.0, 0),
           (-1.12, 0.4), (-1.0, 0.4), (-0.8, 0.12), (-0.25, 0.12), (-0.55, 0.75), (-0.35, 0.75), (0.15, 0.12), (0.85, 0.1)]
    c, sn = math.cos(ang), math.sin(ang)
    d.polygon([(x + s * (px * c - py * sn), y + s * (px * sn + py * c)) for px, py in pts], fill=col)


def flight(t, e, font):
    """two pins (PL -> ?) with a dashed arc and a plane flying along it"""
    t0, t1, a_lbl, b_lbl, t_fly, cy = e
    a = min(1, (t - t0) / 0.3, (t1 - t) / 0.25)
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    _glass(d, (100, cy - 170, W - 100, cy + 150), 40, a)
    xa, xb, yb = 250, 830, cy + 60
    def P(u):
        x = xa + (xb - xa) * u; y = yb - 220 * math.sin(math.pi * u); return x, y
    for i in range(0, 40, 2):
        p0, p1 = P(i / 40), P((i + 1) / 40)
        d.line((p0, p1), fill=(255, 255, 255, int(170 * a)), width=5)
    for x, lbl, col in [(xa, a_lbl, (255, 255, 255)), (xb, b_lbl, ORANGE)]:
        d.ellipse((x - 48, yb - 48, x + 48, yb + 48), fill=col + (int(255 * a),))
        d.text((x, yb + 2), lbl, font=font(40), fill=(NAVY if col == (255, 255, 255) else (255, 255, 255)) + (int(255 * a),), anchor='mm')
    u = ease(t, t_fly, 1.4)
    if u > 0:
        x, y = P(u); x2, y2 = P(min(1, u + 0.01))
        _plane(d, x, y, 46, math.atan2(y2 - y, x2 - x), (255, 255, 255, int(255 * a)))
    return _shadow(lay)


def _flag_pl(d, x, y, w, h, a):
    d.rectangle((x, y, x + w, y + h / 2), fill=(255, 255, 255, int(255 * a)))
    d.rectangle((x, y + h / 2, x + w, y + h), fill=(220, 20, 60, int(255 * a)))


def scene_jurisdiction(t, e, font):
    """blue-placeholder animation: condition cards (citizen + 6 months) -> = POLSKI SĄD"""
    t0, t1, cfg = e
    lay = Image.new('RGBA', (W, H), NAVY + (255,))
    glow = Image.new('RGBA', (W, H)); g = ImageDraw.Draw(glow)
    for i, (bx, by, br, col) in enumerate([(250, 500, 420, (40, 70, 200)), (850, 1350, 520, (30, 50, 170)), (600, 900, 300, (244, 122, 58))]):
        ph = (t - t0) * 0.35 + i * 2.1
        g.ellipse((bx + 60 * math.sin(ph) - br, by + 50 * math.cos(ph * .8) - br, bx + 60 * math.sin(ph) + br, by + 50 * math.cos(ph * .8) + br), fill=col + (60 if i < 2 else 24,))
    lay.alpha_composite(glow.filter(ImageFilter.GaussianBlur(120)))
    d = ImageDraw.Draw(lay)
    k = ease(t, t0, 0.3)
    f = font(54); tw = d.textlength(cfg['title'], font=f); y = 250 - 30 * (1 - k)
    d.rounded_rectangle((W / 2 - tw / 2 - 44, y - 54, W / 2 + tw / 2 + 44, y + 54), 54, fill=ORANGE + (int(255 * k),))
    d.text((W / 2, y + 2), cfg['title'], font=f, fill=(255, 255, 255, int(255 * k)), anchor='mm')
    # card 1: citizen
    for j, (tc, t_ok, lbl) in enumerate([(cfg['t_c1'], cfg['t_c1ok'], cfg['c1']), (cfg['t_c2'], cfg['t_c2ok'], cfg['c2'])]):
        kc = ease(t, tc, 0.4)
        if kc <= 0: continue
        x0, y0 = 90, 420 + j * 330 + 40 * (1 - kc); x1 = W - 90
        card = Image.new('RGBA', (W, H)); ImageDraw.Draw(card).rounded_rectangle((x0, y0, x1, y0 + 270), 30, fill=(255, 255, 255, int(245 * kc)))
        lay.alpha_composite(card); d = ImageDraw.Draw(lay)
        if j == 0:
            _flag_pl(d, x0 + 50, y0 + 85, 150, 100, kc)
            d.rectangle((x0 + 50, y0 + 85, x0 + 200, y0 + 185), outline=(200, 205, 220, int(255 * kc)), width=3)
        else:
            cx, cy, r = x0 + 125, y0 + 135, 75
            d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(220, 222, 235, int(255 * kc)), width=16)
            kr = ease(t, cfg['t_ring'], 1.2)
            if kr > 0: d.arc((cx - r, cy - r, cx + r, cy + r), -90, -90 + 360 * kr, fill=ORANGE + (255,), width=16)
            d.text((cx, cy + 2), cfg['ring'], font=font(46), fill=NAVY + (int(255 * kc),), anchor='mm')
        for li, ln in enumerate(lbl.split('\n')):
            d.text((x0 + 250, y0 + 135 + (li - (len(lbl.split('\n')) - 1) / 2) * 56), ln, font=font(46), fill=NAVY + (int(255 * kc),), anchor='lm')
        ko = ease(t, t_ok, 0.3)
        if ko > 0:
            bx, by = x1 - 70, y0 + 135
            d.ellipse((bx - 42 * ko, by - 42 * ko, bx + 42 * ko, by + 42 * ko), fill=GREEN + (255,))
            d.line([(bx - 18, by + 2), (bx - 5, by + 16), (bx + 20, by - 14)], fill=(255, 255, 255, int(255 * ko)), width=8, joint='curve')
    kr = ease(t, cfg['t_res'], 0.4)
    if kr > 0:
        d.text((W / 2, 1190), '=', font=font(110), fill=ORANGE + (int(255 * kr),), anchor='mm')
        cx, cy = W / 2, 1420
        d.rounded_rectangle((cx - 120, cy - 70, cx + 40, cy - 10), 14, fill=(255, 255, 255, int(255 * kr)))
        d.line((cx - 20, cy - 10, cx + 70, cy + 70), fill=(255, 255, 255, int(255 * kr)), width=22)
        d.rectangle((cx - 170, cy + 80, cx + 170, cy + 100), fill=ORANGE + (int(255 * kr),))
        d.text((cx, cy + 170), cfg['res'], font=font(62), fill=(255, 255, 255, int(255 * kr)), anchor='mm')
    return lay


def boarding_pass(t, e, font):
    """boarding-pass ticket 'WARSZAWA -> ???' sliding in; 'CEL: ROZWÓD' stamp"""
    t0, t1, frm, to, t_to, purpose, cy = e
    k = ease(t, t0, 0.4); a = min(1, (t1 - t) / 0.25)
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    x0, x1, h = 110 - 300 * (1 - k), W - 110 - 300 * (1 - k), 300; y0 = cy - h / 2
    card = Image.new('RGBA', (W, H)); cd = ImageDraw.Draw(card)
    cd.rounded_rectangle((x0, y0, x1, y0 + h), 30, fill=(255, 255, 255, int(250 * a)))
    cd.rounded_rectangle((x0, y0, x1, y0 + 70), 30, fill=ORANGE + (int(255 * a),)); cd.rectangle((x0, y0 + 40, x1, y0 + 70), fill=ORANGE + (int(255 * a),))
    for yy in range(int(y0 + 85), int(y0 + h - 15), 22):
        cd.line((x1 - 230, yy, x1 - 230, yy + 10), fill=(200, 205, 220, int(255 * a)), width=4)
    lay.alpha_composite(card); d = ImageDraw.Draw(lay)
    d.text((x0 + 40, y0 + 36), 'BOARDING PASS', font=font(32), fill=(255, 255, 255, int(255 * a)), anchor='lm')
    d.text((x0 + 40, y0 + 130), frm, font=font(54), fill=NAVY + (int(255 * a),), anchor='lm')
    fw = d.textlength(frm, font=font(54))
    _plane(d, x0 + 40 + fw + 55, y0 + 130, 30, 0, ORANGE + (int(255 * a),))
    kt = ease(t, t_to, 0.3)
    d.text((x0 + 40 + fw + 110, y0 + 130), to if kt > 0.5 else '…', font=font(54), fill=(RED if kt > 0.5 else NAVY) + (int(255 * a),), anchor='lm')
    d.text((x0 + 40, y0 + 220), 'CEL:', font=font(36), fill=(120, 125, 140, int(255 * a)), anchor='lm')
    d.text((x0 + 135, y0 + 220), purpose, font=font(44), fill=NAVY + (int(255 * a),), anchor='lm')
    _plane(d, x1 - 115, y0 + 185, 44, -0.5, (210, 214, 228, int(255 * a)))
    return _shadow(lay)


def scene_key(t, e, font):
    """two puzzle halves (citizenship + residence) slide together into a key that unlocks 'POLSKI SĄD'"""
    t0, t1, cfg = e
    lay = Image.new('RGBA', (W, H), NAVY + (255,))
    glow = Image.new('RGBA', (W, H)); g = ImageDraw.Draw(glow)
    for i, (bx, by, br, col) in enumerate([(250, 500, 420, (40, 70, 200)), (850, 1350, 520, (30, 50, 170)), (600, 900, 300, (244, 122, 58))]):
        ph = (t - t0) * 0.35 + i * 2.1
        g.ellipse((bx + 60 * math.sin(ph) - br, by + 50 * math.cos(ph * .8) - br, bx + 60 * math.sin(ph) + br, by + 50 * math.cos(ph * .8) + br), fill=col + (60 if i < 2 else 24,))
    lay.alpha_composite(glow.filter(ImageFilter.GaussianBlur(120)))
    d = ImageDraw.Draw(lay)
    k0 = ease(t, t0, 0.3)
    f0 = font(54); tw0 = d.textlength(cfg['title'], font=f0); y = 250 - 30 * (1 - k0)
    d.rounded_rectangle((W / 2 - tw0 / 2 - 44, y - 54, W / 2 + tw0 / 2 + 44, y + 54), 54, fill=ORANGE + (int(255 * k0),))
    d.text((W / 2, y + 2), cfg['title'], font=f0, fill=(255, 255, 255, int(255 * k0)), anchor='mm')
    kj = ease(t, cfg['t_join'], 0.6)
    for j, (tp, lbl, col) in enumerate([(cfg['t_p1'], cfg['p1'], (255, 255, 255)), (cfg['t_p2'], cfg['p2'], ORANGE)]):
        kp = ease(t, tp, 0.4)
        if kp <= 0: continue
        w, h = 400, 300
        tx = 540 - w - 4 if j == 0 else 544
        sx = (60 if j == 0 else W - 60 - w)
        x = sx + (tx - sx) * kj; y = 520 + 60 * (1 - kp)
        d.rounded_rectangle((x, y, x + w, y + h), 30, fill=col + (int(250 * kp),))
        nx = x + w if j == 0 else x
        if j == 0: d.ellipse((nx - 45, y + h / 2 - 45, nx + 45, y + h / 2 + 45), fill=col + (int(250 * kp),))
        else: d.ellipse((nx - 45, y + h / 2 - 45, nx + 45, y + h / 2 + 45), fill=NAVY + (255,))
        tc = NAVY if j == 0 else (255, 255, 255)
        fs = 44
        while fs > 24 and max(d.textlength(l, font=font(fs)) for l in lbl.split('\n')) > w - 110: fs -= 2
        for li, ln in enumerate(lbl.split('\n')):
            d.text((x + w / 2 + (-20 if j == 0 else 25), y + h / 2 + (li - (len(lbl.split('\n')) - 1) / 2) * (fs + 12)), ln, font=font(fs), fill=tc + (int(255 * kp),), anchor='mm')
    # lock -> opens (full padlock: shackle + body + keyhole; on open the shackle lifts and the left leg comes out)
    kl = ease(t, cfg['t_lock'], 0.4); ko = ease(t, cfg['t_open'], 0.45)
    if kl > 0:
        cx, by = W / 2, 1150                       # body top
        bw, bh, sw = 300, 250, 30                  # body size, shackle stroke
        ro = 105                                   # shackle outer half-width
        lift = 70 * ko
        col_s = (255, 255, 255, int(255 * kl))
        body_col = (GREEN if ko > 0.5 else ORANGE) + (int(255 * kl),)
        top = by - 230 - lift
        # shackle: arc + two legs
        d.arc((cx - ro, top, cx + ro, top + 2 * ro), 180, 360, fill=col_s, width=sw)
        leg_bottom = by + 20
        d.line((cx + ro - sw / 2, top + ro, cx + ro - sw / 2, leg_bottom - lift * 0), fill=col_s, width=sw)
        if ko < 0.5:
            d.line((cx - ro + sw / 2, top + ro, cx - ro + sw / 2, leg_bottom), fill=col_s, width=sw)
        else:
            d.line((cx - ro + sw / 2, top + ro, cx - ro + sw / 2, top + ro + 50), fill=col_s, width=sw)
        # body
        d.rounded_rectangle((cx - bw / 2, by, cx + bw / 2, by + bh), 34, fill=body_col)
        d.rounded_rectangle((cx - bw / 2 + 14, by + 14, cx + bw / 2 - 14, by + bh - 14), 26, outline=(255, 255, 255, int(70 * kl)), width=4)
        # keyhole
        kx, ky = cx, by + bh * 0.42
        d.ellipse((kx - 30, ky - 30, kx + 30, ky + 30), fill=NAVY + (int(255 * kl),))
        d.polygon([(kx - 16, ky + 10), (kx + 16, ky + 10), (kx + 24, ky + 85), (kx - 24, ky + 85)], fill=NAVY + (int(255 * kl),))
        if ko > 0: d.text((cx, by + bh + 110), cfg['res'], font=font(70), fill=(255, 255, 255, int(255 * ko)), anchor='mm')
    return lay



def scene_passport(t, e, font):
    """open passport; two stamps slam in (citizenship, 6 months) -> gavel 'POLSKI SĄD'"""
    t0, t1, cfg = e
    lay = Image.new('RGBA', (W, H), NAVY + (255,))
    glow = Image.new('RGBA', (W, H)); g = ImageDraw.Draw(glow)
    for i, (bx, by, br, col) in enumerate([(250, 500, 420, (40, 70, 200)), (850, 1350, 520, (30, 50, 170)), (600, 900, 300, (244, 122, 58))]):
        ph = (t - t0) * 0.35 + i * 2.1
        g.ellipse((bx + 60 * math.sin(ph) - br, by + 50 * math.cos(ph * .8) - br, bx + 60 * math.sin(ph) + br, by + 50 * math.cos(ph * .8) + br), fill=col + (60 if i < 2 else 24,))
    lay.alpha_composite(glow.filter(ImageFilter.GaussianBlur(120)))
    d = ImageDraw.Draw(lay)
    k = ease(t, t0 + 0.1, 0.5)
    x0, y0, x1, y1 = 120, 300 + 60 * (1 - k), W - 120, 1150 + 60 * (1 - k)
    d.rounded_rectangle((x0 - 14, y0 - 14, x1 + 14, y1 + 14), 30, fill=(120, 20, 40, int(255 * k)))
    d.rounded_rectangle((x0, y0, x1, y1), 22, fill=(250, 246, 236, int(255 * k)))
    d.line((W / 2, y0, W / 2, y1), fill=(210, 200, 180, int(255 * k)), width=4)
    d.text((x0 + 200, y0 + 70), 'PASZPORT', font=font(40), fill=(120, 20, 40, int(255 * k)), anchor='mm')
    d.rounded_rectangle((x0 + 60, y0 + 130, x0 + 340, y0 + 470), 16, fill=(220, 214, 200, int(255 * k)))
    _person(d, x0 + 200, y0 + 330, 110, (170, 160, 140, int(255 * k)))
    for j in range(4):
        d.rounded_rectangle((x0 + 60, y0 + 520 + j * 60, x0 + 340 - (60 if j == 3 else 0), y0 + 540 + j * 60), 10, fill=(215, 208, 192, int(255 * k)))
    for (ts, txt, pos) in [(cfg['t_s1'], cfg['s1'], (W / 2 + 200, y0 + 260)), (cfg['t_s2'], cfg['s2'], (W / 2 + 200, y0 + 560))]:
        if t >= ts:
            lay.alpha_composite(stamp(t, (ts, t1, txt, pos, 0.62), font)); d = ImageDraw.Draw(lay)
    kr = ease(t, cfg['t_res'], 0.4)
    if kr > 0:
        cx, cy = W / 2, 1380
        d.rounded_rectangle((cx - 120, cy - 70, cx + 40, cy - 10), 14, fill=(255, 255, 255, int(255 * kr)))
        d.line((cx - 20, cy - 10, cx + 70, cy + 70), fill=(255, 255, 255, int(255 * kr)), width=22)
        d.rectangle((cx - 170, cy + 80, cx + 170, cy + 100), fill=ORANGE + (int(255 * kr),))
        d.text((cx, cy + 170), cfg['res'], font=font(62), fill=(255, 255, 255, int(255 * kr)), anchor='mm')
    return lay


# ---------- MODERN set (short 16): gradients, outlined numerals, kinetic type, progress tracker ----------
GRAD_A, GRAD_B = (244, 122, 58), (255, 178, 90)        # brand orange gradient (author: orange + navy)


def _grad(w, h, c1=GRAD_A, c2=GRAD_B, diag=True):
    x = np.linspace(0, 1, w)[None, :]; y = np.linspace(0, 1, h)[:, None]
    t = (x * 0.7 + y * 0.3) if diag else x + y * 0
    arr = np.zeros((h, w, 4), np.uint8)
    for i in range(3): arr[..., i] = (c1[i] + (c2[i] - c1[i]) * t).astype(np.uint8)
    arr[..., 3] = 255
    return Image.fromarray(arr, 'RGBA')


def _grad_text(txt, f, c1=GRAD_A, c2=GRAD_B):
    d0 = ImageDraw.Draw(Image.new('L', (1, 1))); bb = d0.textbbox((0, 0), txt, font=f)
    w, h = bb[2] - bb[0] + 20, bb[3] - bb[1] + 20
    m = Image.new('L', (w, h)); ImageDraw.Draw(m).text((10 - bb[0], 10 - bb[1]), txt, font=f, fill=255)
    g = _grad(w, h, c1, c2); g.putalpha(m); return g


def _kinetic(lay, t, t0, words, cx, cy, size, font, color=(255, 255, 255), stagger=0.09, grad_word=None):
    """words slide up from a mask one by one; returns nothing"""
    f = font(size); d = ImageDraw.Draw(lay)
    widths = [d.textlength(w, font=f) for w in words]; gap = size * 0.3
    total = sum(widths) + gap * (len(words) - 1); x = cx - total / 2
    for i, (w, ww) in enumerate(zip(words, widths)):
        k = ease(t, t0 + i * stagger, 0.35)
        if k > 0:
            h = int(size * 1.4)
            tl = Image.new('RGBA', (int(ww) + 20, h)); ImageDraw.Draw(tl).text((10, h * 0.5), w, font=f, fill=color + (255,), anchor='lm')
            if grad_word is not None and i == grad_word:
                g = _grad(tl.size[0], tl.size[1]); g.putalpha(tl.split()[3]); tl = g
            sh = int(h * (1 - k))
            crop = Image.new('RGBA', tl.size); crop.alpha_composite(tl, (0, sh)) if sh < tl.size[1] else None
            lay.alpha_composite(crop, (int(x - 10), int(cy - h / 2)))
        x += ww + gap


def _dark_card(lay, box, r=36, a=1.0, border=True):
    x0, y0, x1, y1 = [int(v) for v in box]
    c = Image.new('RGBA', (W, H)); cd = ImageDraw.Draw(c)
    cd.rounded_rectangle(box, r, fill=(2, 6, 74, int(220 * a)))
    lay.alpha_composite(c)
    if border:
        g = _grad(x1 - x0, y1 - y0)
        m = Image.new('L', (x1 - x0, y1 - y0)); md = ImageDraw.Draw(m)
        md.rounded_rectangle((0, 0, x1 - x0 - 1, y1 - y0 - 1), r, outline=int(255 * a), width=4)
        g.putalpha(m); lay.alpha_composite(g, (x0, y0))


def big_count(t, e, font):
    """outlined giant numeral + gradient label sliding in"""
    t0, t1, num, label, cy = e
    a = min(1, (t1 - t) / 0.25)
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    k = ease(t, t0, 0.45)
    f = font(int(330 * (0.8 + 0.2 * k)))
    d.text((200, cy), num, font=f, fill=(255, 255, 255, 0), anchor='mm', stroke_width=8, stroke_fill=(255, 255, 255, int(235 * a * k)))
    _kinetic(lay, t, t0 + 0.2, [label], 720, cy, 84, font, grad_word=0)
    if a < 1: lay = _alpha(lay, a)
    return _shadow(lay, 12, 0.5, 6)


def tracker(t, e, font):
    """top progress tracker: 4 segments, current number + label kinetic under it"""
    t0, t1, steps, cy = e
    a = min(1, (t - t0) / 0.3, (t1 - t) / 0.3)
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    n = len(steps); x0, x1 = 140, W - 140; gap = 18; sw = (x1 - x0 - gap * (n - 1)) / n
    cur = max([i for i, (st, _) in enumerate(steps) if t >= st] or [0])
    for i in range(n):
        xs = x0 + i * (sw + gap)
        d.rounded_rectangle((xs, cy, xs + sw, cy + 12), 6, fill=(255, 255, 255, int(70 * a)))
        if i < cur: fr = 1
        elif i == cur: fr = ease(t, steps[i][0], 0.6)
        else: fr = 0
        if fr > 0:
            g = _grad(max(2, int(sw * fr)), 12); m = Image.new('L', g.size); ImageDraw.Draw(m).rounded_rectangle((0, 0, g.size[0] - 1, 11), 6, fill=int(255 * a)); g.putalpha(m)
            lay.alpha_composite(g, (int(xs), int(cy)))
    st, lbl = steps[cur]
    d = ImageDraw.Draw(lay)
    num = f'0{cur + 1}'
    d.text((x0, cy + 75), num, font=font(80), fill=ORANGE + (int(255 * a),), anchor='lm')
    d.text((x0 + 125, cy + 75), f'/ 0{n}', font=font(30), fill=(255, 255, 255, int(150 * a)), anchor='lm')
    sub = Image.new('RGBA', (W, H)); _kinetic(sub, t, st + 0.1, lbl.split(), W / 2 + 70, cy + 72, 44, font, stagger=0.06)
    lay.alpha_composite(_alpha(sub, a))
    return _shadow(lay, 10, 0.55, 4)


def kinetic_title(t, e, font):
    """kinetic headline lines on a soft dark card; gradient accent word index per line"""
    t0, t1, lines, cy, size = e[:5]; accents = e[5] if len(e) > 5 else {}
    a = min(1, (t - t0) / 0.25, (t1 - t) / 0.25)
    lay = Image.new('RGBA', (W, H))
    lh = size * 1.2; hgt = lh * len(lines) + 70
    fw = max(ImageDraw.Draw(lay).textlength(l, font=font(size)) for l in lines) + 110
    _dark_card(lay, (W / 2 - fw / 2, cy - hgt / 2, W / 2 + fw / 2, cy + hgt / 2), 40, a)
    for i, ln in enumerate(lines):
        _kinetic(lay, t, t0 + 0.1 + i * 0.25, ln.split(), W / 2, cy - lh * (len(lines) - 1) / 2 + i * lh, size, font, grad_word=accents.get(str(i)))
    return _alpha(_shadow(lay), a) if a < 1 else _shadow(lay)


def chips(t, e, font):
    """pill chips popping in a row with gradient outline"""
    t0, t1, items, cy = e
    a = min(1, (t1 - t) / 0.25)
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    f = font(40); ws = [d.textlength(s, font=f) + 70 for _, s in items]; gap = 20
    stack = sum(ws) + gap * (len(ws) - 1) > W - 120
    x = (W - sum(ws) - gap * (len(ws) - 1)) / 2
    for idx, ((ct, s), w) in enumerate(zip(items, ws)):
        if stack: x = (W - w) / 2
        k = ease(t, ct, 0.3)
        if k > 0:
            h = 84; y = cy - h / 2 + 20 * (1 - k) + (idx * 104 if stack else 0)
            _dark_card(lay, (x, y, x + w, y + h), 42, a * k)
            d = ImageDraw.Draw(lay)
            d.text((x + w / 2, y + h / 2 + 2), s, font=f, fill=(255, 255, 255, int(255 * a * k)), anchor='mm')
        if not stack: x += w + gap
    return _shadow(lay)


def _modern_bg(t, t0, flip=False):
    g = _grad(W, H, (2, 6, 74), (16, 34, 130)) if not flip else _grad(W, H, (16, 34, 130), (2, 6, 74))
    blob = Image.new('RGBA', (W, H)); b = ImageDraw.Draw(blob)
    for i, (bx, by, br, col) in enumerate([(200, 400, 380, GRAD_A), (900, 1500, 460, (40, 80, 220)), (700, 900, 260, (60, 110, 255))]):
        ph = (t - t0) * 0.4 + i * 2
        b.ellipse((bx + 70 * math.sin(ph) - br, by + 60 * math.cos(ph) - br, bx + 70 * math.sin(ph) + br, by + 60 * math.cos(ph) + br), fill=col + (70,))
    g.alpha_composite(blob.filter(ImageFilter.GaussianBlur(140)))
    # subtle grid
    gr = Image.new('RGBA', (W, H)); gd = ImageDraw.Draw(gr)
    for x in range(0, W, 90): gd.line((x, 0, x, H), fill=(255, 255, 255, 12), width=1)
    for y in range(0, H, 90): gd.line((0, y, W, y), fill=(255, 255, 255, 12), width=1)
    g.alpha_composite(gr)
    return g


def scene_two_homes_modern(t, e, font):
    """argument 2: child between two homes; age + emotions; 'not every child is ready'"""
    t0, t1, cfg = e
    lay = _modern_bg(t, t0)
    d = ImageDraw.Draw(lay)
    k = ease(t, t0, 0.4)
    d.text((110, 300), '02', font=font(220), fill=ORANGE + (int(255 * k),), anchor='lm')
    sub = Image.new('RGBA', (W, H)); _kinetic(sub, t, t0 + 0.15, cfg['title'].split(), 690, 300, 64, font, grad_word=0); lay.alpha_composite(sub)
    d = ImageDraw.Draw(lay)
    # two homes
    kh = ease(t, cfg['t_homes'], 0.5)
    for x in (270, 810):
        if kh > 0:
            _dark_card(lay, (x - 200, 600, x + 200, 1020), 44, kh); d = ImageDraw.Draw(lay)
            _house(d, x, 820, 140 * (0.7 + 0.3 * kh), (255, 255, 255, int(255 * kh)))
    # child bouncing between homes on a dashed path
    if kh > 0:
        for i in range(0, 30, 2):
            xa = 270 + (810 - 270) * i / 30; xb = 270 + (810 - 270) * (i + 1) / 30
            d.line((xa, 1110, xb, 1110), fill=(255, 255, 255, int(120 * kh)), width=4)
        u = 0.5 + 0.5 * math.sin((t - t0) * 2.2)
        _person(d, 270 + 540 * u, 1085 - 40 * abs(math.sin((t - t0) * 4.4)), 60, GRAD_A + (int(255 * kh),))
    # need gauges
    for j, (tt, lbl, val) in enumerate(cfg['gauges']):
        kg = ease(t, tt, 0.5)
        if kg <= 0: continue
        y = 1260 + j * 130; x0, x1 = 130, W - 130
        d.text((x0, y), lbl, font=font(40), fill=(255, 255, 255, int(255 * kg)), anchor='lm')
        d.rounded_rectangle((x0, y + 35, x1, y + 55), 10, fill=(255, 255, 255, 40))
        fill = int((x1 - x0) * val * ease(t, tt + 0.1, 0.9))
        if fill > 4:
            g = _grad(fill, 20); m = Image.new('L', g.size); ImageDraw.Draw(m).rounded_rectangle((0, 0, fill - 1, 19), 10, fill=255); g.putalpha(m)
            lay.alpha_composite(g, (x0, y + 35))
        d = ImageDraw.Draw(lay)
    kv = ease(t, cfg['t_verdict'], 0.35)
    if kv > 0:
        sub = Image.new('RGBA', (W, H)); _kinetic(sub, t, cfg['t_verdict'], cfg['verdict'].split(), W / 2, 1620, 50, font, stagger=0.07, grad_word=1); lay.alpha_composite(sub)
    return lay


def scene_distance_modern(t, e, font):
    """argument 4: stylised map, route draws between two pins, car moves, timer counts minutes; school/routine tags"""
    t0, t1, cfg = e
    lay = _modern_bg(t, t0, flip=True)
    d = ImageDraw.Draw(lay)
    k = ease(t, t0, 0.4)
    d.text((110, 300), '04', font=font(220), fill=ORANGE + (int(255 * k),), anchor='lm')
    sub = Image.new('RGBA', (W, H)); _kinetic(sub, t, t0 + 0.15, cfg['title'].split(), 690, 300, 64, font, grad_word=0); lay.alpha_composite(sub)
    _dark_card(lay, (90, 520, W - 90, 1180), 44, k); d = ImageDraw.Draw(lay)
    # route as smooth s-curve
    pts = [(220 + 640 * u, 1020 - 330 * u + 120 * math.sin(u * math.pi * 2)) for u in np.linspace(0, 1, 60)]
    kr = ease(t, cfg['t_route'], 1.2)
    n = max(2, int(len(pts) * kr))
    if kr > 0:
        g = Image.new('RGBA', (W, H)); gd = ImageDraw.Draw(g); gd.line(pts[:n], fill=(255, 255, 255, 255), width=14, joint='curve')
        gm = g.split()[3]; gg = _grad(W, H); gg.putalpha(gm); lay.alpha_composite(gg); d = ImageDraw.Draw(lay)
        cx, cy = pts[n - 1]
        d.ellipse((cx - 22, cy - 22, cx + 22, cy + 22), fill=(255, 255, 255, 255))
    for (px, py), lbl in [(pts[0], 'DOM 1'), (pts[-1], 'DOM 2')]:
        d.ellipse((px - 34, py - 34, px + 34, py + 34), fill=(12, 14, 30, int(255 * k)), outline=(255, 255, 255, int(255 * k)), width=6)
        d.text((px, py + 70), lbl, font=font(34), fill=(255, 255, 255, int(255 * k)), anchor='mm')
    # timer
    kt = ease(t, cfg['t_timer'], 1.0)
    if kt > 0:
        mins = int(cfg['minutes'] * kt)
        tl = _grad_text(f'{mins} MIN', font(120)); lay.alpha_composite(tl, (int(W / 2 - tl.size[0] / 2), 1230))
        d = ImageDraw.Draw(lay)
        d.text((W / 2, 1410), 'W JEDNĄ STRONĘ', font=font(36), fill=(255, 255, 255, int(200 * kt)), anchor='mm')
    sub = Image.new('RGBA', (W, H)); lay.alpha_composite(chips(t, (t0, t1, cfg['tags'], 1560), font))
    return lay



def four_count(t, e, font):
    """four squares pop in one by one (1..4, orange), then navy pill 'ARGUMENTY'"""
    t0, t1, times, label, t_lbl, cy = e
    a = min(1, (t1 - t) / 0.25)
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    n = len(times); sz, gap = 150, 26; x0 = (W - n * sz - (n - 1) * gap) / 2
    for i, tt in enumerate(times):
        k = ease(t, tt, 0.3)
        if k <= 0: continue
        x = x0 + i * (sz + gap); s2 = sz * (0.6 + 0.4 * k); o = (sz - s2) / 2
        d.rounded_rectangle((x + o, cy - sz / 2 + o, x + o + s2, cy - sz / 2 + o + s2), 30, fill=ORANGE + (int(255 * a * k),))
        d.text((x + sz / 2, cy + 4), str(i + 1), font=font(int(96 * (0.6 + 0.4 * k))), fill=(255, 255, 255, int(255 * a * k)), anchor='mm')
    kl = ease(t, t_lbl, 0.3)
    if kl > 0:
        f = font(56); tw = d.textlength(label, font=f); y = cy + sz / 2 + 80 - 20 * (1 - kl)
        d.rounded_rectangle((W / 2 - tw / 2 - 46, y - 52, W / 2 + tw / 2 + 46, y + 52), 52, fill=NAVY + (int(240 * a * kl),))
        d.text((W / 2, y + 2), label, font=f, fill=(255, 255, 255, int(255 * a * kl)), anchor='mm')
    return _shadow(lay)


def hook_question(t, e, font):
    """navy card 'DOBRY RODZIC' gets a green tick -> arrow -> orange card 'OPIEKA NAPRZEMIENNA' -> big '?' pops"""
    t0, t1, left, t_ok, right, t_right, t_q, cy = e
    a = min(1, (t - t0) / 0.25, (t1 - t) / 0.25)
    lay = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(lay)
    cw, ch = 400, 190
    kl = ease(t, t0 + 0.05, 0.35)
    lx = 70; d.rounded_rectangle((lx, cy - ch / 2 + 30 * (1 - kl), lx + cw, cy + ch / 2 + 30 * (1 - kl)), 34, fill=NAVY + (int(240 * a * kl),))
    for j, ln in enumerate(left.split('\n')):
        d.text((lx + cw / 2, cy + (j - (len(left.split('\n')) - 1) / 2) * 58), ln, font=font(50), fill=(255, 255, 255, int(255 * a * kl)), anchor='mm')
    ko = ease(t, t_ok, 0.3)
    if ko > 0:
        bx, by = lx + cw - 8, cy - ch / 2 + 8; r = 36 * (0.5 + 0.5 * ko)
        d.ellipse((bx - r, by - r, bx + r, by + r), fill=GREEN + (int(255 * a),))
        d.line([(bx - 15, by + 2), (bx - 4, by + 13), (bx + 16, by - 11)], fill=(255, 255, 255, int(255 * a * ko)), width=7, joint='curve')
    kr = ease(t, t_right, 0.35)
    if kr > 0:
        ax0, ax1 = lx + cw + 20, lx + cw + 20 + 70 * kr
        d.line((ax0, cy, ax1, cy), fill=(255, 255, 255, int(255 * a)), width=10)
        if kr > 0.9: d.polygon([(ax1 + 18, cy), (ax1 - 4, cy - 18), (ax1 - 4, cy + 18)], fill=(255, 255, 255, int(255 * a)))
        rx = W - 70 - cw
        d.rounded_rectangle((rx, cy - ch / 2 + 30 * (1 - kr), rx + cw, cy + ch / 2 + 30 * (1 - kr)), 34, fill=ORANGE + (int(250 * a * kr),))
        fs = 46
        while fs > 24 and max(d.textlength(l, font=font(fs)) for l in right.split('\n')) > cw - 50: fs -= 2
        for j, ln in enumerate(right.split('\n')):
            d.text((rx + cw / 2, cy + (j - (len(right.split('\n')) - 1) / 2) * (fs + 12)), ln, font=font(fs), fill=(255, 255, 255, int(255 * a * kr)), anchor='mm')
    kq = ease(t, t_q, 0.3)
    if kq > 0:
        qx, qy = W - 110, cy - ch / 2 - 30; r = 62 * (0.5 + 0.5 * kq)
        d.ellipse((qx - r, qy - r, qx + r, qy + r), fill=(255, 255, 255, int(255 * a)))
        d.text((qx, qy + 4), '?', font=font(int(90 * (0.5 + 0.5 * kq))), fill=NAVY + (int(255 * a),), anchor='mm')
    return _shadow(lay)
