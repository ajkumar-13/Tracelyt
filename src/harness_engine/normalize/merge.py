"""Cross-channel merge. Events describing the same fact arrive from several channels (hooks, OTel logs, SDK stream).
They are merged on deterministic correlation keys; attributes are unioned with first-non-null wins by channel priority.
Nothing is inferred here: a merge requires an exact shared identifier (PLAN-11 P3)."""
from __future__ import annotations
from collections import defaultdict
from typing import Iterable

from harness_engine.model.events import Event, EventType

# Which (type, correlation key) pairs identify the same fact.
MERGE_KEYS: dict[EventType, tuple[str, ...]] = {
    EventType.TOOL_COMPLETED: ("tool_call_id",), EventType.TOOL_FAILED: ("tool_call_id",),
    EventType.TOOL_AUTHORIZED: ("tool_call_id",), EventType.TOOL_REJECTED: ("tool_call_id",),
    EventType.PERMISSION_DENIED: ("tool_call_id",),
    EventType.MODEL_RESPONSE: ("request_id", "message_id"),
    EventType.MODEL_REQUEST: ("request_body_id",),
    EventType.ITERATION_STARTED: ("turn_id",),
    EventType.CONTEXT_COMPACT: ("turn_id", "boundary_uuid"),
    EventType.AGENT_RETURNED: ("child_agent_instance_id", "child_agent_definition"),
    EventType.RUN_COMPLETED: (), EventType.RUN_FAILED: (),
}
CHANNEL_PRIORITY = {"claude_code.hooks": 0, "claude_code.otel_logs": 1, "claude_code.sdk_stream": 2}


def _key(e: Event):
    keys = MERGE_KEYS.get(e.type)
    if keys is None: return None
    if keys == (): return (e.type, e.identity.run_id)
    for k in keys:
        v = e.correlation.get(k)
        if v: return (e.type, e.identity.run_id, k, v)
    return None


def _link_model_events(events: list[Event]) -> None:
    """model.response from OTel api_response_body carries request_id and message_uuid; the SDK stream carries message_id.
    api_request carries request_id. Propagate message_id <-> request_id so both keys are present before merging."""
    rid_to_mid, mid_to_rid = {}, {}
    for e in events:
        if e.type == EventType.MODEL_RESPONSE:
            rid, mid = e.correlation.get("request_id"), e.correlation.get("message_id") or e.attrs.get("message_id")
            if rid and mid: rid_to_mid[rid] = mid; mid_to_rid[mid] = rid
    for e in events:
        if e.type == EventType.MODEL_RESPONSE:
            rid, mid = e.correlation.get("request_id"), e.correlation.get("message_id") or e.attrs.get("message_id")
            if rid and not mid and rid in rid_to_mid: e.correlation["message_id"] = rid_to_mid[rid]
            if mid and not rid and mid in mid_to_rid: e.correlation["request_id"] = mid_to_rid[mid]
            if mid: e.correlation["message_id"] = mid


def _link_agent_returns(events: list[Event]) -> None:
    """OTel subagent_completed has only the definition name; hooks have the instance id. Pair by definition and nearest time."""
    by_def = defaultdict(list)
    for e in events:
        if e.type == EventType.AGENT_RETURNED and e.correlation.get("child_agent_instance_id"):
            by_def[e.attrs.get("child_agent_definition") or e.identity.agent_definition].append(e)
    for e in events:
        if e.type == EventType.AGENT_RETURNED and not e.correlation.get("child_agent_instance_id"):
            cands = by_def.get(e.correlation.get("child_agent_definition"))
            if cands:
                best = min(cands, key=lambda c: abs((c.timestamp - e.timestamp).total_seconds()))
                if abs((best.timestamp - e.timestamp).total_seconds()) < 30:
                    e.correlation["child_agent_instance_id"] = best.correlation["child_agent_instance_id"]
                    e.attrs["child_agent_instance_id"] = best.correlation["child_agent_instance_id"]


def _link_compactions(events: list[Event]) -> None:
    """The SDK stream's compact_boundary has no turn id and no real timestamp; pair the n-th stream compaction with
    the n-th hook compaction in the same run (compactions are strictly ordered within a run)."""
    by_run_hook, by_run_stream = defaultdict(list), defaultdict(list)
    for e in events:
        if e.type != EventType.CONTEXT_COMPACT: continue
        (by_run_stream if e.source_channel == "claude_code.sdk_stream" else by_run_hook)[e.identity.run_id].append(e)
    for run, streams in by_run_stream.items():
        hooks = sorted(by_run_hook.get(run, []), key=lambda e: e.timestamp)
        for i, s in enumerate(sorted(streams, key=lambda e: e.timestamp)):
            if i < len(hooks):
                s.correlation["turn_id"] = hooks[i].correlation.get("turn_id", ""); hooks[i].correlation.setdefault("boundary_uuid", s.correlation.get("boundary_uuid", ""))
                s.timestamp = hooks[i].timestamp


def merge(events: Iterable[Event]) -> tuple[list[Event], dict]:
    evs = list(events)
    # The SDK stream has no timestamps; align its events to the hook/OTel time base by run.
    _link_model_events(evs); _link_agent_returns(evs); _link_compactions(evs)
    groups: dict = defaultdict(list); passthrough: list[Event] = []
    for e in evs:
        k = _key(e)
        (groups[k] if k else passthrough).append(e)
    merged: list[Event] = []; stats = {"input": len(evs), "merged_groups": 0, "merged_away": 0}
    for k, grp in groups.items():
        grp.sort(key=lambda e: CHANNEL_PRIORITY.get(e.source_channel, 9))
        base = grp[0].model_copy(deep=True)
        if len(grp) > 1:
            stats["merged_groups"] += 1; stats["merged_away"] += len(grp) - 1
            for other in grp[1:]:
                for ak, av in other.attrs.items():
                    if base.attrs.get(ak) in (None, "", 0) and av not in (None, ""): base.attrs[ak] = av
                for ck, cv in other.correlation.items(): base.correlation.setdefault(ck, cv)
                for pk, pv in other.payload_refs.items(): base.payload_refs.setdefault(pk, pv)
                base.source_channel = "+".join(sorted(set(base.source_channel.split("+")) | set(other.source_channel.split("+"))))
                if base.sequence is None and other.sequence is not None: base.sequence = other.sequence
                # hooks have exact timestamps; stream does not. Keep the earliest real timestamp.
                if other.source_channel != "claude_code.sdk_stream" and other.timestamp < base.timestamp: base.timestamp = other.timestamp
        merged.append(base)
    merged.extend(passthrough)
    merged.sort(key=lambda e: (e.timestamp, e.sequence if e.sequence is not None else 10**9))
    stats["output"] = len(merged)
    return merged, stats
