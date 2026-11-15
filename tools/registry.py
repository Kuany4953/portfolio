"""The tools the chatbot may ask for, and the code that decides whether to run them (spec §13.3 1-3, 7).

A tool has two halves: the schema (what the model sees, sent as `tools` with every request)
and the function (what our program runs, after checking the arguments itself). The model never
runs anything. `run_tool` never raises on a bad request: the problem goes back to the model as
the tool's result.
"""
import json

from . import github_tool

TOOLS = [
    {"type": "function", "function": {
        "name": "recent_commits",
        "description": "The most recent commits in one of Kuany Kuany's public GitHub repositories "
                       "(owner Kuany4953). Call this before saying anything about what Kuany has worked on "
                       "lately or about any repository. Only Kuany4953's repositories are available.",
        "parameters": {"type": "object",
                       "properties": {
                           "repo": {"type": "string",
                                    "description": "A repository name, for example portfolio, or Kuany4953/name"},
                           "count": {"type": "integer", "description": "How many commits, 1 to 10 (default 5)",
                                     "minimum": 1, "maximum": 10}},
                       "required": ["repo"]}}},
    {"type": "function", "function": {
        "name": "request_intro",
        "description": "Ask to introduce a visitor to Kuany. Only when the visitor explicitly asks to be "
                       "introduced and gives an email address. The request is held until Kuany confirms.",
        "parameters": {"type": "object",
                       "properties": {
                           "email": {"type": "string", "description": "The visitor's email address"},
                           "message": {"type": "string", "description": "What the visitor wants"}},
                       "required": ["email", "message"]}}},
]
SIDE_EFFECTS = {"request_intro"}          # never run on the model's request alone


def request_intro(email: str, message: str) -> dict:
    """The side effect. Nothing calls this with allow_side_effects=True this week: a real outbox
    needs a confirm step (spec §13.5)."""
    raise NotImplementedError("introductions are held until a confirm step exists")


FUNCTIONS = {"recent_commits": lambda **kw: github_tool.recent_commits(**kw), "request_intro": request_intro}
_TYPES = {"string": str, "integer": int}


def validate(name: str, args) -> str | None:
    """An error message, or None if the call is well formed. Plain code, no model."""
    schema = next((t["function"]["parameters"] for t in TOOLS if t["function"]["name"] == name), None)
    if schema is None:
        return f"unknown tool {name!r}; the tools are {sorted(FUNCTIONS)}"
    if not isinstance(args, dict):
        return "arguments must be a JSON object"
    for req in schema.get("required", []):
        if req not in args:
            return f"missing required argument {req!r}"
    for key, val in args.items():
        spec = schema["properties"].get(key)
        if spec is None:
            return f"unexpected argument {key!r}"
        want = _TYPES[spec["type"]]
        if not isinstance(val, want) or isinstance(val, bool):
            return f"argument {key!r} must be {'an' if spec['type'] == 'integer' else 'a'} {spec['type']}, got {type(val).__name__}"
        if "minimum" in spec and not spec["minimum"] <= val <= spec["maximum"]:
            return f"argument {key!r} must be between {spec['minimum']} and {spec['maximum']}"
    return None


def run_tool(name: str, arguments: str | dict, allow_side_effects: bool = False) -> dict:
    """What the loop calls for every tool request. Arguments arrive as a JSON string."""
    if isinstance(arguments, str):
        try:
            args = json.loads(arguments or "{}")
        except json.JSONDecodeError as e:
            return {"error": f"arguments were not valid JSON: {e.msg}"}
    else:
        args = arguments
    problem = validate(name, args)
    if problem:
        return {"error": problem}
    if name in SIDE_EFFECTS and not allow_side_effects:
        return {"error": f"{name} has a side effect and needs Kuany's confirmation first",
                "pending": {"tool": name, "arguments": args}}
    try:
        return FUNCTIONS[name](**args)
    except Exception as e:  # noqa: BLE001 - a tool that breaks is a result the model can read, not a crash
        return {"error": f"{name} failed: {e}"}
