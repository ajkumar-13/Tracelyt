"""Deterministic detectors D1-D10 (SPEC-03 v0.1). Every detector returns Findings with evidence event ids; nothing here
is probabilistic. Each detector carries a version so precision/recall can be tracked per version (PLAN-11 P6)."""
from __future__ import annotations
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Callable

from harness_engine.model.events import Component, Event, EventType


@dataclass
class Finding:
    detector_id: str; version: str; run_id: str; severity: str; confidence: float; component: Component
    affected_event_ids: list[str] = field(default_factory=list); evidence: dict = field(default_factory=dict); summary: str = ""


def _tool_chain(events: list[Event]):
    req = {e.correlation.get("tool_call_id"): e for e in events if e.type == EventType.TOOL_REQUESTED}
    done = {e.correlation.get("tool_call_id"): e for e in events if e.type in (EventType.TOOL_COMPLETED, EventType.TOOL_FAILED)}
    blocked = {e.correlation.get("tool_call_id"): e for e in events if e.type in (EventType.TOOL_REJECTED, EventType.PERMISSION_DENIED)}
    return req, done, blocked


def _artifact_effect(e: Event) -> bool:
    return bool(e.attrs.get("files_created") or e.attrs.get("files_modified") or e.attrs.get("lines_added"))


def d1_doom_loop(events: list[Event], min_repeats: int = 3) -> list[Finding]:
    """Repeated byte-identical tool request without a successful result or artifact effect in between."""
    req, done, blocked = _tool_chain(events)
    by_hash: dict[str, list[Event]] = defaultdict(list)
    for e in sorted(req.values(), key=lambda x: x.timestamp): by_hash[e.attrs.get("input_hash")].append(e)
    out = []
    for h, reqs in by_hash.items():
        if len(reqs) < min_repeats: continue
        results = [done.get(r.correlation["tool_call_id"]) for r in reqs]
        progressed = any(r is not None and r.type == EventType.TOOL_COMPLETED and (_artifact_effect(r) or reqs[0].attrs.get("side_effect_class") == "read_only") for r in results)
        failures = sum(1 for r in results if r is None or r.type == EventType.TOOL_FAILED)
        if failures >= min_repeats - 1 and not progressed:
            out.append(Finding("D1", "0.1.0", reqs[0].identity.run_id, "high", 0.95, Component.LOOP, [r.event_id for r in reqs],
                               {"tool_name": reqs[0].attrs.get("tool_name"), "repeats": len(reqs), "failures": failures, "input_hash": h},
                               f"{len(reqs)} identical {reqs[0].attrs.get('tool_name')} calls, {failures} failed, no state change"))
    return out


def d3_retry_storm(events: list[Event], min_consecutive: int = 3) -> list[Finding]:
    req, done, _ = _tool_chain(events)
    seq = sorted((e for e in done.values()), key=lambda x: x.timestamp)
    out = []; streak: list[Event] = []
    for e in seq + [None]:
        if e is not None and e.type == EventType.TOOL_FAILED and (not streak or streak[-1].attrs.get("tool_name") == e.attrs.get("tool_name")):
            streak.append(e); continue
        if len(streak) >= min_consecutive:
            out.append(Finding("D3", "0.1.0", streak[0].identity.run_id, "high", 0.9, Component.LOOP, [x.event_id for x in streak],
                               {"tool_name": streak[0].attrs.get("tool_name"), "consecutive_failures": len(streak)}, f"{len(streak)} consecutive {streak[0].attrs.get('tool_name')} failures"))
        streak = [e] if (e is not None and e.type == EventType.TOOL_FAILED) else []
    return out


def d4_no_progress(events: list[Event], min_iterations: int = 4) -> list[Finding]:
    """Iterations with tool activity but no artifact effect, no verification pass, and at least one failure."""
    its = defaultdict(list)
    for e in events:
        if e.identity.iteration is not None: its[(e.identity.agent_instance_id, e.identity.iteration)].append(e)
    out = []
    for inst in {k[0] for k in its}:
        keys = sorted(k for k in its if k[0] == inst and k[1] > 0)
        window: list = []
        for k in keys:
            evs = its[k]
            had_tool = any(e.type == EventType.TOOL_REQUESTED for e in evs)
            progress = any(_artifact_effect(e) for e in evs) or any(e.type == EventType.VERIFY_PASSED for e in evs)
            failed = any(e.type in (EventType.TOOL_FAILED, EventType.TOOL_REJECTED, EventType.PERMISSION_DENIED) for e in evs)
            if had_tool and not progress and failed: window.append(k)
            else: window = []
            if len(window) >= min_iterations:
                ids = [e.event_id for kk in window for e in its[kk]]
                out.append(Finding("D4", "0.1.0", evs[0].identity.run_id, "high", 0.85, Component.LOOP, ids, {"agent_instance": inst, "iterations": [k[1] for k in window]},
                                   f"{len(window)} consecutive iterations with tool failures and no artifact or verification progress"))
                window = []
    return out


def d5_budget_spiral(events: list[Event], min_iterations: int = 4) -> list[Finding]:
    """Cost accrues across iterations while recent tool outcomes are mostly failures."""
    by_it = defaultdict(lambda: {"cost": 0.0, "fail": 0, "ok": 0})
    for e in events:
        it = e.identity.iteration
        if it is None: continue
        if e.type == EventType.MODEL_RESPONSE: by_it[it]["cost"] += e.attrs.get("cost_usd") or 0.0
        if e.type == EventType.TOOL_FAILED: by_it[it]["fail"] += 1
        if e.type == EventType.TOOL_COMPLETED: by_it[it]["ok"] += 1
    its = sorted(k for k in by_it if k > 0)
    if len(its) < min_iterations: return []
    tail = its[-min_iterations:]
    fails = sum(by_it[i]["fail"] for i in tail); oks = sum(by_it[i]["ok"] for i in tail); cost = sum(by_it[i]["cost"] for i in tail)
    if fails >= 3 and oks == 0 and cost > 0:
        return [Finding("D5", "0.1.0", events[0].identity.run_id, "medium", 0.8, Component.BUDGET, [], {"tail_iterations": tail, "tail_cost_usd": round(cost, 5), "tail_failures": fails},
                        f"${cost:.4f} spent over {len(tail)} iterations with {fails} failures and no success")]
    return []


def d6_verification_bypass(events: list[Event]) -> list[Finding]:
    """Run ended with an agent-declared completion and no passed verification. Severity high when verification was attempted and blocked."""
    stops = [e for e in events if e.type == EventType.STOP and e.attrs.get("declared_by") == "agent"]
    if not stops: return []
    passed = [e for e in events if e.type == EventType.VERIFY_PASSED]
    if passed: return []
    blocked = [e for e in events if e.type == EventType.VERIFY_ABSTAINED]
    failed = [e for e in events if e.type == EventType.VERIFY_FAILED]
    sev = "high" if (blocked or failed) else "medium"
    return [Finding("D6", "0.1.0", stops[-1].identity.run_id, sev, 0.9 if (blocked or failed) else 0.7, Component.VERIFICATION, [stops[-1].event_id] + [e.event_id for e in blocked + failed],
                    {"verification_attempted": bool(blocked or failed), "blocked": len(blocked), "failed": len(failed)},
                    "completion declared without a passed verification" + (" (verification attempted but blocked)" if blocked else ""))]


def d7_permission_storm(events: list[Event], min_denials: int = 2) -> list[Finding]:
    den = [e for e in events if e.type in (EventType.PERMISSION_DENIED, EventType.TOOL_REJECTED)]
    by_res = defaultdict(list); seen = set()
    for e in sorted(den, key=lambda x: x.timestamp):
        key = e.correlation.get("tool_call_id") or e.event_id
        if key in seen: continue   # the same denial is reported by the stream (permission_denied) and OTel (tool_decision reject)
        seen.add(key); by_res[e.attrs.get("resource") or e.attrs.get("tool_name")].append(e)
    return [Finding("D7", "0.1.0", es[0].identity.run_id, "medium", 0.9, Component.PERMISSION, [e.event_id for e in es], {"resource": r, "denials": len(es)}, f"{len(es)} denials for {r}")
            for r, es in by_res.items() if len(es) >= min_denials]


def d8_context_explosion(events: list[Event], growth: float = 1.5, window: int = 3) -> list[Finding]:
    resp = sorted((e for e in events if e.type == EventType.MODEL_RESPONSE and e.identity.agent_instance_id == "main" and e.attrs.get("input_tokens") is not None), key=lambda e: e.timestamp)
    ctx = [(e.attrs.get("input_tokens") or 0) + (e.attrs.get("cache_read_tokens") or 0) + (e.attrs.get("cache_creation_tokens") or 0) for e in resp]
    out = []
    for i in range(window, len(ctx)):
        if ctx[i - window] and ctx[i] / ctx[i - window] >= growth:
            # growth without artifact effect in the same span
            span = [e for e in events if resp[i - window].timestamp <= e.timestamp <= resp[i].timestamp]
            if not any(_artifact_effect(e) for e in span) and not any(e.type == EventType.VERIFY_PASSED for e in span):
                out.append(Finding("D8", "0.1.0", resp[i].identity.run_id, "medium", 0.75, Component.CONTEXT_BUILDER, [resp[i - window].event_id, resp[i].event_id],
                                   {"context_tokens_from": ctx[i - window], "context_tokens_to": ctx[i]}, f"context grew {ctx[i-window]}->{ctx[i]} tokens with no progress")); break
    return out


def d9_repeated_retrieval(events: list[Event], min_reads: int = 3) -> list[Finding]:
    reads = defaultdict(list); writes = set()
    for e in sorted((x for x in events if x.type == EventType.TOOL_REQUESTED), key=lambda x: x.timestamp):
        fp = e.attrs.get("file_path_hash")
        if not fp: continue
        if e.attrs.get("tool_name") in ("Read",): reads[fp].append(e)
        elif e.attrs.get("tool_name") in ("Write", "Edit"): writes.add(fp); reads[fp] = []
    return [Finding("D9", "0.1.0", es[0].identity.run_id, "low", 0.8, Component.CONTEXT_BUILDER, [e.event_id for e in es], {"file_path_hash": fp, "reads": len(es)}, f"{len(es)} reads of the same file without a write")
            for fp, es in reads.items() if len(es) >= min_reads]


def d10_invalid_tool_args(events: list[Event], min_count: int = 2) -> list[Finding]:
    bad = [e for e in events if e.type == EventType.TOOL_FAILED and (e.attrs.get("error_type") or "").lower() in ("inputvalidationerror", "schemaerror", "validationerror", "invalid_arguments")]
    if len(bad) < min_count: return []
    return [Finding("D10", "0.1.0", bad[0].identity.run_id, "medium", 0.9, Component.TOOL, [e.event_id for e in bad], {"count": len(bad)}, f"{len(bad)} schema-level tool failures")]


DETECTORS: dict[str, Callable[[list[Event]], list[Finding]]] = {
    "D1": d1_doom_loop, "D3": d3_retry_storm, "D4": d4_no_progress, "D5": d5_budget_spiral, "D6": d6_verification_bypass,
    "D7": d7_permission_storm, "D8": d8_context_explosion, "D9": d9_repeated_retrieval, "D10": d10_invalid_tool_args,
}


def run_all(events: list[Event]) -> list[Finding]:
    out: list[Finding] = []
    for d in DETECTORS.values(): out.extend(d(events))
    return out
