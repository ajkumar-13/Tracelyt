# Ramp: owns "Inspect", an OpenCode-based background agent on Modal sandboxes; public record found this pass is thin on failures and gating

evidence_grade: C

Access note: Ramp's primary post (https://builders.ramp.com/post/why-we-built-our-background-agent), the Modal write-up and Zach Bruggeman's posts were all blocked by the egress proxy, and the session's web-search budget was used up before this case. Facts below come from (a) Anthropic's Ramp case study, fetched directly, and (b) the target-list entry, carried forward without re-checking. No substitute was made: public evidence exists, but this pass could not reach it. Re-run this case when search is available.

```yaml
org: Ramp
role: Background-agent / DevEx (public: Zach Bruggeman)
track: builder
date: 2026-10-05
interviewer: desk
method: desk
harnesses_frameworks: [Inspect (built on OpenCode), Modal sandboxes, Cloudflare, Claude Code, MCP servers]
domain: coding
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
controls_owned (fleets): [mcp_servers]
tooling_today: [Datadog, Sentry, Snowflake (as data sources agents read via MCP)]
coding_agent_traces_flow_to: unknown
can_reproduce_failed_run: unknown
has_compared_cohorts: unknown
most_wanted_question: unknown
data_constraints:
  cannot_leave: unknown
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: dev_productivity
credible_contract_size: unknown
automation_limits: unknown
would_allow_pause_stop_on_evidence: unknown
reaction:
  would_use_next_week: unknown
  does_not_believe: unknown
design_partner_candidate: unknown
referrals: [Zach Bruggeman]
quotes:
  - q: 1
    text: "1+ million lines of AI-suggested code implemented in just 30 days"
sources:
  - https://claude.com/customers/ramp
  - https://builders.ramp.com/post/why-we-built-our-background-agent
  - https://x.com/zachbruggeman/status/2010728444771074493
  - https://github.com/ColeMurray/background-agents
tags:
  harnesses_frameworks: carried from 09-interview-targets.md (Inspect/OpenCode/Modal/Cloudflare), not re-verified; Claude Code + MCP stated (claude.com)
  share_of_merged_prs_30_40pct: carried, not re-verified
  tooling_today: stated (claude.com case study: Claude Code connected to Datadog, Sentry, Snowflake via MCP)
  budget_owner: inferred
```

## Evidence
- Ramp built internal incident-response tooling that connects Claude Code to its observability stack (Datadog, Sentry) through MCP; reports "up to 80% reduction in incident investigation time" (https://claude.com/customers/ramp).
- "1+ million lines of AI-suggested code implemented in just 30 days"; 50% weekly active usage of Claude Code across engineering (https://claude.com/customers/ramp).
- Ticket-to-code automation connects project management systems to Claude Code (https://claude.com/customers/ramp).
- Open-Inspect, an open-source clone, says its architecture "follows Ramp's Inspect design, which was built for internal use where all employees are trusted and have access to company repositories" (https://github.com/ColeMurray/background-agents).
- Carried, not re-verified: Inspect is built on OpenCode with Modal sandboxes and Cloudflare, and writes 30-40% of merged PRs (https://builders.ramp.com/post/why-we-built-our-background-agent ; https://x.com/zachbruggeman/status/2010728444771074493).

## What this case says for Gate A
Nothing countable. Ramp owns an open-source-based harness that writes a large share of PRs, which makes it a strong shape for harness-change gating. But this pass found no public failure, regression or trace-destination evidence. Datadog and Sentry show up here as data sources the agent reads, not as places where agent traces go. Re-run this case with web search before it counts toward Gate A.
