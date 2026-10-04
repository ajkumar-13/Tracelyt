# ADR-002 — Two external naming forms for every event
**Status:** accepted · **Date:** 2026-10-04
## Context
OTel has no conventions for compaction, permission, verification, agent-level stop or provenance; proposals exist (PR #535, #445, #483, issue #181). Adoption comes through implementers; a private schema name will not be adopted (PLAN-06).
## Decision
Each event carries a `gen_ai.*` **proposal form** (reusing an existing or proposed OTel name where one exists) and a `harness.*` **registry form** we govern. Mapping table owned by Capture & Standards; the normalizer accepts both plus OpenInference and native adapter formats.
## Consequences
Upstream acceptance never blocks the product; internal names (HEM, HEG) are never external.
## Rollback
Collapse to one form if the registry is adopted upstream wholesale.
