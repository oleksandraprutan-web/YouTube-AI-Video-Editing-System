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
    t0, t1, title, q, t_q = e
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
    d.text((sx, sy + 2), 'SĄD', font=font(34), fill=RED + (int(220 * k),), anchor='mm')
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
    n = len(steps); bw = 300; gap = 25; x0 = (W - n * bw - (n - 1) * gap) / 2
    for i, (st, lbl, col) in enumerate(steps):
        k = ease(t, st, 0.35)
        h = 150 + i * 90; x = x0 + i * (bw + gap); yb = cy + 150
        on = k > 0
        fillc = (tuple(col) + (int(240 * a),)) if on else (255, 255, 255, int(40 * a))
        card = Image.new('RGBA', (W, H)); cd = ImageDraw.Draw(card)
        hh = h * (0.85 + 0.15 * k) if on else h
        cd.rounded_rectangle((x, yb - hh, x + bw, yb), 24, fill=fillc, outline=(255, 255, 255, int(120 * a)), width=3)
        lay.alpha_composite(card); d = ImageDraw.Draw(lay)
        for j, ln in enumerate(lbl.split('\n')):
            d.text((x + bw / 2, yb - hh / 2 + (j - (len(lbl.split('\n')) - 1) / 2) * 46), ln, font=font(38), fill=(255, 255, 255, int(255 * a * (1 if on else .45))), anchor='mm')
    return _shadow(lay)
