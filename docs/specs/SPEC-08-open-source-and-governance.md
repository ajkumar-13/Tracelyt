# SPEC-08 — Open Source and Governance, v0.1

**Version:** 0.1.0 · **Status:** PROPOSED · **Owner:** Capture & Standards with DevRel · **Depends on:** PLAN-06, PLAN-11 D-036, research 01 §A.6/A.7, research 08

## 1. Repositories (initial)
| Repo | Contents | License |
|---|---|---|
| `<spec>` (name per §5) | `harness.*` attribute registry (YAML, weaver-compatible), event definitions, `gen_ai.*` mapping table, OpenInference mapping, conformance suite, fidelity-level definitions, coverage-matrix format, RFCs | Apache 2.0 (spec text CC-BY-4.0) |
| `<spec>-python`, `<spec>-typescript` | SDKs: event model, PayloadRef, identity propagation, redaction, local buffer, OTLP export, side-channel writers | Apache 2.0 |
| `<spec>-instrumentation` | Tier A instrumentors (LangGraph, OpenAI Agents SDK, ADK, PydanticAI, Claude Agent SDK, OpenHands; then CrewAI, Mastra, Vercel AI SDK) | Apache 2.0 |
| `<spec>-adapters` | Tier B hook adapter (Claude Code, Codex, Gemini CLI shared contract), OTLP receiver, Tier C adapters (Cursor hooks, Devin API, Entire Checkpoints, generic gen_ai/OpenInference) | Apache 2.0 |
| `<recorder>` | Local recorder CLI (`qar` or `hrec` per research 08), local store, local UI, basic deterministic detectors D1 to D10 | Apache 2.0 |
| `<spec>-benchmark` | Harness Reliability Benchmark generator, fault library, converters for LongRCA, Who&When, TrajErrBench, AgentRx, TRAIL, MAST; public corpus items with `open_source_permitted` rights | Apache 2.0 (data CC-BY-4.0 or per source license) |

Commercial (closed): managed ingestion and fleet storage, incident engine, first divergence and attribution at scale, context lineage at scale, replay infrastructure and orchestration, regression platform and CI gates, Harness Reliability Score, recommendations, specialized models, optimization, runtime control, enterprise deployment, advisories.

## 2. License (D-036)
Apache 2.0 for code; CC-BY-4.0 for specification text and public corpus. Rationale: the open layer's job is adoption; Elastic License 2.0 (Phoenix) is widely misread and causes friction; the commercial layer is a different codebase.

## 3. RFC and release process
- Registry or event changes go through a public RFC (motivation, proposed attributes with types and requirement levels, affected emitters, migration). Two maintainer approvals; one from Capture & Standards.
- Registry versions are semantic; `0.x` may change with a documented migration; breaking changes after `1.0` are rare and ship with a conformance-suite update.
- Monthly releases; instrumentors pin a registry version.

## 4. Conformance program
An emitter passes when its events validate against the schema, carry required identity fields, use only registered enum values, and its published coverage matrix matches a test capture. Output: a badge plus the matrix. The reference adapters are the first conformers (Claude Code: Proof A).

## 5. Naming (recommendation; founder approves)
Specification: **Agent Harness Semantic Conventions**, repo `harness-semconv`, namespace `harness.*` (free on PyPI, npm, crates, Homebrew; GitHub org free; mirrors OTel wording). Recorder CLI: **`qar`** (quick access recorder; free on all registries), `hrec` as fallback. Caveat from research 08: a descriptive spec name cannot be held as a trademark, so PLAN-06 §6 is amended: the company holds only the product mark; Harness Inc.'s HARNESS marks are checked by counsel before public use.

## 6. Upstream program (Track 1)
First proposals, in order, each with a prototype in our instrumentors:
1. Support and extend **PR #535** `gen_ai.tool.call.decision`: add `gen_ai.tool.call.decision.source` and `.reason` (observed on Claude Code and Codex).
2. **Context provenance** per issue #181, with observed fields (`content.hash`, `kind`, `loaded_by`); evidence from InstructionsLoaded.
3. **Compaction event** `gen_ai.context.compaction` (trigger, tokens before/after, summary ref), extending the existing `gen_ai.conversation.compacted` marker; evidence from PostCompact and `compact_boundary`.
4. **Agent-level stop reason** `gen_ai.agent.stop.reason`, distinct from `gen_ai.response.finish_reasons`.
5. **Verification event** `gen_ai.verification`, distinct from `gen_ai.evaluation.result`.
6. **Agent instance identity** aligned with PR #445 (`gen_ai.agent.execution.id`) and issue #37 (`gen_ai.task.requester.*`).
7. Participation in issue #320 (harness hook stages) with the HOOK domain fields observed in Claude Code.
Budget: two engineers at half time plus devrel; the product never blocks on upstream acceptance (PLAN-06 §9).

## 7. Governance
Phase 1: company maintainers, public RFC process, published roadmap. Phase 3: technical steering group with at least two framework maintainers and one harness vendor; foundation home evaluated (CNCF sandbox or Linux Foundation, where AGNTCY lives) only if it does not slow upstream work (D-047 OPEN).

## 8. Community program
Bounties for long-tail framework adapters, tool and MCP side-effect classifications, detectors, visualizations, benchmark scenarios. Quarterly public benchmark results. Inbound = outbound Apache 2.0 with DCO; no CLA.

## 9. Adoption metrics
Per PLAN-06 §8: emitters (native vs via our packages), installs, upstream proposals by status, conformance passes, external contributors.
