# ADR-004 — Content-addressed payload references
**Status:** accepted · **Date:** 2026-10-04
## Decision
`PayloadRef {sha256, size_bytes, media_type, uri?, redaction}`. Events carry refs, never content. Bytes live in the customer's object store (or local disk for the recorder) by default; `uri` is optional and customer-side. Identical content is stored once. Redaction state is part of the ref.
## Reasons
Economics for long-running agents (PLAN-09 T6), privacy by default (P15, P16), replay cassettes need exact bytes (SPEC-02).
## Consequences
Every detector and divergence method must work on hashes and structure; content-dependent analysis runs customer-side or on opted-in payloads.
