"""No-key tests for what /api/voice accepts (spec.md §12.4 behavior 9).

Every refusal here happens before any billed call.
"""
import io
import wave

import pytest
from loop import MAX_BODY, MAX_COMPRESSED, MAX_WAV_SECONDS, Refused, check_request


def wav_bytes(seconds: float, rate: int = 8000) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(b"\x00\x00" * int(seconds * rate))
    return buf.getvalue()


def refused(ctype, body):
    with pytest.raises(Refused) as e:
        check_request(ctype, body)
    return e.value.status


def test_limits_are_the_spec_values():
    assert MAX_BODY == 4 * 1024 * 1024
    assert MAX_COMPRESSED == 512 * 1024
    assert MAX_WAV_SECONDS == 16


def test_ten_second_wav_is_accepted():
    assert check_request("audio/wav", wav_bytes(10)) == "wav"


def test_wav_over_sixteen_seconds_is_413():
    assert refused("audio/wav", wav_bytes(16.5)) == 413


def test_a_minute_of_wav_is_413():
    assert refused("audio/x-wav", wav_bytes(60)) == 413


def test_unreadable_wav_is_400():
    assert refused("audio/wav", b"RIFF not really a wav") == 400


def test_browser_webm_with_codecs_is_accepted():
    assert check_request("audio/webm;codecs=opus", b"\x1aE\xdf\xa3" + b"\x00" * 1000) == "webm"


def test_compressed_over_512_kb_is_413():
    assert refused("audio/webm", b"\x00" * (600 * 1024)) == 413


def test_body_over_4_mb_is_413():
    assert refused("audio/wav", b"\x00" * (MAX_BODY + 1)) == 413


@pytest.mark.parametrize("ctype", ["text/plain", "application/json", "", None, "audio/x-unknown"])
def test_unknown_type_is_415(ctype):
    assert refused(ctype, b"\x00" * 100) == 415


def test_empty_body_is_400():
    assert refused("audio/webm", b"") == 400


@pytest.mark.parametrize("ctype,fmt", [("audio/mpeg", "mp3"), ("audio/mp4", "m4a"), ("audio/ogg", "ogg"),
                                       ("AUDIO/WEBM", "webm")])
def test_known_types_map_to_formats(ctype, fmt):
    assert check_request(ctype, b"\x00" * 100) == fmt
