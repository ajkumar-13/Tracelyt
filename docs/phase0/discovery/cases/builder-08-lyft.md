# Lyft: Claude-based customer-care agent evaluated on accuracy and brand tone; publicly described an offline-simulator vs production gap

evidence_grade: C

Access note: the primary talk (Nick Ung, Interrupt 2026, "Building Evals That Actually Matter in Production", https://interrupt.langchain.com/recordings) could not be reached, and the web-search budget was used up before this case. Anthropic's Lyft customer page was fetched directly. The simulator-gap fact is carried forward from the target list without re-checking.

```yaml
org: Lyft
role: Safety & Customer Care AI (public: Nick Ung)
track: builder
date: 2026-10-05
interviewer: desk
method: desk
harnesses_frameworks: [Claude (customer care assistant), LangSmith evals (carried), LLM-as-user simulator (carried)]
domain: support
runs_per_day: unknown
failure_definition: unknown
failure_rate_estimate: "carried: ~90% success on the offline simulator, poor in production (unverified)"
cost_per_failed_run: unknown
last_failure:
  symptom: "carried: agent that scored ~90% on the LLM-as-user simulator underperformed in production (unverified)"
  detected_by: production_users (inferred from carried fact)
  time_to_why: unknown
  attributed_component: verification (inferred: the offline eval did not predict production; the failure is in the evaluation harness)
  recurred: unknown
  their_words: ""
harness_change:
  last_change: unknown
  regression_detection: evals (carried: LangSmith evals with simulator; stated: multi-model testing on accuracy and tone)
  silent_regression_experienced: unknown
  would_pay_to_prevent: unknown
controls_owned (fleets): []
tooling_today: [LangSmith (carried)]
coding_agent_traces_flow_to: unknown
can_reproduce_failed_run: unknown
has_compared_cohorts: yes (stated: tested multiple AI models quantitatively and qualitatively)
most_wanted_question: unknown
data_constraints:
  cannot_leave: [customer_data]
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: unknown
credible_contract_size: unknown
automation_limits: "Safety concerns, complex disputes and cases needing empathy are routed to human agents with AI-generated summaries"
would_allow_pause_stop_on_evidence: unknown
reaction:
  would_use_next_week: unknown
  does_not_believe: unknown
design_partner_candidate: unknown
referrals: [Nick Ung]
quotes:
  - q: 1
    text: "accuracy of the response and the ability of the AI models to have the tone and persona that represented our brand"
sources:
  - https://claude.com/customers/lyft
  - https://interrupt.langchain.com/recordings
tags:
  resolution_time_and_routing: stated (claude.com)
  model_comparison: stated (claude.com)
  simulator_gap_and_langsmith: carried from 09-interview-targets.md, not re-verified
  attributed_component: inferred
  cannot_leave: inferred (rider/driver support data)
```

## Evidence
- Lyft's Claude-based support assistant cut resolution time by more than 87%; before it, riders waited 30-40 minutes to reach an agent (https://claude.com/customers/lyft).
- Lyft tested several models both quantitatively and qualitatively, judging "accuracy of the response and the ability of the AI models to have the tone and persona that represented our brand" (https://claude.com/customers/lyft).
- Safety concerns, complex disputes and cases needing empathy are routed to human agents with AI-generated summaries (https://claude.com/customers/lyft).
- Decision-making accuracy is reported as improved by more than 30%; savings were reinvested in support-agent upskilling (https://claude.com/customers/lyft).
- Carried, not re-verified: at Interrupt 2026 Nick Ung described ~90% success on an LLM-as-user simulator alongside poor production performance, with LangSmith used for evals (https://interrupt.langchain.com/recordings).

## What this case says for Gate A
If the carried fact holds, Lyft is direct evidence that offline evals can pass while production fails. That supports gating on production traces and replay rather than on synthetic suites alone. It is a support agent, not a coding agent, and has no public harness-change regression story. The pain and replay counters stay at zero until the talk is verified.
