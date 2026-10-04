# PLAN-14 — Phase 0 Amendments to the Plan (decision changes with evidence)

**Date:** 4 October 2026 · Recorded per PLAN-11 §6 (old, new, reason, evidence, affected, migration).

| # | Old | New | Reason and evidence | Affected | Migration |
|---|---|---|---|---|---|
| A-1 | PLAN-01 §4: "none of 17 platforms ship replay" | Laminar ships cache-based LLM replay (hash excludes system prompt, latches live on miss, tools live); LangSmith Engine ships input replay for fix validation. Differentiator 1 restated as deterministic replay of tools and environment with verified matching and branching from any recorded step, across vendors. | research 07 §0.1 | PLAN-01, PLAN-08 slide 7, SPEC-02 | wording only |
| A-2 | PLAN-01 §4: OpenLIT "branding without a schema" | OpenLIT has 68 `coding_agent.*` constants and an adapter contract. | research 07 §0.3 | PLAN-01, SPEC-01 mapping | add mapping; propose convergence |
| A-3 | PLAN-01: Galileo Agent Control OSS unverified | Apache-2.0 at `agentcontrol/agent-control`; actions `deny`, `steer`, `observe`. | research 07 §0.2 | SPEC-04 §4 | integrate as enforcement point |
| A-4 | PLAN-05 C-7 Proof G in Phase 0 | Proof G executed in Phase 1 week 1 per SPEC-02 §11; Phase 0 produced the R2 cassette and the spec. | Proof results | PLAN-04 Phase 0 gate | gate criterion carried |
| A-5 | PLAN-06 §6 company holds the spec name as a trademark until foundation transfer | Company holds only the product mark; the spec name is descriptive and not protectable. | research 08 §4 | PLAN-06, SPEC-08 §5 | wording |
| A-6 | PLAN-12 §8 event model: compaction attrs | Add `preserved_*` ids, `num_preserved_messages`, `custom_instructions_present`, `summary` payload ref (PostCompact exposes the full summary); provenance gets `source_name_hash`. | Proof A, Proof F | SPEC-01 §5.5 | implemented |
| A-7 | PLAN-12 §7 iteration = each model call | Iteration opens at each model response; unresolved tool requests carry into the next iteration because hooks fire before the OTel record is flushed. | Proof D finding | SPEC-01 §4.2 | implemented |
| A-8 | PLAN-11 D-035 taxonomy components | Add `grader` and `third_party`; every label carries Model-or-Harness edge and fault side. | research 05 §13 | SPEC-03 §2 | implemented in spec |
| A-9 | PLAN-04 Phase 0 discovery: 50 interviews | Kit complete (guide, synthesis template, outreach, 75 named targets, top 20); interviews are founder-run and not started. Gate A interview counters remain open. | this phase | Phase 0 gate | founder action |
| A-10 | PLAN-03 adapter maintenance "two engineers" | Confirmed necessary: Claude Code 2.1.289 differs from the docs in several places (no beta spans exported; `/compact` spawns a subagent; two channels report one denial; two compaction token figures). | Proof A, D | PLAN-03 | none |

Items D-043 (name), D-045 (stores), D-046 (Laminar) remain OPEN with recommendations in `docs/phase0/company/00-decisions.md` and `docs/adrs/`.
