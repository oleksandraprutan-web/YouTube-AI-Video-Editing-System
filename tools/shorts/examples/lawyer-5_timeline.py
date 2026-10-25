# Lawyer short 5 — "opieka naprzemienna a alimenty" (47.7 s). 29.33–34.67 orange placeholder → animated scene.
SRC = 'src/video_v2.mp4'
END = 47.36
SUB_SIZE = 62
PILL_FONT = 44
FIXES = {24: 'naprzemienna', 25: 'nie'}
MERGE = [(78, 'naprzemiennej.')]

ZOOMS = [(0, 1.0), (5.16, 1.15), (5.78, 1.0)]
CUTS = [6.9, 11.27, 22.33, 25.97, 29.33, 34.67, 43.2]
DONUTS = [(0.90, 5.10, 1.56, 1.98, '50/50', 3.32, 'ALIMENTY = 0 zł ?', 300)]   # "po równo u obojga… nikt nie musi płacić?"
WARNS = [(5.16, 6.85, 'UWAŻAJ', 260)]
HEADLINES = [(7.04, 11.20, ['OBOWIĄZEK', 'ALIMENTACYJNY'], 10.64, 'NIE ZNIKA', 230)]
RESULTS = [(20.66, 22.25, 'SĄD NIE ZASĄDZA ALIMENTÓW', (46, 196, 110), 330)]
INCOMES = [(12.40, 16.60, 12.66, 0.95, 99, '', (46, 196, 110), 330),
           (23.60, 29.28, 24.58, 0.35, 26.76, 'SĄD MOŻE ZASĄDZIĆ ALIMENTY', (244, 122, 58), 330)]
SCENES = [(29.33, 34.67, {'fn': 'scene_two_homes', 'title': 'DLACZEGO?', 't_homes': 31.70, 't_equal': 33.48,
           't_verdict': 34.10, 'verdict': 'PODOBNY POZIOM'})]
SPLITS = [(36.40, 43.15, [(38.80, 'LECZENIE'), (39.46, 'SZKOŁA')], 42.04, '+ ALIMENTY WYRÓWNAWCZE', 300)]
NOTEQ = [(43.15, 47.36, (44.30, 'OPIEKA PÓŁ NA PÓŁ'), (45.34, '≠'), (46.52, 'BRAK ALIMENTÓW'), 300)]
ZBLUR = [29.33, 34.67]

SFX = [('counter_ticks.wav', 1.56, -26, 'start'), ('click-pop_04_B.wav', 3.32, -21, 'start'),
       ('hit_01_A.wav', 5.16, -17, 'start'), ('click-pop_04_B.wav', 5.20, -21, 'start'),
       ('click-pop_04_B.wav', 7.06, -21, 'start'), ('hit_01_A.wav', 10.64, -19, 'start'),
       ('counter_ticks.wav', 12.66, -25, 'start'), ('chime_ok.wav', 20.66, -24, 'start'),
       ('counter_ticks.wav', 24.58, -25, 'start'), ('click-pop_04_B.wav', 26.76, -20, 'start'),
       ('whoosh-rise_04_C.wav', 29.33, -21, 'peak'), ('click-pop_04_B.wav', 31.72, -21, 'start'),
       ('counter_ticks.wav', 33.48, -25, 'start'), ('chime_ok.wav', 34.10, -24, 'start'),
       ('whoosh-rise_04_C.wav', 34.67, -21, 'peak'),
       ('click-pop_04_B.wav', 36.42, -21, 'start'), ('counter_ticks.wav', 38.80, -26, 'start'), ('counter_ticks.wav', 39.46, -26, 'start'), ('click-pop_04_B.wav', 42.04, -20, 'start'),
       ('click-pop_01_A.wav', 44.30, -21, 'start'), ('hit_01_A.wav', 45.34, -19, 'start'), ('click-pop_01_A.wav', 46.52, -21, 'start')]
STEMS = 'sep2/htdemucs/audio_v2'
MUSIC_GAIN_DB = -80          # author: no music / background bed
SFX_GAIN_DB = -4             # author: effects a bit quieter
