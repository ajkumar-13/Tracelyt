# Datadog: Codex user in-house; ships "Agent Console" to monitor customers' coding-agent fleets (spend, waste patterns, fix-by-hook)

evidence_grade: B for the product evidence (primary Datadog blog and docs); C for Datadog as a fleet operator itself (the only internal-usage evidence is the openai.com Codex reference in 09-interview-targets.md, which could not be re-verified because openai.com is egress-blocked)

Note: this file is mostly about Datadog as a competitor or channel that has productised fleet observability, because no public source describes Datadog's own internal coding-agent governance.

```yaml
org: Datadog
role: unknown (internal Codex user named in the target list: Brad Carter, Eng Manager; product voices: Amber Tunnell, Senior PM, Agent Console)
track: fleet
date: 2026-10-05
interviewer: desk
method: desk
harnesses_frameworks: [Codex (internal, per target list), Bits AI agents (Bits Investigation, Bits Chat, Bits Agent Builder, Bits Code)]
domain: coding
runs_per_day: unknown
failure_definition: unknown for Datadog internally. Agent Console defines "waste patterns": skipped checks (commits without running tests), retry loops, file rereads
failure_rate_estimate: unknown
cost_per_failed_run: unknown (Agent Console attributes waste-pattern cost in dollars per session/repo)
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
  would_pay_to_prevent: unclear
controls_owned: [hooks]   # inferred from the product: the Fix Library deploys PreToolUse hooks org-wide via PR; Datadog's own internal controls are not public
tooling_today: [Datadog Agent Console (preview), Datadog LLM Observability (supports OTel GenAI semantic conventions), Anthropic Usage and Costs integration, Cursor integration (Datadog Extension for Cursor), GitHub Copilot integration]
coding_agent_traces_flow_to: datadog   # inferred for Datadog itself (dogfooding is likely but not stated); for customers, Claude Code exports OTel logs+metrics to Datadog's OTLP endpoint
can_reproduce_failed_run: unknown
has_compared_cohorts: unknown (the product compares AI-assisted vs non-AI work on DORA metrics; that is a cohort comparison by adoption, not by failure)
most_wanted_question: "Who in my organization is using coding agents the most? What are users doing well with agents and where are they struggling? How does AI spend correlate with engineering output?"   # product framing of customer questions
data_constraints:
  cannot_leave: [unknown]
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: observability   # inferred: sold as part of the Datadog observability platform
credible_contract_size: unknown
automation_limits: ""
would_allow_pause_stop_on_evidence: unknown (the product's remedy is to deploy a blocking PreToolUse hook, "Verify before git", which runs test/lint/build before allowing commits; inferred acceptance of automated gating)
reaction:
  would_use_next_week: ""
  does_not_believe: ""
design_partner_candidate: no   # inferred: direct competitor for fleet observability; possible integration partner instead
referrals: []
quotes:
  - q: 17
    text: "Agent Console helps you answer three practical questions: 1. Who in my organization is using coding agents the most? 2. What are users doing well with agents and where are they struggling? 3. How does AI spend correlate with engineering output?"
sources:
  - https://www.datadoghq.com/blog/claude-code-monitoring/
  - https://docs.datadoghq.com/ai_agents_console/
  - https://docs.datadoghq.com/ai_agents_console/setup/
  - https://docs.datadoghq.com/llm_observability/
  - https://openai.com/index/gartner-2026-agentic-coding-leader/
tags:
  harnesses_frameworks: stated (Bits agents); inferred-unverified (Codex internal, from target list)
  failure_definition: stated (product waste patterns)
  controls_owned: inferred
  coding_agent_traces_flow_to: inferred (internal), stated (product ingestion path)
  budget_owner: inferred
  design_partner_candidate: inferred
  quotes: stated (fetched page)
```

## Evidence
- On June 9, 2026 Datadog launched "Agent Console" (preview), which monitors adoption, spend and behaviour across GitHub Copilot, Claude Code, Cursor, Codex, Opencode and Datadog's own Bits AI agents (https://www.datadoghq.com/blog/claude-code-monitoring/).
- It reports spend by agent, team and user, session-level dollar cost, active users and sessions, lines generated, median time to merge, and the share of AI-assisted commits and PRs (https://www.datadoghq.com/blog/claude-code-monitoring/).
- It detects "waste patterns": skipped checks (agents committing without running tests), retry loops and file rereads. Each is attributed a cost and the affected repositories (https://www.datadoghq.com/blog/claude-code-monitoring/).
- Its "Fix Library" maps patterns to vetted remedies. For example, a "Verify before git" PreToolUse hook runs the repo's test/lint/build before an agent commit, deployable to one repo or a whole organization via PR (https://www.datadoghq.com/blog/claude-code-monitoring/).
- An "Impact Metrics" view compares AI-assisted with non-AI work on DORA-style pillars: adoption, velocity (lead time, review time) and stability (change failure rate, recovery time) (https://www.datadoghq.com/blog/claude-code-monitoring/).
- Claude Code ingestion uses its native OTel export: CLAUDE_CODE_ENABLE_TELEMETRY=1, OTLP logs and metrics exporters pointed at Datadog with a dd-api-key header. Settings are distributed via MDM or server-managed settings. Captured: "usage, cost, latency, errors" (https://docs.datadoghq.com/ai_agents_console/setup/).
- Cursor and Copilot data come through separate integrations (Datadog Extension for Cursor; GitHub Copilot integration). The docs do not say whether prompts or tool content are captured (https://docs.datadoghq.com/ai_agents_console/setup/).
- Datadog LLM Observability "natively supports OpenTelemetry GenAI Semantic Conventions" (https://docs.datadoghq.com/llm_observability/).
- The target list cites OpenAI material naming Datadog as a Codex customer (Brad Carter, Eng Manager). Not re-verified here (https://openai.com/index/gartner-2026-agentic-coding-leader/).

## What this case says for Gate A
The most important finding is competitive. As of June 2026 the default observability vendor already sells a fleet console that ingests Claude Code OTel, Cursor and Copilot data, prices waste per session, and pushes fixes as org-wide hooks. That covers much of the "fleet visibility plus cost" wedge. What it does not show, from the public docs, is per-run reconstruction, first-divergence analysis, incident clustering across failed runs, replay, or CI gating of harness changes. That is where differentiation would have to live. It also signals real market demand: Datadog would not build this without customers asking "where are agents struggling". For the counters, Datadog itself contributes nothing (no internal incident is public). It should be treated as a competitor and possible integration target, not a design partner.
