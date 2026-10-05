# Brex: Claude Code rollout from 50% to 100%, with per-directory CLAUDE.md in a Kotlin/Bazel monorepo and a CI check that flags stale docs

evidence_grade: C (one Anthropic-published story, Oct 30, 2025, with named Brex staff; thin on governance and silent on failures; no further evidence because the session's web-search budget ran out after this case was assigned)

```yaml
org: Brex
role: unknown (named: Hércules Gimenes, SWE Lead, Product AI team; Sumeet Marwaha, Head of Data & Analytics; Andy Reed, Senior Content Designer)
track: fleet
date: 2026-10-05
interviewer: desk
method: desk
harnesses_frameworks: [Claude Code (interactive and headless), MCP servers]
domain: coding
runs_per_day: unknown
failure_definition: unknown
failure_rate_estimate: unknown ("94% compliance rate vs 70% industry standard" appears in the header with the metric undefined)
cost_per_failed_run: unknown
last_failure:
  symptom: unknown
  detected_by: unknown
  time_to_why: unknown
  attributed_component: unknown
  recurred: unknown
  their_words: ""
harness_change:
  last_change: CLAUDE.md added to each major monorepo directory; custom slash commands (e.g. /submit-pr) that preload git status, recent changes and related PR data
  regression_detection: unknown   # the CI check covers docs drift, not agent behaviour
  silent_regression_experienced: unknown
  would_pay_to_prevent: unclear
controls_owned: [rules_files, mcp_servers, ci_checks]   # stated: per-directory CLAUDE.md, MCP servers (Brex Explorer), CI docs-drift check; owner team inferred to be Product AI
tooling_today: [Claude Code, MCP servers, Brex Explorer (text-to-SQL via Claude Code + MCP), headless submission agent, AI data engineering agent]
coding_agent_traces_flow_to: unknown
can_reproduce_failed_run: unknown
has_compared_cohorts: unknown
most_wanted_question: ""
data_constraints:
  cannot_leave: [unknown]   # fintech (card network, banking regulation context is in CLAUDE.md) but no stated constraint on agent telemetry
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: unknown   # possibly the Product AI team (inferred, weak)
credible_contract_size: unknown
automation_limits: "Instead of being in the driver's seat, you're the reviewer of the changes that Claude introduces."
would_allow_pause_stop_on_evidence: unknown
reaction:
  would_use_next_week: ""
  does_not_believe: ""
design_partner_candidate: unknown
referrals: []
quotes:
  - q: 9
    text: "Having up-to-date documentation is something you can trust—it's so powerful"
  - q: 9
    text: "Instead of being in the driver's seat, you're the reviewer of the changes that Claude introduces. You're guiding the vision and direction."
sources:
  - https://claude.com/blog/how-brex-improves-code-quality-and-productivity-with-claude-code
tags:
  harnesses_frameworks: stated
  harness_change.last_change: stated
  controls_owned: stated (artifacts); inferred (ownership)
  automation_limits: stated
  quotes: stated (fetched page via summarizer; treat as near-verbatim)
```

## Evidence
- Brex reported 50% Claude Code adoption, with a goal of 100% by the end of the month (https://claude.com/blog/how-brex-improves-code-quality-and-productivity-with-claude-code).
- "Each major directory in the monorepo now has its own CLAUDE.md file containing domain-specific context." This replaces tribal knowledge about the Mastercard integration and banking regulations (same URL).
- "The Product AI team implemented CI/CD checks that verify when code changes might outdate documentation, prompting updates." Since that documentation is also agent context, this works as a freshness gate on part of the harness (same URL; the context link is inferred).
- Custom commands such as /submit-pr fetch git status, recent changes and related PR data automatically (same URL).
- Headless mode was used to build a "sophisticated submission agent in just a few hours". An "AI data engineering agent" lets any engineer add data tables with the needed file edits and test configs (same URL).
- Brex Explorer is a text-to-SQL interface built on Claude Code plus MCP servers (same URL).
- 3–4x productivity on specific tasks. "94% compliance rate vs 70% industry standard" is quoted with no definition (same URL).
- The article says nothing about security, permissions, cost, failures or rollout mechanics (same URL).

## What this case says for Gate A
Brex shows a pattern we expect in most fleets: the harness that matters is a tree of CLAUDE.md files plus slash commands and MCP servers. A small platform-ish team (Product AI) owns it, and the only automated check covers documentation drift, not agent behaviour. This is the exact gap a "gate rules-file changes against past failures" product targets. It is circumstantial, though: nothing public says a CLAUDE.md change ever regressed anything. All pain counters stay unknown. As a regulated fintech Brex is a plausible live interview, and the headless agents move it toward the builder track.
