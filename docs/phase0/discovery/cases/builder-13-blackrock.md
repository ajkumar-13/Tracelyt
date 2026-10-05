# BlackRock (Aladdin Copilot): LangGraph supervisor fed by a plugin registry from 50+ teams, gated by daily evaluation-driven CI; the closest builder to "regression gating" on desk evidence

evidence_grade: B  (primary Interrupt 2025 talk by Brennan Rosales and Pedro Vicente Valdez, seen only through ZenML/secondary summaries in search snippets; no incident story)

```yaml
org: BlackRock (Aladdin Copilot)
role: AI Engineering Lead (Brennan Rosales, since left per LinkedIn, U) and Principal AI Engineer (Pedro Vicente Valdez)
track: builder
date: 2026-10-05
interviewer: desk-research agent
method: desk
harnesses_frameworks: [LangChain, LangGraph, GPT-4 function calling, plugin registry, MCP (in a related BlackRock agent, see Evidence)]   # stated
domain: workflow   # investment-management copilot across Aladdin apps
runs_per_day: unknown   # stated scale proxies: embedded across 100+ Aladdin applications; platform over ~$11T AUM
failure_definition: unknown   # inferred dimensions from tests: compliance breach (giving investment advice), wrong API interaction, ignoring context in multi-turn
failure_rate_estimate: unknown
cost_per_failed_run: unknown
last_failure:
  symptom: unknown
  detected_by: ci   # inferred: daily CI/CD eval runs exist to make sure the system is "not deteriorating"; no specific detection story
  time_to_why: unknown
  attributed_component: unknown
  recurred: unknown
  their_words: ""
harness_change:
  last_change: "Plugin registry lets 50+ engineering teams contribute tools and agents to the copilot"   # stated (ongoing change stream, not one change)
  regression_detection: ci   # stated: "evaluation-driven development approach with daily CI/CD testing"; system-prompt tests (synthetic data, expert review, LLM-as-judge); end-to-end regression checks on API interactions and multi-turn context
  silent_regression_experienced: unknown   # the existence of daily anti-deterioration CI is suggestive but no regression is described
  would_pay_to_prevent: unknown
controls_owned (fleets): []
tooling_today: [LLM-as-judge evals, daily CI eval suite, synthetic test data, expert review; OpenTelemetry + Langfuse and a fixture-based evaluation harness (attribution to Aladdin Copilot unverified, see Evidence)]
coding_agent_traces_flow_to: unknown
can_reproduce_failed_run: unknown   # a fixture-based evaluation harness is mentioned, which implies partial replay, but its attribution is unverified
has_compared_cohorts: unknown
most_wanted_question: ""
data_constraints:
  cannot_leave: unknown   # regulated asset manager; nothing public seen stating what data cannot leave
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: ai_platform   # inferred: a central AI engineering team owns orchestration and evaluation for contributing teams
credible_contract_size: unknown
automation_limits: "System prompt testing to ensure no investment advice is given"   # stated (compliance guard)
would_allow_pause_stop_on_evidence: unknown
reaction:
  would_use_next_week: ""
  does_not_believe: ""
design_partner_candidate: unknown
referrals: []
quotes:
  - q: 9
    text: "evaluation-driven development approach with daily CI/CD testing to ensure the Aladdin Copilot system is continuously improving and not deteriorating"
    paraphrase: true   # wording is ZenML's summary of the talk, not a speaker quote
sources:
  - https://www.zenml.io/llmops-database/agentic-ai-architecture-for-investment-management-platform
  - https://blog.tmcnet.com/blog/rich-tehrani/ai/how-blackrock-orchestrates-11t-in-assets-with-production-ai-agents.html
  - https://cameronrohn.com/docs/discover/LangChain-Interrupt-2025/presentations/2.11-From-Pilot-to-Platform-Aladdin-Copilot/
  - https://medium.com/youme-technology/day-24-learnings-from-financial-industry-leaders-related-to-agentic-ai-blackrock-5eb96468e693
  - https://www.linkedin.com/in/brennan-rosales-241187133/
tags:
  harnesses_frameworks: stated
  runs_per_day: stated (proxies only)
  last_failure.detected_by: inferred
  harness_change.last_change: stated
  harness_change.regression_detection: stated (secondary summary of primary talk)
  tooling_today: stated (evals, CI) / unverified attribution (OTel, Langfuse, fixtures)
  budget_owner: inferred
  automation_limits: stated
```

## Evidence
- Aladdin Copilot is embedded across BlackRock's investment-management platform; a supervised agentic architecture on LangChain/LangGraph with GPT-4 function calling for orchestration, presented at Interrupt 2025 by Brennan Rosales (AI Engineering Lead) and Pedro Vicente Valdez (Principal AI Engineer), across 100+ applications (https://blog.tmcnet.com/blog/rich-tehrani/ai/how-blackrock-orchestrates-11t-in-assets-with-production-ai-agents.html).
- A plugin registry lets 50+ engineering teams contribute tools and agents (https://www.zenml.io/llmops-database/agentic-ai-architecture-for-investment-management-platform).
- "Evaluation-driven development approach with daily CI/CD testing to ensure the Aladdin Copilot system is continuously improving and not deteriorating" (ZenML summary wording) (https://www.zenml.io/llmops-database/agentic-ai-architecture-for-investment-management-platform).
- System-prompt testing checks compliance (e.g., no investment advice) using synthetic data, expert reviews and LLM-as-judge; end-to-end testing validates API interactions, multi-turn conversations and context respect through regression checks (same ZenML entry, via search snippet).
- The same search surfaced a BlackRock evaluation framework combining black-box (task completion via judge LLMs) and glass-box evaluation (tool use, reasoning trajectories), and an agent that evolved from a single ReAct agent using MCP to LangGraph triage/research/remediation agents with "exception classification pipelines", improved via OpenTelemetry + Langfuse observability and a "fixture-based evaluation harness". The snippet did not make clear whether this describes Aladdin Copilot or a separate BlackRock operations agent; treat as BlackRock-level, attribution unverified (https://www.zenml.io/llmops-tags/langchain; https://www.zenml.io/llmops-database/agentic-ai-architecture-for-investment-management-platform).
- Brennan Rosales now lists a stealth AI startup (https://www.linkedin.com/in/brennan-rosales-241187133/).

## What this case says for Gate A
BlackRock is the clearest builder in this batch that already gates harness changes with a daily CI eval suite, which matches our CI-regression-gating wedge and proves the job exists; it also means they have an in-house answer, so we would be selling an upgrade (component attribution across 50+ contributing teams, first-divergence on trajectory failures) rather than a first tool. The plugin registry is exactly the situation where "which team's tool or prompt broke it" is a hard question, but no public incident confirms the pain. Data constraints are unknown on desk evidence and would likely be strict for a regulated asset manager. Count as a strong qualified target; no contribution to the paid-pain or replay counters without a live conversation.
