# PLAN-05 — Architecture Deltas to HRCP-01

HRCP-01 remains the architecture baseline. This document records what the October 2026 research changes, as proposed decision changes (HRCP-02 §81 format: old, new, reason, evidence, affected components, migration) and new ADR candidates.

## 1. Proposed changes to DECIDED and PROPOSED items

### C-1. Capture is tiered, and fidelity is disclosed per run
- **Old (HRCP-01 §5 to §7):** capture sources listed; automatic where possible; explicit where needed.
- **New:** three explicit capture tiers (A native instrumentation, B hook and OTel adapters for closed harnesses, C API and log adapters), each with a published coverage matrix against the event model, and a computed **fidelity level per run** for both graph reconstruction and replay.
- **Reason:** closed harnesses expose different surfaces (Claude Code 33 hooks plus OTel; Codex 12 hooks plus OTel with gaps in `exec` and `mcp-server`; Cursor hooks only; Devin API only). Pretending uniform capture produces silent gaps in the graph.
- **Evidence:** `docs/research/03` §B.
- **Affected:** Capture & Standards, Execution Graph, Replay, UI.
- **Migration:** none; new.

### C-2. Customer-side payload and replay are the default architecture, not an option
- **Old (HRCP-01 §73 to §74, HRCP-00 §59):** hybrid listed as one of several deployment models; managed SaaS plus OSS local as likely start.
- **New:** structural telemetry to the managed service; payloads, snapshots and replay execution customer-side by default, with managed payload storage as the opt-in simplification for small teams.
- **Reason:** solves three problems at once: telemetry volume economics for long-running agents, data residency and "telemetry cannot leave" objections, and replay security (hostile content executes in the customer's sandbox, not ours).
- **Evidence:** HRCP-00 §81 Risk 7; interview question in HRCP-02 §49; research track 4 on buyer resistance to another vendor holding payloads.
- **Affected:** Data Plane, Replay, Security, pricing.
- **Migration:** design the collector and replay runner for customer-side from v0.1.

### C-3. Harness Event Model is published as an OTel `gen_ai.*` extension plus a `harness.*` registry, not as a private schema
- **Old (HRCP-00 §11, D-028):** HEM as our semantic specification, aligned with OTel and OpenInference "where possible".
- **New:** every control event is proposed upstream as `gen_ai.*` attributes and events; items OTel has not accepted live in a `harness.*` namespace registry with a published mapping. The product consumes both. The HEM name is internal.
- **Reason:** standards win through implementers. OTel has no convention for compaction, permissions, verification or stop reasons and the open proposals (#159, #181) are unowned. Leading that work is the realistic route to adoption; a private name is not.
- **Evidence:** `docs/research/03` §A.
- **Affected:** Capture & Standards, Normalizer.
- **Migration:** v0.1 event names defined with both forms from the start.

### C-4. Event model v0.1 is small
- **Old (HRCP-01 §12):** 24 top-level domains.
- **New:** v0.1 covers nine domains (RUN, LOOP, MODEL, TOOL/MCP, CONTEXT, PERMISSION, AGENT, VERIFICATION, STOP) with roughly twenty events; the other domains (PLAN, MEMORY, RETRIEVAL, HOOK, POLICY, SANDBOX, STATE, HUMAN, ARTIFACT, BUDGET, RECOVERY, ENVIRONMENT) arrive in v0.2 and v0.3 after real traffic validates v0.1. Unknown events are captured via the extensibility structure (HRCP-01 §86).
- **Reason:** adoption is inversely proportional to schema size; OTel GenAI has ~15 operation names after two years.
- **Affected:** everything downstream of the normalizer.

### C-5. Failure taxonomy is adopted, not invented
- **Old (HRCP-00 §72):** 22-class proposed taxonomy.
- **New:** adopt the "Model or Harness?" interaction-centric taxonomy (41 modes assigned to component edges with a fault side) as the primary classification, with MAST's 14 modes and LongRCA's responsible-role labels as mappings; our 22 classes become the component dimension of that taxonomy.
- **Reason:** compatibility with public benchmarks (LongRCA, TRAIL, MAST) and with the research community we are hiring from.
- **Affected:** Intelligence, Benchmark.

### C-6. Graph storage: adjacency tables, no graph database
- **Old (HRCP-01 §41, A-011):** OPEN.
- **New:** materialized adjacency and lineage tables in the analytical store; per-run graphs are hundreds to tens of thousands of nodes; cross-run aggregate graphs via path hashing. Revisit only if lineage traversal latency fails the Phase 1 benchmark.
- **Reason:** query shapes are per-run and per-cohort, not global traversals.
- **Affected:** Execution Graph, Data Plane.

### C-7. Replay strategy: two domains, fixture-plus-snapshot, Level 2 to 3 first
- **Old (HRCP-02 §21 to §24):** coding agents first; branch replay after deterministic replay.
- **New:** coding agents (container plus repo SHA plus recorded fixtures) and API-workflow agents (service fixtures and mocks) in parallel from Phase 2; fidelity Level 2 to 3 is the Phase 2 target, Level 4 is Phase 3; branch replay is Phase 3. The replay runner executes customer-side by default (C-2).
- **Reason:** no standard or product pairs frozen model fixtures with per-step environment snapshots; LangGraph "replay" re-executes LLM calls; Claude Code checkpoints miss Bash side effects. Fidelity disclosure is mandatory to be honest about this.
- **Evidence:** `docs/research/03` §C.

### C-8. Regression gate is the commercial lead; replay is its mechanism
- **Old (HRCP-00 §83 Q3):** whether the first commercial offering begins with incidents or replay is OPEN.
- **New:** commercial launch leads with incidents plus release correlation (Phase 2), and the product customers cannot ship without is the regression gate (Phase 3). Replay is sold as the proof mechanism behind the gate, never as a standalone feature.
- **Reason:** incidents are commoditizing (seven vendors); "re-run last week's failures against the new harness" is unshipped by anyone.

### C-9. "Control plane" moves from category name to Phase 4 capability
- **Old (HRCP-00 §4, D-030):** Harness Reliability Control Plane as commercial category.
- **New:** category language is "reliability engine for the system around the model" or "harness engineering platform"; runtime control remains Layer 7 and arrives per HRCP-02 §33.
- **Reason:** control planes and kill switches are a CISO-owned category with $100M+ rounds and $250M+ exits; the developer buyer does not want a "control plane" from a new vendor.

### C-10. Lossless side channel alongside OTLP
- **New:** OTLP export is sampled, truncated (60 KB) and flush-bounded, so replay-grade capture requires a parallel side channel: raw request and response bodies to customer-side disk or object store (Claude Code already supports `file:<dir>`), filesystem snapshots, and content-addressed payload references in the events.
- **Reason:** nothing in OTel defines a replayable record.

### C-11. Verification adapter independent of harness
- **New:** verification events are produced by an adapter that reads CI results, test runs, lint, build and git state, in addition to any harness-emitted verification events.
- **Reason:** no harness emits first-class verification; coding verification is external anyway; this gives Tier B and C runs verification evidence.

## 2. Confirmations (research supports HRCP-01 as written)

- A-001 OTel transport, A-002 OpenInference compatibility, A-003 harness semantics, A-004 raw evidence separate from derived, A-005 graph supplements trace tree, A-006 no mandatory gateway, A-007 polyglot storage, A-013 deterministic detectors before LLM reasoning, A-014 intervention separated from analytics, A-015 configurable payload capture: all confirmed.
- A-008 ClickHouse: still benchmark-required, but every serious competitor (Langfuse, Laminar, Braintrust's Brainstore, AGNTCY reference stack) converged on it or a custom columnar store; the benchmark is about schema and retention tiers, not whether.
- HRCP-01 §44 edge provenance (runtime, normalizer, detector, statistical inference, reasoning model, human analyst): confirmed as a differentiator. No vendor distinguishes edge provenance in product.
- HRCP-01 §57 replay trust levels: confirmed; extend the same disclosure to graph fidelity (C-1).
- HRCP-01 §82 content addressing: confirmed and promoted to a core contract (C-10).

## 3. New ADR candidates for Phase 0

| ADR | Decision to make |
|---|---|
| ADR-001 | Identity propagation: OTel baggage keys for run, agent instance, task, harness version, policy version; behaviour when the harness does not propagate (Claude Code subprocesses) |
| ADR-002 | Event naming: `gen_ai.*` proposal form and `harness.*` fallback form; mapping table ownership |
| ADR-003 | Fidelity level computation for graph and replay; display contract |
| ADR-004 | Customer-side payload reference format (content hash, store URI, encryption) |
| ADR-005 | Analytical store choice and retention tiers after the Phase 0 benchmark |
| ADR-006 | Durable stream choice |
| ADR-007 | Sandbox isolation technology for replay after the Phase 1 benchmark |
| ADR-008 | Side-effect classification schema for tools and MCP servers |
| ADR-009 | Detector contract and versioning |
| ADR-010 | Data-rights tagging schema for the corpus |
| ADR-011 | Normalizer versioning and re-derivation policy (HRCP-00 §71) |
| ADR-012 | OSS license and repository boundary (see PLAN-06) |

## 4. Capability by capture tier (target at end of Phase 2)

| Event domain | Tier A (native) | Tier B (Claude Code, Codex, Gemini CLI) | Tier C (Cursor, Devin, generic OTel) |
|---|---|---|---|
| RUN, LOOP, STOP | full | full (session, stop reason, iteration via prompt sequence) | partial |
| MODEL | full | full (tokens, model, stop reason; bodies via side channel) | tokens only |
| TOOL / MCP | full | full (request, decision, result, duration) | partial |
| CONTEXT (compaction, provenance) | full | boundaries and token deltas; summary content via side channel where available; InstructionsLoaded provenance on Claude Code | none |
| PERMISSION | full | full (request, decision, source, denial reason) | shell and MCP decisions on Cursor only |
| AGENT (delegation) | full | full on Claude Code and Codex; none on Gemini CLI | none |
| VERIFICATION | full (harness-emitted plus adapter) | adapter only | adapter only |
| MEMORY, STATE, ARTIFACT | full | file artifacts via tool events; no memory | none |

This matrix is published with the standard so customers know what they are getting before they instrument.
