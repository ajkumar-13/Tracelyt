# ADR-005 — Analytical store and retention tiers
**Status:** proposed (benchmark required) · **Date:** 2026-10-04
## Context
Candidates: ClickHouse (Langfuse, Laminar, AGNTCY reference stack converged on it; Brainstore is Braintrust's custom columnar store), Apache Druid, DuckDB/MotherDuck for the local recorder, Postgres-only for the alpha.
## Decision (provisional)
ClickHouse for the managed service, DuckDB for the local recorder, Postgres for metadata. Freeze only after the Phase 0/1 benchmark in `docs/phase0/benchmarks/analytical-store.md` passes: billions of synthetic events, high-cardinality attributes, time-window and cohort queries, trajectory reconstruction, adjacency-table graph queries, retention tiers.
## Rollback
Schema is store-agnostic (events as rows, adjacency tables); migration is an export.
