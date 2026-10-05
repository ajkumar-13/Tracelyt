# PagerDuty: LangGraph SRE agent ("Paige") with parallel hypothesis sub-agents over 46 production tools; a single-agent design hit "context rot" (more context, worse decisions, slower, costlier) and 10+ minute diagnoses; quality is gated by LLM-judge evals plus human sampling and dogfooding on real incidents

evidence_grade: B

Access note (pass 2, 2026-10-05): PagerDuty's two engineering posts ("Inside PagerDuty's SRE Agent: How We Built Deep Incident Investigation" by Viktor Vasylkovskyi, Micah Mayo and Ralph Bird; "Context Over Cleverness: Building PagerDuty's SRE Agent") and two product posts (memory, enhancements) were reached through search snippets; direct fetch is egress-blocked. All pass-1 "carried" facts are now verified. Grade B: primary and specific on architecture and the context-rot failure, but no single production incident with detection path and time-to-root-cause, and no numbers on run volume or failure rate.

```yaml
org: PagerDuty
role: AI agent platform engineering (public: Micah Mayo, Staff SWE; Viktor Vasylkovskyi, Senior SWE; Ralph Bird)
track: builder
date: 2026-10-05
interviewer: desk
method: desk
harnesses_frameworks: [LangGraph orchestration, coordinator + parallel hypothesis sub-agents, 46 production tools (logs, metrics, traces, runbooks via Datadog, CloudWatch, Grafana, Splunk, Dynatrace, Confluence, GitHub), tenant-isolated memory (service observations, incident recollections, human-promoted playbooks), PagerDuty MCP server]
domain: other (SRE incident investigation, multi-tenant SaaS product)
runs_per_day: unknown
failure_definition: "inferred: investigation that is slow, wrong-weighted or hallucinated; the first-message 'read and recommendation' had to be 'immediately useful'"
failure_rate_estimate: unknown
cost_per_failed_run: "unknown; context-rot regime 'took longer and cost more'"
last_failure:
  symptom: "Single-agent design: feeding large incident-context documents (JSON blobs of alerts, past incidents, service topology, dependency graphs, historical patterns, remediation options) caused 'context rot'; beyond a threshold the model 'struggled to weight information correctly, resulting in worse decisions as more data was added'; sequential log search and recall meant an incident with 3-4 candidate root causes took 10+ minutes"
  detected_by: dashboard
  time_to_why: unknown
  attributed_component: context
  recurred: yes
  their_words: "a ceiling on how much context they could give a single agent before it started making worse calls, which took longer and cost more"
harness_change:
  last_change: "Re-architecture from single agent to coordinator + parallel sub-agents, each receiving only the context relevant to its hypothesis; three sub-agent execution modes evaluated, including dispatch-all-then-block-until-slowest; prompt change telling the agent to say when it does not know and ask for what it needs"
  regression_detection: evals
  silent_regression_experienced: unknown
  would_pay_to_prevent: unknown
controls_owned (fleets): [tool_allowlists, permissions]
tooling_today: [LangGraph, LLM-judge evals, human sampling, dogfooding on internal real incidents, early-access customer feedback, memory API]
coding_agent_traces_flow_to: unknown
can_reproduce_failed_run: partially
has_compared_cohorts: yes
most_wanted_question: unknown
data_constraints:
  cannot_leave: [customer_data]
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: ai_platform
credible_contract_size: unknown
automation_limits: "Memory is per-tenant and never used for cross-customer learning; agent and evals configured for 'deterministic output over creativity'; agent instructed to say when it does not know; diagnostics run automatically, remediation recommended/executed under human control"
would_allow_pause_stop_on_evidence: unknown
reaction:
  would_use_next_week: unknown
  does_not_believe: unknown
design_partner_candidate: unknown
referrals: [Micah Mayo, Viktor Vasylkovskyi, Ralph Bird]
quotes:
  - q: 1
    text: "Beyond a certain threshold, the model struggled to weight information correctly, resulting in worse decisions as more data was added."
    paraphrase: true
  - q: 4
    text: "This created a ceiling on how much context they could give a single agent before it started making worse calls, which took longer and cost more."
    paraphrase: true
  - q: 9
    text: "formulates candidate root causes like DNS resolution failure, a bad deploy, or downstream dependency timeout, and spawns a sub-agent for each"
    paraphrase: true
  - q: 10
    text: "building evals to check quality and relevance, using LLM judges and human sampling, and configuring both the agent and evals for deterministic output over creativity"
    paraphrase: true
  - q: 4
    text: "Telling the agent to say when it doesn't know and to ask for what it needs reduced hallucination"
    paraphrase: true
sources:
  - https://www.pagerduty.com/eng/inside-pagerdutys-sre-agent-how-we-built-deep-incident-investigation/
  - https://www.pagerduty.com/eng/context-over-cleverness-building-pagerdutys-sre-agent/
  - https://www.pagerduty.com/blog/ai/we-built-an-sre-agent-with-memory-and-its-transforming-incident-response/
  - https://www.pagerduty.com/blog/ai/new-enhancements-to-pagerdutys-sre-agent-triage-faster-without-waking-a-human/
  - https://support.pagerduty.com/main/docs/sre-agent
tags:
  harnesses_frameworks: stated (eng post: LangGraph, parallel sub-agents, 46 tools; support docs and product posts: tool integrations, memory API)
  failure_definition: inferred (from "immediately useful" first message requirement)
  last_failure.symptom: stated (eng post, via snippets)
  last_failure.detected_by: inferred (dashboard: slowness and cost were measured; source does not name the detection channel)
  last_failure.attributed_component: stated as context ("context rot")
  last_failure.recurred: inferred (described as a regime that worsened as sources were added, not a one-off)
  harness_change.last_change: stated (eng post)
  regression_detection: stated ("Context Over Cleverness": evals with LLM judges and human sampling; dogfooding; early-access gap finding)
  controls_owned: inferred (product-level tool integrations and memory promotion by humans)
  has_compared_cohorts: inferred (three sub-agent execution modes compared; single vs multi-agent compared)
  can_reproduce_failed_run: inferred (dogfooding on real incident data and evals imply replayable incident inputs; not stated as replay of a failed run)
  cannot_leave: inferred (multi-tenant product; memory explicitly tenant-isolated)
  budget_owner: inferred
  automation_limits: stated (memory post, eng posts)
```

## Evidence
- Authors Viktor Vasylkovskyi, Micah Mayo and Ralph Bird documented "architecture decisions, patterns that worked, traps encountered, and infrastructure layers" needed to make deep investigation "reliable in production" (https://www.pagerduty.com/eng/inside-pagerdutys-sre-agent-how-we-built-deep-incident-investigation/).
- Context rot: as the single agent was fed alerts, past incidents, service topology, dependency graphs, historical patterns and remediation options as JSON, "beyond a certain threshold, the model struggled to weight information correctly, resulting in worse decisions as more data was added" (https://www.pagerduty.com/eng/inside-pagerdutys-sre-agent-how-we-built-deep-incident-investigation/).
- Sequential execution: log searches and past-incident recall were slow, so "a moderately complex incident with three or four candidate root causes could take 10+ minutes to diagnose" (https://www.pagerduty.com/eng/inside-pagerdutys-sre-agent-how-we-built-deep-incident-investigation/).
- Fix: a coordinator delegates to sub-agents that "each receive only context relevant to their specific tasks"; the agent "formulates candidate root causes like DNS resolution failure, a bad deploy, or downstream dependency timeout, and spawns a sub-agent for each" to query logs and metrics and report evidence for or against (https://www.pagerduty.com/eng/inside-pagerdutys-sre-agent-how-we-built-deep-incident-investigation/).
- Three ways to run sub-agents are discussed, including dispatching all at once synchronously and blocking "until the slowest one finishes before synthesizing" (https://www.pagerduty.com/eng/inside-pagerdutys-sre-agent-how-we-built-deep-incident-investigation/).
- Scale: "LangGraph orchestration with parallel subagents to run structured investigation across 46 production tools" (https://www.pagerduty.com/eng/inside-pagerdutys-sre-agent-how-we-built-deep-incident-investigation/).
- Evaluation: the team built "evals to check quality and relevance, using LLM judges and human sampling", configured "both the agent and evals for deterministic output over creativity", dogfooded "using real incident data from their own teams", and "identified gaps through real use" during internal release and early access (https://www.pagerduty.com/eng/context-over-cleverness-building-pagerdutys-sre-agent/).
- Hallucination control: "Telling the agent to say when it doesn't know and to ask for what it needs reduced hallucination" (https://www.pagerduty.com/eng/context-over-cleverness-building-pagerdutys-sre-agent/).
- The first unprompted message on incident open had to be "immediately useful", which "raised the bar" (https://www.pagerduty.com/eng/context-over-cleverness-building-pagerdutys-sre-agent/).
- Memory: service-scoped observations, incident recollections and human-promoted playbooks; "memory isn't used for cross-customer learning, and each tenant's memory stays isolated" (https://www.pagerduty.com/blog/ai/we-built-an-sre-agent-with-memory-and-its-transforming-incident-response/).
- Product-side outcome claims (customer case): MTTA 2-3 hours to 5 minutes, critical MTTR 3 hours to under 30 minutes (https://www.pagerduty.com/blog/ai/we-built-an-sre-agent-with-memory-and-its-transforming-incident-response/).

## What this case says for Gate A
PagerDuty's own account attributes its main agent failure to context, not the model: adding more sources made the single agent slower, costlier and wrong-weighted, and the fix was a harness change (sub-agent decomposition and context scoping), validated by LLM-judge evals, human sampling and dogfooding. That is a textbook non-model attribution and a harness-change gating story, though the detection path and time-to-root-cause are not published. The multi-agent, fan-out design is exactly where subagent attribution and first-divergence matter. Two cautions: PagerDuty sells incident tooling and may treat agent reliability as core IP rather than buy it, and tenant isolation of memory suggests customer telemetry cannot leave, so any replay would have to run inside PagerDuty's environment. Counts: attribution = context, silent_regression unknown, traces unknown, cannot_leave customer_data (inferred).
