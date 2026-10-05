# Cisco (CX): LangGraph supervisor agents over ~1.7–1.8M support cases a year; public record is about architecture and outcomes, not failures

evidence_grade: B  (primary Cisco blogs and two Interrupt talks exist, but every detail seen is from search snippets; no failure story, no eval-gating mechanism described)

```yaml
org: Cisco (Customer Experience / CX)
role: Fellow & Chief Architect, CX (Carlos Pereira) is the public voice
track: builder
date: 2026-10-05
interviewer: desk-research agent
method: desk
harnesses_frameworks: [LangGraph, LangGraph Platform, LangSmith]   # stated
domain: support
runs_per_day: unknown   # stated proxies: "25,000+ customer workflows weekly" in-product; ~1.7M annual support cases; 145,000 cases resolved fully by AI in FY2026
failure_definition: unknown
failure_rate_estimate: unknown
cost_per_failed_run: unknown
last_failure:
  symptom: "Early single monolithic agent struggled to maintain accuracy, explainability, and trust as workflows became more complex"   # stated (design-time, not an incident)
  detected_by: unknown   # internal experiments; not a production detection channel
  time_to_why: unknown
  attributed_component: context   # inferred: Cisco says systems failed in real-world use because they "lacked understanding of user intent, system status, operational limits, and lifecycle context", and made "context a first-class concern"
  recurred: unknown
  their_words: "struggled in real-world scenarios because they lacked understanding of user intent, system status, operational limits, and lifecycle context"   # snippet wording of Cisco blog
harness_change:
  last_change: "Moved from a monolithic assistant to specialized cooperating agents (Case Management, Configuration Analysis, PSIRT/Field Notice) under a supervisor"   # stated
  regression_detection: unknown   # LangSmith tracing stated; a talk exists on "Observing and Testing CX Agents" closing the loop from production feedback, contents not visible
  silent_regression_experienced: unknown
  would_pay_to_prevent: unknown
controls_owned (fleets): []
tooling_today: [LangSmith (tracing all supervisor-agent interactions), Splunk/Cisco observability (inferred from on-prem blog mentioning observability stack)]
coding_agent_traces_flow_to: unknown
can_reproduce_failed_run: unknown
has_compared_cohorts: unknown
most_wanted_question: ""
data_constraints:
  cannot_leave: [customer_data]   # inferred: Cisco chose on-prem for AI workloads processing sensitive customer information, citing data sovereignty
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: unknown
credible_contract_size: unknown
automation_limits: "Graduated trust: medium-confidence decisions trigger validation, low-confidence decisions escalate to human review"   # stated (CX Today / Cisco)
would_allow_pause_stop_on_evidence: unknown
reaction:
  would_use_next_week: ""
  does_not_believe: ""
design_partner_candidate: unknown
referrals: []
quotes:
  - q: 4
    text: "catching the broken steps faster"
    note: Pereira on retrofitting AI onto a broken workflow (Interrupt 2026 recap)
  - q: 1
    text: "a single monolithic agent struggled to maintain accuracy, explainability, and trust as workflows became more complex"
    paraphrase: true
sources:
  - https://x.com/LangChain/status/1926368790062703043
  - https://www.zenml.io/llmops-database/multi-agent-ai-platform-for-customer-experience-at-scale
  - https://blogs.cisco.com/cisco-on-cisco/how-cisco-architected-ai-driven-support-and-validated-against-industry-benchmarks
  - https://blogs.cisco.com/cisco-on-cisco/cx-on-premises-ai-infrastructure-deployment
  - https://www.cxtoday.com/service-management-connectivity/cisco-agentic-ai-145000-support-cases/
  - https://medium.com/99p-labs/agents-at-scale-field-notes-from-langchains-2026-interrupt-conference-3abbbfab52d0
  - https://www.youtube.com/watch?v=AqU_WyOdEyo
  - https://www.youtube.com/watch?v=McZgnvn-e84
tags:
  harnesses_frameworks: stated
  runs_per_day: stated (proxies only)
  last_failure.symptom: stated (design-time)
  last_failure.attributed_component: inferred
  harness_change.last_change: stated
  tooling_today: stated (LangSmith) / inferred (observability stack)
  data_constraints.cannot_leave: inferred
  automation_limits: stated
```

## Evidence
- Cisco "automated 60% of 1.8 million support cases with LangGraph, LangSmith, and LangGraph Platform" (LangChain promo of Pereira's Interrupt 2025 talk) (https://x.com/LangChain/status/1926368790062703043).
- Supervisor agent decomposes natural-language queries and routes to renewals, adoption, delivery, sentiment and installed-base agents, sometimes in parallel; CX is a 20,000-person org managing $26B recurring revenue; LangSmith traces supervisor-agent interactions; 95% accuracy in risk recommendations and 20% less operational time after three weeks of limited availability (https://www.zenml.io/llmops-database/multi-agent-ai-platform-for-customer-experience-at-scale).
- Early internal experiments: a single monolithic agent "struggled to maintain accuracy, explainability, and trust"; systems looked strong in demos but failed in real-world scenarios for lack of user intent, system status, operational limits and lifecycle context; design principle "operational reliability over demo polish" (https://blogs.cisco.com/cisco-on-cisco/how-cisco-architected-ai-driven-support-and-validated-against-industry-benchmarks).
- 25,000+ customer workflows per week through in-product self-service, 250,000+ users, 25–30% faster resolution, ~1.7M annual support cases (same Cisco blog).
- 145,000 support cases resolved entirely by AI with zero human intervention in FY2026; medium-confidence decisions trigger validation, low-confidence escalate to human review (https://www.cxtoday.com/service-management-connectivity/cisco-agentic-ai-145000-support-cases/).
- CX moved agentic workloads on-prem (UCS, Nexus 9000) because cloud "data sovereignty challenges" were "untenable" for sensitive customer data, and because unpredictable inference made token costs "skyrocket" (https://blogs.cisco.com/cisco-on-cisco/cx-on-premises-ai-infrastructure-deployment).
- Interrupt 2026: Pereira framed AI as runtime rather than tool; agents evolved from chat assistant to workflow-bound agents beside human decision points (https://medium.com/99p-labs/agents-at-scale-field-notes-from-langchains-2026-interrupt-conference-3abbbfab52d0).
- A second talk, "Observing and Testing CX Agents", is described as showing how to "close the loop between production feedback" and testing; its specifics were not retrievable (https://www.youtube.com/watch?v=AqU_WyOdEyo).

## What this case says for Gate A
Cisco CX is a real, high-volume builder with a multi-agent supervisor harness and an explicit interest in observing and testing agents, so the problem category is live for them. But the public record holds no production incident, no time-to-root-cause, and no description of how harness changes are gated; the "failure" visible is a design-time lesson (monolith to specialists, context as first-class), which points at context/orchestration rather than the model. The on-prem decision on sovereignty grounds is the strongest signal: any replay or flight-recorder product would have to run inside Cisco's environment. Treat it as a qualified target whose pain must be confirmed live; it adds nothing to the regression-pain counter on desk evidence alone.
