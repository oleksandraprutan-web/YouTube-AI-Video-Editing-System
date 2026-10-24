# Lawyer short 4 — "rozwód z manipulatorem: dowody" (52.6 s). 17.6–26.33 in source is a blue placeholder → evidence animation.
SRC = 'src/video.mp4'
SUB_SIZE = 62

ZOOMS = [(0, 1.0), (6.18, 1.18), (6.94, 1.0), (15.70, 1.08), (16.60, 1.0)]
CUTS = [6.13, 10.63, 17.6, 26.33, 32.67, 36.7, 47.43]
PILL_GROUPS = [(6.10, [960, 1100, 1240], [(1.78, 'MANIPULACJE', 0, None), (2.72, 'PROWOKACJE', 1, None), (4.30, 'DZIECI W SPORACH', 2, None)]),
               (52.60, [1030, 1180], [(50.28, 'FAKTY', 0, 0), (51.06, 'DOWODY', 0, 1), (51.76, 'DOBRO DZIECKA', 1, None)])]
BADGES = [(6.18, 9.00, 'UWAŻAJ', 170), (38.44, 42.40, 'PILNA SPRAWA', 170)]
QUOTES = [(14.38, 16.55, 'Drugi rodzic jest narcyzem', 1120)]
XMARKS = [(15.70, 16.55, (965, 1020))]
SCENES = [(17.60, 26.33, {'fn': 'scene_evidence', 'title': 'ZBIERAJ DOWODY',
           'bubbles': [(17.70, 'L'), (17.95, 'R'), (18.20, 'L'), (18.45, 'R')],
           't_shot': 19.26, 'shot_label': 'ZRZUT EKRANU',
           't_list': 20.90, 'list_title': 'DOKUMENTUJ',
           'items': [(22.64, 'KONTAKTY\nZ DZIECKIEM'), (24.44, 'LECZENIE'), (25.34, 'WAŻNE\nDECYZJE')]})]
SPECS_Y = 1000
SPEC_ROWS = [('NIE ODPOWIADAJ', 'na prowokacje'), ('KONTAKT', 'tylko o dziecku'), ('DZIECKO', 'to nie pośrednik')]
SPECS = [(26.40, 28.55, 1), (28.60, 32.65, 2), (32.72, 36.65, 3)]
CIRCLES = [(42.40, 47.40, [42.56, 44.16, 45.74], 760)]                 # "możesz wystąpić do sądu z wnioskiem o zabezpieczenie…"
ZBLUR = [6.18, 17.60, 26.33]

SFX = [('click-pop_05_C.wav', 1.78, -21, 'start'), ('click-pop_05_C.wav', 2.72, -21, 'start'), ('click-pop_05_C.wav', 4.30, -21, 'start'),
       ('hit_01_A.wav', 6.18, -17, 'start'), ('click-pop_04_B.wav', 6.22, -21, 'start'),
       ('click-pop_04_B.wav', 14.40, -21, 'start'), ('buzz_no.wav', 15.70, -26, 'start'), ('pen_scribble.wav', 15.72, -28, 'start'),
       ('whoosh-rise_04_C.wav', 17.60, -21, 'peak'),
       *[('click-pop_01_A.wav', b, -22, 'start') for b in (17.70, 17.95, 18.20, 18.45)],
       ('click-pop_04_B.wav', 19.26, -19, 'start'), ('click-pop_04_B.wav', 20.92, -21, 'start'),
       ('pen_scribble.wav', 22.64, -28, 'start'), ('pen_scribble.wav', 24.44, -28, 'start'), ('pen_scribble.wav', 25.34, -28, 'start'),
       ('chime_ok.wav', 25.50, -24, 'start'),
       ('whoosh-rise_04_C.wav', 26.33, -21, 'peak'),
       ('click-pop_04_B.wav', 26.42, -21, 'start'), ('click-pop_04_B.wav', 28.62, -21, 'start'), ('click-pop_04_B.wav', 32.74, -21, 'start'),
       ('click-pop_04_B.wav', 38.46, -21, 'start'),
       ('whoosh-rise_04_C.wav', 42.40, -21, 'peak'), ('whoosh-rise_04_C.wav', 47.40, -21, 'peak'),
       ('click-pop_05_C.wav', 50.28, -21, 'start'), ('click-pop_05_C.wav', 51.06, -21, 'start'), ('click-pop_05_C.wav', 51.76, -21, 'start')]
