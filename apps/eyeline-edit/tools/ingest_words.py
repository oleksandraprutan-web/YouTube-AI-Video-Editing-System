# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "numpy", "soundfile", "imageio-ffmpeg",
#   "mlx-whisper; sys_platform == 'darwin' and platform_machine == 'arm64'",
#   "faster-whisper; sys_platform != 'darwin' or platform_machine != 'arm64'",
# ]
# ///
"""Word timings for one Eyeline take, fillers included. Writes edit/words/<take>.tsv (start, end, word, prob)
and edit/words/<take>.json (segments). The prompt keeps "um" and "uh" in the transcript, so they can be cut.

    uv run tools/ingest_words.py <project> <take folder name>
"""
import json, os, subprocess, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
HUB = Path(os.environ.get("HF_HOME", Path.home() / ".cache" / "huggingface")) / "hub" / "models--mlx-community--whisper-large-v3-turbo" / "snapshots"
if HUB.is_dir() and any(HUB.iterdir()):
    os.environ["HF_HUB_OFFLINE"] = "1"      # cached: never wait on an update check
import project as P

proj, take_dir = Path(sys.argv[1]), sys.argv[2]
take_path = proj / "takes" / take_dir
key = P.take_key(take_dir)
tmp = Path(tempfile.gettempdir()) / f"eyeline-{key}-{os.getpid()}-16k.wav"
subprocess.run([P.ffmpeg(), "-v", "error", "-y", "-i", str(take_path / "audio.wav"), "-ac", "1", "-ar", "16000", str(tmp)], check=True)
PROMPT = "Um, so, uh, basically you guys, I mean, like, um, okay. Uh, so the, the thing is, um, right."
import asr as mlx_whisper
r = mlx_whisper.transcribe(str(tmp), path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="en",
                           word_timestamps=True, condition_on_previous_text=False, temperature=0.0,
                           initial_prompt=PROMPT)
rows, segs = [], []
for s in r["segments"]:
    ws = [(round(w["start"], 3), round(w["end"], 3), w["word"].strip(), round(w.get("probability", 1), 3)) for w in s.get("words", []) if w["word"].strip()]
    segs.append({"start": s["start"], "end": s["end"], "text": s["text"].strip(), "noSpeech": s.get("no_speech_prob", 0), "words": ws})
    rows += ws
(proj / "edit" / "words").mkdir(parents=True, exist_ok=True)
P.write_atomic(proj / "edit" / "words" / f"{key}.tsv",
               "start\tend\tword\tprob\n" + "".join(f"{a:.3f}\t{b:.3f}\t{w}\t{p}\n" for a, b, w, p in rows))
P.write_json(proj / "edit" / "words" / f"{key}.json", {"take": take_dir, "model": "whisper-large-v3-turbo", "segments": segs})
tmp.unlink(missing_ok=True)
print(key, len(rows), "words", sum(1 for _, _, w, _ in rows if w.lower().strip(",.?!") in ("um", "uh", "er", "erm", "hmm")), "fillers")
