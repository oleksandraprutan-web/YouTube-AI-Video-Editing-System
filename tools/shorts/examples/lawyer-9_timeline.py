# Lawyer short 9 — "dziecko nie chce iść do taty" (36.2 s). Side/depth animations, PIP, text behind person, author's SFX pack.
SRC = 'src/video.mp4'
SUB_SIZE = 62
STEMS = 'sep/htdemucs/audio'
MUSIC_GAIN_DB = -80
SFX_GAIN_DB = -4
FIXES = {71: 'niechęć', 88: 'nocowań'}
MERGE = [(79, 'do sądu')]

ZOOMS = [(0, 1.0), (9.12, 1.0)]
CUTS = [9.13, 19.63, 25.3]
BUBBLES = [(0.40, 3.30, [(0.52, 'PŁACZE', (215, 600), 'R'), (1.16, 'KRZYCZY', (870, 680), 'L'), (2.14, 'NIE CHCĘ DO TATY!', (540, 1230), 'L')])]
PIPS = [(3.30, 9.08, {'fn': 'court_doc', 'args': ('POSTANOWIENIE SĄDU', 'MUSISZ ZMUSIĆ?', 5.12)})]
BEHIND = [(9.12, 9.80, ['NIE', 'ZAWSZE'], 720, (255, 255, 255), 230),
          (15.96, 19.55, ['NIE', 'ZMUSZAJ'], 560, (244, 122, 58), 200)]
SIDECARDS = [(10.40, 15.80, [(12.76, 'LĘKI', 'L'), (13.64, 'ZACHOWANIE OJCA', 'R'), (14.94, 'INNE PRZYCZYNY', 'L')], 980)]
CHECKLISTS = [(19.80, 25.20, [(20.04, 'PRZYGOTUJ'), (22.40, 'ZACHĘCAJ'), (23.82, 'SZUKAJ ROZWIĄZAŃ')], 1220, 'dim')]
SCENES = [(25.30, 36.18, {'fn': 'scene_contacts', 't_court': 28.62, 't_title': 29.60, 'title': 'ZMIANA KONTAKTÓW',
           'options': [(31.64, 'SKRÓCENIE', 'clock'), (32.68, 'BEZ\nNOCOWAŃ', 'moon'), (34.52, 'NADZÓR\nKURATORA', 'eye')]})]

SFX = [('pop1.wav', 0.52, -20, 'start'), ('pop2.wav', 1.16, -20, 'start'), ('msg_in.wav', 2.14, -22, 'start'),
       ('whoosh1.wav', 3.30, -20, 'peak'), ('click1.wav', 3.80, -20, 'start'), ('pencil_s.wav', 3.95, -26, 'start'), ('click2.wav', 5.12, -18, 'start'),
       ('whoosh_fast.wav', 9.08, -22, 'peak'), ('bass_s.wav', 9.12, -20, 'start'),
       ('whoosh2.wav', 12.76, -22, 'peak'), ('whoosh2.wav', 13.64, -22, 'peak'), ('whoosh2.wav', 14.94, -22, 'peak'),
       ('metal.wav', 15.96, -20, 'start'), ('letters_s.wav', 16.00, -26, 'start'),
       ('click1.wav', 19.82, -21, 'start'), ('marker_s.wav', 20.04, -26, 'start'), ('marker_s.wav', 22.40, -26, 'start'), ('marker_s.wav', 23.82, -26, 'start'),
       ('ok.wav', 24.40, -24, 'start'),
       ('whoosh_el.wav', 25.30, -21, 'peak'), ('text_in_s.wav', 25.40, -25, 'start'),
       ('whoosh1.wav', 28.62, -21, 'peak'), ('click2.wav', 29.62, -19, 'start'),
       ('clock_s.wav', 31.64, -24, 'start'), ('pop1.wav', 32.68, -20, 'start'), ('pencil_s.wav', 33.03, -26, 'start'), ('pop2.wav', 34.52, -20, 'start'), ('star_s.wav', 35.0, -26, 'start')]
