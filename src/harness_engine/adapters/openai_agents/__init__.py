"""OpenAI Agents SDK Tier A instrumentor (SPEC-06 §1, §5.2).

Live use (requires `openai-agents`):
    proc = HarnessTracingProcessor(); add_trace_processor(proc)
    rec = HookRecorder(); await Runner.run(agent, task, hooks=HarnessRunHooks(rec))
    events, stats = normalize_records(proc.records + rec.records)

Replay of captured records needs only `harness_engine` (see tests/fixtures/openai_agents/).
"""
from __future__ import annotations
import json
from typing import Iterable

from harness_engine.model.events import Event
from .common import CHANNEL_HOOKS, CHANNEL_TRACING, merge, post
from .hooks import HarnessAgentHooks, HarnessRunHooks, HookRecorder, parse_hooks
from .processor import HarnessTracingProcessor, TraceMapper, parse_tracing

__all__ = ["HarnessTracingProcessor", "HarnessRunHooks", "HarnessAgentHooks", "HookRecorder", "TraceMapper",
           "normalize_records", "load_records", "CHANNEL_TRACING", "CHANNEL_HOOKS"]


def load_records(path: str) -> list[dict]:
    with open(path) as f:
        return [json.loads(l) for l in f if l.strip()]


def normalize_records(records: Iterable[dict], harness_version: str | None = None) -> tuple[list[Event], dict]:
    """Map tracing and hook records, merge on exact correlation ids, number iterations, and compute the Proof B metric:
    v01_exception_rate = native signals kept as UNKNOWN / all native signals (tracing objects + hook/approval/wrap records)."""
    recs = list(records)
    for r in recs:
        if r.get("channel") == "meta" and not harness_version: harness_version = r.get("harness_version")
    tev, tst, tm = parse_tracing(recs, harness_version)
    hev, hst = parse_hooks(recs, harness_version, trace_mapper=tm)
    merged, mst = merge(tev + hev)
    merged = post(merged)
    stats = {"tracing": tst, "hooks": hst, "merge": mst}
    total = tst["records"] + hst["records"]; unm = tst["unmapped"] + hst["unmapped"]
    stats["native_signals"] = total
    stats["mapped"] = tst["mapped"] + hst["mapped"]
    stats["structural"] = tst["structural"] + hst["structural"]
    stats["unmapped"] = unm
    stats["unmapped_names"] = {**tst["unmapped_names"], **{k: v + tst["unmapped_names"].get(k, 0) for k, v in hst["unmapped_names"].items()}}
    stats["v01_exception_rate"] = (unm / total) if total else 0.0
    stats["v01_exception_rate_tracing_only"] = (tst["unmapped"] / tst["records"]) if tst["records"] else 0.0
    return merged, stats
