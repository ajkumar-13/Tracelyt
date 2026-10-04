# Phase 0 field-level research (4 October 2026)

Nine parallel research tracks, run against primary sources (cloned repositories, published packages, official docs) with every claim tagged by verification level. These replace the October 3 survey in `docs/archive/research/` wherever they disagree; each file opens with its corrections to that archive.

| File | Track | Feeds |
|---|---|---|
| 01-otel-genai-openinference-registry.md | All 79 `gen_ai.*` attributes, span/event/metric definitions, MCP conventions, open agentic issues, OpenInference constants, mapping table | SPEC-01, SPEC-06, SPEC-08 |
| 02-claude-code-surfaces.md | Every hook event's input and output fields, every OTel metric/event/span, Agent SDK message union, transcript format, permissions, compaction, checkpoints, 2026 changelog | SPEC-01, SPEC-06, Proof A |
| 03-codex-gemini-cursor-surfaces.md | Codex hooks (12 events, JSON schemas), Codex OTel and rollout files, app-server protocol, Gemini CLI telemetry and hooks, Cursor hooks; coverage table | SPEC-06 |
| 04-framework-surfaces.md | LangGraph, LangChain v1, Deep Agents, OpenAI Agents SDK, ADK, PydanticAI, Claude Agent SDK, OpenHands, CrewAI, Mastra, AutoGen/AG2, Vercel AI SDK: telemetry, callbacks, state, checkpoints; coverage matrix | SPEC-01, SPEC-06 |
| 05-failure-taxonomies-benchmarks.md | Model-or-Harness 41 modes, MAST 14, LongRCA, MegaRCA, TRAIL, AgentErrorTaxonomy, Who&When, Oat, TrajDebug, Failure-as-a-Process, compaction benchmarks, OpenHands stuck detector; unified mapping and metric definitions | SPEC-03, SPEC-07 |
| 06-replay-sandbox-prior-art.md | Record/replay libraries, durable execution journals, sandbox snapshot APIs, environment reproducibility, academic replay, MCP tool annotations, CI prior art; proposed replayable-step record | SPEC-02 |
| 07-competitor-data-models.md | Schemas and mechanisms of LangSmith, Langfuse, Phoenix, Laminar, Raindrop, Judgeval, Weave, AgentOps, Entire, Galileo Agent Control, Datadog, OpenLIT, OpenLLMetry; HRCP teardown rows; schema union | Teardown, SPEC-01 |
| 08-naming.md | 40 candidates, 12-name collision table, top 3, spec and CLI names | Company decisions |
| 09-interview-targets.md | 75 organizations across three tracks with evidence, pain signals, channels, top 20 | Discovery |

Research artifacts captured in this repository rather than described: `tests/fixtures/claude_code/` holds real hook, OTel, SDK-stream, raw-body and transcript captures from Claude Code 2.1.289 (Proofs A, D, E).
