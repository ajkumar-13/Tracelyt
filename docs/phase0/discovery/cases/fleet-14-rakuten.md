# Rakuten: Claude Code for 7-hour autonomous runs plus Claude Managed Agents across functions, including a self-improving production-exception RCA agent

evidence_grade: C (two Anthropic-published customer stories with named Rakuten staff; marketing metrics with no stated methodology; no incident, governance or telemetry detail)

```yaml
org: Rakuten
role: unknown (named: Yusuke Kaji, GM AI for Business; Kenta Naruse, MLE; Tanapat Ratana, Applied AI Group; Shoko Sakamoto, PM for FinOps/cloud dashboards/observability)
track: fleet
date: 2026-10-05
interviewer: desk
method: desk
harnesses_frameworks: [Claude Code, Claude Managed Agents]
domain: coding   # also workflow: product, sales, marketing and finance agents
runs_per_day: unknown
failure_definition: unknown ("initial critical errors" is a reported metric but not defined)
failure_rate_estimate: unknown (pilot result "initial critical errors dropped by 97%", method undisclosed)
cost_per_failed_run: unknown
last_failure:
  symptom: unknown
  detected_by: unknown
  time_to_why: unknown
  attributed_component: unknown
  recurred: unknown
  their_words: ""
harness_change:
  last_change: unknown (agents with memory "remember what went wrong in past sessions"; the RCA agent "self-improves from feedback", so the harness changes continuously)
  regression_detection: unknown
  silent_regression_experienced: unknown
  would_pay_to_prevent: unclear
controls_owned: [unknown]   # agents run in sandboxed environments, per the case study
tooling_today: [Claude Code, Claude Managed Agents, Slack, Microsoft Teams, internal Kanban-style task system]
coding_agent_traces_flow_to: unknown
can_reproduce_failed_run: unknown
has_compared_cohorts: unknown
most_wanted_question: ""
data_constraints:
  cannot_leave: [unknown]
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: ai_platform   # inferred from "GM of AI for Business" and "AI Empowerment Section" owning the rollout
credible_contract_size: unknown
automation_limits: "We delegate goals, not tasks" (stated philosophy; no stated limits)
would_allow_pause_stop_on_evidence: unknown
reaction:
  would_use_next_week: ""
  does_not_believe: ""
design_partner_candidate: unknown
referrals: []
quotes:
  - q: 9
    text: "You can have five tasks running in parallel by delegating four to Claude Code"
  - q: 9
    text: "We delegate goals, not tasks"
  - q: 10
    text: "Individual learning becomes organizational learning instantly"
sources:
  - https://claude.com/customers/rakuten
  - https://claude.com/customers/rakuten-qa
tags:
  harnesses_frameworks: stated
  harness_change.last_change: stated (memory and feedback loops), inferred (that this means continuous harness change)
  budget_owner: inferred
  quotes: stated (fetched pages)
```

## Evidence
- Claude Code ran for 7 hours autonomously on activation-vector extraction in vLLM, a 12.5M-line multi-language open-source codebase, and reached a reported 99.9% numerical accuracy (https://claude.com/customers/rakuten).
- Rakuten reports a 79% cut in time to market, from 24 days to 5 (https://claude.com/customers/rakuten).
- Specialist agents went live across product, sales, marketing and finance within a week. They are wired into Slack, Teams and a custom Kanban-style task system and run in sandboxed environments (https://claude.com/customers/rakuten ; https://claude.com/customers/rakuten-qa).
- Tanapat Ratana built an agent that "investigates production exceptions, delivers root cause analysis to Slack, and self-improves from feedback". It was distributed so non-engineers can set it up on their own products (https://claude.com/customers/rakuten-qa).
- Agents with memory "remember what went wrong in past sessions and avoid repeating those mistakes" (https://claude.com/customers/rakuten-qa).
- Pilot result: "initial critical errors dropped by 97%, with cost and latency down more than 30%". The page gives no methodology (https://claude.com/customers/rakuten-qa).
- Major releases moved from quarterly to biweekly (https://claude.com/customers/rakuten-qa).
- Neither page names an observability stack, evaluation, testing, permission model or cost control (https://claude.com/customers/rakuten-qa).

## What this case says for Gate A
Rakuten is a heavy user of long-running and self-modifying agents: multi-hour runs, cross-session memory, and an RCA agent whose behaviour changes from feedback. Those are exactly the conditions where silent harness drift is likely and where a flight recorder plus regression gate would matter. The public record is pure vendor marketing, though. It shows no incident, no telemetry destination, no data constraint and no governance owner, so it adds nothing to the counters. Ironically, Rakuten has itself built an agent that does incident RCA into Slack, which hints at appetite but also at a build-it-yourself reflex. Worth a live conversation (Shoko Sakamoto's FinOps/observability role is the closest persona). Evidence is weak.
