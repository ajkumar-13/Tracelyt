# PLAN-06 — Open Standard Strategy

## 1. Objective

Make the harness control-event model the thing agent frameworks and harness vendors emit by default, so that customers arrive with data already in our shape. The standard is distribution and legitimacy, not protection (HRCP-00 §36, §37; HRCP-02 §45).

## 2. Honest position on terminology

- "Harness" is now the practitioner term (Hashimoto, Sequoia, deepset, Fiddler, OpenLIT). We use it and do not try to own it.
- "Harness Event Model", "Harness Execution Graph", "Flight Recorder" and "Control Plane" are internal names. Externally, the convention is the attribute namespace, and success means nobody says "HEM" because they say `gen_ai.context.compaction`.
- The names worth owning are product nouns: first divergence, fidelity level, Harness Reliability Score, verified success, cost per verified success.

## 3. Two-track publication

**Track 1: upstream to OpenTelemetry GenAI.** Propose control events as `gen_ai.*` extensions through the GenAI SIG, taking ownership of the unowned issues:
- Checkpoint, pause and resume span events (issue #159 territory): `gen_ai.agent.paused`, `.resumed`, `.checkpointed`, with reason and checkpoint id.
- Context provenance (issue #181 territory): what context was loaded, by which mechanism, hashed not content.
- New proposals: context compaction (`trigger`, `tokens_before`, `tokens_after`, `summary_ref`, `policy_version`), permission decision (`actor`, `resource`, `action`, `decision`, `source`, `policy_version`, `reason`), verification (`claim_ref`, `evidence_refs`, `evaluator`, `policy`, `outcome`), stop reason taxonomy beyond `finish_reasons`, delegation (`parent_agent_instance`, `child_agent_instance`, `task_ref`, `shared_context_refs`, `budget`), subagent instance identity distinct from `gen_ai.agent.id`.
- Participation: one to two engineers at half time in the SIG from Phase 0; co-author the agentic conventions meta-issue (#35) work; contribute to the MCP conventions where tool semantics overlap.
- Expectation: 12 to 24 months to Development-status acceptance of a subset; Stable status is years away for all of `gen_ai.*`.

**Track 2: a `harness.*` registry we govern.** Everything OTel has not accepted, published as an attribute registry with versioning, conformance tests and a mapping table to `gen_ai.*` and OpenInference. Modelled on OpenInference's relationship to OTel. The product consumes both tracks identically.

## 4. Instrumentors and adapters as the adoption engine

| Tier | Targets | Phase | Mechanism |
|---|---|---|---|
| A | LangGraph, OpenAI Agents SDK, Google ADK, PydanticAI, Claude Agent SDK, OpenHands | 1 | Instrumentor packages emitting both `gen_ai.*` and `harness.*`; upstream PRs to frameworks that have native OTel (PydanticAI, ADK, AutoGen, Mastra, Vercel AI SDK) |
| A | CrewAI, Mastra, Vercel AI SDK, AutoGen/AG2, Temporal and Restate journals | 2 | As above; durable-execution journals as Tier A sources |
| B | Claude Code, Codex CLI, Gemini CLI | 1 | Hook adapter (shared stdin-JSON contract) plus OTLP receiver plus side-channel capture; study and possibly collaborate with `o11y-dev/opentelemetry-hooks` |
| C | Cursor hooks, Devin API, Entire Checkpoints, generic `gen_ai.*` and OpenInference | 2 | API and log adapters |
| Vendor-native | Cognition, Cursor, Factory, Replit, Sierra, model-lab agent products | 3 | Design-partner relationships; the goal is two vendors emitting our control events natively by Phase 3 |

Conformance suite: any emitter can validate against the spec. Published coverage matrix per emitter (PLAN-05 §4).

## 5. Open-source boundary

Open (Apache 2.0): specification and registry, conformance suite, SDKs, instrumentors and adapters, collector components, local recorder and local UI, basic deterministic detectors (D1 to D10), benchmark harness and public corpus, CLI.

Commercial: managed ingestion and fleet storage, incident engine and clustering, first divergence and attribution, context lineage at scale, replay infrastructure and sandbox orchestration, regression platform and CI gates, Harness Reliability Score, recommendations with deltas, specialized models, optimization, runtime control, enterprise deployment, governance and compliance, advisories.

Why Apache 2.0 over a source-available license: the open layer's job is adoption; the commercial layer is not the open layer. Phoenix's Elastic License 2.0 is widely misreported as Apache and causes friction; avoid it.

## 6. Governance

- Phase 1: spec in our repository with a public RFC process and a published roadmap; we are the maintainers.
- Phase 3: a technical steering group with seats for at least two framework maintainers and one harness vendor; neutral project naming; consider a foundation home (CNCF sandbox or Linux Foundation, where AGNTCY already lives) only if it does not slow the upstream OTel work.
- Trademark: the spec name is held by the company until a foundation transfer; the product name is distinct.

## 7. Community program

Contribution targets: framework adapters, tool and MCP side-effect classifications, detectors, visualizations, benchmark scenarios (HRCP-02 §46). Bounties for adapters to long-tail frameworks. Quarterly public benchmark results.

## 8. Adoption metrics (reported monthly)

- Emitters: number of frameworks and harnesses emitting `harness.*` or accepted `gen_ai.*` control events; number emitting natively without our packages.
- Installs: SDK and instrumentor downloads; distinct organizations with the local recorder.
- Upstream: proposals filed, in review, accepted at Development status.
- Conformance: emitters passing the suite; coverage score per emitter.
- Community: external contributors, adapters contributed, benchmark submissions.

## 9. Risks specific to the standard

- **Vendors standardize their own namespaces.** Claude Code emits `claude_code.*`; W&B emits `forge.permission_request`. Mitigation: ship mappings for each immediately; upstream fast enough that mapping to `gen_ai.*` is the path of least resistance.
- **OTel rejects control events as out of scope.** Mitigation: Track 2 is complete on its own; OpenInference proves a parallel vocabulary can reach 40+ instrumentors.
- **OpenLIT or another OSS project claims the space first.** OpenLIT rebranded around harness engineering on 1 Oct 2026 without a schema. Mitigation: publish the registry and conformance suite in Phase 1; invite them to adopt it.
- **Standard work consumes the team.** Mitigation: capped at two half-time engineers plus devrel; the product never blocks on upstream acceptance.
