# PLAN-13 — Specification Program and Documentation Governance

Replaces HRCP-02 §78 to §89 (archived). Defines the specifications the streams build to, their order, owners, required contents and acceptance.

## 1. Order and timing (Phase 0, months 0 to 3; v0.1 of each)

| Spec | Title | Owner stream | Depends on | Required contents | Acceptance |
|---|---|---|---|---|---|
| SPEC-01 | Telemetry and Execution Graph | Capture & Standards with Execution Graph | PLAN-11, PLAN-12 | Every v0.1 event, every field, required vs optional, identity and versioning contracts, evidence and payload refs, `gen_ai.*` proposal form and `harness.*` form for each event, OTel and OpenInference mappings, graph node and edge schema with provenance, fidelity level computation, examples per capture tier, extensibility for unknown events | Proofs A and B pass; conformance suite exists; coverage matrix per emitter published |
| SPEC-05 | Security, Privacy and Deployment | Security & Privacy | PLAN-12 §20 | Threat model, tenant isolation, encryption and keys, secret handling and redaction, retention classes, customer-side payload and runner, private and hybrid deployment, replay security, control-plane authorization, audit log, data-rights tagging, training-permission separation | Reviewed by external security counsel; enforced in normalizer and SDK from v0.1 |
| SPEC-07 | Benchmark and Evaluation | Benchmark & Corpus | SPEC-01 | Fault-injection harness, case structure, fault library, domains, metrics, external baselines (LongRCA, MAST, TRAIL, AgentErrorBench), rules against LLM-only grading, corpus schema with data rights, publication cadence | v0.1 benchmark runs on Proofs D to G |
| SPEC-06 | Integration Framework | Capture & Standards | SPEC-01 | Adapter contracts for Tier A, B, C; hook adapter for the shared CLI contract; verification and version adapters; plugin classes; coverage matrix format; adapter maintenance policy | Three Tier B adapters and six Tier A instrumentors conform |
| SPEC-02 | Replay, Simulation and Regression | Replay & Sandbox with Regression & CI | SPEC-01, SPEC-05 | What is captured (manifest), side channel format, what is deterministic, external service representation, fidelity levels R1 to R5 and their measurement, branch replay, side-effect classification, sandbox isolation requirements, customer-side runner, incident-to-case conversion, regression report format, CI check format, Pareto reporting | Proof G passes at R2; runner design reviewed against SPEC-05 |
| SPEC-03 | Reliability Intelligence | Reliability Intelligence | SPEC-01, SPEC-07 | Adopted failure taxonomy with mappings, detector contract and D1 to D10 definitions, incident clustering, release correlation, cohort comparison, trajectory alignment, first-divergence algorithm family and evaluation, root-component attribution output and confidence bands, specialized-model admission rule, human review workflow | Proofs D, E, F pass thresholds in PLAN-04 Phase 0 gate |
| SPEC-08 | Open Source and Governance | Capture & Standards with DevRel | PLAN-06 | Repositories, license, commercial boundary, RFC process, release model, conformance program, upstream strategy and proposal list, community program, trademark policy | Public repo layout approved; first OTel proposals drafted |
| SPEC-04 | Runtime Control | Runtime Control | SPEC-03, SPEC-05 | Policy language, intervention catalogue and risk levels, approval workflow, fail-open/fail-closed/degrade-to-human, rollback, control audit, latency requirements, readiness gate metrics, integration with gateways and security products | Design-only in Phase 0; implementation spec at Phase 2 |

## 2. Specification document standard

Every spec contains: version, status (per PLAN-11 §1), owner, dependencies, decision log, open questions, change history. Specs are versioned; breaking changes are rare and recorded as decision changes.

## 3. Architecture Decision Records

Any significant technical choice receives an ADR: context, options, decision, reasons, consequences, rollback. Numbered ADR-001 onward (initial list in PLAN-05 §3). Architect of record: Data Plane lead. ADRs sit above PLAN-12 in the hierarchy (PLAN-11 §7) and are appended to PLAN-12 §26 when they settle an OPEN item.

## 4. Repository layout for specs and plan
```
docs/
  plan/        PLAN-00 to PLAN-13   source of truth
  specs/       SPEC-01 to SPEC-08   written in Phase 0
  adrs/        ADR-001 onward
  archive/     HRCP-00/01/02 and research (provenance, read-only)
```

## 5. Review cadence
- Weekly spec review in Phase 0; each spec has a named reviewer from a different stream.
- Monthly gate review (PLAN-10 §7) takes decisions that change PLAN-11 or PLAN-12.
- Quarterly: plan documents re-read against the market; the archive gains a dated research update rather than edits to old files.
