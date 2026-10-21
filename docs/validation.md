# Initial release validation

Validated on macOS with Python 3.12:

- Six automated tests: public-tree exclusions, JSON examples, safe project creation, board timeline overlap rejection, editor save conflicts/source validation/media ranges, and teleprompter project/static-file boundaries.
- Python source compilation and JavaScript syntax checks for both apps.
- Isolated Chromium editor test: synthetic project loaded and played with no page errors.
- Synthetic six-second camera/audio source generated locally; its two-interval edit exported as a 4.004-second video.
- Generic board timeline rendered as a silent 1920×1080, 24000/1001 H.264 track.
- README relative links checked. Seven PNGs and three GIF excerpts included from owner-supplied media.
- Public text checked for machine paths, common credential patterns and non-placeholder skills. No copied long lines from the private skill guides were found.

These checks do not validate real speech-recognition accuracy, microphone hardware, Windows/Linux recording, GPU encoders, long-form sync, or a particular user's creative workflow. Candidate cuts require listening and human approval. A GitHub Actions template is included at templates/github-ci.yml; it is not enabled in this release.
