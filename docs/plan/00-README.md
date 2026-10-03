# Company Plan — Index

**Date:** 3 October 2026
**Status:** Planning baseline, derived from HRCP-00/01/02, the research in `docs/research/`, and founder discussions.
**Operating assumption for this plan set:** a founding team that can hire 100+ engineers and fund them for 24 to 36 months. Where the plan would differ for a small team, it says so.

## Documents

| Doc | Title | Purpose |
|---|---|---|
| PLAN-01 | Thesis and Differentiation | What we are building, why now, how we differ from every competitor class, and what the moat actually is |
| PLAN-02 | End-State Vision: The Harness Engine | What the company becomes if the graph, first divergence and replay hypotheses hold, and why that breaks the category |
| PLAN-03 | Organization and Team | Teams, headcount by phase, hiring sequence, operating model for 100+ engineers |
| PLAN-04 | Phased Roadmap | Five overlapping phases over 36 months, with workstreams, deliverables, gates and headcount |
| PLAN-05 | Architecture Deltas to HRCP-01 | What the research changes in the architecture: tiered capture, fidelity levels, customer-side default, graph storage, replay strategy |
| PLAN-06 | Open Standard Strategy | How the Harness Event Model becomes an adopted convention rather than private vocabulary |
| PLAN-07 | Go-to-Market and Pricing | ICP tiers, design partner program, positioning against each competitor, pricing architecture |
| PLAN-08 | Investor Pitch | Narrative, deck outline, market sizing, competitive FAQ, ask and use of funds |
| PLAN-09 | Risks and Kill Criteria | Every material risk with mitigation, and the evidence that would make us stop or pivot |
| PLAN-10 | Metrics and Benchmark | Company, product and research metrics; the Harness Reliability Benchmark |

## Relationship to the HRCP series

HRCP-00 (constitution) remains the source of truth for principles. This plan set proposes amendments to it, listed in PLAN-05 §1 as explicit decision changes with reasons, per HRCP-02 §81. The future specs HRCP-03 through HRCP-10 should be written from this plan set, in the order given in PLAN-04 Phase 0.

## Vocabulary used in this plan set

- **Harness**: everything around the model in an agent system: loop, planner, context builder, compactor, memory, retrieval, tools, MCP, permissions, hooks, sandbox, state, subagents, verification, budget, stop logic.
- **Open harness**: a harness the customer builds or controls (LangGraph, OpenAI Agents SDK, Google ADK, PydanticAI, Claude Agent SDK, OpenHands, custom). They can emit any event we define.
- **Closed harness**: a vendor product the customer runs but cannot modify (Claude Code, Codex, Cursor, Devin, Copilot coding agent). We capture what hooks, OTel export and APIs expose.
- **Capture tier**: A (native instrumentation, full fidelity), B (hook and OTel adapters, high fidelity with known gaps), C (API and log adapters, skeleton).
- **Fidelity level**: a per-run disclosure of how complete the reconstruction is, for both the graph and replay.
- **Harness Engine**: the whole closed loop: capture → normalize → graph → detect → incident → diverge → attribute → replay → regress → recommend → control → measure.

## Working name

"Tracelyt" is a placeholder and collides with existing products (see research assessment §3.8). A naming decision is a Phase 0 deliverable.
