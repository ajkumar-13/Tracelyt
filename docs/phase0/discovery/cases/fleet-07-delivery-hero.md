# Delivery Hero: Herogen (Claude Opus 4.5) merges 100+ PRs a day behind a Claude+Gemini review council, with Claude Code and every other tool routed through a LiteLLM proxy on Google Cloud

evidence_grade: B

Primary but promotional: Anthropic customer story with on-record quotes from Rodrigue Schäfer (VP Platform), fetched directly from claude.com, plus the Code w/ Claude 2026 session listing (Delivery Hero, Doctolib, monday.com) whose blurb promises "where it broke" but whose recording was not accessible. The BusinessWire release in the target list is egress-blocked and the web-search budget was exhausted, so no press facts were added.

```yaml
org: Delivery Hero
role: unknown (public: Rodrigue Schäfer, Vice President of Platform)
track: fleet
date: 2026-10-05
interviewer: desk (no interview)
method: desk
harnesses_frameworks: [Herogen (in-house autonomous delivery agent on Claude Opus 4.5), Claude Code, LiteLLM proxy, Google Cloud (Vertex-hosted Claude and Gemini), Jira, "council of agents" reviewers (Claude + Gemini)]
domain: coding
runs_per_day: ">100 merged Herogen PRs per day (~9% of all PRs); ~15% of engineers using Herogen; target 1 in 5 merged PRs in 2026; >4,000 engineers, Claude target ~50% of them"
failure_definition: "Ticket not completed; success is measured as ticket completion with zero to one developer interactions (inferred from the 85% success metric)"
failure_rate_estimate: "~15% (85% success rate on assigned tickets)"
cost_per_failed_run: unknown
last_failure:
  symptom: unknown (session blurb says the speakers discuss 'where it broke'; content not accessible)
  detected_by: unknown
  time_to_why: unknown
  attributed_component: unknown
  recurred: unknown
  their_words: "If you churn out five times more changes to your production environment, you will have five times more incidents if the change failure rate remains at the same level."
harness_change:
  last_change: "Model-led: platform attributes success to 'the new models that were substantially better in terms of quality'; LiteLLM proxy lets them adopt newest models without months of procurement"
  regression_detection: manual
  silent_regression_experienced: unknown
  would_pay_to_prevent: unknown
controls_owned (fleets): [model_effort, mcp_servers, ci_checks]
tooling_today: [LiteLLM proxy (request routing and usage data), Google Cloud, Jira, multi-model review council, human final review]
coding_agent_traces_flow_to: other
can_reproduce_failed_run: unknown
has_compared_cohorts: unknown
most_wanted_question: "How to keep change failure rate flat while change volume multiplies (inferred from Schäfer quote)"
data_constraints:
  cannot_leave: unknown
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: ai_platform
credible_contract_size: unknown
automation_limits: "Human does a final check after the agent council review on every Herogen PR"
would_allow_pause_stop_on_evidence: unknown
reaction:
  would_use_next_week: unknown
  does_not_believe: unknown
design_partner_candidate: unknown
referrals: []
quotes:
  - q: 7
    text: "If you churn out five times more changes to your production environment, you will have five times more incidents if the change failure rate remains at the same level."
  - q: 4
    text: "The tooling itself wasn't the main driver of the success of agentic engineering. The main driver was the new models that were substantially better in terms of quality."
  - q: 10
    text: "Google Cloud allowed us to set up a proxy and give our engineers choice by offering all Google Cloud models, hooked up with whatever tools they use."
sources:
  - https://claude.com/customers/delivery-hero
  - https://claude.com/code-with-claude/session/ldn-building-ai-native-at-enterprise-scale-monday-com-doctolib-and-delivery-hero
  - https://www.businesswire.com/news/home/20260424082392/en/Delivery-Hero-Unveils-Herogen-Autonomous-AI-Agent-Unlocks-130-Person-Engineering-Output
tags:
  harnesses_frameworks: stated
  runs_per_day: stated
  failure_definition: inferred (from "85% success rate ... zero to one developer interactions")
  failure_rate_estimate: inferred (complement of stated 85%)
  last_failure.their_words: stated
  harness_change.last_change: stated
  harness_change.regression_detection: inferred (only human review and agent council are described)
  controls_owned: stated (model routing via LiteLLM; planned Claude tool stack with built-in context for payment/order APIs) / inferred (CI)
  coding_agent_traces_flow_to: inferred (usage data is quoted from LiteLLM requests: "Claude models account for roughly 95% of all LiteLLM requests")
  budget_owner: inferred (Herogen was "self-funded within my organization", the platform org)
  automation_limits: stated
```

## Evidence

- Herogen, built on Claude Opus 4.5, picks up Jira tasks, writes code, iterates on tests and opens a PR; a "council of agents" (Claude and Gemini) reviews before a human final check, deliberately multi-model to reduce single-model blind spots (https://claude.com/customers/delivery-hero).
- >100 merged PRs/day (~9% of all PRs), 85% success on assigned tickets, 18x the Q1 2026 goal; only ~15% of engineers use it so far (https://claude.com/customers/delivery-hero).
- Built by a principal engineer and two staff engineers as a virtual team "self-funded within my organization" (https://claude.com/customers/delivery-hero).
- All coding tools route through a LiteLLM proxy on Google Cloud; Claude is ~95% of LiteLLM requests across central engineering teams (https://claude.com/customers/delivery-hero).
- Schäfer credits model quality, not tooling, for the agentic shift, which began working "until late 2025, when a new generation of models changed what was possible" (https://claude.com/customers/delivery-hero).
- Claude Code is used for exploratory work alongside Herogen; plan is a dedicated team providing a Claude tool stack with built-in context for payment APIs, order APIs and infra definitions, targeting ~50% of 4,000+ engineers (https://claude.com/customers/delivery-hero).
- Schäfer: five times more changes means five times more incidents at a constant change failure rate; team is investing in agent-driven operations and safer rollouts (https://claude.com/customers/delivery-hero).
- Code w/ Claude 2026 session (Delivery Hero, Doctolib, monday.com) is billed as covering "where it broke, and how they stay ahead of a model that changes every few months"; Doctolib "governs Claude Code across its entire healthcare engineering org" (https://claude.com/code-with-claude/session/ldn-building-ai-native-at-enterprise-scale-monday-com-doctolib-and-delivery-hero).

## What this case says for Gate A

Delivery Hero is a mixed fleet-and-builder: a closed harness (Claude Code) for exploration plus an in-house autonomous agent producing ~9% of PRs, all funnelled through one LiteLLM proxy that already captures usage. They state the downstream risk plainly (incidents scale with change volume) and attribute progress to model upgrades they adopt quickly, which is exactly the setting where a model change could silently shift Herogen's 85% success rate. But there is no public account of a specific regression, of how the 85% is measured over time, or of replay interest. The "where it broke" talk is the most promising lead to watch if a transcript becomes reachable. Pain counters: unknown, with a stated change-failure-rate concern.
