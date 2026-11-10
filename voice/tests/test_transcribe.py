"""No-key tests for the transcriber (spec.md §12.2, §12.4 behaviors 1, 11).

A fake client stands in for OpenRouter, so nothing is billed. These prove the
request shape, one call per clip, and that a bad reply is reported, not raised.
"""
import json
from types import SimpleNamespace

import pytest
from transcribe import DEFAULT_MODEL, fmt_for, transcribe, transcribe_set

WAV = b"RIFF\x24\x00\x00\x00WAVEfmt "


class FakeSTT:
    def __init__(self, replies):
        self.replies, self.calls = list(replies), []

    def create_transcription(self, **kwargs):
        self.calls.append(kwargs)
        reply = self.replies.pop(0)
        if isinstance(reply, Exception):
            raise reply
        return reply


def fake_client(*replies):
    return SimpleNamespace(stt=FakeSTT(replies))


def reply(text, seconds=4.2, cost=0.00002):
    return SimpleNamespace(text=text, usage=SimpleNamespace(seconds=seconds, cost=cost))


def test_default_model_is_the_spec_model():
    assert DEFAULT_MODEL == "openai/whisper-large-v3-turbo"


@pytest.mark.parametrize("name,fmt", [("a.wav", "wav"), ("B.WAV", "wav"), ("c.webm", "webm"), ("d.mp3", "mp3")])
def test_format_comes_from_the_suffix(name, fmt):
    assert fmt_for(name) == fmt


def test_unknown_format_is_refused():
    with pytest.raises(ValueError):
        fmt_for("notes.txt")


def test_one_call_sends_base64_audio_and_records_the_bill():
    client = fake_client(reply("Hello Kuany"))
    r = transcribe(client, WAV, "wav", language="en")
    (call,) = client.stt.calls
    assert call["model"] == DEFAULT_MODEL
    assert call["input_audio"] == {"data": "UklGRiQAAABXQVZFZm10IA==", "format": "wav"}
    assert call["language"] == "en"
    assert r["text"] == "Hello Kuany"
    assert r["audio_seconds"] == 4.2 and r["cost"] == 0.00002
    assert "seconds" in r and r["model"] == DEFAULT_MODEL


def test_language_is_omitted_when_not_given():
    client = fake_client(reply("hi"))
    transcribe(client, WAV, "wav")
    assert "language" not in client.stt.calls[0]


def test_missing_usage_is_recorded_as_none_not_a_crash():
    client = fake_client(SimpleNamespace(text="hi", usage=None))
    r = transcribe(client, WAV, "wav")
    assert r["audio_seconds"] is None and r["cost"] is None


def write_set(tmp_path, entries):
    for e in entries:
        (tmp_path / e["file"]).write_bytes(WAV)
    path = tmp_path / "set.json"
    path.write_text(json.dumps(entries))
    return path


def test_set_makes_exactly_one_call_per_clip_and_checks_each(tmp_path):
    path = write_set(tmp_path, [
        {"file": "a.wav", "text": "My name is Kuany", "must_contain": ["Kuany"]},
        {"file": "b.wav", "text": "I took CPSC 415", "must_contain": ["CPSC 415"]},
    ])
    client = fake_client(reply("My name is Kwani"), reply("I took CPSC 415"))
    results = transcribe_set(client, path)
    assert len(client.stt.calls) == 2
    assert [r["file"] for r in results] == ["a.wav", "b.wav"]
    assert results[0]["check"]["missing"] == ["Kuany"] and not results[0]["check"]["passed"]
    assert results[1]["check"]["passed"]


def test_empty_transcript_in_a_set_is_a_failed_result_not_a_crash(tmp_path):
    path = write_set(tmp_path, [{"file": "a.wav", "text": "My name is Kuany", "must_contain": ["Kuany"]}])
    results = transcribe_set(fake_client(reply("")), path)
    assert results[0]["check"]["empty"] is True and results[0]["check"]["wer"] == 1.0


def test_a_failed_call_is_reported_and_the_set_continues(tmp_path):
    path = write_set(tmp_path, [
        {"file": "a.wav", "text": "one two three"},
        {"file": "b.wav", "text": "four five six"},
    ])
    client = fake_client(RuntimeError("400 unsupported format"), reply("four five six"))
    results = transcribe_set(client, path)
    assert len(client.stt.calls) == 2
    assert "400 unsupported format" in results[0]["error"]
    assert results[0]["check"]["empty"] is True
    assert results[1]["check"]["passed"]


def test_per_clip_tolerance_is_used(tmp_path):
    path = write_set(tmp_path, [{"file": "a.wav", "text": "one two three four five", "max_wer": 0.2,
                                 "note": "why it is looser"}])
    results = transcribe_set(fake_client(reply("one two three four fiver")), path)
    assert results[0]["check"]["wer"] == pytest.approx(0.2) and results[0]["check"]["passed"]


def test_language_flag_overrides_the_clip(tmp_path):
    path = write_set(tmp_path, [{"file": "a.wav", "text": "hola", "language": "es"}])
    client = fake_client(reply("hola"))
    transcribe_set(client, path, language="en")
    assert client.stt.calls[0]["language"] == "en"
