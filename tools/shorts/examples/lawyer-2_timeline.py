# Lawyer short 2 — "opieka naprzemienna: 4 kwestie" (50 s source, black tail after 48.07)
SRC = 'src/video_hq.mp4'   # author: second-to-last version
END = 48.65
FIXES = {47: 'nauki'}
MERGE = [(9, 'naprzemiennej,'), (114, 'OZSS'), (123, 'naprzemienną,')]

ZOOMS = [(0, 1.0), (4.5, 1.1), (6.52, 1.35), (7.83, 1.0), (27.0, 1.12), (30.80, 1.0), (43.62, 1.1)]   # fewer zooms (author)
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
BLURS = [(0.0, 2.05, (690, 230, 1030, 960), (725, 230, 1040, 960))]   # hide folder labels on the shelf
BROLL = [(12.47, 16.57), (19.60, 23.83)]               # author's cutaways: keep still
CUTS = [7.78, 12.47, 16.57, 19.60, 23.83, 38.07]
ZBLUR = [6.52, 12.47, 16.57, 19.60, 23.83, 38.05]        # punch + cuts to/from B-roll

SFX = [('whoosh-rise_01_A.wav', 2.38, -18, 'peak'), ('click-pop_01_A.wav', 2.45, -18, 'start'),

       ('hit_01_A.wav', 6.52, -12, 'start'), ('click-pop_04_B.wav', 6.98, -16, 'start'), ('click-pop_04_B.wav', 7.13, -16, 'start'),
       ('click-pop_04_B.wav', 10.76, -17, 'start'),
       
       ('click-pop_04_B.wav', 16.50, -17, 'start'),
       
       ('click-pop_04_B.wav', 23.82, -17, 'start'),
       ('click-pop_04_B.wav', 30.82, -17, 'start'),
       
       ('click-pop_05_C.wav', 33.18, -16, 'start'), ('click-pop_05_C.wav', 34.40, -16, 'start'),
       ('click-pop_05_C.wav', 35.12, -16, 'start'), ('click-pop_05_C.wav', 36.60, -16, 'start'),

       ('whoosh-rise_04_C.wav', 39.70, -17, 'peak'), ('whoosh-rise_04_C.wav', 43.55, -17, 'peak'),
]
BLUR_STYLE = 'soft'   # author chose A
