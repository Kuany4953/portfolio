"""No-key tests for the claim check (spec §13.3 8): what plain code flags, and what it lets through."""
from tools.claims import check_answer

FOUND = {"tool": "recent_commits", "arguments": '{"repo": "cpsc415-week05"}',
         "result": {"repo": "Kuany4953/cpsc415-week05", "found": True,
                    "commits": [{"sha": "b416914", "date": "2026-11-14", "message": "CHECKS: person-looking check"}]}}
MISSING = {"tool": "recent_commits", "arguments": '{"repo": "blockchain-voting"}',
           "result": {"error": "no public repository named 'Kuany4953/blockchain-voting'",
                      "repo": "Kuany4953/blockchain-voting", "found": False}}


def test_an_answer_built_from_the_result_is_supported():
    a = "In cpsc415-week05, commit b416914 on 2026-11-14 was the person-looking check (November 14)."
    assert check_answer(a, [FOUND]) == {"supported": True, "unsupported": []}


def test_a_sha_no_tool_returned_is_flagged():
    r = check_answer("The last commit was 9f3c2a1.", [FOUND])
    assert r["unsupported"] == ["commit '9f3c2a1' was not returned by a tool"]


def test_an_iso_date_no_tool_returned_is_flagged():
    r = check_answer("Kuany committed on 2026-11-13.", [FOUND])
    assert r["unsupported"] == ["date '2026-11-13' was not returned by a tool"]


def test_a_month_name_date_no_tool_returned_is_flagged():
    assert not check_answer("Yesterday, Nov 13, 2026, Kuany fixed a bug.", [FOUND])["supported"]
    assert not check_answer("On November 3 Kuany pushed.", [FOUND])["supported"]
    assert check_answer("On Nov. 14 Kuany pushed.", [FOUND])["supported"]


def test_ordinary_hex_looking_words_are_not_shas():
    # "acceded" is 7 letters of a-f; a SHA must contain a digit to count
    assert check_answer("The request was acceded to.", [])["supported"]


def test_a_distinctive_repo_named_without_a_lookup_is_flagged():
    r = check_answer("Kuany has been busy in assignment-4-solid.", [])
    assert r["unsupported"] == ["repository 'assignment-4-solid' named without a recent_commits result"]


def test_the_full_owner_form_is_always_matched():
    r = check_answer("See Kuany4953/portfolio for details.", [])
    assert r["unsupported"] == ["repository 'portfolio' named without a recent_commits result"]


def test_a_plain_word_repo_name_is_not_matched_bare():
    assert check_answer("This portfolio site has a chatbot.", [])["supported"]


def test_a_repo_the_tool_said_does_not_exist_described_anyway_is_flagged():
    r = check_answer("blockchain-voting is a voting app with a React front end.", [MISSING])
    assert r["unsupported"] == ["repository 'blockchain-voting' was not found, but the answer does not say so"]


def test_a_repo_the_tool_said_does_not_exist_reported_honestly_is_supported():
    a = "There's no public repository named blockchain-voting on Kuany's account."
    assert check_answer(a, [MISSING])["supported"]


def test_check_cannot_see_an_invented_description_of_a_real_repo():
    """Honest limit: a repository that was looked up, described with things the commits never said."""
    a = "cpsc415-week05 is a Kubernetes operator with 2,000 stars."
    assert check_answer(a, [FOUND])["supported"]
