# Interview Synthesis Template

Copy per interview to `docs/phase0/discovery/interviews/YYYY-MM-DD-<org>.md`. Fields marked (G) feed the Gate A counters.

```yaml
org:
role:
track: builder | fleet | vendor
date:
interviewer:
harnesses_frameworks: []          # e.g. LangGraph, Claude Agent SDK, Claude Code, Codex
domain: coding | workflow | support | research | other
runs_per_day:
failure_definition:
failure_rate_estimate:
cost_per_failed_run:
last_failure:
  symptom:
  detected_by: user | cost_alert | dashboard | ci | nobody
  time_to_why:
  attributed_component: model | prompt | context | compaction | memory | tool | mcp | permission | retry | subagent | verification | budget | environment | unknown
  recurred: yes | no
  their_words: ""
harness_change:
  last_change:
  regression_detection: none | manual | evals | ci | production_users
  silent_regression_experienced: yes | no      # (G) pain counter
  would_pay_to_prevent: yes | no | unclear      # (G) pain counter
controls_owned (fleets): [rules_files, hooks, permissions, mcp_servers, tool_allowlists, model_effort, budgets, ci_checks]
tooling_today: []
coding_agent_traces_flow_to: none | datadog | grafana | langsmith | other
can_reproduce_failed_run: yes | partially | no
has_compared_cohorts: yes | no
most_wanted_question: ""
data_constraints:
  cannot_leave: [prompts, tool_outputs, code, customer_data, none]
  replay_inside_env_ok: yes | no | conditional   # (G) replay counter
  replay_outside_env_ok: yes | no
budget_owner: observability | ai_platform | dev_productivity | security | unknown
credible_contract_size:
automation_limits: ""
would_allow_pause_stop_on_evidence: yes | no | conditional
reaction:
  would_use_next_week: ""
  does_not_believe: ""
design_partner_candidate: yes | maybe | no      # (G)
referrals: []
quotes:
  - q: 1
    text: ""
```

## Gate A counters (update weekly in `00-counters.md`)

| Counter | Target at 50 | Kill trigger at 20 |
|---|---|---|
| Interviews completed | 50 | — |
| Described a harness regression they would pay to prevent | ≥ 15 | < 4 at 20 (projects to < 8) |
| Would host replay inside their environment | ≥ 10 | < 2 at 20 |
| Design-partner candidates (yes) | ≥ 12 | — |
| Attributed last failure to a non-model component | report share | — |
| Already pipe coding-agent traces to an observability stack | report share | — |
| Budget owner distribution | report | — |
