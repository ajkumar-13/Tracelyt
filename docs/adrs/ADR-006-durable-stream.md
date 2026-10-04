# ADR-006 — Durable stream
**Status:** open · **Date:** 2026-10-04
## Context
Normalized events enter a durable stream before downstream processing (PLAN-12 §10). Candidates: Kafka-compatible (Redpanda, Apache Kafka), managed cloud streaming, NATS JetStream, Postgres-backed queue for the alpha.
## Decision
Deferred to the Phase 1 benchmark (`docs/phase0/benchmarks/stream.md`). Alpha uses a Postgres-backed queue behind an interface so the choice does not leak into consumers.
