# Lawyer short 7 — "odrzucenie spadku a dzieci" (45.5 s). New animated set + new SFX palette.
SRC = 'src/video.mp4'
SUB_SIZE = 62
STEMS = 'sep/htdemucs/audio'
MUSIC_GAIN_DB = -80
SFX_GAIN_DB = -4

ZOOMS = [(0, 1.0), (6.14, 1.12), (6.82, 1.0)]
CUTS = [6.1, 7.37, 13.63, 16.7, 23.17, 26.13, 33.47, 40.83]
DEBTS = [(0.30, 2.70, 'ZOSTAWIŁ PO SOBIE', 120000, 1.04, 290)]                        # "zostawił po sobie same długi"
DISSOLVES = [(3.50, 7.30, 'PROBLEM', 5.26, 6.14, 290)]                             # "problem zniknie?" … "Niestety nie zawsze" → wraca
RINGS = [(9.10, 13.60, 6, '6', 'MIESIĘCY', 9.32, 230, 110)]                              # "6 miesięcy od dnia…"
FLIPS = [(14.50, 16.65, [(15.24, 'SĄD', 'gavel'), (15.84, 'NOTARIUSZ', 'seal')], 1160)]
TILES = [(18.40, 23.10, [('MAJĄTEK', 18.72, 'x', 'NIE PRZEJMIESZ'), ('DŁUGI', 20.20, 'ok', 'NIE ODPOWIADASZ')], 300)]
PULSES = [(23.40, 26.05, 'WIELE OSÓB ZAPOMINA', 230)]
FAMILY = [(26.13, 33.40, 27.80, 29.34, 'KOLEJNI SPADKOBIERCY', 31.98, 220, 0.72)]
HEADLINES = [(34.40, 40.75, ['MAŁOLETNIE', 'DZIECI'], 38.64, 'SĄD RODZINNY', 270, 0.72)]
FOLLOW = [(43.40, 45.53, 44.02, 300)]
ZBLUR = [6.14]

SFX = [('swoosh_down.wav', 0.30, -22, 'peak'), ('tick_soft.wav', 1.10, -24, 'start'), ('tick_soft.wav', 1.40, -24, 'start'), ('tick_soft.wav', 1.70, -24, 'start'), ('thud.wav', 2.10, -18, 'start'),
       ('pop_soft.wav', 3.50, -22, 'start'), ('dissolve.wav', 5.26, -24, 'start'),
       ('snap.wav', 6.14, -20, 'start'), ('thud.wav', 6.16, -20, 'start'),
       ('glass.wav', 9.32, -24, 'start'), *[('tick_soft.wav', 9.32 + 0.37 * i, -25, 'start') for i in range(6)],
       ('swoosh_up.wav', 15.10, -24, 'peak'), ('marimba.wav', 15.24, -22, 'start'), ('marimba_hi.wav', 15.84, -22, 'start'),
       ('bubble.wav', 18.72, -22, 'start'), ('notify.wav', 20.20, -24, 'start'),
       ('blip.wav', 23.40, -22, 'start'),
       ('pop_soft.wav', 26.15, -22, 'start'), ('snap.wav', 27.80, -20, 'start'), ('swoosh_up.wav', 29.30, -24, 'peak'), ('sparkle.wav', 29.40, -25, 'start'), ('marimba_hi.wav', 31.98, -23, 'start'),
       ('pop_soft.wav', 34.42, -22, 'start'), ('thud.wav', 38.64, -18, 'start'),
       ('swoosh_up.wav', 43.40, -24, 'peak'), ('snap.wav', 44.02, -20, 'start'), ('sparkle.wav', 44.06, -25, 'start')]
