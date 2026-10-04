"""Verification adapter (PLAN-11 D-038): derives verify.* events from observed tool executions of known verifiers.
No harness emits first-class verification; a test runner invocation that completes is observed evidence of a verification
attempt, and its exit status is the outcome. Source channel is recorded so these events are distinguishable."""
from __future__ import annotations
import re
from harness_engine.model.events import CaptureTier, Component, Event, EventType, INTERFACES, StopReason, new_event_id

VERIFIER_PATTERNS = [
    (re.compile(r"\bpytest\b"), "pytest"), (re.compile(r"\bpython3? -m unittest\b"), "unittest"), (re.compile(r"\bnpm (test|run test)\b"), "npm_test"),
    (re.compile(r"\bgo test\b"), "go_test"), (re.compile(r"\bcargo test\b"), "cargo_test"), (re.compile(r"\bmake (test|check)\b"), "make_test"),
    (re.compile(r"\b(ruff|flake8|eslint|mypy|tsc)\b"), "lint_or_typecheck"), (re.compile(r"\b(npm run build|cargo build|go build|make)\b"), "build"),
]
CHANNEL = "verification_adapter"


def _verifier_for(command: str | None) -> str | None:
    if not command: return None
    for rx, name in VERIFIER_PATTERNS:
        if rx.search(command): return name
    return None


def derive_verification_events(events: list[Event], command_lookup: dict[str, str]) -> list[Event]:
    """command_lookup maps tool_call_id -> command text (from the hook capture; the event itself carries only hashes)."""
    out: list[Event] = []
    requested = {e.correlation.get("tool_call_id"): e for e in events if e.type == EventType.TOOL_REQUESTED}
    for e in events:
        if e.type not in (EventType.TOOL_COMPLETED, EventType.TOOL_FAILED, EventType.TOOL_REJECTED, EventType.PERMISSION_DENIED): continue
        tcid = e.correlation.get("tool_call_id"); req = requested.get(tcid)
        if not req or req.attrs.get("tool_name") != "Bash": continue
        verifier = _verifier_for(command_lookup.get(tcid))
        if not verifier: continue
        if e.type == EventType.TOOL_COMPLETED: etype, outcome = EventType.VERIFY_PASSED, "passed"
        elif e.type == EventType.TOOL_FAILED: etype, outcome = EventType.VERIFY_FAILED, "failed"
        else: etype, outcome = EventType.VERIFY_ABSTAINED, "abstained"   # verification was attempted but blocked
        comp, counter = INTERFACES[etype]
        out.append(Event(event_id=new_event_id(e.event_id, "verify"), type=etype, native_type=f"derived.{verifier}", timestamp=e.timestamp, sequence=e.sequence,
                         identity=e.identity.model_copy(), versions=e.versions, component=comp, counterpart=counter, parent_event_id=e.event_id,
                         correlation={"tool_call_id": tcid or ""}, status="ok" if outcome == "passed" else ("error" if outcome == "failed" else "denied"),
                         attrs={"claim": "tests_pass" if "test" in verifier or verifier == "pytest" else verifier, "evaluator": verifier, "outcome": outcome,
                                "evidence_hashes": [h for h in [e.attrs.get("output_hash")] if h], "exit_code": e.attrs.get("exit_code")},
                         capture_tier=e.capture_tier, source_channel=CHANNEL))
    return out


def command_lookup_from_hooks(hooks_jsonl_lines) -> dict[str, str]:
    import json
    out = {}
    for l in hooks_jsonl_lines:
        if not l.strip(): continue
        d = json.loads(l); p = d["payload"]
        if d["_hook"] == "PreToolUse" and p.get("tool_name") == "Bash":
            out[p.get("tool_use_id", "")] = (p.get("tool_input") or {}).get("command", "")
    return out
