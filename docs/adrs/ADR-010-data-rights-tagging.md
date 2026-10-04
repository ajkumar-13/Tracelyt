# ADR-010 — Data-rights tagging of corpus items
**Status:** accepted · **Date:** 2026-10-04
## Decision
Every corpus item carries exactly one of `internal_benchmark`, `open_source_permitted`, `customer_isolated`, `training_prohibited`, `training_allowed`, plus `source`, `license` and the customer contract reference. Operational processing and training permissions are separate fields. Queries for cross-customer learning filter on rights at the storage layer, not in application code. Permission is never inferred.
