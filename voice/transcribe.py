"""Audio in, text out, through OpenRouter's transcription endpoint (spec.md §12.2).

    python3 transcribe.py clips/mine-01.wav                       # one clip
    python3 transcribe.py --set clips/expected.json               # every clip, once each
    python3 transcribe.py --set clips/expected.json --model elevenlabs/scribe-v2 --out transcripts-scribe.json

The answer key's format matches the course example: a list of
{file, text, must_contain, max_wer?, note?, language?}. Request shape adapted
from examples/voice-loop/transcribe.py. Needs OPENROUTER_API_KEY; without it
nothing is billed.
"""
import argparse
import base64
import json
import os
import sys
import time
from pathlib import Path

from check import TOLERANCE, check_clip

DEFAULT_MODEL = "openai/whisper-large-v3-turbo"
COMPARISON_MODEL = "elevenlabs/scribe-v2"
FORMATS = {".wav": "wav", ".mp3": "mp3", ".m4a": "m4a", ".webm": "webm", ".ogg": "ogg", ".flac": "flac"}


def fmt_for(name: str | Path) -> str:
    fmt = FORMATS.get(Path(name).suffix.lower())
    if not fmt:
        raise ValueError(f"{name}: unknown audio format; one of {sorted(FORMATS)}")
    return fmt


def transcribe(client, audio: bytes, fmt: str, model: str = DEFAULT_MODEL,
               language: str | None = None) -> dict:
    """One billed call. Returns the text, audio seconds and cost from usage, and wall-clock seconds."""
    t0 = time.time()
    kwargs = {"language": language} if language else {}
    r = client.stt.create_transcription(
        model=model, input_audio={"data": base64.b64encode(audio).decode(), "format": fmt}, **kwargs)
    u = getattr(r, "usage", None)
    return {"text": r.text, "model": model,
            "audio_seconds": getattr(u, "seconds", None), "cost": getattr(u, "cost", None),
            "seconds": round(time.time() - t0, 1)}


def transcribe_set(client, set_path: Path, model: str = DEFAULT_MODEL,
                   language: str | None = None) -> list[dict]:
    """Each clip in the answer key: one call, checked in code. A failed call is recorded, not raised."""
    results = []
    for entry in json.loads(Path(set_path).read_text()):
        path = Path(set_path).parent / entry["file"]
        try:
            r = transcribe(client, path.read_bytes(), fmt_for(path), model,
                           language or entry.get("language"))
        except Exception as e:  # noqa: BLE001 - one bad clip must not stop the set
            r = {"text": None, "model": model, "audio_seconds": None, "cost": None,
                 "seconds": None, "error": str(e)}
        r["file"] = entry["file"]
        r["check"] = check_clip(entry["text"], r["text"], entry.get("must_contain", []),
                                entry.get("max_wer", TOLERANCE))
        results.append(r)
    return results


def line(r: dict) -> str:
    c = r["check"]
    verdict = "ok" if c["passed"] else "FAIL"
    return (f"{r['file']}: {verdict}  wer={c['wer']:.3f}  missing={c['missing']}  "
            f"{r['audio_seconds']}s audio  ${r['cost']}  {r['seconds']}s"
            + (f"  error={r['error']}" if r.get("error") else "")
            + f"\n    got: {r['text']!r}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("audio", nargs="?", type=Path)
    ap.add_argument("--set", type=Path, help="answer key: list of {file, text, must_contain}")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--language", help="ISO-639-1 hint (en, es, ...); omitted means auto-detect")
    ap.add_argument("--out", type=Path, default=Path("transcripts-whisper.json"))
    a = ap.parse_args()
    if not (a.set or a.audio):
        ap.error("give an audio file or --set")
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        sys.exit("OPENROUTER_API_KEY is not set; nothing was billed.")
    from openrouter import OpenRouter
    client = OpenRouter(api_key=key)
    if a.set:
        results = transcribe_set(client, a.set, a.model, a.language)
        for r in results:
            print(line(r))
        a.out.write_text(json.dumps(results, indent=2))
        total = sum(r["cost"] or 0 for r in results)
        print(f"{len(results)} clips, {a.model}, ${total:.5f} total, written to {a.out}")
    else:
        r = transcribe(client, a.audio.read_bytes(), fmt_for(a.audio), a.model, a.language)
        print(f"{r['text']}\n[{r['model']}  {r['audio_seconds']}s audio  ${r['cost']}  {r['seconds']}s]")


if __name__ == "__main__":
    main()
