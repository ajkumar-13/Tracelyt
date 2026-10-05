# Elastic (substitute for Salesforce): Kibana's Claude Code reviewer ran past its 20-minute timeout because its time-budget hook silently lost its executable bit; hooks also block agents from publishing PR reviews

evidence_grade: A

**Substitution note.** Track 2 row 8 (Salesforce) was replaced: its only evidence (cursor.com customer topic page) is egress-blocked and the web-search budget was exhausted. (Doctolib was considered but is already covered as fleet-18 by another agent.) Elastic runs Claude Code and Cursor across the public elastic/kibana repo, and its hook scripts, settings and the PRs that changed them are primary evidence fetched from GitHub. Fleet size is not public.

```yaml
org: Elastic (elastic/kibana)
role: unknown (public: PR authors Ikuni17, kapral18)
track: fleet
date: 2026-10-05
interviewer: desk (no interview)
method: desk
harnesses_frameworks: [Claude Code (interactive + "reviewerclaude" GitHub Agentic Workflow), Cursor (cursor agent co-authors PRs; shared hooks under .cursor/hooks), GitHub Agentic Workflows (gh-aw), kbn-github skill, GitHub MCP (discouraged)]
domain: coding
runs_per_day: unknown (Claude reviewer enabled by default on Kibana PRs in PR #274743, mid-2026)
failure_definition: "Reviewer exceeds its 20-minute agent timeout without producing a review; review posted with wrong classification; agent publishes a PR review without a separate submission step"
failure_rate_estimate: unknown
cost_per_failed_run: unknown
last_failure:
  symptom: "After the Claude reviewer was enabled by default, it hit the 20-minute agent timeout; a time-budget hook was added, but it did not fire because restoring .claude from GitHub artifacts dropped the executable bit (0644 instead of 0755), producing 'Permission denied'; the reviewer also wandered across the repo instead of staying on changed files"
  detected_by: ci
  time_to_why: "days (fix #275661 merged Jul 6, 2026; hook not firing fixed in #277053 merged Jul 10, 2026)"
  attributed_component: environment
  recurred: yes
  their_words: "wandering across the repo"
harness_change:
  last_change: "Jul 10, 2026: run time-budget hook via node (read-only permission suffices) and scope verification to changed files plus direct imports (#277053)"
  regression_detection: manual
  silent_regression_experienced: yes
  would_pay_to_prevent: unknown
controls_owned (fleets): [hooks, permissions, tool_allowlists, mcp_servers, budgets, ci_checks, rules_files]
tooling_today: [.claude/settings.json hooks (PreToolUse, PostToolBatch), shared .agents/hooks analyzers reused by Cursor wrappers, kbn-github skill, AGENTS.md human-in-the-loop publication gate, GitHub Agentic Workflows]
coding_agent_traces_flow_to: unknown
can_reproduce_failed_run: partially
has_compared_cohorts: no
most_wanted_question: unknown
data_constraints:
  cannot_leave: unknown
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: unknown
credible_contract_size: unknown
automation_limits: "Agents may not publish PR reviews (approve / request changes / comment) in one step; reviews must be created PENDING and submitted separately; human-in-the-loop publication gate in AGENTS.md"
would_allow_pause_stop_on_evidence: yes
reaction:
  would_use_next_week: unknown
  does_not_believe: unknown
design_partner_candidate: unknown
referrals: []
quotes:
  - q: 21
    text: "Keeps PR review *creation* in PENDING so a review is never published without an explicit, separate submission step."
  - q: 21
    text: "BEST-EFFORT and intentionally minimal. It catches the *accidental* publish a cooperating agent would actually type — nothing more. It is deny-only and fails OPEN"
  - q: 9
    text: "WARNING: A GitHub MCP server is active, which adds ~50k tokens of overhead per session."
sources:
  - https://raw.githubusercontent.com/elastic/kibana/main/.claude/settings.json
  - https://raw.githubusercontent.com/elastic/kibana/main/.claude/hooks/reviewer_time_budget.mjs
  - https://raw.githubusercontent.com/elastic/kibana/main/.claude/hooks/warn-github-mcp.mjs
  - https://raw.githubusercontent.com/elastic/kibana/main/.claude/hooks/strip-review-event.mjs
  - https://raw.githubusercontent.com/elastic/kibana/main/.agents/hooks/strip-review-event.mjs
  - https://github.com/elastic/kibana/commits/main/.claude/settings.json
  - https://github.com/elastic/kibana/pull/275661
  - https://github.com/elastic/kibana/pull/277053
tags:
  harnesses_frameworks: stated (settings, hook headers, commit co-authors)
  failure_definition: inferred (from the problems the PRs fix)
  last_failure.symptom: stated (PR #275661 and #277053 descriptions as returned by fetch)
  last_failure.detected_by: inferred (reviewer runs in CI via GitHub Agentic Workflows; failures observed there)
  last_failure.time_to_why: inferred (from merge dates)
  last_failure.attributed_component: inferred (artifact restore dropped file mode = environment; scope drift = prompt/guardrails)
  last_failure.recurred: inferred (timeout persisted after first fix because the hook never ran)
  silent_regression_experienced: inferred (the guardrail hook failed silently for days; the fix PR had to verify "10/10 PostToolBatch hook invocations succeeded")
  controls_owned: stated
  can_reproduce_failed_run: inferred ("Ran the new Claude hook locally ... Force review mode with env variables")
  automation_limits: stated (hook header comment)
  would_allow_pause_stop_on_evidence: stated (time-budget hook tells the agent "Stop all work now and produce a review output" at 85%)
  quotes: stated (verbatim from raw hook files)
```

## Evidence

- Kibana's `.claude/settings.json` registers three hooks: PreToolUse on `mcp__github.*` (warn), PreToolUse on `Bash(gh *)` (strip-review-event), PostToolBatch (reviewer_time_budget) (https://raw.githubusercontent.com/elastic/kibana/main/.claude/settings.json).
- The GitHub-MCP hook warns that an active GitHub MCP server "adds ~50k tokens of overhead per session" and points to an in-repo gh-based skill instead (https://raw.githubusercontent.com/elastic/kibana/main/.claude/hooks/warn-github-mcp.mjs).
- The strip-review-event policy is shared by Claude Code and Cursor wrappers; it denies `gh pr review --approve/--request-changes/--comment` and inline-body review creation so reviews stay PENDING; it is explicitly "deny-only and fails OPEN", with shell evasions listed as won't-fix (https://raw.githubusercontent.com/elastic/kibana/main/.agents/hooks/strip-review-event.mjs).
- The time-budget hook only runs inside the `reviewerclaude` GitHub Agentic Workflow, has a 20-minute limit, injects milestone messages at 25/50/75%, and at 85% tells the agent "Stop all work now and produce a review output" (https://raw.githubusercontent.com/elastic/kibana/main/.claude/hooks/reviewer_time_budget.mjs).
- PR #275661 (merged Jul 6, 2026) fixed problems found after enabling the Claude reviewer by default (#274743): agent exceeded the 20-minute timeout, tried to post "Request Changes" reviews, and GraphQL prefetch lacked retries (https://github.com/elastic/kibana/pull/275661).
- PR #277053 (Jul 10, 2026): the time-budget hook "was not firing" because `.claude` restored from GitHub artifacts lost the executable bit (0644), causing "Permission denied"; the reviewer was also "wandering across the repo"; fix runs the hook via `node` and scopes verification to changed files and direct imports; verified "10/10 PostToolBatch hook invocations succeeded" (https://github.com/elastic/kibana/pull/277053).
- `.claude/settings.json` has 3 commits (Jun 2, Jul 6, Jul 10, 2026), two co-authored by Cursor's agent (https://github.com/elastic/kibana/commits/main/.claude/settings.json).

## What this case says for Gate A

This is a concrete, primary example of a silent harness regression in a closed vendor harness: a guardrail hook that the team believed was enforcing a time budget never ran in CI, because the environment changed a file mode, and the agent kept timing out until someone traced it. Nothing alerted on "hook did not fire"; the fix PR had to prove hook invocations by hand. It also shows the control surface a platform team owns (hooks shared across Claude Code and Cursor, MCP discouragement for cost, publish-blocking permissions) and the team's own admission that its permission hook fails open. Willingness to pay, data constraints and fleet size are unknown, but this counts toward "silent regression experienced: yes", attributed to environment plus hook, not the model.
