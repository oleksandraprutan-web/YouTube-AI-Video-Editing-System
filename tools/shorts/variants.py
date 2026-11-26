"""Variant sheets: python3 variants.py variants.json -> out/<name>.jpg ; json: {"name":..., "times":[..], "variants":{"A · ...": {"KEY": value,...}}}"""
import sys, subprocess, json, os
cfgp = sys.argv[1]; sys.argv = ['x']; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render
from PIL import Image, ImageDraw, ImageFont
C = json.load(open(cfgp)); V = C['variants']; ts = C['times']
F = ImageFont.truetype(os.path.expanduser('~/.fonts/Montserrat-Black.ttf'), 30)
n = len(ts); cw = n * 275 + 10
sheet = Image.new('RGB', (len(V) * (cw + 20) + 10, 560), (18, 18, 24)); d = ImageDraw.Draw(sheet)
def conv(v):
    if isinstance(v, list): return [conv(x) for x in v]
    if isinstance(v, dict): return {k: conv(x) for k, x in v.items()}
    return v
for vi, (name, cfg) in enumerate(V.items()):
    saved = {k: getattr(render, k) for k in cfg}
    for k, v in cfg.items():
        v = conv(v)
        if isinstance(v, list): v = [tuple(tuple(z) if isinstance(z, list) and k != 'SCENES' else z for z in x) if isinstance(x, list) else x for x in v]
        setattr(render, k, v)
    for ti, t in enumerate(ts):
        raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(t), '-i', render.SRC, '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
        im = render.render_frame(Image.frombytes('RGB', (1080, 1920), raw), t).resize((270, 480))
        sheet.paste(im, (20 + vi * (cw + 20) + ti * 275, 65))
    d.text((20 + vi * (cw + 20), 20), name, font=F, fill=(244, 122, 58))
    for k, v in saved.items(): setattr(render, k, v)
sheet.save(f"out/{C['name']}.jpg", quality=90)
print('ok')
