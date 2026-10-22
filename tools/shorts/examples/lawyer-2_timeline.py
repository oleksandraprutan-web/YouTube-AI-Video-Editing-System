# Lawyer short 2 — "opieka naprzemienna: 4 kwestie" (50 s source, black tail after 48.07)
SRC = 'src/video.mp4'
END = 48.07
FIXES = {47: 'nauki'}
MERGE = [(9, 'naprzemiennej,'), (114, 'OZSS'), (123, 'naprzemienną,')]

ZOOMS = [(0, 1.0), (2.0, 1.15), (4.5, 1.3), (6.52, 1.55), (7.83, 1.1), (9.12, 1.25), (10.74, 1.0),
         (12.47, 1.0), (16.57, 1.0), (19.60, 1.0), (19.60, 1.0), (23.83, 1.0), (27.00, 1.25),
         (28.78, 1.12), (30.80, 1.0), (33.10, 1.05), (38.13, 1.1), (43.62, 1.2), (46.40, 1.35)]
QUOTES = [(2.38, 6.40, 'Chcę opieki naprzemiennej, bo kocham swoje dziecko')]   # she quotes what a parent says in court
XMARKS = [(6.98, 7.70, (540, 190))]                      # "Niestety to nie wystarczy"
BIGTEXT = []
HEADINGS = []
SPEC_ROWS = [('1. WARUNKI', 'mieszkaniowe'), ('2. ODLEGŁOŚĆ', 'między domami'),
             ('3. WSPÓŁPRACA', 'rodziców'), ('4. POTRZEBY', 'dziecka')]
SPECS = [(10.74, 13.60, 1), (16.48, 19.50, 2), (23.80, 26.90, 3), (30.80, 33.05, 4)]
TINT = (0, 0)
PILL_END = 37.98
PILL_Y = 920                                           # pills on the chest, head stays clear
PILLS = [(33.18, 'WIEK', 0, 0), (34.40, 'ZDROWIE', 0, 1),
         (35.12, 'RELACJE Z RODZEŃSTWEM', 1, None), (36.60, 'PRZYSTOSOWANIE DO ZMIAN', 2, None)]
CIRCLES = [(39.70, 43.55, [39.88, 41.04], 760)]          # only once: OZSS opinion
TOPTITLE = []
ZBLUR = [6.52, 12.47, 16.57, 19.60, 23.83, 38.05]        # punch + cuts to/from B-roll

SFX = [('whoosh-rise_01_A.wav', 2.38, -18, 'peak'), ('click-pop_02_A.wav', 2.45, -18, 'start'),
       ('swish_03_C.wav', 2.0, -20, 'peak'), ('swish_03_C.wav', 4.5, -20, 'peak'),
       ('hit_01_A.wav', 6.52, -12, 'start'), ('click-pop_04_B.wav', 6.98, -16, 'start'), ('click-pop_04_B.wav', 7.13, -16, 'start'),
       ('whoosh-rise_03_C.wav', 10.74, -16, 'peak'), ('click-pop_02_A.wav', 10.86, -18, 'start'),
       ('swish_01_B.wav', 12.47, -18, 'peak'), ('swish_01_B.wav', 16.57, -18, 'peak'),
       ('whoosh-rise_03_C.wav', 16.48, -16, 'peak'), ('click-pop_02_A.wav', 16.60, -18, 'start'),
       ('swish_01_B.wav', 19.60, -18, 'peak'), ('swish_01_B.wav', 23.83, -18, 'peak'),
       ('whoosh-rise_03_C.wav', 23.80, -16, 'peak'), ('click-pop_02_A.wav', 23.92, -18, 'start'),
       ('whoosh-rise_03_C.wav', 30.80, -16, 'peak'), ('click-pop_02_A.wav', 30.92, -18, 'start'),
       
       ('click-pop_05_C.wav', 33.18, -16, 'start'), ('click-pop_05_C.wav', 34.40, -16, 'start'),
       ('click-pop_05_C.wav', 35.12, -16, 'start'), ('click-pop_05_C.wav', 36.60, -16, 'start'),
       ('swish_01_B.wav', 38.05, -18, 'peak'),
       ('whoosh-rise_03_C.wav', 39.70, -16, 'peak'), ('whoosh-rise_04_C.wav', 43.55, -17, 'peak'),
]
