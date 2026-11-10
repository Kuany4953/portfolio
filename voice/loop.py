"""One voice turn and what the server accepts (spec.md §12.4 behaviors 2, 6, 9, 10).

No network here: the three billed steps are passed in, so the same code runs on
the server (real client) and in the tests (fakes).
"""
import base64
import io
import wave

from shape import spoken

MAX_BODY = 4 * 1024 * 1024          # Vercel refuses over 4.5 MB before our code runs
MAX_COMPRESSED = 512 * 1024         # 15 s even at 256 kbps
MAX_WAV_SECONDS = 16                # the page stops at 15 s; a direct POST must not do better
MIN_WORDS = 3
NOT_CAUGHT = "I didn't catch that."
FORMATS = {"audio/webm": "webm", "audio/ogg": "ogg", "audio/mpeg": "mp3", "audio/mp3": "mp3",
           "audio/wav": "wav", "audio/x-wav": "wav", "audio/wave": "wav",
           "audio/mp4": "m4a", "audio/x-m4a": "m4a"}


class Refused(Exception):
    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status


def check_request(content_type: str | None, body: bytes) -> str:
    """The format to send to the transcriber, or Refused(status) before anything is billed."""
    if len(body) > MAX_BODY:
        raise Refused(413, f"recording over {MAX_BODY // (1024 * 1024)} MB")
    kind = (content_type or "").split(";")[0].strip().lower()
    fmt = FORMATS.get(kind)
    if not fmt:
        raise Refused(415, f"unsupported audio type {kind!r}; send one of {sorted(FORMATS)}")
    if not body:
        raise Refused(400, "empty recording")
    if fmt == "wav":
        try:
            with wave.open(io.BytesIO(body)) as w:
                seconds = w.getnframes() / w.getframerate()
        except (wave.Error, EOFError, ZeroDivisionError) as e:
            raise Refused(400, f"not a readable WAV: {e}") from None
        if seconds > MAX_WAV_SECONDS:
            raise Refused(413, f"recording is {seconds:.1f} s; the limit is {MAX_WAV_SECONDS} s")
    elif len(body) > MAX_COMPRESSED:
        raise Refused(413, f"compressed recording over {MAX_COMPRESSED // 1024} KB (about 15 s)")
    return fmt


def voice_turn(audio: bytes, fmt: str, transcribe_fn, answer_fn, speak_fn) -> dict:
    """Hear, think, speak, once. transcribe_fn(audio, fmt) -> {text, cost, ...};
    answer_fn(question) -> (typed answer, cost), the same function the typed path calls;
    speak_fn(text) -> (audio bytes, cost)."""
    heard = transcribe_fn(audio, fmt)
    question = (heard.get("text") or "").strip()
    costs = {"transcribe": heard.get("cost"), "answer": 0, "speak": 0}
    result = {"transcript": question, "answer": NOT_CAUGHT, "audio": None, "speak_error": None}
    if len(question.split()) >= MIN_WORDS:
        typed, costs["answer"] = answer_fn(question)
        result["answer"] = spoken(typed)
        try:
            data, costs["speak"] = speak_fn(result["answer"])
            result["audio"] = base64.b64encode(data).decode()
        except Exception as e:  # noqa: BLE001 - the visitor can still read what they could not hear
            result["speak_error"] = str(e)[:300]
    costs["total"] = sum(c for c in costs.values() if c)
    result["costs"] = costs
    return result
