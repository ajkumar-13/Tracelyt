# Stripe: Minions (forked goose + deterministic blueprints) merge 1,300+ PRs/week; failure handled by structure (2 CI rounds, human review), not by measurement

evidence_grade: B

Primary sources: stripe.dev Minions Part 1/2 posts (Steve Kaliski, Alistair Gray), Alistair Gray's Background Agents Summit talk, Anthropic's Stripe case study. stripe.dev is blocked to direct fetch; facts come from search snippets of those posts and faithful secondary summaries. No public incident narrative or success-rate number exists.

```yaml
org: Stripe
role: Developer Infrastructure / Minions (public: Alistair Gray, Steve Kaliski, Scott MacVicar)
track: builder
date: 2026-10-05
interviewer: desk
method: desk
harnesses_frameworks: [Minions (fork of Block goose, late 2024), Blueprints (deterministic + agentic nodes), Toolshed (central MCP server, ~400-500 tools), Devbox, Claude Code (1,370 engineers), Cursor]
domain: coding
runs_per_day: "unknown runs; 1,300+ merged PRs/week (~185/day merged) as of Feb 2026"
failure_definition: "inferred: build not green after 2 CI rounds -> escalate to human; PR not merged"
failure_rate_estimate: unknown (Stripe has not published a success rate)
cost_per_failed_run: unknown
last_failure:
  symptom: unknown (no specific public incident). Recurring classes named: agent cannot fix failing CI within two rounds; context overload when exposing all tools; global rules not working in a huge codebase.
  detected_by: ci
  time_to_why: unknown
  attributed_component: unknown
  recurred: unknown
  their_words: "Agent quality is a dev infrastructure problem."
harness_change:
  last_change: "Fork of goose stripped of human-in-the-loop features (interruptibility, confirmation prompts); conditional subdirectory rule files; curated per-task tool subset (~15) from Toolshed; CI capped at two rounds"
  regression_detection: inferred manual + ci (human review of every PR and normal CI; no public harness-change eval gate)
  silent_regression_experienced: unknown
  would_pay_to_prevent: unknown
controls_owned (fleets): [rules_files, mcp_servers, tool_allowlists, ci_checks]
tooling_today: [Toolshed MCP server, Sourcegraph code search, Devbox, standard CI/linters]
coding_agent_traces_flow_to: unknown
can_reproduce_failed_run: partially (inferred: reproducible pre-warmed devboxes make environment re-creation possible; no stated replay of agent runs)
has_compared_cohorts: unknown
most_wanted_question: unknown
data_constraints:
  cannot_leave: [code]
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: dev_productivity
credible_contract_size: unknown
automation_limits: "Every PR is human-reviewed; max two CI rounds before handing to a human; Claude Code deployed only as a signed enterprise binary to avoid npm supply-chain risk"
would_allow_pause_stop_on_evidence: unknown
reaction:
  would_use_next_week: unknown
  does_not_believe: unknown
design_partner_candidate: unknown
referrals: [Alistair Gray, Steve Kaliski, Scott MacVicar]
quotes:
  - q: 1
    text: "Dev boxes were a strategy credit"
  - q: 2
    text: "People think it is a replacement for themselves and then don't quite give it the right amount of context"
sources:
  - https://background-agents.com/summit/sessions/alistair-gray/
  - https://ona.com/stories/background-agents-summit
  - https://x.com/ona_hq/status/2050286794789339165
  - https://www.engineering.fyi/article/minions-stripe-s-one-shot-end-to-end-coding-agents-part-2
  - https://blog.bytebytego.com/p/how-stripes-minions-ship-1300-prs
  - https://lilting.ch/en/articles/stripe-minions-agent-architecture
  - https://www.mintmcp.com/blog/stripe-minions-explained
  - https://dotzlaw.com/insights/ai-04-stripe-minions-deterministic-rails/
  - https://claude.com/customers/stripe
tags:
  runs_per_day: stated (PR count); run count unknown
  failure_definition: inferred (from the two-CI-round escalation rule)
  detected_by: inferred (CI is the stated feedback loop)
  harness_change.last_change: stated
  regression_detection: inferred
  can_reproduce_failed_run: inferred
  cannot_leave: inferred (signed-binary, supply-chain posture and internal devboxes; not an explicit statement)
  budget_owner: inferred (Developer Infrastructure owns Minions)
```

## Evidence
- Minions merge 1,300+ PRs per week with humans reviewing but writing none of the code (https://www.engineering.fyi/article/minions-stripe-s-one-shot-end-to-end-coding-agents-part-2 ; https://blog.bytebytego.com/p/how-stripes-minions-ship-1300-prs).
- Built on a fork of Block's goose (late 2024); customization removed features that assume a human is watching: interruptibility, human-triggered commands, confirmation prompts (https://lilting.ch/en/articles/stripe-minions-agent-architecture).
- Blueprints mix agentic loops with deterministic nodes that run tests and enforce CI policy rather than asking the model (https://dotzlaw.com/insights/ai-04-stripe-minions-deterministic-rails/).
- At most two CI rounds before the task surfaces to a human; justified by diminishing returns of retries (https://dotzlaw.com/insights/ai-04-stripe-minions-deterministic-rails/ ; https://www.sitepoint.com/stripe-minions-architecture-explained/).
- Toolshed central MCP server exposes ~400-500 internal tools, but Minions get a small curated per-task subset because agents do better with fewer tools (https://www.mintmcp.com/blog/stripe-minions-explained ; https://www.engineering.fyi/article/minions-stripe-s-one-shot-end-to-end-coding-agents-part-2).
- Global agent rules did not work in the codebase; Stripe uses subdirectory-conditional rule files shared with Cursor and Claude Code (https://lilting.ch/en/articles/stripe-minions-agent-architecture).
- Alistair Gray: agent quality is a dev-infrastructure problem; 30M-line Ruby codebase; runs start from Slack, Jira or web UI (https://background-agents.com/summit/sessions/alistair-gray/ ; https://ona.com/stories/background-agents-summit).
- Stripe has not published Minion success-rate metrics (secondary analysis) (https://www.sitepoint.com/stripe-minions-architecture-explained/).
- Claude Code rollout to 1,370 engineers required 2-3 months building a signed enterprise binary to avoid npm supply-chain risk (https://claude.com/customers/stripe).

## What this case says for Gate A
Stripe owns every harness layer we target (forked agent loop, rule files, tool subset selection, CI policy), so harness changes are frequent and real. But its public posture is "control failure by structure": deterministic nodes, a hard two-round retry cap and mandatory human review absorb failures, and nothing public describes a silent regression, a trace store or a replay need. The absence of any published success rate is itself notable: either they measure it privately or the PR-merge count is the metric. It is a strong interview target for first-divergence and attribution, but the desk evidence does not count toward the pain or replay counters.
