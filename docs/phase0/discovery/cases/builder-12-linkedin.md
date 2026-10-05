# LinkedIn: in-house agent platform (Hiring Assistant on LangGraph, plus background coding agents) that records every agent step by default; no public incident story

evidence_grade: B  (primary talks at QCon London 2025 and QCon AI NY 2025 and LinkedIn eng blog, seen through InfoQ/ZenML/snippets; strong on architecture and observability intent, silent on concrete failures)

```yaml
org: LinkedIn
role: Distinguished/Principal engineers on the agent platform (Karthik Ramgopal, Daniel Hewlett, Prince Valluri are the public voices)
track: builder
date: 2026-10-05
interviewer: desk-research agent
method: desk
harnesses_frameworks: [LangGraph (Hiring Assistant), in-house agent life-cycle service over LinkedIn messaging infra + gRPC, MCP, in-house background coding-agent orchestrator with sandboxes]   # stated
domain: other   # recruiting workflow agent; also coding (background agents producing PRs)
runs_per_day: unknown
failure_definition: unknown   # quality dimensions are named (hallucination rate, Responsible AI violation, coherence) for an earlier GenAI product
failure_rate_estimate: unknown
cost_per_failed_run: unknown
last_failure:
  symptom: "Single-LLM-block design could not be improved without side effects; moved to supervisor + sub-agents for quality isolation"   # inferred from QCon London summary
  detected_by: unknown
  time_to_why: unknown
  attributed_component: unknown   # LinkedIn names classes of systematic errors (retry spikes, ranking anomalies, drift vs Talent Graph) but no attributed incident
  recurred: unknown
  their_words: ""
harness_change:
  last_change: "Specs replaced free-form prompts for background coding agents; MCP adopted as tool layer"   # stated (QCon AI NY 2025)
  regression_detection: evals   # stated: moved from human annotation to automated evaluations; "AI-powered judges" evaluate quality against product policies; gating mechanism (CI vs manual) unknown
  silent_regression_experienced: unknown
  would_pay_to_prevent: unknown
controls_owned (fleets): []
tooling_today: [OpenTelemetry trace IDs on planner/skill/evaluator/memory events (secondary source), in-house orchestration audit trail, LangGraph Platform / LangSmith (per LangChain marketing; unconfirmed by LinkedIn)]
coding_agent_traces_flow_to: other   # stated: in-house orchestrator records "detailed traces of every action"; destination system unnamed
can_reproduce_failed_run: partially   # inferred: traces let engineers "reconstruct a complete reasoning path" (secondary source)
has_compared_cohorts: unknown
most_wanted_question: ""
data_constraints:
  cannot_leave: [customer_data]   # inferred: member/recruiter data over 1B profiles; LinkedIn builds platform in-house rather than buying; not explicitly stated as a policy
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: ai_platform   # inferred: central platform team owns orchestration, tooling and observability
credible_contract_size: unknown
automation_limits: "Human-in-the-loop by design; background-agent PRs go through standard code review"   # stated
would_allow_pause_stop_on_evidence: unknown
reaction:
  would_use_next_week: ""
  does_not_believe: ""
design_partner_candidate: unknown
referrals: []
quotes:
  - q: 13
    text: "Everything which agents are doing is observable by default, which means every step, every tool call, every decision, everything they're doing is audited."
  - q: 8
    text: "A spec is how we translate the developer's intent into something the agent can reliably execute"
sources:
  - https://www.infoworld.com/article/4054974/how-linkedin-built-an-agentic-ai-platform.html
  - https://www.infoq.com/news/2025/09/linkedin-multi-agent/
  - https://qconlondon.com/presentation/apr2025/lessons-learned-building-linkedins-first-agent-hiring-assistant
  - https://www.zenml.io/llmops-database/building-linkedin-s-first-production-agent-hiring-assistant-platform-and-architecture
  - https://www.infoq.com/news/2025/12/qcon-ai-linkedin/
  - https://earezki.com/ai-news/2025-12-19-qcon-ai-new-york-2025-ai-platform-scaling-at-linkedin/
  - https://www.infoq.com/presentations/ai-multi-agentic-tools/
  - https://mlsavvy.substack.com/p/part-3-inside-linkedins-ai-agents
  - https://blog.bytebytego.com/p/how-linkedin-built-an-ai-powered
  - https://leaddev.com/ai/how-linkedin-built-ai-hiring-agent
  - https://baoyu.io/translations/generative-ai/musings-on-building-a-generative-ai-product
tags:
  harnesses_frameworks: stated
  last_failure.symptom: inferred
  harness_change.last_change: stated
  harness_change.regression_detection: stated (evals) / unknown (gating)
  tooling_today: stated (in-house traces) / secondary (OTel trace IDs)
  coding_agent_traces_flow_to: stated (in-house, unnamed)
  can_reproduce_failed_run: inferred
  data_constraints.cannot_leave: inferred
  budget_owner: inferred
  automation_limits: stated
```

## Evidence
- LinkedIn reused its messaging infrastructure as the multi-agent orchestration layer; a stateless "agent life-cycle service" coordinates agents, with state held in conversational and experiential memory stores; agents expose gRPC interfaces (https://www.infoworld.com/article/4054974/how-linkedin-built-an-agentic-ai-platform.html; https://www.infoq.com/news/2025/09/linkedin-multi-agent/).
- Stated lessons: reuse infrastructure, design for human-in-the-loop, and "observability and context engineering have become essential for debugging, continuous improvement" (https://www.infoq.com/news/2025/09/linkedin-multi-agent/).
- QCon London 2025 (Ramgopal, Hewlett): moved from a single LLM block to a supervisor/sub-agent design for parallel development and "independent quality improvement without side effects"; moved from human annotation to automated evaluations to speed development (https://qconlondon.com/presentation/apr2025/lessons-learned-building-linkedins-first-agent-hiring-assistant; https://www.zenml.io/llmops-database/building-linkedin-s-first-production-agent-hiring-assistant-platform-and-architecture).
- Hiring Assistant quality framework: product-policy "rails" with minimum quality thresholds, enforced by AI-powered judges (https://blog.bytebytego.com/p/how-linkedin-built-an-ai-powered).
- Secondary analysis says every planner decision, skill invocation, evaluator judgment and memory write carries an OpenTelemetry trace ID, used to catch systematic errors visible only across many runs: "sudden spikes in retries, unusual ranking patterns, or drift between LLM outputs and Talent Graph signals" (https://mlsavvy.substack.com/p/part-3-inside-linkedins-ai-agents). Not confirmed on a LinkedIn-owned page.
- QCon AI NY 2025 (Valluri, Ramgopal): background coding agents turn structured specs into PRs inside sandboxes with scoped identity; the orchestrator records "detailed traces of every action taken"; everything is "observable by default" and audited (https://www.infoq.com/news/2025/12/qcon-ai-linkedin/; https://earezki.com/ai-news/2025-12-19-qcon-ai-new-york-2025-ai-platform-scaling-at-linkedin/).
- Named challenge: context fragmentation, and large-scale MCP use makes it hard to pick "the right tools to be called at the right time" (https://www.infoq.com/presentations/ai-multi-agentic-tools/).
- An earlier LinkedIn GenAI product used linguist-run annotation of up to 500 daily conversations scoring hallucination rate, Responsible AI violations, coherence and style, which drove prompt iteration (https://baoyu.io/translations/generative-ai/musings-on-building-a-generative-ai-product, translation of LinkedIn's eng blog post).

## What this case says for Gate A
LinkedIn is a sophisticated builder that already built its own trace-everything orchestrator and automated judge evals in-house, which makes it more of a "build" than a "buy" signal: the flight-recorder and audit pieces of our pitch already exist internally. The named systematic-error classes (retry spikes, ranking drift) map onto our failure-detection and cohort-comparison ideas, and tool-selection trouble at MCP scale is a non-model component pain, but nothing public describes a specific regression, its detection, or how harness changes are gated before release. No desk evidence for the regression-pain or replay counters; useful mainly as proof that large builders treat agent traces as first-class and keep them internal.
