# Lawyer short 8 — "dziecko się usamodzielniło, przestałeś płacić alimenty" (48.3 s). 10.0–19.2 orange placeholder → milestones animation.
SRC = 'src/video.mp4'
SUB_SIZE = 62
STEMS = 'sep/htdemucs/audio'
MUSIC_GAIN_DB = -80
SFX_GAIN_DB = -4

ZOOMS = [(0, 1.0), (4.80, 1.12), (5.60, 1.0)]
CUTS = [7.97, 10.0, 19.2, 26.73]
TOGGLES = [(0.70, 4.70, 'PRZELEW: ALIMENTY', ('AKTYWNY', 'ZATRZYMANY'), 3.56, 260)]     # "przestałeś płacić alimenty"
PULSES = [(4.80, 7.15, 'UWAŻAJ', 230)]
RESULTS = [(7.24, 7.95, 'MOŻE CIĘ SŁONO KOSZTOWAĆ', (225, 25, 30), 300)]
PEOPLE = [(8.02, 9.95, 5, 8.70, 'TEN SAM BŁĄD', 290)]
SCENES = [(10.00, 19.20, {'fn': 'scene_milestones', 'title': 'DZIECKO:',
           'items': [(11.46, 'SKOŃCZYŁO SZKOŁĘ'), (12.74, 'PODJĘŁO PRACĘ'), (14.78, 'UTRZYMUJE SIĘ')],
           't_transfer': 16.20, 't_stop': 17.46, 't_q': 18.14, 'q': 'KONIEC ALIMENTÓW?'})]
HEADLINES = [(19.28, 26.70, ['ZASĄDZONE', 'PRZEZ SĄD'], 22.92, 'TYLKO SĄD', 230, 0.8)]
DEBTS = [(27.32, 31.70, 'ZADŁUŻENIE ALIMENTACYJNE', 24000, 28.78, 290)]
RESULTS += [(31.82, 34.15, 'POSTĘPOWANIE EGZEKUCYJNE', (225, 25, 30), 300), (39.62, 41.25, 'BEZPIECZNE ROZWIĄZANIE', (46, 196, 110), 300)]
DOCS = [(41.32, 45.40, [(41.32, 'POZEW DO SĄDU'), (43.32, 'O UCHYLENIE'), (43.96, 'obowiązku alimentacyjnego')], 1290)]
FOLLOW = [(46.40, 48.25, 47.14, 300)]
ZBLUR = [10.0, 19.2]

SFX = [('pop_soft.wav', 0.72, -22, 'start'), ('snap.wav', 3.56, -20, 'start'),
       ('blip.wav', 4.80, -22, 'start'), ('thud.wav', 7.24, -18, 'start'),
       *[('tick_soft.wav', 8.70 + 0.12 * i, -24, 'start') for i in range(5)],
       ('swoosh_up.wav', 10.00, -24, 'peak'), ('pop_soft.wav', 10.05, -22, 'start'),
       ('marimba.wav', 11.46, -22, 'start'), ('marimba.wav', 12.74, -22, 'start'), ('marimba_hi.wav', 14.78, -22, 'start'),
       ('bubble.wav', 16.20, -22, 'start'), ('thud.wav', 17.46, -18, 'start'), ('glass.wav', 18.14, -24, 'start'),
       ('swoosh_down.wav', 19.20, -24, 'peak'),
       ('pop_soft.wav', 19.30, -22, 'start'), ('thud.wav', 22.92, -18, 'start'),
       ('pop_soft.wav', 27.34, -22, 'start'), *[('tick_soft.wav', 28.78 + 0.1 * i, -25, 'start') for i in range(11)],
       ('thud.wav', 31.82, -18, 'start'),
       ('notify.wav', 39.62, -24, 'start'), ('pop_soft.wav', 41.34, -22, 'start'), ('blip.wav', 43.32, -22, 'start'), ('blip.wav', 43.96, -22, 'start'),
       ('swoosh_up.wav', 46.40, -24, 'peak'), ('snap.wav', 47.14, -20, 'start'), ('sparkle.wav', 47.18, -25, 'start')]
