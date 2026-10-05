# GitHub (Copilot cloud agent, Copilot CLI, Agent HQ): staged go/no-go model evals, and the most standards-aligned telemetry of any vendor (OTel GenAI semconv, agent audit log)

evidence_grade: A

```yaml
org: GitHub (Microsoft)
role: harness vendor and multi-agent platform (Copilot cloud agent, Copilot CLI, Copilot SDK, third-party agents / Agent HQ, Agentic Workflows)
track: vendor
date: 2026-10-05
interviewer: desk-research agent (vendor track)
method: desk
harnesses_frameworks: [Copilot cloud agent, Copilot CLI, Copilot SDK, Claude and Codex as third-party agents on GitHub, GitHub Agentic Workflows]
domain: coding
runs_per_day: unknown
failure_definition: "resolution rate (percentage of tasks successfully completed), token efficiency, latency, tool call reliability; in production: error rates, response latency, aggregate usage"   # stated
failure_rate_estimate: unknown
cost_per_failed_run: unknown
last_failure:
  symptom: unknown        # no public GitHub harness-regression postmortem found in this pass
  detected_by: unknown
  time_to_why: unknown
  attributed_component: unknown
  recurred: unknown
  their_words: ""
harness_change:
  last_change: unknown
  regression_detection: evals          # staged benchmark suites vs baselines plus go/no-go board (stated)
  silent_regression_experienced: unknown
  would_pay_to_prevent: unknown
controls_owned (fleets): n/a (vendor); exposes: [custom instructions, hooks, mcp enterprise allowlist, firewall, copilot environment secrets, policies for third-party agents, managed settings incl. enforced OTel, budgets]
tooling_today: [SWE-Bench + internal eval suites with multiple runs, cross-functional go/no-go board, production monitoring of error rates and latency, RAI red teaming]
coding_agent_traces_flow_to: other     # customer OTLP backend of choice (Grafana/App Insights example) + enterprise audit log streaming
can_reproduce_failed_run: partially   # session logs retained on github.com for cloud agent; local session-state; no replay feature
has_compared_cohorts: yes             # new models compared against baselines and production models (stated)
most_wanted_question: unknown
data_constraints:
  cannot_leave: [prompts, tool_outputs, code]    # stated as default: OTel excludes prompts, responses, tool arguments unless opted in
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: unknown
credible_contract_size: unknown
automation_limits: "cloud agent pushes only to copilot/ or the PR branch, never default branch; firewall on by default; only copilot-environment secrets; Agentic Workflows stage writes through a safe-output service with type/count limits"
would_allow_pause_stop_on_evidence: unknown
would_emit_standard_signal: yes        # already emits OTel GenAI semconv (gen_ai.operation.name=invoke_agent, gen_ai.agent.*, gen_ai.conversation.id) and links the GenAI/MCP semconv
reaction:
  would_use_next_week: unknown
  does_not_believe: unknown
design_partner_candidate: unknown
referrals: []
quotes:
  - q: 10
    text: "Models must meet or exceed baseline performance across key metrics like resolution rate, token efficiency, and latency, before advancing to the next stage. A cross-functional review board makes a formal go/no-go decision before any model is approved for user-facing deployment."
  - q: 13
    text: "All signal names and attributes follow the OTel GenAI Semantic Conventions"
  - q: 18
    text: "By default, the data does not include prompts, responses, or tool arguments."
sources:
  - https://github.com/github/docs/blob/main/content/copilot/responsible-use/agents.md
  - https://github.com/github/docs/blob/main/content/copilot/concepts/enterprise/opentelemetry.md
  - https://github.com/github/docs/blob/main/content/copilot/reference/copilot-cli-reference/cli-command-reference.md
  - https://github.com/github/docs/blob/main/content/copilot/reference/enterprise-administrators/agentic-audit-log-events.md
  - https://github.com/github/docs/blob/main/content/copilot/concepts/security-governance-and-network-settings/session-data.md
  - https://github.com/github/docs/blob/main/content/copilot/concepts/agents/about-third-party-coding-agents.md
  - https://github.com/github/docs/blob/main/content/copilot/how-tos/copilot-sdk/observability/opentelemetry.md
  - https://github.blog/ai-and-ml/generative-ai/under-the-hood-security-architecture-of-github-agentic-workflows/
tags:
  failure_definition: stated
  regression_detection: stated
  has_compared_cohorts: stated
  coding_agent_traces_flow_to: stated (OTLP export, audit log streaming)
  data_constraints.cannot_leave: stated (defaults)
  can_reproduce_failed_run: inferred (logs kept, no replay)
  would_emit_standard_signal: stated
  last_failure: unknown (not found)
```

## Evidence
- Copilot agents are evaluated with "industry-standard benchmarks (e.g., SWE-Bench) and internally developed evaluation suites", multiple runs per eval for nondeterminism, metrics resolution rate, token efficiency, latency and tool-call reliability; "monitored continuously in production via error rates, response latency, and aggregate usage patterns" (https://github.com/github/docs/blob/main/content/copilot/responsible-use/agents.md).
- New models pass a staged process: surface-specific benchmark suites, comparison to baselines and current production models, and a "cross-functional review board" go/no-go (same source). This gates model changes; nothing similar is described for prompt/tool changes.
- Benchmark tasks come from public repos and synthetic scenarios; "no real user queries or customer code are used" (same source), i.e. GitHub does not mine customer failures for its regression set.
- Copilot CLI: "All signal names and attributes follow the OTel GenAI Semantic Conventions", e.g. gen_ai.operation.name=invoke_agent, gen_ai.provider.name, gen_ai.agent.id/version, gen_ai.conversation.id (https://github.com/github/docs/blob/main/content/copilot/reference/copilot-cli-reference/cli-command-reference.md).
- Enterprises can enforce OTel config through managed settings that "cannot be overridden"; traces, metrics and events (e.g. edit accept/reject) go to any OTLP backend; content capture is off by default (https://github.com/github/docs/blob/main/content/copilot/concepts/enterprise/opentelemetry.md).
- Agentic audit log: actor:Copilot filter over 180 days, actor_is_agent and agent_session_id fields; streamed Copilot API usage records carry request/response bodies up to 1 MB (https://github.com/github/docs/blob/main/content/copilot/reference/enterprise-administrators/agentic-audit-log-events.md).
- Session data: CLI keeps full session records under ~/.copilot/session-state/ plus a SQLite store; local sessions sync to the GitHub account by default unless policy disables it; cloud-agent session logs persist on github.com and are visible to repo collaborators (https://github.com/github/docs/blob/main/content/copilot/concepts/security-governance-and-network-settings/session-data.md).
- Third-party agents (public preview): Anthropic Claude and OpenAI Codex run on GitHub under "the same security protections, mitigations, and limitations" as the Copilot cloud agent (https://github.com/github/docs/blob/main/content/copilot/concepts/agents/about-third-party-coding-agents.md).
- Agentic Workflows (Mar 2026): agent container behind a firewall, MCP gateway and model proxy hold credentials, writes staged through a safe-output service; network, proxy, gateway and container actions are logged at trust boundaries "for incident reconstruction" (https://github.blog/ai-and-ml/generative-ai/under-the-hood-security-architecture-of-github-agentic-workflows/, archived in github.com/aintnorest/knowledge-base-intelligent-systems).
- Responsible-use doc warns CLI may suggest "commands for file deletion or hard drive formatting" and "You are ultimately responsible for the commands executed" (https://github.com/github/docs/blob/main/content/copilot/responsible-use/agents.md).

## What this case says for Gate A
GitHub is the clearest "would emit a standard signal" yes: it already follows OTel GenAI semconv, links the MCP semconv, and lets enterprises enforce OTLP export. That makes a convention-plus-collector play credible on the GitHub surface, and as host of Claude and Codex agents, GitHub is a plausible aggregation point (Agent HQ) that could also become a competitor. Its regression gate covers model swaps with a formal board, but its eval data excludes customer tasks, so customers' own harness changes (instructions, hooks, MCP allowlists) are ungated, which is our wedge. No public harness-regression postmortem was found, so this case adds nothing to the pain counter.
