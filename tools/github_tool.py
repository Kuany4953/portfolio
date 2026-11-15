"""recent_commits: the last few commits of one of Kuany Kuany's public GitHub repositories (spec §13.3 4).

Only the Kuany4953 account. Everything that can go wrong comes back as a result the model can
read, never an exception: another owner, a malformed name, a repository that does not exist
(404), the rate limit (403/429), no network. No key is needed for public repositories (60
requests an hour per address); GITHUB_TOKEN is used if it is set.

    python3 -m tools.github_tool portfolio
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request

OWNER = "Kuany4953"
NAME = re.compile(r"[A-Za-z0-9_.-]+")


def _fetch(url: str, headers: dict):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.load(resp)


def recent_commits(repo: str, count: int = 5, fetch=None) -> dict:
    fetch = fetch or _fetch
    repo = (repo or "").strip()
    owner, _, name = repo.rpartition("/")
    if owner and owner.lower() != OWNER.lower():
        return {"error": f"only {OWNER}'s repositories are available, not {owner!r}"}
    if not NAME.fullmatch(name) or name in (".", "..") or "/" in owner:
        return {"error": f"repo must be a repository name or {OWNER}/name, got {repo!r}"}
    full = f"{OWNER}/{name}"
    count = max(1, min(int(count), 10))
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "portfolio-chatbot"}
    if os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    try:
        data = fetch(f"https://api.github.com/repos/{full}/commits?per_page={count}", headers)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {"error": f"no public repository named {full!r}", "repo": full, "found": False}
        if e.code in (403, 429):
            return {"error": "GitHub rate limit reached; try again in an hour"}
        if e.code == 409:                                   # GitHub's answer for an empty repository
            return {"repo": full, "found": True, "commits": []}
        return {"error": f"GitHub answered {e.code}"}
    except (urllib.error.URLError, TimeoutError, ValueError) as e:
        return {"error": f"could not reach GitHub: {e}"}
    return {"repo": full, "found": True,
            "commits": [{"sha": c["sha"][:7], "date": c["commit"]["author"]["date"][:10],
                         "message": c["commit"]["message"].splitlines()[0][:100]} for c in data[:count]]}


if __name__ == "__main__":
    print(json.dumps(recent_commits(sys.argv[1] if len(sys.argv) > 1 else "portfolio"), indent=1))
