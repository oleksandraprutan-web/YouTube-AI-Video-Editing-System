# Lawyer short 16 — "4 argumenty przeciw opiece naprzemiennej" (41.1 s). MODERN style: gradients, outlined numerals, kinetic type, top tracker.
# 15.0–20.9 orange placeholder → argument 2 scene; 28.4–34.93 blue placeholder → argument 4 scene.
SRC = 'src/video.mp4'
SUB_SIZE = 62
STEMS = 'sep/htdemucs/audio'
MUSIC_GAIN_DB = -80
SFX_GAIN_DB = -4

ZOOMS = [(0, 1.0)]
CUTS = [9.8, 15.0, 20.9, 28.4, 34.93]
HOOKQ = [(0.30, 4.15, 'DOBRY\nRODZIC', 0.98, 'OPIEKA\nNAPRZEMIENNA', 2.04, 3.52, 330)]
FOURS = [(4.22, 9.75, [4.46, 4.62, 4.78, 4.94], 'ARGUMENTY', 5.10, 300)]
TRACKERS = [(9.82, 14.98, [(9.82, 'PRZEPROWADZKI'), (99, ''), (99, ''), (99, '')], 150),
            (20.90, 28.38, [(0, 'PRZEPROWADZKI'), (0, 'WIEK I EMOCJE'), (20.90, 'KONFLIKT RODZICÓW'), (99, '')], 150)]
CHIPS = [(10.82, 14.98, [(10.82, 'CIĄGŁE PRZEPROWADZKI'), (13.36, 'BRAK BEZPIECZEŃSTWA')], 330)]
SCENES = [(15.00, 20.90, {'fn': 'scene_two_homes_modern', 'title': 'WIEK I EMOCJE', 't_homes': 15.3,
           'gauges': [(15.90, 'WIEK DZIECKA', 0.35), (17.02, 'POTRZEBY EMOCJONALNE', 0.85)],
           't_verdict': 18.52, 'verdict': 'NIE KAŻDE DZIECKO JEST GOTOWE'}),
          (28.40, 34.93, {'fn': 'scene_distance_modern', 'title': 'ODLEGŁOŚĆ', 't_route': 29.58, 't_timer': 31.12, 'minutes': 75,
           'tags': [(32.90, 'NAUKA'), (33.88, 'CODZIENNOŚĆ')]})]
BEHIND = [(21.90, 25.00, ['KONFLIKT'], 520, (255, 120, 90), 190)]
CHIPS += [(25.62, 28.38, [(25.62, 'DZIECKO'), (27.34, 'W ŚRODKU SPORU')], 420)]
BEHIND += [(39.66, 41.05, ['DOBRO', 'DZIECKA'], 470, (255, 140, 60), 175)]

SFX = [('pop1.wav', 0.32, -21, 'start'), ('ok.wav', 0.98, -26, 'start'), ('whoosh2.wav', 2.04, -22, 'peak'), ('pop_low.wav', 3.52, -18, 'start'),
       ('click1.wav', 4.46, -21, 'start'), ('click1.wav', 4.62, -21, 'start'), ('click1.wav', 4.78, -21, 'start'), ('click1.wav', 4.94, -21, 'start'), ('pop_low.wav', 5.10, -19, 'start'),
       ('click1.wav', 9.84, -21, 'start'), ('pop1.wav', 10.82, -21, 'start'), ('pop2.wav', 13.36, -21, 'start'),
       ('whoosh_el.wav', 15.00, -21, 'peak'), ('click1.wav', 15.90, -22, 'start'), ('click1.wav', 17.02, -22, 'start'), ('text_in_s.wav', 18.52, -25, 'start'),
       ('whoosh_el.wav', 20.90, -22, 'peak'), ('click1.wav', 20.95, -21, 'start'), ('pop_low.wav', 21.90, -19, 'start'),
       ('pop1.wav', 25.62, -21, 'start'), ('pop2.wav', 27.34, -21, 'start'),
       ('whoosh_el.wav', 28.40, -21, 'peak'), ('swipe.wav', 29.58, -24, 'start'), ('clock_s.wav', 31.12, -25, 'start'), ('pop1.wav', 32.90, -21, 'start'), ('pop2.wav', 33.88, -21, 'start'),
       ('whoosh_el.wav', 34.93, -22, 'peak'),
       ('star_s.wav', 39.68, -26, 'start')]
