import numpy as np, soundfile as sf, subprocess, os
from PIL import Image, ImageDraw, ImageFont
SR = 48000; SLOT = 2.0
L = '../lawyer-test/sfx/'
items = [
 (L + 'click-pop_04_B.wav', 'Щелчок', 'сейчас: плашки, списки'),
 (L + 'click-pop_01_A.wav', 'Короткий щелчок', 'сейчас: пункты, галочки'),
 (L + 'click-pop_05_C.wav', 'Щелчок-таблетка', 'сейчас: таблетки'),
 (L + 'hit_01_A.wav', 'Удар', 'сейчас: галочка, резкий наезд'),
 (L + 'bass_01_A.wav', 'Низкий бас', 'драматичный момент'),
 (L + 'whoosh-rise_04_C.wav', 'Плавный свист', 'сейчас: вход/выход синего фона'),
 (L + 'typing.mp3', 'Печать (ваш звук)', 'сейчас: текст на синем'),
 ('pop.wav', 'Поп-пузырёк', 'появление текста/иконки'),
 ('tap.wav', 'Тап', 'мелкие элементы, кружки-месяцы'),
 ('ding.wav', 'Динь', 'важно / уведомление / «PAMIĘTAJ»'),
 ('chime_ok.wav', 'Позитивный перезвон', 'галочка, «KORZYSTNE»'),
 ('buzz_no.wav', 'Ошибка «НЕТ»', 'красный крестик, «BRAK…»'),
 ('stamp.wav', 'Удар печати', 'печать «BRAK ZGODY»'),
 ('ka_ching.wav', 'Касса', 'суммы, деньги, результат'),
 ('coins.wav', 'Монеты', 'деньги, кредит'),
 ('counter_ticks.wav', 'Тиканье счётчика', 'цифры набегают'),
 ('whoosh_soft.wav', 'Мягкий короткий свист', 'выезд плашки/карточки'),
 ('riser_short.wav', 'Короткое нарастание', 'перед раскрытием итога'),
 ('paper_flip.wav', 'Шорох бумаги', 'карточка, документ, план'),
 ('pen_scribble.wav', 'Ручка', 'галочка рисуется, подчёркивание'),
 ('typewriter_ding.wav', 'Машинка + звонок', 'конец строки печати'),
 ('camera_shutter.wav', 'Затвор камеры', 'скриншот, «фото» документа'),
]
def load(p, start=None, dur=None):
    cmd = ['ffmpeg', '-v', 'error'] + (['-ss', str(start)] if start else []) + ['-i', p] + (['-t', str(dur)] if dur else []) + ['-ac', '1', '-ar', str(SR), '-f', 'f32le', '-']
    return np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.float32)
audio = np.zeros(int(SLOT * len(items) * SR) + SR, np.float32)
F1 = ImageFont.truetype(os.path.expanduser('~/.fonts/Montserrat-Black.ttf'), 120)
F2 = ImageFont.truetype(os.path.expanduser('~/.fonts/Montserrat-Black.ttf'), 58)
F3 = ImageFont.truetype(os.path.expanduser('~/.fonts/Montserrat-Medium.ttf'), 40)
os.makedirs('frames', exist_ok=True); lst = []
for i, (p, name, use) in enumerate(items):
    x = load(p, 2.45, 1.4) if p.endswith('typing.mp3') else load(p)
    x = x / (np.abs(x).max() + 1e-9) * 0.7
    s = int((i * SLOT + 0.35) * SR); audio[s:s + len(x)] += x[:len(audio) - s]
    im = Image.new('RGB', (720, 1280), (2, 6, 74)); d = ImageDraw.Draw(im)
    d.ellipse((260, 300, 460, 500), fill=(244, 122, 58)); d.text((360, 405), str(i + 1), font=F1, fill='white', anchor='mm')
    d.text((360, 640), name, font=F2, fill='white', anchor='mm')
    d.text((360, 730), use, font=F3, fill=(200, 205, 230), anchor='mm')
    d.text((360, 1180), 'новый' if i >= 7 else 'уже в монтаже', font=F3, fill=(244, 122, 58) if i >= 7 else (150, 160, 200), anchor='mm')
    fn = f'frames/{i:02d}.png'; im.save(fn); lst.append(f"file '{fn}'\nduration {SLOT}\n")
open('frames.txt', 'w').write(''.join(lst) + f"file 'frames/{len(items)-1:02d}.png'\n")
sf.write('catalog.wav', audio, SR)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', 'frames.txt', '-i', 'catalog.wav', '-c:v', 'libx264', '-r', '30', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-shortest', 'sound_catalog.mp4'])
print('ok', len(items))
