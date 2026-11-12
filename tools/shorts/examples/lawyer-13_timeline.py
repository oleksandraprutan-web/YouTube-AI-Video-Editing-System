# Lawyer short 13 — "narcyz a władza rodzicielska" (53.5 s). 40.8–45.23 orange placeholder → label animation.
SRC = 'src/video.mp4'
SUB_SIZE = 62
STEMS = 'sep/htdemucs/audio'
MUSIC_GAIN_DB = -80
SFX_GAIN_DB = -4

ZOOMS = [(0, 1.0)]
CUTS = [6.63, 11.57, 19.37, 21.37, 33.33, 40.8, 45.23]
SIDECARDS = [(0.40, 3.70, [(0.70, 'ROZWÓD Z NARCYZEM', 'L'), (1.86, 'OGRANICZENIE WŁADZY', 'R')], 300)]
PULSES = [(4.30, 6.60, 'JEDNA WAŻNA RZECZ', 420)]
BUBBLES = [(7.40, 10.75, [(7.66, 'WYSOKI SĄDZIE…', (380, 380), 'L'), (10.08, 'ON JEST NARCYZEM!', (680, 520), 'R')])]
BEHIND = [(10.78, 11.55, ['NIE', 'WYSTARCZY'], 520, (255, 255, 255), 145)]
TILES = [(12.04, 19.35, [('ETYKIETA', 12.30, 'x', 'BEZ ZNACZENIA'), ('WPŁYW NA DZIECKO', 17.76, 'ok', 'MA ZNACZENIE')], 430)]
RESULTS = [(19.56, 21.30, 'CO MA ZNACZENIE?', (244, 122, 58), 420)]
CHECKLISTS = [(22.40, 33.30, [(23.70, 'UTRUDNIA KONTAKTY'), (25.64, 'STAWIA WARUNKI'), (29.60, 'SAM DECYDUJE O ZDROWIU')], 1230, 'dim')]
TUGS = [(34.40, 40.75, 37.60, 'DZIECKO W KONFLIKCIE', 360)]
SCENES = [(40.80, 45.23, {'fn': 'scene_label', 'tag': 'NARCYZ', 't_lens': 42.56, 't_x': 44.60,
           't_msg': 41.66, 'msg': ['NIE UDOWADNIAJ', 'ETYKIETY']})]
SIDECARDS += [(45.40, 53.50, [(45.66, 'KONKRETNE ZACHOWANIA', 'L'), (47.46, 'DOWODY', 'R'), (49.14, 'DOBRO DZIECKA', 'L')], 290)]

SFX = [('whoosh2.wav', 0.70, -22, 'peak'), ('whoosh2.wav', 1.86, -22, 'peak'),
       ('warn.wav', 4.32, -27, 'start'),
       ('msg_sent.wav', 7.66, -22, 'start'), ('msg_in.wav', 10.08, -22, 'start'),
       ('pop1.wav', 12.30, -21, 'start'), ('fail.wav', 12.40, -27, 'start'), ('pop1.wav', 17.76, -21, 'start'), ('ok.wav', 17.86, -26, 'start'),
       ('click2.wav', 19.58, -20, 'start'),
       ('marker_s.wav', 23.70, -26, 'start'), ('marker_s.wav', 25.64, -26, 'start'), ('marker_s.wav', 29.60, -26, 'start'),
       ('pop_low.wav', 34.42, -19, 'start'), ('swipe.wav', 37.60, -24, 'start'),
       ('whoosh_el.wav', 40.80, -21, 'peak'), ('text_in_s.wav', 41.66, -25, 'start'), ('whoosh1.wav', 42.56, -23, 'peak'), ('metal.wav', 44.60, -21, 'start'),
       ('whoosh_el.wav', 45.23, -22, 'peak'),
       ('whoosh2.wav', 45.66, -22, 'peak'), ('whoosh2.wav', 47.46, -22, 'peak'), ('whoosh2.wav', 49.14, -22, 'peak'), ('star_s.wav', 51.52, -27, 'start')]
