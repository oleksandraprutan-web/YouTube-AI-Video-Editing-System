import cv2, json, subprocess, numpy as np, sys
src = sys.argv[1]; W, H = 1080, 1920
cc = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', src, '-vf', 'fps=10,scale=540:960', '-f', 'rawvideo', '-pix_fmt', 'gray', '-'], stdout=subprocess.PIPE)
res = []; n = 0
while True:
    b = dec.stdout.read(540 * 960)
    if len(b) < 540 * 960: break
    g = np.frombuffer(b, np.uint8).reshape(960, 540)
    f = cc.detectMultiScale(g, 1.1, 6, minSize=(50, 50))
    if len(f):
        x, y, w, h = max(f, key=lambda r: r[2] * r[3])
        res.append([round(n / 10, 2), int((x + w / 2) * 2), int((y + h / 2) * 2), int(w * 2)])
    else: res.append([round(n / 10, 2), None, None, None])
    n += 1
json.dump(res, open('faces.json', 'w'))
