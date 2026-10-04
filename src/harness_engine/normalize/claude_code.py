"""Normalize a captured Claude Code run directory into a v0.1 event list.

Expected layout (as produced by the Proof A capture harness):
  <dir>/hooks.jsonl              hook stdin dumps  (optional)
  <dir>/otlp/logs-*.json          OTLP/HTTP JSON log batches (optional)
  <dir>/stream*.jsonl            Agent SDK stream-json (optional)
"""
from __future__ import annotations
import glob, json, os
from datetime import timezone

from harness_engine.adapters.claude_code.hooks import parse_hooks
from harness_engine.adapters.claude_code.otel_logs import parse_otlp_logs
from harness_engine.adapters.claude_code.stream import parse_stream
from harness_engine.model.events import Event, EventType
from .merge import merge


def _post(events: list[Event]) -> list[Event]:
    """Derived-but-observed fields: iteration numbering per agent instance (each model.response opens a new iteration,
    the tool activity it triggers belongs to it), and stop.verification_present from observed verify.* events. No inference."""
    counters: dict[tuple, int] = {}
    seen_resp: set[str] = set()
    # A tool request is logged by the hook before the OTel record of the model response that produced it is flushed,
    # so requests with no decision/result yet are carried into the iteration opened by the next model.response.
    pending: dict[tuple, list[Event]] = {}
    for e in events:
        k = (e.identity.run_id, e.identity.agent_instance_id)
        if e.type == EventType.MODEL_RESPONSE and e.correlation.get("request_id") and e.correlation["request_id"] not in seen_resp:
            seen_resp.add(e.correlation["request_id"]); counters[k] = counters.get(k, 0) + 1
            e.identity.iteration = counters[k]
            for pe in pending.get(k, []): pe.identity.iteration = counters[k]
            pending[k] = []
        elif e.type == EventType.MODEL_REQUEST:
            e.identity.iteration = counters.get(k, 0) + 1
        elif e.type in (EventType.RUN_STARTED, EventType.RUN_RESUMED):
            e.identity.iteration = 0
        else:
            e.identity.iteration = counters.get(k, 0)
            if e.type == EventType.TOOL_REQUESTED: pending.setdefault(k, []).append(e)
            elif e.type in (EventType.TOOL_AUTHORIZED, EventType.TOOL_REJECTED, EventType.PERMISSION_DENIED, EventType.TOOL_COMPLETED, EventType.TOOL_FAILED):
                tc = e.correlation.get("tool_call_id")
                pending[k] = [pe for pe in pending.get(k, []) if pe.correlation.get("tool_call_id") != tc]
    seen_verify = set()
    for e in events:
        if e.type in (EventType.VERIFY_PASSED, EventType.VERIFY_FAILED, EventType.VERIFY_EVIDENCE): seen_verify.add(e.identity.run_id)
        if e.type == EventType.STOP: e.attrs["verification_present"] = e.identity.run_id in seen_verify
    return events


def normalize_dir(d: str, session_id: str | None = None, keep_pii: bool = False, body_path_rewrite=None, path_rewrite=None, with_verification: bool = True) -> tuple[list[Event], dict]:
    all_events: list[Event] = []; stats: dict = {}
    hp = os.path.join(d, "hooks.jsonl")
    if os.path.exists(hp):
        lines = [l for l in open(hp) if l.strip()]
        if session_id: lines = [l for l in lines if json.loads(l)["payload"].get("session_id") == session_id]
        ev, st = parse_hooks(lines, path_rewrite=path_rewrite); all_events += ev; stats["hooks"] = st
        hook_lines = lines
    batches = []
    for f in sorted(glob.glob(os.path.join(d, "otlp", "*logs-*.json"))):
        try: batches.append(json.load(open(f)))
        except Exception: pass
    if batches:
        ev, st = parse_otlp_logs(batches, keep_pii=keep_pii, body_path_rewrite=body_path_rewrite)
        if session_id: ev = [e for e in ev if e.identity.run_id == session_id]
        all_events += ev; stats["otel_logs"] = st
    base = min((e.timestamp for e in all_events), default=None)
    for f in sorted(glob.glob(os.path.join(d, "stream*.jsonl"))):
        ev, st = parse_stream(open(f), base_time=base)
        if session_id: ev = [e for e in ev if e.identity.run_id == session_id]
        all_events += ev; stats.setdefault("stream", {"records": 0, "mapped": 0})
        stats["stream"]["records"] += st["records"]; stats["stream"]["mapped"] += st["mapped"]
    merged, mstats = merge(all_events); stats["merge"] = mstats
    if with_verification and os.path.exists(hp):
        from .verification import derive_verification_events, command_lookup_from_hooks
        vevents = derive_verification_events(merged, command_lookup_from_hooks(hook_lines))
        merged = sorted(merged + vevents, key=lambda e: (e.timestamp, e.sequence if e.sequence is not None else 10**9))
        stats["verification_events"] = len(vevents)
    merged = _post(merged)
    # Proof B metric: share of native records that fall outside v0.1 (preserved as UNKNOWN).
    total = sum(s.get("records", 0) for k, s in stats.items() if k in ("hooks", "otel_logs"))
    unm = sum(s.get("unmapped", 0) for k, s in stats.items() if k in ("hooks", "otel_logs"))
    stats["v01_exception_rate"] = (unm / total) if total else 0.0
    stats["v01_exception_rate_excluding_hook_domain"] = None
    hookdom = sum(v for k, s in stats.items() if k in ("hooks", "otel_logs") for n, v in s.get("unmapped_names", {}).items()
                  if n in ("hook_registered", "hook_execution_start", "hook_execution_complete", "managed_settings_resolved", "plugin_loaded"))
    if total: stats["v01_exception_rate_excluding_hook_domain"] = (unm - hookdom) / total
    return merged, stats
