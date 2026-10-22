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
