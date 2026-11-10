"""Local server: the page plus /api/voice and /api/ask, the same handler Vercel runs.

    set -a; . ../.env; set +a        # the key, from the git-ignored .env
    python3 server.py                # then open http://localhost:8000
"""
import os
import sys
from http.server import ThreadingHTTPServer

from web import Handler

if __name__ == "__main__":
    if not os.environ.get("OPENROUTER_API_KEY"):
        sys.exit("OPENROUTER_API_KEY is not set; load it from .env first.")
    port = int(os.environ.get("PORT", "8000"))
    print(f"http://localhost:{port}", flush=True)
    try:
        ThreadingHTTPServer(("localhost", port), Handler).serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
