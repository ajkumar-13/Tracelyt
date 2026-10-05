# Clay: Claygent web-research agent at very high volume (~350M runs/month carried); public material is about cost and model choice, not failures

evidence_grade: C

Access note: the Interrupt 2026 recap (https://8thlight.com/insights/production-is-the-new-prototype-notes-from-langchain-interrupt-2026) was blocked, and the web-search budget was used up before this case. Anthropic's Clay customer page (an older case study) was fetched directly. The volume numbers are carried forward from the target list without re-checking.

```yaml
org: Clay
role: AI platform / Claygent (public: Jeff Barg; Adam Eldefrawy, Software Engineer)
track: builder
date: 2026-10-05
interviewer: desk
method: desk
harnesses_frameworks: [Claygent (custom), Claude 3 Haiku (customer-preferred model at the time of the case study), LangSmith (carried, uncertain)]
domain: research
runs_per_day: "~11.7M (carried: ~350M agent runs/month; 1B+ total; unverified)"
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
  regression_detection: unknown
  silent_regression_experienced: unknown
  would_pay_to_prevent: unknown
controls_owned (fleets): []
tooling_today: [LangSmith (carried, flagged uncertain in target list)]
coding_agent_traces_flow_to: unknown
can_reproduce_failed_run: unknown
has_compared_cohorts: unknown
most_wanted_question: unknown
data_constraints:
  cannot_leave: unknown
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: unknown
credible_contract_size: unknown
automation_limits: unknown
would_allow_pause_stop_on_evidence: unknown
reaction:
  would_use_next_week: unknown
  does_not_believe: unknown
design_partner_candidate: unknown
referrals: [Jeff Barg]
quotes:
  - q: 1
    text: "You can scale and do a lot more volume on Haiku a lot more cheaply than any other model"
sources:
  - https://claude.com/customers/clay
  - https://8thlight.com/insights/production-is-the-new-prototype-notes-from-langchain-interrupt-2026
tags:
  runs_per_day: carried from 09-interview-targets.md, not re-verified (per-day is arithmetic)
  model_choice_and_use_cases: stated (claude.com)
  langsmith: carried, marked uncertain at source
```

## Evidence
- Claygent scrapes the public web for prospect research and generates personalized emails from tailored prompts (https://claude.com/customers/clay).
- Model choice is driven by cost at volume: "You can scale and do a lot more volume on Haiku a lot more cheaply than any other model" (Adam Eldefrawy) (https://claude.com/customers/clay).
- Clay's baseline for comparison is human data work: manual categorization accuracy is "often between 50-70% even with incentives for quality" (https://claude.com/customers/clay).
- Carried, not re-verified: about 350M agent runs a month and 1B+ Claygent runs in total, from an Interrupt 2026 recap (https://8thlight.com/insights/production-is-the-new-prototype-notes-from-langchain-interrupt-2026).

## What this case says for Gate A
Clay's volume makes per-run flight recording a cost problem first, and its runs are short web-research tasks rather than long, stateful, mutating harness runs. It likely falls below our screen on run length and mutation. No failure, regression or replay evidence was found. Treat it as low priority for Gate A, and consider swapping it for a long-run builder (for example Elastic or AppFolio) when search is available.
