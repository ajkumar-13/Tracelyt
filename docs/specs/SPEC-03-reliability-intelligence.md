# SPEC-03 — Reliability Intelligence, v0.1

**Version:** 0.1.0 · **Status:** PROPOSED · **Owner:** Reliability Intelligence · **Depends on:** SPEC-01, SPEC-07, research 05 · **Reference implementation:** `src/harness_engine/detectors/deterministic.py`, `src/harness_engine/divergence/first_divergence.py` · **Validated against:** Proofs D, E, F (`docs/phase0/proofs/results.md`)

## 1. Scope
Failure taxonomy (adopted, not invented), the detector contract, deterministic detectors D1 to D10, incident clustering inputs, cohort comparison and first divergence, root-component attribution output, confidence bands, and the admission rule for specialized models. Everything inferred carries confidence and evidence; nothing inferred is presented as observed (PLAN-11 P3 to P5).

## 2. Failure taxonomy (D-035)

**Primary:** the Model-or-Harness interaction-centric taxonomy (arXiv 2607.28802): 41 failure modes, each assigned to an **edge** between two components and a **fault side** (model, harness, environment, grader). Judges reach κ 0.76 against human labels.
**Mappings maintained:** MAST (14 modes, trace-level), TRAIL (3-way tree), AgentErrorTaxonomy/TrajErrBench (17 modes by module), AgentRx, Who&When and LongRCA responsible-role labels, Failure-as-a-Process (CLI coding agents), compaction benchmarks (Governance Decay ConstraintRot, Lost in Compaction COMPINT, Omission Constraints Decay).

**Our component dimension** is the endpoint set from SPEC-01 §6 plus two additions recommended by research 05 §13: **grader** (where instruction–grader mismatch and benchmark defects belong) and **third_party** (an actor, distinct from the external-environment channel). Every label we store carries three fields: `component` (ours), `edge` (Model-or-Harness, e.g. `CONTEXT—MODEL`) and `fault_side`. The full crosswalk table is in research 05 §13(i) and is reproduced into `docs/specs/taxonomy/crosswalk.csv` in Phase 1. Known gaps in all published taxonomies that our telemetry can fill: **hook** failures (no dedicated edge anywhere) and **artifact** failures (stubbed or fabricated outputs).

## 3. Detector contract (ADR-009)

Every detector publishes: `detector_id`, `version`, `scope` (run, fleet, streaming), `definition`, positive examples, negative examples, measured `precision` and `recall` on the benchmark (SPEC-07) and on partner data, `known_blind_spots`, `cost`, `latency`. A Finding carries `detector_id`, `version`, `run_id`, `severity`, `confidence`, `component`, `affected_event_ids`, `evidence`, `summary`. A detector may not ship below precision 0.9 on controls (PLAN-10). Detectors emit `caused_by` edges with `source=detector` only via a separate step; the finding itself is evidence, not an edge.

## 4. Deterministic detectors v0.1 (run scope)

| ID | Name | Definition | Positive example | Negative example | Phase 0 result |
|---|---|---|---|---|---|
| D1 | Doom loop | ≥3 byte-identical tool requests (same `input_hash`) with no successful result that changed an artifact, and ≥2 failures | 8 identical failing shell commands | 3 identical read-only `ls` calls that succeed | fires on loop run; 0 FP on 15 controls/faults |
| D2 | Tool thrashing | ≥4 consecutive tool requests cycling among ≥3 distinct tools with no artifact or verification progress | explore/read/grep cycling | normal read-then-edit sequences | not implemented in v0.1 |
| D3 | Retry storm | ≥3 consecutive failures of the same tool | 8 consecutive Bash failures | one failure then success | fires on loop run |
| D4 | No progress | ≥4 consecutive iterations with tool activity, at least one failure, and no artifact effect or verification pass | loop run iterations 1–8 | F2 runs (recovered within 2 iterations) | fires on loop run |
| D5 | Budget spiral | cost accrues across the last 4 iterations while tool outcomes are ≥3 failures and 0 successes | loop run | success runs | fires on loop run |
| D6 | Verification bypass (policy) | run ends with an agent-declared stop and no `verify.passed`; severity high when a verification was attempted and blocked or failed | F1 cohort (pytest denied, completion declared) | S cohort | 5/5 on F1, 0/5 on S |
| D7 | Permission storm | ≥2 distinct denials (by `tool_call_id`) for the same resource | F1-3/4/5 | F1-1/2 (single denial) | 3/5 on F1 as expected |
| D8 | Context explosion | main-agent context (input + cache read + cache write tokens) grows ≥1.5× over 3 model calls with no artifact or verification progress | long exploratory loops | growth during productive edits | no positives in fixtures |
| D9 | Repeated retrieval | ≥3 reads of the same file hash with no intervening write | reread loops | read-edit-read | no positives in fixtures |
| D10 | Invalid tool arguments | ≥2 tool failures with schema or validation error types | repeated schema errors | runtime errors | no positives in fixtures |

Dedupe rule (Proof finding 3): the same denial arrives from two channels; detectors key on `tool_call_id`.

D6 is deliberately a **policy** detector: it says the run ended unverified, not that the agent lied. A **claim detector** (completion asserted in the final message without evidence) is a separate v0.2 item that needs a claim classifier and is evaluated against Failure-as-a-Process's "fabricates success in 26% of failed runs" finding.

## 5. Streaming and fleet detectors (Phase 2)
Failure-rate shift, cost shift, latency shift, tool-distribution shift, by harness version and model; change-point detection against release correlation (PLAN-12 §13).

## 6. Incident clustering inputs (Phase 2)
Signature = (failure class, first-divergence token, responsible component, tool, harness version, error type hash, embedding of the abstracted trajectory). Quality metrics per SPEC-07 §6: ARI, AMI, V-measure, B-cubed F1, purity, silhouette, coverage.

## 7. Cohort comparison and first divergence (v0, validated in Proof F)

**Trajectory abstraction:** tokens of (event type, tool or verifier name, outcome). Content never enters a token; the instruction-file content hash does, because a differing instruction file is an observed input difference.
**Alignment:** pairwise longest-common-subsequence between each failed and each successful run; the first non-matching token in the failed run is its divergence.
**Aggregation:** candidates ranked by the fraction of (failed, success) pairs that diverge there; median position reported.
**Upstream check (attribution step):** observed inputs are compared between cohorts: instruction content hashes keyed by source name, tool-definition hashes, model, harness config hash. If one differs between every failed and every successful run, its component is the **primary hypothesis** and the divergent event's component is the **mechanism**. Otherwise the divergent event's component is the hypothesis.
**Output:** ranked candidates with agreement, example event ids, upstream differences, primary and mechanism components, an explanation sentence that uses "hypothesis" and "agreement", never "cause".

Phase 0 results: S vs F1 → `permission.denied:Bash`, agreement 1.0, primary permission (correct); S vs F2 → instruction content hash differs, primary context_builder, mechanism visible as exploratory shell calls (correct); leave-one-out single-run top-3 localization 10/10. Caveat: single-fault, five-run cohorts, one task class. Realistic expectation on real data is bounded by LongRCA (24% exact root step) until the corpus grows.

**Phase 1 to 2 research agenda:** semantic stage alignment (not token LCS), state-hash alignment, Oat-style success-dynamics anomaly scoring, Continual Search style iterative evidence gathering for long traces, evaluation on LongRCA-Mini and TrajErrBench.

## 8. Root-component attribution output contract
`primary_component`, `primary_confidence`, `mechanism_component`, `first_divergence {token, position, agreement, event_id}`, `upstream_differences[]`, `alternatives[]` (never dropped when ambiguous), `evidence_event_ids[]`, `edge`, `fault_side`, `explanation`. Confidence bands shown in product: Observed (1.0, runtime edge), High (≥0.8 agreement with an observed input difference), Medium (0.5–0.8), Weak (<0.5), Unknown.

## 9. Specialized model admission (D-041)
A model ships only when it beats the rules-and-statistics baseline on SPEC-07 by a published margin on held-out partner data, with its cost and latency. Candidates in order: failure-type classifier, first-divergence ranker, root-component classifier, incident similarity encoder, context-loss detector, tool-misuse detector, verification-weakness detector, regression-risk estimator.

## 10. Human review
Every incident exposes the evidence package; analysts can accept, reject or relabel the hypothesis; relabels become `human_analyst` edges and corpus labels with data rights.

## 11. Open questions
1. Alignment method for heterogeneous task classes (semantic stage alignment vs state hashing).
2. Whether D6 should split into policy-level and claim-level detectors in v0.2.
3. Token design for tool calls: binary-level abstraction loses the F2 mechanism detail (wrong path) while protecting content; evaluate hashed-argument buckets.
