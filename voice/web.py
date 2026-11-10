"""HTTP handler for /api/voice and /api/ask (spec.md §12.4 behaviors 8, 9, 10).

The same class serves both locally (voice/server.py) and on Vercel (api/voice.py,
api/ask.py). The key is read from the server's environment on each request and
never appears in a reply.
"""
import json
import os
import tempfile
from http.server import BaseHTTPRequestHandler
from pathlib import Path

from answer import answer
from loop import MAX_BODY, Refused, check_request, voice_turn
from speak import speak
from transcribe import transcribe

PAGE = Path(__file__).resolve().parent.parent / "index.html"
MAX_QUESTION = 2000


def client():
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise Refused(500, "the server has no API key configured")
    from openrouter import OpenRouter
    return OpenRouter(api_key=key)


def run_voice(c, audio: bytes, fmt: str) -> dict:
    def speak_fn(text):
        with tempfile.TemporaryDirectory() as d:     # Vercel can write only under /tmp
            out = Path(d) / "answer.mp3"
            info = speak(c, text, out)
            return out.read_bytes(), info["cost"]
    return voice_turn(audio, fmt,
                      lambda a, f: transcribe(c, a, f),
                      lambda q: answer(c, q, spoken=True),
                      speak_fn)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/api/"):
            return self.send_json(405, {"error": "POST only"})
        body = PAGE.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length") or 0)
            if length > MAX_BODY:                       # refuse before reading it
                raise Refused(413, f"recording over {MAX_BODY // (1024 * 1024)} MB")
            body = self.rfile.read(length)
            if self.path == "/api/voice":
                fmt = check_request(self.headers.get("Content-Type"), body)
                return self.send_json(200, run_voice(client(), body, fmt))
            if self.path == "/api/ask":
                question = body.decode("utf-8", "replace").strip()[:MAX_QUESTION]
                if not question:
                    raise Refused(400, "empty question")
                text, cost = answer(client(), question)
                return self.send_json(200, {"transcript": question, "answer": text, "audio": None,
                                            "costs": {"transcribe": 0, "answer": cost, "speak": 0,
                                                      "total": cost or 0}})
            self.send_json(404, {"error": "not found"})
        except Refused as e:
            self.send_json(e.status, {"error": str(e)})
        except Exception as e:  # noqa: BLE001 - the provider's message goes back, never the key
            self.log_error("voice: %s", e)
            self.send_json(502, {"error": str(e)[:300]})

    def send_json(self, status: int, data: dict):
        payload = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)
