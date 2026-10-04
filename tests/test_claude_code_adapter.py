import json, os, collections
import pytest
from harness_engine.normalize.claude_code import normalize_dir
from harness_engine.model.events import EventType, Component

FIX = os.path.join(os.path.dirname(__file__), "fixtures", "claude_code")


def _count(events):
    return collections.Counter(e.type for e in events)


def test_proof_a_run_normalizes_with_low_exception_rate():
    events, stats = normalize_dir(FIX, session_id="2514bbc3-9419-453a-a491-d07ac2cabfbf")
    c = _count(events)
    assert c[EventType.RUN_STARTED] >= 1
    assert c[EventType.CONTEXT_PROVENANCE_LOADED] >= 1
    assert c[EventType.TOOL_REQUESTED] == 9
    assert c[EventType.TOOL_FAILED] >= 1 and c[EventType.TOOL_COMPLETED] >= 7
    # one reviewer subagent, plus the subagent Claude Code spawns to perform /compact (observed, see proof-A findings)
    assert c[EventType.AGENT_SPAWNED] >= 1 and c[EventType.AGENT_RETURNED] == 2
    assert c[EventType.CONTEXT_COMPACT] == 1, c
    assert c[EventType.MODEL_RESPONSE] >= 10 and c[EventType.MODEL_REQUEST] >= 10
    assert stats["v01_exception_rate_excluding_hook_domain"] < 0.10, stats
    # every event validates against its attribute model
    for e in events:
        if e.type != EventType.UNKNOWN:
            assert e.validated_attrs() is not None


def test_cross_channel_merge_joins_tool_events_and_compaction():
    events, stats = normalize_dir(FIX, session_id="2514bbc3-9419-453a-a491-d07ac2cabfbf")
    tool_done = [e for e in events if e.type in (EventType.TOOL_COMPLETED, EventType.TOOL_FAILED)]
    merged = [e for e in tool_done if "+" in e.source_channel]
    assert len(merged) >= 7, [e.source_channel for e in tool_done]
    comp = [e for e in events if e.type == EventType.CONTEXT_COMPACT][0]
    assert comp.attrs["tokens_before"] == 32800 and comp.attrs["tokens_after"] == 2496
    assert "summary" in comp.payload_refs  # from PostCompact hook
    assert comp.component == Component.COMPACTOR


def test_subagent_delegation_edge_has_both_instance_and_cost():
    events, _ = normalize_dir(FIX, session_id="2514bbc3-9419-453a-a491-d07ac2cabfbf")
    ret = [e for e in events if e.type == EventType.AGENT_RETURNED and e.attrs.get("child_agent_definition") == "reviewer"]
    assert len(ret) == 1
    assert ret[0].attrs["child_agent_instance_id"] and ret[0].attrs.get("total_tokens"), ret[0]
    sub_model_calls = [e for e in events if e.type == EventType.MODEL_RESPONSE and e.identity.agent_definition == "reviewer"]
    assert sub_model_calls, "subagent model calls should carry the agent definition"


def test_pii_is_stripped_by_default():
    events, stats = normalize_dir(FIX, session_id="2514bbc3-9419-453a-a491-d07ac2cabfbf")
    assert stats["otel_logs"]["pii_attrs_stripped"] > 0
    blob = json.dumps([e.model_dump(mode="json") for e in events])
    assert "user.email" not in blob and "account_uuid" not in blob


def test_proof_d_loop_run_has_eight_identical_failed_tool_calls():
    d = os.path.join(FIX, "proofD")
    sid = [l.split("=")[1].strip() for l in open(os.path.join(d, "sessions.txt")) if l.startswith("loop=")][0]
    events, _ = normalize_dir(d, session_id=sid)
    failed = [e for e in events if e.type == EventType.TOOL_FAILED]
    assert len(failed) == 8
    req = [e for e in events if e.type == EventType.TOOL_REQUESTED]
    assert len({e.attrs["input_hash"] for e in req}) == 1, "all eight requests should be byte-identical"
    stop = [e for e in events if e.type == EventType.STOP]
    assert stop and stop[0].attrs["verification_present"] is False
