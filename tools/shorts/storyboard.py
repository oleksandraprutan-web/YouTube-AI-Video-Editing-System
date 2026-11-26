"""Storyboard sheets from storyboard.json ([[t, code, text], ...]) -> out/storyboard_N.jpg. Run in the project folder."""
import sys, subprocess, json, os
sys.argv = ['x']; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render
from PIL import Image, ImageDraw, ImageFont
F = os.path.expanduser('~/.fonts/Montserrat-Black.ttf')
B = json.load(open('storyboard.json'))
tw, th, cap, cols = 300, 533, 120, 5
os.makedirs('out', exist_ok=True)
for part in range(0, len(B), 10):
    chunk = B[part:part + 10]; rows = (len(chunk) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * tw + (cols + 1) * 14, rows * (th + cap) + (rows + 1) * 14), (18, 18, 24))
    d = ImageDraw.Draw(sheet)
    for i, (t, code, txt) in enumerate(chunk):
        raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(t), '-i', render.SRC, '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
        im = render.render_frame(Image.frombytes('RGB', (1080, 1920), raw), t).resize((tw, th))
        x = 14 + (i % cols) * (tw + 14); y = 14 + (i // cols) * (th + cap + 14)
        sheet.paste(im, (x, y))
        m, s = divmod(t, 60)
        d.rounded_rectangle((x, y + th + 8, x + 116, y + th + 44), 8, fill=(244, 122, 58))
        d.text((x + 58, y + th + 26), f'{int(m)}:{s:04.1f}', font=ImageFont.truetype(F, 22), fill='white', anchor='mm')
        d.text((x + 128, y + th + 26), code, font=ImageFont.truetype(F, 24), fill=(244, 122, 58), anchor='lm')
        d.multiline_text((x, y + th + 52), txt, font=ImageFont.truetype(F, 19), fill='white', spacing=4)
    sheet.save(f'out/storyboard_{part // 10 + 1}.jpg', quality=90)
print('ok')
