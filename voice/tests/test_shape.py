"""No-key tests for the spoken shape and the audio check (spec.md §12.4, behaviors 3, 6)."""
import pytest
from check import words
from shape import is_audio, spoken

TYPED = """## Clasona

**Kuany** built an MCP-driven agent for *Vesoko*. It writes product descriptions
from seller data. See https://example.com/vesoko for more. The Meta Ads flow
was team work. He also did DevOps for Closet X."""


# --- spoken() ---------------------------------------------------------------

def test_markdown_is_stripped():
    out = spoken(TYPED)
    for mark in ("#", "*", "_", "`"):
        assert mark not in out


def test_urls_are_removed():
    assert "http" not in spoken(TYPED)
    assert "example.com" not in spoken(TYPED)


def test_markdown_link_keeps_its_text_and_drops_the_url():
    assert spoken("See [my repo](https://github.com/x/y) for code.") == "See my repo for code."


def test_list_markers_are_stripped():
    out = spoken("Skills:\n- Kubernetes.\n- Docker.\n1. CI/CD.")
    assert out == "Skills: Kubernetes. Docker. CI/CD."


def test_at_most_three_sentences():
    out = spoken("One. Two! Three? Four. Five.")
    assert out == "One. Two! Three?"


def test_short_answer_is_unchanged():
    assert spoken("My profile doesn't say.") == "My profile doesn't say."


def test_fenced_code_is_removed():
    assert spoken("Here is how.\n```\npip install x\n```\nThat is all.") == "Here is how. That is all."


def test_shaping_only_removes_never_adds():
    """Every word spoken appears in the typed answer, in the same order."""
    out, src = words(spoken(TYPED)), words(TYPED)
    it = iter(src)
    assert all(w in it for w in out)


def test_empty_answer_stays_empty():
    assert spoken("") == ""


# --- is_audio() --------------------------------------------------------------

WAV = b"RIFF\x24\x00\x00\x00WAVEfmt "
MP3_ID3 = b"ID3\x04\x00\x00\x00\x00\x00\x00"
MP3_SYNC = b"\xff\xfb\x90\x64\x00\x00"
JSON = b'{"error": {"message": "voice not found"}}'


@pytest.mark.parametrize("ctype,data", [("audio/wav", WAV), ("audio/mpeg", MP3_ID3),
                                        ("audio/mpeg", MP3_SYNC), ("audio/wav; codecs=1", WAV)])
def test_real_audio_is_accepted(ctype, data):
    assert is_audio(ctype, data)


def test_json_body_with_json_type_is_rejected():
    assert not is_audio("application/json", JSON)


def test_json_body_labelled_audio_is_rejected():
    assert not is_audio("audio/mpeg", JSON)


def test_audio_bytes_labelled_json_are_rejected():
    assert not is_audio("application/json", WAV)


@pytest.mark.parametrize("ctype,data", [(None, WAV), ("audio/wav", b""), ("audio/wav", None)])
def test_missing_type_or_body_is_rejected(ctype, data):
    assert not is_audio(ctype, data)


def test_raw_pcm_has_no_header_and_is_accepted():
    assert is_audio("audio/pcm;rate=24000;channels=1", b"\x01\x00\xfe\xff" * 100)


@pytest.mark.parametrize("body", [JSON, b"<html>error</html>"])
def test_text_labelled_pcm_is_rejected(body):
    assert not is_audio("audio/pcm;rate=24000", body)
