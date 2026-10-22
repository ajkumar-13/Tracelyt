"""Proof B (second harness): capture the OpenAI Agents SDK under the Tier A instrumentor with a scripted model.

No API key and no network: every model turn comes from ScriptedModel, the OpenAI trace exporter is replaced by our
processor, and session compaction calls a fake `responses.compact` client. Real SDK code runs everything else:
function tools, an input guardrail, a handoff, needs_approval interruptions with RunState approve/reject and resume,
RunHooks + AgentHooks, a model-emitted `compaction` item, and an OpenAIResponsesCompactionSession (streamed run).

Run with an interpreter that has openai-agents installed:
    PYTHONPATH=src /path/to/venv/bin/python scripts/capture_openai_agents.py [out_dir]
Writes <out_dir>/raw.jsonl (native records), events.jsonl (normalized v0.1 events), stats.json.
"""
from __future__ import annotations
import asyncio, json, os, re, sys
from types import SimpleNamespace

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from agents import (Agent, GuardrailFunctionOutput, InputGuardrail, RunConfig, Runner, SQLiteSession, function_tool,
                    set_trace_processors)
from agents.memory import OpenAIResponsesCompactionSession
from agents.tracing import custom_span
from openai.types.responses import ResponseUsage
from openai.types.responses.response_usage import InputTokensDetails, OutputTokensDetails

from harness_engine.adapters.openai_agents import (HarnessAgentHooks, HarnessRunHooks, HarnessTracingProcessor, HookRecorder,
                                                   normalize_records)
from harness_engine.adapters.openai_agents.common import harness_version
from harness_engine.adapters.openai_agents.scripted_model import ScriptedModel, Step, call, compaction, text

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "tests", "fixtures", "openai_agents", "scenario1")


# ---- tools ----------------------------------------------------------------------------------------------------
@function_tool
def lookup_order(order_id: str) -> str:
    """Look up an order by id."""
    with custom_span("orders.db_lookup", {"table": "orders"}):
        return json.dumps({"order_id": order_id, "total": 42, "status": "delivered"})


@function_tool
def ledger_balance(order_id: str) -> str:
    """Read the ledger balance for an order (always fails in this scenario)."""
    raise RuntimeError("ledger service unavailable")


@function_tool(needs_approval=True)
def refund_order(order_id: str, amount: int) -> str:
    """Refund an order. Requires human approval."""
    return f"refunded {amount} on {order_id}"


@function_tool(needs_approval=True)
def close_account(order_id: str) -> str:
    """Close the customer account. Requires human approval."""
    return "account closed"


async def no_account_numbers(ctx, agent, user_input):
    return GuardrailFunctionOutput(output_info={"checked": True}, tripwire_triggered=False)


MAIN_SCRIPT = [
    Step([call("lookup_order", {"order_id": "A-100"}, "call_lookup_1")], input_tokens=120, output_tokens=18),
    Step([call("transfer_to_billing", {}, "call_handoff_1")], input_tokens=160, output_tokens=9),
    Step([call("ledger_balance", {"order_id": "A-100"}, "call_ledger_1")], input_tokens=210, output_tokens=15),
    Step([call("refund_order", {"order_id": "A-100", "amount": 42}, "call_refund_1"),
          call("close_account", {"order_id": "A-100"}, "call_close_1")], input_tokens=260, output_tokens=30),
    Step([compaction("cmp_main_1"), text("Refunded 42 on A-100. The account stays open.", "msg_final_1")], input_tokens=90, output_tokens=16),
]


class _FakeResponses:
    """Stands in for AsyncOpenAI().responses: only `compact` is called by the compaction session."""
    def __init__(self): self.calls = 0
    async def compact(self, **kwargs):
        self.calls += 1
        return SimpleNamespace(output=[{"type": "compaction", "id": f"cmp_session_{self.calls}", "encrypted_content": "c2Vzc2lvbi1jb21wYWN0aW9u"}],
                               usage=ResponseUsage(input_tokens=640, output_tokens=48, total_tokens=688,
                                                   input_tokens_details=InputTokensDetails(cached_tokens=0, cache_write_tokens=0),
                                                   output_tokens_details=OutputTokensDetails(reasoning_tokens=0)))


async def run_scenario(proc: HarnessTracingProcessor, rec: HookRecorder) -> dict:
    model = ScriptedModel(steps=list(MAIN_SCRIPT))
    billing = Agent(name="billing", instructions="Settle billing questions.", model=model,
                    tools=[ledger_balance, refund_order, close_account], hooks=HarnessAgentHooks(rec))
    triage = Agent(name="triage", instructions="Route customer requests.", model=model, tools=[lookup_order], handoffs=[billing],
                   input_guardrails=[InputGuardrail(guardrail_function=no_account_numbers, name="no_account_numbers")])
    cfg = RunConfig(workflow_name="proof-b-scenario1", trace_include_sensitive_data=True)
    hooks = HarnessRunHooks(rec)

    r1 = await Runner.run(triage, "Please refund order A-100.", hooks=hooks, run_config=cfg)
    pending = rec.record_interruptions(r1)
    state = r1.to_state()
    for item in pending:
        if item.tool_name == "refund_order": rec.approve(state, item)
        else: rec.reject(state, item, rejection_message="Account closure not authorised.")
    r2 = await Runner.run(triage, state, hooks=hooks, run_config=cfg)
    assert not r2.interruptions and r2.final_output, r2

    # Session compaction (OpenAIResponsesCompactionSession) on a streamed run: no span, no hook; instrumentor wraps the client.
    client = rec.wrap_compaction_client(SimpleNamespace(responses=_FakeResponses()))
    session = OpenAIResponsesCompactionSession("proof-b-session", SQLiteSession("proof-b-session"), client=client, model="gpt-4.1",
                                               should_trigger_compaction=lambda ctx: True)
    solo = Agent(name="notes", instructions="Keep short notes.", model=ScriptedModel(steps=[Step([text("Noted.", "msg_notes_1")])]))
    r3 = Runner.run_streamed(solo, "Remember: order A-100 refunded.", session=session, run_config=RunConfig(workflow_name="proof-b-session"))
    async for _ in r3.stream_events():
        pass
    return {"interruptions": [(i.tool_name) for i in pending], "final_output": r2.final_output, "session_final": r3.final_output,
            "model_calls": len(model.calls)}


# ---- scrub: stable ids, no identifying values ----------------------------------------------------------------
_ID = re.compile(r"\b(trace|span|group)_[0-9a-f]{24,32}\b")
_SCRUB = [(re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}"), "user@example.com"),
          (re.compile(r"/tmp/claude-0/[^\"' ,}\]]*"), "/work/tmp"), (re.compile(r"/home/[^\"' ,}\]]*"), "/work/home"),
          (re.compile(r"sk-[A-Za-z0-9_-]{16,}"), "sk-REDACTED")]


def scrub(records: list[dict]) -> list[dict]:
    blob = json.dumps(records); mapping: dict[str, str] = {}
    def _sub(m):
        k = m.group(0)
        if k not in mapping:
            n = sum(1 for v in mapping.values() if v.startswith(m.group(1))) + 1
            mapping[k] = f"{m.group(1)}_{n:0{32 if m.group(1) == 'trace' else 24}d}"
        return mapping[k]
    blob = _ID.sub(_sub, blob)
    for rx, rep in _SCRUB: blob = rx.sub(rep, blob)
    return json.loads(blob)


def main() -> None:
    proc = HarnessTracingProcessor(); rec = HookRecorder()
    set_trace_processors([proc])  # replaces the OpenAI exporter: nothing leaves the process
    summary = asyncio.run(run_scenario(proc, rec))
    version = harness_version()
    meta = {"channel": "meta", "kind": "capture", "harness_version": version, "scenario": "scenario1", "model": "scripted-model-1",
            "trace_include_sensitive_data": True, "include_task_and_turn_spans": True}
    raw = [meta] + sorted(proc.records + rec.records, key=lambda r: r["ts"])
    live_events, _ = normalize_records(raw)
    raw = scrub(raw)
    events, stats = normalize_records(raw)
    assert [e.type for e in events] == [e.type for e in live_events], "replay of scrubbed records must match the live mapping"
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "raw.jsonl"), "w") as f:
        for r in raw: f.write(json.dumps(r, sort_keys=True) + "\n")
    with open(os.path.join(OUT, "events.jsonl"), "w") as f:
        for e in events: f.write(e.model_dump_json(exclude_none=True) + "\n")
    with open(os.path.join(OUT, "stats.json"), "w") as f:
        json.dump(stats, f, indent=2, sort_keys=True, default=str)
    print(f"openai-agents {version}; scenario: {summary}")
    print(f"native signals: {stats['native_signals']} (tracing {stats['tracing']['records']}, hooks {stats['hooks']['records']})")
    print(f"mapped: {stats['mapped']}  structural: {stats['structural']}  unmapped: {stats['unmapped']} {stats['unmapped_names']}")
    print(f"structural detail: tracing {stats['tracing']['structural_names']} hooks {stats['hooks']['structural_names']}")
    print(f"v0.1 exception rate: {stats['v01_exception_rate']:.4f} (tracing only {stats['v01_exception_rate_tracing_only']:.4f})")
    print(f"events: {len(events)} after merge ({stats['merge']})")


if __name__ == "__main__":
    main()
