"""The claim check (spec §13.3 8): plain code looking for things the answer names that no tool returned.

It flags commit SHAs, dates and my repository names that are not in the turn's tool results,
and a repository the tool said does not exist when the answer does not say so. It cannot judge
meaning: a looked-up repository described with things the commits never said passes. That limit
is tested and written down in tools/CHECKS.md.
"""
import json
import re
from pathlib import Path

REPOS = json.loads((Path(__file__).parent / "repos.json").read_text())
OWNER = "kuany4953"
SHA = re.compile(r"(?<![\w-])(?=[0-9a-f]*\d)(?=[0-9a-f]*[a-f])[0-9a-f]{7,40}(?![\w-])", re.I)
ISO = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
MONTHS = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
MONTH_DAY = re.compile(r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+(\d{1,2})\b", re.I)
NOT_FOUND = ("no public repository", "doesn't exist", "does not exist", "couldn't find", "could not find",
             "can't find", "cannot find", "not find", "no repository", "not found")


def _distinctive(name: str) -> bool:
    return bool(re.search(r"[-_.\d]", name))


def _named(name: str, low: str) -> bool:
    n = re.escape(name.lower())
    if re.search(rf"{OWNER}/{n}(?![\w-])", low):
        return True
    return _distinctive(name) and re.search(rf"(?<![\w/-]){n}(?![\w-])", low) is not None


def check_answer(answer: str, trace: list) -> dict:
    shas, dates, found, missing = set(), set(), set(), set()
    for s in trace:
        if s.get("tool") != "recent_commits":
            continue
        r = s.get("result") or {}
        short = (r.get("repo") or "").split("/")[-1].lower()
        if r.get("found"):
            found.add(short)
            for c in r.get("commits", []):
                shas.add(c["sha"].lower())
                dates.add(c["date"])
        elif r.get("found") is False and short:
            missing.add(short)
    low = answer.lower()
    month_days = {d[5:] for d in dates}
    unsupported = []
    for m in SHA.finditer(answer):
        if not any(m.group().lower().startswith(s) or s.startswith(m.group().lower()) for s in shas):
            unsupported.append(f"commit {m.group()!r} was not returned by a tool")
    for m in ISO.finditer(answer):
        if m.group() not in dates:
            unsupported.append(f"date {m.group()!r} was not returned by a tool")
    for m in MONTH_DAY.finditer(answer):
        mmdd = f"{MONTHS.index(m.group(1)[:3].lower()) + 1:02d}-{int(m.group(2)):02d}"
        if mmdd not in month_days:
            unsupported.append(f"date {m.group()!r} was not returned by a tool")
    for name in REPOS:
        key = name.lower()
        if key not in found and key not in missing and _named(name, low):
            unsupported.append(f"repository {name!r} named without a recent_commits result")
    for key in sorted(missing):
        if re.search(rf"(?<![\w-]){re.escape(key)}(?![\w-])", low) and not any(p in low for p in NOT_FOUND):
            unsupported.append(f"repository {key!r} was not found, but the answer does not say so")
    return {"supported": not unsupported, "unsupported": unsupported}
