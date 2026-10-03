# PLAN-11 — Principles, Decision Register and Governance

**Status:** Source of truth for principles and decisions. Replaces HRCP-00 (archived at `docs/archive/hrcp/`). Every other plan document must be consistent with this one; conflicts are resolved by amending this document through §6.

## 1. Classification

Every important statement carries one of:
- **DECIDED** — we build around it; changing it requires a recorded decision change (§6).
- **PROPOSED** — current preferred direction, not yet validated enough to freeze.
- **OPEN** — unresolved; requires experiment, customer evidence, benchmark or research.

Hypotheses must never silently become architecture.

## 2. Definition

**DECIDED.** We are building the reliability engine for the system around the model: an engine that reconstructs the complete execution of autonomous agents as a harness execution graph, detects where harnesses fail, groups failures into incidents, finds where failed trajectories first diverge from successful ones, attributes failures to harness components with typed evidence, reproduces them by replay, validates fixes against historical trajectories as a gate on harness changes, recommends changes with measured deltas, and, when precision is proven, intervenes at runtime under policy.

Category language: "reliability engine for the system around the model" or "harness engineering platform". Not "LLM observability", "tracing", "AI analytics", "evaluation tooling", and not "control plane" as the category name (runtime control is a capability, PLAN-04 Phase 3 to 4).

## 3. Principles (all DECIDED unless marked)

**P1. Harness execution, not the model request, is the unit of analysis.** LLM call → trace → trajectory → harness execution graph.

**P2. Tracing is substrate, not product.** The product is capture → normalize → reconstruct → detect → correlate → diagnose → replay → verify → recommend → control.

**P3. A trace tree is insufficient; execution is a graph with provenance.** Relationships span the trajectory (memory written at step 12 read at step 184). Every edge carries its source: runtime, normalizer, detector, statistical inference, reasoning model, human analyst. Observed, reconstructed and inferred edges are never indistinguishable.

**P4. Observed, statistical and causal are three different claims and the product never conflates them.** "Permission X blocked tool Y" is observed. "Failure rate rose after compressor v8" is statistical association. "Compressor v8 likely caused it because it removes region state" is a causal hypothesis with confidence. Correlation is never presented as causation.

**P5. Evidence first.** Every automated finding carries evidence, affected population, confidence, alternatives where ambiguous, and, for recommendations, the replay-measured delta. Never "AI thinks the tool failed."

**P6. Cheapest adequate intelligence.** Algorithms → rules → statistics → small classifiers → specialized models → frontier model → human. Frontier models never run over raw traces routinely; they operate on compressed graph summaries for hard cases. Specialized models ship only when they beat the rules baseline by a published margin.

**P7. Incident-first.** The production surface starts at incidents, not at millions of traces. Traces remain accessible underneath.

**P8. Production failures become permanent regression cases.** Incident → diagnosis → replay case → fix → historical regression → deployment → monitoring. The harness ratchets.

**P9. Verification carries evidence.** Claim, evidence, evaluator, policy, threshold, environment, version, decision. Never a bare `passed = true`.

**P10. Replay is a core capability and branch-aware replay is a differentiation target; fidelity is disclosed per run.** Deterministic replay of recorded fixtures until divergence, then controlled live branching. Graph fidelity (G1 to G5) and replay fidelity (R1 to R5) are computed and shown for every run. We never claim a level a fleet is not achieving.

**P11. The regression gate is the commercial lead; replay is its mechanism.** Incidents and release correlation launch the managed product; the product customers cannot ship without is the gate that re-runs historical failures against every harness change. Replay is sold as proof, never as a standalone feature.

**P12. Capture is tiered and both open and closed harnesses are first-class.** Tier A native instrumentation; Tier B hook and OTel adapters for closed harnesses; Tier C API and log adapters. Each tier's coverage matrix is published. Every phase advances A and B together.

**P13. Build above standards; publish ours as an extension, not a private schema.** OpenTelemetry transport and `gen_ai.*` conventions; OpenInference compatibility; our control events proposed upstream to OTel and maintained in a `harness.*` registry until accepted. No proprietary transport. The schema is distribution, not moat.

**P14. Framework-independent, model-independent, provider-independent.** No one framework controls the data model. Customers are never forced through our gateway.

**P15. Customer-side payloads and replay are the default architecture.** Structural telemetry to the managed service; payloads, snapshots and replay execution in the customer's environment unless they opt into managed storage.

**P16. Privacy and security from day one.** Telemetry may contain credentials, PII, proprietary code and customer records. Telemetry is untrusted input: model and tool outputs are data, never instructions. Redaction in the SDK and collector; secret detection; tenant identity in every storage path; encryption in transit and at rest; retention by data class.

**P17. Customer telemetry never silently trains shared models.** Training permissions are distinct from operational processing. Cross-customer learning requires explicit data rights per corpus item. Permission is never inferred.

**P18. Raw evidence is immutable; derived interpretations are versioned and rebuildable.** Normalization, graph construction, incident clustering and classifiers can all be recomputed from retained evidence when they improve.

**P19. Version everything.** Agent, harness, prompt, model and configuration, tool schema, MCP server, skill, memory state, context strategy, policy, verification policy, runtime image, code commit, dataset, environment. Regression analysis without versioning is unreliable.

**P20. Runtime control is policy-driven, auditable, and arrives after measurement.** Low-risk interventions first; high-impact interventions only after detector precision, false-positive rate, attribution accuracy, rollback reliability and control-plane availability are measured per fleet. Human approval remains available for high-risk interventions. Control path is separated from analytics path and fails per customer-selected policy (fail-open, fail-closed, degrade-to-human).

**P21. Success-adjusted economics are first-class.** Cost per verified success, loop waste, reread waste, subagent cost, by harness version. Never price by span alone.

**P22. API-first.** Every core function is programmatic: get incident, compare runs, replay, run regression, query provenance, evaluate policy, request intervention.

**P23. Different interfaces for different questions.** Timeline, trajectory, state transitions, graph, context evolution, subagent tree, artifact history, incident cohort, replay branches. A waterfall is not assumed optimal.

**P24. Humans stay in consequential decisions.** The platform reduces investigation labour; autonomy expands as evidence quality is demonstrated.

**P25. Adopt before inventing.** Failure taxonomy from "Model or Harness?" and MAST; benchmarks alongside LongRCA, TRAIL and MAST; existing sandboxes and durable-execution journals as capture sources.

**P26. Evidence gates fund phases.** No stream scales past a gate its evidence has not passed, regardless of team size.

## 4. Product boundaries (DECIDED)

We observe and diagnose; we do not become: a model gateway, a memory platform, a document or parsing engine, enterprise IAM, an MCP marketplace or gateway, a BPO operator, a generic eval platform, a prompt CMS, an agent builder, a workflow builder, a vector database, or an agent security firewall. We integrate with each and, where we hold evidence they need, we export it to them.

## 5. Decision register

Numbering continues from HRCP-00 D-001 to D-030 (archived). Changed items cite the archived decision.

| ID | Decision | Status |
|---|---|---|
| D-001 | Harness reliability engine, not generic LLM observability | DECIDED |
| D-002 | Harness execution is the primary unit | DECIDED |
| D-003 | OpenTelemetry is the telemetry foundation | DECIDED |
| D-004 | OpenInference compatibility | DECIDED |
| D-005 | Semantic layer represents harness-specific runtime behaviour | DECIDED |
| D-006/007 | Execution is a graph with provenance, not only a tree | DECIDED |
| D-008 | Incident-centric workflows over trace browsing | DECIDED |
| D-009 | Deterministic and inexpensive analysis before frontier reasoning | DECIDED |
| D-010 | Production incidents feed regression suites | DECIDED |
| D-011/012 | Replay is core; branch-aware replay is a differentiation target | DECIDED |
| D-013 | Verification carries evidence and provenance | DECIDED |
| D-014/015 | Context, state, memory, permissions, tools, subagents, artifacts and stop decisions are explicit events | DECIDED |
| D-016 | Success-adjusted economics are first-class | DECIDED |
| D-017/018 | Runtime intervention is a later layer; high-risk intervention is policy-driven and auditable | DECIDED |
| D-019 | Open-source instrumentation and semantic conventions | DECIDED |
| D-020 | No model gateway as the product | DECIDED |
| D-021 | Framework-independent | DECIDED |
| D-022 | Telemetry isolated and privacy-aware by design | DECIDED |
| D-023 | Raw evidence distinct from derived interpretations | DECIDED |
| D-024 | API-first | DECIDED |
| D-025 | Separate from document-state, memory, IAM, MCP gateway and BPO layers | DECIDED |
| D-026 | **Changed from "coding agents first".** Two domains from Phase 1: coding agents and API-driven workflow agents; browser, research and computer-use agents in Phase 4. Reason: founder direction plus both domains satisfy the alignment and snapshot constraints. | DECIDED |
| D-027 | Open-source developer product is the Flight Recorder (internal name); external name decided in Phase 0 | PROPOSED |
| D-028 | **Changed.** Event model is published as `gen_ai.*` proposals plus a `harness.*` registry; "Harness Event Model" is internal | DECIDED |
| D-029 | Execution graph (internal name "Harness Execution Graph") stored as adjacency tables, no graph database unless the Phase 1 benchmark fails | DECIDED |
| D-030 | **Changed from "Harness Reliability Control Plane".** Category: reliability engine for the system around the model / harness engineering platform | DECIDED |
| D-031 | Regression gate is the commercial lead; replay is its mechanism | DECIDED |
| D-032 | Capture is tiered (A, B, C) with a published coverage matrix and per-run fidelity levels | DECIDED |
| D-033 | Customer-side payloads and replay runner are the default architecture | DECIDED |
| D-034 | Event model v0.1 is nine domains and roughly twenty events; other domains in v0.2 and v0.3 | DECIDED |
| D-035 | Failure taxonomy adopted from "Model or Harness?" with MAST and LongRCA mappings | DECIDED |
| D-036 | Open-source license Apache 2.0; boundary per PLAN-06 §5 | DECIDED |
| D-037 | A lossless side channel (raw bodies, snapshots, content-addressed payload refs) accompanies OTLP export | DECIDED |
| D-038 | Verification adapter independent of harness (CI, tests, git) | DECIDED |
| D-039 | Both open and closed harnesses advance in every phase | DECIDED |
| D-040 | Harness vendors are a strategic design-partner track | DECIDED |
| D-041 | Specialized models ship only when they beat the rules baseline by a published margin | DECIDED |
| D-042 | Benchmark team is independent of the teams it grades | DECIDED |
| D-043 | Company and product name | OPEN (Phase 0) |
| D-044 | Pricing architecture | OPEN (Gate H) |
| D-045 | Analytical store, stream, sandbox isolation technology | OPEN (Phase 0 and 1 benchmarks) |
| D-046 | Relationship with Laminar (compete, partner, merge) | OPEN (Phase 0) |
| D-047 | Foundation home for the specification | OPEN (Phase 3) |

## 6. Change management

A DECIDED item may change. The change records: old decision, new decision, reason, evidence, affected components, migration plan. Changes are appended to this register and to PLAN-05 as the change log. The first batch (D-026, D-028, D-030, D-031 to D-042) was decided on 3 October 2026 on the basis of `docs/archive/research/` and founder review.

## 7. Source-of-truth hierarchy

```
PLAN-11 Principles and Decisions
        ↓
approved ADRs
        ↓
PLAN-12 Architecture Baseline, PLAN-04 Roadmap, other PLAN documents
        ↓
SPEC-01 to SPEC-08 (PLAN-13)
        ↓
component specifications
        ↓
implementation documentation
```

A README does not silently override the plan. Archived HRCP and research documents are provenance, not authority.

## 8. Open strategic questions

1. Exact first design partners per track (Phase 0).
2. Company and product name (Phase 0).
3. Which of the OTel control-event proposals are accepted, and on what timeline.
4. Replay isolation technology and customer-side runner packaging.
5. Pricing architecture and value metric.
6. Boundary between statistical correlation and causal attribution in product copy, per confidence band.
7. Whether specialized models are ever published.
8. Hosted vs hybrid priority by segment.
9. Laminar relationship.
10. Foundation home for the specification.
