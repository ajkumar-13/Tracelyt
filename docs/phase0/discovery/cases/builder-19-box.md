# Box: enterprise-content agents behind an LLM gateway with model routing (Sonnet orchestrates, Opus generates); public record says nothing about failures or evals

evidence_grade: B  (primary Anthropic/Claude customer story fetched in full; thin on every reliability question)

```yaml
org: Box
role: AI platform engineering (no named engineer in the source)
track: builder
date: 2026-10-05
interviewer: desk-research agent
method: desk
harnesses_frameworks: [in-house LLM gateway, Claude Sonnet + Opus, Anthropic Skills API (PowerPoint, Excel, Word, PDF), OpenAI Agents SDK (per 09-interview-targets, not re-verified)]   # stated (Claude page) / unverified (OpenAI)
domain: workflow   # document analysis and generation over enterprise content
runs_per_day: unknown
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
  last_change: "Added Skills-based document generation: two new integration points (file upload in, file download out) on the existing gateway; routed generation to Opus and orchestration to Sonnet"   # stated
  regression_detection: unknown
  silent_regression_experienced: unknown
  would_pay_to_prevent: unknown
controls_owned (fleets): []
tooling_today: [in-house production LLM gateway handling "logging, request counting, and access control"]
coding_agent_traces_flow_to: unknown
can_reproduce_failed_run: unknown
has_compared_cohorts: unknown
most_wanted_question: ""
data_constraints:
  cannot_leave: [customer_data]   # inferred: agreement that "customer data isn't used for training"; security review framed around new data paths; skill containers short-lived
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: unknown
credible_contract_size: unknown
automation_limits: ""
would_allow_pause_stop_on_evidence: unknown
reaction:
  would_use_next_week: ""
  does_not_believe: ""
design_partner_candidate: unknown
referrals: []
quotes:
  - q: 7
    text: "orchestrating over Box content is well-bounded, while producing a document that looks right demands more from the model"
  - q: 15
    text: "two new data paths, not a new trust boundary"
sources:
  - https://claude.com/customers/box
  - https://openai.com/index/new-tools-for-building-agents/
tags:
  harnesses_frameworks: stated
  harness_change.last_change: stated
  tooling_today: stated
  data_constraints.cannot_leave: inferred
```

## Evidence
- Box routes LLM requests through a production gateway that handles "logging, request counting, and access control" (https://claude.com/customers/box).
- The integration added exactly two points: "file upload on the way in, file download on the way out" (https://claude.com/customers/box).
- Model routing: Sonnet interprets requests and assembles context; Opus generates documents, reversing the usual planner/executor split (https://claude.com/customers/box).
- Uses Anthropic's pre-built Skills for PowerPoint, Excel, Word and PDF; spreadsheet analysis benefits from the "full structure of a spreadsheet rather than just text extracted by RAG" (https://claude.com/customers/box).
- Security: existing agreement that "customer data isn't used for training"; skill execution containers are "short-lived, lasting only minutes"; review focused on "two new data paths, not a new trust boundary" (https://claude.com/customers/box).
- Outcome claim: contract redlining for jurisdiction changes went from "an afternoon of manual review" to 2 minutes (https://claude.com/customers/box).
- 09-interview-targets lists Box as an OpenAI Agents SDK launch partner with "permission-aware agents" (https://openai.com/index/new-tools-for-building-agents/); not re-verified in this pass.

## What this case says for Gate A
Box is a multi-model builder with its own gateway that already logs every LLM call, so it has the raw material for traces but nothing public about agent failures, evals, or how model-routing or skill changes are gated. Multi-vendor routing (Claude plus OpenAI) is a plausible source of silent regressions when either vendor ships a model or the routing rules change, but that is our inference, not their statement. Customer content is the product, so any replay must stay inside Box's boundary. This case adds nothing to the Gate A counters; it is a target to qualify live, not evidence. Evidence collection was cut short when the session's web-search budget ran out (see coordinator report).
