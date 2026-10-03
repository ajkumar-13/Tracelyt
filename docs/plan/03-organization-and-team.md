# PLAN-03 — Organization and Team

Assumption: capital to hire 100+ engineers over 12 to 18 months and run for 24 to 36 months. Indicative cost: fully loaded engineering at $250K to $300K per head per year in the US and Europe, less with a distributed team; 95 engineers plus GTM, infrastructure and research compute runs $40M to $50M per year at steady state. A 30-month plan at this scale is an $80M to $110M program. Comparables: Entire raised $60M seed; Braintrust $121M total; Raindrop ~$50M. This plan is a Series A or B scale company from day one and should be presented as such.

## 1. Operating model

- **Streams, not layers.** Teams are organized around the stages of the Harness Engine so that each owns an outcome, not a tier of the stack. Platform and infrastructure are shared services.
- **Evidence gates still gate.** A large team does not skip HRCP-02's gates; it runs the streams in parallel and funds each stream's next phase when its gate passes. See PLAN-04.
- **Every stream dogfoods.** We run our own agents (coding and internal workflow) through the full engine. Our incidents become our regression cases (HRCP-01 §84).
- **Specs before scale.** HRCP-03 through HRCP-10 are written in Phase 0 by the stream leads, as one-page ADRs plus a spec, not as novels. Source-of-truth hierarchy per HRCP-02 §80.
- **Research is embedded.** Attribution, alignment, replay fidelity and clustering researchers sit inside the Intelligence and Replay streams with a shared benchmark team, not in a separate lab.

## 2. Teams and steady-state headcount (month 18)

| Team | Mandate | Eng | Notes |
|---|---|---|---|
| **Capture & Standards** | SDKs (Python, TypeScript, Go), framework instrumentors (LangGraph, OpenAI Agents SDK, Google ADK, PydanticAI, Claude Agent SDK, OpenHands, CrewAI, Mastra, Vercel AI SDK), closed-harness adapters (Claude Code, Codex, Gemini CLI, Cursor, Devin API, Entire Checkpoints, durable-execution journals), OTel SIG participation, event validators | 16 | Includes 2 permanent adapter-maintenance engineers because closed harnesses ship weekly. 1 to 2 engineers assigned to OTel GenAI SIG work half-time. |
| **Data Plane** | Ingestion gateway, semantic normalizer (versioned), durable stream, raw evidence store, telemetry store (ClickHouse, benchmarked), object store, metadata (Postgres), identity propagation, sampling, backpressure, content addressing, hybrid deployment (customer-side payload and sandbox) | 14 | Owns the contracts in HRCP-02 §71: identity, versioning, event semantics, provenance, tenant boundary, schema evolution, replay references. |
| **Flight Recorder & Developer Experience** | OSS CLI, local recorder, local UI, Run Explorer, Context Explorer, timeline and trajectory views, subagent tree, artifact history, docs, examples | 10 | The open-source product. Measured on install-to-insight time. |
| **Execution Graph & Query** | Graph builder (observed, reconstructed, inferred edges with provenance), context lineage, memory provenance, version graph, query model and API, cross-run aggregate graphs, fidelity levels | 10 | Owns HRCP-03's graph half. |
| **Reliability Intelligence** | Deterministic detectors (D1 to D10 and beyond), streaming statistical detectors, incident engine and clustering, release correlation, cohort comparison, first-divergence engine, root-component attribution, confidence and evidence packaging, specialized models (Phase 3+) | 16 | 4 are research engineers. Owns HRCP-05. |
| **Replay & Sandbox** | Replay manifest, fixture capture (model and tool outputs, MCP, network), environment snapshots (container, filesystem, repo SHA), sandbox isolation (microVM evaluation), side-effect classification, branch replay, fidelity measurement, replay security | 14 | Owns HRCP-04 replay half and the replay parts of HRCP-07. 3 are sandbox and security specialists. |
| **Regression & CI** | Regression workbench, incident-to-case conversion, control sets, CI integrations (GitHub, GitLab, Buildkite), Pareto reports, PR check output, recommendations with deltas, optimization search (Phase 4) | 8 | Owns HRCP-04 regression half. |
| **Benchmark & Corpus** | Harness Reliability Benchmark, fault injection harness, labelled corpus with data rights, LongRCA and MAST integration, labeling tooling, evaluation of our own detectors and attribution | 6 | Owns HRCP-09. Independent of the teams it measures. |
| **Security & Privacy** | Threat model, tenant isolation, redaction and secret detection, encryption and key options, retention, audit log, compliance (SOC 2, ISO 27001, GDPR), telemetry-is-untrusted-input enforcement | 6 | Owns HRCP-07. Starts Phase 0 per HRCP-02 §34. |
| **Infrastructure & SRE** | Cloud, Kubernetes, multi-region, self-observability, cost engineering, hybrid and self-hosted packaging, control-path vs analytics-path separation | 8 | Owns HRCP-00 §55 SLO philosophy. |
| **Runtime Control** | Policy engine, intervention adapters, approval workflows, control audit, fail-open/fail-closed semantics, integration with gateways and security products | 4 → 10 | Starts at 4 in Phase 2 for design and low-risk interventions; grows in Phase 4. Owns HRCP-06. |
| **Design & UX** | Incident Center, Run Explorer, Context Explorer, Replay Lab, Regression Workbench, Harness Compare, Economics | 5 | Different interfaces per HRCP-00 §64, not one waterfall. |
| **Engineering total** | | **~117** | |

### Non-engineering (month 18)

| Function | Head | Notes |
|---|---|---|
| Product management | 7 | One per major stream plus a platform PM |
| Developer relations & community | 4 | OSS adoption, instrumentor contributions, standard advocacy, benchmark publication |
| Forward-deployed / solutions engineers | 8 | Embedded with design partners; instrument, replay, and feed back |
| Sales & partnerships | 6 | Engineering-led motion; partnerships with observability vendors, harness vendors, sandbox providers |
| Research scientists (shared) | 3 | Alignment, causal attribution, replay fidelity |
| Finance, legal, people, ops | 7 | Legal matters early: data rights, DPAs, training policy |
| **Total company** | **~152** | |

## 3. Hiring sequence

**Months 0 to 3 (to ~30):** Founding leads for Capture & Standards, Data Plane, Intelligence, Replay, Security, and Product. Two forward-deployed engineers. Head of Design. First devrel. The people who write HRCP-03 to HRCP-10.

**Months 3 to 9 (to ~75):** Fill Capture (instrumentors and adapters are the long pole), Data Plane, Flight Recorder, Graph, Intelligence detectors, Replay fixtures and sandbox, Benchmark. Second wave of forward-deployed engineers as design partners sign.

**Months 9 to 18 (to ~150):** Regression & CI, specialized models research, Runtime Control nucleus, Infra for hybrid and self-hosted, compliance, sales.

**Months 18 to 36:** Replace attrition; grow Runtime Control and Optimization; regional and compliance expansion driven by enterprise demand.

## 4. Roles that are unusual and must be hired deliberately

- **Sandbox and isolation engineers** (microVM, gVisor, Firecracker, network policy). Replay executes hostile content.
- **Instrumentation engineers who have shipped OTel instrumentors** and can work inside framework communities.
- **Standards engineers** with OTel or CNCF SIG experience.
- **Sequence alignment and causal inference researchers** for first divergence, ideally with agent-trajectory benchmark publications (LongRCA, MAST, TRAIL authors are a hiring pool).
- **Forward-deployed engineers** who can live in a design partner's environment and instrument a custom harness in a week.
- **Data rights counsel.** The corpus is the asset; its legality is the risk.

## 5. Decision rights

- HRCP-00 changes: founders plus stream leads, recorded as decision changes (HRCP-02 §81).
- Architecture: ADR process (HRCP-02 §79), owned by the Data Plane lead as architect of record.
- Schema and standard: Capture & Standards lead, with a public RFC process once the spec is published.
- Gate decisions: a monthly gate review using the metrics in PLAN-10; streams present evidence, not progress.

## 6. What a 100-engineer team must not do

- Build all seven layers simultaneously to the same depth. Depth follows gates.
- Let the platform (ingestion, storage) outrun the semantics. Garbage telemetry then expensive reasoning (HRCP-02 §74).
- Build the enterprise dashboard before the differentiated intelligence exists.
- Ship runtime control before detector precision is measured.
- Treat the standard as marketing. It is engineering with a release schedule and conformance tests.
