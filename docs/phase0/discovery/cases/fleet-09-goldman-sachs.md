# Goldman Sachs: first major bank to pilot Devin, with "hundreds" of agent instances planned to scale to thousands alongside ~12k developers; no public governance or incident detail reachable

evidence_grade: C

Kept rather than substituted because two independent public sources exist (CNBC July 2025, Forbes August 2026), but neither could be fetched (egress-blocked) and the web-search budget was exhausted, so facts come from the target list's summary of the Forbes piece and a secondary research corpus that summarizes CNBC and IBM. Treat everything here as secondary.

```yaml
org: Goldman Sachs
role: unknown (public: Marco Argenti, CIO)
track: fleet
date: 2026-10-05
interviewer: desk (no interview)
method: desk
harnesses_frameworks: [Devin (Cognition), GitHub Copilot, Claude (for ops, per target list)]
domain: coding
runs_per_day: "unknown; 'hundreds of instances, planning thousands' of Devin agents; ~12k developers"
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
  last_change: unknown
  regression_detection: unknown
  silent_regression_experienced: unknown
  would_pay_to_prevent: unknown
controls_owned (fleets): []
tooling_today: []
coding_agent_traces_flow_to: unknown
can_reproduce_failed_run: unknown
has_compared_cohorts: unknown
most_wanted_question: unknown
data_constraints:
  cannot_leave: unknown
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: unknown
credible_contract_size: unknown
automation_limits: unknown
would_allow_pause_stop_on_evidence: unknown
reaction:
  would_use_next_week: unknown
  does_not_believe: unknown
design_partner_candidate: unknown
referrals: []
quotes: []
sources:
  - https://www.cnbc.com/2025/07/11/goldman-sachs-autonomous-coder-pilot-marks-major-ai-milestone.html
  - https://www.ibm.com/think/news/goldman-sachs-first-ai-employee-devin
  - https://www.forbes.com/sites/bernardmarr/2026/08/06/how-goldman-sachs-is-using-agentic-ai-for-software-engineering-at-scale/
  - https://github.com/Chipagosfinest/software-factory/blob/main/docs/devin-factory.md
tags:
  harnesses_frameworks: stated in secondary sources (corpus summary of CNBC; target list summary of Forbes)
  runs_per_day: stated in secondary sources
```

## Evidence

- Goldman Sachs was described as the first major bank to adopt Devin, running "hundreds of instances" and planning thousands; the CIO expected 3-4x impact over prior AI tools (secondary corpus summarizing CNBC and IBM) (https://github.com/Chipagosfinest/software-factory/blob/main/docs/devin-factory.md; https://www.cnbc.com/2025/07/11/goldman-sachs-autonomous-coder-pilot-marks-major-ai-milestone.html).
- Forbes (Aug 2026), as summarized in our target list: Devin scaling from hundreds to thousands of agents alongside ~12k developers; Copilot in use; Claude used for ops (https://www.forbes.com/sites/bernardmarr/2026/08/06/how-goldman-sachs-is-using-agentic-ai-for-software-engineering-at-scale/).
- Nothing reachable describes governance, permissions, telemetry, cost controls or incidents.

## What this case says for Gate A

Goldman is a scale signal only: a regulated bank running a closed vendor agent in the hundreds to thousands of instances. Everything a Gate A counter needs (failures, regressions, data constraints, replay) is unknown from public evidence. In regulated finance, code and prompts are likely unable to leave the environment, but that is an assumption to test in a conversation, not a finding. This row should not move any counter.
