# Stripe: zero-config Claude Code for 1,370 engineers plus 1,300 unattended Minion PRs a week, governed by shared rule files, a central MCP server and a two-CI-round cap

evidence_grade: B

Primary sources exist (Anthropic customer story quoting Stripe's Developer Infrastructure lead; Stripe's own two-part "Minions" blog on stripe.dev), but they describe architecture and outcomes, not incidents. stripe.dev is egress-blocked, so Minions facts come from search snippets of the post and of InfoQ/ByteByteGo rewrites.

```yaml
org: Stripe
role: unknown (public: Scott MacVicar, Developer Infrastructure Team Lead)
track: fleet
date: 2026-10-05
interviewer: desk (no interview)
method: desk
harnesses_frameworks: [Claude Code (signed enterprise binary), Cursor, Minions (fork of Block's Goose), Toolshed MCP server (~400-500 tools), "six different coding assistants" enabled]
domain: coding
runs_per_day: "unknown per day; Minions >1,300 merged PRs per week (up from 1,000); Claude Code installed for 1,370 engineers"
failure_definition: "unknown; implicit: a Minion PR that does not pass CI within two rounds or is rejected in human review (inferred)"
failure_rate_estimate: unknown
cost_per_failed_run: unknown
last_failure:
  symptom: unknown (no public incident found)
  detected_by: unknown
  time_to_why: unknown
  attributed_component: unknown
  recurred: unknown
  their_words: ""
harness_change:
  last_change: "Rules authored in Cursor-compatible format with directory/file-pattern scoping, auto-synced for Claude Code so Minions, Cursor and Claude Code share one rule set; Claude Code shipped as a pre-configured signed binary"
  regression_detection: ci
  silent_regression_experienced: unknown
  would_pay_to_prevent: unknown
controls_owned (fleets): [rules_files, mcp_servers, tool_allowlists, ci_checks, budgets]
tooling_today: [Toolshed MCP server, devboxes (pre-warmed EC2), local lint on push (<5s), standard CI, human code review on every agent PR]
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
automation_limits: "Minions have submission authority but not merge authority; every agent PR is human-reviewed; max two CI rounds per task"
would_allow_pause_stop_on_evidence: unknown
reaction:
  would_use_next_week: unknown
  does_not_believe: unknown
design_partner_candidate: unknown
referrals: []
quotes:
  - q: 12
    text: "Claude Code is pre-installed on everyone's laptop. It just works out of the box."
  - q: 10
    text: "CI runs cost tokens, compute, and time, and there are diminishing marginal returns if an LLM is running against indefinitely many rounds of a full CI loop."
sources:
  - https://claude.com/customers/stripe
  - https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents
  - https://www.infoq.com/news/2026/03/stripe-autonomous-coding-agents/
  - https://blog.bytebytego.com/p/how-stripes-minions-ship-1300-prs
  - https://lilting.ch/en/articles/stripe-minions-agent-architecture
  - https://tenki.cloud/blog/agent-pr-volume-ci-scale
  - https://www.mintmcp.com/blog/stripe-minions-explained
  - https://www.zenml.io/llmops-database/ai-powered-developer-productivity-with-minions-and-machine-to-machine-payments
tags:
  harnesses_frameworks: stated
  runs_per_day: stated (weekly)
  failure_definition: inferred (from two-CI-round cap and mandatory review)
  harness_change.last_change: stated
  harness_change.regression_detection: inferred (CI and human review are the only stated gates)
  controls_owned: stated (rules, MCP/Toolshed, CI cap) / inferred (budgets, from the CI-rounds cost rationale)
  budget_owner: inferred (Developer Infrastructure team owns rollout)
  automation_limits: stated
  quotes: stated (first verbatim from claude.com fetch; second verbatim as quoted in tenki.cloud snippet of Stripe's post)
```

## Evidence

- Claude Code is used by 1,370 Stripe engineers in a zero-configuration rollout, pre-installed on laptops and devboxes, pre-configured with rules, tokens and auth (https://claude.com/customers/stripe).
- Stripe worked with Anthropic for 2-3 months to produce a signed enterprise binary, avoiding the npm dependency chain because of supply-chain risk (https://claude.com/customers/stripe).
- Developer Infrastructure enabled six different coding assistants rather than standardising on one (https://claude.com/customers/stripe).
- Stripe is exploring the Claude Agent SDK for incident detection and resolution, aiming above 5.5 nines (https://claude.com/customers/stripe).
- Minions are unattended, one-shot coding agents started from Slack; >1,300 PRs/week merged, all human-reviewed, no human-written code (https://www.infoq.com/news/2026/03/stripe-autonomous-coding-agents/; https://blog.bytebytego.com/p/how-stripes-minions-ship-1300-prs).
- Minions run in pre-warmed isolated devboxes, use a fork of Goose, reach ~500 internal tools through the central Toolshed MCP server, and use "blueprints" mixing deterministic code with agent loops (https://lilting.ch/en/articles/stripe-minions-agent-architecture; https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents).
- One rule set in Cursor format with directory/file-pattern scoping is shared by Minions, Cursor and Claude Code (auto-synced) (https://lilting.ch/en/articles/stripe-minions-agent-architecture).
- Minions are capped at two CI rounds per task for cost/diminishing-returns reasons; local lint runs on push in under five seconds (https://tenki.cloud/blog/agent-pr-volume-ci-scale; https://lilting.ch/en/articles/stripe-minions-agent-architecture).
- Agents have submission authority but not merge authority (https://www.mintmcp.com/blog/stripe-minions-explained).
- No public incident, cost blowout, or observability export of Claude Code traces found for Stripe (searches above returned none).

## What this case says for Gate A

Stripe shows a platform team that centrally owns the harness surface for a mixed fleet: one rules corpus shared across three agents, a single MCP server, a signed pre-configured Claude Code binary, and a hard CI-round budget. That is exactly the configuration surface a regression gate would sit on, and the shared rules file means one edit affects every agent at once. But there is no public evidence of a silent regression, of failure analysis tooling, or of where agent traces go, so the pain counters stay unknown. Stripe builds in-house (Minions, Toolshed, devboxes) and treats human review plus CI as the safety net; it would be a reference design rather than a likely early buyer.
