# Lawyer short 11 — "ograniczenie władzy ≠ zakaz kontaktu" (30.7 s). Person sits low → graphics in the top band.
SRC = 'src/video.mp4'
SUB_SIZE = 62
STEMS = 'sep/htdemucs/audio'
MUSIC_GAIN_DB = -80
SFX_GAIN_DB = -4

ZOOMS = [(0, 1.0)]
CUTS = [4.47, 8.87, 14.13, 19.5]
DOORS = [(0.30, 4.40, 3.08, 380)]                                     # author chose variant E
SEPARATE = [(4.50, 8.85, 'WŁADZA\nRODZICIELSKA', 'KONTAKTY\nZ DZIECKIEM', 7.60, 'DWIE ODRĘBNE KWESTIE', 420)]
STRIKES = [(8.90, 14.10, 'TRACI KONTAKT', 10.44, (540, 470))]
BEHIND = [(14.62, 16.40, ['NADAL'], 790, (255, 255, 255), 235)]
PULSES = [(19.56, 22.98, 'ZAGROŻENIE DOBRA DZIECKA', 420)]
LADDERS = [(23.06, 30.74, [(23.66, 'KONTAKT\nOGRANICZONY', (244, 122, 58)), (25.54, 'NADZÓR\nKURATORA', (244, 122, 58)), (29.56, 'CAŁKOWITY\nZAKAZ', (225, 25, 30))], 470)]

SFX = [('pop_low.wav', 0.42, -19, 'start'), ('click1.wav', 0.75, -21, 'start'), ('pop1.wav', 3.08, -21, 'start'), ('whoosh1.wav', 3.40, -24, 'peak'),
       ('pop1.wav', 4.52, -21, 'start'), ('whoosh2.wav', 7.60, -22, 'peak'), ('click2.wav', 7.92, -20, 'start'),
       ('click1.wav', 8.92, -21, 'start'), ('marker_s.wav', 10.44, -26, 'start'),
              ('warn.wav', 19.58, -27, 'start'),
       ('pop_low.wav', 23.66, -19, 'start'), ('pop_low.wav', 25.54, -19, 'start'), ('metal.wav', 29.56, -21, 'start')]
