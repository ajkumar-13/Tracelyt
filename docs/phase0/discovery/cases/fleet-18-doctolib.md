# Doctolib: CTO-level governance of Claude Code across a healthcare engineering org, with a central prompt/command/subagent repo pulled at setup, headless Claude opening maintenance PRs in CI, and a public panel on surviving model upgrades "every few months"

evidence_grade: C (pass 2: re-searched; the only sources remain the Anthropic customer story, the Code w/ Claude London session abstract and third-party recaps of that panel. No Doctolib-authored post on Claude Code exists publicly and the talk recording could not be read. Kept at C; the recording is the untapped primary.)

```yaml
org: Doctolib
role: unknown (named: Alex Kaluzny, CTO (speaker); Julien Tanay, Staff Engineer leading the AI tooling program; Thomas Bentkowski, Platform PM)
track: fleet
date: 2026-10-05
interviewer: desk (no interview)
method: desk
harnesses_frameworks: [Claude Code (interactive across VSCode, JetBrains and CLI; headless in CI), subagents, custom slash commands, plan mode, planned GitHub Actions ticket-to-PR agents]
domain: coding
runs_per_day: unknown (whole development team after a 30-engineer pilot; headless CI jobs run on each code change in the main infrastructure repo)
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
  last_change: "Central repository of prompts, custom commands and subagents that every developer pulls at Claude Code setup; headless Claude in CI opening PRs for routine maintenance and updating docs; planned: ticket-to-PR agents via GitHub Actions, tailored AI reviews for triage and code quality, specs-driven development"
  regression_detection: unknown   # panel recap says model upgrades "require evals, prompt rework, A/B testing", but no Doctolib-specific practice is described
  silent_regression_experienced: unknown
  would_pay_to_prevent: unclear
controls_owned (fleets): [rules_files, ci_checks]   # stated: central prompt/command/subagent repo; CI jobs; "governs Claude Code across its entire healthcare engineering org" (session abstract)
tooling_today: [Claude Code, central prompts/commands/subagents repo, headless CI jobs (docs-as-code, maintenance PRs), Claude-powered PR review in the main infrastructure repo, Anthropic Skilljar training]
coding_agent_traces_flow_to: unknown
can_reproduce_failed_run: unknown
has_compared_cohorts: unknown
most_wanted_question: unknown
data_constraints:
  cannot_leave: unknown   # healthcare data (420k professionals, 90M patients) makes customer_data restrictions likely, but nothing public about agent telemetry
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: dev_productivity   # inferred: Staff Engineer-led "AI tooling program" with a Platform PM, CTO-sponsored
credible_contract_size: unknown
automation_limits: ""
would_allow_pause_stop_on_evidence: unknown
reaction:
  would_use_next_week: unknown
  does_not_believe: unknown
design_partner_candidate: unknown
referrals: [Delivery Hero (Rodrigue Schäfer, VP Platform; "autonomous agent that now merges 100+ PRs a day"), monday.com (Ruslan Semenov, Engineering Director) co-presented]
quotes:
  - q: 9
    text: "Engineers can now contribute to areas outside their expertise much faster. This fundamentally changes our development velocity."
  - q: 22
    text: "We want to help shape the roadmap of Claude Code and explore what's possible with autonomous agents."
  - q: 10
    text: "model upgrades are not drop-in swaps: they require evals, prompt rework, A/B testing, and sometimes rethinking orchestration"
    paraphrase: true
sources:
  - https://claude.com/customers/doctolib
  - https://claude.com/code-with-claude/session/ldn-building-ai-native-at-enterprise-scale-monday-com-doctolib-and-delivery-hero
  - https://www.juanmacias.me/posts/code-with-claude-london-2026/
  - https://relvehq.com/events/code-with-claude-london
  - https://claude.com/blog/code-w-claude-london-2026-rethinking-how-we-build
tags:
  harnesses_frameworks: stated
  runs_per_day: stated (pilot size, rollout, CI jobs)
  harness_change.last_change: stated (customer story)
  regression_detection: unknown; the panel takeaway is a third-party recap of a three-company panel, not attributed to Doctolib alone
  controls_owned: stated (artifacts), inferred (CTO governance from the abstract)
  budget_owner: inferred
  data_constraints: inferred
  referrals: stated (session page)
  quotes: q9 and q22 from the fetched customer page via summarizer (near-verbatim); q10 is a recap's summary of the panel, marked paraphrase and not attributable to Doctolib alone
```

## Evidence

- A 30-engineer pilot preceded the rollout to the whole development team; engineers self-onboard in under five minutes across VSCode, JetBrains and CLI; Claude Code is "the most-used AI tool on Doctolib's engineering team" (https://claude.com/customers/doctolib).
- The platform team keeps "a centralized repository of prompts, custom commands, and subagents that all developers pull during their initial Claude Code setup", so every engineer starts with the same workflows (docs, tests, review, debugging) (https://claude.com/customers/doctolib).
- Headless Claude Code runs in CI: jobs update technical documentation on each change, open PRs for routine maintenance, and Claude-powered reviews run in the main infrastructure repository (https://claude.com/customers/doctolib).
- Doctolib chose Claude Code for its documentation, Skilljar training courses, and "slash commands, subagents, and plan mode"; billing is license-free pay-as-you-go; no cost controls are named (https://claude.com/customers/doctolib).
- Reported outcomes: visual-regression-testing infrastructure migrated in hours rather than weeks; ramp-up on unfamiliar stacks cut from weeks to days (https://claude.com/customers/doctolib).
- Planned: autonomous ticket-to-PR agents via GitHub Actions in Q1, tailored AI-assisted reviews for triage and code quality, specs-driven development; Tanay: "We want to help shape the roadmap of Claude Code and explore what's possible with autonomous agents." (https://claude.com/customers/doctolib).
- Code w/ Claude London (19 May 2026) session abstract: "Doctolib governs Claude Code across its entire healthcare engineering org", alongside Delivery Hero's "autonomous agent that now merges 100+ PRs a day" and monday.com; the session promised to cover where implementations faced challenges and "how they stay ahead of model updates that occur every few months" (https://claude.com/code-with-claude/session/ldn-building-ai-native-at-enterprise-scale-monday-com-doctolib-and-delivery-hero).
- A third-party recap of the London event summarizes the panel's takeaway as "model upgrades are not drop-in swaps: they require evals, prompt rework, A/B testing, and sometimes rethinking orchestration"; it does not attribute the statement to Doctolib specifically (https://www.juanmacias.me/posts/code-with-claude-london-2026/; https://relvehq.com/events/code-with-claude-london).
- Not public: incidents, cost controls, MCP usage, observability stack, health-data constraints on agent traffic, or any Doctolib-authored engineering post on the program.

## What this case says for Gate A

Doctolib still fits the profile on paper: CTO-sponsored governance, one central repository that fans prompt, command and subagent changes out to every developer, and headless agents acting in CI. The London panel confirms the team thinks about model upgrades as events that need evals and prompt rework, which is the harness-change problem in Tracelyt's pitch, but the public record does not say what Doctolib itself does about it. No failure, regression or telemetry fact is public, so nothing counts toward Gate A. The session recording is the next source; Tanay and Bentkowski are the live-interview targets, and the question is how a change to the central repo is validated before every engineer pulls it.
