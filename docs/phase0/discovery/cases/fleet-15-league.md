# League: health-tech at 98% Claude adoption with no bake-off, overnight "Swarm" runs of up to 50 parallel agents, tier-based model access and strict agent permission limits, patient data in an environment Claude cannot reach, and an automatic prompt-rewriting loop

evidence_grade: B (pass 2: two Anthropic-published pages with named League executives, including a Q&A with concrete governance mechanisms (tiered model access, permission limits, connector controls, spend transparency) and an automatic prompt-optimization system. Vendor-curated and silent on incidents, so not A.)

Replacement note (pass 1): target row 15 (Instacart) was replaced; its evidence sits on openai.com (egress-blocked). League is row 23 of the same Track 2 list.

```yaml
org: League
role: unknown (named: Signy Roland, AVP of AI Transformation; Jordan Christensen, SVP Data and AI Engineering; Dan Galperin, CEO/CTO and co-founder)
track: fleet
date: 2026-10-05
interviewer: desk (no interview)
method: desk
harnesses_frameworks: [Claude Code, Claude Enterprise, "Swarm" (internal orchestration layer on Claude Code / Claude Platform: lead agent decomposes work and spawns a parallel agent team), Claude-based PR triage bot, automatic prompt-rewriting system, Claude Security, Claude Design]
domain: coding   # plus finance (60+ automated processes), compliance, legal, infrastructure
runs_per_day: unknown (overnight Swarm sessions; up to 50 parallel agents on a single problem; one eight-PR stack merged ~48,000 lines across 271 files; 2–3x more merges per engineer per week)
failure_definition: unknown
failure_rate_estimate: unknown
cost_per_failed_run: unknown
last_failure:
  symptom: unknown
  detected_by: unknown
  time_to_why: unknown
  attributed_component: unknown
  recurred: unknown
  their_words: ""
harness_change:
  last_change: "Model swaps on release day (Opus 4.5 at its December release; Fable for exploratory sessions; 'I went into Fable the day it came out'); an automatic prompt-rewriting system that optimizes agent prompts across 4 codebases in 2 languages"
  regression_detection: production_users   # inferred: no bake-off by policy; engineers review every PR next morning; the prompt-rewriting loop closes on agent outcomes, not on a frozen test set
  silent_regression_experienced: unknown
  would_pay_to_prevent: unclear
controls_owned (fleets): [permissions, model_effort, tool_allowlists, budgets, ci_checks]   # stated: tier-based model access controls, strict agent permission limits, connector availability management, "custom boundary-setting", spend and usage transparency, PR triage bot
tooling_today: [Claude Code, Swarm, PR triage bot, prompt-rewriting system, Claude Security, Claude Enterprise admin controls]
coding_agent_traces_flow_to: unknown
can_reproduce_failed_run: unknown
has_compared_cohorts: no   # stated: no bake-off; "your bake-off is going to be wrong as soon as you finish it"
most_wanted_question: unknown
data_constraints:
  cannot_leave: [customer_data]   # stated: patient data lives in a separate environment with no Claude access
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: ai_platform   # inferred from the AVP of AI Transformation and SVP Data & AI Engineering roles
credible_contract_size: unknown
automation_limits: "'none of it ships until an engineer reviews it'; patient-data environment has no Claude access; vendor risk assessments validated by Claude (49 of 53) are human-signed; strict agent permission limits while controls were built"
would_allow_pause_stop_on_evidence: unknown
reaction:
  would_use_next_week: unknown
  does_not_believe: unknown
design_partner_candidate: unknown
referrals: []
quotes:
  - q: 10
    text: "The pace of change is so fast that your bake-off is going to be wrong as soon as you finish it."
  - q: 10
    text: "I went into Fable the day it came out and started using it, and I was unlocked further."
  - q: 21
    text: "Nobody is watching them work...because none of it ships until an engineer reviews it"
  - q: 18
    text: "it took us less than a quarter to stand up all of the security things we needed to become AI-native."
sources:
  - https://claude.com/customers/league
  - https://claude.com/customers/league-qa
tags:
  harnesses_frameworks: stated (both pages)
  runs_per_day: stated (50 agents, 48k lines/271 files/8 PRs, 2-3x merges)
  harness_change.last_change: stated (release-day adoption; prompt-rewriting system described in the Q&A, wording via summarizer)
  regression_detection: inferred
  controls_owned: stated (Q&A lists tier-based model access controls, connector availability management, custom boundary-setting, spend and usage transparency; case study: strict agent permission limits)
  has_compared_cohorts: stated (no bake-off)
  cannot_leave: stated
  budget_owner: inferred
  automation_limits: stated
  quotes: verbatim from fetched pages via summarizer (treat as near-verbatim)
```

## Evidence

- Adoption rose from ~80% at the March 2026 rollout to 98%; AI-authored code from ~70% to 98%; idea-to-PR cycle time halved; PR merge rate per engineer up 2–3x; a customer implementation landed two months early; 60+ finance processes automated (https://claude.com/customers/league; https://claude.com/customers/league-qa).
- The enterprise agreement was signed on a Friday and the company was live on Monday; leadership explicitly rejected a formal bake-off: "The pace of change is so fast that your bake-off is going to be wrong as soon as you finish it." Christensen adopted a new model the day it shipped (https://claude.com/customers/league).
- Swarm is League's orchestration layer on Claude Code: a lead agent decomposes work and spawns a parallel team; each agent "takes a real piece of the build, writes the code, runs the tests, and opens a pull request"; runs happen overnight with engineer review next morning; up to 50 parallel agents on one problem; one eight-PR stack merged ~48,000 lines across 271 files (https://claude.com/customers/league-qa).
- Governance mechanisms named in the Q&A: tier-based model access controls, connector availability management, "custom boundary-setting", Claude Security deployment, and spend and usage transparency; the case study adds "strict agent permission limits" while controls were implemented and a ~3-month security review from agreement to company-wide deployment (https://claude.com/customers/league-qa; https://claude.com/customers/league).
- A PR triage bot routes every pull request by change scale and risk (https://claude.com/customers/league).
- An automatic prompt-rewriting system optimizes agent prompts across 4 codebases in 2 languages, described as turning manual debugging into an autonomous loop (summarizer wording) (https://claude.com/customers/league-qa).
- Patient data is housed in a separate environment with no Claude access; vendor security assessments dropped from weeks to 15 minutes, with Claude flagging 49 of 53 as safe and a human signing each (https://claude.com/customers/league).
- A 48-hour "Accelatron" event in March 2026 forced production shipping and reset speed expectations; pods of 3–4 engineers scope, build and deploy in one session (https://claude.com/customers/league).
- Not public: incidents, cost events, telemetry stack, or whether the prompt-rewriting loop is gated against regressions.

## What this case says for Gate A

League is the cleanest statement of the "no bake-off" posture: adopt models on release day, run 50-agent swarms overnight, and rely on next-morning human review as the only regression gate. It now also shows a harness that rewrites its own prompts automatically, which is a continuous harness change with no described baseline. That is the exact exposure a cheap before/after comparison addresses, and the sales risk is equally clear: the SVP considers bake-offs a waste, so the pitch must be "automatic and invisible", not "evaluation". League does own real controls (tiered model access, permission limits, connector allowlists, spend visibility) so a platform buyer exists. Patient-data isolation supports in-environment-only telemetry and replay. No pain counter moves; cannot_leave = customer_data is stated.
