# SPEC-07 — Benchmark and Evaluation (Harness Reliability Benchmark), v0.1

**Version:** 0.1.0 · **Status:** APPROVED v0.1 (founder approval 2026-10-05; Phase 1 baseline) · **Owner:** Benchmark & Corpus (independent of the teams it grades, D-042) · **Depends on:** SPEC-01, SPEC-03, research 05 · **Reference implementation:** `scripts/run_proofs.py`, `tests/test_proof_gates.py`, fixtures in `tests/fixtures/claude_code/`

## 1. Purpose
Test our own claims with ground truth. Detection, localization, first divergence, root-component attribution, reproduction, fix validation and regression detection are each measured against injected or human-labelled truth. Never evaluate a diagnosis only by asking a model whether it sounds right (HRCP-02 §57).

## 2. Case structure
`task`, `environment` (container image, repo state, tool allowlist, instruction files), `baseline_harness`, `mutated_harness`, `injected_fault`, `expected_symptom`, `true_first_divergence` (event type and position, or input difference), `true_responsible_component` (plus edge and fault side), `expected_evidence`, `success_criteria`, `data_rights`.

## 3. Fault library (v0.1 implemented ⇢ Phase 1 targets)
Implemented in Phase 0 on Claude Code: **permission fault** (tool removed from allowlist so the verifier is denied headlessly; expected component permission), **context fault** (instruction file points at a non-existent test path; expected context_builder), **retry storm** (instructed identical failing command; expected loop). Phase 1: remove a context field; change a tool schema; modify the prompt; change retry threshold; modify memory; change model; modify verification policy; change budget; change stop condition; subagent context loss; memory poisoning; compaction policy change; MCP server version change.

## 4. Domains
v0.1: coding agents in containers (Claude Code headless; Codex and Gemini CLI next) and API-workflow agents with mocked services (Phase 1). Later: browser, research, computer-use.

## 5. External baselines and conversion
Report every method on public sets alongside ours: **LongRCA-Mini** (200) and LongRCA (1,140; `history[i]` 0-based; labels role and root step), **Who&When** (184), **TrajErrBench** (486, plus converted AgentErrorBench and Who&When), **AgentRx**, **SearchAuditBench**, **TRAIL** (148, OpenInference span trees), **MAST-Data** (1,642, trace-level only). Common record format and conversion rules per research 05 §13(ii): 0-based unified steps with a `native_step` field; MAST kept as trace-level labels. Published numbers to beat: LongRCA best baseline 13.2% exact root step, RCTA 24.1%; TRAIL best ~11% joint accuracy; Model-or-Harness judges κ 0.76.

## 6. Metrics (adopted definitions, research 05 §13(iii))
**Detection:** precision, recall, F1; AUROC and AUPRC for scored detectors; **recall at fixed false-positive rate** on successful runs (1%, 2%, 5%); early detection: lead time, detect-before-irrecoverable rate with window 1 step; step-level AUROC and top-k hit rate (k=3).
**Localization:** exact; ±k accuracy (k ∈ 3, 5); tolerance-span accuracy; MAE with coverage; normalized distance; signed bias; directional window. Report micro and macro over sources.
**Responsible role:** accuracy with LongRCA `normalize_role`; the role must be predicted explicitly, not derived from the step.
**Component, edge, fault side:** accuracy, macro-F1, Cohen's κ; mode accuracy conditioned on gold category.
**Category:** macro-F1 (single-label), weighted F1 (multi-label), location–category joint accuracy plus a precision-aware joint F1, joint "All" accuracy.
**Clustering:** ARI, AMI, V-measure, B-cubed P/R/F1, purity, silhouette, coverage.
**Replay (SPEC-02):** reproduction rate at each fidelity level; event, state, artifact and outcome fidelity.
**Regression:** injected-regression catch rate; false regression rate on no-op changes.
**Cost and latency:** analysis cost per run and per incident; time to useful diagnosis.

## 7. Phase 0 measurements (recorded)
Detectors: 0/5 false-positive runs on the control cohort; loop run fires D1, D3, D4, D5; F1 cohort D6 5/5, D7 3/5 (as expected by construction). First divergence: cohort-level top-1 correct for both faults with agreement 1.0; single-run top-3 localization 10/10. Normalization: 3.5% of native records outside v0.1 excluding deferred domains. Graph fidelity G3 (proofA) and G4 (runs with verification). Replay: not measured.

## 8. Rules
Controlled faults are necessary and insufficient; no robustness claim without real production failures carrying data rights. The benchmark team publishes quarterly and grades every detector, divergence, replay and model claim independently.

## 9. Open questions
1. How to inject faults into Tier A frameworks uniformly (instrumentor-level fault injection hooks).
2. Whether to publish our cohorts (they are small, synthetic, and contain scrubbed vendor telemetry) or only the generator.
