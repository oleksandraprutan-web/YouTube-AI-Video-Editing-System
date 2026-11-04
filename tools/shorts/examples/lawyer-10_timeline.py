# Lawyer short 10 — "meldunek a eksmisja" (39.8 s). 22.93–32.03 blue placeholder → eviction animation.
SRC = 'src/video.mp4'
SUB_SIZE = 62
STEMS = 'sep/htdemucs/audio'
MUSIC_GAIN_DB = -80
SFX_GAIN_DB = -4

ZOOMS = [(0, 1.0)]
CUTS = [8.33, 16.97, 22.93, 32.03]
BUBBLES = [(2.30, 5.80, [(3.30, 'JESTEM ZAMELDOWANY!', (540, 1180), 'L')])]
PIPS = [(5.88, 8.30, {'fn': 'shield_q', 'args': ('MELDUNEK', 7.24)})]
BEHIND = [(8.34, 8.84, ['NIE'], 700, (244, 122, 58), 380)]
HEADLINES = [(8.86, 12.95, ['MELDUNEK', 'CHRONI PRZED EKSMISJĄ'], 9.64, 'MIT', 240, 0.75)]
NOTEQ = [(13.08, 16.90, (13.76, 'MELDUNEK'), (14.42, '≠'), (15.04, 'PRAWO DO MIESZKANIA'), 320)]
TILES = [(17.06, 21.10, [('EWIDENCJA', 17.62, 'ok', 'TO JEST WPIS'), ('TYTUŁ PRAWNY', 19.34, 'x', 'TO NIE JEST')], 330)]
RESULTS = [(21.22, 22.90, 'CO TO OZNACZA W PRAKTYCE?', (244, 122, 58), 330)]
SCENES = [(22.93, 32.03, {'fn': 'scene_eviction', 't_terminated': 24.90, 't_expired': 25.94, 't_tenant': 26.86,
           't_court': 29.90, 't_pozew': 31.06, 'pozew': 'POZEW O EKSMISJĘ'})]
STRIKES = [(33.78, 37.95, 'NIC MI NIE ZROBISZ', 37.02, (540, 1180))]
BEHIND += [(38.70, 39.84, ['MOŻESZ!'], 720, (244, 122, 58), 190)]

SFX = [('msg_in.wav', 3.30, -22, 'start'),
       ('whoosh1.wav', 5.88, -20, 'peak'), ('click2.wav', 7.24, -19, 'start'),
       ('whoosh_fast.wav', 8.88, -22, 'peak'), ('metal.wav', 9.64, -20, 'start'),
       ('click1.wav', 13.76, -21, 'start'), ('pop_low.wav', 14.42, -19, 'start'), ('click1.wav', 15.04, -21, 'start'),
       ('pop1.wav', 17.62, -21, 'start'), ('fail.wav', 19.34, -26, 'start'),
       ('click2.wav', 21.22, -20, 'start'),
       ('whoosh_el.wav', 22.93, -21, 'peak'), ('pencil_s.wav', 23.10, -26, 'start'),
       ('metal.wav', 24.90, -22, 'start'), ('metal.wav', 25.94, -22, 'start'), ('pop2.wav', 26.86, -20, 'start'),
       ('whoosh2.wav', 29.90, -22, 'peak'), ('pop_low.wav', 30.30, -19, 'start'), ('text_in_s.wav', 31.06, -25, 'start'),
       ('whoosh_el.wav', 32.03, -22, 'peak'),
       ('msg_in.wav', 33.80, -22, 'start'), ('marker_s.wav', 37.02, -26, 'start'),
       ('star_s.wav', 38.74, -26, 'start')]
