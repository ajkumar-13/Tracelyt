# Sentry (substitute for Citi): checked-in Claude Code permission allowlist, MCP allowlist and a company skills marketplace, with AGENTS.md as the single source of truth across Claude Code, Cursor and Copilot

evidence_grade: B

**Substitution note.** Track 2 row 10 (Citi) was replaced: its only cited evidence (American Banker) is egress-blocked and the web-search budget was exhausted, leaving nothing verifiable. Sentry publishes its closed-harness governance artifacts in public repos (getsentry/sentry, getsentry/skills), fetched directly from GitHub. Thin on incidents and fleet size. Caveat: Sentry also sells error and AI-agent monitoring (Seer, MCP server), so it is a possible competitor or partner as well as a fleet operator.

```yaml
org: Sentry (Functional Software)
role: unknown (public committers to .claude/settings.json include dcramer, evanpurkhiser, chromy, cvxluo, joshuarli)
track: fleet
date: 2026-10-05
interviewer: desk (no interview)
method: desk
harnesses_frameworks: [Claude Code, Cursor, GitHub Copilot, Cline (via skills.sh compatibility), Sentry MCP server, Linear MCP (claude.ai connector), sentry-skills plugin marketplace]
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
  last_change: "Apr 20, 2026: replace pre-commit with prek in Claude settings (#110808); Mar 12, 2026: allowlist read-only Linear MCP tools (#110474); Jan 2026: several commits widening the default Bash allowlist (git diff, gh repo view, pnpm typecheck, mypy) and adding a setup command"
  regression_detection: unknown
  silent_regression_experienced: unknown
  would_pay_to_prevent: unknown
controls_owned (fleets): [rules_files, permissions, tool_allowlists, mcp_servers, ci_checks]
tooling_today: [.claude/settings.json (allow-only list, ~100 entries, empty deny list), enabledMcpjsonServers [sentry], getsentry/skills marketplace (claude-settings-audit, code-review, find-bugs, iterate-pr, commit, deslop), prek lint/type hooks, CI check enforcing frontend/backend PR split]
coding_agent_traces_flow_to: unknown
can_reproduce_failed_run: unknown
has_compared_cohorts: unknown
most_wanted_question: unknown
data_constraints:
  cannot_leave: [customer_data]
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: dev_productivity
credible_contract_size: unknown
automation_limits: "Allowlist covers read-only git/gh/docker commands, lint/test/typecheck, read-only Sentry and Linear MCP tools, and WebFetch to a fixed set of docs domains; anything else prompts. Agents told never to include customer identifiers in PRs, commits or code."
would_allow_pause_stop_on_evidence: unknown
reaction:
  would_use_next_week: unknown
  does_not_believe: unknown
design_partner_candidate: unknown
referrals: []
quotes:
  - q: 12
    text: "AGENTS.md files are the source of truth for AI agent instructions. Always update the relevant AGENTS.md file when adding or modifying agent guidance. Do not add to CLAUDE.md or Cursor rules."
  - q: 18
    text: "Never include customer information in pull requests, commits, or code."
sources:
  - https://raw.githubusercontent.com/getsentry/sentry/master/.claude/settings.json
  - https://raw.githubusercontent.com/getsentry/sentry/master/AGENTS.md
  - https://raw.githubusercontent.com/getsentry/sentry/master/CLAUDE.md
  - https://github.com/getsentry/sentry/commits/master/.claude/settings.json
  - https://github.com/getsentry/skills
tags:
  harnesses_frameworks: stated (settings.json, AGENTS.md, skills README)
  harness_change.last_change: stated (commit history)
  controls_owned: stated
  tooling_today: stated
  cannot_leave: stated (AGENTS.md customer-information rule; applies to what agents write into git, not necessarily to telemetry)
  budget_owner: inferred ("dx(claude)" commit prefix suggests developer-experience ownership)
  automation_limits: stated
  quotes: stated (verbatim from raw files)
```

## Evidence

- `.claude/settings.json` in getsentry/sentry is an allow-only permission policy (~100 entries: read-only git/gh/docker, pytest/mypy/pnpm lint/test/typecheck, read-only Sentry and Linear MCP tools, sentry-skills skills, WebFetch to ~10 docs domains) with an empty deny list; `enableAllProjectMcpServers: true`, `enabledMcpjsonServers: ["sentry"]` (https://raw.githubusercontent.com/getsentry/sentry/master/.claude/settings.json).
- The settings file has 9 commits from Jul 24, 2025 to Apr 20, 2026, mostly "dx(claude): Allow claude to run X by default" widenings, plus "allowlist read-only Linear MCP tools" (https://github.com/getsentry/sentry/commits/master/.claude/settings.json).
- CLAUDE.md is a one-line include of AGENTS.md; AGENTS.md declares itself the single source of truth and forbids adding guidance to CLAUDE.md or Cursor rules (https://raw.githubusercontent.com/getsentry/sentry/master/CLAUDE.md; https://raw.githubusercontent.com/getsentry/sentry/master/AGENTS.md).
- AGENTS.md is split by area (backend, tests, frontend) with workflow steering moved into skills under `.agents/skills/` (https://raw.githubusercontent.com/getsentry/sentry/master/AGENTS.md).
- AGENTS.md tells agents to "always use `required_permissions: ['all']` for Python commands to avoid sandbox permission issues", a workaround that widens permissions to get past sandbox friction (https://raw.githubusercontent.com/getsentry/sentry/master/AGENTS.md).
- AGENTS.md: "Never include customer information in pull requests, commits, or code" (https://raw.githubusercontent.com/getsentry/sentry/master/AGENTS.md).
- getsentry/skills is a Claude Code plugin marketplace "for Sentry employees", including `claude-settings-audit` ("generate recommended Claude Code settings.json permissions"), `iterate-pr` (iterate until CI passes), and a `commit` skill marked "ALWAYS use"; also compatible with Cursor, Cline and Copilot via skills.sh (https://github.com/getsentry/skills).

## What this case says for Gate A

Sentry is a clean public example of who owns what in a mid-size fleet: developer experience owns a checked-in permission allowlist, MCP enablement and a skills marketplace; AGENTS.md is the one rules file shared across three vendor harnesses. The permission file only ever widens in its history, and there is even a skill to audit settings, which suggests that keeping permissions right is an ongoing manual chore. There is no public incident, telemetry or regression data, so pain counters stay unknown; the customer-information rule shows customer data is a hard constraint in at least one direction. As an observability vendor itself, Sentry is more likely a partner or competitor than a buyer.
