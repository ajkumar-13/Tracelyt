"""OpenAI Agents SDK Tier A instrumentor (Proof B, second harness).

The fixture was captured by scripts/capture_openai_agents.py (openai-agents 0.24.0, scripted model, no network). These
tests replay the raw native records with the system interpreter; the live test runs only where `agents` is importable."""
import collections, json, os
import pytest

from harness_engine.adapters.openai_agents import load_records, normalize_records
from harness_engine.model.events import Component, EventType as T

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIX = os.path.join(ROOT, "tests", "fixtures", "openai_agents", "scenario1")
MAIN_RUN = "trace_00000000000000000000000000000001"
SESSION_RUN = "trace_00000000000000000000000000000002"

# Main run: triage -> lookup_order -> handoff to billing -> failing tool -> two approval interruptions -> approve one,
# reject one, resume -> approved tool runs -> final answer with a compaction item.
EXPECTED_MAIN = [
    T.RUN_STARTED,
    T.ITERATION_STARTED, T.UNKNOWN,  # input guardrail span
    T.MODEL_REQUEST, T.MODEL_RESPONSE, T.TOOL_REQUESTED, T.TOOL_STARTED, T.UNKNOWN,  # custom span inside the tool
    T.TOOL_COMPLETED, T.ITERATION_COMPLETED,
    T.ITERATION_STARTED, T.MODEL_REQUEST, T.MODEL_RESPONSE, T.AGENT_SPAWNED, T.ITERATION_COMPLETED,
    T.ITERATION_STARTED, T.MODEL_REQUEST, T.MODEL_RESPONSE, T.TOOL_REQUESTED, T.TOOL_STARTED, T.TOOL_FAILED, T.ITERATION_COMPLETED,
    T.ITERATION_STARTED, T.MODEL_REQUEST, T.MODEL_RESPONSE, T.TOOL_REQUESTED, T.TOOL_REQUESTED,
    T.PERMISSION_REQUESTED, T.PERMISSION_REQUESTED, T.ITERATION_COMPLETED,
    T.RUN_COMPLETED, T.PERMISSION_GRANTED, T.PERMISSION_DENIED,
    T.RUN_RESUMED, T.TOOL_STARTED, T.TOOL_COMPLETED,
    T.ITERATION_STARTED, T.MODEL_REQUEST, T.MODEL_RESPONSE, T.CONTEXT_COMPACT, T.STOP, T.ITERATION_COMPLETED,
    T.AGENT_RETURNED, T.RUN_COMPLETED,
]


@pytest.fixture(scope="module")
def norm():
    return normalize_records(load_records(os.path.join(FIX, "raw.jsonl")))


def _run(events, run_id):
    return [e for e in events if e.identity.run_id == run_id]


def test_replay_matches_committed_events(norm):
    events, _ = norm
    committed = [json.loads(l) for l in open(os.path.join(FIX, "events.jsonl")) if l.strip()]
    assert [(e.event_id, e.type.value) for e in events] == [(c["event_id"], c["type"]) for c in committed]


def test_scenario_emits_expected_event_types_in_order(norm):
    events, _ = norm
    assert [e.type for e in _run(events, MAIN_RUN)] == EXPECTED_MAIN
    sess = _run(events, SESSION_RUN)
    assert [e.type for e in sess] == [T.RUN_STARTED, T.ITERATION_STARTED, T.MODEL_REQUEST, T.MODEL_RESPONSE, T.STOP,
                                      T.ITERATION_COMPLETED, T.CONTEXT_COMPACT, T.RUN_COMPLETED]
    wrap = [e for e in sess if e.type == T.CONTEXT_COMPACT][0]
    assert wrap.native_type == "openai_agents.wrap.responses.compact" and wrap.component == Component.COMPACTOR
    assert wrap.attrs["tokens_before"] == 640 and "summary" in wrap.payload_refs


def test_tool_requested_links_to_result_by_tool_call_id(norm):
    events, _ = norm
    main = _run(events, MAIN_RUN)
    req = {e.correlation["tool_call_id"]: e for e in main if e.type == T.TOOL_REQUESTED}
    done = {e.correlation["tool_call_id"]: e for e in main if e.type in (T.TOOL_COMPLETED, T.TOOL_FAILED)}
    assert set(req) == {"call_lookup_1", "call_ledger_1", "call_refund_1", "call_close_1"}
    assert set(done) == {"call_lookup_1", "call_ledger_1", "call_refund_1"}  # close_account was rejected, never ran
    for cid, d in done.items():
        assert req[cid].timestamp <= d.timestamp and req[cid].attrs["tool_name"] == d.attrs["tool_name"]
        assert "+" in d.source_channel, "hooks and tracing should merge on tool_call_id"
    assert done["call_ledger_1"].type == T.TOOL_FAILED and done["call_ledger_1"].attrs["error_type"] == "ToolError"
    perms = {(e.type, e.correlation["tool_call_id"]) for e in main if e.type.value.startswith("permission.")}
    assert perms == {(T.PERMISSION_REQUESTED, "call_refund_1"), (T.PERMISSION_REQUESTED, "call_close_1"),
                     (T.PERMISSION_GRANTED, "call_refund_1"), (T.PERMISSION_DENIED, "call_close_1")}


def test_agent_spawned_links_to_agent_returned(norm):
    events, _ = norm
    main = _run(events, MAIN_RUN)
    spawned = [e for e in main if e.type == T.AGENT_SPAWNED]
    returned = [e for e in main if e.type == T.AGENT_RETURNED]
    assert len(spawned) == 1 and len(returned) == 1
    s, r = spawned[0], returned[0]
    child = s.attrs["child_agent_instance_id"]
    assert child == r.attrs["child_agent_instance_id"] == s.correlation["child_agent_instance_id"] == r.correlation["child_agent_instance_id"]
    assert s.attrs["child_agent_definition"] == "billing" and s.attrs["via_tool_call_id"] == "call_handoff_1"
    assert s.identity.agent_instance_id == r.identity.agent_instance_id != child  # parent (triage) owns both ends
    billing = [e for e in main if e.identity.agent_definition == "billing"]
    # every billing event, including the resumed segment's new agent span, resolves to the spawned instance
    assert billing and {e.identity.agent_instance_id for e in billing} == {child}
    assert {e.identity.parent_agent_instance_id for e in billing} == {s.identity.agent_instance_id}


def test_every_mapped_event_validates_and_carries_no_inline_content(norm):
    events, _ = norm
    for e in events:
        if e.type != T.UNKNOWN:
            assert e.validated_attrs() is not None, e
        else:
            assert e.native_type and e.attrs.get("native") is not None
        assert e.capture_tier.value == "A" and e.versions.harness == "openai-agents@0.24.0"
        assert set(e.source_channel.split("+")) <= {"openai_agents.tracing", "openai_agents.hooks"}
    blob = json.dumps([e.model_dump(mode="json") for e in events])
    for text in ("Please refund order A-100", "Refunded 42 on A-100", "ledger service unavailable", "Route customer requests"):
        assert text not in blob, text
    model = [e for e in events if e.type == T.MODEL_RESPONSE]
    assert all(e.attrs["input_tokens"] and e.versions.model == "scripted-model-1" for e in model)


def test_fixtures_hold_no_identifying_values():
    import re
    for name in ("raw.jsonl", "events.jsonl", "stats.json"):
        s = open(os.path.join(FIX, name)).read()
        assert not re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}", s), name
        assert "/tmp/" not in s and "/home/" not in s and "sk-" not in s, name


def test_gate_proof_b_openai_agents_exception_rate_under_10_percent(norm):
    _, stats = norm
    assert stats["native_signals"] == stats["mapped"] + stats["structural"] + stats["unmapped"]
    assert stats["unmapped_names"] == {"span.guardrail": 1, "span.custom:orders.db_lookup": 1}, stats["unmapped_names"]
    assert stats["v01_exception_rate"] < 0.10, stats
    assert stats["v01_exception_rate_tracing_only"] < 0.10, stats


def test_live_scenario_when_sdk_installed(tmp_path):
    pytest.importorskip("agents.tracing")
    import subprocess, sys
    subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "capture_openai_agents.py"), str(tmp_path)], check=True,
                   env={**os.environ, "PYTHONPATH": os.path.join(ROOT, "src")})
    events, stats = normalize_records(load_records(str(tmp_path / "raw.jsonl")))
    assert [e.type for e in events if e.identity.run_id == MAIN_RUN] == EXPECTED_MAIN
    assert stats["v01_exception_rate"] < 0.10
