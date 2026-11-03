import numpy as np, soundfile as sf
SR = 48000; rng = np.random.default_rng(11)
def t(d): return np.arange(int(d * SR)) / SR
def env(x, a=0.002, r=0.2):
    n = len(x); e = np.ones(n); na = max(1, int(a * SR)); e[:na] = np.linspace(0, 1, na); e *= np.exp(-np.arange(n) / SR / r); return x * e
def norm(x, p=0.8): return x / (np.abs(x).max() + 1e-9) * p
def bp(d, lo, hi):
    n = rng.standard_normal(int(d * SR)); F = np.fft.rfft(n); f = np.fft.rfftfreq(len(n), 1 / SR); F[(f < lo) | (f > hi)] = 0; return np.fft.irfft(F, len(n))
def sweep_noise(d, f0, f1):
    n = rng.standard_normal(int(d * SR)); out = np.zeros_like(n); y = 0
    fc = np.geomspace(f0, f1, len(n)); a = 1 - np.exp(-2 * np.pi * fc / SR)
    for i in range(len(n)): y += a[i] * (n[i] - y); out[i] = y
    return out - np.convolve(out, np.ones(64) / 64, 'same')
S = {}
tt = t(0.12); S['blip'] = env(np.sin(2 * np.pi * (600 + 1800 * tt / 0.12) * tt), 0.002, 0.05)
tt = t(0.16); S['bubble'] = env(np.sin(2 * np.pi * (300 * np.exp(tt * 14)) * tt * 0.6), 0.001, 0.05)
tt = t(0.9); S['glass'] = env(np.sin(2 * np.pi * 2637 * tt) + .5 * np.sin(2 * np.pi * 3951 * tt) + .2 * np.sin(2 * np.pi * 6272 * tt), 0.0005, 0.22)
tt = t(0.8); S['marimba'] = env(np.sin(2 * np.pi * 523 * tt) + .35 * np.sin(2 * np.pi * 523 * 4 * tt) * np.exp(-tt * 30), 0.001, 0.18)
tt = t(0.8); S['marimba_hi'] = env(np.sin(2 * np.pi * 784 * tt) + .35 * np.sin(2 * np.pi * 784 * 4 * tt) * np.exp(-tt * 30), 0.001, 0.16)
x = sweep_noise(0.45, 300, 5000); S['swoosh_up'] = x * np.sin(np.linspace(0, np.pi, len(x))) ** 1.5
x = sweep_noise(0.45, 5000, 300); S['swoosh_down'] = x * np.sin(np.linspace(0, np.pi, len(x))) ** 1.5
tt = t(0.4); S['thud'] = env(np.sin(2 * np.pi * (90 - 40 * tt) * tt), 0.002, 0.08) + env(bp(0.4, 60, 400), 0.001, 0.03) * .4
sp = np.zeros(int(1.0 * SR))
for i, f in enumerate([3136, 3951, 4699, 5274, 6272]):
    s = int(i * 0.07 * SR); x = env(np.sin(2 * np.pi * f * t(0.5)), 0.0005, 0.09); sp[s:s + len(x)] += x * (1 - i * .12)
S['sparkle'] = sp
S['tick_soft'] = env(bp(0.04, 1500, 4000), 0.0003, 0.006)
a = env(np.sin(2 * np.pi * 880 * t(0.5)), .002, .12); b = env(np.sin(2 * np.pi * 1318.5 * t(0.7)), .002, .18)
nt = np.zeros(int(0.9 * SR)); nt[:len(a)] += a; nt[int(.12 * SR):int(.12 * SR) + len(b)] += b; S['notify'] = nt
S['snap'] = env(bp(0.08, 1800, 9000), 0.0003, 0.012) + env(np.sin(2 * np.pi * 1200 * t(0.08)), 0.0003, 0.01) * .5
tt = t(0.25); S['pop_soft'] = env(np.sin(2 * np.pi * (500 + 700 * tt / .25) * tt), 0.003, 0.05) * np.hanning(len(tt)) ** .3
dis = np.zeros(int(1.0 * SR))
for i in range(40):
    s = int(rng.uniform(0, .7) * SR); x = env(bp(.03, 3000, 10000), .0003, .008) * rng.uniform(.3, 1); dis[s:s + len(x)] += x
S['dissolve'] = dis * np.linspace(1, .2, len(dis))
for k, v in S.items(): sf.write(f'{k}.wav', norm(v).astype(np.float32), SR)
print(list(S))
