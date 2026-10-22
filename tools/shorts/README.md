# Shorts renderer (lawyer profile, first test edit)

Code used for the first test edit of a lawyer short. The timeline (zooms, navy/circle segments, pills, big text, arrow, sound events) is hard-coded at the top of `render.py` / in `mix.py` for that one video — copy and adjust per video.

Run from a project folder under `.local/` (media is never committed):

```
project/
  src/<video>.mp4           # cut source video
  words.json                # word timings: [{"w","s","e","p"}] from faster-whisper (large-v3-turbo, language="pl")
  sfx/*.wav, sfx/typing.mp3 # author's sound effects (not in git)
```

```
python3 /path/to/tools/shorts/mix.py          # voice + SFX + typing sound -> out/mix.wav (-14 LUFS)
python3 /path/to/tools/shorts/render.py --preview   # stills into prev/
python3 /path/to/tools/shorts/render.py       # -> out/preview.mp4 (1080x1920, 30 fps)
```

Needs: ffmpeg, numpy, Pillow, faster-whisper, font `~/.fonts/Montserrat-Black.ttf`.
