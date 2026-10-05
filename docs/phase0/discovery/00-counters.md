# Gate A Counters (desk research, final 2026-10-05)

Generated from `cases/` by `scripts/tally_discovery.py`; proxies and the candidate list are maintained by hand below. Method and limits: `04-desk-research-method.md`. Narrative: `05-synthesis.md`.

## 1. Observable counters (generated)

| Counter | All (50) | A+B only (48) | builder | fleet | vendor |
|---|---|---|---|---|---|
| Cases filed | 50 | 48 | 20 | 20 | 10 |
| Silent regression experienced (yes) | 9 | 9 | 3 | 2 | 4 |
| Would pay to prevent (yes, stated) | 1 | 1 | 1 | 0 | 0 |
| Replay inside env OK (yes or conditional, stated) | 0 | 0 | 0 | 0 | 0 |
| Design-partner candidate (yes) | 0 | 0 | 0 | 0 | 0 |
| Design-partner candidate (yes or maybe) | 1 | 1 | 1 | 0 | 0 |
| Last failure attributed to non-model component | 26 | 26 | 9 | 8 | 9 |
| Last failure attributed to model | 2 | 2 | 0 | 1 | 1 |
| Coding-agent traces flow to an observability stack | 21 | 21 | 6 | 8 | 7 |
| Can reproduce a failed run (yes) | 0 | 0 | 0 | 0 | 0 |
| Has compared cohorts (yes) | 19 | 19 | 8 | 6 | 5 |
| Would allow pause/stop on evidence (yes or conditional) | 6 | 6 | 0 | 5 | 1 |

Evidence grades: A 13, B 35, C 2 (Goldman Sachs, Doctolib). Attributed component where stated (28 cases): context 6, verification 6, environment 5, permission 4, prompt 3, model 2, budget 1, compaction 1. Budget owner where inferable (32 cases): AI platform 17, developer productivity 13, security 1, observability 1. Regression detection today where stated: evals 20, CI 7, manual 6, production users 3, none 1.

## 2. Counters against the PLAN-04 targets and PLAN-09 §6 kill triggers

| Counter | Target at 50 | Kill trigger at 20 | Stated (desk) | Proxy (declared in `04` §4) | Reading |
|---|---|---|---|---|---|
| Interviews completed | 50 | — | 0 live; 50 desk cases (48 A/B) | — | Desk cases are not interviews; reported as such. |
| Described a harness regression they would pay to prevent | ≥ 15 | < 4 | Silent regression stated: **9** (Lyft, Shopify, AutonomyAI, Microsoft .NET, Elastic, Anthropic, Codex, Amp, Amazon). Would pay stated: **1** (AutonomyAI, inferred from switching vendors to catch regressions). | Harness-caused failure with material cost described: **13** (the nine above plus Uber budget exhaustion, Spotify PRs that pass CI but are wrong, PagerDuty context rot, the Railway database wipe). | The kill trigger does not fire (9 stated against "fewer than 4"). The target of 15 is not met and cannot be met from the public record because willingness to pay is unobservable. |
| Would host replay inside their environment | ≥ 10 | < 2 | **0** stated. | Content cannot leave the environment, stated or inferred: **19** (stated for League, Factory, GitHub; inferred for 16 others). Already run agents in customer-controlled sandboxes: **7** (Stripe dev boxes, Ramp on Modal, Spotify Kubernetes pods, NVIDIA OpenShell, Brex CrabTrap proxy, Cisco CX on-prem, Coinbase self-hosted LangSmith). | Not evaluable; the trigger is neither passed nor failed. The proxies say in-environment replay is the only plausible deployment, not that anyone will host ours. First Phase 1 question. |
| Design-partner candidates (yes) | ≥ 12 | — | **0** confirmed; 1 maybe (AutonomyAI). | Candidate list below: **18** organizations with a public owner and unsolved pain in scope. | Recruiting list, not a count. |
| Attributed last failure to a non-model component | report share | — | **26 of 28** attributed cases (93%); corpus: 108 of 113 issues (96%). | — | Strongest finding; survivorship applies. |
| Already pipe coding-agent traces to an observability stack | report share | — | **21 of 50**, but only Datadog states a third-party destination; the rest are in-house gateways, MLflow, LangSmith, Logfire, Braintrust, Temporal, audit logs. | — | Capability universal, routing rare, destination mostly in-house. |
| Budget owner distribution | report | — | AI platform 17, developer productivity 13, security 1, observability 1, unknown 18. | — | Matches PLAN-07 buyer (platform team). |

## 3. Design-partner candidate list for Phase 1 (from the cases)

Ranked by evidence grade, pain in scope, and absence of an in-house equivalent. Public owners are named in each case file; confirm titles before contact (`03-outreach-and-tracking.md`).

| # | Organization | Track | Case | Why |
|---|---|---|---|---|
| 1 | Spotify | builder/fleet | builder-03, fleet-04 | Worst failure is "passes CI, functionally wrong"; says it has no structured way to pick prompts or models; traces already in MLflow. |
| 2 | Salesforce (Agentforce DX) | builder | builder-06 | Two swappable harnesses with different, incomplete telemetry; upstream upgrades can silently drop stream content; standards collaborator. |
| 3 | Elastic (Kibana) | fleet | fleet-08 | Lived a silent hook regression for weeks; hooks shared across Claude Code and Cursor; permission hook fails open. |
| 4 | Microsoft .NET (dotnet/runtime) | fleet | fleet-06 | 27 rules-file edits in 17 months, each validated by hand across models; silent model-routing regression. |
| 5 | Shopify (Sidekick) | builder | builder-16 | Prompt-attributed failures and reward hacking; eval-driven but no change gate on the harness. |
| 6 | Lyft | builder | builder-08 | 90% simulator success versus poor production; CI prompt linting but no production-derived regression suite. |
| 7 | monday.com (Sidekick) | builder | builder-15 | Context and tool-sprawl failures; CI-gated offline evals; closest to adopting a production-derived gate. |
| 8 | Stripe (Minions) | builder/fleet | builder-02, fleet-02 | 1,300+ unattended PRs a week; failure controlled by structure, no published success rate. |
| 9 | Brex | fleet | fleet-17 | Agent blind to CI and review-bot feedback; CrabTrap logs every agent request; stale-docs CI check is its only gate. |
| 10 | Monzo (Agent Chip) | builder | builder-05 | 1,800 tasks a day in a regulated bank; golden-set replay exists for one agent only. |
| 11 | Ramp (Inspect) | builder | builder-04 | Owns the harness (OpenCode fork on Modal); Braintrust wired in with no stated gate. |
| 12 | Nubank | fleet | fleet-11 | Held-out benchmark built by hand for one migration; CI-gated skill vetting extending to MCP and rules. |
| 13 | PagerDuty (SRE agent) | builder | builder-07 | Context rot stated as the failure; parallel subagents; evals in place. |
| 14 | Duolingo (DevXAI) | builder | builder-17 | One library switching between Codex CLI and Claude Code SDK; needs a cross-harness gate. |
| 15 | AutonomyAI | builder | builder-20 | Twelve silent no-op deployments; switched vendors to catch regressions; the one "would pay" signal. |
| 16 | BlackRock (Aladdin Copilot) | builder | builder-13 | Daily CI evals across a plugin registry fed by 50+ teams; attribution across teams is the pain. |
| 17 | Factory | vendor | vendor-08 | Content stays with the customer; OTLP under its own names; verification-gated Missions. Standards and emitter conversation. |
| 18 | Sourcegraph Amp | vendor | vendor-06 | Documented model-update regression; "mini evaluation" after prompt edits; enterprise control plane. Emitter conversation. |

Excluded on purpose: Datadog, Sentry, Cloudflare (sell adjacent products), NVIDIA, Uber, LinkedIn (build the layer in-house), Goldman Sachs and Doctolib (grade C), the Railway incident (individual developer).

## 4. Corpus and survey lines (not merged into the case counts)
- GitHub corpus: 113 issues; 30 (27%) tied to a specific change, 18 of them a harness release; 0 detected by CI or a gate; 62% seen live by the user; 5 (4%) classed model.
- Surveys: 52% run offline evals and 37% online (LangChain, N=1,340); 75% of production agent teams forgo formal benchmarks (UC Berkeley, N=306); automated root-step localization 11–24% (TRAIL, LongRCA); 7% use LLM observability in production (Grafana, N=1,255) against 89% with some agent observability in a self-selected LangChain audience.
