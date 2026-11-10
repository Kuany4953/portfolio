"""Text in, audio out, through OpenRouter's speech endpoint (spec.md §12.3).

    python3 speak.py "Hello from CPSC 415." --out answer-mai.wav
    python3 speak.py --from answer.txt --model elevenlabs/eleven-v4-turbo --voice george --out answer-eleven.mp3

The CLI shapes the text first (shape.spoken: no markdown, at most three sentences).
The reply is raw audio, with no usage in it. The bill is in the generation record
(X-Generation-Id), which can take about a minute to appear, so until then the cost
is the catalog price per character times characters. Request shape adapted from
examples/voice-loop/speak.py. A .wav output asks for PCM and writes the header
here, because MP3 headers have carried a wrong length and cut transcripts short.
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.request
import wave
from pathlib import Path

from shape import is_audio, spoken

DEFAULT_MODEL = "microsoft/mai-voice-2.1-flash"
DEFAULT_VOICE = "en-IN-Priya:MAI-Voice-2.1-Flash"
COMPARISON = ("elevenlabs/eleven-v4-turbo", "george")
CATALOG = "https://openrouter.ai/api/v1/models?output_modalities=speech"


class NotAudio(RuntimeError):
    """The speech endpoint replied with something that is not audio (usually a JSON error)."""


def speak(client, text: str, out: Path, model: str = DEFAULT_MODEL, voice: str = DEFAULT_VOICE,
          prices: dict[str, float] | None = None) -> dict:
    """One billed call. Saves the audio only if it is audio, and returns what CHECKS.md records."""
    out = Path(out)
    fmt = "pcm" if out.suffix.lower() == ".wav" else "mp3"
    t0 = time.time()
    r = client.tts.create_speech(model=model, input=text, voice=voice, response_format=fmt)
    data = r.read()
    seconds = round(time.time() - t0, 1)
    ctype = r.headers.get("content-type", "")
    if not is_audio(ctype, data):
        raise NotAudio(f"expected audio, got {ctype or 'no content type'}: {data[:300]!r}")
    if fmt == "pcm":
        rate = int((re.search(r"rate=(\d+)", ctype) or ["", "24000"])[1])
        channels = int((re.search(r"channels=(\d+)", ctype) or ["", "1"])[1])
        with wave.open(str(out), "wb") as w:
            w.setnchannels(channels)
            w.setsampwidth(2)
            w.setframerate(rate)
            w.writeframes(data)
    else:
        out.write_bytes(data)
    gen_id = r.headers.get("x-generation-id")
    billed = billed_cost(client, gen_id)
    return {"file": str(out), "model": model, "voice": voice, "chars": len(text), "bytes": len(data),
            "seconds": seconds, "generation_id": gen_id,
            "cost": billed if billed is not None else estimate(model, len(text), prices),
            "cost_is_estimate": billed is None}


def billed_cost(client, gen_id: str | None) -> float | None:
    """One look at the generation record. Not there yet is normal; the estimate covers it."""
    if not gen_id:
        return None
    try:
        return client.generations.get_generation(id=gen_id).data.total_cost
    except Exception:  # noqa: BLE001 - the audio is already saved; a missing record is not an error
        return None


def catalog_prices() -> dict[str, float]:
    """Per-character price of each speech model, from OpenRouter's public catalog (no key)."""
    with urllib.request.urlopen(CATALOG, timeout=20) as resp:
        return {m["id"]: float(m["pricing"].get("prompt") or 0) for m in json.load(resp)["data"]}


def estimate(model: str, chars: int, prices: dict[str, float] | None = None) -> float | None:
    prices = catalog_prices() if prices is None else prices
    return round(prices[model] * chars, 6) if model in prices else None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("text", nargs="?")
    ap.add_argument("--from", dest="src", type=Path, help="read the typed answer from a file")
    ap.add_argument("--out", type=Path, default=Path("answer-mai.wav"))
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--voice", default=DEFAULT_VOICE)
    a = ap.parse_args()
    typed = a.src.read_text() if a.src else a.text
    if not typed:
        ap.error("give the text, or --from a file")
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        sys.exit("OPENROUTER_API_KEY is not set; nothing was billed.")
    from openrouter import OpenRouter
    text = spoken(typed)
    try:
        info = speak(OpenRouter(api_key=key), text, a.out, a.model, a.voice)
    except NotAudio as e:
        sys.exit(f"not saved: {e}")
    print(f"spoken: {text!r}")
    print(f"{info['file']}  {info['bytes']} bytes  {info['chars']} chars  {info['seconds']}s  "
          f"${info['cost']}{' (estimated)' if info['cost_is_estimate'] else ''}  "
          f"[{info['model']} / {info['voice']}]  gen={info['generation_id']}")


if __name__ == "__main__":
    main()
