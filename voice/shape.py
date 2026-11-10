"""Spoken shape and audio check (spec.md §12.4, behaviors 3 and 6).

spoken() turns the typed answer into what is said aloud. It only removes text,
never adds it, so the spoken answer can say nothing the typed answer did not.
"""
import re

MAX_SENTENCES = 3


def spoken(text: str) -> str:
    """Strip markdown and URLs, collapse whitespace, keep at most three sentences."""
    t = text or ""
    t = re.sub(r"```.*?```", " ", t, flags=re.DOTALL)                    # fenced code
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)                  # [text](url) -> text
    t = re.sub(r"(?:https?://|www\.)\S*[^\s.,;:!?)]", "", t)        # bare URLs
    t = re.sub(r"^\s{0,3}#+.*$", "", t, flags=re.MULTILINE)                 # heading lines
    t = re.sub(r"^\s*(?:[-*+]|\d+[.)])\s+", "", t, flags=re.MULTILINE)      # list markers
    t = re.sub(r"[*`]+|(?<!\w)_+|_+(?!\w)", "", t)                  # emphasis, inline code
    t = re.sub(r"\s+", " ", t).strip()
    t = re.sub(r"\s+([.,;:!?])", r"\1", t)                          # space left before punctuation
    sentences = re.split(r"(?<=[.!?])\s+", t) if t else []
    return " ".join(sentences[:MAX_SENTENCES])


def is_audio(content_type: str | None, data: bytes | None) -> bool:
    """True only if the reply is labelled audio and its bytes start with an audio header."""
    if not content_type or not data:
        return False
    if not content_type.split(";")[0].strip().lower().startswith("audio/"):
        return False
    wav = data[:4] == b"RIFF" and data[8:12] == b"WAVE"
    id3 = data[:3] == b"ID3"
    mpeg_sync = len(data) >= 2 and data[0] == 0xFF and (data[1] & 0xE0) == 0xE0
    return wav or id3 or mpeg_sync
