# Monzo: "Agent Chip" internal harness in a regulated bank (~1,800 tasks/day); primary talk not reachable this pass

evidence_grade: C

Access note: the primary sources (Suhail Patel's Background Agents Summit session https://background-agents.com/summit/sessions/suhail-patel/ and InfoQ's write-up https://www.infoq.com/news/2026/03/shipping-monzo/) were blocked by the egress proxy, and the web-search budget ran out before this case. No Anthropic or Claude customer page exists for Monzo (claude.com/customers/monzo returned 404). Every fact below is carried forward from the target list and has not been checked again. The case is kept rather than replaced because the primary evidence does exist.

```yaml
org: Monzo
role: Platform group (public: Suhail Patel, Principal Engineer)
track: builder
date: 2026-10-05
interviewer: desk
method: desk
harnesses_frameworks: ["Agent Chip (internal harness: code generation, review, incident investigation)", Claude, Cursor]
domain: coding
runs_per_day: "~1,800 tasks/day (carried, unverified)"
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
controls_owned (fleets): [mcp_servers, permissions]
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
automation_limits: "Golden paths, sandboxing and MCP governance for Claude and Cursor; conventions encoded as skills (carried, unverified)"
would_allow_pause_stop_on_evidence: unknown
reaction:
  would_use_next_week: unknown
  does_not_believe: unknown
design_partner_candidate: unknown
referrals: [Suhail Patel]
quotes: []
sources:
  - https://background-agents.com/summit/sessions/suhail-patel/
  - https://www.infoq.com/news/2026/03/shipping-monzo/
tags:
  runs_per_day: carried from 09-interview-targets.md, not re-verified
  harnesses_frameworks: carried, not re-verified
  controls_owned: inferred from carried "sandboxing and MCP governance"
  cannot_leave: inferred (UK regulated bank; no explicit statement seen)
```

## Evidence
- Carried, not re-verified: Monzo runs "Agent Chip", an internal harness for code generation, review and incident investigation, at about 1,800 tasks a day and roughly 10% of merged PRs (https://background-agents.com/summit/sessions/suhail-patel/ ; https://www.infoq.com/news/2026/03/shipping-monzo/).
- Carried, not re-verified: Claude and Cursor are governed through golden paths, sandboxing and MCP governance, and conventions are encoded as skills (https://background-agents.com/summit/sessions/suhail-patel/).

## What this case says for Gate A
On the carried facts, Monzo has the shape we want: high volume, its own harness, incident investigation as an agent task, and regulatory pressure that makes in-environment replay the only plausible option. But this pass verified nothing and contributes zero to every counter. Re-run it with web search.
