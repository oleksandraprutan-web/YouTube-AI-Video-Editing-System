# Lawyer short 14 — "opieka naprzemienna bez współpracy / konflikt lojalnościowy" (40.9 s). 18.33–29.97 blue placeholder → loyalty animation.
SRC = 'src/video.mp4'
SUB_SIZE = 62
STEMS = 'sep/htdemucs/audio'
MUSIC_GAIN_DB = -80
SFX_GAIN_DB = -4
BG_DIM = 0.35                      # author: darker background, pro-studio look
PILL_FONT = 44

ZOOMS = [(0, 1.0)]
CUTS = [15.9, 18.33, 29.97]
SIDECARDS = [(0.30, 5.95, [(1.00, 'BRAK POROZUMIENIA', 'L'), (4.50, 'ŻĄDA OPIEKI NAPRZEMIENNEJ', 'R')], 260)]
LINKS = [(6.04, 9.75, 'MAMA', 'TATA', 'STAŁA WSPÓŁPRACA', 7.04, 8.20, 360)]
PILL_GROUPS = [(15.85, [170, 275, 380], [(11.78, 'SZKOŁA', 0, 0), (12.48, 'LECZENIE', 0, 1), (13.28, 'ZAJĘCIA DODATKOWE', 1, None), (14.64, 'CODZIENNE POTRZEBY', 2, None)])]
PULSES = [(15.94, 18.30, 'KAŻDA ROZMOWA = KŁÓTNIA', 300)]
SCENES = [(18.33, 29.97, {'fn': 'scene_loyalty', 'title': 'WYOBRAŹ SOBIE', 't_bad': 21.80, 't_move': 23.98,
           't_fear': 25.16, 'fear': 'BOI SIĘ…', 't_msg': 27.70, 'msg': 'POSŁANIEC MIĘDZY RODZICAMI'})]
BEHIND = [(30.58, 33.55, ['KONFLIKT', 'LOJALNOŚCIOWY'], 430, (244, 122, 58), 100)]
PULSES += [(33.62, 35.70, 'NAPIĘCIE EMOCJONALNE', 300)]
HEADLINES = [(35.76, 40.87, ['SĄD BADA', 'WSPÓŁPRACĘ RODZICÓW'], 40.04, 'KLUCZOWE', 300, 0.8)]

SFX = [('whoosh2.wav', 1.00, -22, 'peak'), ('whoosh2.wav', 4.50, -22, 'peak'),
       ('pop1.wav', 6.06, -21, 'start'), ('pencil_s.wav', 7.04, -27, 'start'), ('click2.wav', 8.20, -20, 'start'),
       ('pop1.wav', 11.78, -21, 'start'), ('pop1.wav', 12.48, -21, 'start'), ('pop2.wav', 13.28, -21, 'start'), ('pop2.wav', 14.64, -21, 'start'),
       ('warn.wav', 15.96, -27, 'start'),
       ('whoosh_el.wav', 18.33, -21, 'peak'), ('text_in_s.wav', 18.40, -25, 'start'), ('fail.wav', 21.80, -27, 'start'),
       ('swipe.wav', 23.98, -24, 'start'), ('pop_low.wav', 25.16, -19, 'start'), ('msg_sent.wav', 27.70, -22, 'start'), ('msg_in.wav', 28.80, -22, 'start'),
       ('whoosh_el.wav', 29.97, -22, 'peak'),
       ('pop_low.wav', 30.60, -19, 'start'), ('warn.wav', 33.64, -27, 'start'),
       ('click1.wav', 35.78, -21, 'start'), ('metal.wav', 40.04, -21, 'start')]
