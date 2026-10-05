# Duolingo: DevXAI's "CodingAgent" library wraps OpenAI Codex CLI and the Claude Code SDK behind one interface (switched by a single enum); agents run as Temporal "AgentWorkflow" with per-tool-call retries, timeouts and replay visible in the Temporal UI; a shared platform with built-in evals (agent output, changed files and git diff graded against authored scenarios) cut agent creation from weeks to ~10 minutes

evidence_grade: B

Access note (2026-10-05): primary sources are three Duolingo Engineering posts ("Agentic Workflows: Scale AI Prompts Beyond Cursor, No Code Required"; "Making production-ready agents the default: building Duolingo's agent platform"; "How We Built an AI Agent to Remove Feature Flags") plus the AI Slackbot post, all reached through search snippets and a ZenML summary; blog.duolingo.com is egress-blocked. Grade B: primary and specific on architecture, harness switching and eval design, but no published failed-run story, no volumes and no regression incident.

```yaml
org: Duolingo
role: DevXAI (developer experience AI) team
track: builder
date: 2026-10-05
interviewer: desk
method: desk
harnesses_frameworks: [CodingAgent library (wraps OpenAI Codex CLI and Anthropic Claude Code SDK; provider switched by one enum), Temporal AgentWorkflow (runtimes: OpenAI Agents SDK, Claude Agents SDK, Codex CLI), agent registry (system prompt, tools, access requirements), no-code workflow platform, internal AI Slackbot with 180+ MCP tools, open-sourced Slack MCP server, Cursor for IDE work]
domain: coding
runs_per_day: unknown
failure_definition: "inferred: agent run fails an authored eval scenario (graded on output, changed files and git diff) or a tool call exhausts retries/timeouts in Temporal"
failure_rate_estimate: unknown
cost_per_failed_run: unknown
last_failure:
  symptom: "No failed-run story published. Stated difficulty: the feature-flag agent needed 'a significant portion of the development week on prompt engineering' and extension from Python-only to Kotlin"
  detected_by: unknown
  time_to_why: unknown
  attributed_component: unknown
  recurred: unknown
  their_words: ""
harness_change:
  last_change: "Consolidated per-team agent infrastructure into one platform (define once in a registry; platform handles execution, observability, orchestration, evaluation); CodingAgent abstraction allows switching between Codex CLI and Claude Code SDK by changing one enum"
  regression_detection: evals
  silent_regression_experienced: unknown
  would_pay_to_prevent: unknown
controls_owned (fleets): [mcp_servers, tool_allowlists, permissions]
tooling_today: [Temporal UI (every tool call's inputs, outputs, failures and retries), platform-native agent evals with authored scenarios, self-service UI for feature-flag removal, Slackbot with 180+ MCP tools]
coding_agent_traces_flow_to: other (Temporal UI holds per-tool-call history; no observability vendor named)
can_reproduce_failed_run: partially
has_compared_cohorts: unknown (harness switching by enum makes cross-vendor comparison possible; no comparison published)
most_wanted_question: unknown
data_constraints:
  cannot_leave: unknown
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: dev_productivity
credible_contract_size: unknown
automation_limits: "Feature-flag agent opens PRs assigned to the requesting engineer rather than merging; agents declare access requirements in the registry"
would_allow_pause_stop_on_evidence: unknown
reaction:
  would_use_next_week: unknown
  does_not_believe: unknown
design_partner_candidate: unknown
referrals: []
quotes:
  - q: 9
    text: "Duolingo created a single library called CodingAgent, which wraps both Codex CLI and Claude Code SDK into a single library, and switching agents is as simple as changing a single enum parameter."
    paraphrase: true
  - q: 13
    text: "Every tool call—including inputs, outputs, failures, and retries—is visible in the Temporal UI."
  - q: 10
    text: "Agent evals run the real agent against authored scenarios. They capture the agent's output, change files, and git diff before grading the result."
  - q: 9
    text: "developers define agents through a simple registry specifying system prompts, tools, and access requirements, while the platform handles execution, observability, orchestration, and evaluation automatically"
    paraphrase: true
  - q: 10
    text: "spending a significant portion of the development week on prompt engineering"
    paraphrase: true
sources:
  - https://blog.duolingo.com/agentic-workflows/
  - https://blog.duolingo.com/production-ready-ai-agent-platform/
  - https://blog.duolingo.com/buildingaiagents/
  - https://blog.duolingo.com/aislackbot/
  - https://www.zenml.io/llmops-database/building-a-production-ready-ai-agent-platform-with-temporal
  - https://www.zenml.io/llmops-database/ai-agent-for-automated-feature-flag-removal
  - https://chatforest.com/guides/duolingo-mcp-agentic-platform/
tags:
  harnesses_frameworks: stated (agentic-workflows post for CodingAgent and enum; platform post for Temporal AgentWorkflow and runtimes; Slackbot post for 180+ MCP tools)
  failure_definition: inferred (from eval grading and Temporal retry semantics)
  last_failure.symptom: stated as development difficulty (feature-flag post), not as a production incident
  harness_change.last_change: stated (platform post; agentic-workflows post)
  regression_detection: stated (platform evals; whether they gate CI is not stated)
  controls_owned: inferred (registry declares tools and access; MCP tools curated by DevXAI)
  tooling_today: stated
  coding_agent_traces_flow_to: inferred (Temporal UI is named as where tool calls are visible; no Datadog/LangSmith/etc. named)
  can_reproduce_failed_run: inferred (Temporal workflow history and "automatic replay if the workflow restarts" give durable state; replay of a failed agent run for debugging is not stated)
  budget_owner: inferred (DevXAI team)
  automation_limits: stated (feature-flag post)
  time_to_10_minutes: stated (platform post via ZenML: "weeks to approximately 10 minutes", by Aug 2026)
```

## Evidence
- CodingAgent "wraps both Codex CLI and Claude Code SDK into a single library"; the library "abstracts multiple LLM providers behind a single interface—OpenAI Codex via Codex CLI and Anthropic Claude via Claude Code SDK—and switching between providers requires only changing an enum parameter" (https://blog.duolingo.com/agentic-workflows/ ; https://chatforest.com/guides/duolingo-mcp-agentic-platform/).
- The no-code platform "lets any employee create and deploy AI coding agents in under five minutes"; the internal Slackbot connects "180+ MCP tools"; Duolingo open-sourced a Slack MCP server (https://blog.duolingo.com/agentic-workflows/ ; https://blog.duolingo.com/aislackbot/).
- Execution layer: a Temporal workflow called AgentWorkflow "serves as a wrapper abstracting away shared infrastructure and setup requirements"; it "already supported a few runtimes, including the Claude Agents SDK and Codex CLI" alongside the OpenAI Agents SDK (https://blog.duolingo.com/production-ready-ai-agent-platform/ ; https://www.zenml.io/llmops-database/building-a-production-ready-ai-agent-platform-with-temporal).
- Reliability: "Every tool call gets independent retry with configurable backoff, timeout enforcement, full observability in the Temporal UI, and automatic replay if the workflow restarts"; "Every tool call—including inputs, outputs, failures, and retries—is visible in the Temporal UI" (https://blog.duolingo.com/production-ready-ai-agent-platform/).
- Evaluation: "Agent evals run the real agent against authored scenarios. They capture the agent's output, change files, and git diff before grading the result"; evaluation is "a first-class concern" of the platform (https://blog.duolingo.com/production-ready-ai-agent-platform/).
- Developers "define agents through a simple registry specifying system prompts, tools, and access requirements, while the platform handles execution, observability, orchestration, and evaluation automatically"; agent creation time fell "from weeks to approximately 10 minutes" by August 2026 (https://www.zenml.io/llmops-database/building-a-production-ready-ai-agent-platform-with-temporal).
- Feature-flag removal agent: Codex CLI on Temporal, started from a self-service UI; clones repos, removes obsolete flags in Python and Kotlin, and "automatically creates pull requests assigned to the requesting engineer"; prototype to production in about a week, with "a significant portion of the development week on prompt engineering" (https://blog.duolingo.com/buildingaiagents/ ; https://www.zenml.io/llmops-database/ai-agent-for-automated-feature-flag-removal).

## What this case says for Gate A
Duolingo is the clearest public example of a builder that can swap the underlying coding harness (Codex CLI vs Claude Code SDK) with one enum, which means every vendor-side harness change and every internal prompt or tool change lands on a shared platform used by non-engineers. That is precisely where a regression gate for harness changes pays off, and their platform already grades real runs on output, changed files and git diff, so a gating hook has a natural place. Temporal gives them durable per-tool-call history and workflow replay, which overlaps with the flight-recorder half of our pitch but not with first-divergence, cohort comparison or component attribution. Nothing public describes a production failure, a regression, run volumes or data constraints, so pain is unverified. Counts: silent_regression unknown, attribution unknown, traces to Temporal UI (other), cannot_leave unknown.
