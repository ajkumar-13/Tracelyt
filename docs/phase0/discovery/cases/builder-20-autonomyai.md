# AutonomyAI: coding agents (PydanticAI) that query their own Pydantic Logfire traces through the Logfire MCP server, during the build and again a day after merge, comparing intended against actual behaviour and filing their own tickets; in five weeks the loop caught 12 silent no-op deployments and 65 issues from real traffic, at about a third of the team's Datadog spend

evidence_grade: B

Access note (2026-10-05): the single primary source is Pydantic's customer case study "How AutonomyAI's agents catch their own regressions with Pydantic Logfire" (pydantic.dev, egress-blocked, reached through several search snippets), supported by Pydantic's Logfire MCP documentation. No AutonomyAI-authored engineering post was found. Grade B: a vendor-published case with concrete numbers and a described detection mechanism, but written by the observability vendor, with no root-cause times, no run volumes and no named incident beyond the aggregate counts.

```yaml
org: AutonomyAI
role: CTO / engineering (no individual named in the sources found)
track: builder
date: 2026-10-05
interviewer: desk
method: desk
harnesses_frameworks: [PydanticAI, Pydantic Logfire (OpenTelemetry-based, spans queryable as SQL), Logfire MCP server (agents query traces directly), "harness" model of a customer's brownfield codebase (components, design system, APIs, tests), Git-native workflows; previously Datadog]
domain: coding
runs_per_day: unknown
failure_definition: "Stated: a deployed change whose actual behaviour in production traces does not match intended behaviour, including 'silent no-op deployments' (change shipped, nothing changed)"
failure_rate_estimate: "12 silent no-op deployments and 65 issues surfaced from real traffic over five weeks (counts only; no denominator)"
cost_per_failed_run: unknown
last_failure:
  symptom: "Silent no-op deployments: code changes were merged and deployed but production traces showed no change in behaviour; found by agents re-querying Logfire 'a day later' and comparing intended against actual behavior"
  detected_by: dashboard
  time_to_why: "about one day from deploy to detection (the loop queries traces 'a day later'); root-cause time unknown"
  attributed_component: unknown
  recurred: yes
  their_words: "turning production telemetry into a feedback loop that files its own tickets"
harness_change:
  last_change: "Replaced Datadog with Logfire as agent-queryable observability; wired the Logfire MCP server into the agents so they debug their own code while building and review behaviour after merge"
  regression_detection: production_users
  silent_regression_experienced: yes
  would_pay_to_prevent: yes
controls_owned (fleets): [mcp_servers]
tooling_today: [Pydantic Logfire, Logfire MCP server, PydanticAI, ticket system fed by agents]
coding_agent_traces_flow_to: other (Logfire)
can_reproduce_failed_run: unknown
has_compared_cohorts: yes
most_wanted_question: "inferred: did the change I shipped actually change behaviour in production (intended vs actual)"
data_constraints:
  cannot_leave: unknown
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: ai_platform
credible_contract_size: "unknown; Logfire 'carries the workload at roughly a third of the team's Datadog spend' (Pydantic also states 'about 3.5x cheaper')"
automation_limits: "Agents file tickets rather than self-remediate in production (stated loop ends at ticket creation); code ships as 'merge-ready' PRs into customer codebases"
would_allow_pause_stop_on_evidence: unknown
reaction:
  would_use_next_week: unknown
  does_not_believe: unknown
design_partner_candidate: maybe
referrals: []
quotes:
  - q: 13
    text: "AutonomyAI's agents query Logfire directly through the MCP server to debug their own code while building and to review behavior after merge, turning production telemetry into a feedback loop that files its own tickets."
  - q: 1
    text: "Over five weeks the loop caught 12 silent no-op deployments and surfaced 65 issues from real traffic, and Logfire carries the workload at roughly a third of the team's Datadog spend."
  - q: 2
    text: "after a change ships, agents query real Logfire traces over the following days and compare intended behavior against actual behavior"
    paraphrase: true
sources:
  - https://pydantic.dev/case-studies/autonomyai
  - https://pydantic.dev/docs/ai/harness/logfire-mcp/
  - https://pydantic.dev/events/ask-your-traces
  - https://pydantic.dev/logfire/vs-datadog
  - https://autonomyai.io/business/which-ai-agents-can-handle-both-design-and-code-generation-for-web-apps/
tags:
  harnesses_frameworks: stated (case study: PydanticAI, Logfire, MCP server; AutonomyAI site for "harness" model of brownfield codebases)
  failure_definition: stated (case study)
  failure_rate_estimate: stated counts (case study)
  last_failure.symptom: stated (case study snippets)
  last_failure.detected_by: inferred (agents querying a trace store; closest template value is dashboard)
  last_failure.time_to_why: inferred from "a day later" detection; root-cause time not stated
  last_failure.attributed_component: unknown (the case study does not say why deployments were no-ops)
  last_failure.recurred: stated (12 instances in five weeks)
  harness_change.last_change: stated
  regression_detection: stated (post-deploy comparison of intended vs actual on production traces; no pre-merge gate described)
  silent_regression_experienced: stated ("silent no-op deployments")
  would_pay_to_prevent: inferred (they pay for Logfire specifically to catch regressions; the case study title is "catch their own regressions")
  coding_agent_traces_flow_to: stated (Logfire)
  has_compared_cohorts: inferred (intended vs actual comparison across days of traffic)
  design_partner_candidate: inferred (already operates the regression-detection loop and buys observability for it; a buyer who understands the category)
  budget_owner: inferred
  credible_contract_size: stated as relative cost only
```

## Evidence
- AutonomyAI "is an agentic operating system that lets product and design teams ship merge-ready code into existing brownfield codebases" and "runs Pydantic Logfire as agent-queryable AI observability" (https://pydantic.dev/case-studies/autonomyai).
- "Its agents query Logfire directly through the MCP server to debug their own code while building and to review behavior after merge, turning production telemetry into a feedback loop that files its own tickets" (https://pydantic.dev/case-studies/autonomyai).
- "Over five weeks the loop caught 12 silent no-op deployments and surfaced 65 issues from real traffic, and Logfire carries the workload at roughly a third of the team's Datadog spend" (https://pydantic.dev/case-studies/autonomyai).
- Detection mechanism: the no-op deployments "came from querying the traces again a day later and comparing intended against actual behavior after code changes were deployed"; "after a change ships, agents query real Logfire traces over the following days and compare intended behavior against actual behavior" (https://pydantic.dev/case-studies/autonomyai).
- Technical basis: Logfire is built on OpenTelemetry and "exposes span data as SQL", and the Logfire MCP server "giv[es] a coding agent direct query access to that data" (https://pydantic.dev/case-studies/autonomyai ; https://pydantic.dev/docs/ai/harness/logfire-mcp/).
- AutonomyAI builds a "harness", "a deep model of its components, design system, APIs, and tests, so the agent writes code the way the team's own engineers would" (https://autonomyai.io/business/which-ai-agents-can-handle-both-design-and-code-generation-for-web-apps/).
- Pydantic's own comparison page claims Logfire is "about 3.5x cheaper than Datadog" (https://pydantic.dev/logfire/vs-datadog).

## What this case says for Gate A
AutonomyAI is the one builder in this pass that already runs the exact loop we describe, in miniature: production traces are compared against the intent of a change, silent regressions are detected, and the finding becomes a ticket. The "12 silent no-op deployments" count is direct evidence that silent regressions happen often enough in agent-written code to justify a dedicated detector, and the fact that they moved off Datadog to get queryable traces shows willingness to pay and to change vendors for this capability. Two limits: the loop is post-deploy and agent-driven, not a pre-merge CI gate, and the source is the observability vendor, so adoption, cost and failure attribution are told from Logfire's side. This is a small company, so contract size is likely small, but as a design partner it is unusually well-qualified. Counts: silent_regression yes, attribution unknown, traces to Logfire (other), cannot_leave unknown.
