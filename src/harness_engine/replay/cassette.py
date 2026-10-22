"""Replay cassette: the recorded model-call boundary of one run (SPEC-02 §2, R2 fixtures).

Source today: Claude Code's `OTEL_LOG_RAW_API_BODIES=file:<dir>` side channel (index.jsonl + request/response
JSON files). Each entry becomes a ModelCallEnvelope. Conversation linkage uses Anthropic message threads
(`thread.type == "continue"` with `previous_message_id`), which is the server-side state SPEC-02 §12 Q2 asks
about: on replay the server *is* the state, so the recorded response id is the conversation key.
"""
from __future__ import annotations
import hashlib, json, os, re
from dataclasses import dataclass, field
from typing import Any, Optional

# ---- normalization profile `claude_code_v1` (SPEC-02 §3, S1 verification key) ----------------------------
# Volatile fields the harness or the API change on every run. Dropped before hashing; recorded in the profile.
VOLATILE_TOP = ("metadata", "thread", "diagnostics")
BILLING_HEADER = re.compile(r"^x-anthropic-billing-header:.*$", re.M)
SYSTEM_REMINDER = re.compile(r"<system-reminder>.*?</system-reminder>\s*", re.S)
TOTAL_TOKENS = re.compile(r"<total_tokens>\d+ tokens left</total_tokens>")
# Harness-generated identifiers inside tool results (subagent ids, task output paths, session ids).
VOLATILE_IDS = [
    (re.compile(r"agentId: [0-9a-f]{12,}"), "agentId: <id>"),
    (re.compile(r"to: '[0-9a-f]{12,}'"), "to: '<id>'"),
    (re.compile(r"output_file: \S+"), "output_file: <path>"),
    (re.compile(r"/tasks/[0-9a-f]{12,}\.output"), "/tasks/<id>.output"),
    (re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"), "<uuid>"),
]
# Environment noise inside tool outputs that carries no state: wall-clock durations printed by test runners and
# shells. Exit codes and file state are compared unnormalized.
VOLATILE_NOISE = [
    (re.compile(r"\bin \d+\.\d+s\b"), "in <t>s"),
    (re.compile(r"\b\d+\.\d+ ?(s|ms|seconds)\b"), "<t>\\1"),
]


def _norm_text(t: str) -> str:
    t = SYSTEM_REMINDER.sub("", t)
    t = TOTAL_TOKENS.sub("", t)
    t = BILLING_HEADER.sub("", t)
    for rx, rep in VOLATILE_IDS + VOLATILE_NOISE:
        t = rx.sub(rep, t)
    return t.strip()


def _norm_block(b: Any) -> Any:
    if isinstance(b, str):
        return _norm_text(b)
    if not isinstance(b, dict):
        return b
    b = dict(b); b.pop("cache_control", None)
    t = b.get("type")
    if t == "text":
        b["text"] = _norm_text(b.get("text", ""))
    elif t == "thinking":
        b = {"type": "thinking"}                     # content redacted by the channel; signature is per-response
    elif t == "redacted_thinking":
        b = {"type": "redacted_thinking"}
    elif t == "tool_result":
        c = b.get("content")
        b["content"] = _drop_empty([_norm_block(x) for x in c]) if isinstance(c, list) else _norm_text(c or "")
    elif t == "tool_use":
        b = {"type": "tool_use", "id": b.get("id"), "name": b.get("name"), "input": b.get("input")}
    return b


def _drop_empty(blocks: list) -> list:
    """Harness-injected context (system reminders, token budgets) normalizes to empty text; drop those blocks."""
    return [b for b in blocks if not (isinstance(b, dict) and b.get("type") == "text" and not b.get("text"))]


def normalize_request(req: dict) -> dict:
    r = {k: v for k, v in req.items() if k not in VOLATILE_TOP}
    sysm = r.get("system")
    if isinstance(sysm, list):
        r["system"] = _drop_empty([_norm_block(b) for b in sysm])
    elif isinstance(sysm, str):
        r["system"] = _norm_text(sysm)
    msgs = []
    for m in r.get("messages", []):
        c = m.get("content")
        msgs.append({"role": m.get("role"), "content": _drop_empty([_norm_block(b) for b in c]) if isinstance(c, list) else _norm_text(c or "")})
    r["messages"] = msgs
    if "tools" in r:
        r["tools"] = [{"name": t.get("name"), "schema": sha(json.dumps(t.get("input_schema", {}), sort_keys=True))} for t in r["tools"]]
    return r


def normalize_delta(req: dict) -> dict:
    """The new input the harness is sending: the last message only. Threaded requests carry one new message;
    non-threaded requests carry the whole history, so only the last message is compared."""
    return {"messages": normalize_request(req)["messages"][-1:]}


def normalize_config(req: dict) -> dict:
    """The harness-side configuration of a call: model, params, system prompt, tool roster, betas. Drift here is
    harness configuration drift (version, entrypoint, feature flags), not environment divergence."""
    r = normalize_request(req)
    return {k: v for k, v in r.items() if k != "messages"}


def sha(s: str | bytes) -> str:
    return hashlib.sha256(s.encode() if isinstance(s, str) else s).hexdigest()


def canonical(o: Any) -> str:
    return json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


@dataclass
class ModelCallEnvelope:
    index: int                                  # invocation_index in recording order
    query_source: str                           # "sdk" (main agent) or "agent:<kind>:<name>"
    request: dict
    response: dict
    request_id: Optional[str] = None
    exact_key: str = ""                         # sha256 of the request minus VOLATILE_TOP
    normalized_key: str = ""                    # sha256 of normalize_request(request)
    delta_key: str = ""                         # sha256 of normalize_delta(request): the new message only
    config_key: str = ""                        # sha256 of normalize_config(request): model, params, system, tools
    served: bool = False

    @property
    def response_id(self) -> str:
        return self.response.get("id", "")

    @property
    def previous_message_id(self) -> Optional[str]:
        th = self.request.get("thread") or {}
        return th.get("previous_message_id") if th.get("type") == "continue" else None

    @property
    def is_create(self) -> bool:
        return self.previous_message_id is None

    @property
    def conversation_key(self) -> str:
        return conversation_key(self.request)


def conversation_key(req: dict) -> str:
    """Where this call sits in its conversation, independent of transport.

    Threaded requests (Anthropic message threads) carry `previous_message_id`; non-threaded requests carry the
    whole history, whose last user message holds the tool_result ids the harness is answering. Both forms map
    to the same key when the tool_use ids are the recorded ones, which replay guarantees because it serves
    the recorded responses. A first call has no tool results: key "initial".
    """
    th = req.get("thread") or {}
    if th.get("type") == "continue" and th.get("previous_message_id"):
        return "prev:" + th["previous_message_id"]
    msgs = req.get("messages") or []
    if not msgs:
        return "initial"
    last = msgs[-1]
    c = last.get("content")
    ids = [b.get("tool_use_id") for b in c if isinstance(b, dict) and b.get("type") == "tool_result"] if isinstance(c, list) else []
    return "results:" + ",".join(sorted(x for x in ids if x)) if ids else "initial"


@dataclass
class Cassette:
    run_id: str
    envelopes: list[ModelCallEnvelope] = field(default_factory=list)
    source_dir: str = ""

    @classmethod
    def from_raw_bodies(cls, d: str) -> "Cassette":
        idx = [json.loads(l) for l in open(os.path.join(d, "index.jsonl")) if l.strip()]
        env, run_id = [], ""
        for i, j in enumerate(idx):
            run_id = run_id or j.get("session_id", "")
            req = json.load(open(os.path.join(d, j["request_file"])))
            resp = json.load(open(os.path.join(d, j["response_file"])))
            e = ModelCallEnvelope(index=i, query_source=j.get("query_source", "sdk"), request=req, response=resp, request_id=j.get("request_id"))
            e.exact_key = sha(canonical({k: v for k, v in req.items() if k not in VOLATILE_TOP}))
            e.normalized_key = sha(canonical(normalize_request(req)))
            e.delta_key = sha(canonical(normalize_delta(req)))
            e.config_key = sha(canonical(normalize_config(req)))
            env.append(e)
        return cls(run_id=run_id, envelopes=env, source_dir=d)

    def by_response_id(self, rid: str) -> Optional[ModelCallEnvelope]:
        for e in self.envelopes:
            if e.response_id == rid:
                return e
        return None
