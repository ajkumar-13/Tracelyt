"""First-divergence engine v0 (Proof E/F). Compares a failure cohort against a success cohort of the same task class.

Method (deterministic, explainable):
1. Abstract each run into a trajectory of tokens: (event type, tool/verifier name, outcome). Content never enters a token;
   only the provenance content hash does, because a differing instruction file IS an observed input difference.
2. Align every failed run against every successful run with a longest-common-subsequence alignment and record the first
   non-matching token in the failed run.
3. Aggregate: the first-divergence candidates are ranked by the fraction of (failed, success) pairs that diverge there.
4. Attribution: the divergent event's owning component is the mechanism; if an observed upstream input differs between
   cohorts (provenance content hash, harness config hash, model, tool definitions hash), that component is the primary
   root-component hypothesis and the mechanism becomes the alternative. Confidence is the agreement fraction. Nothing
   is presented as proven causation (PLAN-11 P4)."""
from __future__ import annotations
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from difflib import SequenceMatcher

from harness_engine.model.events import Component, Event, EventType

SKIP = {EventType.UNKNOWN, EventType.RUN_STARTED, EventType.RUN_RESUMED, EventType.RUN_COMPLETED, EventType.RUN_FAILED, EventType.ITERATION_STARTED}


def token(e: Event) -> str:
    if e.type == EventType.CONTEXT_PROVENANCE_LOADED:
        return f"{e.type.value}:{e.attrs.get('source_kind')}:{(e.attrs.get('content_hash') or 'nohash')[:12]}"
    if e.type in (EventType.TOOL_REQUESTED, EventType.TOOL_COMPLETED, EventType.TOOL_FAILED, EventType.TOOL_AUTHORIZED, EventType.TOOL_REJECTED):
        name = e.attrs.get("tool_name", "")
        if name == "Bash": name = f"Bash[{e.attrs.get('command_binary') or '?'}]" if e.type == EventType.TOOL_REQUESTED else "Bash"
        return f"{e.type.value}:{name}"
    if e.type.value.startswith("verify."): return f"{e.type.value}:{e.attrs.get('evaluator')}"
    if e.type in (EventType.PERMISSION_REQUESTED, EventType.PERMISSION_DENIED, EventType.PERMISSION_GRANTED): return f"{e.type.value}:{e.attrs.get('resource')}"
    if e.type == EventType.MODEL_RESPONSE: return f"{e.type.value}:{e.attrs.get('finish_reason') or ''}"
    if e.type == EventType.STOP: return f"stop:{e.attrs.get('reason')}"
    return e.type.value


def trajectory(events: list[Event]) -> list[tuple[str, Event]]:
    evs = sorted((e for e in events if e.type not in SKIP and e.identity.agent_instance_id in (None, "main")), key=lambda e: (e.timestamp, e.sequence or 10**9))
    # Bash tool requests carry the binary in the token, so a Bash[pytest] vs Bash[pytest tests/spec] difference is invisible here by design:
    # commands are content. The verifier adapter and failure outcome carry the signal instead.
    return [(token(e), e) for e in evs]


@dataclass
class Divergence:
    position: int; token: str; event: Event; against_success_token: str | None


@dataclass
class CohortReport:
    n_failed: int; n_success: int
    candidates: list[dict] = field(default_factory=list)      # ranked first-divergence tokens
    primary_component: Component | None = None
    primary_confidence: float = 0.0
    mechanism_component: Component | None = None
    upstream_differences: list[dict] = field(default_factory=list)
    explanation: str = ""


def first_divergence(failed: list[tuple[str, Event]], success: list[tuple[str, Event]]) -> Divergence | None:
    a = [t for t, _ in failed]; b = [t for t, _ in success]
    sm = SequenceMatcher(a=a, b=b, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal": continue
        if i1 < len(failed):
            return Divergence(i1, failed[i1][0], failed[i1][1], b[j1] if j1 < len(b) else None)
        return Divergence(i1 - 1, failed[-1][0], failed[-1][1], b[j1] if j1 < len(b) else None)  # failed run ended early
    return None


def _observed_inputs(events: list[Event]) -> dict[str, str]:
    """Inputs that are observed, not inferred: instruction content hashes, harness/model versions, tool definition hashes."""
    out = {}
    for e in events:
        if e.type == EventType.CONTEXT_PROVENANCE_LOADED and e.attrs.get("content_hash"):
            out[f"provenance:{e.attrs.get('source_kind')}:{(e.attrs.get('source_name_hash') or '')[:8]}"] = e.attrs["content_hash"]
        if e.type == EventType.MODEL_REQUEST:
            if e.attrs.get("tools_hash"): out.setdefault("tools_hash", e.attrs["tools_hash"])
            if e.attrs.get("model"): out.setdefault("model", e.attrs["model"])
        if e.versions.harness_config_hash: out["harness_config_hash"] = e.versions.harness_config_hash
    return out


UPSTREAM_COMPONENT = {"provenance": Component.CONTEXT_BUILDER, "tools_hash": Component.TOOL, "model": Component.MODEL, "harness_config_hash": Component.ENVIRONMENT}


def compare_cohorts(failed_runs: list[list[Event]], success_runs: list[list[Event]]) -> CohortReport:
    F = [trajectory(r) for r in failed_runs]; S = [trajectory(r) for r in success_runs]
    rep = CohortReport(n_failed=len(F), n_success=len(S))
    votes: Counter = Counter(); example: dict[str, Event] = {}; positions: dict[str, list[int]] = defaultdict(list)
    pairs = 0
    for f in F:
        for s in S:
            d = first_divergence(f, s); pairs += 1
            if d: votes[d.token] += 1; example.setdefault(d.token, d.event); positions[d.token].append(d.position)
    for tok, n in votes.most_common(5):
        rep.candidates.append({"token": tok, "agreement": round(n / pairs, 3), "component": example[tok].component.value, "median_position": sorted(positions[tok])[len(positions[tok]) // 2], "example_event_id": example[tok].event_id})
    # Upstream observed-input differences between cohorts
    fin = [_observed_inputs(r) for r in failed_runs]; sin = [_observed_inputs(r) for r in success_runs]
    keys = set().union(*fin, *sin)
    for k in sorted(keys):
        fv = Counter(d.get(k) for d in fin); sv = Counter(d.get(k) for d in sin)
        if set(fv) and set(sv) and not (set(fv) & set(sv)):
            rep.upstream_differences.append({"input": k, "failed_values": len(fv), "success_values": len(sv), "component": UPSTREAM_COMPONENT.get(k.split(":")[0], Component.UNKNOWN).value})
    if rep.candidates:
        top = rep.candidates[0]; rep.mechanism_component = Component(top["component"]); rep.primary_confidence = top["agreement"]
        if rep.upstream_differences:
            rep.primary_component = Component(rep.upstream_differences[0]["component"])
            rep.explanation = (f"Observed input '{rep.upstream_differences[0]['input']}' differs between every failed and every successful run; "
                               f"first trajectory divergence at '{top['token']}' (position {top['median_position']}, agreement {top['agreement']}). "
                               f"Primary hypothesis: {rep.primary_component.value}; mechanism: {rep.mechanism_component.value}.")
        else:
            rep.primary_component = rep.mechanism_component
            rep.explanation = f"No observed input differs; first divergence at '{top['token']}' (position {top['median_position']}, agreement {top['agreement']}). Hypothesis: {rep.primary_component.value}."
    return rep
