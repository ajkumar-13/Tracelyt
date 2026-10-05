# Coinbase: code-first LangGraph agents after a six-week "Agentic AI Tiger Team"; deterministic nodes unit-tested, LLM nodes run under eval harnesses with an LLM judge; developer-support agents across Discord, Slack and an internal assistant on self-hosted LangSmith, with "build the glass box before the agent"

evidence_grade: B

Access note (pass 2, 2026-10-05): the primary Coinbase engineering post "Building enterprise AI agents at Coinbase: engineering for trust, scale, and repeatability", Evan Kormos's Interrupt 2026 talk ("How Coinbase Builds Developer Support Agents") and two ZenML summaries were reached through search snippets; direct fetch is egress-blocked. Anthropic's Coinbase page was fetched directly in pass 1. All pass-1 "carried" facts (LangGraph, LangSmith, "glass box") are now verified. Grade B: primary and specific on evaluation structure and observability, but no published failed-run story, no volumes for the agents, and no regression incident. For coding-agent fleet facts see fleet-12-coinbase.md.

```yaml
org: Coinbase
role: Enterprise Applications & Architecture (Agentic AI Tiger Team); Developer Platform support engineering (public: Evan Kormos; Varsha Mahadevan, Senior EM)
track: builder
date: 2026-10-05
interviewer: desk
method: desk
harnesses_frameworks: [LangGraph / LangChain code-first graphs ("data" nodes separated from "LLM" nodes), self-hosted LangSmith (tracing; adopted company-wide), Python services behind one HTTP back end serving Discord AI Chat, Slack Triage and a Support Engineer Assistant, MCP server for developer docs with RAG fallback, multi-layered guardrails, CB-GPT internal platform (35-50 apps), Claude (support chatbot)]
domain: support
runs_per_day: "unknown for the agents; support chatbot handles 'thousands of messages per hour'"
failure_definition: unknown
failure_rate_estimate: unknown
cost_per_failed_run: unknown
last_failure:
  symptom: "No failed-run story published. Stated risks engineered against: hallucination and jailbreaking (custom guardrails, 'different LLMs require varying amounts of tuning'), and remote MCP being unreliable (RAG fallback added)"
  detected_by: unknown
  time_to_why: unknown
  attributed_component: unknown
  recurred: unknown
  their_words: ""
harness_change:
  last_change: "Tiger Team standardised a code-first LangGraph pattern over six weeks (Institutional support, Onramp onboarding, Listing legal review); developer-support back end unified across three surfaces; RAG fallback added for unreliable remote MCP"
  regression_detection: evals
  silent_regression_experienced: unknown
  would_pay_to_prevent: unknown
controls_owned (fleets): [mcp_servers, permissions, ci_checks]
tooling_today: [self-hosted LangSmith (company-wide standard), LLM-as-judge spot checks and confidence scoring, curated eval datasets, unit tests for deterministic nodes, human-in-the-loop handoff designed into UX]
coding_agent_traces_flow_to: unknown (agent traces to self-hosted LangSmith; coding-agent traces not stated; see fleet-12)
can_reproduce_failed_run: partially
has_compared_cohorts: yes
most_wanted_question: unknown
data_constraints:
  cannot_leave: [customer_data, prompts]
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: ai_platform
credible_contract_size: unknown
automation_limits: "Human kept in the loop 'by designing the handoff and feedback loop into the UX'; interpretability and auditability required 'for human and regulatory trust'; financial compliance guardrails on the support chatbot"
would_allow_pause_stop_on_evidence: unknown
reaction:
  would_use_next_week: unknown
  does_not_believe: unknown
design_partner_candidate: unknown
referrals: [Evan Kormos, Varsha Mahadevan]
quotes:
  - q: 13
    text: "Build the glass box before the agent"
  - q: 13
    text: "Observability isn't a feature you add later. It's the base layer."
  - q: 9
    text: "Enterprise AI agents are software services that require the same rigor as any production system, plus interpretability and auditability for human and regulatory trust"
    paraphrase: true
  - q: 10
    text: "deterministic nodes—data retrieval, schema validation, business rule application—covered by conventional unit tests"
    paraphrase: true
  - q: 10
    text: "LLM steps run with evaluation harnesses and curated datasets, and Coinbase uses a second LLM as a judge for spot-checks and confidence scoring"
    paraphrase: true
  - q: 1
    text: "outperformed all competitors in our internal tests"
sources:
  - https://www.coinbase.com/blog/building-enterprise-AI-agents-at-Coinbase
  - https://www.zenml.io/llmops-database/building-enterprise-ai-agents-with-code-first-approach-for-trust-and-auditability
  - https://www.youtube.com/watch?v=py9d6zTl4Dc
  - https://www.zenml.io/llmops-database/scaling-ai-powered-developer-support-through-agentic-systems
  - https://medium.com/99p-labs/agents-at-scale-field-notes-from-langchains-2026-interrupt-conference-3abbbfab52d0
  - https://claude.com/customers/coinbase
  - docs/phase0/discovery/cases/fleet-12-coinbase.md
tags:
  harnesses_frameworks: stated (Coinbase blog; ZenML summary of Kormos talk; Anthropic page)
  runs_per_day: stated for chatbot only (Anthropic page)
  last_failure.symptom: stated as engineered-against risks (ZenML developer-support summary), not as an incident
  harness_change.last_change: stated (Coinbase blog; Kormos talk recap)
  regression_detection: stated (unit tests on deterministic nodes, eval harnesses with curated datasets on LLM nodes, LLM judge spot checks)
  controls_owned: inferred (own MCP server, guardrails, unit tests in CI)
  tooling_today: stated
  coding_agent_traces_flow_to: inferred-unknown (self-hosted LangSmith is the company-wide standard for agents; coding-agent traces not mentioned)
  can_reproduce_failed_run: inferred ("every tool call, retrieval, decision, and output is traced" implies reconstruction; replay not stated)
  has_compared_cohorts: stated (internal model tests; LLM judge confidence scoring)
  cannot_leave: inferred (self-hosted LangSmith rather than SaaS; regulatory auditability; "strict security and compliance standards")
  budget_owner: inferred (Enterprise Applications & Architecture team; company-wide AI team adopted the LangSmith deployment)
  automation_limits: stated
```

## Evidence
- Over six weeks an "Agentic AI Tiger Team" in Enterprise Applications and Architecture paved roads for building and hosting agents and set a blueprint for other teams; use cases were Institutional support, Onramp onboarding and Listing legal review (https://www.coinbase.com/blog/building-enterprise-AI-agents-at-Coinbase).
- Framing: agents "require the same rigor as any production system, plus interpretability and auditability for human and regulatory trust", which drove the code-first choice over low-code tools (https://www.coinbase.com/blog/building-enterprise-AI-agents-at-Coinbase ; https://www.zenml.io/llmops-database/building-enterprise-ai-agents-with-code-first-approach-for-trust-and-auditability).
- Code-first graphs (LangGraph/LangChain) give "typed interfaces, version control, clean separation of 'data' nodes from 'LLM' nodes, and the ability to attach observability, evaluation, and human-in-the-loop controls as first-class concerns" (https://www.coinbase.com/blog/building-enterprise-AI-agents-at-Coinbase).
- Evaluation is split by node type: deterministic data-fetch and transform steps are unit-tested; "LLM steps run with evaluation harnesses and curated datasets", with "a second LLM as a judge for spot-checks and confidence scoring" (https://www.coinbase.com/blog/building-enterprise-AI-agents-at-Coinbase ; https://www.zenml.io/llmops-database/building-enterprise-ai-agents-with-code-first-approach-for-trust-and-auditability).
- "Observability-first": "every tool call, retrieval, decision, and output is traced"; humans kept in the loop by designing handoff and feedback into the UX (https://www.coinbase.com/blog/building-enterprise-AI-agents-at-Coinbase).
- Interrupt 2026 (Evan Kormos): developer-support agent for the Coinbase Developer Platform runs across a Discord bot, Slack triage and an internal support-engineer assistant on one HTTP back end; the same MCP server for docs serves customer-facing and internal agents, with "RAG fallback for when remote MCP is unreliable"; "Build the glass box before the agent"; "Observability isn't a feature you add later. It's the base layer."; "The platform layer matters more than the agent" (https://medium.com/99p-labs/agents-at-scale-field-notes-from-langchains-2026-interrupt-conference-3abbbfab52d0 ; https://www.youtube.com/watch?v=py9d6zTl4Dc).
- The developer-support team built a hosted (self-hosted) LangSmith deployment that "was subsequently adopted company-wide by Coinbase's AI team" as the organisation-approved observability standard; custom guardrails against hallucination and jailbreaking were needed and "different LLMs require varying amounts of tuning" (https://www.zenml.io/llmops-database/scaling-ai-powered-developer-support-through-agentic-systems).
- Support chatbot: "thousands of messages per hour", financial-compliance guardrails, Claude chosen because it "outperformed all competitors in our internal tests"; 35-50 internal apps on CB-GPT (https://claude.com/customers/coinbase).

## What this case says for Gate A
Coinbase has institutionalised the two halves of what we sell, observability-first tracing and node-level evals, and did so on self-hosted LangSmith because of regulatory auditability. That is strong confirmation that traces must stay in-environment for this buyer class and that an incumbent trace store already exists. The explicit split between deterministic nodes (unit tests) and LLM nodes (evals plus judge) is a native form of component attribution, which suggests they would understand our pitch quickly but may believe they already have it. What is missing is any public failure or regression story, so this case contributes architecture and constraints, not pain. Counts: silent_regression unknown, attribution unknown, traces to LangSmith (self-hosted) for agents and unknown for coding agents, cannot_leave customer_data + prompts (inferred).
