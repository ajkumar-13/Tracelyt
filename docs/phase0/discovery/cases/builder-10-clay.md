# Clay: Claygent runs 300-350M+ times a month (trillions of tokens a week); replaced "comparatively weak early evaluations" with a layered eval program (deterministic checks, assertions, LLM judges, multi-turn tests, online metrics, human review, production-trace analysis) and is consolidating traces in a data lake with shadow deployments; names production drift, judge bias and eval noise as unresolved

evidence_grade: B

Access note (pass 2, 2026-10-05): the primary sources are Jeff Barg's Interrupt 2026 talk ("How Clay runs 350 million GTM agents a month", YouTube, blocked) and a second Clay talk on evaluation and data foundations; both are captured in ZenML LLMOps-database summaries and 8th Light's conference notes, reached through search snippets. Anthropic's older Clay page was fetched directly in pass 1. The pass-1 "carried" volume is now verified (350M/month per the talk title; "more than 300 million" per the eval summary). Grade B: primary talks with specifics on scale, eval structure and named risks, but no concrete failed-run story and no regression incident.

```yaml
org: Clay
role: AI platform / Claygent engineering (public: Jeff Barg; Adam Eldefrawy, Software Engineer)
track: builder
date: 2026-10-05
interviewer: desk
method: desk
harnesses_frameworks: [Claygent (proprietary agent, "custom agent harnesses"), Sculptor (100,000+ weekly messages), AWS ECS with durable workflow execution (moved from Lambda), adaptive rate limiting modelled on TCP congestion control, prompt caching, bounded retries, Claude 3 Haiku at the time of the Anthropic case study]
domain: research
runs_per_day: "~10-12M (350M+ Claygent executions/month per Interrupt talk; 'more than 300 million' per eval talk; 'trillions of tokens weekly'; 40M companies, 900M contacts)"
failure_definition: "inferred: hallucinated or vague research answers that need manual verification (third-party reviews); internally measured by deterministic checks, assertions, LLM judges and online behavioural metrics"
failure_rate_estimate: unknown
cost_per_failed_run: "unknown; cost managed with prompt caching ('up to 70% savings') and bounded retries"
last_failure:
  symptom: "No single incident published. Stated systemic problems: early evaluations were 'comparatively weak'; infrastructure reliability on Lambda forced a move to ECS with durable workflows; rate-limit throttling; and, per third-party reviews, hallucinated or vague Claygent answers and 'unpredictable credit consumption'"
  detected_by: unknown
  time_to_why: unknown
  attributed_component: unknown
  recurred: unknown
  their_words: ""
harness_change:
  last_change: "Replaced weak early evals with a layered program; moved execution from Lambda to ECS with durable workflow patterns; added TCP-style back-pressure (4-10x throughput); consolidating traces into a data lake with guarded agent access, separate dev and serving compute, CLI/API tools and shadow deployments"
  regression_detection: evals
  silent_regression_experienced: unknown
  would_pay_to_prevent: unknown
controls_owned (fleets): []
tooling_today: [layered evals (deterministic checks, structured assertions, LLM judges, multi-turn tests, online behavioural metrics, human review, production-trace analysis), data lake of traces and operational data, shadow deployments, per-agent reasoning traces and per-segment spend/error views in product, prompt version history with instant rollback]
coding_agent_traces_flow_to: unknown (agent traces go to an internal data lake; coding agents not discussed)
can_reproduce_failed_run: partially
has_compared_cohorts: yes
most_wanted_question: "inferred: how to keep offline evals predictive under 'production drift, judge bias, evaluation noise'"
data_constraints:
  cannot_leave: unknown
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: ai_platform
credible_contract_size: unknown
automation_limits: "Agent-oriented guardrails on data-lake access; bounded retries; human review tier in evals"
would_allow_pause_stop_on_evidence: unknown
reaction:
  would_use_next_week: unknown
  does_not_believe: unknown
design_partner_candidate: unknown
referrals: [Jeff Barg, Adam Eldefrawy]
quotes:
  - q: 6
    text: "Claygent, their proprietary agent, executes over 350 million times per month, processing trillions of tokens weekly across a dataset of over 40 million companies and 900 million contacts."
    paraphrase: true
  - q: 10
    text: "replaced comparatively weak early evaluations with a layered evaluation program spanning deterministic checks, structured assertions, LLM judges, multi-turn tests, online behavioral metrics, and human review"
    paraphrase: true
  - q: 17
    text: "production drift, judge bias, evaluation noise, and the operational complexity of long-running agents remain unresolved risks"
    paraphrase: true
  - q: 9
    text: "treats infrastructure, throughput, cost, and quality as four discrete engineering disciplines, each with its own tools"
    paraphrase: true
  - q: 1
    text: "You can scale and do a lot more volume on Haiku a lot more cheaply than any other model"
sources:
  - https://www.youtube.com/watch?v=LmQtSORYPfw
  - https://www.zenml.io/llmops-database/scaling-go-to-market-ai-agents-at-production-scale
  - https://www.zenml.io/llmops-database/production-evaluation-and-data-foundations-for-go-to-market-agents-3e9f8dff
  - https://8thlight.com/insights/production-is-the-new-prototype-notes-from-langchain-interrupt-2026
  - https://www.clay.com/claygent
  - https://www.clay.com/changelog/product-roundup-week-of-jun-1-2026
  - https://claude.com/customers/clay
  - https://getfuzzy.ai/blog/clay-review-2026
tags:
  harnesses_frameworks: stated (ZenML summaries of the two talks; Anthropic page for Haiku)
  runs_per_day: stated monthly figures (350M+ and "more than 300 million" from two talks); per-day is arithmetic
  failure_definition: inferred (from eval layers and third-party review complaints)
  cost_per_failed_run: stated cost controls only
  last_failure.symptom: stated as systemic issues in the talks; hallucination/vagueness is from third-party reviews, not Clay
  harness_change.last_change: stated (both ZenML summaries)
  regression_detection: stated (layered evals, shadow deployments, production-trace analysis)
  tooling_today: stated (ZenML eval summary; Clay changelog for reasoning traces, spend/error views, version history and rollback)
  coding_agent_traces_flow_to: inferred-unknown (data lake for agent traces; nothing on coding agents)
  can_reproduce_failed_run: inferred (every agent decision carries a reasoning trace and traces are consolidated; replay not stated)
  has_compared_cohorts: inferred (shadow deployments and online behavioural metrics imply cohort comparison)
  most_wanted_question: inferred from the named unresolved risks
  budget_owner: inferred
  cannot_leave: unknown (Clay's data is largely scraped public web plus customer CRM data; no statement found)
```

## Evidence
- Claygent "executes over 350 million times per month, processing trillions of tokens weekly across a dataset of over 40 million companies and 900 million contacts" (https://www.zenml.io/llmops-database/scaling-go-to-market-ai-agents-at-production-scale ; talk: https://www.youtube.com/watch?v=LmQtSORYPfw).
- Clay treats "infrastructure, throughput, cost, and quality as four discrete engineering disciplines, each with its own tools"; a back-pressure system "modeled on TCP congestion control" throttles requests against rate limits for "4-10x throughput improvements over naive approaches" (https://8thlight.com/insights/production-is-the-new-prototype-notes-from-langchain-interrupt-2026).
- Infrastructure reliability came from moving "from Lambda to ECS with durable workflow execution patterns"; cost from prompt caching ("up to 70% savings") and bounded retries; quality from proprietary context, "custom agent harnesses, and both offline and online evaluation systems" (https://www.zenml.io/llmops-database/scaling-go-to-market-ai-agents-at-production-scale).
- As usage grew past 300M Claygent runs a month and 100,000+ weekly Sculptor messages, Clay "replaced comparatively weak early evaluations with a layered evaluation program spanning deterministic checks, structured assertions, LLM judges, multi-turn tests, online behavioral metrics, human review, and production-trace analysis" (https://www.zenml.io/llmops-database/production-evaluation-and-data-foundations-for-go-to-market-agents-3e9f8dff).
- Clay is "consolidating traces and operational data in a data lake with guarded agent access, separate development and serving compute, CLI/API tools, and shadow deployments", aiming for "a feedback loop in which production evidence improves agents and their evaluation suites" (https://www.zenml.io/llmops-database/production-evaluation-and-data-foundations-for-go-to-market-agents-3e9f8dff).
- The summary's own caveat: the approach "improves the organization's ability to change prompts and agent behavior safely, although production drift, judge bias, evaluation noise, and the operational complexity of long-running agents remain unresolved risks" (https://www.zenml.io/llmops-database/production-evaluation-and-data-foundations-for-go-to-market-agents-3e9f8dff).
- Product-side: "every agent decision in Clay comes with a full reasoning trace"; per-agent and per-segment spend and error views; prompt changes are versioned automatically and can be rolled back instantly (https://www.clay.com/changelog/product-roundup-week-of-jun-1-2026 ; https://www.clay.com/claygent).
- Third-party reviews report that when Claygent fails users "get hallucinated answers or vague responses that need manual verification" and "unpredictable credit consumption" (https://getfuzzy.ai/blog/clay-review-2026).
- Older Anthropic case study: model choice driven by cost at volume, "You can scale and do a lot more volume on Haiku a lot more cheaply than any other model"; human categorisation baseline "often between 50-70%" (https://claude.com/customers/clay).

## What this case says for Gate A
Clay is the highest-volume builder in the corpus and has explicitly said its early evals were weak and that drift, judge bias and eval noise remain open problems even after a layered program and a trace data lake. That is a stated, unsolved need for exactly the production-evidence-to-regression-gate loop we propose, and shadow deployments plus "production-trace analysis" are a native form of cohort comparison. The constraints cut the other way: runs are short web-research tasks, not long mutating harness runs, and at 10M+ runs a day per-run flight recording is a cost problem before it is a value problem. Clay has also built most of the stack in-house and would evaluate us as a component of its data lake, not a platform. No failure incident, root-cause time or data-residency statement was found. Counts: silent_regression unknown, attribution unknown, traces to an internal data lake (other), cannot_leave unknown.
