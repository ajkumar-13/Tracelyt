# Rakuten: 7-hour autonomous Claude Code runs, Claude Managed Agents across business functions, an internal "Rakuten-SWE-Bench" that showed 3x production-task completion on a model upgrade, and a cost-per-task vs completion-ratio routing rule

evidence_grade: B (pass 2: Rakuten's own blog, a Rakuten GM's named quotes in two Anthropic customer stories and an Anthropic engineering post, a Code w/ Claude Tokyo keynote abstract, and an internal benchmark cited on Anthropic's Opus 4.7 release page. Specific on evaluation practice and multi-vendor tooling; no incident or telemetry detail, so not A.)

```yaml
org: Rakuten
role: unknown (named: Yusuke Kaji, GM AI for Business; Kenta Naruse, Machine Learning Engineer; Manoj Desai, Manager, AI Empowerment Section; Tanapat Ratana, Applied AI Group lead; Shoko Sakamoto, PM for FinOps/observability dashboards)
track: fleet
date: 2026-10-05
interviewer: desk (no interview)
method: desk
harnesses_frameworks: [Claude Code, Claude Managed Agents (persistent compute, memory, sandboxed environments), OpenAI Codex (two-day internal workshop with OpenAI; openai.com customer story), Rakuten AI agentic platform (internal), internal Rakuten-SWE-Bench task suite]
domain: coding   # plus workflow agents in product, sales, marketing, finance, FinOps and production-exception RCA
runs_per_day: unknown (agents "close issues roughly 10x faster across every domain"; specialist agents deployed in product, sales, marketing and finance within a week; non-engineers also use Claude Code)
failure_definition: unknown ("initial critical errors" is a reported metric but undefined; Rakuten-SWE-Bench scores "production task resolution" plus Code Quality and Test Quality)
failure_rate_estimate: "unknown in absolute terms; pilot claim: initial critical errors down 97% with memory-enabled agents; Opus 4.7 resolved 3x more Rakuten-SWE-Bench production tasks than Opus 4.6"
cost_per_failed_run: unknown ("cost per task" is tracked alongside task completion ratio)
last_failure:
  symptom: unknown (Kaji describes agents that previously needed correction "at 2 a.m. or 3 a.m."; no incident is described)
  detected_by: unknown
  time_to_why: unknown
  attributed_component: unknown
  recurred: unknown
  their_words: "Compared with previous models, it understands its mistake before I point it out at 2 a.m. or 3 a.m.—so that I can sleep."
harness_change:
  last_change: "Model upgrades (Opus 4.6 → 4.7; Fable 5 adopted for whole-task delegation); memory-enabled agents that carry lessons across sessions; a self-improving RCA agent; routing rule that sends Fable 5 the work where 'the extra capability changes the outcome'"
  regression_detection: evals   # internal Rakuten-SWE-Bench re-run on model upgrades; task completion ratio and cost per task tracked
  silent_regression_experienced: unknown
  would_pay_to_prevent: unclear
controls_owned (fleets): [model_effort, budgets, rules_files]   # stated: model routing by cost/completion; "appropriate context and coding guidelines" given to Claude Code; sandboxed Managed Agents environments. Owner inferred: AI for Business / AI Empowerment Section
tooling_today: [Claude Code, Claude Managed Agents, Codex, Rakuten-SWE-Bench, Slack, Microsoft Teams, internal Kanban-style task system, "ambient observability agents" that track anomalies and post to Slack, production-exception RCA agent]
coding_agent_traces_flow_to: unknown   # Rakuten has observability agents and a FinOps/observability PM, but no stack is named
can_reproduce_failed_run: unknown
has_compared_cohorts: yes   # model-vs-model on the internal production task suite; completion ratio vs cost per task per model
most_wanted_question: unknown
data_constraints:
  cannot_leave: unknown
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: ai_platform   # inferred: GM of AI for Business and the AI Empowerment Section own the rollout and the model-routing economics
credible_contract_size: unknown
automation_limits: "'We delegate goals, not tasks'; whole tasks handed over and several run at once since Fable 5; non-engineers work through Claude Code 'without directly editing code' with context and coding guidelines as the guardrail (Rakuten blog); Managed Agents run in sandboxed environments"
would_allow_pause_stop_on_evidence: unknown
reaction:
  would_use_next_week: unknown
  does_not_believe: unknown
design_partner_candidate: unknown
referrals: []
quotes:
  - q: 9
    text: "I didn't write any code during those seven hours. I just provided occasional guidance"
  - q: 10
    text: "Our agents with memory remember what went wrong in past sessions and avoid repeating those mistakes"
  - q: 10
    text: "Compared with previous models, it understands its mistake before I point it out at 2 a.m. or 3 a.m.—so that I can sleep."
  - q: 7
    text: "measures task completion ratio alongside cost per task, then sends Fable 5 the work where the extra capability changes the outcome"
    paraphrase: true
  - q: 9
    text: "We delegate goals, not tasks"
sources:
  - https://claude.com/customers/rakuten
  - https://claude.com/customers/rakuten-qa
  - https://claude.com/blog/working-at-the-frontier-rakuten
  - https://claude.com/code-with-claude/session/tyo-rakuten-ai-nization
  - https://rakuten.today/blog/rakuten-accelerates-development-with-claude-code%EF%BF%BC.html
  - https://rakuten.today/blog/rakuten-codex-workshop-openai.html
  - https://openai.com/index/rakuten/
  - https://www.anthropic.com/news/claude-opus-4-7
  - https://chatforest.com/builders-log/code-with-claude-tokyo-recap-rakuten-canva-japan-builder-guide/
tags:
  harnesses_frameworks: stated (claude.com pages; rakuten.today Codex workshop; openai.com story title)
  runs_per_day: stated (10x, one-week deployments, non-engineer use)
  failure_rate_estimate: stated (97%, 3x) with method undisclosed
  last_failure.their_words: stated (Anthropic blog, fetched)
  harness_change.last_change: stated (blog, release page); routing rule stated via summarizer, marked paraphrase
  regression_detection: stated (Rakuten-SWE-Bench on the Opus 4.7 release page) / inferred that it is re-run on each upgrade
  controls_owned: stated (routing, guidelines, sandboxes); owner inferred
  has_compared_cohorts: inferred from the model-vs-model benchmark
  budget_owner: inferred
  automation_limits: stated
  quotes: verbatim from fetched claude.com pages except where marked paraphrase
```

## Evidence

- Claude Code ran autonomously for 7 hours on an activation-vector extraction task in vLLM (12.5M lines, multiple languages) and reached a reported 99.9% numerical accuracy; Kenta Naruse: "I didn't write any code during those seven hours. I just provided occasional guidance"; time to market for new features fell from 24 to 5 days (79%) (https://claude.com/customers/rakuten).
- Rakuten's own blog repeats the figures, quotes Manoj Desai (AI Empowerment Section) and says non-engineers were asked to use Claude Code too; "with appropriate context and coding guidelines, Claude Code acts as a safety guardrail" (snippet rendering) (https://rakuten.today/blog/rakuten-accelerates-development-with-claude-code%EF%BF%BC.html).
- Rakuten is multi-vendor: it hosted a two-day Codex workshop with OpenAI for engineers and non-engineers, and OpenAI publishes a Rakuten story titled "Rakuten fixes issues twice as fast with Codex" (title only; page blocked) (https://rakuten.today/blog/rakuten-codex-workshop-openai.html; https://openai.com/index/rakuten/).
- Managed Agents: specialist agents for product, sales, marketing and finance went live within a week, wired into Slack, Teams and a Kanban-style task system, running in sandboxed environments with persistent compute, memory and storage; agents listed include user-feedback collection, ticket triage, PRD/wireframe/prototype, FinOps pipelines (Shoko Sakamoto), a production-exception RCA agent that "self-improves from feedback" (Tanapat Ratana) and "ambient observability agents" that track anomalies and post to Slack (https://claude.com/customers/rakuten-qa).
- Pilot claim: memory-enabled agents cut "initial critical errors" by 97% with cost and latency down more than 30%; releases moved from quarterly to every two weeks. No methodology is given (https://claude.com/customers/rakuten-qa).
- Anthropic engineering post (20 Jul 2026): Kaji began testing Claude in Sept 2024 and moved to production in March 2025; agents "close issues roughly 10x faster across every domain"; Fable 5 "re-checks its own assumptions" and lets him "hand over a whole task and run several at once"; the team "measures task completion ratio alongside cost per task, then sends Fable 5 the work where the extra capability changes the outcome" (https://claude.com/blog/working-at-the-frontier-rakuten).
- Anthropic's Opus 4.7 release cites "Rakuten-SWE-Bench", a Rakuten production task suite, on which Opus 4.7 "resolves 3x more production tasks than Opus 4.6, with double-digit gains in Code Quality and Test Quality"; it is a partner-run benchmark on proprietary tasks (https://www.anthropic.com/news/claude-opus-4-7).
- Code w/ Claude Tokyo keynote (10 Jun 2026): Rakuten evaluates agents on "how autonomously an agent can run, and how broadly it can empower people"; the ceiling "is set by how work is structured rather than by model intelligence"; memory is treated as a corporate asset; a recap adds that next-generation agents need "self-reflection" to recognise failing paths and retry (https://claude.com/code-with-claude/session/tyo-rakuten-ai-nization; https://chatforest.com/builders-log/code-with-claude-tokyo-recap-rakuten-canva-japan-builder-guide/).
- Not public: any incident, runaway-cost event, OTel export destination, permission policy, or data-residency rule for agent transcripts.

## What this case says for Gate A

Rakuten already does two things Tracelyt wants to sell: it keeps a frozen production task suite and re-scores models on it when the vendor ships an upgrade, and it tracks completion ratio against cost per task to decide routing. That is cohort comparison and regression gating for model changes, built in-house and apparently limited to model swaps rather than to its own harness changes (memory, self-improving RCA agent, coding guidelines). The self-improving agents and cross-session memory are exactly where silent drift would hide, and nothing public says they are gated. The record is still vendor-curated and silent on incidents, telemetry and data constraints, so no pain counter moves. It does count as "has compared cohorts: yes". Kaji's group and the FinOps/observability PM are the live-interview targets; the question is whether Rakuten-SWE-Bench is run on harness changes or only on model releases.
