"""Claude Code Agent SDK `stream-json` -> enrichment events (compaction metrics, headless permission denials,
per-turn model finish reasons, run totals and terminal reason)."""
from __future__ import annotations
import json
from typing import Iterable

from harness_engine.model.events import (CaptureTier, DecisionSource, Event, EventType, Identity, INTERFACES, StopReason, Versions, new_event_id)
from .common import CHANNEL_STREAM, HARNESS, ts
from datetime import datetime, timezone

TERMINAL_TO_STOP = {"completed": StopReason.AGENT_DECLARED_COMPLETE, "max_turns": StopReason.MAX_TURNS, "error": StopReason.FATAL_ERROR,
                    "budget_exceeded": StopReason.BUDGET_EXHAUSTED, "interrupted": StopReason.HUMAN_STOP}


def _mk(etype, sid, native, attrs, when, correlation=None, status=None, agent=None):
    comp, counter = INTERFACES[etype]
    return Event(event_id=new_event_id(sid, native, json.dumps(correlation or {}, sort_keys=True), str(when)), type=etype, native_type=f"stream.{native}",
                 timestamp=when, identity=Identity(run_id=sid, session_id=sid, agent_instance_id=agent or "main", agent_definition=agent or "main"),
                 versions=Versions(harness=HARNESS), component=comp, counterpart=counter, correlation=correlation or {}, status=status, attrs=attrs,
                 capture_tier=CaptureTier.B, source_channel=CHANNEL_STREAM)


def parse_stream(lines: Iterable[str], base_time: datetime | None = None) -> tuple[list[Event], dict]:
    """The stream has no per-message timestamps; events are ordered by position and stamped base_time + index ms."""
    events: list[Event] = []; stats = {"records": 0, "mapped": 0}
    t0 = base_time or datetime.now(timezone.utc)
    i = 0
    for line in lines:
        line = line.strip()
        if not line: continue
        try: d = json.loads(line)
        except json.JSONDecodeError: continue
        i += 1; stats["records"] += 1
        sid = d.get("session_id", ""); when = t0.replace(microsecond=0) + __import__("datetime").timedelta(milliseconds=i)
        t, st = d.get("type"), d.get("subtype")
        if t == "system" and st == "compact_boundary":
            m = d.get("compact_metadata", {}); seg = m.get("preserved_segment", {}) or {}
            events.append(_mk(EventType.CONTEXT_COMPACT, sid, "compact_boundary",
                              {"trigger": m.get("trigger", "unknown"), "tokens_before": m.get("pre_tokens"), "tokens_after": m.get("post_tokens"),
                               "tokens_dropped": m.get("cumulative_dropped_tokens"), "duration_ms": m.get("duration_ms"),
                               "preserved_head_id": seg.get("head_uuid"), "preserved_anchor_id": seg.get("anchor_uuid"), "preserved_tail_id": seg.get("tail_uuid"),
                               "num_preserved_messages": len((m.get("preserved_messages") or {}).get("uuids", []) or [])}, when,
                              correlation={"boundary_uuid": d.get("uuid", "")})); stats["mapped"] += 1
        elif t == "system" and st == "permission_denied":
            events.append(_mk(EventType.PERMISSION_DENIED, sid, "permission_denied",
                              {"actor": "main", "resource": d.get("tool_name"), "action": "invoke", "decision": "denied", "source": DecisionSource.HEADLESS_DEFAULT,
                               "reason": d.get("reason") or "headless_no_prompt"}, when, correlation={"tool_call_id": d.get("tool_use_id", "")}, status="denied")); stats["mapped"] += 1
        elif t == "assistant":
            msg = d.get("message", {}); sr = msg.get("stop_reason")
            if sr:
                events.append(_mk(EventType.MODEL_RESPONSE, sid, "assistant", {"model": msg.get("model", ""), "message_id": msg.get("id"), "finish_reason": sr,
                                                                               "num_tool_calls": sum(1 for b in msg.get("content", []) if b.get("type") == "tool_use")}, when,
                                  correlation={"message_id": msg.get("id", "")}, agent=None)); stats["mapped"] += 1
        elif t == "result":
            u = d.get("usage", {}) or {}
            events.append(_mk(EventType.RUN_COMPLETED if not d.get("is_error") else EventType.RUN_FAILED, sid, "result",
                              {"stop_reason": TERMINAL_TO_STOP.get(d.get("terminal_reason"), StopReason.UNKNOWN), "total_turns": d.get("num_turns"), "duration_ms": d.get("duration_ms"),
                               "total_cost_usd": d.get("total_cost_usd"), "input_tokens": u.get("input_tokens"), "output_tokens": u.get("output_tokens"),
                               "cache_read_tokens": u.get("cache_read_input_tokens"), "cache_creation_tokens": u.get("cache_creation_input_tokens"),
                               "num_permission_denials": len(d.get("permission_denials", []) or []), "terminal_reason": d.get("terminal_reason")}, when,
                              status="ok" if not d.get("is_error") else "error")); stats["mapped"] += 1
    return events, stats
