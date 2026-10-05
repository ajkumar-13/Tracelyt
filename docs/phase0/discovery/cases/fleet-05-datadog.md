# Datadog (substitute for Monzo): AI Developer Experience team gates every fleet-wide Claude Code default (model, effort, context compression, AGENTS.md) on 140+ nightly agent evals and A/B cohorts

evidence_grade: A

**Substitution note.** Track 2 row 5 (Monzo) was replaced: the only Monzo evidence is a background-agents summit session page and an Ona recap, both egress-blocked, and the session's web-search budget was exhausted before Monzo could be researched through snippets. Datadog is Track 2 row 20 in 09-interview-targets.md and publishes first-party, specific posts on how it governs its own coding-agent fleet (datadoghq.com is fetchable). Caveat: Datadog sells LLM/Agent Observability, so these posts double as product marketing and Datadog is a likely competitor as well as a reference.

**Overlap note.** fleet-20-datadog.md (another agent) covers Datadog as a product vendor and states no public source describes Datadog's internal governance; the three datadoghq.com posts cited here are that source. Count Datadog once in the tallies; this file is the fleet-operator view.

```yaml
org: Datadog
role: unknown (posts are by Datadog's AI Developer Experience team and the "Frontend Augmented by AI" guild)
track: fleet
date: 2026-10-05
interviewer: desk (no interview)
method: desk
harnesses_frameworks: [Claude Code (CLI), Cursor, OpenAI, Anthropic API, internal AI Gateway, Datadog agent skills, Headroom (tool-output compression)]
domain: coding
runs_per_day: unknown (A/B test sample "over 1,000 engineers"; a cost alert reached 768 distinct users in its first week; 50+ dev teams use the frontend golden paths)
failure_definition: "Eval-defined: weighted deterministic + LLM-judge score on Datadog-specific tasks, plus cost, duration and run-to-run consistency"
failure_rate_estimate: unknown
cost_per_failed_run: unknown
last_failure:
  symptom: "During a routine rolling deployment of the internal AI Gateway, the graceful-shutdown period was too short for in-flight agent requests, which increased request timeouts until it was extended"
  detected_by: dashboard
  time_to_why: unknown
  attributed_component: environment
  recurred: unknown
  their_words: "Its graceful shutdown period was too short for in-flight agent requests to complete, which increased the number of request timeouts until we extended it appropriately."
harness_change:
  last_change: "Oct 2026: default Claude Code model switched from Sonnet 5 to Opus 5.5 after nightly evals showed about half the cost per run and faster completion; earlier: Opus 4.8 -> Sonnet 4.6 default (8% proficiency loss accepted for 36.7% lower cost, ~$687K/month saved); Claude Code CLI default effort high -> medium (~$288K/month); Headroom tool-output compression piloted (-27% cost/user); root AGENTS.md removed from shared frontend repo after eval"
  regression_detection: evals
  silent_regression_experienced: unknown
  would_pay_to_prevent: unknown
controls_owned (fleets): [rules_files, hooks, model_effort, budgets, ci_checks, tool_allowlists]
tooling_today: [Datadog Agent Observability (traces per gateway request: user, team, model, tokens, cost), Agent Observability Experiments (eval runs, trajectories, run comparison), Cloud Cost Management AI Costs, Cost monitors + Workflow Automation Slack nudges, AI Guard (blocks tool calls on policy), internal AI Gateway]
coding_agent_traces_flow_to: datadog
can_reproduce_failed_run: partially
has_compared_cohorts: yes
most_wanted_question: unknown
data_constraints:
  cannot_leave: unknown
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: dev_productivity
credible_contract_size: unknown
automation_limits: "Deterministic gates (tests, security scans, approvals, merge permissions) decide whether agent output progresses; the agent can revise but cannot override them. AI Guard can stop a tool call before it executes."
would_allow_pause_stop_on_evidence: yes
reaction:
  would_use_next_week: unknown
  does_not_believe: unknown
design_partner_candidate: no
referrals: []
quotes:
  - q: 10
    text: "We didn't need to measure the engineering capability of different agents and models on standard engineering tasks. Rather, we needed to measure an agent's ability to work on Datadog engineering tasks."
  - q: 10
    text: "Teams often need to update controls as models shift, codebases change, and new best practices supplant existing ones."
  - q: 1
    text: "Its graceful shutdown period was too short for in-flight agent requests to complete, which increased the number of request timeouts until we extended it appropriately."
sources:
  - https://www.datadoghq.com/blog/how-datadog-saves-money-by-optimizing-ai-usage/
  - https://www.datadoghq.com/blog/ai-development-golden-paths/
  - https://www.datadoghq.com/blog/golden-paths-for-ai-agents/
  - https://www.datadoghq.com/blog/claude-code-monitoring/
tags:
  harnesses_frameworks: stated
  runs_per_day: stated (cohort sizes only)
  failure_definition: stated (weighted deterministic + LLM scores, consistency score)
  last_failure: stated (golden-paths-for-ai-agents post)
  last_failure.detected_by: inferred (timeouts observed in monitoring; post does not say how)
  harness_change.last_change: stated (all figures from the cost post, including Oct 2026 editor's note)
  harness_change.regression_detection: stated
  controls_owned: stated (AGENTS.md, skills, hooks, lint/tests, model default, effort, cost alerts) / inferred (tool allowlists via AI Guard)
  coding_agent_traces_flow_to: stated ("Every Claude Code request is run through an AI gateway ... The gateway sends a trace of each request to Agent Observability")
  can_reproduce_failed_run: inferred (eval runs store trajectories and support comparison; production replay not described)
  has_compared_cohorts: stated (A/B of Headroom over 1,000+ engineers; AGENTS.md branch vs control)
  budget_owner: inferred (AI Developer Experience team)
  would_allow_pause_stop_on_evidence: stated (AI Guard blocking; cost-alert workflows)
  design_partner_candidate: inferred (Datadog sells the competing product)
```

## Evidence

- Every Claude Code request goes through an internal AI gateway that tags team/product; the gateway sends a trace per request (user, team, model, tokens, estimated cost) to Datadog Agent Observability; the AI Developer Experience team watches a cost dashboard across Anthropic, Cursor and OpenAI (https://www.datadoghq.com/blog/how-datadog-saves-money-by-optimizing-ai-usage/).
- The AI DevEx team built a self-service agentic evaluation platform; 140+ evals run nightly, scored by weighted deterministic + LLM checks, published to Agent Observability Experiments with trajectories and run comparison (https://www.datadoghq.com/blog/how-datadog-saves-money-by-optimizing-ai-usage/).
- Default model change Opus 4.8 -> Sonnet 4.6 was gated on those evals: an 8% loss in proficiency on Datadog workflows accepted for 36.7% lower cost; ~$687K saved in a month (https://www.datadoghq.com/blog/how-datadog-saves-money-by-optimizing-ai-usage/).
- Claude Code CLI default effort changed high -> medium using the same method: >$288K/month saved (https://www.datadoghq.com/blog/how-datadog-saves-money-by-optimizing-ai-usage/).
- October 2026 editor's note: after adding Opus 5.5 to nightly evals it cost about half as much per run as Sonnet 5 and was faster, so the Claude Code default was switched to Opus 5.5 (https://www.datadoghq.com/blog/how-datadog-saves-money-by-optimizing-ai-usage/).
- Headroom tool-output compression: 47% cost reduction in evals, then A/B over 1,000+ engineers showed -27% cost/user, -39% input tokens (https://www.datadoghq.com/blog/how-datadog-saves-money-by-optimizing-ai-usage/).
- Cost monitors + Workflow Automation DM users who cross spend thresholds; first week reached 768 users and cut >$150K in spend week over week (https://www.datadoghq.com/blog/how-datadog-saves-money-by-optimizing-ai-usage/).
- Frontend guild (50+ teams) tested removing a bloated root AGENTS.md against a control branch: 13% faster runs, 16% fewer input tokens, 10% lower spend, but ~7% lower consistency; changes ship only after multiple runs beat baseline, then are watched on a live score/cost/duration dashboard (https://www.datadoghq.com/blog/ai-development-golden-paths/).
- The guild states controls (skills, hooks, tests, AGENTS.md) need owners with "monitoring data, visualizations, and alerts" because models and codebases change (https://www.datadoghq.com/blog/ai-development-golden-paths/).
- Incident: a rolling deploy of the internal AI Gateway had too short a graceful-shutdown window for in-flight agent requests, raising timeouts until extended (https://www.datadoghq.com/blog/golden-paths-for-ai-agents/).
- Datadog AI Guard evaluates prompts, responses and tool calls and can block a tool call before execution (https://www.datadoghq.com/blog/golden-paths-for-ai-agents/).

## What this case says for Gate A

Datadog is the most complete public example of a fleet operator already doing what the regression gate proposes: centrally owned Claude Code defaults (model, effort, rules files, context compression) changed only after nightly eval runs and A/B cohorts, with traces of every request in an observability backend. That validates the problem and the workflow: they accepted a measured 8% quality loss for cost, and they track consistency drift when rules files change. It also shows the bar: a serious fleet operator expects eval-gated harness changes, cohort comparison and per-request traces, and Datadog sells those pieces as a product. No silent regression is reported, because their method is designed to make regressions visible. For Gate A this is evidence of demand for the workflow and evidence of a strong incumbent in it, not a design-partner lead.
