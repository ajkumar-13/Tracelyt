# Instacart: "Olive", a background coding-agent platform on the Codex SDK where engineers start a remote dev environment and complete tasks "with a single click"; Codex cleans up dead code and expired experiments; Instacart's own blog says the development environment was the biggest driver of agent quality and that an agent removed 15+ feature flags from one service in a single PR; the CTO says code is regenerated weekly and "in 97% of cases" builders do not read it

evidence_grade: B

Access note (2026-10-05): no Instacart-authored post about Olive was found. Evidence is (a) OpenAI's Codex general-availability post, which carries the Olive description as a customer example, (b) VentureBeat's report of CTO Anirban Kundu's remarks at VB Transform 2026, (c) Instacart's own engineering post "AI-Driven Development at Instacart: Scaling Impact and Increasing Velocity", which covers coding agents, environment effects and feature-flag cleanup but does not name Olive, and (d) Instacart's Ava posts. Grade B (primary but thin): Instacart's blog is primary on agent practice, but Olive itself is described only by OpenAI, and there is no failure, eval or trace-tooling detail.

```yaml
org: Instacart
role: Developer productivity / Olive platform (public: Anirban Kundu, CTO)
track: builder
date: 2026-10-05
interviewer: desk
method: desk
harnesses_frameworks: [Olive (background coding-agent platform) on the OpenAI Codex SDK, remote development environments, Claude Code (Enterprise customer; AGENTS.md in the open-source Formula repo), Cursor, Ava (internal assistant on GPT-4/GPT-3.5, 2023)]
domain: coding
runs_per_day: unknown
failure_definition: unknown
failure_rate_estimate: unknown
cost_per_failed_run: unknown
last_failure:
  symptom: "No incident published. Stated systemic finding: 'how much the development environment impacted AI performance'; agents were 'most effective in modular, well-annotated workspaces', and scoped single-service workspaces gave 'more reliable outputs' than a big repository"
  detected_by: unknown
  time_to_why: unknown
  attributed_component: environment
  recurred: unknown
  their_words: "One of the most consistent learnings was just how much the development environment impacted AI performance."
harness_change:
  last_change: "Codex SDK integrated into Olive (announced with Codex GA)"
  regression_detection: unknown
  silent_regression_experienced: unknown
  would_pay_to_prevent: unknown
controls_owned (fleets): [rules_files]
tooling_today: [AGENTS.md rules file (Formula repo), scoped IDE workspaces per service, Claude models split by task (architecture/ERD planning vs writing and reviewing code)]
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
automation_limits: "inferred: Codex 'edit[s] and test[s] changes' and takes on 'repetitive, well-understood changes'; humans do not read code in '97% of cases' (CTO), so review is not the control"
would_allow_pause_stop_on_evidence: unknown
reaction:
  would_use_next_week: unknown
  does_not_believe: unknown
design_partner_candidate: unknown
referrals: [Anirban Kundu]
quotes:
  - q: 9
    text: "Engineers spin up a remote development environment and complete end-to-end tasks with a single click, using Codex to edit and test changes"
  - q: 9
    text: "Codex automatically cleans up tech debt like dead code and expired experiments, improving code quality and reducing latency across codebases."
  - q: 8
    text: "in 97% of cases, Instacart's builders don't even read code anymore"
    paraphrase: true
  - q: 10
    text: "AI-generated code gets rebuilt so often that tech debt has stopped being a concern"
    paraphrase: true
  - q: 4
    text: "One of the most consistent learnings was just how much the development environment impacted AI performance."
  - q: 9
    text: "cleaning up 15+ feature flags from a single service in a single PR"
sources:
  - https://openai.com/index/codex-now-generally-available/
  - https://venturebeat.com/orchestration/instacarts-cto-says-ai-made-the-company-stop-worrying-about-tech-debt
  - https://tech.instacart.com/ai-driven-development-at-instacart-scaling-impact-and-increasing-velocity-43f6b3902a32
  - https://tech.instacart.com/scaling-productivity-with-ava-instacarts-internal-ai-assistant-ed7f02558d84
  - https://bloomberry.com/data/anthropic-claude/
tags:
  harnesses_frameworks: stated (OpenAI Codex GA post for Olive + Codex SDK; Instacart blog for Claude models, AGENTS.md, Cursor; Ava posts)
  last_failure.symptom: stated (Instacart blog) as a systemic finding, not an incident
  last_failure.attributed_component: stated (environment quality drove agent output quality)
  controls_owned: stated (AGENTS.md in Formula repo)
  tooling_today: stated (Instacart blog)
  harness_change.last_change: stated (OpenAI post)
  automation_limits: inferred (OpenAI post on edit/test; VentureBeat on not reading code)
  budget_owner: inferred
  quotes: OpenAI post verbatim; VentureBeat paraphrased
```

## Evidence
- "At Instacart, the Codex SDK is integrated with Olive, their background coding agent platform. Engineers spin up a remote development environment and complete end-to-end tasks with a single click, using Codex to edit and test changes" (https://openai.com/index/codex-now-generally-available/).
- "Codex automatically cleans up tech debt like dead code and expired experiments, improving code quality and reducing latency across codebases. It also takes on repetitive, well-understood changes, reducing backlog and significantly accelerating engineering velocity" (https://openai.com/index/codex-now-generally-available/).
- VB Transform 2026: CTO Anirban Kundu said AI-generated code "gets rebuilt so often that tech debt has stopped being a concern"; "in 97% of cases, Instacart's builders don't even read code anymore"; agents handle "the bulk of code generation and boilerplate", with newer projects' code "generated or regenerated on a weekly basis" (https://venturebeat.com/orchestration/instacarts-cto-says-ai-made-the-company-stop-worrying-about-tech-debt).
- Instacart's engineering blog: "One of the most consistent learnings was just how much the development environment impacted AI performance"; agents "were most effective in modular, well-annotated workspaces", and teams that scoped IDE workspaces to a single service "saw improved indexing speed, smarter suggestions, and more reliable outputs" (https://tech.instacart.com/ai-driven-development-at-instacart-scaling-impact-and-increasing-velocity-43f6b3902a32).
- Same post: when cleaning up stale feature flags or deprecated logic "the AI agent identified unused paths and rewrote the class with precision, cleaning up 15+ feature flags from a single service in a single PR"; different Claude models are treated "like specialized team members" (architecture/ERD planning vs writing and reviewing code); the open-source Formula repo carries an AGENTS.md for Claude Code; the post does not name Olive (https://tech.instacart.com/ai-driven-development-at-instacart-scaling-impact-and-increasing-velocity-43f6b3902a32).
- Earlier internal assistant Ava (GPT-4/GPT-3.5): over half of employees monthly, 900+ weekly; "60% of Instacart's engineers generate around 70,000 lines of code using Ava every month" (https://tech.instacart.com/scaling-productivity-with-ava-instacarts-internal-ai-assistant-ed7f02558d84).

## What this case says for Gate A
Instacart is a strong-shape target: a background agent built on a vendor SDK (so vendor harness changes flow straight into production), doing automated cleanup where "passes CI but is wrong" is the main risk, and a leadership stance that humans mostly do not read the code. If builders do not read code, the only controls left are tests and whatever the harness itself verifies, which is the argument for component attribution and regression gating. Instacart's own blog adds one countable attribution: output quality was driven by the development environment (workspace scoping, annotation), which is an environment-component finding rather than a model one, and it is the kind of effect that only shows up when cohorts of runs are compared. Still missing: any failure incident, eval practice, trace sink or data constraint. Treat as an outreach candidate with a confirmed harness shape. Counts: silent_regression unknown, attribution = environment (systemic, not an incident), traces unknown, cannot_leave unknown.
