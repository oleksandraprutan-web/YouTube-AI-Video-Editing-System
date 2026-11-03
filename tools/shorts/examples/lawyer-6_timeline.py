# Lawyer short 6 — "najemca nie płaci: nie wyrzucaj sam" (42.4 s). 17.57–29.77 blue placeholder → steps animation.
SRC = 'src/video.mp4'
SUB_SIZE = 62
PILL_FONT = 44
STEMS = 'sep/htdemucs/audio'
MUSIC_GAIN_DB = -80
SFX_GAIN_DB = -4

ZOOMS = [(0, 1.0), (8.06, 1.12), (8.76, 1.0)]
CUTS = [9.37, 17.57, 29.77, 37.27]
PILL_GROUPS = [(5.20, [110, 210], [(2.38, 'NIE PŁACI CZYNSZU', 0, None), (3.88, 'NIE CHCE SIĘ WYPROWADZIĆ', 1, None)])]
QUOTES = [(5.26, 7.98, 'Zmienić zamki i wyrzucić jego rzeczy?')]
WARNS = [(8.06, 9.30, 'TO NIE TAKIE PROSTE', 250)]
HEADLINES = [(9.40, 13.75, ['EKSMISJA', 'NA WŁASNĄ RĘKĘ'], 11.32, 'NIE WOLNO', 230)]
RESULTS = [(15.86, 17.52, 'ODPOWIEDZIALNOŚĆ PRAWNA', (225, 25, 30), 300)]
SCENES = [(17.57, 29.77, {'fn': 'scene_rent_steps', 'title': 'CO MOŻESZ ZROBIĆ?', 't_months': 19.58,
           'months_label': 'MIN. 3 OKRESY ZALEGŁOŚCI', 't_x': [21.26, 21.56, 22.00],
           'steps': [(24.14, 1, 'PISEMNE\nUPRZEDZENIE', 'envelope'), (27.82, 2, 'DODATKOWY TERMIN\nNA ZAPŁATĘ', 'clock')]})]
SPECS_Y = 110
SPEC_ROWS = [('3. WYPOWIEDZENIE', 'umowy'), ('4. POZEW', 'o eksmisję do sądu')]
SPECS = [(31.50, 34.30, 1), (34.34, 37.22, 2)]
STRIKES = [(37.30, 42.35, 'NA WŁASNĄ RĘKĘ', 41.64, (540, 300))]
ZBLUR = [17.57, 29.77]

SFX = [('click-pop_05_C.wav', 2.38, -21, 'start'), ('click-pop_05_C.wav', 3.88, -21, 'start'),
       ('click-pop_04_B.wav', 5.28, -21, 'start'),
       ('hit_01_A.wav', 8.06, -17, 'start'),
       ('click-pop_04_B.wav', 9.42, -21, 'start'), ('hit_01_A.wav', 11.32, -19, 'start'),
       ('buzz_no.wav', 15.86, -26, 'start'),
       ('whoosh-rise_04_C.wav', 17.57, -21, 'peak'), ('click-pop_04_B.wav', 19.60, -21, 'start'),
       ('pen_scribble.wav', 21.26, -28, 'start'), ('pen_scribble.wav', 21.56, -28, 'start'), ('pen_scribble.wav', 22.00, -28, 'start'),
       ('click-pop_04_B.wav', 24.16, -21, 'start'), ('counter_ticks.wav', 27.84, -25, 'start'),
       ('whoosh-rise_04_C.wav', 29.77, -21, 'peak'),
       ('click-pop_04_B.wav', 31.52, -21, 'start'), ('click-pop_04_B.wav', 34.36, -21, 'start'),
       ('click-pop_04_B.wav', 37.32, -21, 'start'), ('pen_scribble.wav', 41.64, -27, 'start'), ('buzz_no.wav', 41.84, -27, 'start')]
