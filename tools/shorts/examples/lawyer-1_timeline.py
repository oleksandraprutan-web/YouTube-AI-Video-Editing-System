# Lawyer short 1 — "opieka naprzemienna bez zgody matki" (41.9 s), infographic version
SRC = 'src/video.mp4'

ZOOMS = [(0, 1.0), (3.84, 1.1), (5.5, 1.0), (8.74, 1.3), (9.54, 1.0), (19.08, 1.08), (22.74, 1.0), (30.72, 1.1), (39.06, 1.0)]
CALENDARS = [(1.10, 5.45, 'U CIEBIE', 1.30, 'Z MATKĄ', 2.26)]          # "tydzień u Ciebie, a tydzień z matką"
STAMPS = [(3.84, 5.45, 'BRAK ZGODY', (540, 245))]                     # "kategorycznie się na to nie zgadza"
CHECKS = [(8.74, 9.50, (540, 210), 100)]                              # "Otóż nie." — you DO have a chance
CIRCLES = [(11.50, 16.62, [11.66, 13.80, 14.94], 720)]               # "brak zgody matki nie przekreśla…"
BADGES = [(16.76, 19.00, 'BARDZO WAŻNY WARUNEK', 230)]                # "Ale jest jeden bardzo ważny warunek"
LINKS = [(19.08, 22.70, 'TY', 'MATKA', 'WSPÓŁPRACA', 19.62, 21.22, 260)]  # "czy potraficie ze sobą współpracować"
PILL_Y = 920
PILL_END = 30.62
PILLS = [(25.42, 'LECZENIE', 0, 0), (26.44, 'SZKOŁA', 0, 1),
         (27.42, 'ZAJĘCIA POZALEKCYJNE', 1, None), (29.26, 'CODZIENNA OPIEKA', 2, None)]
PLANS = [{'t0': 33.40, 't1': 38.98, 'title': 'PLAN WYCHOWAWCZY', 'title_t': 34.22, 'cy': 1290,
          'items': [(35.92, 'LECZENIE'), (36.40, 'SZKOŁA'), (36.94, 'ZAJĘCIA POZALEKCYJNE'), (37.66, 'CODZIENNA OPIEKA')]}]
ARROWS = [(39.35, 41.89, (540, 1215))]
ZBLUR = [8.74]

SFX = [('click-pop_04_B.wav', 1.30, -17, 'start'), ('click-pop_04_B.wav', 2.26, -17, 'start'),
       ('hit_01_A.wav', 3.84, -12, 'start'),
       ('hit_01_A.wav', 8.74, -13, 'start'), ('click-pop_01_A.wav', 8.86, -16, 'start'),
       ('whoosh-rise_04_C.wav', 11.50, -17, 'peak'), ('whoosh-rise_04_C.wav', 16.62, -17, 'peak'),
       ('click-pop_04_B.wav', 16.78, -17, 'start'),
       ('click-pop_04_B.wav', 19.10, -18, 'start'), ('click-pop_04_B.wav', 19.25, -18, 'start'), ('click-pop_04_B.wav', 21.22, -17, 'start'),
       ('click-pop_05_C.wav', 25.42, -16, 'start'), ('click-pop_05_C.wav', 26.44, -16, 'start'),
       ('click-pop_05_C.wav', 27.42, -16, 'start'), ('click-pop_05_C.wav', 29.26, -16, 'start'),
       ('whoosh-rise_04_C.wav', 33.40, -17, 'peak'), ('click-pop_04_B.wav', 34.22, -17, 'start'),
       ('click-pop_01_A.wav', 35.92, -16, 'start'), ('click-pop_01_A.wav', 36.40, -16, 'start'),
       ('click-pop_01_A.wav', 36.94, -16, 'start'), ('click-pop_01_A.wav', 37.66, -16, 'start'),
       ('whoosh-rise_04_C.wav', 38.98, -17, 'peak'),
       ('click-pop_04_B.wav', 39.35, -17, 'start')]
