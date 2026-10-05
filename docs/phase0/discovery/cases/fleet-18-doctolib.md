# Doctolib: CTO-level governance of Claude Code across a healthcare engineering org, with a central prompt/command/subagent repo and headless Claude in CI

evidence_grade: C (Anthropic-published customer story with named Doctolib staff, plus a Code w/ Claude London 2026 session abstract; no talk transcript, incident or telemetry detail could be retrieved)

```yaml
org: Doctolib
role: unknown (named: Alex Kaluzny, CTO (speaker); Julien Tanay, Staff Engineer leading the AI tooling program; Thomas Bentkowski, Platform PM)
track: fleet
date: 2026-10-05
interviewer: desk
method: desk
harnesses_frameworks: [Claude Code (interactive, headless in CI), subagents, custom commands]
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
  last_change: unknown (a centralized repository of prompts, custom commands and subagents is distributed to all developers; GitHub Actions integration was "planned for Q1")
  regression_detection: unknown
  silent_regression_experienced: unknown
  would_pay_to_prevent: unclear
controls_owned: [rules_files, ci_checks]   # stated: central prompt/command/subagent repo; Claude-powered reviews and docs-update CI jobs. Inferred: the talk abstract says the CTO "governs Claude Code across its entire healthcare engineering org"
tooling_today: [Claude Code, central prompts/commands/subagents repo, CI docs-as-code jobs, Claude-powered PR review in the main infrastructure repo]
coding_agent_traces_flow_to: unknown
can_reproduce_failed_run: unknown
has_compared_cohorts: unknown
most_wanted_question: ""
data_constraints:
  cannot_leave: [unknown]   # healthcare (patient data) context makes customer_data very likely restricted, but nothing public about agent telemetry
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: dev_productivity   # inferred: a Staff Engineer leads an "AI tooling program" with a Platform PM
credible_contract_size: unknown
automation_limits: ""
would_allow_pause_stop_on_evidence: unknown
reaction:
  would_use_next_week: ""
  does_not_believe: ""
design_partner_candidate: unknown
referrals: [Delivery Hero (Rodrigue Schäfer, VP Platform), monday.com (Ruslan Semenov) co-presented]
quotes:
  - q: 9
    text: "Engineers can now contribute to areas outside their expertise much faster. This fundamentally changes our development velocity."
sources:
  - https://claude.com/customers/doctolib
  - https://claude.com/code-with-claude/session/ldn-building-ai-native-at-enterprise-scale-monday-com-doctolib-and-delivery-hero
tags:
  harnesses_frameworks: stated
  controls_owned: stated (artifacts), inferred (CTO governance from abstract wording)
  budget_owner: inferred
  data_constraints: inferred
  quotes: stated (fetched page via summarizer)
```

## Evidence
- A pilot with 30 engineers came before the company-wide rollout to the whole development team (https://claude.com/customers/doctolib).
- Doctolib keeps a "centralized repository of prompts, custom commands, and subagents" for all developers. That is a centrally owned harness layer (https://claude.com/customers/doctolib).
- Headless Claude Code runs in the CI pipeline. CI jobs keep documentation up to date with each change, and Claude-powered reviews run in the main infrastructure repository (https://claude.com/customers/doctolib).
- Doctolib migrated its whole visual-regression-testing infrastructure in hours instead of weeks, and ramp-up on unfamiliar stacks fell from weeks to days (https://claude.com/customers/doctolib).
- A pay-as-you-go, license-free billing model let the rollout scale without upfront commitment. The page names no cost controls (https://claude.com/customers/doctolib).
- At Code w/ Claude London (19 May 2026), CTO Alex Kaluzny presented how Doctolib "governs Claude Code across its entire healthcare engineering org", alongside Delivery Hero ("merges 100+ PRs a day") and monday.com (https://claude.com/code-with-claude/session/ldn-building-ai-native-at-enterprise-scale-monday-com-doctolib-and-delivery-hero).
- No public detail on security, health-data constraints, MCP, observability or incidents (https://claude.com/customers/doctolib).

## What this case says for Gate A
Doctolib fits the target profile well on paper. Governance is CTO-sponsored and spans the org, a central repository distributes prompts, commands and subagents (a single harness change point that fans out to every developer), and headless agents run in CI. Patient data makes "replay inside our environment only" the likely posture, but that is inference. The public record has no failure, regression or telemetry evidence, so nothing counts toward Gate A. The London talk recording, if one surfaces, is the source to mine next, and the team is a good live-interview target.
