# Lawyer short 3 — "spadek z dobrodziejstwem inwentarza" (49.6 s). 24.3–36.77 in source is a blue placeholder → animated example.
SRC = 'src/video_v3.mp4'

ZOOMS = [(0, 1.0), (4.56, 1.06), (9.04, 1.22), (9.74, 1.0), (17.54, 1.1), (18.98, 1.0), (36.77, 1.0), (43.04, 1.08), (46.70, 1.0)]
CUTS = [10.8, 24.3, 36.77, 43.0]
MONTHS = [(0.0, 2.95, 6, '6 MIESIĘCY', 0.42, 300)]                                   # "Minęło 6 miesięcy"
QUOTES = [(4.56, 8.95, 'Będziesz musiał spłacić jej kredyty z własnych środków?'),     # the viewer's fear
          (46.70, 49.64, 'Nie oznacza automatycznego umorzenia kredytu')]
CHECKS = [(9.04, 10.75, (540, 260), 100)]                                            # "Spokojnie, to tak nie działa"
CIRCLES = [(10.80, 16.95, [10.88, 12.20, 14.26, 15.82], 760)]                       # the legal rule, typed
CAPS = [(18.98, 24.25, 19.44, 21.48, 300)]                                           # "odpowiedzialność … ograniczona do wartości aktywów"
SCENES = [(24.30, 36.77, {'fn': 'scene_inheritance', 'title': 'PRZYKŁAD', 't_title': 24.35,
           'asset_label': 'MIESZKANIE', 't_asset': 26.76, 't_asset_num': 27.48, 'asset': 420000,
           'debt_label': 'KREDYT', 't_debt': 29.76, 't_debt_num': 30.78, 'debt': 55000,
           't_eq': 32.82, 't_verdict': 35.84, 'verdict': 'KORZYSTNE'})]
BADGES = [(40.86, 42.95, 'BRAK MAJĄTKU, TYLKO DŁUGI', 260), (43.14, 46.55, 'PAMIĘTAJ', 260)]
ZBLUR = [9.04, 24.30, 36.77]

SFX = [*[('click-pop_01_A.wav', 0.42 + 0.22 * i, -24, 'start') for i in range(6)],
       ('click-pop_04_B.wav', 4.58, -21, 'start'),
       ('hit_01_A.wav', 9.04, -17, 'start'), ('chime_ok.wav', 9.10, -23, 'start'), ('pen_scribble.wav', 9.16, -28, 'start'),
       ('whoosh-rise_04_C.wav', 10.80, -21, 'peak'), ('whoosh-rise_04_C.wav', 16.95, -21, 'peak'),
       ('counter_ticks.wav', 19.44, -25, 'start'), ('pen_scribble.wav', 21.48, -28, 'start'),
       ('whoosh-rise_04_C.wav', 24.30, -21, 'peak'), ('click-pop_04_B.wav', 24.40, -21, 'start'),
       ('click-pop_01_A.wav', 26.76, -20, 'start'), ('counter_ticks.wav', 27.48, -25, 'start'),
       ('click-pop_01_A.wav', 29.76, -20, 'start'), ('counter_ticks.wav', 30.78, -25, 'start'),
       ('click-pop_04_B.wav', 32.82, -21, 'start'), ('chime_ok.wav', 35.84, -22, 'start'),
       ('whoosh-rise_04_C.wav', 36.77, -21, 'peak'),
       ('buzz_no.wav', 40.88, -26, 'start'), ('click-pop_04_B.wav', 43.16, -21, 'start'),
       ('click-pop_04_B.wav', 46.72, -21, 'start')]
STEMS = 'sep3/htdemucs/audio_v3'
MUSIC_GAIN_DB = -8          # author: music quieter
SUB_SIZE = 62               # author: subtitles a bit smaller
