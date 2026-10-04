# Tracelyt (working name) — the reliability engine for the system around the model

Planning repository for a startup building reliability infrastructure for autonomous AI agents and their harnesses.

**Source of truth: `docs/plan/`.** Start at `docs/plan/00-README.md`, then PLAN-11 (principles and decisions), PLAN-01 (thesis), PLAN-02 (end-state vision), PLAN-12 (architecture), PLAN-04 (36-month roadmap with gates).

**Phase 0 (4 October 2026)** is complete except founder-run interviews and Proof G: see `docs/phase0/99-gate-report.md`. Specifications: `docs/specs/`. ADRs: `docs/adrs/`. Reference implementation and real Claude Code fixtures: `src/`, `tests/`. Run `python3 -m pytest -q` to re-check the Phase 0 gate criteria.

`docs/archive/` holds the original HRCP-00/01/02 documents and the October 2026 research reports. They are provenance for the plan and are read-only.

Note: the working name collides with Evidently AI's `tracely` OpenTelemetry library and other products; naming is a Phase 0 decision (PLAN-11 D-043).
