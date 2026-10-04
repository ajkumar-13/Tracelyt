"""Harness execution graph builder (PLAN-12 §11). Edges carry provenance: observed (runtime identifiers), reconstructed
(normalizer ordering or content addressing), inferred (detectors/attribution, added elsewhere with confidence)."""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from harness_engine.model.events import Event, EventType


class EdgeSource(str, Enum):
    RUNTIME = "runtime"            # observed: shared runtime identifier
    NORMALIZER = "normalizer"      # reconstructed: ordering / scoping rules
    CONTENT = "content_addressing" # reconstructed: hash match
    DETECTOR = "detector"          # inferred
    STATISTICAL = "statistical_inference"
    MODEL = "reasoning_model"
    HUMAN = "human_analyst"


@dataclass
class Edge:
    src: str; dst: str; rel: str; source: EdgeSource; confidence: float = 1.0; method: Optional[str] = None; evidence: dict = field(default_factory=dict)


@dataclass
class Graph:
    run_id: str
    nodes: dict[str, Event] = field(default_factory=dict)
    edges: list[Edge] = field(default_factory=list)
    fidelity: str = "G1"
    fidelity_reasons: list[str] = field(default_factory=list)

    def out(self, nid: str, rel: str | None = None): return [e for e in self.edges if e.src == nid and (rel is None or e.rel == rel)]
    def inc(self, nid: str, rel: str | None = None): return [e for e in self.edges if e.dst == nid and (rel is None or e.rel == rel)]


def build_graph(events: list[Event]) -> Graph:
    evs = sorted((e for e in events if e.type != EventType.UNKNOWN), key=lambda e: (e.timestamp, e.sequence or 10**9))
    if not evs: return Graph(run_id="")
    g = Graph(run_id=evs[0].identity.run_id)
    for e in evs: g.nodes[e.event_id] = e
    run_node = next((e for e in evs if e.type in (EventType.RUN_STARTED, EventType.RUN_RESUMED)), evs[0])
    # Structural parent_of: run -> iteration/turn scope; every event's parent is its turn or the run. (reconstructed by scoping)
    turn_nodes = {e.correlation.get("turn_id"): e for e in evs if e.type == EventType.ITERATION_STARTED and e.correlation.get("turn_id")}
    by_tcid: dict[str, list[Event]] = defaultdict(list)
    for e in evs:
        if e is run_node: continue
        parent = turn_nodes.get(e.identity.turn_id) if e.identity.turn_id else None
        if parent is not None and parent is not e:
            g.edges.append(Edge(parent.event_id, e.event_id, "parent_of", EdgeSource.RUNTIME, method="shared turn_id"))
        else:
            g.edges.append(Edge(run_node.event_id, e.event_id, "parent_of", EdgeSource.RUNTIME, method="shared run_id"))
        if e.correlation.get("tool_call_id"): by_tcid[e.correlation["tool_call_id"]].append(e)
    # Tool chain: requested -> authorized/rejected -> completed/failed, all on tool_call_id (observed).
    for tcid, group in by_tcid.items():
        req = next((x for x in group if x.type == EventType.TOOL_REQUESTED), None)
        if not req: continue
        for x in group:
            if x.type in (EventType.TOOL_AUTHORIZED,): g.edges.append(Edge(x.event_id, req.event_id, "approved_by", EdgeSource.RUNTIME, method="tool_call_id"))
            elif x.type in (EventType.TOOL_REJECTED, EventType.PERMISSION_DENIED): g.edges.append(Edge(x.event_id, req.event_id, "blocked_by", EdgeSource.RUNTIME, method="tool_call_id"))
            elif x.type == EventType.PERMISSION_REQUESTED: g.edges.append(Edge(req.event_id, x.event_id, "requires", EdgeSource.RUNTIME, method="tool_call_id"))
            elif x.type in (EventType.TOOL_COMPLETED, EventType.TOOL_FAILED): g.edges.append(Edge(req.event_id, x.event_id, "produces", EdgeSource.RUNTIME, method="tool_call_id"))
            elif x.type in (EventType.VERIFY_PASSED, EventType.VERIFY_FAILED, EventType.VERIFY_ABSTAINED): g.edges.append(Edge(x.event_id, req.event_id, "verified_by", EdgeSource.NORMALIZER, method="verification_adapter"))
    # requested_by: a tool request is requested by the most recent model.response in the same agent instance before it.
    last_resp: dict[str, Event] = {}
    for e in evs:
        key = e.identity.agent_instance_id or "main"
        if e.type == EventType.MODEL_RESPONSE: last_resp[key] = e
        elif e.type == EventType.TOOL_REQUESTED and key in last_resp:
            g.edges.append(Edge(e.event_id, last_resp[key].event_id, "requested_by", EdgeSource.NORMALIZER, confidence=0.95, method="latest model.response in agent instance"))
    # Delegation: agent.spawned -> child events (observed via agent_instance_id); agent.returned -> parent context.
    spawned = {e.attrs.get("child_agent_instance_id"): e for e in evs if e.type == EventType.AGENT_SPAWNED}
    for e in evs:
        inst = e.identity.agent_instance_id
        if inst in spawned and e is not spawned[inst] and e.type != EventType.AGENT_RETURNED:
            g.edges.append(Edge(spawned[inst].event_id, e.event_id, "delegated_to", EdgeSource.RUNTIME, method="agent_instance_id"))
        if e.type == EventType.AGENT_RETURNED and e.attrs.get("child_agent_instance_id") in spawned:
            g.edges.append(Edge(e.event_id, spawned[e.attrs["child_agent_instance_id"]].event_id, "returned_to", EdgeSource.RUNTIME, method="agent_instance_id"))
    # Context lineage: compaction compacts everything in the run before it (reconstructed by ordering); provenance loads feed the run.
    for e in evs:
        if e.type == EventType.CONTEXT_COMPACT:
            prior = [x for x in evs if x.timestamp < e.timestamp and x.identity.run_id == e.identity.run_id and x.type in (EventType.MODEL_RESPONSE, EventType.TOOL_COMPLETED, EventType.TOOL_FAILED, EventType.AGENT_RETURNED)]
            for x in prior: g.edges.append(Edge(e.event_id, x.event_id, "compacted_from", EdgeSource.NORMALIZER, confidence=0.9, method="precedes compaction in run"))
        if e.type == EventType.CONTEXT_PROVENANCE_LOADED:
            g.edges.append(Edge(e.event_id, run_node.event_id, "loaded_into", EdgeSource.RUNTIME, method="InstructionsLoaded"))
    g.fidelity, g.fidelity_reasons = compute_fidelity(g)
    return g


def compute_fidelity(g: Graph) -> tuple[str, list[str]]:
    types = {e.type for e in g.nodes.values()}
    reasons = []
    level = "G1"
    tool_reqs = [e for e in g.nodes.values() if e.type == EventType.TOOL_REQUESTED]
    closed = sum(1 for r in tool_reqs if g.out(r.event_id, "produces") or g.inc(r.event_id, "blocked_by"))
    if tool_reqs and closed == len(tool_reqs): level = "G2"; reasons.append(f"all {len(tool_reqs)} tool requests closed by result or block")
    elif tool_reqs: reasons.append(f"{len(tool_reqs)-closed} tool requests without result or block")
    compactions = [e for e in g.nodes.values() if e.type == EventType.CONTEXT_COMPACT]
    if level == "G2" and (not compactions or all("summary" in c.payload_refs and c.attrs.get("tokens_before") for c in compactions)) and EventType.CONTEXT_PROVENANCE_LOADED in types:
        level = "G3"; reasons.append("context provenance present; compactions carry summary ref and token counts" if compactions else "context provenance present; no compaction occurred")
    if level == "G3" and types & {EventType.VERIFY_PASSED, EventType.VERIFY_FAILED, EventType.VERIFY_ABSTAINED}:
        level = "G4"; reasons.append("verification evidence chain present")
    if any(e.source in (EdgeSource.DETECTOR, EdgeSource.STATISTICAL, EdgeSource.MODEL) for e in g.edges): level = "G5"; reasons.append("inferred edges present")
    return level, reasons
