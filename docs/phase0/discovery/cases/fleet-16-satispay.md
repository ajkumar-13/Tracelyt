# Satispay: EU payments company reached 90% Claude Code adoption in 30 days after a head-to-head evaluation, with budget-level (not per-seat) spend and IT-managed device rollout

evidence_grade: C (one Anthropic-published customer story with a named CTO; specific on rollout mechanics; no incidents or telemetry)

Replacement note: target row 16 (Cisco, Codex) was replaced. Its evidence URL is on openai.com, which is egress-blocked, and the session's web-search budget was exhausted, so no verifiable Cisco-Codex facts could be gathered. A builder-track Cisco CX case already exists (builder-11-cisco-cx.md). Satispay is row 24 of the same Track 2 list.

```yaml
org: Satispay
role: unknown (named: Fabio Rapposelli, CTO)
track: fleet
date: 2026-10-05
interviewer: desk
method: desk
harnesses_frameworks: [Claude Code, internal subagents, MCP servers]
domain: coding
runs_per_day: unknown (~20 requests a day from other departments after launch; issue-to-PR automation pilot running)
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
  last_change: internal subagents for reusable patterns (Java scaffolding, modernization approaches); MCP server for generating data-transformation Lambdas
  regression_detection: manual   # inferred: a 30-day head-to-head evaluation was run once, at tool selection
  silent_regression_experienced: unknown
  would_pay_to_prevent: unclear
controls_owned: [model_effort, budgets, mcp_servers]   # stated: budget-level spend management that "allows free model selection"; MCP servers; rollout via IT-managed device fleet
tooling_today: [Claude Code, subagents, MCP servers, managed device fleet (IT)]
coding_agent_traces_flow_to: unknown
can_reproduce_failed_run: unknown
has_compared_cohorts: yes   # stated: a 30-day evaluation comparing Claude Code against a competitor tool on code and reviews
most_wanted_question: ""
data_constraints:
  cannot_leave: [unknown]   # payments/fraud context; nothing public on agent telemetry
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: unknown   # spend is managed at budget level; owner not stated
credible_contract_size: unknown
automation_limits: "Agentic fraud investigation pilot keeps a human in the loop for decisions (stated). 'The model is an accelerator, not an authority.'"
would_allow_pause_stop_on_evidence: unknown
reaction:
  would_use_next_week: ""
  does_not_believe: ""
design_partner_candidate: unknown
referrals: []
quotes:
  - q: 21
    text: "The model is an accelerator, not an authority."
  - q: 9
    text: "We're moving to a model where the engineer becomes an engineering manager of agents."
  - q: 16
    text: "Claude Code's output, both the code it wrote and the reviews it produced, was considered best across the board."
sources:
  - https://claude.com/customers/satispay
tags:
  harnesses_frameworks: stated
  controls_owned: stated
  has_compared_cohorts: stated (tool selection only)
  regression_detection: inferred
  automation_limits: stated
  quotes: stated (fetched page via summarizer)
```

## Evidence
- 90% Claude Code adoption across engineering within 30 days. More than 75% of code committed each month is generated with Claude (https://claude.com/customers/satispay).
- Before rollout Satispay ran a 30-day evaluation of Claude Code against a competitor tool, comparing both the code written and the reviews produced (https://claude.com/customers/satispay).
- Spend is managed at budget level rather than per seat, which allows free model selection. IT ran the rollout through the managed device fleet (https://claude.com/customers/satispay).
- Internal subagents hold reusable patterns such as Java scaffolding and modernization approaches. An MCP server is used to generate data-transformation Lambdas, cutting them from 3–5 days to under an hour (https://claude.com/customers/satispay).
- A Java 8→21 plus major Spring upgrade of the core transaction service was done in under 4 days against a 4-week estimate (https://claude.com/customers/satispay).
- Pilots are running for issue-to-PR automation and for agentic fraud investigation with a human in the loop (https://claude.com/customers/satispay).
- AI proficiency was added to the engineering performance framework. The team skews toward earlier-career engineers working on a legacy Java/Spring codebase (https://claude.com/customers/satispay).
- About 6M consumers and 450k+ merchants. The page discloses no incidents, observability or data-residency rules (https://claude.com/customers/satispay).

## What this case says for Gate A
Satispay shows that a mid-size regulated fleet will run a structured, cohort-style comparison once, at tool selection, then govern by budget and managed settings. The question is whether that comparison discipline extends to ongoing harness changes (subagents, MCP servers, model choice under "free model selection"). The public story does not say. Budget-level spend with free model choice means model mix can shift without a deliberate decision, a plausible source of silent quality or cost change, but that is inference. The CTO's "accelerator, not an authority" stance and human-in-the-loop fraud pilot suggest openness to evidence-based gating. Nothing here counts toward the counters.
