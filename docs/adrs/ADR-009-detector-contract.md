# ADR-009 — Detector contract and versioning
**Status:** accepted · **Date:** 2026-10-04
## Decision
Every detector publishes id, version, scope, definition, positive and negative examples, measured precision and recall per benchmark version and per partner fleet, blind spots, cost, latency. Findings carry evidence event ids and a component. Precision below 0.9 on controls blocks shipping. Detector output never becomes a graph edge without passing through the attribution step with `source=detector` and a confidence. Two channels reporting one fact are deduped on the shared identifier (Proof D finding).
