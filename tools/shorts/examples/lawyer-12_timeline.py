# Lawyer short 12 — "mama zostawiła kredyt — czy musisz spłacać?" (40.5 s). 11.37–16.23 blue placeholder → kinship animation.
SRC = 'src/video.mp4'
SUB_SIZE = 62
STEMS = 'sep/htdemucs/audio'
MUSIC_GAIN_DB = -80
SFX_GAIN_DB = -4
FIXES = {93: 'polisy.'}

ZOOMS = [(0, 1.0)]
CUTS = [6.87, 11.37, 16.23, 20.73, 28.33, 34.5]
NOTIFS = [(0.90, 2.98, 'BANK', 'Zaległa rata kredytu', 'Do spłaty: 1 240 zł', 330)]   # author chose variant A
RESULTS = []
PIPS = [(3.04, 5.75, {'fn': 'court_doc', 'args': ('UMOWA KREDYTU', 'MUSISZ SPŁACAĆ?', 4.48, 'BANK')})]
BEHIND = [(5.80, 6.85, ['NIE', 'ZAWSZE'], 440, (255, 255, 255), 190)]
HEADLINES = [(6.92, 11.30, ['AUTOMATYCZNIE', 'PRZEJMUJESZ DŁUGI'], 10.70, 'NIEPRAWDA', 330, 0.8)]
SCENES = [(11.37, 16.23, {'fn': 'scene_kinship', 't_link': 11.74, 't_bank': 13.86, 't_claim': 14.42, 't_block': 15.56, 'verdict': 'NIE AUTOMATYCZNIE'})]
SIDECARDS = [(16.30, 20.70, [(17.74, 'CZY JESTEŚ SPADKOBIERCĄ?', 'L'), (19.58, 'JAK PRZYJMUJESZ SPADEK?', 'R')], 330)]
OPTIONS3 = [(20.74, 28.20, [(21.00, 'ODRZUCENIE', 'BEZ DŁUGÓW', (46, 196, 110)),
                            (22.54, 'INWENTARZ', 'DO WARTOŚCI', (244, 122, 58)),
                            (24.40, 'WPROST', 'CAŁY DŁUG', (225, 25, 30))], 27.14, 'INNE KONSEKWENCJE', 420)]
INSURE = [(28.80, 34.40, 30.12, 33.24, 420)]
RESULTS += [(37.52, 40.47, 'NAJPIERW USTAL OBOWIĄZEK', (244, 122, 58), 560)]

SFX = [('msg_in.wav', 0.95, -21, 'start'),
       ('whoosh1.wav', 3.04, -20, 'peak'), ('pencil_s.wav', 3.30, -26, 'start'), ('click2.wav', 4.48, -19, 'start'),
       ('click1.wav', 6.94, -21, 'start'), ('metal.wav', 10.70, -20, 'start'),
       ('whoosh_el.wav', 11.37, -21, 'peak'), ('pop1.wav', 11.74, -21, 'start'), ('pop_low.wav', 13.86, -19, 'start'),
       ('whoosh2.wav', 14.42, -22, 'peak'), ('fail.wav', 15.56, -26, 'start'),
       ('whoosh_el.wav', 16.23, -22, 'peak'),
       ('whoosh2.wav', 17.74, -22, 'peak'), ('whoosh2.wav', 19.58, -22, 'peak'),
       ('pop1.wav', 21.00, -21, 'start'), ('pop1.wav', 22.54, -21, 'start'), ('pop_low.wav', 24.40, -19, 'start'), ('click2.wav', 27.14, -20, 'start'),
       ('pop_low.wav', 28.82, -19, 'start'), ('clock_s.wav', 30.12, -25, 'start'), ('ok.wav', 33.24, -25, 'start'),
       ('click1.wav', 37.54, -20, 'start')]
