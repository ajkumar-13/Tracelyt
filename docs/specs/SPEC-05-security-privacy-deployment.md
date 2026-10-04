# SPEC-05 — Security, Privacy and Deployment, v0.1

**Version:** 0.1.0 · **Status:** PROPOSED · **Owner:** Security & Privacy · **Depends on:** PLAN-11 P15 to P17, PLAN-12 §16, §20 · **Enforced in:** adapters (PII stripping), SPEC-01 content profile, SPEC-02 runner · **Review:** external security counsel before Phase 1 GA

## 1. First principles
1. **Telemetry is untrusted input.** Model outputs, tool outputs, hook outputs and transcript text may contain adversarial instructions. No component executes, follows or interprets captured content; every UI renders it as data; every automated analysis treats it as text, never as instruction.
2. **Payloads stay with their owner.** Structural events travel; content is referenced by hash and remains in the customer's store unless they opt in to managed payload storage (P15).
3. **Identity of people is not telemetry.** Attributes identifying a person or account are stripped at the adapter unless the customer opts in.
4. **Replay executes hostile content and must be isolated as such.** Default: customer-side runner, network deny-by-default, credential stripping, resource and time limits, output sanitization, audit.
5. **Customer telemetry never trains shared models without explicit, per-item data rights** (P17).
6. **Tenant identity on every storage path; authorization never UI-only.**

## 2. Threat model v0.1

| # | Threat | Vector observed or expected | Controls (owner) |
|---|---|---|---|
| T1 | Prompt injection via captured payloads into our analysis | compaction summaries, tool outputs, final messages contain instructions; frontier-model investigations read compressed summaries | content never passed as instructions; investigations operate on structural summaries; any model call over payload content uses a fixed system prompt that frames content as data and is tested with injection probes (Intelligence) |
| T2 | Secret leakage in telemetry | shell commands and tool inputs contain tokens; raw request bodies include `metadata.user_id`; OTel resource attributes include account identifiers | SDK and collector secret detection (key formats, authorization headers, `sk-ant-`, `ghp_`, AWS, GCP, JWT); shell commands reduced to binary; raw bodies stay customer-side; PII attribute strip list (Capture) |
| T3 | PII in vendor telemetry by default | **Observed:** every Claude Code OTel record carries `user.email`, `user.account_id`, `user.account_uuid`, `user.id`, `organization.id`, `ccr.session.id` | adapter strips these unless `keep_pii=True`; the strip list is versioned per adapter and published (Capture) |
| T4 | Tenant escape | shared analytical store, shared object store, replay orchestrator | tenant id in every table key and object prefix; row-level policies; per-tenant encryption keys in Phase 3; authorization at the API, not the UI (Data Plane, Infra) |
| T5 | Telemetry poisoning or forgery | an agent or a compromised hook emits fake events to hide a failure or trigger an intervention | events signed by the collector; `source_channel` and `capture_tier` recorded; detectors cross-check channels (a tool result with no request, a stop with no model response) and flag inconsistency; runtime control never acts on single-channel evidence (Capture, Control) |
| T6 | Replay escape or side effects | replayed tool calls hit production services; sandbox breakout | side-effect classification (SPEC-02); irreversible, financial, external-communication and security-sensitive tools are mocked or refused in replay; isolation technology chosen by ADR-007 benchmark; network deny-by-default; credentials never mounted (Replay, Security) |
| T7 | Malicious artifacts | replayed repository content or fixtures contain executables | fixtures are data; the runner executes only the harness under test in the sandbox; artifact scanning before snapshot promotion (Replay) |
| T8 | Supply chain | our SDK, instrumentors and hook adapter run inside customer harnesses | signed releases; SBOM; minimal dependencies; hook adapter is a single-file script with no network access beyond the configured receiver; reproducible builds (Capture, Infra) |
| T9 | Control-plane abuse | an attacker triggers interventions (pause, deny, stop) at scale | control path separate from analytics path; role separation (viewer, analyst, replay operator, policy author, control approver, administrator); high-impact interventions require approval; full audit (Control) |
| T10 | Identity spoofing | forged collector identity or tenant header | mTLS between collector and ingestion; per-tenant credentials; no tenant from client-supplied headers alone (Infra) |
| T11 | Data exfiltration via export or integration | exports, observability-vendor integrations | export is a role; exports are audited; integration payloads are structural unless opted in (Management) |
| T12 | Hook adapter as an attack surface on the customer's machine | the hook command runs with the developer's privileges on every tool call | adapter writes append-only to a local file or POSTs to localhost; never reads stdin beyond the payload; never executes content; documented timeout; code audited and tiny (Capture) |
| T13 | Over-collection by configuration drift | a customer enables content capture flags fleet-wide by accident | content flags are per-project with explicit confirmation; collector reports the active profile as a metric; weekly profile audit in the product (Management) |

## 3. Data classification and retention classes
| Class | Examples | Default location | Default retention |
|---|---|---|---|
| Structural telemetry | events with hashes and sizes | managed store | 90 days (OPEN) |
| Payloads | prompts, tool I/O, summaries, raw bodies | customer object store | 7 days (OPEN) |
| Snapshots and fixtures | filesystem snapshots, cassettes | customer object store | tied to incident lifetime |
| Incident evidence | evidence packages, graphs | managed store | 1 year (OPEN) |
| Corpus items | labelled trajectories with data rights | managed, segregated by rights | per rights tag |
| Audit log | policy, intervention, replay, export, retention, permission changes | managed, immutable | 7 years or per contract |

## 4. Redaction and secret detection
Redaction points: before SDK emission (strongest), collector-side, ingestion-side. Secret detectors: known key formats, authorization and cookie headers, private keys, connection strings, high-entropy tokens near key-like names. Shell commands: binary only by default. File paths: hashed by default. Redaction state is recorded on every `PayloadRef` (`none`, `partial`, `full`, `hashed`).

## 5. Deployment models
Default **hybrid**: collector, payload store, snapshot store, replay runner customer-side; structural telemetry to the managed service. **Managed**: opt-in payload storage and managed replay for small teams. **Private cloud / self-hosted** (Phase 3): the full engine in the customer's environment. The event model and adapters are identical across models.

## 6. Replay security (summary; detail in SPEC-02)
Customer-side runner by default; container isolation in Phase 1 with microVM evaluated in the ADR-007 benchmark; network deny-by-default with explicit allowlists for mocked services only; no credentials mounted; resource quotas and wall-clock limits; outputs sanitized before leaving the sandbox; every replay audited (who, what manifest, what fidelity, what side-effect classes were permitted).

## 7. Control-plane security (design, Phase 3+)
Separate availability domain from analytics; roles as above; every intervention records trigger, policy version, evidence, decision, actor, execution, result and rollback possibility; fail-open, fail-closed or degrade-to-human per customer policy per action class; high-impact interventions require a human approver until the readiness gate is met for that fleet (PLAN-04 Phase 4).

## 8. Data rights and training separation
Every corpus item carries one of: `internal_benchmark`, `open_source_permitted`, `customer_isolated`, `training_prohibited`, `training_allowed`. Operational processing permissions are distinct from training permissions. Cross-customer learning reads only items whose rights allow it. Permission is never inferred (HRCP-02 §60).

## 9. Compliance direction
SOC 2 Type I in Phase 2, Type II in Phase 3; ISO 27001 and regional deployment by customer demand. Architecture must never preclude them; no compliance theatre before product-market evidence (PLAN-09 D4).

## 10. Open questions
1. Default retention values (structural 90 days, payload 7 days) need partner input.
2. Whether the hook adapter should sign payloads with a per-machine key to address T5 on Tier B.
3. Managed replay offering: whether to offer it at all in Phase 2 given T6.
