# PLAN-12 — Technical Architecture Baseline

**Status:** Source of truth for architecture. Replaces HRCP-01 (archived) with the PLAN-05 deltas applied. Architecture-level; wire schemas belong in SPEC-01 (PLAN-13). Decisions reference PLAN-11.

## 1. Architecture properties
Framework-, model- and provider-independent; OTel-native; append and evidence oriented; version-aware; replay-aware; privacy-aware with customer-side payloads by default; multi-agent-aware; policy-aware; artifact-aware; API-first; horizontally scalable; fidelity-disclosing.

## 2. Planes
- **Capture plane**: SDKs, instrumentors, adapters, collector, side channel. Runs in the customer environment.
- **Data plane**: ingestion, normalization, durable stream, raw evidence, telemetry store, metadata, payload references.
- **Intelligence plane**: graph, detectors, incidents, divergence, attribution, economics, models.
- **Replay plane**: manifests, fixtures, snapshots, sandbox orchestration, regression. Executes customer-side by default.
- **Control plane** (capability, Phase 3+): policy, intervention, approval, control audit. Separate availability and authorization from analytics.
- **Management plane**: organizations, projects, users, retention, integrations, data rights.

## 3. System context
```
Customer environment                         Managed service
┌──────────────────────────────┐             ┌──────────────────────────────┐
│ Agent runtime(s)             │             │ Ingestion gateway            │
│  ├ Tier A instrumentors ─────┼─ OTLP ─────▶│ Versioned normalizer         │
│  ├ Tier B hook/OTel adapters ┼─ OTLP ─────▶│ Durable stream               │
│  └ Tier C API/log adapters ──┼─ OTLP ─────▶│ Raw evidence │ Telemetry     │
│ Collector + local detectors  │             │ Metadata     │ Graph tables  │
│ Redaction, secret detection  │             │ Detectors → Incidents        │
│ Payload store (customer S3) ◀┼─ refs ──────│ Divergence → Attribution     │
│ Snapshot store               │             │ Regression orchestrator      │
│ Replay runner (sandbox) ◀────┼─ jobs ──────│ Economics │ Models           │
│ Verification adapter (CI/git)┼────────────▶│ APIs │ UI │ CLI │ CI checks  │
└──────────────────────────────┘             └──────────────────────────────┘
```
Managed payload storage is an opt-in simplification; the default keeps payloads, snapshots and replay customer-side (PLAN-11 P15).

## 4. Capture tiers and sources
| Tier | Sources | Mechanism |
|---|---|---|
| A | LangGraph, OpenAI Agents SDK, Google ADK, PydanticAI, Claude Agent SDK, OpenHands, CrewAI, Mastra, Vercel AI SDK, custom harnesses via SDK; durable-execution journals (Temporal, Restate, Inngest) | Instrumentor packages emitting `gen_ai.*` plus `harness.*`; upstream PRs where frameworks have native OTel |
| B | Claude Code, Codex CLI, Gemini CLI | Hook adapter on the shared stdin-JSON hook contract; OTLP receiver for native export; side channel for raw bodies and snapshots |
| C | Cursor hooks, Devin API, Entire Checkpoints, generic `gen_ai.*`, OpenInference | API and log adapters |
| Adjunct | CI systems, git, container images, prompt and tool registries, policy deployments, approval services | Verification and version adapters |
The coverage matrix per emitter (PLAN-05 §4) is part of the published standard.

## 5. SDK
Thin: instrumentation, context propagation, event helpers, normalization to v0.1, local buffering with bounded queue and disk buffer, redaction and secret detection, sampling, async batched export, side-channel writers. Contains no commercial intelligence. Python and TypeScript first; Go in Phase 2.

## 6. Event envelope (conceptual)
`event_id, event_type, timestamp, organization_id, project_id, run_id, session_id, agent_id, agent_instance_id, parent_event_id, correlation_ids[], harness_version, component, component_version, input_ref, output_ref, status, attributes{}, evidence_refs[], payload_refs[] (content hash + store URI), fidelity_hints, schema_version, normalizer_version`.

## 7. Identity
Hierarchy: organization → workspace/project → application → agent definition → agent version → agent instance → run → session → iteration → event. Never conflate `trace_id, run_id, session_id, agent_id, agent_instance_id, subagent_id, task_id, workflow_id, artifact_id, incident_id, replay_id, regression_case_id`. One OTel trace may not map to one semantic run.

Propagation: run identity, trace context, agent instance, delegation identity, task identity, harness version, policy version via W3C trace context and OTel baggage. Where the harness does not propagate (Claude Code subprocesses, MCP servers), the adapter correlates via hook payloads (`session_id, agent_id, tool_use_id`). Sensitive identity propagation is minimized. ADR-001.

## 8. Event model
**v0.1 (DECIDED, D-034), nine domains, ~20 events:**
- RUN: started, resumed, paused, completed, failed, aborted.
- LOOP: iteration.started, iteration.completed (iteration number, budget remaining, state hash before/after, progress signal).
- MODEL: request, response (provider, model, version, config, tokens, latency, stop reason, request and response ids; bodies by payload ref).
- TOOL/MCP: requested, authorized, rejected, started, completed, failed (intent separated from execution; MCP server and tool identity, schema version, side-effect class).
- CONTEXT: build, compact (trigger, tokens before/after, summary ref, policy version, removed source refs), provenance.loaded (what was loaded, by which mechanism, hashed).
- PERMISSION: requested, granted, denied (actor, resource, action, policy, decision, source, reason, scope).
- AGENT: spawned, returned, cancelled (parent, child instance, task ref, shared context refs, budget).
- VERIFICATION: requested, evidence, passed, failed, abstained (claim, evidence refs, evaluator, policy, threshold).
- STOP: reason taxonomy: success, verified_success, agent_declared_complete, budget_exhausted, timeout, no_progress, policy_stop, human_stop, fatal_error, external_dependency, unknown.

**v0.2 and v0.3 domains:** PLAN, MEMORY, RETRIEVAL, HOOK, POLICY, SANDBOX, STATE, HUMAN, ARTIFACT, BUDGET, RECOVERY, ENVIRONMENT, added as real traffic validates v0.1. Unknown framework events are captured as `namespace, event_type, attributes`, never dropped.

Each event is defined with its `gen_ai.*` proposal form and its `harness.*` registry form (ADR-002).

## 9. Raw evidence vs semantic events
Raw telemetry and side-channel captures are immutable and retained by policy. Normalization is versioned; semantic events, graphs, incidents and hypotheses are derived and rebuildable (PLAN-11 P18). ADR-011.

## 10. Stream and storage
- Durable stream before downstream processing (technology OPEN, D-045; Kafka-compatible candidates benchmarked in Phase 0).
- Metadata and configuration: PostgreSQL (PROPOSED).
- High-volume telemetry: column-oriented analytical store, ClickHouse PROPOSED pending the Phase 0 benchmark on billions of events, high-cardinality attributes, time-window and cohort queries, trajectory reconstruction, retention tiers (A-008).
- Payloads, snapshots, fixtures, export bundles: S3-compatible object storage, customer-side by default, content-addressed (`payload_hash → object`).
- Graph: materialized adjacency and lineage tables in the analytical store (D-029). Per-run graphs are hundreds to tens of thousands of nodes; cross-run aggregates via path hashing.
- Retention tiers: structural telemetry, raw payload, incident evidence, customer-selected. Values OPEN.

## 11. Execution graph
**Nodes:** run, iteration, agent instance, model call, plan, context state, memory entry, retrieval, tool request, tool execution, policy decision, permission decision, sandbox action, state mutation, verification, artifact, human action, stop decision.
**Edges:** `parent_of, requested_by, approved_by, blocked_by, delegated_to, returned_to, produces, mutates, reads_from, writes_to, derived_from, compacted_from, retrieved_from, verified_by, invalidated_by, depends_on, supersedes, replayed_from, regression_of, caused_by, influenced_by`. Each edge carries relationship type, timestamp, confidence, **source** (runtime, normalizer, detector, statistical inference, reasoning model, human analyst), derivation method, evidence refs.
**Edge classes:** observed (directly from events with ids), reconstructed (content addressing: hashes of tool results, context items, memory entries; inclusion detection by hash, substring, embedding), inferred (from divergence and attribution; always with confidence).
**Fidelity levels G1 to G5** computed per run (PLAN-10 §3) and displayed everywhere the graph is shown.
**Context lineage:** tool result → context item → compaction → summary → model call; declared or pinned state keys tracked across compaction. **Memory provenance:** who wrote, when, under which agent, from which source, which later decisions read it. **Version graph:** agent, harness, prompt, model, tool, MCP, policy, context strategy, runtime, commit.

## 12. Detector engine
Categories: real-time deterministic (loop, retry storm, budget spiral, tool thrash, permission storm, verification bypass, context explosion, repeated retrieval, invalid tool arguments, no progress, recovery failure); streaming statistical (failure-rate, latency, cost, tool-distribution shifts); batch intelligence (clustering, cohort comparison, root-component ranking, first divergence). Contract: `detector_id, version, scope, evidence, severity, confidence, affected events and runs, recommended next analysis`, plus published definition, positive and negative examples, precision, recall, blind spots, cost, latency (ADR-009). Deterministic detectors can run customer-side in the collector.

## 13. Incident engine
Clusters signals on failure type, first divergence, event sequence, error, tool, harness version, embedding, environment, state, output behaviour. Lifecycle: detected → triaged → investigating → root-cause hypothesis → reproduced → fix proposed → regression tested → resolved → monitoring. Release correlation against git, CI, images, prompt registry, agent and model config, tool registry, policy deployment. Each incident answers: what, how many runs, since when, which versions, common divergence, responsible component, cost, evidence, reproducible.

## 14. Trajectory representations and first divergence
Representations: sequence, tree, graph, state-transition sequence, artifact history. First-divergence pipeline: normalize → align comparable stages (semantic stage alignment, event-type alignment, dynamic sequence alignment, graph matching, task checkpoints) → identify earliest significant divergence → rank divergent events → correlate with outcome → inspect upstream dependencies → root-component candidates → evidence package. Output preserves alternatives with confidence. Evaluated on the Harness Reliability Benchmark and LongRCA (PLAN-10 §4).

## 15. Reliability models
Inputs are compressed semantic structures (graph summary, important events, divergence candidates, version changes, detector outputs, artifact diff, verification evidence), not raw traces. Candidates in sequence per PLAN-11 P6 and D-041: failure-type classifier, first-divergence ranker, root-component classifier, incident similarity encoder, context-loss detector, tool-misuse detector, verification-weakness detector, regression-risk estimator.

## 16. Replay
**Manifest:** task, agent and harness versions, commit, model and config, prompt versions, tool and MCP versions, context state, memory snapshot, filesystem snapshot, environment, policy, permissions, external fixtures, recorded model outputs, side-effect classes.
**Side channel (D-037):** raw request and response bodies, tool outputs, filesystem snapshots, network fixtures written customer-side with content-addressed refs in events; OTLP alone is lossy.
**Modes:** exact fixture replay; partial replay; branch replay (reuse history until divergence, then controlled live execution, capture the branch); live shadow replay; counterfactual replay.
**Fidelity R1 to R5** disclosed per replay. Expected vs actual state compared continuously; first replay divergence is itself evidence.
**Side effects:** tools and MCP servers classified read-only, reversible write, irreversible write, financial, security-sensitive, external communication (ADR-008); replay policy differs by class; default replay is in controlled environments with network deny-by-default, credential stripping, resource and time limits, output sanitization, audit.
**Runner:** executes in the customer's sandbox by default (container first; microVM evaluated, ADR-007); managed runner as opt-in.
**Domains:** coding (repo SHA plus image plus fixtures) and API-workflow (service fixtures and mocks) from Phase 2.

## 17. Regression engine
Suites: production failures, customer cases, synthetic cases, security cases, performance cases, policy cases. Baseline vs candidate across success, verification, cost, latency, trajectory changes, tool usage, human intervention, security events, failure distribution. Pareto reporting, no single score. CI integration: PR touching harness files → regression suite → report (fixed, introduced, cost per success, verified success) → optional merge gate. Recommendations are replay experiments with attached deltas (Phase 3). Optimization search over harness configuration space (Phase 4).

## 18. Runtime control (architecture only until Phase 3)
Inputs: policy, execution state, detectors, incident intelligence, identity, risk. Flow: runtime event → detector → policy engine → risk evaluation → (low risk) intervention adapter, (high risk) human approval → adapter → runtime. Interventions: observe, warn, pause, require human, deny action, stop agent, change budget, change model, disable tool, restrict permission, switch fallback, increase verification, roll back configuration. Policies explicit and versioned, never buried in prompts. Control audit: trigger, policy, evidence, decision, actor, execution, result, rollback possibility. Enforcement via existing gateways and security products where possible. Readiness gate per PLAN-04 Phase 4.

## 19. APIs, query, CLI, CI
API families: events, runs, sessions, agents, graphs, incidents, replays, regressions, policies, interventions, artifacts, evaluations. Query model supports: failures after harness version N; runs where compaction preceded tool selection; compare cohorts; permission approval followed by sandbox denial; incidents by MCP server version; failures derived from memory entry X; cost per verified success by model; replay incident N against harness M. CLI: record, run inspect, incident inspect, replay, regression run, compare. CI: GitHub, GitLab, Buildkite checks.

## 20. Privacy and security architecture
Structural metadata separated from sensitive payload; payload customer-side by default (P15). Redaction before SDK emission, collector-side, ingestion-side; secret detection for keys, tokens, credentials, authorization headers. TLS in transit, encryption at rest, customer-managed keys (Phase 3), strict tenant isolation with tenant identity in every storage path, authorization never UI-only. Training permissions distinct from operational processing; default isolation. Replay isolation per §16. Telemetry treated as untrusted input throughout the normalizer and UI. Threat model categories: prompt injection in payloads, malicious tool and MCP output, secret leakage, tenant escape, telemetry poisoning, replay and sandbox escape, malicious artifacts, supply chain, control-plane abuse, forged telemetry, identity spoofing, exfiltration. Roles: viewer, analyst, replay operator, policy author, control approver, administrator. Immutable audit of policy changes, interventions, replays, exports, retention and permission changes.

## 21. Scale and operations
Sampling: head, tail, error-biased, incident, high-cost, rare-behaviour, adaptive. Local analysis: deterministic detectors customer-side. Content addressing for repeated payloads. Backpressure: bounded queue, drop policy, disk buffer, async export; telemetry failure never blocks the agent; control traffic separate. Self-observability: ingestion latency, drops, queue depth, normalization errors, detector delay, storage latency, replay failures, control latency; we dogfood our own engine. Schema evolution: explicit versions, old SDK to new backend compatibility, breaking changes rare. Plugins: model provider, framework, tool, MCP, memory, sandbox, verification, artifact, identity, CI, observability export. Existing observability: export incidents, scores and findings into Datadog, Grafana, Honeycomb, Dynatrace; never require replacement.

## 22. Canonical representation
External event → adapter → event model (v0.1 `gen_ai.*`/`harness.*`) → execution graph with fidelity. Intelligence operates on the normalized representation, never on framework payloads.

## 23. Minimum viable engineering version (Phase 1 to 2)
SDKs; Tier A instrumentors (six); Tier B adapters (three); OTel and OpenInference ingestion; versioned normalizer; identity propagation; run, iteration, model, tool, context, permission, agent, verification and stop events; analytical store; adjacency tables with G1 to G3; run explorer, timeline, subagent tree, context explorer; deterministic detectors; incident grouping; release correlation; cohort compare; replay manifest and side channel; replay v1 customer-side; regression workbench alpha.

## 24. Deferred
Autonomous high-impact intervention, broad policy engine, complex causal inference, specialized models (until D-041 is met), graph database, all frameworks, all deployment models, managed replay at scale, cross-customer learning.

## 25. Validation gates
Ingestion (events per second, bursts, loss, SDK overhead); storage (query latency, retention cost, high cardinality, trajectory reconstruction); graph (relationship and lineage query latency, cohort queries); replay (reproduction rate, fixture accuracy, divergence handling); intelligence (detector precision, clustering quality, root-component accuracy). Quantitative targets in PLAN-10.

## 26. Architecture decision register
| ID | Decision | Status |
|---|---|---|
| A-001 | OTel transport, no proprietary transport | DECIDED |
| A-002 | OpenInference compatibility | DECIDED |
| A-003 | Harness-specific semantics as `gen_ai.*` proposals plus `harness.*` registry | DECIDED |
| A-004 | Raw evidence separate from derived interpretations | DECIDED |
| A-005 | Execution graph supplements trace trees | DECIDED |
| A-006 | Instrumentation never requires our gateway | DECIDED |
| A-007 | Polyglot storage | DECIDED |
| A-008 | ClickHouse for analytics | PROPOSED, benchmark required |
| A-009 | PostgreSQL for metadata | PROPOSED |
| A-010 | Object storage for payloads, snapshots, fixtures, customer-side by default | DECIDED |
| A-011 | Adjacency tables, no graph database | DECIDED |
| A-012 | Branch-aware replay is a core target | DECIDED |
| A-013 | Deterministic detectors precede LLM reasoning | DECIDED |
| A-014 | Control path separated from analytics path | DECIDED |
| A-015 | Payload capture configurable; structural-only is a first-class mode | DECIDED |
| A-016 | Tiered capture with published coverage and per-run fidelity | DECIDED |
| A-017 | Lossless side channel alongside OTLP | DECIDED |
| A-018 | Replay runner customer-side by default | DECIDED |
| A-019 | Verification adapter independent of harness | DECIDED |
| A-020 | Event model v0.1 limited to nine domains | DECIDED |
| A-021 | Durable stream technology | OPEN |
| A-022 | Sandbox isolation technology | OPEN |
