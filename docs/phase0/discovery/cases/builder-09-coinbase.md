# Coinbase: LangGraph + LangSmith multi-agent support and an internal CB-GPT platform; "black box to glass box" framing, but no failure detail reachable this pass

evidence_grade: C

Access note: Coinbase's primary blog post (https://www.coinbase.com/blog/building-enterprise-AI-agents-at-Coinbase) and Evan Kormos's Interrupt 2026 talk could not be reached, and the web-search budget was used up before this case. Anthropic's Coinbase customer page was fetched directly. The LangGraph/LangSmith and "glass box" facts are carried forward from the target list without re-checking. For coding-agent fleet facts, see fleet-12-coinbase.md.

```yaml
org: Coinbase
role: Agent platform / developer support EM (public: Evan Kormos; Varsha Mahadevan, Senior EM)
track: builder
date: 2026-10-05
interviewer: desk
method: desk
harnesses_frameworks: [LangGraph (carried), LangSmith (carried), CB-GPT internal platform, Claude (support chatbot)]
domain: support
runs_per_day: "unknown runs; support chatbot handles 'thousands of messages per hour' (stated)"
failure_definition: unknown
failure_rate_estimate: unknown
cost_per_failed_run: unknown
last_failure:
  symptom: unknown
  detected_by: unknown
  time_to_why: unknown
  attributed_component: unknown
  recurred: unknown
  their_words: ""
harness_change:
  last_change: unknown
  regression_detection: evals (stated only as "internal tests" and "performance benchmarks" for model selection)
  silent_regression_experienced: unknown
  would_pay_to_prevent: unknown
controls_owned (fleets): []
tooling_today: [LangSmith (carried)]
coding_agent_traces_flow_to: unknown (agent traces to LangSmith carried; coding-agent traces unknown)
can_reproduce_failed_run: unknown
has_compared_cohorts: yes (stated: Claude "outperformed all competitors in our internal tests")
most_wanted_question: unknown
data_constraints:
  cannot_leave: [customer_data]
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: unknown
credible_contract_size: unknown
automation_limits: "Support chatbot runs with 'robust financial compliance guardrails'"
would_allow_pause_stop_on_evidence: unknown
reaction:
  would_use_next_week: unknown
  does_not_believe: unknown
design_partner_candidate: unknown
referrals: [Evan Kormos, Varsha Mahadevan]
quotes:
  - q: 1
    text: "outperformed all competitors in our internal tests"
  - q: 2
    text: "black box to glass box"
    paraphrase: true
sources:
  - https://claude.com/customers/coinbase
  - https://www.coinbase.com/blog/building-enterprise-AI-agents-at-Coinbase
  - docs/phase0/discovery/cases/fleet-12-coinbase.md
tags:
  volumes_guardrails_model_eval: stated (claude.com)
  langgraph_langsmith_glass_box: carried from 09-interview-targets.md, not re-verified
  cannot_leave: inferred (regulated exchange; "strict security and compliance standards" stated)
```

## Evidence
- The Claude-based support chatbot handles "thousands of messages per hour" for several million users across 100+ geographies (https://claude.com/customers/coinbase).
- Coinbase built "robust financial compliance guardrails" into the chatbot and says Claude "met all our security requirements" (https://claude.com/customers/coinbase).
- Model choice came from internal tests: Claude "outperformed all competitors in our internal tests" (Varsha Mahadevan) (https://claude.com/customers/coinbase).
- 35-50 internal applications were built on the CB-GPT platform (https://claude.com/customers/coinbase).
- Carried, not re-verified: the multi-agent developer-support system runs on LangGraph and LangSmith, and Coinbase talked publicly about moving from "black box to glass box" observability (https://www.coinbase.com/blog/building-enterprise-AI-agents-at-Coinbase).

## What this case says for Gate A
Coinbase cares publicly about observability ("glass box") and works in a compliance-heavy setting where traces probably cannot leave. That makes it a natural candidate for in-environment replay, but the evidence is inference and carried facts only. It contributes no verified failure, regression or replay evidence. LangSmith already holds its agent traces, so we would be competing with an incumbent.
