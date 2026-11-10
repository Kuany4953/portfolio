"""No-key tests for the speaker (spec.md §12.3, §12.4 behavior 3).

A fake client stands in for OpenRouter, so nothing is billed.
"""
import wave
from types import SimpleNamespace

import pytest
from speak import COMPARISON, DEFAULT_MODEL, DEFAULT_VOICE, NotAudio, speak

PCM = b"\x01\x00\xfe\xff" * 2400          # 0.1 s of 24 kHz mono 16-bit
MP3 = b"ID3\x04\x00\x00\x00\x00\x00\x00" + b"\x00" * 50
JSON = b'{"error":{"message":"voice not found"}}'
PRICES = {DEFAULT_MODEL: 0.00002, "elevenlabs/eleven-v4-turbo": 0.00005}


class FakeReply:
    def __init__(self, data, ctype, gen_id="gen-123"):
        self._data = data
        self.headers = {"content-type": ctype, **({"x-generation-id": gen_id} if gen_id else {})}

    def read(self):
        return self._data


class FakeTTS:
    def __init__(self, reply):
        self.reply, self.calls = reply, []

    def create_speech(self, **kwargs):
        self.calls.append(kwargs)
        return self.reply


class FakeGenerations:
    def __init__(self, cost):
        self.cost = cost

    def get_generation(self, id):
        if isinstance(self.cost, Exception):
            raise self.cost
        return SimpleNamespace(data=SimpleNamespace(total_cost=self.cost))


NOT_YET = RuntimeError("not found yet")      # the generation record usually lags about a minute


def fake_client(reply, billed=NOT_YET):
    return SimpleNamespace(tts=FakeTTS(reply), generations=FakeGenerations(billed))


def test_defaults_are_the_spec_models():
    assert DEFAULT_MODEL == "microsoft/mai-voice-2.1-flash"
    assert DEFAULT_VOICE == "en-IN-Priya:MAI-Voice-2.1-Flash"
    assert COMPARISON == ("elevenlabs/eleven-v4-turbo", "george")


def test_wav_out_asks_for_pcm_and_writes_a_valid_wav(tmp_path):
    out = tmp_path / "a.wav"
    client = fake_client(FakeReply(PCM, "audio/pcm;rate=24000;channels=1"))
    info = speak(client, "Hello from CPSC 415.", out, prices=PRICES)
    assert client.tts.calls == [{"model": DEFAULT_MODEL, "input": "Hello from CPSC 415.",
                                 "voice": DEFAULT_VOICE, "response_format": "pcm"}]
    with wave.open(str(out)) as w:
        assert (w.getframerate(), w.getnchannels(), w.getsampwidth()) == (24000, 1, 2)
        assert w.readframes(w.getnframes()) == PCM
    assert info["bytes"] == len(PCM)


def test_mp3_out_writes_the_bytes(tmp_path):
    out = tmp_path / "a.mp3"
    client = fake_client(FakeReply(MP3, "audio/mpeg"))
    speak(client, "Hi.", out, prices=PRICES)
    assert client.tts.calls[0]["response_format"] == "mp3"
    assert out.read_bytes() == MP3


def test_records_chars_bytes_seconds_model_voice(tmp_path):
    text = "Kuany built an agent for Vesoko."
    info = speak(fake_client(FakeReply(MP3, "audio/mpeg")), text, tmp_path / "a.mp3",
                 model="elevenlabs/eleven-v4-turbo", voice="george", prices=PRICES)
    assert info["chars"] == len(text)
    assert info["bytes"] == len(MP3)
    assert info["model"] == "elevenlabs/eleven-v4-turbo" and info["voice"] == "george"
    assert isinstance(info["seconds"], float)


def test_json_reply_raises_and_nothing_is_saved(tmp_path):
    out = tmp_path / "a.wav"
    with pytest.raises(NotAudio, match="voice not found"):
        speak(fake_client(FakeReply(JSON, "application/json")), "Hi.", out, prices=PRICES)
    assert not out.exists()


def test_json_body_labelled_audio_raises_and_nothing_is_saved(tmp_path):
    out = tmp_path / "a.mp3"
    with pytest.raises(NotAudio):
        speak(fake_client(FakeReply(JSON, "audio/mpeg")), "Hi.", out, prices=PRICES)
    assert not out.exists()


def test_cost_is_estimated_from_price_per_character_when_no_record(tmp_path):
    info = speak(fake_client(FakeReply(MP3, "audio/mpeg")), "x" * 100, tmp_path / "a.mp3", prices=PRICES)
    assert info["cost"] == pytest.approx(0.002)
    assert info["cost_is_estimate"] is True


def test_billed_cost_from_the_generation_record_wins(tmp_path):
    client = fake_client(FakeReply(MP3, "audio/mpeg"), billed=0.0017)
    info = speak(client, "x" * 100, tmp_path / "a.mp3", prices=PRICES)
    assert info["cost"] == 0.0017 and info["cost_is_estimate"] is False
    assert info["generation_id"] == "gen-123"


def test_unknown_price_is_none_not_a_crash(tmp_path):
    info = speak(fake_client(FakeReply(MP3, "audio/mpeg"), billed=None), "Hi.", tmp_path / "a.mp3",
                 model="someone/else", voice="v", prices=PRICES)
    assert info["cost"] is None and info["cost_is_estimate"] is True
