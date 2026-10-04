# Phase 0 — Charter and Tracker

**Phase:** 0, Foundation (PLAN-04). **Started:** 4 October 2026. **Target exit:** Gate A (Semantic Viability) and partial Gate B (Developer Utility), per PLAN-04 Phase 0 exit criteria.
**Operating rule:** evidence before architecture; every workstream produces an artifact that can be checked, measured or reused by the stream that inherits it.

## 1. Purpose of Phase 0 in one paragraph

Before any stream scales, answer with evidence: what already exists, what is commodity, what the standards already solve, where existing systems are structurally insufficient, and which three capabilities can plausibly create differentiation. Write the specifications the streams will build to. Prove the architecture on real agent executions (Proofs A to G). Start customer contact on day one. Decide the name, license, standards engagement and the Laminar question.

## 2. Workstreams, deliverables, status

| # | Workstream | Deliverable | Location | Status |
|---|---|---|---|---|
| W1 | Customer discovery | Interview guide per track; screening criteria; 75-organization target list with evidence; outreach messages; synthesis template; **50 interviews** (founder-run) | `docs/phase0/discovery/` | Kit complete (guide, template, outreach, 75 targets); interviews not started (founder) |
| W2 | Field-level research | Exact attribute registries (OTel GenAI, OpenInference); closed-harness surfaces (Claude Code, Codex, Gemini CLI, Cursor); framework span and state models; failure taxonomies and benchmarks; replay and sandbox APIs; competitor data models; naming collisions; interview targets | `docs/phase0/research/` | Complete: nine reports in `docs/phase0/research/` |
| W3 | Specifications v0.1 | SPEC-01 Telemetry and Graph; SPEC-05 Security; SPEC-07 Benchmark; SPEC-06 Integration; SPEC-02 Replay and Regression; SPEC-03 Intelligence; SPEC-08 Open Source; SPEC-04 Control (design) | `docs/specs/` | Complete: eight specs v0.1 in `docs/specs/` |
| W4 | Engineering proofs A to G | Reference implementation: event model, adapters, normalizer, graph builder with fidelity, detectors, alignment and first divergence, replay manifest and fixture replay; measurements | `src/`, `tests/`, `docs/phase0/proofs/` | Proofs A, B (half), C, D, E, F complete; G carried to Phase 1 week 1 |
| W5 | Competitive teardown completion | HRCP-02 §5 template per competitor; schema union table | `docs/phase0/teardown/` | Complete: `docs/phase0/teardown/` |
| W6 | Architecture benchmarks and ADRs | ADR-001 to ADR-012 drafted; benchmark plans and workload generator spec for analytical store, stream, sandbox | `docs/adrs/`, `docs/phase0/benchmarks/` | Complete: ADR-001..012 and three benchmark plans |
| W7 | Security | Threat model v0.1 (inside SPEC-05); telemetry-as-untrusted-input rules enforced in the proof normalizer | `docs/specs/SPEC-05`, `src/` | Complete: SPEC-05 threat model; PII stripping enforced in adapters |
| W8 | Company decisions | Name recommendation with collision evidence; license decision; OTel SIG engagement plan with first proposals drafted; Laminar analysis | `docs/phase0/company/` | Complete: `docs/phase0/company/00-decisions.md` |
| W9 | Gate report | Status against Gate A/B criteria; founder actions; open items | `docs/phase0/99-gate-report.md` | Complete: `docs/phase0/99-gate-report.md` |

## 3. Exit criteria (from PLAN-04, restated as checkboxes)

- [x] Proof B (half): Claude Code normalizes at 3.5% exceptions excluding deferred domains; second harness pending.
- [x] Proof D: injected doom loop and verification bypass detected with zero false positives on the control set.
- [x] Proof F: injected first divergence found in the top 3 for at least 70% of controlled cases.
- [ ] Proof G: at least R2 fidelity on 80% of recorded failures, R3 on 50%.
- [ ] Interviews: at least 15 of 50 describe a harness regression they would pay to prevent; at least 10 will host replay in their environment.
- [x] SPEC-01 to SPEC-08 at v0.1 with owners, decision logs and open questions.
- [x] ADRs for storage, stream, identity, naming forms, fidelity, payload refs.
- [x] Threat model v0.1.
- [ ] Name decided and cleared; license decided; first OTel proposals drafted.

Kill or re-plan triggers (PLAN-09 §6): Proof F under 40%; fewer than 8 of 50 interviews show pain; Proof B over 25% exceptions; fewer than 5 of 50 will host replay.

## 4. Division of labour in this phase

**Produced in this repository:** everything in §2 except the interviews themselves and the benchmark executions that require infrastructure (ClickHouse at billions of events, microVM sandboxes). Those are specified here with runnable workload generators so the first infrastructure engineers can execute them in week one.

**Founder actions:** run the 50 interviews from the kit; approve the name; approve the license; decide the Laminar question; approve SPEC v0.1s at the gate review.

## 5. First-principles constraints that shape every Phase 0 artifact

1. **A harness is a system of components with interfaces; failures occur at interfaces.** Every event we define names the component on each side of the interface, so attribution is possible by construction rather than by inference.
2. **Observed, reconstructed and inferred facts have different epistemic status and must be stored differently.** Observed events carry runtime identifiers. Reconstructed edges carry the method and the content hashes that justify them. Inferred edges carry confidence and the detector or model version that produced them.
3. **A record is replayable only if every nondeterministic input is captured.** Model responses, tool outputs, external service responses, time, randomness, environment state. Anything not captured must be declared, which is what fidelity levels are.
4. **Telemetry is untrusted input.** Model and tool outputs may contain adversarial instructions; nothing in the pipeline executes or follows content, and the UI renders it as data.
5. **Payloads stay with their owner.** Structural events travel; content is referenced by hash and stays customer-side unless the customer chooses otherwise.
6. **Schemas earn adoption by being small and correct.** v0.1 is nine domains and roughly twenty events; everything else is extensibility until real traffic argues for promotion.
7. **Nothing is claimed that is not measured.** Every detector ships with precision and recall; every divergence with confidence; every replay with a fidelity level; every recommendation with a replay-measured delta.
