"""No-key tests for the schemas, the decision (validate / run_tool) and the GitHub tool (spec §13.3 1-4, 7).

GitHub is never called: recent_commits takes a `fetch` function, and these tests pass fakes.
"""
import io
import json
import urllib.error

import pytest

from tools import github_tool, registry
from tools.github_tool import recent_commits
from tools.registry import SIDE_EFFECTS, TOOLS, run_tool, validate


# ---- the schema the model sees (behavior 1) ------------------------------------------------------
def test_two_schemas_with_name_description_and_json_schema_arguments():
    names = [t["function"]["name"] for t in TOOLS]
    assert names == ["recent_commits", "request_intro"]
    for t in TOOLS:
        f = t["function"]
        assert t["type"] == "function" and f["description"] and f["parameters"]["type"] == "object"
    rc = TOOLS[0]["function"]
    assert rc["parameters"]["required"] == ["repo"]
    assert rc["parameters"]["properties"]["count"] == {
        "type": "integer", "description": rc["parameters"]["properties"]["count"]["description"],
        "minimum": 1, "maximum": 10}
    assert "Call this before" in rc["description"] and "Kuany4953" in rc["description"]


def test_request_intro_is_the_side_effect():
    assert SIDE_EFFECTS == {"request_intro"}


# ---- validation in code (behavior 2) -------------------------------------------------------------
def test_wrong_argument_name_is_reported_as_missing_required():
    assert validate("recent_commits", {"name": "portfolio"}) == "missing required argument 'repo'"


def test_unexpected_argument():
    assert validate("recent_commits", {"repo": "portfolio", "branch": "main"}) == "unexpected argument 'branch'"


def test_wrong_type_string():
    assert validate("recent_commits", {"repo": 42}) == "argument 'repo' must be a string, got int"


def test_wrong_type_integer_and_bool_is_not_an_integer():
    assert validate("recent_commits", {"repo": "p", "count": "5"}) == "argument 'count' must be an integer, got str"
    assert validate("recent_commits", {"repo": "p", "count": True}) == "argument 'count' must be an integer, got bool"


def test_integer_out_of_range():
    assert validate("recent_commits", {"repo": "p", "count": 50}) == "argument 'count' must be between 1 and 10"


def test_arguments_must_be_an_object():
    assert validate("recent_commits", ["portfolio"]) == "arguments must be a JSON object"


def test_invalid_json_is_an_error_result_not_an_exception():
    r = run_tool("recent_commits", '{"repo": "portf')
    assert r["error"].startswith("arguments were not valid JSON")


def test_empty_arguments_string_means_no_arguments():
    assert run_tool("recent_commits", "") == {"error": "missing required argument 'repo'"}


# ---- unknown tool (behavior 3) -------------------------------------------------------------------
def test_unknown_tool_is_an_error_result_listing_the_tools():
    r = run_tool("get_resume", "{}")
    assert r == {"error": "unknown tool 'get_resume'; the tools are ['recent_commits', 'request_intro']"}


# ---- the side effect is held (behavior 7) --------------------------------------------------------
def test_side_effect_is_held_and_not_run(monkeypatch):
    sent = []
    monkeypatch.setitem(registry.FUNCTIONS, "request_intro", lambda **kw: sent.append(kw) or {"sent": True})
    r = run_tool("request_intro", '{"email": "r@x.com", "message": "coffee?"}')
    assert r["pending"] == {"tool": "request_intro", "arguments": {"email": "r@x.com", "message": "coffee?"}}
    assert "confirmation" in r["error"] and sent == []
    assert run_tool("request_intro", '{"email": "r@x.com", "message": "hi"}', allow_side_effects=True) == {"sent": True}
    assert sent == [{"email": "r@x.com", "message": "hi"}]


def test_bad_side_effect_call_is_an_error_before_it_is_pending():
    r = run_tool("request_intro", '{"email": "r@x.com"}')
    assert r == {"error": "missing required argument 'message'"}


# ---- the GitHub tool: only my repositories, errors as results (behavior 4) -----------------------
def fake_fetch(payload=None, status=None, calls=None):
    def fetch(url, headers):
        if calls is not None:
            calls.append(url)
        if status:
            raise urllib.error.HTTPError(url, status, "x", {}, io.BytesIO(b""))
        return payload
    return fetch


COMMITS = [{"sha": "abcdef1234567", "commit": {"author": {"date": "2026-11-10T08:16:45Z"},
                                               "message": "Voice: record skipped step 5a\n\nbody"}}]


def test_success_returns_short_sha_date_and_first_line():
    calls = []
    r = recent_commits("portfolio", 3, fetch=fake_fetch(COMMITS, calls=calls))
    assert r == {"repo": "Kuany4953/portfolio", "found": True,
                 "commits": [{"sha": "abcdef1", "date": "2026-11-10", "message": "Voice: record skipped step 5a"}]}
    assert calls == ["https://api.github.com/repos/Kuany4953/portfolio/commits?per_page=3"]


def test_owner_prefix_is_accepted_case_insensitively():
    r = recent_commits("kuany4953/portfolio", fetch=fake_fetch(COMMITS))
    assert r["found"] and r["repo"] == "Kuany4953/portfolio"


def test_another_owner_is_refused_without_calling_github():
    calls = []
    r = recent_commits("kousen/ai-integration-course", fetch=fake_fetch(COMMITS, calls=calls))
    assert "only Kuany4953" in r["error"] and calls == []


@pytest.mark.parametrize("bad", ["", "a b", "../etc", "x/y/z", "port?folio"])
def test_a_malformed_name_is_refused_without_calling_github(bad):
    calls = []
    assert "error" in recent_commits(bad, fetch=fake_fetch(COMMITS, calls=calls)) and calls == []


def test_404_is_a_not_found_result():
    r = recent_commits("blockchain-voting", fetch=fake_fetch(status=404))
    assert r == {"error": "no public repository named 'Kuany4953/blockchain-voting'",
                 "repo": "Kuany4953/blockchain-voting", "found": False}


@pytest.mark.parametrize("status", [403, 429])
def test_rate_limit_is_a_result(status):
    assert "rate limit" in recent_commits("portfolio", fetch=fake_fetch(status=status))["error"]


def test_network_failure_is_a_result():
    def down(url, headers):
        raise urllib.error.URLError("no route")
    assert "could not reach GitHub" in recent_commits("portfolio", fetch=down)["error"]


def test_run_tool_reaches_the_github_tool(monkeypatch):
    monkeypatch.setattr(github_tool, "_fetch", fake_fetch(COMMITS))
    r = run_tool("recent_commits", json.dumps({"repo": "portfolio", "count": 1}))
    assert r["found"] and r["commits"][0]["sha"] == "abcdef1"


def test_an_empty_repository_is_found_with_no_commits():
    """GitHub answers 409 for a repository with no commits. Added after the eval: softwaredesign310
    came back found with no commits, and this branch had no test."""
    assert recent_commits("softwaredesign310", fetch=fake_fetch(status=409)) == {
        "repo": "Kuany4953/softwaredesign310", "found": True, "commits": []}
