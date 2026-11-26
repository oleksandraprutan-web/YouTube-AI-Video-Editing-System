# Lawyer short 15 — "rozwód z obcokrajowcem w Polsce" (29.2 s). 8.67–19.5 blue placeholder → jurisdiction animation.
SRC = 'src/video_v2.mp4'
SUB_SIZE = 62
STEMS = 'sep2/htdemucs/audio_v2'
MUSIC_GAIN_DB = -80
SFX_GAIN_DB = -4

ZOOMS = [(0, 1.0)]
CUTS = [4.57, 8.67, 19.5]
PASSES = [(0.30, 4.50, 'WARSZAWA', '???', 2.58, 'ROZWÓD', 300)]          # author chose A
BEHIND = [(7.82, 8.62, ['W POLSCE'], 560, (244, 122, 58), 170)]
SCENES = [(8.67, 19.50, {'fn': 'scene_key', 'title': 'POLSKI SĄD, JEŚLI:', 't_p1': 9.0, 'p1': 'OBYWATELKA\nPOLSKI',
           't_p2': 10.76, 'p2': '6 MIESIĘCY\nW POLSCE', 't_join': 15.64, 't_lock': 15.64, 't_open': 17.66, 'res': 'POLSKI SĄD'})]   # author chose D
TILES = [(19.56, 26.20, [('OBYWATELSTWO', 20.26, 'x', 'NIE MASZ'), ('ROK W POLSCE', 25.36, 'ok', 'WYSTARCZY')], 400)]
RESULTS = [(27.12, 29.18, 'MIEJSCE ŚLUBU BEZ ZNACZENIA', (46, 196, 110), 420)]

SFX = [('whoosh1.wav', 0.30, -21, 'peak'), ('pop_low.wav', 2.58, -19, 'start'),
       ('pop_low.wav', 7.82, -19, 'start'),
       ('whoosh_el.wav', 8.67, -21, 'peak'), ('text_in_s.wav', 8.75, -25, 'start'),
       ('pop1.wav', 9.00, -21, 'start'), ('pop1.wav', 10.76, -21, 'start'),
       ('swipe.wav', 15.64, -24, 'start'), ('metal.wav', 16.20, -22, 'start'), ('ok.wav', 17.66, -25, 'start'),
       ('whoosh_el.wav', 19.50, -22, 'peak'),
       ('pop1.wav', 19.58, -21, 'start'), ('fail.wav', 20.26, -27, 'start'), ('ok.wav', 25.36, -26, 'start'),
       ('click2.wav', 27.14, -20, 'start')]
