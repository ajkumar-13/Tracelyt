# PagerDuty: LangGraph SRE agent with parallel sub-agent hypothesis fan-out; primary engineering post not reachable this pass

evidence_grade: C

Access note: PagerDuty's engineering post (https://www.pagerduty.com/eng/inside-pagerdutys-sre-agent-how-we-built-deep-incident-investigation/) was blocked to both WebFetch and curl, and the web-search budget was used up before this case. The only facts are carried forward from the target list. The case is kept rather than replaced because the primary evidence does exist.

```yaml
org: PagerDuty
role: AI agent platform (public: Micah Mayo, Staff SWE; Viktor Vasylkovskyi, Senior SWE)
track: builder
date: 2026-10-05
interviewer: desk
method: desk
harnesses_frameworks: [LangGraph (bulk-synchronous-parallel sub-agent hypothesis fan-out)]
domain: other (SRE incident investigation)
runs_per_day: unknown
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
tooling_today: unknown
coding_agent_traces_flow_to: unknown
can_reproduce_failed_run: unknown
has_compared_cohorts: unknown
most_wanted_question: unknown
data_constraints:
  cannot_leave: [customer_data]
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
referrals: [Micah Mayo, Viktor Vasylkovskyi]
quotes: []
sources:
  - https://www.pagerduty.com/eng/inside-pagerdutys-sre-agent-how-we-built-deep-incident-investigation/
tags:
  harnesses_frameworks: carried from 09-interview-targets.md, not re-verified
  cannot_leave: inferred (agent investigates customers' production incidents; customer telemetry implied)
```

## Evidence
- Carried, not re-verified: PagerDuty's SRE agent is built on LangGraph and fans out sub-agents in parallel to test hypotheses (a bulk-synchronous-parallel pattern) during incident investigation (https://www.pagerduty.com/eng/inside-pagerdutys-sre-agent-how-we-built-deep-incident-investigation/).

## What this case says for Gate A
Nothing countable from this pass. The architecture (long-running, tool-heavy, parallel sub-agents) is where subagent attribution and first-divergence analysis matter most, and an SRE-native buyer understands incident tooling. All of that is inference from a single carried fact, so re-run this case with web search.
