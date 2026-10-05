# monday.com: Sidekick V2, one agent over 200+ tools, failed from context pollution, LLM confusion and rising cost; rebuilt on LangGraph Deep Agents with three-tier tool discovery, sandboxed code execution and self-healing (94% recovery); monday Service gates every change with offline "safety net" regression evals in CI (162s to 18s) against real staging dependencies and online "monitor" evals on production traces

evidence_grade: A

Access note (2026-10-05): primary sources are LangChain's co-authored posts "Building monday.com Sidekick: why capable agents need more than just tools" and "monday Service + LangSmith: Building a Code-First Evaluation Strategy from Day 1", Omri Bruchim's Interrupt 2026 talk ("How Monday.com Built Sidekick on Deep Agents", YouTube, blocked), and three ZenML LLMOps-database summaries including the one named in the assignment ("Monday: Building an Evaluation-First Development Strategy for AI Service Agents"), plus a MetalBear webinar recap on staging evals. All reached through search snippets. Grade A: primary talk and vendor-co-authored posts with a concrete architecture failure, its cause and the eval gating that followed.

```yaml
org: monday.com
role: AI platform / Sidekick and monday Service agent engineering (public: Omri Bruchim)
track: builder
date: 2026-10-05
interviewer: desk
method: desk
harnesses_frameworks: [Sidekick V1 (simple ReAct loop), V2 (monolithic multi-agent, one agent per product division, 200+ tools), V3 (LangGraph Deep Agents: three-tier tool discovery base/context-specific/deferred-semantic-search, delegation-first sub-agents with middleware pipelines, Python code execution in LangChain sandbox replacing hundreds of tools, self-healing), monday Service role-based agents (LangGraph), LangSmith (tracing, evals, datasets, comparing implementations), Vitest, GitOps CI/CD, Kubernetes staging via MetalBear mirrord, Claude Code used in the engineering workflow]
domain: workflow
runs_per_day: unknown
failure_definition: "Stated: 'successful execution is not equivalent to a useful result'; they evaluate whether Sidekick 'selected the correct context, followed permissions, completed the task, and produced an answer the user could trust'; metrics: goal completion, correctness, tool selection, trajectory, groundedness, scope adherence"
failure_rate_estimate: "94% recovery success rate for self-healing in V3 (no base failure rate given)"
cost_per_failed_run: unknown
last_failure:
  symptom: "Sidekick V2: one agent handling 200+ tools (20+ per product domain, one agent per division: CRM, Service, Marketing) suffered 'context pollution everywhere, the LLM confused, costs rising, and it still wasn't working'"
  detected_by: dashboard
  time_to_why: unknown
  attributed_component: context
  recurred: yes
  their_words: "context pollution, LLM confusion, and cost explosion"
harness_change:
  last_change: "Rearchitected V2 to V3 on Deep Agents (progressive tool discovery, sub-agent delegation, sandboxed code execution, self-healing); monday Service added CI-gated offline evals and online multi-turn evaluators; eval loop sped up 8.7x (162s to 18s) by parallelising Vitest files and concurrent LLM-judge calls"
  regression_detection: ci
  silent_regression_experienced: unknown
  would_pay_to_prevent: unknown
controls_owned (fleets): [permissions, tool_allowlists, ci_checks]
tooling_today: [LangSmith (tracing, debugging, evals, datasets, implementation comparison), Vitest, GitOps CI/CD with evals as version-controlled code, LangChain sandbox, Kubernetes staging reached from local/CI via mirrord, Linear Slack bot to ticket, Claude Code for planning and code, system-prompt artifacts under review]
coding_agent_traces_flow_to: unknown (agent traces go to LangSmith; Claude Code is used in the dev workflow but its traces are not discussed)
can_reproduce_failed_run: partially
has_compared_cohorts: yes
most_wanted_question: unknown
data_constraints:
  cannot_leave: [customer_data]
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: ai_platform
credible_contract_size: unknown
automation_limits: "Agent must follow permissions and scope adherence is an eval criterion; code runs only in an isolated sandbox; own permission controls retained"
would_allow_pause_stop_on_evidence: unknown
reaction:
  would_use_next_week: unknown
  does_not_believe: unknown
design_partner_candidate: unknown
referrals: [Omri Bruchim]
quotes:
  - q: 1
    text: "one agent trying to handle 200+ tools, with context pollution everywhere, the LLM confused, costs rising, and it still wasn't working"
    paraphrase: true
  - q: 11
    text: "successful execution is not equivalent to a useful result"
  - q: 10
    text: "offline evals run against their staging environment with controlled datasets, gating changes before they ship, while online evals grade live agent behavior continuously after it is shipped to production"
    paraphrase: true
  - q: 10
    text: "8.7x faster evaluation feedback loops (from 162 seconds to 18 seconds)"
  - q: 9
    text: "stateful multi-step execution, explicit delegation to subagents, isolated execution for code and artifacts, integrated tracing and evaluation, and the ability to keep using our own tools, retrieval layer, models, and permission controls"
  - q: 10
    text: "Linear's Slack bot to convert conversation into ticket, planning with Claude Code, code and system-prompt artifacts, eval, review, deploy"
    paraphrase: true
sources:
  - https://www.langchain.com/blog/building-monday-com-sidekick-why-capable-agents-need-more-than-just-tools
  - https://www.youtube.com/watch?v=c2fLLS7np3Y
  - https://www.zenml.io/llmops-database/scaling-ai-agents-from-monolithic-to-multi-agent-architecture-with-deepagent
  - https://blog.langchain.com/customers-monday/
  - https://www.zenml.io/llmops-database/building-an-evaluation-first-development-strategy-for-ai-service-agents
  - https://www.zenml.io/llmops-database/running-agent-evaluations-against-real-staging-dependencies
  - https://dev.to/metalbear/how-mondaycom-runs-agent-evals-against-real-dependencies-webinar-recap-41ge
  - https://8thlight.com/insights/production-is-the-new-prototype-notes-from-langchain-interrupt-2026
  - https://medium.com/99p-labs/agents-at-scale-field-notes-from-langchains-2026-interrupt-conference-3abbbfab52d0
tags:
  harnesses_frameworks: stated (LangChain Sidekick post; ZenML summaries; 99P Labs notes on engineering workflow)
  failure_definition: stated (LangChain Sidekick post; ZenML eval-first summary for metric list)
  failure_rate_estimate: stated (94% recovery, ZenML Deep Agents summary)
  last_failure.symptom: stated (8th Light and 99P Labs notes on the Interrupt talk; ZenML summary)
  last_failure.detected_by: inferred (cost and quality were observed internally; no detection channel named)
  last_failure.attributed_component: stated as context pollution from tool count (context); tool sprawl is the proximate cause
  last_failure.recurred: inferred (described as a persistent state of V2, not a single event)
  harness_change.last_change: stated (all sources)
  regression_detection: stated (monday Service: CI gating with offline safety-net evals; online monitors)
  controls_owned: stated (permissions as eval criterion; own permission controls; CI)
  tooling_today: stated
  can_reproduce_failed_run: inferred (production traces are evaluated online and datasets are replayed offline against real staging dependencies; replay of a specific failed production run is not stated)
  has_compared_cohorts: stated (LangSmith used for "comparing different agent implementations")
  cannot_leave: inferred (customer work-management data across CRM/Service; staging evals are kept in their own Kubernetes)
  budget_owner: inferred
```

## Evidence
- Sidekick evolved from a simple ReAct loop (V1) through "a problematic monolithic multi-agent system with over 200 tools (V2)" to a Deep Agents architecture (V3); V2 "suffered from context pollution, confused LLMs, and rising costs due to too many tools and infinite contexts across different domains like Monday CRM, Monday Service, and Monday Marketing" (https://www.zenml.io/llmops-database/scaling-ai-agents-from-monolithic-to-multi-agent-architecture-with-deepagent).
- Interrupt 2026 (Omri Bruchim): V2 "added 20+ tools per product domain, each division getting its own agent. That version failed due to context pollution, LLM confusion, and cost explosion"; V3 uses "progressive tool discovery: a three-tier system where the agent only sees the tools relevant to its current context, with a third tier of semantically searchable tools it can activate on demand" (https://8thlight.com/insights/production-is-the-new-prototype-notes-from-langchain-interrupt-2026).
- V3 principles: three-tier tool discovery, delegation-first sub-agents with middleware pipelines, Python code execution in a LangChain sandbox "to replace hundreds of specific tools", and self-healing, "result[ing] in a 94% recovery success rate" (https://www.zenml.io/llmops-database/scaling-ai-agents-from-monolithic-to-multi-agent-architecture-with-deepagent).
- Why Deep Agents: "stateful multi-step execution, explicit delegation to subagents, isolated execution for code and artifacts, integrated tracing and evaluation, and the ability to keep using our own tools, retrieval layer, models, and permission controls" (https://www.langchain.com/blog/building-monday-com-sidekick-why-capable-agents-need-more-than-just-tools).
- Evaluation philosophy: "successful execution is not equivalent to a useful result"; they evaluate whether Sidekick "selected the correct context, followed permissions, completed the task, and produced an answer the user could trust", combining offline evals with production signals (https://www.langchain.com/blog/building-monday-com-sidekick-why-capable-agents-need-more-than-just-tools).
- monday Service: evaluation embedded "from Day 0" as "offline 'safety net' evaluations for regression testing and online 'monitor' evaluations for real-time production quality"; LangGraph + LangSmith + Vitest; "8.7x faster evaluation feedback loops (from 162 seconds to 18 seconds)"; "GitOps-style CI/CD deployment with evaluations managed as version-controlled code" (https://blog.langchain.com/customers-monday/ ; https://www.zenml.io/llmops-database/building-an-evaluation-first-development-strategy-for-ai-service-agents).
- Evals run against "a real, isolated pre-production environment rather than relying solely on mocks", connecting local or CI agent code to Kubernetes staging services (auth, permissions, databases, integrations, queues) "without deploying a new agent version"; criteria: goal completion, correctness, tool selection, trajectory, groundedness, scope adherence; "offline evals ... gating changes before they ship, while online evals grade live agent behavior continuously" (https://www.zenml.io/llmops-database/running-agent-evaluations-against-real-staging-dependencies ; https://dev.to/metalbear/how-mondaycom-runs-agent-evals-against-real-dependencies-webinar-recap-41ge).
- Engineering workflow: "Linear's Slack bot to convert conversation into ticket, planning with Claude Code, code and system-prompt artifacts, eval, review, deploy"; LangSmith for "tracing, debugging, evaluations, dataset management, and comparing different agent implementations" (https://medium.com/99p-labs/agents-at-scale-field-notes-from-langchains-2026-interrupt-conference-3abbbfab52d0).

## What this case says for Gate A
monday.com gives a named harness failure with a non-model cause (tool sprawl polluting context) that was detected through cost and quality, fixed by re-architecting the harness, and then institutionalised as CI-gated regression evals plus online monitors, which is the regression-gating loop we propose. System prompts are treated as reviewed artifacts in the same pipeline as code, and trajectory and tool-selection are explicit eval criteria, so component attribution is a native concept here. The caution is the same as Lyft and Coinbase: they built it on LangSmith and are a LangChain showcase, so we would be a complement to an incumbent. Nothing public covers run volumes, time-to-root-cause or data residency. Counts: silent_regression unknown (V2 failure was visible, not silent), attribution = context, traces to LangSmith, cannot_leave customer_data (inferred).
