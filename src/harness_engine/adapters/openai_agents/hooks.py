"""OpenAI Agents SDK lifecycle hooks, approvals and compaction wraps -> v0.1 events (channel `openai_agents.hooks`).

Live side: `HarnessRunHooks` (pass as `Runner.run(..., hooks=)`), `HarnessAgentHooks` (set as `Agent.hooks`),
`HookRecorder.record_interruptions/approve/reject` (the SDK has no approval callback: `RunResult.interruptions` and
`RunState.approve/reject` are the only surface), and `HookRecorder.wrap_compaction_client` (session compaction through
`responses.compact` emits neither a span nor a hook in 0.24.0, so the instrumentor wraps the client call).
Each callback is recorded as a content-free dict (names, ids, digests) with the current trace and span ids, which are
the exact join keys to the tracing channel. `parse_hooks` maps the records and needs no SDK import.

Correlation keys shared with the tracing channel: tool_call_id, response_id, turn_span_id, child_agent_instance_id,
compaction_item_id, final_agent_instance_id. `common.merge` dedupes on them.
"""
from __future__ import annotations
import json
from typing import Any, Iterable

from harness_engine.model.events import (CaptureTier, DecisionSource, Event, EventType, Identity, INTERFACES, StopReason,
                                          Versions, new_event_id)
from .common import (CHANNEL_HOOKS, HARNESS, SDK_DEFAULT_TOOL_ERROR, count, digest, new_stats, now_iso, ref_from_digest, sha, ts)

try:
    from agents import AgentHooks as _AgentHooksBase, RunHooks as _RunHooksBase
except Exception:  # pragma: no cover - openai-agents absent: mapping still works on recorded dicts
    _AgentHooksBase = _RunHooksBase = object  # type: ignore[assignment,misc]


# ---- live recording --------------------------------------------------------------------------------------------

def _ctx() -> dict:
    try:
        from agents.tracing import get_current_span, get_current_trace
    except Exception:
        return {}
    tr, sp = get_current_trace(), get_current_span()
    out = {"trace_id": getattr(tr, "trace_id", None), "span_id": getattr(sp, "span_id", None), "parent_id": getattr(sp, "parent_id", None)}
    if sp is not None:
        sd = sp.span_data; out["span_type"] = getattr(sd, "type", None)
        if out["span_type"] == "turn": out["turn"] = getattr(sd, "turn", None)
    return out


def _tool_names(agent: Any) -> list[str]:
    return sorted(getattr(t, "name", str(t)) for t in (getattr(agent, "tools", None) or []))


def _handoff_tool_names(agent: Any) -> list[str]:
    names = []
    for h in getattr(agent, "handoffs", None) or []:
        if hasattr(h, "tool_name"): names.append(h.tool_name)
        else:
            try:
                from agents import Handoff
                names.append(Handoff.default_tool_name(h))
            except Exception:
                names.append(f"transfer_to_{getattr(h, 'name', h)}")
    return sorted(names)


def _model_name(agent: Any) -> str | None:
    m = getattr(agent, "model", None)
    return m if isinstance(m, str) else getattr(m, "name", None) or getattr(m, "model", None)


def _item_summary(o: Any) -> dict:
    d = o if isinstance(o, dict) else (o.model_dump(mode="json", exclude_none=True) if hasattr(o, "model_dump") else {"type": str(type(o))})
    s = {"type": d.get("type"), "id": d.get("id")}
    if d.get("type") == "function_call":
        s.update(call_id=d.get("call_id"), name=d.get("name"), arguments=digest(d.get("arguments") or ""))
    elif d.get("type") == "compaction":
        s["content"] = digest(d.get("encrypted_content") or d)
    elif d.get("type") == "message":
        s["content"] = digest("".join(c.get("text", "") for c in d.get("content") or [] if isinstance(c, dict)))
    return s


class HookRecorder:
    def __init__(self):
        self.records: list[dict] = []

    def record(self, kind: str, payload: dict, ctx: dict | None = None) -> None:
        self.records.append({"channel": "hooks", "kind": kind, "ts": now_iso(), "payload": {**(ctx if ctx is not None else _ctx()), **payload}})

    # approvals: RunResult.interruptions / RunState.approve / RunState.reject
    def record_interruptions(self, result: Any) -> list[Any]:
        tid = getattr(getattr(result, "trace", None), "trace_id", None) or getattr(getattr(result, "_trace_state", None), "trace_id", None)
        for it in getattr(result, "interruptions", None) or []:
            raw = it.raw_item
            call_id = raw.get("call_id") if isinstance(raw, dict) else getattr(raw, "call_id", None)
            self.record("run_state.interruption", {"agent": getattr(it.agent, "name", None), "tool_name": it.tool_name, "tool_call_id": call_id,
                                                   "item_type": getattr(it, "type", None)}, ctx={"trace_id": tid})
        return list(getattr(result, "interruptions", None) or [])

    def _decide(self, state: Any, item: Any, approved: bool, always: bool, message: str | None) -> None:
        if approved: state.approve(item, always_approve=always)
        else: state.reject(item, always_reject=always, rejection_message=message)
        ts_ = getattr(state, "_trace_state", None)
        raw = item.raw_item
        call_id = raw.get("call_id") if isinstance(raw, dict) else getattr(raw, "call_id", None)
        self.record("run_state.approve" if approved else "run_state.reject",
                    {"agent": getattr(item.agent, "name", None), "tool_name": item.tool_name, "tool_call_id": call_id, "always": always,
                     "message": digest(message) if message else None}, ctx={"trace_id": getattr(ts_, "trace_id", None)})

    def approve(self, state: Any, item: Any, always_approve: bool = False) -> None:
        self._decide(state, item, True, always_approve, None)

    def reject(self, state: Any, item: Any, always_reject: bool = False, rejection_message: str | None = None) -> None:
        self._decide(state, item, False, always_reject, rejection_message)

    def wrap_compaction_client(self, client: Any) -> Any:
        """Wrap `client.responses.compact` (used by OpenAIResponsesCompactionSession) to record each compaction."""
        rec = self; orig = client.responses.compact

        async def compact(**kwargs):
            ctx = _ctx()
            out = await orig(**kwargs)
            items = [_item_summary(o) for o in (getattr(out, "output", None) or [])]
            usage = getattr(out, "usage", None)
            rec.record("wrap.responses.compact", {"mode": "previous_response_id" if kwargs.get("previous_response_id") else "input",
                                                  "num_input_items": len(kwargs.get("input") or []), "model": kwargs.get("model"), "output_items": items,
                                                  "input_tokens": getattr(usage, "input_tokens", None), "output_tokens": getattr(usage, "output_tokens", None)}, ctx=ctx)
            return out
        client.responses.compact = compact
        return client

    # shared callback bodies
    def agent_start(self, src: str, agent: Any) -> None:
        self.record(f"{src}.on_agent_start" if src == "run_hooks" else f"{src}.on_start", {"agent": agent.name})

    def agent_end(self, src: str, agent: Any, output: Any) -> None:
        self.record(f"{src}.on_agent_end" if src == "run_hooks" else f"{src}.on_end", {"agent": agent.name, "output": digest(output)})

    def handoff(self, src: str, from_agent: Any, to_agent: Any) -> None:
        self.record(f"{src}.on_handoff", {"from_agent": from_agent.name, "to_agent": to_agent.name})

    def llm_start(self, src: str, agent: Any, system_prompt: str | None, input_items: list) -> None:
        self.record(f"{src}.on_llm_start", {"agent": agent.name, "model": _model_name(agent), "num_input_items": len(input_items or []),
                                            "tools": _tool_names(agent), "handoff_tools": _handoff_tool_names(agent),
                                            "system": digest(system_prompt) if system_prompt else None, "input": digest([_jsonable(i) for i in input_items or []])})

    def llm_end(self, src: str, agent: Any, response: Any) -> None:
        u = getattr(response, "usage", None)
        self.record(f"{src}.on_llm_end", {"agent": agent.name, "model": _model_name(agent), "response_id": response.response_id,
                                          "request_id": getattr(response, "request_id", None), "handoff_tools": _handoff_tool_names(agent),
                                          "input_tokens": getattr(u, "input_tokens", None), "output_tokens": getattr(u, "output_tokens", None),
                                          "output_items": [_item_summary(o) for o in response.output]})

    def tool_start(self, src: str, context: Any, agent: Any, tool: Any) -> None:
        self.record(f"{src}.on_tool_start", {"agent": agent.name, "tool_name": getattr(tool, "name", None), "tool_call_id": getattr(context, "tool_call_id", None),
                                             "arguments": digest(getattr(context, "tool_arguments", "") or ""),
                                             "mcp": bool(getattr(tool, "_mcp_server_name", None))})

    def tool_end(self, src: str, context: Any, agent: Any, tool: Any, result: Any) -> None:
        self.record(f"{src}.on_tool_end", {"agent": agent.name, "tool_name": getattr(tool, "name", None), "tool_call_id": getattr(context, "tool_call_id", None),
                                           "result": digest(result if isinstance(result, (str, dict, list)) else str(result)),
                                           "sdk_default_error": isinstance(result, str) and result == SDK_DEFAULT_TOOL_ERROR})


def _jsonable(i: Any) -> Any:
    return i if isinstance(i, (dict, str)) else (i.model_dump(mode="json") if hasattr(i, "model_dump") else str(i))


class HarnessRunHooks(_RunHooksBase):  # type: ignore[misc,valid-type]
    def __init__(self, recorder: HookRecorder):
        self.r = recorder
    async def on_agent_start(self, context, agent) -> None: self.r.agent_start("run_hooks", agent)
    async def on_agent_end(self, context, agent, output) -> None: self.r.agent_end("run_hooks", agent, output)
    async def on_handoff(self, context, from_agent, to_agent) -> None: self.r.handoff("run_hooks", from_agent, to_agent)
    async def on_llm_start(self, context, agent, system_prompt, input_items) -> None: self.r.llm_start("run_hooks", agent, system_prompt, input_items)
    async def on_llm_end(self, context, agent, response) -> None: self.r.llm_end("run_hooks", agent, response)
    async def on_tool_start(self, context, agent, tool) -> None: self.r.tool_start("run_hooks", context, agent, tool)
    async def on_tool_end(self, context, agent, tool, result) -> None: self.r.tool_end("run_hooks", context, agent, tool, result)


class HarnessAgentHooks(_AgentHooksBase):  # type: ignore[misc,valid-type]
    def __init__(self, recorder: HookRecorder):
        self.r = recorder
    async def on_start(self, context, agent) -> None: self.r.agent_start("agent_hooks", agent)
    async def on_end(self, context, agent, output) -> None: self.r.agent_end("agent_hooks", agent, output)
    async def on_handoff(self, context, agent, source) -> None: self.r.handoff("agent_hooks", source, agent)
    async def on_llm_start(self, context, agent, system_prompt, input_items) -> None: self.r.llm_start("agent_hooks", agent, system_prompt, input_items)
    async def on_llm_end(self, context, agent, response) -> None: self.r.llm_end("agent_hooks", agent, response)
    async def on_tool_start(self, context, agent, tool) -> None: self.r.tool_start("agent_hooks", context, agent, tool)
    async def on_tool_end(self, context, agent, tool, result) -> None: self.r.tool_end("agent_hooks", context, agent, tool, result)


# ---- mapping ---------------------------------------------------------------------------------------------------

class HookMapper:
    """Maps hook records. With a TraceMapper from the same capture, agent instances resolve through the SDK's span tree
    (exact span ids); alone, it falls back to the span parent ids the hook saw."""

    def __init__(self, harness_version: str | None = None, trace_mapper: Any = None):
        self.versions = Versions(harness=f"{HARNESS}@{harness_version}" if harness_version else HARNESS)
        self.tm = trace_mapper
        self.events: list[Event] = []; self.stats = new_stats(); self._seq = 0
        self.turn_agent: dict[str, str] = {}                 # turn span id -> agent span id (fallback only)
        self.by_name: dict[tuple[str, str], str] = {}        # (run, agent name) -> instance
        self.parent: dict[str, str] = {}                     # child instance -> parent instance
        self.handoffs: dict[tuple[str, str], dict] = {}      # (run, to_agent) -> {"from_instance", "when"}

    def _agent_span(self, p: dict) -> str | None:
        if self.tm is not None:
            a = self.tm.agent_span_of(p.get("span_id"))
            if a: return a
        if p.get("span_type") == "agent": return p.get("span_id")
        if p.get("span_type") == "turn":
            self.turn_agent[p["span_id"]] = p.get("parent_id"); return p.get("parent_id")
        par = p.get("parent_id")
        return self.turn_agent.get(par or "", par)

    def _instance(self, p: dict) -> str | None:
        run = p.get("trace_id") or ""
        if p.get("span_id"):
            aspan = self._agent_span(p)
            inst = self.tm.instance_of_agent_span(aspan) if self.tm is not None else aspan
            if inst and p.get("agent"): self.by_name[(run, p["agent"])] = inst
            return inst
        return self.by_name.get((run, p.get("agent") or ""))

    def _emit(self, etype: EventType, rec: dict, attrs: dict, status=None, correlation=None, payload_refs=None, identity_update=None, model=None) -> None:
        p = rec["payload"]; comp, counter = INTERFACES[etype]; self._seq += 1
        run = p.get("trace_id") or ""; inst = self._instance(p)
        ident = Identity(run_id=run, trace_id=run or None, span_id=p.get("span_id"), agent_definition=p.get("agent"), agent_instance_id=inst,
                         parent_agent_instance_id=self.parent.get(inst or ""), iteration=p.get("turn") or (self.tm.turn_of(p.get("span_id")) if self.tm is not None else None))
        if identity_update: ident = ident.model_copy(update=identity_update)
        corr = {k: v for k, v in (correlation or {}).items() if v}
        self.events.append(Event(event_id=new_event_id(run, rec["kind"], rec["ts"], etype.value, json.dumps(corr, sort_keys=True)), type=etype,
                                 native_type=f"openai_agents.{rec['kind']}", timestamp=ts(rec["ts"]), sequence=self._seq, identity=ident,
                                 versions=self.versions.model_copy(update={"model": model}) if model else self.versions,
                                 component=comp, counterpart=counter, correlation=corr, status=status, attrs=attrs,
                                 payload_refs={k: v for k, v in (payload_refs or {}).items() if v is not None},
                                 capture_tier=CaptureTier.A, source_channel=CHANNEL_HOOKS))

    def feed(self, rec: dict) -> None:
        k = rec["kind"]; p = rec["payload"]; run = p.get("trace_id") or ""
        cb = k.split(".", 1)[1] if "." in k else k
        if cb in ("on_agent_start", "on_start"):
            inst = self._instance(p); ho = self.handoffs.get((run, p.get("agent") or ""))
            if ho and inst and inst not in self.parent:
                self.parent[inst] = ho["from_instance"]
                self._emit(EventType.AGENT_SPAWNED, rec, {"child_agent_instance_id": inst, "child_agent_definition": p.get("agent"), "is_async": False},
                           correlation={"child_agent_instance_id": inst},
                           identity_update={"agent_instance_id": ho["from_instance"], "agent_definition": ho["from_agent"], "parent_agent_instance_id": None})
                return count(self.stats, "mapped", k)
            return count(self.stats, "structural", k)
        if cb in ("on_agent_end", "on_end"):
            inst = self._instance(p)
            self._emit(EventType.STOP, rec, {"reason": StopReason.AGENT_DECLARED_COMPLETE, "declared_by": "agent", "native_reason": "final_output"},
                       correlation={"final_agent_instance_id": inst}, payload_refs={"final_message": ref_from_digest(p.get("output"))})
            if inst in self.parent:
                self._emit(EventType.AGENT_RETURNED, rec, {"child_agent_instance_id": inst, "status": "ok", "result_hash": (p.get("output") or {}).get("sha256")},
                           correlation={"child_agent_instance_id": inst}, payload_refs={"result": ref_from_digest(p.get("output"))},
                           identity_update={"agent_instance_id": self.parent[inst], "agent_definition": None, "parent_agent_instance_id": None})
            return count(self.stats, "mapped", k)
        if cb == "on_handoff":
            src = dict(p, agent=p.get("from_agent"))
            # agent_hooks.on_handoff fires on the target with the target's span current; only run_hooks sees the source span.
            from_inst = self._instance(src) if k.startswith("run_hooks") else self.by_name.get((run, p.get("from_agent") or ""))
            self.handoffs.setdefault((run, p.get("to_agent") or ""), {"from_instance": from_inst, "from_agent": p.get("from_agent"), "when": rec["ts"]})
            return count(self.stats, "mapped", k)  # emitted as agent.spawned when the target agent starts (exact child id)
        if cb == "on_llm_start":
            turn_span = p.get("span_id") if p.get("span_type") == "turn" else None
            self._emit(EventType.MODEL_REQUEST, rec, {"model": p.get("model") or "", "num_messages": p.get("num_input_items"),
                                                      "num_tools": len(p.get("tools") or []) + len(p.get("handoff_tools") or []),
                                                      "tools_hash": sha(p.get("tools") or []), "system_hash": (p.get("system") or {}).get("sha256"), "query_source": "sdk"},
                       correlation={"turn_span_id": turn_span}, payload_refs={"input": ref_from_digest(p.get("input"))}, model=p.get("model"))
            return count(self.stats, "mapped", k)
        if cb == "on_llm_end":
            items = p.get("output_items") or []; hnames = set(p.get("handoff_tools") or [])
            calls = [i for i in items if i.get("type") == "function_call"]
            self._emit(EventType.MODEL_RESPONSE, rec, {"model": p.get("model") or "", "request_id": p.get("request_id"), "message_id": p.get("response_id"),
                                                       "input_tokens": p.get("input_tokens"), "output_tokens": p.get("output_tokens"),
                                                       "finish_reason": "tool_use" if calls else "end_turn", "num_tool_calls": len(calls)},
                       status="ok", correlation={"response_id": p.get("response_id"), "request_id": p.get("request_id")}, model=p.get("model"))
            for c in calls:
                if c.get("name") in hnames: continue
                a = c.get("arguments") or {}
                self._emit(EventType.TOOL_REQUESTED, rec, {"tool_name": c.get("name") or "", "tool_call_id": c.get("call_id") or "", "tool_source": "function",
                                                           "input_hash": a.get("sha256"), "input_size_bytes": a.get("size_bytes")},
                           correlation={"tool_call_id": c.get("call_id")}, payload_refs={"input": ref_from_digest(a or None)})
            for c in items:
                if c.get("type") == "compaction":
                    self._emit(EventType.CONTEXT_COMPACT, rec, {"trigger": "auto"}, correlation={"compaction_item_id": c.get("id")},
                               payload_refs={"summary": ref_from_digest(c.get("content"))})
            return count(self.stats, "mapped", k)
        if cb == "on_tool_start":
            a = p.get("arguments") or {}
            self._emit(EventType.TOOL_STARTED, rec, {"tool_name": p.get("tool_name") or "", "tool_call_id": p.get("tool_call_id") or "",
                                                     "tool_source": "mcp" if p.get("mcp") else "function", "input_hash": a.get("sha256"), "input_size_bytes": a.get("size_bytes")},
                       correlation={"tool_call_id": p.get("tool_call_id")})
            return count(self.stats, "mapped", k)
        if cb == "on_tool_end":
            # Hooks receive the model-facing string; a failure is visible only as the SDK's default error text.
            ok = not p.get("sdk_default_error"); r = p.get("result") or {}
            self._emit(EventType.TOOL_COMPLETED if ok else EventType.TOOL_FAILED, rec,
                       {"tool_name": p.get("tool_name") or "", "tool_call_id": p.get("tool_call_id") or "", "success": ok, "output_hash": r.get("sha256"),
                        "output_size_bytes": r.get("size_bytes"), "error_type": None if ok else "ToolError"},
                       status="ok" if ok else "error", correlation={"tool_call_id": p.get("tool_call_id")}, payload_refs={"output": ref_from_digest(r or None)})
            return count(self.stats, "mapped", k)
        if k in ("run_state.interruption", "run_state.approve", "run_state.reject"):
            etype, dec, status = {"run_state.interruption": (EventType.PERMISSION_REQUESTED, "pending", "unknown"),
                                  "run_state.approve": (EventType.PERMISSION_GRANTED, "granted", "ok"),
                                  "run_state.reject": (EventType.PERMISSION_DENIED, "denied", "denied")}[k]
            self._emit(etype, rec, {"actor": self.by_name.get((run, p.get("agent") or "")), "resource": p.get("tool_name"), "action": "invoke",
                                    "tool_call_id": p.get("tool_call_id"), "decision": dec,
                                    "source": DecisionSource.UNKNOWN if dec == "pending" else (DecisionSource.USER_PERMANENT if p.get("always") else DecisionSource.USER)},
                       status=status, correlation={"tool_call_id": p.get("tool_call_id")},
                       payload_refs={"reason": ref_from_digest(p.get("message"))})
            return count(self.stats, "mapped", k)
        if k == "wrap.responses.compact":
            items = p.get("output_items") or []
            self._emit(EventType.CONTEXT_COMPACT, rec, {"trigger": "auto", "tokens_before": p.get("input_tokens"), "tokens_after": p.get("output_tokens"),
                                                        "num_preserved_messages": len(items)},
                       correlation={"compaction_item_id": next((i.get("id") for i in items if i.get("type") == "compaction"), None)},
                       payload_refs={"summary": next((ref_from_digest(i.get("content")) for i in items if i.get("type") == "compaction"), None)})
            return count(self.stats, "mapped", k)
        self._emit(EventType.UNKNOWN, rec, {"native": p})
        count(self.stats, "unmapped", k)


def parse_hooks(records: Iterable[dict], harness_version: str | None = None, trace_mapper: Any = None) -> tuple[list[Event], dict]:
    m = HookMapper(harness_version, trace_mapper)
    for r in records:
        if r.get("channel") == "hooks": m.feed(r)
    return m.events, m.stats
