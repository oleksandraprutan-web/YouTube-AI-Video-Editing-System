# Shorts renderer

Generic renderer for vertical shorts (1080×1920, 30 fps). Per-video timeline lives in `timeline.py` inside the project folder (see `examples/`).

Project folder (under `.local/`, never committed):
```
project/
  src/video.mp4        # cut source
  words.json           # faster-whisper word timings (large-v3-turbo, language="pl")
  faces.json           # python3 tools/shorts/face.py src/video.mp4  (face tracking for zoom anchor)
  sfx/                 # author's sound effects + typing.mp3 (not in git)
  timeline.py          # zooms, headings, pills, circle, SFX, ASR fixes …
```
Run inside the project folder:
```
python3 ../../tools/shorts/mix.py                       # voice + SFX + typing -> out/mix.wav (-14 LUFS)
python3 ../../tools/shorts/render.py --preview 3 10 25   # stills into prev/
python3 ../../tools/shorts/render.py                     # -> out/preview.mp4
```
Timeline keys: END, ZOOMS, XMARKS, BIGTEXT, HEADINGS, TINT+PILLS, CIRCLES (start, end, phrase splits, centre_y), TOPTITLE, ARROWS, ZBLUR, SFX, FIXES, MERGE.
Needs: ffmpeg, numpy, Pillow, faster-whisper, opencv-python-headless<5, `~/.fonts/Montserrat-Black.ttf`.
