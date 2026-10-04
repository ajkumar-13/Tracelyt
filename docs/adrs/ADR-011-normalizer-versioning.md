# ADR-011 — Normalizer versioning and re-derivation
**Status:** accepted · **Date:** 2026-10-04
## Decision
Raw captures are immutable. Every normalized event carries `schema_version` and the normalizer version in `native_type` lineage; event ids are deterministic from native identifiers so re-normalization is idempotent. Derived artifacts (graphs, findings, incidents, hypotheses) carry the versions that produced them and are rebuilt from raw evidence when normalization, graph construction or detectors improve (PLAN-11 P18).
