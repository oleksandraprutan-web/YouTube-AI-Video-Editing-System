"""Person matte with MODNet (Apache-2.0, Xenova/modnet ONNX). Writes mattes/<frame>.png (L, 1080x1920) for frames in [t0, t1)."""
import sys, os, subprocess, numpy as np, onnxruntime as ort
from PIL import Image
MODEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../.local/models/modnet/model.onnx')
src, t0, t1 = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
W, H, FPS = 1080, 1920, 30
os.makedirs('mattes', exist_ok=True)
sess = ort.InferenceSession(MODEL, providers=['CPUExecutionProvider'])
inp = sess.get_inputs()[0].name
dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', str(t0), '-i', src, '-t', str(t1 - t0), '-r', str(FPS), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
n0 = int(round(t0 * FPS)); i = 0
while True:
    raw = dec.stdout.read(W * H * 3)
    if len(raw) < W * H * 3: break
    im = Image.frombytes('RGB', (W, H), raw).resize((288, 512), Image.BILINEAR)
    x = (np.asarray(im, np.float32) / 255 - 0.5) / 0.5
    m = sess.run(None, {inp: x.transpose(2, 0, 1)[None]})[0][0, 0]
    Image.fromarray((np.clip(m, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR).save(f'mattes/{n0 + i:05d}.png')
    i += 1
print('mattes', i)
