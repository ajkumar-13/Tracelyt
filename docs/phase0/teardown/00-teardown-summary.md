# Competitive Teardown — Phase 0 completion (HRCP-02 §5 template, condensed)

Full per-vendor rows with sources: `docs/phase0/research/07-competitor-data-models.md` (schemas read from primary repositories at pinned commits). This document records the decisions the teardown produces: what to integrate, what never to rebuild, what remains unaddressed, and the corrections to our own earlier claims.

## 1. Corrections to PLAN-01 §4 (recorded as Phase 0 amendments)
| Earlier claim | Correction (evidence) | Effect |
|---|---|---|
| "None of 17 platforms ship replay" | **Laminar** serves cached LLM responses keyed by `(project, replay_trace_id, cache_until, input_hash)` with system messages excluded; replays from cache until the first miss, then runs live; tools are not stubbed. **LangSmith Engine** fix validation replays an issue's trace inputs against baseline and preview deployments as experiments. | Differentiator 1 narrows to: deterministic replay of **tools and environment**, S1 verified matching with divergence detection, and **branching from an arbitrary recorded step**, across vendors. Still unshipped by anyone. |
| "Galileo Agent Control OSS unverified" | Open source at `github.com/agentcontrol/agent-control`, Apache-2.0; canonical actions `deny`, `steer`, `observe` (allow/warn/log are aliases). | SPEC-04 integrates it as an enforcement point. |
| "OpenLIT has branding, no schema" | OpenLIT defines 68 `coding_agent.*` constants and a strict adapter contract: edit decisions, permission mode, subagent spawn/complete, git commit and PR, loop detection, session outcome enum. | The closest existing closed-harness schema. SPEC-01's mapping table must include it; propose convergence rather than compete on vocabulary. |
| "Weave has no failure clustering" | Server-side `intent_signatures`, `failure_signatures`, `signature_cluster_runs`, `signature_clusters`; server-side PII redaction `pii-v1`. | Clustering is commodity (now eight vendors). |
| Phoenix DECISION span kind = agent decision | It is a call to a decision model that scores candidates (`decision.*` attributes). | Remove from the harness-event prior-art list. |
| OTel has no harness concepts | `gen_ai.conversation.compacted`, memory operations, `plan`, `invoke_workflow`, `gen_ai.main_agent.*`, `gen_ai.skill.*` exist at Development status; collector-contrib `genainormalizerprocessor` (alpha) rewrites OpenInference and OpenLLMetry into `gen_ai.*` and Dynatrace ships it. | Our normalizer overlaps the upstream processor for the commodity layer; build ours as a superset that consumes it rather than a parallel implementation. |
| Datadog has no RCA | Insights (inefficient caching, large tool results, verbose output, tool-call retry loops, prompt rule violations; auto-resolve) and Patterns (UMAP + HDBSCAN). | Datadog detects a subset of our D-series natively; our differentiation is attribution to harness components and the regression gate, not detection alone. |

## 2. Per-vendor decisions (integrate / never rebuild / unaddressed)
| Vendor | Integrate | Never rebuild | Unaddressed by them |
|---|---|---|---|
| LangSmith | export incidents into their UI for LangGraph shops; consume `langsmith.*` span attributes; study Engine's issue schema | run storage, playground, evaluators, prompt management | component-level attribution, deterministic tool replay, regression gate on harness changes, cross-vendor |
| Langfuse (ClickHouse) | ingest `langfuse.*` observation types; MCP server as an analyst surface | observation storage, scores, prompt management | clustering worker, RCA, replay, regression |
| Phoenix / Arize AX (Dynatrace) | OpenInference instrumentors as Tier A sources; study Signal's issue output | Phoenix UI, evaluators, experiments | deterministic replay, regression gate, harness component model, cross-run divergence as a primitive |
| Laminar | nothing to integrate yet; decide relationship (company doc) | their ClickHouse signals pipeline | tool and environment replay, branching, regression gate, harness semantics, open standard |
| Raindrop | ingest `raindrop.*` events if a customer has them | issue triage agents | replay, attribution, regression gate, open standard, coding-agent fleets |
| Judgment Labs | Judgeval traces as a Tier A source | scorers | deterministic replay, harness model, closed harnesses |
| W&B Weave / Forge | `weave-claude-code` plugin as prior art for Tier B; map `forge.*` and `weave.compaction.*` | Weave call storage | branching replay, regression gate, cross-vendor control events |
| AgentOps | nothing (time travel removed from SDK 0.4) | — | everything beyond visual replay |
| Entire | ingest Checkpoints attached to commits as a Tier C source (`session_id`, `turn_id`, `token_usage`, `skill_events`) | git provenance | failure detection, replay, attribution, regression |
| Galileo Agent Control (Splunk) | enforcement point: `deny`/`steer`/`observe` | guardrail runtime | detection-to-policy loop with evidence |
| Datadog | export incidents and scores; map 7 span kinds; cite Insights as detector prior art | APM, Insights, Patterns | harness component model, replay, regression, cross-vendor fleets |
| OpenLIT | map `coding_agent.*` (68 constants) in the normalizer; propose convergence | instrumentation breadth | intelligence, replay, regression; schema has no fidelity disclosure |
| Traceloop OpenLLMetry | map `traceloop.*` (workflow, task, agent, tool) | instrumentors | control events |
| Honeycomb, Grafana, Dynatrace | export; rely on `gen_ai.*` subset they read | APM, Agent Timeline | harness semantics, replay, regression |

## 3. Schema union
Research 07 §16 provides the per-concept union of vendor attribute names (trace/span, kind, session, turn, agent, subagent, tool, MCP, skills, model, messages, reasoning, usage, cost, context/compaction, memory, …). It is the input to the normalizer's mapping table (SPEC-01 §2, SPEC-06) and will be converted to `docs/specs/mapping/vendor-attributes.csv` in Phase 1.

## 4. Capabilities still unshipped by anyone (as of 2026-10-04, after corrections)
1. Deterministic replay of tools and environment with S1 verified matching and branching from any recorded step, across vendors and frameworks.
2. A computed success-vs-failure first-divergence primitive with upstream input comparison (we have a v0; see Proof F).
3. A cross-harness control-event model with fidelity disclosure (OpenLIT is closest, Claude-Code-only in practice, no fidelity).
4. Regression gating of harness changes against recorded production incidents in CI.
5. Closed loop from evidence to enforcement policy exported to existing gateways.
6. Harness Reliability Score and recommendations with replay-measured deltas.

## 5. Competitive response policy applied (HRCP-02 §77)
Laminar's cache replay and LangSmith's fix validation are structurally incomplete for our target (no tool or environment determinism, no branching, single vendor each), not commoditized, and we should not integrate them; our architecture still adds the unique parts. Proceed.
