"""Replay engine tests (SPEC-02 §3, §5): cassette loading, S1 matching across transports, divergence reporting,
and the Messages API streaming encoder. Fixtures: the scrubbed proofA cassette (first three calls complete)."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
from harness_engine.replay.cassette import Cassette, normalize_request, canonical, sha
from harness_engine.replay.match import Matcher
from harness_engine.replay.server import sse_events

FIX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", "claude_code", "rawbodies")


def _cassette():
    """The committed fixture is the full scrubbed proofA cassette: 11 model calls, two conversations (main agent
    and the reviewer subagent), linked by Anthropic message threads."""
    return Cassette.from_raw_bodies(FIX)


def test_recorded_requests_match_exactly_in_order():
    c = _cassette(); m = Matcher(c)
    assert len(c.envelopes) == 11
    assert [m.match(e.request).level for e in c.envelopes] == ["exact"] * 11
    assert m.summary()["coverage"] == 1.0 and m.summary()["first_divergence_seq"] is None


def test_non_threaded_history_requests_match_at_delta_level():
    """A harness that sends the whole history instead of message threads is matched by the tool_result ids it answers."""
    c = _cassette(); m = Matcher(c); hist = {}
    levels = []
    for e in c.envelopes:
        req = dict(e.request); req.pop("thread", None)
        if e.previous_message_id:
            prev = c.by_response_id(e.previous_message_id)
            req["messages"] = hist[prev.index] + [{"role": "assistant", "content": prev.response["content"]}] + e.request["messages"]
        hist[e.index] = req["messages"]
        r = m.match(req); levels.append((r.level, r.envelope.index))
    assert [i for _, i in levels] == list(range(11))                      # every call routed to its own envelope
    assert all(l in ("exact", "delta") for l, _ in levels)
    assert [l for l, _ in levels][:2] == ["exact", "delta"]


def test_changed_tool_result_is_reported_as_divergence_not_masked():
    c = _cassette(); m = Matcher(c, policy="report")
    m.match(c.envelopes[0].request)
    req = json.loads(json.dumps(c.envelopes[1].request))
    req["messages"][0]["content"][0]["content"] = "File created somewhere else"
    r = m.match(req)
    assert r.level == "positional-miss" and r.divergence is not None
    assert any(d["path"].endswith("content") for d in r.divergence.field_diff)
    assert m.summary()["first_divergence_seq"] == 2


def test_strict_policy_stops_at_first_miss():
    c = _cassette(); m = Matcher(c, policy="strict")
    req = json.loads(json.dumps(c.envelopes[0].request)); req["messages"][0]["content"] = "something else"
    r = m.match(req)
    assert r.envelope is None and r.level == "positional-miss"


def test_normalization_ignores_harness_injected_context_and_volatile_ids():
    c = _cassette(); req = json.loads(json.dumps(c.envelopes[0].request))
    req["metadata"] = {"user_id": "other"}; req["thread"] = {"type": "create"}
    req["messages"][0]["content"].insert(0, {"type": "text", "text": "<system-reminder>\nToday's date is 2099-01-01.\n</system-reminder>"})
    assert sha(canonical(normalize_request(req))) == c.envelopes[0].normalized_key


def test_sse_encoding_round_trips_content_blocks():
    c = _cassette(); msg = c.envelopes[0].response
    evs = list(sse_events(msg))
    names = [n for n, _ in evs]
    assert names[0] == "message_start" and names[-1] == "message_stop" and "message_delta" in names
    starts = [e for n, e in evs if n == "content_block_start"]
    assert [s["content_block"]["type"] for s in starts] == [b["type"] for b in msg["content"]]
    tool = [e for n, e in evs if n == "content_block_delta" and e["delta"]["type"] == "input_json_delta"]
    assert json.loads(tool[0]["delta"]["partial_json"]) == next(b["input"] for b in msg["content"] if b["type"] == "tool_use")
