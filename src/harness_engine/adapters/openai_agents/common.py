"""Shared helpers for the OpenAI Agents SDK Tier A instrumentor.

Native records are kept as plain dicts so the mapping runs without `openai-agents` installed (tests replay the
captured fixture with the system interpreter). One raw record per line:
  {"channel": "meta",    "kind": "capture", "harness_version": "0.24.0", ...}
  {"channel": "tracing", "kind": "trace_start" | "trace_end" | "span_start" | "span_end", "ts": iso, "trace"|"span": <SDK export()>}
  {"channel": "hooks",   "kind": "<native callback name>", "ts": iso, "payload": {...}}   # content-free: digests only
"""
from __future__ import annotations
import hashlib, json
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Iterable

from harness_engine.model.events import Event, EventType, PayloadRef

HARNESS = "openai-agents"
CHANNEL_TRACING = "openai_agents.tracing"
CHANNEL_HOOKS = "openai_agents.hooks"
# The SDK's default_tool_error_function text (agents/tool.py, 0.24.0). Hooks see only this string on a failed tool.
SDK_DEFAULT_TOOL_ERROR = "An error occurred while running the tool. Please try again."


def sha(obj: Any) -> str:
    if isinstance(obj, (dict, list)):
        obj = json.dumps(obj, sort_keys=True, default=str)
    if isinstance(obj, str):
        obj = obj.encode()
    return hashlib.sha256(obj).hexdigest()


def canon(obj: Any) -> str:
    return obj if isinstance(obj, str) else json.dumps(obj, sort_keys=True, default=str)


def ref(obj: Any) -> PayloadRef:
    return PayloadRef.of(canon(obj))


def digest(obj: Any) -> dict:
    """Content-free stand-in recorded by the hook adapter: enough to build a PayloadRef, nothing more."""
    b = canon(obj).encode()
    return {"sha256": hashlib.sha256(b).hexdigest(), "size_bytes": len(b)}


def ref_from_digest(d: dict | None) -> PayloadRef | None:
    return PayloadRef(sha256=d["sha256"], size_bytes=d["size_bytes"]) if d else None


def ts(s: str | None) -> datetime:
    if not s:
        return datetime.now(timezone.utc)
    d = datetime.fromisoformat(s.replace("Z", "+00:00"))
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def harness_version() -> str | None:
    try:
        from importlib.metadata import version
        return version("openai-agents")
    except Exception:
        return None


def new_stats() -> dict:
    """records = native signals. mapped: produced >=1 v0.1 event. structural: consumed into v0.1 identity or
    correlation fields (or deduplicated against a sibling signal) without an event of its own. unmapped: kept as UNKNOWN."""
    return {"records": 0, "mapped": 0, "structural": 0, "unmapped": 0, "unmapped_names": {}, "structural_names": {}}


def count(stats: dict, outcome: str, name: str) -> None:
    stats["records"] += 1; stats[outcome] += 1
    if outcome in ("unmapped", "structural"):
        d = stats[f"{outcome}_names"]; d[name] = d.get(name, 0) + 1


# ---- cross-channel merge -------------------------------------------------------------------------------------
# Which correlation key identifies the same fact across the tracing and hook channels. Exact identifiers only:
# tool_call_id and response_id come from the model output; span ids are the SDK's own.
_FAMILY = {EventType.TOOL_FAILED: EventType.TOOL_COMPLETED}
MERGE_KEYS: dict[EventType, tuple[str, ...]] = {
    EventType.MODEL_REQUEST: ("turn_span_id",), EventType.MODEL_RESPONSE: ("response_id",),
    EventType.TOOL_REQUESTED: ("tool_call_id",), EventType.TOOL_STARTED: ("tool_call_id",),
    EventType.TOOL_COMPLETED: ("tool_call_id",), EventType.TOOL_FAILED: ("tool_call_id",),
    EventType.PERMISSION_REQUESTED: ("tool_call_id",), EventType.PERMISSION_GRANTED: ("tool_call_id",),
    EventType.PERMISSION_DENIED: ("tool_call_id",),
    EventType.AGENT_SPAWNED: ("child_agent_instance_id",), EventType.AGENT_RETURNED: ("child_agent_instance_id",),
    EventType.CONTEXT_COMPACT: ("compaction_item_id",), EventType.STOP: ("final_agent_instance_id",),
}
CHANNEL_PRIORITY = {CHANNEL_TRACING: 0, CHANNEL_HOOKS: 1}


def _key(e: Event):
    for k in MERGE_KEYS.get(e.type, ()):
        v = e.correlation.get(k)
        if v: return (_FAMILY.get(e.type, e.type), e.identity.run_id, k, v)
    return None


def merge(events: Iterable[Event]) -> tuple[list[Event], dict]:
    evs = list(events)
    groups: dict = defaultdict(list); passthrough: list[Event] = []
    for e in evs:
        k = _key(e)
        (groups[k] if k else passthrough).append(e)
    out: list[Event] = []; stats = {"input": len(evs), "merged_groups": 0, "merged_away": 0}
    for grp in groups.values():
        grp.sort(key=lambda e: (CHANNEL_PRIORITY.get(e.source_channel, 9), e.sequence or 0))
        base = grp[0].model_copy(deep=True)
        if len(grp) > 1:
            stats["merged_groups"] += 1; stats["merged_away"] += len(grp) - 1
            for other in grp[1:]:
                for ak, av in other.attrs.items():
                    if base.attrs.get(ak) in (None, "") and av not in (None, ""): base.attrs[ak] = av
                for ck, cv in other.correlation.items(): base.correlation.setdefault(ck, cv)
                for pk, pv in other.payload_refs.items(): base.payload_refs.setdefault(pk, pv)
                if base.status is None: base.status = other.status
                base.source_channel = "+".join(sorted(set(base.source_channel.split("+")) | set(other.source_channel.split("+"))))
        out.append(base)
    out.extend(passthrough)
    out.sort(key=lambda e: (e.timestamp, e.sequence if e.sequence is not None else 10**9))
    stats["output"] = len(out)
    return out, stats


def post(events: list[Event]) -> list[Event]:
    """Iteration numbering is native here (SDK turn spans carry `turn`). Events that fall outside a turn span (an
    approved tool executed on resume before the next turn opens) take the run's last observed turn. stop.verification_present
    from observed verify.* events, as for Claude Code."""
    last: dict[str, int] = {}; seen_verify: set[str] = set()
    for e in events:
        r = e.identity.run_id
        if e.identity.iteration is None: e.identity.iteration = last.get(r, 0)
        else: last[r] = e.identity.iteration
        if e.type in (EventType.VERIFY_PASSED, EventType.VERIFY_FAILED, EventType.VERIFY_EVIDENCE): seen_verify.add(r)
        if e.type == EventType.STOP: e.attrs["verification_present"] = r in seen_verify
    return events
