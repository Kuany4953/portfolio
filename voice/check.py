"""Transcript checker (spec.md §12.4, behaviors 1, 4, 5).

Code, not a model, compares a transcript with text a person wrote before the
model heard the clip. No network, no key.
"""
import re

TOLERANCE = 0.15


def words(text: str | None) -> list[str]:
    """Lowercase, drop punctuation, split on whitespace."""
    return re.sub(r"[^\w\s]", " ", (text or "").lower()).split()


def wer(expected: str, got: str | None) -> float:
    """Word error rate: (substitutions + deletions + insertions) / expected words."""
    ref, hyp = words(expected), words(got)
    if not ref:
        raise ValueError("expected text is empty; fix the answer key")
    # One row of the word-level edit-distance table at a time.
    prev = list(range(len(hyp) + 1))
    for i, r in enumerate(ref, 1):
        cur = [i]
        for j, h in enumerate(hyp, 1):
            cur.append(min(prev[j] + 1,               # deletion
                           cur[j - 1] + 1,            # insertion
                           prev[j - 1] + (r != h)))   # substitution or match
        prev = cur
    return prev[-1] / len(ref)


def _squash(text: str) -> str:
    """Lowercase and remove all whitespace, so spacing and case do not count."""
    return re.sub(r"\s+", "", text.lower())


def missing_words(must_survive: list[str], got: str | None) -> list[str]:
    """The named words that do not appear in the transcript, in the order given."""
    have = _squash(got or "")
    return [w for w in must_survive if _squash(w) not in have]


def check_clip(expected: str, got: str | None, must_survive: list[str],
               tolerance: float = TOLERANCE) -> dict:
    """Score one transcript. An empty transcript is a failed result, never an exception."""
    empty = not (got or "").strip()
    rate = 1.0 if empty else wer(expected, got)
    missing = missing_words(must_survive, got)
    return {"wer": rate, "missing": missing, "empty": empty,
            "passed": not empty and rate <= tolerance and not missing}
