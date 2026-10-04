# ADR-003 — Fidelity levels computed per run and always displayed
**Status:** accepted · **Date:** 2026-10-04
## Context
Capture completeness differs by harness and channel. Claiming uniform reconstruction would be false (PLAN-11 P10).
## Decision
Graph fidelity G1 to G5 (SPEC-01 §10) computed by `graph/builder.py`; replay fidelity R1 to R5 (SPEC-02 §5) computed by the runner. Every run, incident, replay and regression report displays its level and the reasons. Marketing never claims a level a fleet does not reach.
## Consequences
UI and API carry fidelity everywhere; the benchmark reports results per level.
