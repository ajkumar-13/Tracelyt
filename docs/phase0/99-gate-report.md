# Phase 0 Gate Report (4 October 2026)

**Gates assessed:** Gate A (Semantic Viability), Gate B partial (Developer Utility), per PLAN-04 Phase 0 exit criteria. **Overall:** engineering and specification criteria met or met-with-caveat; customer-evidence criteria open pending founder-run interviews; Proof G carried to Phase 1 week 1.

## 1. Criteria

| Criterion | Target | Result | Status |
|---|---|---|---|
| Proof B: normalize Claude Code and one open harness into v0.1 | < 10% framework-specific exceptions | Claude Code: **3.5%** excluding the HOOK/configuration domains deferred to v0.2 (55.7% including them, inflated by our own 22 registered hooks). Second harness: specified (SPEC-06 §5.2), not captured. | **Half met** |
| Proof D: injected doom loop and verification bypass detected, zero false positives on controls | 0 FP | Loop run: D1, D3, D4, D5 fire. F1 cohort: D6 5/5, D7 3/5 (as constructed). Controls S-1..S-5, proofD control and bypass: **0/7 false positives**. | **Met** |
| Proof F: injected first divergence in top-3 | ≥ 70% | Single-run leave-one-out: **10/10**; cohort-level top-1 correct for both faults (permission; context_builder via observed instruction-hash difference). | **Met** (controlled, single-fault, one task class) |
| Proof G: replay | R2 on 80%, R3 on 50% | Not executed. R2 cassette (11 request/response pairs) captured; S1 matching, fidelity measurement and runner specified (SPEC-02). | **Open → Phase 1 week 1** |
| Proof A: capture a complex coding-agent execution | qualitative | Met at G3; three channels plus side channel; nine findings that changed the specs. | **Met** |
| Proof C: visualize context changes and verification gates | qualitative | Graph with provenance-typed edges and fidelity (G3/G4) built and tested; no UI yet. | **Met at data level** |
| Interviews | ≥ 15/50 pain, ≥ 10/50 host replay | Kit complete; 75 targets with evidence; **0 conducted** (founder action). | **Open** |
| SPEC-01 to SPEC-08 at v0.1 | all | All eight written with decision logs and open questions; SPEC-01 has generated JSON Schema. | **Met** |
| ADRs for storage, stream, identity, naming, fidelity, payload refs | drafted | ADR-001 to ADR-012 (005, 006, 007 provisional pending benchmarks with plans written). | **Met** |
| Threat model v0.1 | written | SPEC-05 with 13 threats, controls, owners; PII finding enforced in code. | **Met** |
| Name, license, OTel proposals | decided / drafted | Name recommended (Kernmantle; spec `harness-semconv`; CLI `qar`) pending counsel and founder; license decided (Apache 2.0); seven upstream proposals sequenced. | **Recommendation ready** |

## 2. Kill triggers (PLAN-09 §6, Gate A/B)
Proof F under 40%: **no** (100%). Proof B over 25% exceptions: **no** (3.5%). Fewer than 8 of 50 interviews show pain: **not yet measurable**. Fewer than 5 of 50 will host replay: **not yet measurable**. No trigger fires on the evidence available.

## 3. What Phase 0 established that we did not know on 3 October
1. Claude Code exposes the full compaction summary and preserved-segment ids through supported interfaces; context lineage on a closed harness is feasible at G3 without the unstable transcript.
2. Vendor OTel carries personal identifiers by default; our adapters must strip them, and did.
3. Hook records can precede the flushed OTel record of the model response that caused them; iteration logic must tolerate this.
4. `/compact` is itself a subagent in 2.1.289.
5. The published taxonomies have no edge for hook failures and no artifact category; our telemetry fills both.
6. Replay is less unshipped than the archive claimed (Laminar cache replay, LangSmith input replay) and more narrowly defined now: tools, environment, verified matching, branching.
7. OTel already has the right places to put our control events (PR #535, issue #181, PR #445) and a maintainer waiting for prototypes; the upstream path is concrete.
8. The naming space for harness and evidence words is crowded by small 2026 projects; Kernmantle is the cleanest candidate found.

## 4. Founder actions to close Gate A
1. Approve or redirect the name; order registrar and counsel checks.
2. Begin the 50 interviews from the kit; file counters weekly.
3. Approve SPEC v0.1s for stream build-out at the first gate review.
4. Decide the Laminar posture (recommendation: compete; acqui-merge as the only partnership form).

## 5. Phase 1 week-1 engineering backlog (from this report)
Proof G at R2 and R3 on the proofA cassette; second-harness capture (OpenAI Agents SDK) for Proof B; OTLP receiver hardening and the shared hook adapter binary; workspace snapshotter and egress proxy for shell `fs_delta` and `network[]`; benchmark executions per `docs/phase0/benchmarks/`; first OTel proposal PR with Proof A evidence.

## 6. Repository map produced by Phase 0
`docs/phase0/00-charter.md` · `docs/phase0/research/` (9 reports + index) · `docs/phase0/discovery/` (guide, synthesis template, outreach) · `docs/phase0/proofs/` (Proof A findings, results, results.json) · `docs/phase0/teardown/` · `docs/phase0/company/` · `docs/phase0/benchmarks/` · `docs/specs/SPEC-01..08` + `schema/` · `docs/adrs/ADR-001..012` · `docs/plan/14-phase0-amendments.md` · `src/harness_engine/` (model, adapters, normalize, graph, detectors, divergence) · `tests/` (adapter tests, gate tests, fixtures) · `scripts/run_proofs.py`.
