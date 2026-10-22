#!/usr/bin/env bash
# One-time setup for a fresh cloud session: fonts, Python deps, speech model.
set -e
mkdir -p ~/.fonts
for f in Black Medium; do
  [ -f ~/.fonts/Montserrat-$f.ttf ] || curl -sS -o ~/.fonts/Montserrat-$f.ttf https://raw.githubusercontent.com/JulietaUla/Montserrat/master/fonts/ttf/Montserrat-$f.ttf
done
fc-cache -f >/dev/null || true
pip3 install -q faster-whisper "opencv-python-headless<5" numpy pillow 2>&1 | grep -v WARN || true
python3 -c "from huggingface_hub import snapshot_download; snapshot_download('mobiuslabsgmbh/faster-whisper-large-v3-turbo')" >/dev/null
echo "shorts setup ok"
