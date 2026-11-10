"""POST /api/ask on Vercel: the typed path, through the same answer function as /api/voice."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "voice"))

from web import Handler as handler  # noqa: F401 - Vercel looks for a class named `handler`
