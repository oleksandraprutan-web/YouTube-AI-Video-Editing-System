# Lawyer short 5 — "opieka naprzemienna a alimenty" (47.7 s). 29.33–34.67 orange placeholder → animated scene.
SRC = 'src/video.mp4'
END = 47.36
SUB_SIZE = 62
PILL_FONT = 44
FIXES = {24: 'naprzemienna', 25: 'nie'}
MERGE = [(78, 'naprzemiennej.')]

ZOOMS = [(0, 1.0), (5.16, 1.15), (5.78, 1.0)]
CUTS = [6.9, 11.27, 22.33, 25.97, 29.33, 34.67, 43.2]
CALENDARS = [(0.90, 3.25, 'U MAMY', 1.56, 'U TATY', 1.98)]                 # "mieszka po równo u obojga rodziców"
QUOTES = [(3.30, 5.10, 'Nikt nie musi płacić alimentów?')]
BADGES = [(5.16, 6.85, 'UWAŻAJ', 200)]
STRIKES = [(8.40, 11.20, 'ALIMENTY ZNIKAJĄ', 10.64, (540, 300))]          # "nie oznacza automatycznie, że obowiązek … znika"
INCOMES = [(12.40, 22.25, 12.66, 0.95, 20.66, 'SĄD NIE ZASĄDZA ALIMENTÓW', (46, 196, 110), 330),
           (23.60, 29.28, 24.58, 0.35, 26.76, 'SĄD MOŻE ZASĄDZIĆ ALIMENTY', (244, 122, 58), 330)]
SCENES = [(29.33, 34.67, {'fn': 'scene_two_homes', 'title': 'DLACZEGO?', 't_homes': 31.70, 't_equal': 33.48,
           't_verdict': 34.10, 'verdict': 'PODOBNY POZIOM'})]
PILL_GROUPS = [(43.15, [100, 200], [(38.80, 'LECZENIE', 0, 0), (39.46, 'SZKOŁA', 0, 1), (42.04, '+ ALIMENTY WYRÓWNAWCZE', 1, None)])]
CIRCLES = [(43.15, 47.36, [43.22, 44.30], 760)]                          # "opieka pół na pół nie zawsze oznacza brak alimentów"
ZBLUR = [29.33, 34.67]

SFX = [('click-pop_04_B.wav', 1.56, -21, 'start'), ('click-pop_04_B.wav', 1.98, -21, 'start'),
       ('click-pop_04_B.wav', 3.32, -21, 'start'),
       ('hit_01_A.wav', 5.16, -17, 'start'), ('click-pop_04_B.wav', 5.20, -21, 'start'),
       ('click-pop_04_B.wav', 8.42, -21, 'start'), ('pen_scribble.wav', 10.64, -27, 'start'), ('buzz_no.wav', 10.84, -27, 'start'),
       ('counter_ticks.wav', 12.66, -25, 'start'), ('chime_ok.wav', 20.66, -24, 'start'),
       ('counter_ticks.wav', 24.58, -25, 'start'), ('click-pop_04_B.wav', 26.76, -20, 'start'),
       ('whoosh-rise_04_C.wav', 29.33, -21, 'peak'), ('click-pop_04_B.wav', 31.72, -21, 'start'),
       ('counter_ticks.wav', 33.48, -25, 'start'), ('chime_ok.wav', 34.10, -24, 'start'),
       ('whoosh-rise_04_C.wav', 34.67, -21, 'peak'),
       ('click-pop_05_C.wav', 38.80, -21, 'start'), ('click-pop_05_C.wav', 39.46, -21, 'start'), ('click-pop_05_C.wav', 42.04, -21, 'start'),
       ('whoosh-rise_04_C.wav', 43.15, -21, 'peak')]
