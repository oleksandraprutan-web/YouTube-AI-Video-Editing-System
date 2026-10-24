import numpy as np, soundfile as sf
SR = 48000
rng = np.random.default_rng(3)
def t(d): return np.arange(int(d * SR)) / SR
def env(x, a=0.002, r=0.2):
    n = len(x); e = np.ones(n); na = max(1, int(a * SR)); e[:na] = np.linspace(0, 1, na)
    e *= np.exp(-np.arange(n) / SR / r); return x * e
def norm(x, p=0.8): return x / (np.abs(x).max() + 1e-9) * p
def bp_noise(d, lo, hi):
    n = rng.standard_normal(int(d * SR)); F = np.fft.rfft(n); f = np.fft.rfftfreq(len(n), 1 / SR)
    F[(f < lo) | (f > hi)] = 0; return np.fft.irfft(F, len(n))
S = {}
tt = t(0.18); S['pop'] = env(np.sin(2 * np.pi * (900 - 2500 * tt) * tt), 0.001, 0.04)
S['tap'] = env(bp_noise(0.05, 2000, 6000), 0.0005, 0.008) + env(np.sin(2 * np.pi * 1800 * t(0.05)), 0.0005, 0.01) * 0.5
tt = t(1.2); S['ding'] = env(sum(np.sin(2 * np.pi * f * tt) * g for f, g in [(1760, 1), (3520, .4), (5280, .15)]), 0.001, 0.35)
a = env(np.sin(2 * np.pi * 1318.5 * t(0.9)) + .3 * np.sin(2 * np.pi * 2637 * t(0.9)), 0.002, 0.25)
b = env(np.sin(2 * np.pi * 1661 * t(0.9)) + .3 * np.sin(2 * np.pi * 3322 * t(0.9)), 0.002, 0.3)
S['chime_ok'] = np.concatenate([a[:int(.11 * SR)], b])
sq = lambda f, d: np.sign(np.sin(2 * np.pi * f * t(d)))
S['buzz_no'] = np.concatenate([env(sq(140, .16), .002, .2) * np.hanning(int(.16 * SR)), np.zeros(int(.06 * SR)), env(sq(110, .22), .002, .2) * np.hanning(int(.22 * SR))]) * 0.6
tt = t(0.45); S['stamp'] = env(np.sin(2 * np.pi * (120 - 60 * tt) * tt), 0.001, 0.09) + env(bp_noise(0.45, 200, 3000), 0.0005, 0.03) * 0.6
def metal(f0, d, r):
    tt = t(d); return env(sum(np.sin(2 * np.pi * f0 * k * tt) / k for k in (1, 2.76, 5.4, 8.9)), 0.0005, r)
kc = np.zeros(int(1.3 * SR)); kc[:int(.05 * SR)] += env(bp_noise(.05, 1000, 8000), .0005, .015)
x = metal(2400, 1.1, .3); kc[int(.12 * SR):int(.12 * SR) + len(x)] += x * .9; S['ka_ching'] = kc
cn = np.zeros(int(1.0 * SR))
for i, (dt, f) in enumerate([(0, 3200), (.12, 3500), (.21, 3100), (.27, 3600), (.31, 3300)]):
    x = metal(f, .5, .12) * (0.9 - i * .12); s = int(dt * SR); cn[s:s + len(x)] += x[:len(cn) - s]
S['coins'] = cn
tk = np.zeros(int(1.2 * SR))
for i in range(18):
    s = int(i * 1.2 / 18 * SR); x = env(bp_noise(.02, 3000, 9000), .0003, .004); tk[s:s + len(x)] += x
S['counter_ticks'] = tk
n = bp_noise(0.5, 300, 4000); w = np.sin(np.linspace(0, np.pi, len(n))) ** 2; S['whoosh_soft'] = n * w
n = bp_noise(0.9, 200, 6000); w = np.linspace(0, 1, len(n)) ** 2.5; w[-int(.03 * SR):] *= np.linspace(1, 0, int(.03 * SR)); S['riser_short'] = n * w
pf = np.zeros(int(.5 * SR))
for s0, d in [(0, .12), (.1, .18)]:
    x = bp_noise(d, 1500, 7000) * np.hanning(int(d * SR)); s = int(s0 * SR); pf[s:s + len(x)] += x
S['paper_flip'] = pf
n = bp_noise(0.7, 2500, 8000); m = (np.sin(2 * np.pi * 9 * t(0.7)) > 0) * 0.8 + 0.2; S['pen_scribble'] = n * m * np.hanning(len(n)) * 0.7
tw = np.zeros(int(1.0 * SR)); x = env(bp_noise(.03, 800, 5000), .0003, .01); tw[:len(x)] += x
y = env(np.sin(2 * np.pi * 2093 * t(.8)) + .4 * np.sin(2 * np.pi * 4186 * t(.8)), .001, .25); tw[int(.08 * SR):int(.08 * SR) + len(y)] += y * .8; S['typewriter_ding'] = tw
sh = np.zeros(int(.35 * SR)); a = env(bp_noise(.05, 1500, 9000), .0005, .012); sh[:len(a)] += a; sh[int(.09 * SR):int(.09 * SR) + len(a)] += a * .8; S['camera_shutter'] = sh
for k, v in S.items(): sf.write(f'{k}.wav', norm(v).astype(np.float32), SR)
print(list(S))
