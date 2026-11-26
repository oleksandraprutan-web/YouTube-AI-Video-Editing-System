# Lawyer short 15 — "rozwód z obcokrajowcem w Polsce" (29.2 s). 8.67–19.5 blue placeholder → jurisdiction animation.
SRC = 'src/video.mp4'
SUB_SIZE = 62
STEMS = 'sep/htdemucs/audio'
MUSIC_GAIN_DB = -80
SFX_GAIN_DB = -4

ZOOMS = [(0, 1.0)]
CUTS = [4.57, 8.67, 19.5]
FLIGHTS = [(0.30, 4.50, 'PL', '?', 2.30, 300)]                                  # "musisz jechać do obcego kraju?"
BEHIND = [(7.82, 8.62, ['W POLSCE'], 560, (244, 122, 58), 170)]
SCENES = [(8.67, 19.50, {'fn': 'scene_jurisdiction', 'title': 'POLSKI SĄD, JEŚLI:',
           't_c1': 9.00, 't_c1ok': 9.96, 'c1': 'OBYWATELKA\nPOLSKI',
           't_c2': 10.76, 't_ring': 12.32, 't_c2ok': 14.18, 'c2': 'MIESZKASZ\nW POLSCE', 'ring': '6 M',
           't_res': 17.66, 'res': 'POLSKI SĄD'})]
TILES = [(19.56, 26.20, [('OBYWATELSTWO', 20.26, 'x', 'NIE MASZ'), ('ROK W POLSCE', 25.36, 'ok', 'WYSTARCZY')], 400)]
RESULTS = [(27.12, 29.18, 'MIEJSCE ŚLUBU BEZ ZNACZENIA', (46, 196, 110), 420)]

SFX = [('pop1.wav', 0.32, -21, 'start'), ('whoosh_fast.wav', 2.30, -23, 'peak'),
       ('pop_low.wav', 7.82, -19, 'start'),
       ('whoosh_el.wav', 8.67, -21, 'peak'), ('text_in_s.wav', 8.75, -25, 'start'),
       ('pop1.wav', 9.00, -21, 'start'), ('ok.wav', 9.96, -26, 'start'), ('pop1.wav', 10.76, -21, 'start'),
       ('clock_s.wav', 12.32, -25, 'start'), ('ok.wav', 14.18, -26, 'start'), ('metal.wav', 17.66, -21, 'start'),
       ('whoosh_el.wav', 19.50, -22, 'peak'),
       ('pop1.wav', 19.58, -21, 'start'), ('fail.wav', 20.26, -27, 'start'), ('ok.wav', 25.36, -26, 'start'),
       ('click2.wav', 27.14, -20, 'start')]
