# PLAN-04 — Phased Roadmap (36 months, 100+ engineers)

Phases overlap. Each phase lists objectives, workstreams by team, deliverables, exit gate with measurable criteria, approximate headcount, and what is deliberately not built. Gates are from HRCP-02 §75, made quantitative. Month numbers are from first hire.

```
Phase 0  Foundation            M0  ─────── M3
Phase 1  Recorder & Signal         M2 ─────────────── M9
Phase 2  Incidents & Replay v1          M6 ───────────────────── M15
Phase 3  Regression & Score                   M12 ──────────────────────── M24
Phase 4  Optimization & Control                         M20 ───────────────────────── M36
```

---

## Phase 0 — Foundation (M0 to M3)

### Objectives
Answer HRCP-02 §6 with evidence, write the specs the streams will build to, prove the architecture on real agents, and start customer contact on day one.

### Workstreams

**Customer discovery (founders, product, forward-deployed).** Fifty structured conversations in twelve weeks: twenty open-harness builders, twenty closed-harness fleet operators, ten harness vendors. Use HRCP-02 §49 plus: sessions per day; failures per thousand sessions; who finds out; whether coding-agent OTel already flows to Datadog or Grafana; the last harness change and how regression was detected; whether replay in their environment is acceptable; which telemetry cannot leave. Verbatim quotes become a document in `docs/archive/research/`.

**Specification (stream leads).** In this order: HRCP-03 Telemetry and Execution Graph (event model v0.1 limited to ~20 events across RUN, LOOP, MODEL, TOOL/MCP, CONTEXT, PERMISSION, AGENT, VERIFICATION, STOP; identity and version contracts; OTel and OpenInference mapping; fidelity levels), HRCP-07 Security and Privacy (threat model, tenant boundary, redaction, customer-side payload default), HRCP-09 Benchmark (fault-injection design, adoption of LongRCA-Mini and MAST as external baselines), HRCP-08 Integration Framework (adapter contracts for Tier A, B, C), HRCP-04 Replay (manifest, fidelity levels, side-effect classes), HRCP-05 Intelligence (failure taxonomy adopted from "Model or Harness?" and MAST, detector contract), HRCP-10 Open Source (license, governance, repo layout), HRCP-06 Runtime Control (design only).

**Competitive teardown completion (product + 2 engineers).** Finish the HRCP-02 §5 template for the 17 incumbents and 12 newcomers already profiled in `docs/archive/research/`, with hands-on trials of LangSmith Engine, Arize Signal, Laminar, Raindrop, Weave's Claude Code plugin and AgentOps replay.

**Engineering proofs (first 12 engineers).** HRCP-02 §90 Proofs A to G, scoped:
- A: capture a complex Claude Code run via hooks plus OTel into the v0.1 model.
- B: normalize Claude Code and a LangGraph harness into the same model; count framework-specific exceptions.
- C: visualize context changes and verification gates for one run.
- D: detect an injected doom loop and an injected verification bypass.
- E: compare a successful and failed trajectory on one SWE-bench-style task.
- F: identify an injected first divergence (schema change, missing context field) on 50 runs.
- G: replay a recorded Claude Code failure from repo SHA plus container plus recorded model outputs, measure event and outcome fidelity.

**Architecture benchmarks (Data Plane).** ClickHouse vs alternatives on billions of synthetic events with high-cardinality attributes; adjacency-table graph queries vs a graph database; stream technology choice. Resolve A-008, A-009, A-010, A-011.

**Security (Security lead).** Threat model v0.1 covering HRCP-02 §35. Telemetry-as-untrusted-input enforced in the normalizer from day one.

**Company.** Name decided and cleared. Entity, data-rights counsel engaged, OSS license chosen (Apache 2.0 recommended; see PLAN-06), OTel GenAI SIG participation started.

### Deliverables
HRCP-03 to HRCP-10 at v0.1; Proofs A to G with measurements; interview synthesis; architecture decision records for storage and stream; threat model v0.1; name; licensing decision; benchmark v0.1 design.

### Exit gate (Gate A: Semantic Viability; partial Gate B)
- Proof B: both harnesses normalize with under 10% framework-specific event exceptions.
- Proof D: injected loops and bypasses detected with zero false positives on the control set.
- Proof F: injected first divergence found in the top 3 for at least 70% of controlled cases.
- Proof G: at least Level 2 replay fidelity (recorded fixtures) on 80% of recorded failures, Level 3 on 50%.
- Interviews: at least 15 of 50 describe a harness regression they would pay to prevent; at least 10 will host replay in their environment.
If Proof F is under 40% or fewer than 8 of 50 interviews show pain, re-plan before Phase 1 hiring (PLAN-09).

### Headcount: 12 → 30. Not built: anything commercial, any UI beyond the proof, any specialized model.

---

## Phase 1 — Open Flight Recorder and Reliability Signal (M2 to M9)

### Objectives
Ship the open-source product developers actually install; get the event model into six frameworks and three CLIs; prove detectors find real failures; land eight design partners streaming production data.

### Workstreams

**Capture & Standards.** SDKs (Python, TypeScript). Tier A instrumentors: LangGraph, OpenAI Agents SDK, Google ADK, PydanticAI, Claude Agent SDK, OpenHands. Tier B adapters: Claude Code (hooks plus OTel plus raw-bodies side channel), Codex CLI (hooks plus OTel), Gemini CLI. Tier C: generic `gen_ai.*` and OpenInference ingestion, Entire Checkpoints import. Event validators and conformance suite. First upstream proposals to OTel for compaction, permission, verification and stop-reason events (PLAN-06).

**Data Plane.** Ingestion gateway, versioned normalizer, durable stream, raw evidence store, telemetry store, metadata store, content-addressed payloads, identity propagation library (run, agent instance, task, harness version, policy version via OTel baggage), customer-side payload mode from the first release.

**Flight Recorder & DX.** `install → instrument → run → open local UI → inspect` under ten minutes. Timeline, execution tree, subagent tree, context events, permission decisions, stop reasons, basic graph. Local deterministic detectors. CLI (`record`, `run inspect`, `compare`).

**Execution Graph.** Observed edges complete (parent_of, requested_by, approved_by, blocked_by, delegated_to, returned_to, produces, mutates). Fidelity level computed and displayed per run. Reconstructed edges begin: content-addressed derived_from for tool results into context.

**Reliability Intelligence.** Detectors D1 to D10 with the HRCP-02 §13 contract (definition, positive and negative examples, precision, recall, blind spots, cost, latency, version). Detector evaluation on the benchmark. Streaming statistical detectors (failure-rate shift, cost shift, tool-distribution shift).

**Replay & Sandbox.** Replay manifest v1. Fixture capture for coding agents (repo SHA, working tree, image, recorded model and tool outputs, test commands). Sandbox isolation evaluation (container vs microVM) with benchmarks. Side-effect classification v1 for common tools and MCP servers.

**Benchmark & Corpus.** Harness Reliability Benchmark v0.1: fault-injection harness over a coding task suite and a workflow-agent task suite; cases per HRCP-02 §54; LongRCA-Mini and MAST as external baselines. Corpus with data-rights tags from the first record.

**Security & Privacy.** Redaction and secret detection in SDK and collector. Tenant identity in every storage path. Audit log v1.

**Design partners (forward-deployed, product).** Eight signed: four builders, three fleets, one harness vendor. Each streams production structural telemetry within four weeks of signing. Weekly failure review with each.

### Deliverables
OSS release 0.x with six instrumentors and three adapters; managed ingestion in private alpha; detectors D1 to D10 with published precision and recall; benchmark v0.1 public; eight design partners live; first OTel proposals filed.

### Exit gate (Gate B: Developer Utility; Gate C: Reliability Signal)
- OSS: 2,000 weekly active local-UI sessions or 500 distinct organizations, whichever first; median install-to-first-insight under ten minutes in user tests.
- Instrumentation overhead under 3% wall time and under 1% unparseable events on partner traffic.
- Detectors: at least 5 of 10 at precision over 0.9 on partner production data; partners confirm at least 20 real failures found that they had not seen.
- Partners: 6 of 8 still streaming at month 9 and asking for the incident view.

### Headcount: 30 → 75. Not built: incident UI beyond grouping, branch replay, specialized models, control.

---

## Phase 2 — Incident Platform and Replay v1 (M6 to M15)

### Objectives
Commercial launch of the managed platform on incidents, release correlation and cohort comparison; first-divergence v1; replay v1 for coding and workflow agents; regression workbench alpha; context lineage.

### Workstreams

**Reliability Intelligence.** Incident engine: clustering on failure type, first divergence, event sequence, tool, harness version, embedding; incident lifecycle (HRCP-01 §49). Release correlation against git, CI, image, prompt registry, agent and model config, tool registry, policy deployment. Cohort comparison. **First-divergence engine v1**: semantic stage alignment plus event-type alignment plus change-point detection over normalized trajectories; ranked divergence candidates with confidence; root-component candidates with evidence packages; alternatives preserved (HRCP-01 §53). Evaluate on benchmark v0.1 and LongRCA-Mini.

**Execution Graph.** Context lineage: pre- and post-compaction content hashes, declared-state survival detection, reread waste. Memory provenance. Version graph. Cross-run aggregate graph by path hashing. Query API for HRCP-01 §70 questions.

**Replay & Sandbox.** Replay v1 (HRCP-02 §22): reproduce recorded coding-agent trajectories without production side effects, Level 2 to 3. Workflow-agent replay with service fixtures and mocks. Replay divergence tracking (expected vs actual state per step). Replay fidelity metrics (event, state, artifact, outcome). Replay security controls per HRCP-02 §25 and §37. Customer-side replay runner for hybrid deployments.

**Regression & CI.** Incident → replay fixture → expected behaviour → verification requirements. Workbench alpha: baseline vs candidate harness across historical failures and a success control set; report success, cost, latency, new failures, fixed failures. GitHub check on PRs touching harness files for two design partners.

**Data Plane.** Scale to design-partner fleet volumes; tiered retention (structural vs payload vs incident evidence); sampling strategies (error-biased, incident, high-cost, rare-behaviour); self-observability.

**Capture & Standards.** Adapters for Cursor hooks and Devin API (Tier C). Instrumentors for CrewAI, Mastra, Vercel AI SDK. Verification adapter (CI results, test runs, git) independent of harness. OTel proposals iterated; conformance suite public.

**Economics.** Cost per run, per successful run, per verified successful run; loop waste; reread waste; subagent cost; by harness version.

**Runtime Control (nucleus of 4).** Policy language design; intervention adapter contracts; fail-open/fail-closed semantics; nothing autonomous shipped.

**Security & Privacy.** SOC 2 Type I started; DPA template; training-policy controls distinct from operational processing (HRCP-01 §78); regional storage design.

**Design & UX.** Incident Center v1 (HRCP-02 §16), Run Explorer, Context Explorer, Replay Lab alpha.

**Go-to-market.** Commercial launch at month 12 to 14 with incident platform plus replay v1. Pricing experiments per HRCP-02 §62 with partners. Positioning tested per PLAN-07.

### Deliverables
Incident Center GA; release correlation GA; first-divergence v1 in product with confidence; replay v1 for two domains; regression workbench alpha with CI check for two partners; context lineage; economics; commercial launch; first paying customers.

### Exit gate (Gate D: Incident Value; Gate E: Divergence Value; Gate F: Replay Feasibility)
- Incident compression: on partner fleets, at least 100x reduction from failing runs to incidents with partners rating at least 70% of incidents "real and actionable".
- Release correlation finds the causal release for at least 80% of partner-confirmed regressions.
- First divergence: top-3 accuracy at least 70% on benchmark v0.1 injected faults; at least 35% exact root step on LongRCA-Mini (above the published 24%); partners agree with the top hypothesis in at least 60% of reviewed incidents.
- Replay: Level 3 fidelity on at least 60% of recorded coding failures and Level 2 on at least 70% of workflow failures; outcome fidelity (replay reproduces the failure class) at least 75% where Level 3 is achieved.
- Commercial: at least 5 paying customers, at least 2 at six figures annual, at least 1 having changed its release workflow because of the platform (HRCP-02 §51).

### Headcount: 75 → 120. Not built: branch replay, specialized models, autonomous intervention, self-hosted enterprise.

---

## Phase 3 — Regression Platform, Branch Replay, Harness Reliability Score (M12 to M24)

### Objectives
Make the regression gate the product teams cannot ship without; branch-aware replay; the Harness Reliability Score and recommendations with proven deltas; specialized models where they beat rules; enterprise readiness; low-risk runtime control.

### Workstreams

**Replay & Sandbox.** Branch-aware replay (HRCP-02 §24): replay until divergence, branch into controlled live execution, capture the new branch, compare. Counterfactual replay against alternative model, tool version, policy. Live shadow replay for harness candidates. Fidelity Level 4 (near-deterministic sandbox) for coding; network fixture library for workflow agents.

**Regression & CI.** Regression platform GA: suites of production failures, customer cases, synthetic cases, security cases, performance cases. Pareto reporting (HRCP-01 §63). CI integrations for GitHub, GitLab, Buildkite. Merge gate mode. **Recommendations with proven deltas**: each recommendation is a replay experiment with success, cost and regression results attached.

**Reliability Intelligence.** **Harness Reliability Score** v1 across context, tools, recovery, verification, delegation, budget and stop (PLAN-02 §2.2), computed per harness version and fleet, published methodology. Specialized models where they beat the rules-and-statistics baseline on the benchmark: failure-type classifier, first-divergence ranker, root-component classifier, incident similarity encoder (HRCP-02 §30, sequenced per §31). Frontier-model reasoning used only on compressed graph summaries for hard incidents (HRCP-01 §54).

**Runtime Control.** Low-risk interventions: warn, pause, request human, reduce budget, require extra verification (HRCP-02 §32). Policy engine versioned and auditable. Human approval workflows. Integrations with existing gateways and security products for enforcement rather than building a gateway.

**Data Plane & Infra.** Hybrid deployment GA (collector plus payload plus replay customer-side). Self-hosted enterprise packaging. Multi-region. Customer-managed keys.

**Security & Privacy.** SOC 2 Type II; ISO 27001 started; GDPR controls; enterprise DPA; private deployment reviews.

**Capture & Standards.** Spec v1.0 of the harness conventions published with governance; upstreamed items in OTel; instrumentor contributions from the community; harness-vendor native integrations (at least two vendors emitting our control events from their own harness).

**Benchmark & Corpus.** Benchmark v1.0 public with leaderboard; corpus with outcome labels ("fix worked in production") large enough to train the Phase 3 models; external publication of results.

**Design & UX.** Regression Workbench, Harness Compare, Economics, Policy & Control surfaces.

**Go-to-market.** Enterprise motion added to engineering-led; land-and-expand per HRCP-02 §68; partnerships with observability vendors (export incidents into Datadog, Grafana, Honeycomb) and sandbox providers.

### Deliverables
Branch replay; regression platform GA with merge gates; Harness Reliability Score; recommendations with deltas; specialized models v1 where justified; low-risk runtime control GA; hybrid and self-hosted GA; SOC 2 Type II; spec v1.0; benchmark v1.0.

### Exit gate (Gate G: Regression Value; Gate H: Commercial Value)
- Regression: at least 10 customers running the gate on every harness change; at least 20 documented regressions prevented before production; at least 3 customers report a measured verified-success improvement attributable to a recommendation.
- Branch replay: at least 50% of divergence cases successfully branched and compared at Level 3 or better.
- Score: adopted internally by at least 10 customers as a release metric; methodology cited externally.
- Specialized models: each shipped model beats the rules baseline by a published margin on the benchmark, or is not shipped.
- Commercial: net revenue retention over 120% on the Phase 2 cohort; at least 25 paying customers; at least 5 enterprise deployments; pricing architecture chosen from the HRCP-02 §62 experiments.

### Headcount: 120 → 150. Not built: autonomous high-impact intervention, cross-customer intelligence, harness optimization.

---

## Phase 4 — Harness Optimization and Reliability Control (M20 to M36)

### Objectives
Deliver the end state in PLAN-02: harness optimization using replay as the simulator; evidence-derived runtime control including higher-impact interventions under policy; ecosystem reliability intelligence with explicit consent; the verified-autonomy evidence product.

### Workstreams

**Regression & CI → Optimization.** Configuration-space search over compaction policy and thresholds, context budget, retry and backoff, verification requirements per action class, delegation depth and shared context, model and effort per step, tool exposure per phase, stop conditions. Replay-backed Pareto frontiers of verified success against cost and latency. Human approves, canary deploys, production confirms, result enters the corpus (HRCP-02 §94).

**Runtime Control.** Higher-impact interventions (disable tool, deny action, switch model, roll back harness configuration, stop agent) only where the readiness gate (HRCP-02 §33) is met per fleet: measured detector precision, false-positive rate, attribution accuracy, rollback reliability, policy correctness, control-plane availability. Policies derived from measured failure classes. Full control audit.

**Reliability Intelligence.** Cross-customer learning only under explicit data rights; Harness Reliability Advisories for models, tools, MCP servers and frameworks; model and framework reliability index. Context-loss, tool-misuse and verification-weakness detectors as specialized models. Regression-risk estimator for proposed changes.

**Verified-autonomy evidence.** Per-fleet evidence packages: verified success rate, unsafe-action rate, reproduction rate, regression coverage, intervention audit, suitable for risk, audit and procurement. The long-term value metric moves toward verified autonomous work (HRCP-00 §60).

**Capture & Standards.** Browser, research and computer-use agent domains added. Spec v2 with community governance board.

**Enterprise.** Regional deployments by demand; additional compliance by demand (HRCP-02 §41).

### Deliverables
Harness optimizer GA for at least two task classes; runtime control with policy-gated high-impact interventions; advisories program; verified-autonomy evidence packages; two new agent domains.

### Exit gate (Gate I: Control Readiness, plus optimization value)
- Optimizer: on at least 5 customer task classes, a replay-recommended configuration improves verified success per dollar by a measured margin confirmed in production.
- Control: zero production incidents caused by false-positive interventions over a defined measurement period per fleet before high-impact interventions are enabled for that fleet.
- Advisories: at least 10 published with confirmed upstream fixes.
- Commercial: the HRCP-02 §93 north-star demonstration performed live on a customer fleet.

### Headcount: ~150 steady state.

---

## Cross-phase rules

1. **Gates fund phases.** A stream's next-phase headcount is released when its gate passes. Streams can be ahead or behind each other.
2. **Nothing autonomous before measurement.** Detector precision, attribution accuracy and rollback reliability are published numbers before interventions move past "warn and pause".
3. **Specs lead code by one phase.** HRCP-0x at v0.1 before the stream scales.
4. **Open and closed harnesses move together.** Every phase adds capability for Tier A and Tier B; Tier C follows where APIs allow.
5. **Two domains, then more.** Coding and API-workflow agents through Phase 3; browser, research and computer-use agents in Phase 4.
6. **The benchmark team grades everyone.** Detector, divergence, replay and model claims are evaluated by Benchmark & Corpus, not by the teams making them.

## Small-team variant

If the team is 2 to 5 people, run Phase 0 as written (minus hiring), then Phase 1 limited to Claude Code plus one open harness, D1/D4/D5/D6/D8 only, and one design partner, and go directly to the regression gate for that partner before any incident UI. Timeline to the first paid regression gate: 6 to 9 months.
