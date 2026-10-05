# Factory (Droids): validator-gated Missions, internal evals for its router, and the most customer-controlled OTel export (content spans never sent to Factory)

evidence_grade: B

```yaml
org: Factory
role: harness vendor (Droid CLI, Droid exec, Missions, Factory Router, web app)
track: vendor
date: 2026-10-05
interviewer: desk-research agent (vendor track)
method: desk
harnesses_frameworks: [Droid, Missions (orchestrator / workers / validators)]
domain: coding
runs_per_day: unknown
failure_definition: "unmet behavioural assertions in a mission contract; validator-found issues"   # stated (Missions)
failure_rate_estimate: "one reported mission: no milestone passed first validation; 81 issues found; 21 of 61 features were fixes"   # stated
cost_per_failed_run: unknown
last_failure:
  symptom: "Mission example (Slack clone, 16.5 h): every milestone failed its first validation round; validators surfaced 81 issues"   # stated
  detected_by: ci                       # validators inside the harness
  time_to_why: unknown
  attributed_component: verification
  recurred: yes                         # repeated validation rounds (up to four)
  their_words: unknown
harness_change:
  last_change: unknown
  regression_detection: evals           # "Factory evaluations", Terminal Bench 2, Legacy Bench (router)
  silent_regression_experienced: unknown
  would_pay_to_prevent: unknown
controls_owned (fleets): n/a (vendor); exposes: [hierarchical org settings, model allow/deny lists, autonomy limits, command risk classification, Droid Shield DLP, hooks configuration, sandboxes, OTel export, audit log]
tooling_today: [Factory evaluations, Terminal Bench 2, Legacy Bench, Missions validators, Agent Readiness reports]
coding_agent_traces_flow_to: other     # customer OTLP collector (metrics fan-out; content spans only to customer)
can_reproduce_failed_run: unknown
has_compared_cohorts: unknown
most_wanted_question: unknown
data_constraints:
  cannot_leave: [prompts, tool_outputs, code]   # stated as design: message content spans "never reach Factory"; airgapped mode sends nothing
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: unknown
credible_contract_size: unknown
automation_limits: "autonomy limits per org; command risk classification; Droid Shield secret scanning; allow/deny lists"
would_allow_pause_stop_on_evidence: unknown
would_emit_standard_signal: partial     # emits OTLP but in a proprietary droid.* namespace, not gen_ai.*
reaction:
  would_use_next_week: unknown
  does_not_believe: unknown
design_partner_candidate: unknown
referrals: []
quotes:
  - q: 18
    text: "Message content is sent only to the collector you configure and never reaches Factory."
  - q: 13
    text: "Droid emits OTEL metrics, traces, and logs that can serve as fine‑grained audit data inside your own systems"
  - q: 18
    text: "In fully airgapped environments, Factory never receives any runtime data; you are responsible for all retention and residency decisions."
sources:
  - https://github.com/Factory-AI/factory/blob/main/docs/enterprise/telemetry-export.mdx
  - https://github.com/Factory-AI/factory/blob/main/docs/enterprise/compliance-audit-and-monitoring.mdx
  - https://github.com/Factory-AI/factory/blob/main/docs/enterprise/privacy-and-data-flows.mdx
  - https://github.com/Factory-AI/factory/blob/main/docs/enterprise/eu-deployment.mdx
  - https://github.com/Factory-AI/factory/blob/main/docs/enterprise/llm-safety-and-agent-controls.mdx
  - https://github.com/Factory-AI/factory/blob/main/docs/web/factory-router.mdx
  - https://factory.com/news/missions-architecture
  - https://www.zenml.io/llmops-database/enterprise-autonomous-software-engineering-with-ai-droids
  - https://jobs.ashbyhq.com/factory/2243dab2-62dc-4c64-b4bc-8f7314475607
tags:
  failure_rate_estimate: stated (single mission run)
  last_failure: stated
  attributed_component: inferred (failures caught at the verification stage)
  regression_detection: stated (router docs)
  coding_agent_traces_flow_to: stated
  data_constraints: stated
  would_emit_standard_signal: stated (droid.* namespace) / inferred (not gen_ai semconv)
```

## Evidence
- Droid exports OTLP metrics to a customer collector "in the same export cycle" as Factory's own; metrics are in a `droid.*` namespace (files_modified, tool.invocations, tool.execution_time, mcp.tool_invocations, hook.invocations, git.pull_requests) with user.id, organization.id, session.id attributes (https://github.com/Factory-AI/factory/blob/main/docs/enterprise/telemetry-export.mdx).
- With OTEL_LOG_MESSAGE_CONTENT, user/assistant messages and tool calls/results go out as trace spans (droid.message.user, droid.tool.call, droid.tool.result) to the customer endpoint only; if the endpoint equals Factory's collector, content logging is auto-disabled (same source).
- Compliance doc: customer-side OTel includes "Command execution metadata, including risk classification and outcome"; Factory-side audit logs record policy changes including "autonomy limits, Droid Shield settings, hooks configuration"; SOC 2, ISO 27001, ISO 42001 (https://github.com/Factory-AI/factory/blob/main/docs/enterprise/compliance-audit-and-monitoring.mdx).
- Deployment modes: cloud, hybrid, fully airgapped; recommends provider enterprise endpoints "to get first‑party zero‑retention guarantees"; an EU deployment exists for data-residency customers (https://github.com/Factory-AI/factory/blob/main/docs/enterprise/privacy-and-data-flows.mdx ; https://github.com/Factory-AI/factory/blob/main/docs/enterprise/eu-deployment.mdx).
- Factory Router claims 43% cost savings "while maintaining frontier-level performance in Factory evaluations", citing Terminal Bench 2 and Legacy Bench (https://github.com/Factory-AI/factory/blob/main/docs/web/factory-router.mdx).
- Missions (Apr 2026): orchestrator writes a behavioural-assertion contract; fresh validators gate each milestone; one 16.5 h run spent 37.2% of wall time validating; no milestone passed first validation, 81 issues, 21 fix features (https://factory.com/news/missions-architecture, archived in github.com/aintnorest/knowledge-base-intelligent-systems).
- Secondary: Factory reportedly stopped running SWE-bench in favour of behaviour specs with rubrics, and ships a "Reliability Droid" (https://www.zenml.io/llmops-database/enterprise-autonomous-software-engineering-with-ai-droids via research/09).
- Factory hires "AI Engineer (Droid reliability at scale)" (https://jobs.ashbyhq.com/factory/2243dab2-62dc-4c64-b4bc-8f7314475607 via research/09).

## What this case says for Gate A
Factory designs its telemetry for enterprises that will not let content leave: content spans go only to the customer collector, and airgapped mode sends Factory nothing. That validates the "cannot_leave" constraint and the "replay inside the customer environment" design, and it means Factory's own cross-customer regression analysis is blind to content, so in-environment tooling is the only place where failure analysis can run on content. Factory already emits OTLP, but in a proprietary `droid.*` namespace; adoption of a shared convention is plausible (they built the plumbing) but not evidenced. Its validator-gated Missions show the vendor treating verification as a first-class harness component.
