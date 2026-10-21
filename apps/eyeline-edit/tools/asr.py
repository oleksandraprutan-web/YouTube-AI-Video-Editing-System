"""Local speech recognition adapter. Models download on first use."""
import platform
_model = None

def transcribe(path, **options):
    global _model
    options.pop("path_or_hf_repo", None)
    if platform.system() == "Darwin" and platform.machine() == "arm64":
        import mlx_whisper
        return mlx_whisper.transcribe(path, path_or_hf_repo="mlx-community/whisper-large-v3-turbo", **options)
    from faster_whisper import WhisperModel
    if _model is None:
        _model = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8")
    segments, _ = _model.transcribe(path, **options)
    rows = [{"start": s.start, "end": s.end, "text": s.text, "no_speech_prob": s.no_speech_prob,
             "words": [{"start": w.start, "end": w.end, "word": w.word, "probability": w.probability}
                       for w in (s.words or [])]} for s in segments]
    return {"segments": rows, "text": " ".join(s["text"] for s in rows)}
