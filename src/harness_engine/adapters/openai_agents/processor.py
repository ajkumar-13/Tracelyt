"""OpenAI Agents SDK tracing -> v0.1 events (Tier A instrumentor, channel `openai_agents.tracing`).

`HarnessTracingProcessor` is a `TracingProcessor` registered with `add_trace_processor()` (additive; the OpenAI
exporter keeps working). It records each trace/span callback as a plain dict (the SDK's own `export()`) and maps the
records with `TraceMapper`, which needs no SDK import, so a captured record file can be re-normalized anywhere.

Mapping (span types and fields as observed in openai-agents 0.24.0):
  trace start                  -> run.started                      (run_id = trace_id)
  task span (custom/task)      -> run.resumed on a reattached trace (RunState resume); run.completed|failed at end, + stop
  turn span (custom/turn)      -> iteration.started / iteration.completed (iteration = SDK turn number)
  agent span                   -> identity (agent_instance_id = span id); agent.returned at the end of a handoff target
  generation / response span   -> model.request + model.response; tool.requested per function_call output item;
                                  context.compact per `compaction` output item (server-side compaction)
  function span                -> tool.started + tool.completed | tool.failed; an approval-pending span (no output, no
                                  error: the SDK's needs_approval short-circuit) -> permission.requested
  handoff span                 -> agent.spawned (emitted when the target agent span opens, so the child id is exact)
  trace end                    -> run.completed only when no task span was seen (task spans are on by default)
  guardrail / custom / mcp_tools / speech* / transcription -> unknown (native_type preserved)
Function spans carry no call id; the tool_call_id is joined from the preceding generation output by (name, arguments).
"""
from __future__ import annotations
import json, re
from typing import Any, Iterable

from harness_engine.model.events import (CaptureTier, DecisionSource, Event, EventType, Identity, INTERFACES, StopReason,
                                          Versions, new_event_id)
from .common import CHANNEL_TRACING, HARNESS, canon, count, new_stats, now_iso, ref, sha, ts

try:  # live use only; the mapper below runs without the SDK
    from agents.tracing import TracingProcessor as _ProcessorBase
except Exception:  # pragma: no cover - exercised when openai-agents is absent
    _ProcessorBase = object  # type: ignore[assignment,misc]

UNMAPPED_SPAN_TYPES = {"guardrail", "mcp_tools", "transcription", "speech", "speech_group"}


def _sdk_type(sd: dict) -> str:
    """Task and turn spans export as type "custom" with data.sdk_span_type (research 04 note 2)."""
    if sd.get("type") == "custom" and isinstance(sd.get("data"), dict) and sd["data"].get("sdk_span_type"):
        return sd["data"]["sdk_span_type"]
    return sd.get("type", "unknown")


def _out_items(sd: dict) -> list[dict]:
    """Output items of a generation span. Chat-Completions-style models export [Response.model_dump()]; accept a bare item list too."""
    out = sd.get("output") or []
    items: list[dict] = []
    for o in out:
        if isinstance(o, dict) and o.get("object") == "response": items.extend(o.get("output") or [])
        elif isinstance(o, dict): items.append(o)
    return items


def _response_id(sd: dict) -> str | None:
    for o in sd.get("output") or []:
        if isinstance(o, dict) and o.get("object") == "response": return o.get("id")
    return sd.get("response_id")


def _handoff_tool_name(agent_name: str | None) -> str:
    return re.sub(r"[^a-z0-9_]", "_", f"transfer_to_{agent_name or ''}".lower())


def _message_text(item: dict) -> str:
    return "".join(c.get("text", "") for c in item.get("content") or [] if isinstance(c, dict))


class TraceMapper:
    """Stateful mapper over tracing records in arrival order. One instance per capture (handles many traces)."""

    def __init__(self, harness_version: str | None = None):
        self.versions = Versions(harness=f"{HARNESS}@{harness_version}" if harness_version else HARNESS)
        self.events: list[Event] = []
        self.stats = new_stats()
        self.spans: dict[str, dict] = {}            # span_id -> {"type", "parent_id", "data"}
        self.agents: dict[str, dict] = {}           # agent span id -> {"name", "instance", "parent_instance", "tools", "handoffs", ...}
        self.traces: dict[str, dict] = {}           # trace_id -> per-trace state
        self._seq = 0

    # ---- lookups shared with the hook mapper (exact span ids, no inference) ----
    def agent_span_of(self, span_id: str | None) -> str | None:
        while span_id:
            s = self.spans.get(span_id)
            if not s: return None
            if s["type"] == "agent": return span_id
            span_id = s["parent_id"]
        return None

    def instance_of_agent_span(self, agent_span_id: str | None) -> str | None:
        a = self.agents.get(agent_span_id or "")
        return a["instance"] if a else agent_span_id

    def turn_of(self, span_id: str | None) -> int | None:
        while span_id:
            s = self.spans.get(span_id)
            if not s: return None
            if s["type"] == "turn": return s["data"].get("data", {}).get("turn")
            span_id = s["parent_id"]
        return None

    # ---- event construction ----
    def _identity(self, trace_id: str, span_id: str | None) -> Identity:
        aspan = self.agent_span_of(span_id)
        a = self.agents.get(aspan or "", {})
        return Identity(run_id=trace_id, trace_id=trace_id, span_id=span_id, agent_definition=a.get("name"),
                        agent_instance_id=a.get("instance"), parent_agent_instance_id=a.get("parent_instance"),
                        iteration=self.turn_of(span_id), session_id=self.traces.get(trace_id, {}).get("group_id"))

    def _emit(self, etype: EventType, trace_id: str, span_id: str | None, native: str, when: str | None, attrs: dict,
              status=None, correlation=None, payload_refs=None, model: str | None = None, identity: Identity | None = None) -> Event:
        comp, counter = INTERFACES[etype]
        self._seq += 1
        corr = {k: v for k, v in (correlation or {}).items() if v}
        e = Event(event_id=new_event_id(trace_id, native, span_id or "", etype.value, json.dumps(corr, sort_keys=True)),
                  type=etype, native_type=f"openai_agents.{native}", timestamp=ts(when), sequence=self._seq,
                  identity=identity or self._identity(trace_id, span_id),
                  versions=self.versions.model_copy(update={"model": model}) if model else self.versions,
                  component=comp, counterpart=counter, correlation=corr, status=status, attrs=attrs,
                  payload_refs={k: v for k, v in (payload_refs or {}).items() if v is not None},
                  capture_tier=CaptureTier.A, source_channel=CHANNEL_TRACING)
        self.events.append(e)
        return e

    def _unknown(self, trace_id: str, span_id: str | None, native: str, when: str | None, native_attrs: dict) -> None:
        self._emit(EventType.UNKNOWN, trace_id, span_id, native, when, {"native": native_attrs})
        count(self.stats, "unmapped", native)

    def _trace(self, trace_id: str) -> dict:
        return self.traces.setdefault(trace_id, {"ended": False, "tasks": 0, "group_id": None, "pending_calls": [],
                                                 "handoff": None, "seg": None, "last_agent": None})

    # ---- record feed ----
    def feed(self, rec: dict) -> None:
        kind = rec.get("kind")
        if kind == "trace_start": self._trace_start(rec)
        elif kind == "trace_end": self._trace_end(rec)
        elif kind == "span_start": self._span_start(rec["span"], rec.get("ts"))
        elif kind == "span_end": self._span_end(rec["span"])

    def _trace_start(self, rec: dict) -> None:
        t = rec["trace"]; tid = t["id"]; st = self._trace(tid); st["group_id"] = t.get("group_id")
        self._emit(EventType.RUN_STARTED, tid, None, "trace.start", rec.get("ts"),
                   {"entrypoint": "sdk", "source": "startup", "task": None},
                   correlation={"trace_id": tid, "workflow_name_hash": sha(t.get("workflow_name") or "")})
        count(self.stats, "mapped", "trace.start")

    def _trace_end(self, rec: dict) -> None:
        tid = rec["trace"]["id"]; st = self._trace(tid); st["ended"] = True
        if st["tasks"]:
            count(self.stats, "structural", "trace.end")  # run end already emitted from the task span
            return
        self._emit(EventType.RUN_COMPLETED, tid, None, "trace.end", rec.get("ts"), {"stop_reason": StopReason.UNKNOWN, "terminal_reason": "trace_end"})
        count(self.stats, "mapped", "trace.end")

    def _span_start(self, sp: dict, when: str | None) -> None:
        sd = sp.get("span_data") or {}; typ = _sdk_type(sd); sid = sp["id"]; tid = sp["trace_id"]; st = self._trace(tid)
        self.spans[sid] = {"type": typ, "parent_id": sp.get("parent_id"), "data": sd}
        start = sp.get("started_at") or when
        if typ == "task":
            st["tasks"] += 1
            st["seg"] = {"task_span": sid, "pending": [], "final": None, "turns": 0, "error": None, "resumed": st["ended"] or st["tasks"] > 1}
            if st["seg"]["resumed"]:
                self._emit(EventType.RUN_RESUMED, tid, sid, "span.task.start", start, {"entrypoint": "sdk", "source": "resume"},
                           correlation={"task_span_id": sid})
        elif typ == "agent":
            name = sd.get("name"); instance = sid; parent = None
            seg = st["seg"] or {}
            ho = st["handoff"]
            if ho and ho["to_agent"] == name:
                parent = ho["from_instance"]
            elif seg.get("resumed") and not seg.get("agent_seen") and st["last_agent"] and st["last_agent"]["name"] == name:
                # RunState resume re-opens the interrupted agent under a new span: same logical instance.
                instance = st["last_agent"]["instance"]; parent = st["last_agent"]["parent_instance"]
            if seg: seg["agent_seen"] = True
            self.agents[sid] = {"name": name, "instance": instance, "parent_instance": parent, "tools": sd.get("tools") or [],
                                "handoffs": sd.get("handoffs") or [], "spawned_at": None, "tokens": 0, "tool_uses": 0}
            st["last_agent"] = self.agents[sid]
            if ho and ho["to_agent"] == name:
                self.agents[sid]["spawned_at"] = ho["when"]
                ident = self._identity(tid, ho["handoff_span"])
                self._emit(EventType.AGENT_SPAWNED, tid, ho["handoff_span"], "span.handoff", ho["when"],
                           {"child_agent_instance_id": instance, "child_agent_definition": name, "via_tool_call_id": ho.get("call_id"), "is_async": False},
                           correlation={"child_agent_instance_id": instance, "tool_call_id": ho.get("call_id")}, identity=ident)
                st["handoff"] = None
        elif typ == "turn":
            if st["seg"]: st["seg"]["turns"] += 1
            turn = (sd.get("data") or {}).get("turn")
            self._emit(EventType.ITERATION_STARTED, tid, sid, "span.turn.start", start, {"iteration": turn or 0}, correlation={"turn_span_id": sid})

    def _span_end(self, sp: dict) -> None:
        sd = sp.get("span_data") or {}; typ = _sdk_type(sd); sid = sp["id"]; tid = sp["trace_id"]; st = self._trace(tid)
        if sid not in self.spans: self._span_start(sp, sp.get("started_at"))
        self.spans[sid]["data"] = sd
        end, start, err = sp.get("ended_at"), sp.get("started_at"), sp.get("error")
        dur = int((ts(end) - ts(start)).total_seconds() * 1000) if end and start else None
        seg = st["seg"] or {}
        if typ == "task": return self._task_end(sp, sd, tid, st, seg, err)
        if typ == "agent":
            a = self.agents.get(sid, {}); a["tools"] = sd.get("tools") or a.get("tools", []); a["handoffs"] = sd.get("handoffs") or a.get("handoffs", [])
            if a.get("parent_instance") and not seg.get("pending"):
                ident = self._identity(tid, sid).model_copy(update={"agent_instance_id": a["parent_instance"], "agent_definition": None, "parent_agent_instance_id": None})
                spawned = a.get("spawned_at")
                self._emit(EventType.AGENT_RETURNED, tid, sid, "span.agent.end", end,
                           {"child_agent_instance_id": a["instance"], "status": "error" if err else "ok", "total_tokens": a.get("tokens") or None,
                            "total_tool_uses": a.get("tool_uses"), "duration_ms": int((ts(end) - ts(spawned)).total_seconds() * 1000) if spawned else dur},
                           correlation={"child_agent_instance_id": a["instance"]}, identity=ident)
                count(self.stats, "mapped", "span.agent")
            else:
                count(self.stats, "structural", "span.agent")
            return
        if typ == "turn":
            self._emit(EventType.ITERATION_COMPLETED, tid, sid, "span.turn.end", end, {"iteration": (sd.get("data") or {}).get("turn") or 0},
                       correlation={"turn_span_id": sid})
            count(self.stats, "mapped", "span.turn"); return
        if typ in ("generation", "response"): return self._model(sp, sd, tid, st, seg, err, dur)
        if typ == "function": return self._function(sp, sd, tid, st, seg, err, dur)
        if typ == "handoff":
            aspan = self.agent_span_of(sp.get("parent_id")); a = self.agents.get(aspan or "", {})
            to = sd.get("to_agent"); call_id = None
            mine = [c for c in st["pending_calls"] if c["agent_span"] == aspan and not c["requested"]]
            # Default handoff tool name is transfer_to_<agent> (Handoff.default_tool_name); else the agent's first unconsumed call.
            pick = next((c for c in mine if c["name"] == _handoff_tool_name(to)), mine[0] if mine else None)
            if pick: call_id = pick["call_id"]; st["pending_calls"].remove(pick)
            st["handoff"] = {"from_instance": a.get("instance"), "to_agent": to, "when": end, "handoff_span": sid, "call_id": call_id}
            if err:
                self._unknown(tid, sid, "span.handoff.error", end, {"error": err}); return
            count(self.stats, "mapped", "span.handoff"); return
        name = f"span.{typ}" if typ != "custom" else f"span.custom:{sd.get('name')}"
        self._unknown(tid, sid, name, end, {k: v for k, v in sd.items() if k not in ("input", "output")} | ({"error": err} if err else {}))

    def _request(self, tid: str, c: dict) -> None:
        if c["requested"]: return
        c["requested"] = True; args = c.get("arguments") or ""
        self._emit(EventType.TOOL_REQUESTED, tid, c["gen_span"], f"span.{c['gen_type']}.output.function_call", c["when"],
                   {"tool_name": c.get("name") or "", "tool_call_id": c.get("call_id") or "", "tool_source": "function", "input_hash": sha(args), "input_size_bytes": len(args.encode())},
                   correlation={"tool_call_id": c.get("call_id")}, payload_refs={"input": ref(args)})

    def _task_end(self, sp, sd, tid, st, seg, err) -> None:
        if not seg.get("pending"):
            # Calls no span ever consumed (e.g. an approval rejected on resume: 0.24.0 opens no span for it).
            for c in list(st["pending_calls"]):
                self._request(tid, c); st["pending_calls"].remove(c)
        end = sp.get("ended_at"); usage = (sd.get("data") or {}).get("usage") or {}
        pending = bool(seg.get("pending")); final = seg.get("final")
        if err:
            reason = StopReason.MAX_TURNS if "Max turns" in (err.get("message") or "") else StopReason.FATAL_ERROR
            self._emit(EventType.STOP, tid, sp["id"], "span.task.error", end, {"reason": reason, "declared_by": "error", "native_reason": err.get("message")},
                       correlation={"task_span_id": sp["id"]})
            self._emit(EventType.RUN_FAILED, tid, sp["id"], "span.task.end", end, {"stop_reason": reason, "terminal_reason": err.get("message"), "total_turns": seg.get("turns"),
                       "input_tokens": usage.get("input_tokens"), "output_tokens": usage.get("output_tokens")}, status="error", correlation={"task_span_id": sp["id"]})
        else:
            if final and not pending:
                self._emit(EventType.STOP, tid, final["span"], "span.generation.final_output", final["when"],
                           {"reason": StopReason.AGENT_DECLARED_COMPLETE, "declared_by": "agent", "native_reason": "final_output"},
                           correlation={"final_agent_instance_id": final["instance"]}, payload_refs={"final_message": ref(final["text"])})
            self._emit(EventType.RUN_COMPLETED, tid, sp["id"], "span.task.end", end,
                       {"stop_reason": StopReason.AGENT_DECLARED_COMPLETE if final and not pending else StopReason.UNKNOWN,
                        "terminal_reason": "interrupted:tool_approval" if pending else ("final_output" if final else "task_end"),
                        "total_turns": seg.get("turns"), "input_tokens": usage.get("input_tokens"), "output_tokens": usage.get("output_tokens"),
                        "cache_read_tokens": (usage.get("input_tokens_details") or {}).get("cached_tokens")},
                       status="ok", correlation={"task_span_id": sp["id"]})
        count(self.stats, "mapped", "span.task")

    def _model(self, sp, sd, tid, st, seg, err, dur) -> None:
        sid, start, end = sp["id"], sp.get("started_at"), sp.get("ended_at")
        model = sd.get("model") or ""; usage = sd.get("usage") or {}; items = _out_items(sd)
        aspan = self.agent_span_of(sid); a = self.agents.get(aspan or "", {})
        turn_span = sp.get("parent_id") if self.spans.get(sp.get("parent_id") or "", {}).get("type") == "turn" else None
        rid = _response_id(sd)
        calls = [i for i in items if i.get("type") == "function_call"]
        inp = sd.get("input")
        self._emit(EventType.MODEL_REQUEST, tid, sid, f"span.{sd.get('type')}.start", start,
                   {"model": model, "num_messages": len(inp) if isinstance(inp, list) else None, "query_source": "sdk",
                    "provider": "openai" if "api.openai.com" in str((sd.get("model_config") or {}).get("base_url", "")) else None},
                   correlation={"turn_span_id": turn_span or sid, "generation_span_id": sid}, payload_refs={"input": ref(inp) if inp is not None else None}, model=model or None)
        a["tokens"] = (a.get("tokens") or 0) + (usage.get("input_tokens") or 0) + (usage.get("output_tokens") or 0)
        self._emit(EventType.MODEL_RESPONSE, tid, sid, f"span.{sd.get('type')}.end", end,
                   {"model": model, "request_id": rid, "message_id": rid, "input_tokens": usage.get("input_tokens"), "output_tokens": usage.get("output_tokens"),
                    "cache_read_tokens": (usage.get("input_tokens_details") or {}).get("cached_tokens"),
                    "thinking_tokens": (usage.get("output_tokens_details") or {}).get("reasoning_tokens"), "duration_ms": dur,
                    # The SDK exposes no normalized finish reason; this is read off the output item types (observed, not inferred).
                    "finish_reason": None if err else ("tool_use" if calls else "end_turn"), "num_tool_calls": len(calls),
                    "error_type": (err or {}).get("data", {}).get("name") if err else None},
                   status="error" if err else "ok", correlation={"response_id": rid or sid, "generation_span_id": sid},
                   payload_refs={"output": ref(sd.get("output")) if sd.get("output") is not None else None}, model=model or None)
        # The agent span's tool list is filled after the span opens, so whether a function_call is a tool or a handoff is
        # settled when a function or handoff span consumes it; tool.requested keeps the generation's timestamp.
        for c in calls:
            st["pending_calls"].append({"call_id": c.get("call_id"), "name": c.get("name"), "arguments": c.get("arguments"), "agent_span": aspan,
                                        "gen_span": sid, "gen_type": sd.get("type"), "when": end, "requested": False})
        for c in items:
            if c.get("type") == "compaction":
                self._emit(EventType.CONTEXT_COMPACT, tid, sid, f"span.{sd.get('type')}.output.compaction", end,
                           {"trigger": "auto"}, correlation={"compaction_item_id": c.get("id") or sha(c)}, payload_refs={"summary": ref(c.get("encrypted_content") or c)})
        msgs = [i for i in items if i.get("type") == "message"]
        if msgs and not calls and seg is not None:
            seg["final"] = {"text": "".join(_message_text(m) for m in msgs), "when": end, "span": sid, "instance": a.get("instance")}
        count(self.stats, "mapped", f"span.{sd.get('type')}")

    def _function(self, sp, sd, tid, st, seg, err, dur) -> None:
        sid, start, end = sp["id"], sp.get("started_at"), sp.get("ended_at")
        name, inp, out = sd.get("name"), sd.get("input"), sd.get("output")
        aspan = self.agent_span_of(sid); a = self.agents.get(aspan or "", {})
        call = None
        for i, c in enumerate(st["pending_calls"]):
            if c["name"] == name and (inp is None or c["arguments"] == inp):
                call = c; break
        call_id = (call or {}).get("call_id") or ""
        if call: self._request(tid, call)
        mcp = sd.get("mcp_data") or None
        req = {"tool_name": name or "", "tool_call_id": call_id, "tool_source": "mcp" if mcp else "function",
               "mcp_server": (mcp or {}).get("server"), "input_hash": sha(inp) if inp is not None else None,
               "input_size_bytes": len(inp.encode()) if isinstance(inp, str) else None}
        corr = {"tool_call_id": call_id, "function_span_id": sid}
        emsg = (err or {}).get("message") or ""; edata = (err or {}).get("data") or {}
        if err is None and out is None:
            # 0.24.0 needs_approval short-circuit: the span closes with neither output nor error and the body never runs.
            # The call stays pending; the resumed run opens a fresh function span for it once approved.
            self._emit(EventType.PERMISSION_REQUESTED, tid, sid, "span.function.approval_pending", end,
                       {"actor": a.get("instance"), "resource": name, "action": "invoke", "tool_call_id": call_id, "decision": "pending", "source": DecisionSource.UNKNOWN},
                       status="unknown", correlation=corr)
            if seg is not None: seg["pending"].append(call_id)
            count(self.stats, "mapped", "span.function"); return
        if call: st["pending_calls"].remove(call)
        if "manually rejected" in str(edata.get("error", "")) or emsg == "Tool execution rejected":
            self._emit(EventType.PERMISSION_DENIED, tid, sid, "span.function.rejected", end,
                       {"actor": a.get("instance"), "resource": name, "action": "invoke", "tool_call_id": call_id, "decision": "denied", "source": DecisionSource.USER},
                       status="denied", correlation=corr)
            count(self.stats, "mapped", "span.function"); return
        a["tool_uses"] = (a.get("tool_uses") or 0) + 1
        self._emit(EventType.TOOL_STARTED, tid, sid, "span.function.start", start, req, correlation=corr, payload_refs={"input": ref(inp) if inp is not None else None})
        ok = err is None
        res = {"tool_name": name or "", "tool_call_id": call_id, "success": ok, "duration_ms": dur,
               "output_hash": sha(out) if out is not None else None, "output_size_bytes": len(canon(out).encode()) if out is not None else None}
        if not ok:
            res["error_type"] = "ToolError" if emsg.startswith("Error running tool") else emsg or "error"
            res["error_message_hash"] = sha(canon(edata)) if edata else None
        self._emit(EventType.TOOL_COMPLETED if ok else EventType.TOOL_FAILED, tid, sid, "span.function.end", end, res,
                   status="ok" if ok else "error", correlation=corr, payload_refs={"output": ref(out) if out is not None else None})
        count(self.stats, "mapped", "span.function")


def parse_tracing(records: Iterable[dict], harness_version: str | None = None) -> tuple[list[Event], dict, TraceMapper]:
    m = TraceMapper(harness_version)
    for r in records:
        if r.get("channel") == "tracing": m.feed(r)
    return m.events, m.stats, m


class HarnessTracingProcessor(_ProcessorBase):  # type: ignore[misc,valid-type]
    """Live processor. Records native trace/span exports; `events()` maps them. Register with `add_trace_processor`."""

    def __init__(self, harness_version: str | None = None):
        from .common import harness_version as _hv
        self.harness_version = harness_version or _hv()
        self.records: list[dict] = []

    def _rec(self, kind: str, key: str, obj: Any) -> None:
        exp = obj.export() if hasattr(obj, "export") else None
        if exp is None: return
        self.records.append({"channel": "tracing", "kind": kind, "ts": now_iso(), key: json.loads(json.dumps(exp, default=str))})

    def on_trace_start(self, trace) -> None: self._rec("trace_start", "trace", trace)
    def on_trace_end(self, trace) -> None: self._rec("trace_end", "trace", trace)
    def on_span_start(self, span) -> None: self._rec("span_start", "span", span)
    def on_span_end(self, span) -> None: self._rec("span_end", "span", span)
    def shutdown(self) -> None: pass
    def force_flush(self) -> None: pass

    def events(self) -> tuple[list[Event], dict]:
        ev, st, _ = parse_tracing(self.records, self.harness_version)
        return ev, st
