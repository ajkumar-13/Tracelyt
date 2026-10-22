"""S1 matching: positional cursor per conversation, verified against exact or normalized hash (SPEC-02 §3).

A miss is recorded as a divergence with a field diff and is never masked. Policies:
  strict  -> stop serving at the first miss (the harness sees an error)
  report  -> serve the positional candidate anyway and record the divergence (fidelity downgraded)
Live branching (proxy to the real provider after a miss) is Phase 2.
"""
from __future__ import annotations
import json
from dataclasses import dataclass, field, asdict
from typing import Any, Optional

from .cassette import Cassette, ModelCallEnvelope, VOLATILE_TOP, canonical, conversation_key, normalize_config, normalize_delta, normalize_request, sha


@dataclass
class Divergence:
    seq: int
    expected_key: str
    actual_key: str
    field_diff: list[dict]
    candidate_index: Optional[int]
    reason: str


@dataclass
class MatchResult:
    seq: int
    envelope: Optional[ModelCallEnvelope]
    level: str                      # exact | normalized | delta | positional-miss | no-candidate
    divergence: Optional[Divergence] = None
    config_drift: Optional[list[dict]] = None   # harness-configuration differences, reported separately


def _diff(a: Any, b: Any, path: str = "$", out: list | None = None, limit: int = 40) -> list[dict]:
    out = [] if out is None else out
    if len(out) >= limit:
        return out
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                out.append({"path": f"{path}.{k}", "kind": "missing_in_" + ("actual" if k not in b else "expected")})
            else:
                _diff(a[k], b[k], f"{path}.{k}", out, limit)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append({"path": path, "kind": "length", "expected": len(a), "actual": len(b)})
        for i, (x, y) in enumerate(zip(a, b)):
            _diff(x, y, f"{path}[{i}]", out, limit)
    elif a != b:
        ex, ac = canonical(a), canonical(b)
        out.append({"path": path, "kind": "value", "expected": ex[:200], "actual": ac[:200]})
    return out


class Matcher:
    def __init__(self, cassette: Cassette, policy: str = "report"):
        assert policy in ("strict", "report")
        self.cassette, self.policy = cassette, policy
        self.seq = 0
        self.results: list[MatchResult] = []

    def _candidate(self, req: dict) -> tuple[Optional[ModelCallEnvelope], str]:
        key = conversation_key(req)
        if key != "initial":
            # threaded recording answering a threaded replay: previous_message_id is the response we served;
            # a non-threaded replay (or recording) is keyed by the tool_result ids it answers.
            prev = key[5:] if key.startswith("prev:") else None
            for e in self.cassette.envelopes:
                if e.served: continue
                if prev and e.previous_message_id == prev: return e, "conversation"
                if e.conversation_key == key: return e, "conversation"
                if key.startswith("results:") and e.previous_message_id and self._results_key_of_threaded(e) == key:
                    return e, "conversation"
                if prev and e.conversation_key.startswith("results:") and self._prev_of_results(prev) == e.conversation_key:
                    return e, "conversation"
            return None, f"no unserved continuation for {key}"
        nk = sha(canonical(normalize_request(req)))
        for e in self.cassette.envelopes:                 # prefer a hash-verified create
            if not e.served and e.is_create and e.conversation_key == "initial" and e.normalized_key == nk:
                return e, "create-hash"
        for e in self.cassette.envelopes:                 # else the next unserved initial call, positionally
            if not e.served and e.conversation_key == "initial":
                return e, "create-positional"
        return None, "no unserved initial envelope"

    def _results_key_of_threaded(self, e: ModelCallEnvelope) -> str:
        """A threaded recorded request holds only the new message; its tool_result ids give the results key."""
        return conversation_key({"messages": e.request.get("messages", [])})

    def _prev_of_results(self, prev_response_id: str) -> str:
        """For a threaded replay answering response X, the recorded non-threaded request that answers X is the
        one whose last message carries X's tool_use ids."""
        e = self.cassette.by_response_id(prev_response_id)
        if not e: return ""
        ids = sorted(b["id"] for b in e.response.get("content", []) if b.get("type") == "tool_use")
        return "results:" + ",".join(ids) if ids else ""

    def match(self, req: dict) -> MatchResult:
        self.seq += 1
        e, how = self._candidate(req)
        if e is None:
            r = MatchResult(self.seq, None, "no-candidate", Divergence(self.seq, "", "", [], None, how))
            self.results.append(r); return r
        ek = sha(canonical({k: v for k, v in req.items() if k not in VOLATILE_TOP}))
        nk = sha(canonical(normalize_request(req)))
        if ek == e.exact_key:
            level, div = "exact", None
        elif nk == e.normalized_key:
            level, div = "normalized", None
        elif sha(canonical(normalize_delta(req))) == e.delta_key:
            level, div = "delta", None               # same new input; transport or harness config differs
        else:
            fd = _diff(normalize_delta(e.request), normalize_delta(req))
            div = Divergence(self.seq, e.delta_key, sha(canonical(normalize_delta(req))), fd, e.index, f"new-input mismatch ({how})")
            level = "positional-miss"
        drift = None
        if sha(canonical(normalize_config(req))) != e.config_key:
            drift = _diff(normalize_config(e.request), normalize_config(req), limit=12)
        if level != "positional-miss" or self.policy == "report":
            e.served = True
        r = MatchResult(self.seq, e if (level != "positional-miss" or self.policy == "report") else None, level, div, drift)
        self.results.append(r)
        return r

    def summary(self) -> dict:
        n = len(self.cassette.envelopes)
        served = sum(1 for e in self.cassette.envelopes if e.served)
        levels = {}
        for r in self.results:
            levels[r.level] = levels.get(r.level, 0) + 1
        first = next((r.divergence for r in self.results if r.divergence), None)
        drift_paths = sorted({d["path"] for r in self.results if r.config_drift for d in r.config_drift})
        extra = [r.seq for r in self.results if r.level == "no-candidate"]
        return {"envelopes": n, "requests_seen": len(self.results), "served": served, "coverage": served / n if n else 0.0,
                "levels": levels, "first_divergence_seq": first.seq if first else None,
                "config_drift_calls": sum(1 for r in self.results if r.config_drift), "config_drift_paths": drift_paths[:20],
                "extra_requests": extra,
                "divergences": [asdict(r.divergence) for r in self.results if r.divergence]}
