# League: health-tech moved to 98% Claude adoption with no bake-off, adopts new models on release day, keeps patient data in an environment Claude cannot reach

evidence_grade: C (one Anthropic-published customer story with named League executives; specific on governance posture but vendor-curated; no incidents)

Replacement note: target row 15 (Instacart) was replaced. Its evidence URL is on openai.com, which is egress-blocked; claude.com/customers/instacart returns 404; and the session's web-search budget was exhausted, so no verifiable Instacart facts could be gathered. League is row 23 of the same Track 2 list.

```yaml
org: League
role: unknown (named: Signy Roland, AVP of AI Transformation; Jordan Christensen, SVP Data and AI Engineering; Dan Galperin, CTO and co-founder)
track: fleet
date: 2026-10-05
interviewer: desk
method: desk
harnesses_frameworks: [Claude Code, Claude (enterprise), "Swarm" (internal parallel-agent orchestration on Claude Platform), Claude-based PR triage bot]
domain: coding
runs_per_day: unknown (overnight autonomous coding sessions via Swarm; 2–3x more merges per week)
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
  last_change: adopted a new frontier model on release day ("I went into Fable the day it came out and started using it")
  regression_detection: unknown   # no formal bake-off; "your bake-off is going to be wrong as soon as you finish it"
  silent_regression_experienced: unknown
  would_pay_to_prevent: unclear
controls_owned: [permissions, ci_checks]   # stated: patient-data environment isolated from Claude; a PR triage bot classifies every PR by scale and risk. Inferred: an AI Transformation function owns the rollout
tooling_today: [Claude Code, Swarm (internal orchestrator), Claude PR triage bot]
coding_agent_traces_flow_to: unknown
can_reproduce_failed_run: unknown
has_compared_cohorts: no   # inferred: they explicitly skipped formal tool bake-offs
most_wanted_question: ""
data_constraints:
  cannot_leave: [customer_data]   # stated: patient data kept in a separate environment with no Claude access
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: ai_platform   # inferred from the "AVP of AI Transformation" and "SVP Data and AI Engineering" roles
credible_contract_size: unknown
automation_limits: "Patient data environment has no Claude access; vendor risk assessments validated by Claude are then signed off by a human (49 of 53 validated)."
would_allow_pause_stop_on_evidence: unknown
reaction:
  would_use_next_week: ""
  does_not_believe: ""
design_partner_candidate: unknown
referrals: []
quotes:
  - q: 10
    text: "The pace of change is so fast that your bake-off is going to be wrong as soon as you finish it."
  - q: 10
    text: "I went into Fable the day it came out and started using it, and I was unlocked further."
  - q: 18
    text: "it took us less than a quarter to stand up all of the security things we needed to become AI-native."
sources:
  - https://claude.com/customers/league
tags:
  harnesses_frameworks: stated
  harness_change.last_change: stated
  regression_detection: stated (no bake-off), inferred (no gating)
  data_constraints.cannot_leave: stated
  controls_owned: stated (isolation, triage bot), inferred (owner)
  budget_owner: inferred
  quotes: stated (fetched page via summarizer)
```

## Evidence
- Claude adoption rose from about 80% at the March 2026 rollout to 98%. AI-authored code went from about 70% to 98%, and cycle time from idea to PR halved (https://claude.com/customers/league).
- The enterprise agreement was signed on a Friday and the company was live on Monday, with no formal bake-off (https://claude.com/customers/league).
- Jordan Christensen: "The pace of change is so fast that your bake-off is going to be wrong as soon as you finish it." He also said he started using a new model "the day it came out" (https://claude.com/customers/league).
- Patient data is kept in a separate environment that Claude cannot access. Standing up the needed security controls took less than a quarter (https://claude.com/customers/league).
- "Swarm" is an internal orchestration tool on Claude Platform for parallel agents, including overnight autonomous coding sessions (https://claude.com/customers/league).
- A Claude-based bot triages every pull request by change scale and risk (https://claude.com/customers/league).
- Vendor risk assessments dropped from weeks to 15 minutes. Claude validated 49 of 53, and each was then signed off by a human (https://claude.com/customers/league).
- No incidents, telemetry stack or cost controls are disclosed (https://claude.com/customers/league).

## What this case says for Gate A
League is a clean example of the risk posture our CI-gating pitch addresses. Leadership explicitly rejects bake-offs as too slow and moves to new models on release day, while overnight autonomous agents produce 98% of the code. Any model or harness regression would therefore reach the whole org at once with no comparison baseline. Whether they would value a cheap, automatic before/after comparison or reject it as "bake-off" friction is the question for a live interview. Stated patient-data isolation means customer data cannot reach the agent, let alone a third party. That supports in-environment-only telemetry and replay. No pain-counter evidence exists publicly.
