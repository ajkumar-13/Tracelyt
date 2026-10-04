# Company Plan — Index

**Date:** 3 October 2026
**Status:** **Source of truth.** The documents in this directory are what the company is built from. HRCP-00/01/02 and the research reports are archived in `docs/archive/` as provenance and are read-only.
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
| PLAN-11 | Principles, Decision Register and Governance | The constitution: principles, decisions D-001 to D-047, change management, source-of-truth hierarchy. Replaces HRCP-00 |
| PLAN-12 | Technical Architecture Baseline | Self-contained architecture with the PLAN-05 deltas applied. Replaces HRCP-01 |
| PLAN-14 | Phase 0 Amendments | Decision changes with evidence recorded after Phase 0 |
| PLAN-13 | Specification Program | SPEC-01 to SPEC-08: order, owners, required contents, acceptance; ADR and documentation governance |

## Reading order

New team members: PLAN-11 (principles and decisions) → PLAN-01 (thesis) → PLAN-02 (vision) → PLAN-12 (architecture) → PLAN-04 (roadmap) → the stream-specific documents.

## Relationship to the archive

HRCP-00/01/02 (30 September 2026) were the founding documents. On 3 October 2026 the founders decided that `docs/plan/` is the source of truth. PLAN-11 absorbs HRCP-00's principles and decision register with the changes recorded in PLAN-05; PLAN-12 absorbs HRCP-01 with those changes applied; PLAN-04 and PLAN-13 absorb HRCP-02. Section citations such as "HRCP-00 §14" in these documents point to `docs/archive/hrcp/` and remain valid as provenance. Factual claims cite `docs/archive/research/`.

## Vocabulary used in this plan set

- **Harness**: everything around the model in an agent system: loop, planner, context builder, compactor, memory, retrieval, tools, MCP, permissions, hooks, sandbox, state, subagents, verification, budget, stop logic.
- **Open harness**: a harness the customer builds or controls (LangGraph, OpenAI Agents SDK, Google ADK, PydanticAI, Claude Agent SDK, OpenHands, custom). They can emit any event we define.
- **Closed harness**: a vendor product the customer runs but cannot modify (Claude Code, Codex, Cursor, Devin, Copilot coding agent). We capture what hooks, OTel export and APIs expose.
- **Capture tier**: A (native instrumentation, full fidelity), B (hook and OTel adapters, high fidelity with known gaps), C (API and log adapters, skeleton).
- **Fidelity level**: a per-run disclosure of how complete the reconstruction is, for both the graph and replay.
- **Harness Engine**: the whole closed loop: capture → normalize → graph → detect → incident → diverge → attribute → replay → regress → recommend → control → measure.

## Working name

"Tracelyt" is a placeholder and collides with existing products (see research assessment §3.8). A naming decision is a Phase 0 deliverable.

## Phase 0 outputs

Phase 0 ran on 4 October 2026. Start at `docs/phase0/99-gate-report.md`. Specifications are in `docs/specs/`, ADRs in `docs/adrs/`, the reference implementation in `src/harness_engine/` with real Claude Code captures under `tests/fixtures/`.
