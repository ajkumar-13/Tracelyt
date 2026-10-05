# Nubank: Devin fleet run against a held-out migration benchmark for a 6M-LOC ETL split

evidence_grade: C (the vendor-published customer story quotes a named Nubank PM; Nubank's own blog post covers LLM workflows in general, not the Devin fleet; no postmortem or incident detail)

```yaml
org: Nubank
role: unknown (the public quote comes from Jose Carlos Castro, Senior Product Manager)
track: fleet
date: 2026-10-05
interviewer: desk
method: desk
harnesses_frameworks: [Devin]
domain: coding
runs_per_day: unknown (the migration covered >100,000 data-class implementations split into subtasks run as parallel Devin sessions)
failure_definition: unknown (inferred, from the benchmark story, that failure means not completing a migration subtask on the held-out evaluation set)
failure_rate_estimate: unknown (fine-tuning "doubled task completion scores", but the absolute rates are not public)
cost_per_failed_run: unknown
last_failure:
  symptom: unknown
  detected_by: unknown
  time_to_why: unknown
  attributed_component: unknown
  recurred: unknown
  their_words: ""
harness_change:
  last_change: fine-tuned Devin on examples of earlier manual migrations, and Devin built itself scripts/tools for common subtasks
  regression_detection: evals
  silent_regression_experienced: unknown
  would_pay_to_prevent: unclear
controls_owned: [ci_checks]   # inferred: engineers review and merge Devin PRs; no evidence on rules files, hooks or budgets
tooling_today: [Devin, held-out migration benchmark built from historic human migrations]
coding_agent_traces_flow_to: unknown
can_reproduce_failed_run: unknown
has_compared_cohorts: yes   # inferred: they compared fine-tuned against base Devin on the held-out set
most_wanted_question: ""
data_constraints:
  cannot_leave: [unknown]   # a regulated bank; no public statement about agent telemetry
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: unknown
credible_contract_size: unknown
automation_limits: "humans review Devin's changes, make minor adjustments, then merge (stated in the PM quote)"
would_allow_pause_stop_on_evidence: unknown
reaction:
  would_use_next_week: ""
  does_not_believe: ""
design_partner_candidate: unknown
referrals: []
quotes:
  - q: 9
    text: "Rather than engineers having to work across several files and complete an entire migration task 100%, they could just review Devin's changes, make minor adjustments, then merge their PR"
sources:
  - https://devin.ai/customers/nubank/
  - https://x.com/cognition_labs/status/1866579175743820116
  - https://building.nu.com/enhancing-engineering-workflows-with-ai-a-real-world-experience/
  - https://fast.io/resources/devin-ai-use-cases/
tags:
  harnesses_frameworks: stated
  runs_per_day: inferred (from the 100k data classes and the parallel-session framing)
  harness_change.last_change: stated
  harness_change.regression_detection: stated (benchmark evaluation set)
  controls_owned: inferred
  has_compared_cohorts: inferred
  automation_limits: stated
  quotes: stated (search snippet of the Devin customer page)
```

## Evidence
- The job was to split Nubank's core ETL, an 8-year-old monolith of several million lines, into sub-modules. Done by hand it was estimated at a multi-year effort spread over more than 1,000 engineers (https://devin.ai/customers/nubank/).
- It covered more than 6 million lines and more than 100,000 data-class implementations, each migrated on its own, with an expected scope of 18 months (https://devin.ai/customers/nubank/).
- Nubank collected earlier manual migrations, used some to fine-tune Devin and held the rest back as a benchmark evaluation set (https://devin.ai/customers/nubank/).
- On that set, fine-tuning doubled task-completion scores and made tasks about 4x faster. Per-subtask time fell from about 40 to about 10 minutes (https://devin.ai/customers/nubank/ ; https://fast.io/resources/devin-ai-use-cases/).
- Reported outcome: a 12x efficiency gain in engineering hours and more than 20x cost savings. Cognition says the project went from about 1.5 years to about 2 months (https://x.com/cognition_labs/status/1866579175743820116).
- Devin built itself "classical tools and scripts" that it later reused on the most common subtasks (https://devin.ai/customers/nubank/). In effect the agent was changing its own harness.
- Engineers reviewed and merged Devin's PRs rather than editing each data class by hand (PM quote, https://devin.ai/customers/nubank/).
- Nubank's own engineering blog (a Clojure Conj 2024 talk by Carin Meier and Marlon Silva) covers LLM-assisted workflows in general. The snippets show no governance, telemetry or incident detail (https://building.nu.com/enhancing-engineering-workflows-with-ai-a-real-world-experience/).
- No public evidence of incidents, cost overruns, telemetry export or which data cannot leave.

## What this case says for Gate A
Nubank is the clearest public example of a fleet operator building its own held-out regression set before scaling a vendor agent. That is the "gate harness changes on a frozen task corpus" behaviour we want to sell, done by hand for one migration. It shows the need, but it also shows a sophisticated team can build this in-house for a bounded, repeated task class. The evidence comes almost entirely from Cognition's marketing, so it says nothing about failures, silent regressions, telemetry destinations or data residency. As a regulated bank, Nubank would probably restrict code and customer data leaving its environment, but that is inference only. It is worth a live conversation about whether the benchmark-set practice outlived the migration. It adds nothing to the pain counters.
