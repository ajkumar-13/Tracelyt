# PLAN-09 — Risks and Kill Criteria

Extends HRCP-00 §81 and HRCP-02 §76 with the October 2026 evidence. Each risk has an owner, a leading indicator we watch, and the mitigation already in the plan.

## 1. Market and competitive risks

| # | Risk | Evidence | Indicator | Mitigation |
|---|---|---|---|---|
| M1 | Customers are satisfied with clustered traces and an AI assistant | Seven vendors cluster failures; LangSmith Engine and Arize Signal open PRs | Design partners stop reviewing incidents; "Datadog is enough" in interviews | Lead with the regression gate and replay, which none of them ship; export into their tools rather than compete for the dashboard |
| M2 | Incumbent assembles the loop by acquisition | Arize to Dynatrace, Galileo to Splunk, Portkey to Palo Alto are explicit attempts | Incumbent announces replay or regression against production | Speed on replay and corpus; open standard makes us the reference implementation; partner with the incumbents that lack it |
| M3 | A funded newcomer builds the same loop | Raindrop ~$50M, Judgment Labs $32M, Laminar same wedge, Entire $60M on coding-agent recording | Their roadmap announcements; shared design partners | Parallel streams rather than sequencing; coding-agent and closed-harness depth they lack; decide Laminar relationship in Phase 0 |
| M4 | Platform vendors absorb the harness and the evidence | Claude Managed Agents, OpenAI Frontier, Vertex Agent Engine | Vendor ships failure clustering or regression for its own agent | Cross-vendor is structural; vendors become customers; native emission partnerships |
| M5 | Budget sits with security, not reliability | Headline incidents are sold as security; $250M to $300M security exits | Buyers route us to the CISO | Evidence export to security products; security-case regression suites; do not become a firewall |
| M6 | Buyer fatigue with observability vendors | HN vendor cycling; 84% pursuing tool consolidation | Procurement objections on "another vendor" | Customer-side payloads and replay; integration-first; price as release infrastructure, not telemetry |
| M7 | True agent penetration outside coding stays low for two years | Menlo 16%, McKinsey ≤10%, Gartner 17% | Builder pipeline thin | Two domains with coding first; vendor track; grow with the market rather than ahead of it |
| M9 | The largest fleets build the layer in-house | Desk research 2026-10-05: Uber (gateways, uReview, cost dashboards), LinkedIn (observable-by-default orchestrator), NVIDIA (OpenShell policy sandbox, hiring for evals), Datadog (140+ nightly evals, A/B cohorts before changing Claude Code defaults), Spotify (verifiers and judge) all built the adjacent layers themselves (`docs/phase0/discovery/05-synthesis.md` §3.6) | Design-partner conversations end with "we have this"; references but no contracts from top-20 fleets | Open recorder and convention make the build path the expensive one; sell the gate and replay, which none of them built; target the next 200 fleets with central platform teams but no eval infrastructure |
| M10 | Datadog becomes the default fleet monitor for coding agents | Agent Console (June 2026) ingests Claude Code OTel, prices waste per session, pushes hooks org-wide (`cases/fleet-20-datadog.md`) | Prospects already on the console; Datadog announces replay or change gating | Position as the layer the console lacks (reconstruction, incidents, first divergence, replay, gate); export into it; never compete for the fleet dashboard |
| M8 | Cost pain declines as a wedge | LangChain: cost fell down the blocker list | Economics features unused | Economics is success-adjusted, not cost alone; lead with quality and regression |

## 2. Technical risks

| # | Risk | Evidence | Indicator | Mitigation |
|---|---|---|---|---|
| T1 | Framework instrumentation cannot be normalized meaningfully | HRCP-02 §76 | Proof B exceptions over 10%; v0.1 model needs per-framework forks | Small v0.1 model; extensibility for unknown events; fidelity disclosure instead of false uniformity |
| T2 | Closed harnesses close further or churn their surfaces | Claude Code JSONL "internal and changes between versions"; Codex `exec` and `mcp-server` have no OTel | Adapter breakage rate; vendor removes hooks | Two permanent adapter engineers; prefer hooks and OTel over transcripts; vendor partnerships; Tier C fallback |
| T3 | First divergence provides little value on real data | LongRCA best 24% exact; TRAIL 11% | Benchmark top-3 under 40% controlled; partners disagree with hypotheses | Product delivers on observed and reconstructed layers plus regression gate without it; ranked hypotheses with confidence; corpus improves it over time |
| T4 | Replay fidelity ceiling too low to be useful | No standard for replayable records; LangGraph replay re-executes LLM calls; checkpoints miss Bash side effects | Level 3 under 50% of coding failures at Phase 2 | Fixture-plus-snapshot side channel; customer-side runner; Level 2 regression still beats no gating; disclose fidelity |
| T5 | Replay is economically useless | HRCP-02 §76 | Replay compute cost exceeds the cost of re-running the task N times without fixtures | Measure early; fall back to re-run with recorded fixtures only where they reduce variance or cost |
| T6 | Telemetry volume makes SaaS uneconomic | Long-running agents; HRCP-00 §81 Risk 7 | Cost per million runs above pricing | Structural telemetry only; customer-side payloads by default; content addressing; tiered retention; local detectors |
| T7 | Identity propagation fails across processes and MCP | Claude Code does not pass OTEL_* to subprocesses | Orphaned spans; broken delegation trees | Propagation library in Phase 1; hook-based correlation; fidelity disclosure |
| T8 | Replay executes hostile content and escapes | HRCP-02 §35 to §37 | Any sandbox incident | Customer-side runner by default; microVM isolation benchmarked; network deny-by-default; credential stripping |
| T9 | Detectors produce alert fatigue | HRCP-02 §13 | Precision under 0.9 on partner data | Detector contract with published precision; no detector ships below threshold |
| T10 | Specialized models never beat rules | HRCP-02 §31 | Benchmark margins flat | Ship only models that beat the baseline by a published margin; frontier reasoning on compressed summaries for the rest |

## 3. Standard and ecosystem risks

| # | Risk | Indicator | Mitigation |
|---|---|---|---|
| S1 | OTel rejects control events | Proposals stall past 12 months | Track 2 `harness.*` registry is complete alone; OpenInference precedent |
| S2 | Vendors standardize their own namespaces | `claude_code.*`, `forge.*` proliferate | Immediate mappings; upstream fast; vendor partnerships |
| S3 | Another OSS project claims the space | OpenLIT "harness engineering" branding | Publish registry and conformance in Phase 1; invite adoption |
| S4 | Standard work consumes the team | Engineers pulled into SIG process | Cap at two half-time engineers plus devrel; product never blocks on upstream |

## 4. Data and legal risks

| # | Risk | Mitigation |
|---|---|---|
| D1 | Corpus built on data without rights | Data-rights tag on every corpus item from day one; counsel in Phase 0; never infer permission (HRCP-02 §60) |
| D2 | Customer telemetry becomes training data without consent | Training permissions distinct from operational processing; default isolation; explicit opt-in for cross-customer learning (HRCP-01 §78) |
| D3 | Sensitive payloads leak | Customer-side default; redaction in SDK; secret detection; retention tiers; audit |
| D4 | Compliance demanded before product-market fit | Architecture that does not preclude it; SOC 2 Type I in Phase 2, Type II in Phase 3; no compliance theatre earlier (HRCP-02 §41) |

## 5. Execution risks at 100+ engineers

| # | Risk | Mitigation |
|---|---|---|
| E1 | Build all layers to equal depth and arrive undifferentiated | Gates fund phases; benchmark team grades claims; depth follows evidence |
| E2 | Platform outruns semantics | Normalizer and event model v0.1 before storage scale |
| E3 | Hiring the unusual roles slowly | Sandbox, instrumentation, standards, alignment and forward-deployed roles opened in month 0; research hiring from LongRCA, MAST, TRAIL author pools |
| E4 | Burn before product-market fit | Second close tied to Gates D/E/F; monthly gate review; small-team variant as a fallback plan |
| E5 | Name and brand collisions | Rename in Phase 0; distinct spec and product names |

## 6. Kill and pivot criteria

Revise or stop the thesis if, at the stated gate, the evidence shows:

**At Gate A/B (month 3):**
- Fewer than 8 of 50 interviewees describe a harness regression they would pay to prevent.
- Proof B needs more than 25% framework-specific exceptions.
- Proof F finds the injected divergence in the top 3 for under 40% of controlled cases.
- Fewer than 5 of 50 will host replay in their environment.

**At Gate C (month 9):**
- Fewer than half the detectors reach precision 0.9 on partner data, or partners confirm fewer than 10 real failures found.
- OSS adoption under 100 organizations with no growth.
- Fewer than 4 of 8 partners still streaming.

**At Gate D/E/F (month 15):**
- Partners rate under 50% of incidents real and actionable.
- First divergence under 50% top-3 on controlled faults, and partners agree with under 40% of hypotheses.
- Level 3 replay under 40% of coding failures and Level 2 under 50% of workflow failures.
- Fewer than 3 paying customers, none changing a release workflow because of us.
- A competitor ships regression-against-production-failures as a CI gate and partners say it is good enough.

**At Gate G/H (month 24):**
- Fewer than 5 customers running the regression gate on every change.
- No documented prevented regression.
- Net revenue retention under 100%.

**Pivot options, in order of preference if a kill criterion fires:**
1. Narrow to the regression gate for one domain and one harness family (the small-team variant).
2. Become the standard and instrumentation company with a managed recorder, and license the intelligence to platforms.
3. Sell the replay and sandbox capability to an observability or security platform that lacks it.

## 7. Competitive response policy

Per HRCP-02 §77: when a competitor ships a planned capability, ask whether their implementation is structurally complete, whether it supports both open and closed harnesses, whether it is commoditized, whether we should integrate rather than build, and whether the loop still adds something unique. Record the answer as an ADR.
