"""The tool loop: the model asks, the program decides, the model answers from what it got back.

One `run` is one question. Each trip through the loop is one billed chat call, and a tool request
costs another call to deliver its result. The loop stops when the model answers without asking
for a tool, or after MAX_STEPS calls; then the answer is the program's sentence (spec §13.3 6).
"""
import json
import time

from .claims import check_answer
from .registry import TOOLS, run_tool

MAX_STEPS = 4
def cap_answer(steps: int) -> str:
    return f"I couldn't finish answering that in {steps} steps. Please try a simpler question."


CAP_ANSWER = cap_answer(MAX_STEPS)
CONFIRM_NOTE = "Kuany has to confirm before anything is sent."
EMPTY_ANSWER = "I couldn't put an answer together. Please ask again."
# Per-model decision (Week 5): MiMo returns nothing with hidden reasoning on; M3 keeps it on.
REASONING = {"xiaomi/mimo-v2.6-flash": {"enabled": False}}


def _send(client, model, messages, max_tokens):
    kwargs = {"model": model, "messages": messages, "tools": TOOLS, "max_tokens": max_tokens}
    if model in REASONING:
        kwargs["reasoning"] = REASONING[model]
    return client.chat.send(**kwargs)


def run(client, system: str, question: str, model: str, max_steps: int = MAX_STEPS,
        max_tokens: int = 1500) -> dict:
    """Returns {"answer", "trace", "stopped_by", "cost", "pending", "check", "model"}."""
    messages = [{"role": "system", "content": system}, {"role": "user", "content": question}]
    trace, pending, cost = [], [], 0.0
    for step in range(1, max_steps + 1):
        t0 = time.time()
        c = _send(client, model, messages, max_tokens)
        cost += getattr(c.usage, "cost", None) or 0.0
        msg = c.choices[0].message
        calls = msg.tool_calls or []
        if not calls:                                   # the model answered: done
            text = (msg.content or "").strip() or EMPTY_ANSWER
            if pending and "confirm" not in text.lower():
                text = f"{text} {CONFIRM_NOTE}"
            trace.append({"step": step, "answer": text, "finish": c.choices[0].finish_reason,
                          "seconds": round(time.time() - t0, 2)})
            return _result(text, trace, "answer", cost, pending, model)
        messages.append({"role": "assistant", "content": msg.content or "",
                         "tool_calls": [{"id": tc.id, "type": "function",
                                         "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                                        for tc in calls]})
        for tc in calls:
            result = run_tool(tc.function.name, tc.function.arguments)
            if "pending" in result:
                pending.append(result["pending"])
            trace.append({"step": step, "tool": tc.function.name, "arguments": tc.function.arguments,
                          "result": result, "seconds": round(time.time() - t0, 2)})
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps(result)})
    return _result(cap_answer(max_steps), trace, "cap", cost, pending, model)   # the program's answer, not the model's


def _result(answer, trace, stopped_by, cost, pending, model):
    return {"answer": answer, "trace": trace, "stopped_by": stopped_by, "cost": round(cost, 8),
            "pending": pending, "check": check_answer(answer, trace), "model": model}
