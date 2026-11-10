"""Browser check of the voice page (the Week 5 way), adapted from examples/voice-loop/test_browser.py.

    set -a; . ../.env; set +a; python3 server.py &      # the server needs the key; the browser must not
    python3 -m pytest test_browser.py -v                # three billed calls, about ten seconds

Uploads a fixture clip through the page's file picker (a microphone can't be scripted
reliably), waits for the answer, then checks what the browser was allowed to see.
The last three assertions are the point. Whether the answer honestly says "not yet"
about Kubernetes is my judgment, recorded in CHECKS.md, not graded here.
Skipped when no server is running, so a plain pytest run never bills anything.
"""
import os
import urllib.request
from pathlib import Path

import pytest

URL = os.environ.get("VOICE_URL", "http://localhost:8000")
CLIP = Path(__file__).parent / "clips" / "course" / "clip-02.wav"   # "Have you ever deployed anything with Kubernetes?"


def server_up() -> bool:
    try:
        urllib.request.urlopen(URL, timeout=2)
        return True
    except OSError:
        return False


pytestmark = pytest.mark.skipif(not server_up(), reason=f"no server at {URL}; start voice/server.py first")


def test_voice_page_answers_and_the_key_never_reaches_the_browser():
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not os.environ.get("HEADED"))
        page = browser.new_page()
        requests = []
        page.on("request", lambda r: requests.append((r.url, r.headers.get("authorization"))))

        page.goto(URL)
        html = page.content()
        page.set_input_files("#file", str(CLIP))
        page.click("#send")
        page.wait_for_function("document.querySelector('#out').textContent.includes('Answer:')", timeout=120_000)
        out = page.inner_text("#out")
        has_audio = page.evaluate("!!document.querySelector('#player').src")
        browser.close()

    print("\n" + out)
    said, answer = out.split("Answer:")[0], out.split("Answer:")[1]
    assert "sk-or" not in html and "openrouter" not in html.lower()   # no key, no provider URL in the page
    assert said.startswith("You said:") and "kubernetes" in said.lower(), out   # transcript shown, name survived
    assert len(answer.split("[")[0].strip()) > 20, out                 # a real answer, not the fallback
    assert "speech failed" not in out, out
    assert has_audio                                                   # audio came back
    assert all(auth is None for _, auth in requests)                   # no Authorization header left the browser
    assert all("openrouter" not in url for url, _ in requests)         # the browser never called the provider
    assert any(url.endswith("/api/voice") for url, _ in requests)      # it called our server
