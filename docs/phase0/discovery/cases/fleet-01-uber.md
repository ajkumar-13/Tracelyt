# Uber: Claude Code fleet of ~5,000 engineers burned the 2026 AI budget in four months, then a platform team re-engineered cost (cache TTL, default model, 400K cap)

evidence_grade: A

Primary sources: Uber Engineering blog posts on the MCP Gateway, the agent identity system and "Running a Software Factory Efficiently at Uber Scale" (Aug 2026), plus on-record CTO/COO statements reported by Fortune, Axios and Yahoo Finance. uber.com is egress-blocked, so all Uber-blog facts below come from search snippets of those pages or of faithful rewrites (ZenML, Port newsletter).

```yaml
org: Uber
role: unknown (public sources: CTO Praveen Neppalli Naga, COO Andrew Macdonald, Uber Engineering blog author Uday Kiran Medisetty)
track: fleet
date: 2026-10-05
interviewer: desk (no interview)
method: desk
harnesses_frameworks: [Claude Code, Cursor, Minions (Uber in-house background agent), AIFX CLI, MCP Gateway (800+ MCP servers, 5,000 tools), LLM gateway, uReview]
domain: coding
runs_per_day: "unknown per day; Minions ~1,800 code changes/week; weekly agent requests grew 9.4x Feb-Aug 2026; AAIF headline '60,000 AI agent tasks per week'"
failure_definition: "unknown for coding fleet; the budget was the failure surface (cost per 1K requests, cost per session, cost per active session hour, cache hit rate are the tracked metrics)"
failure_rate_estimate: unknown
cost_per_failed_run: "unknown; per-engineer spend typically $150-250/month, heavy users $500-2,000/month; CTO burned $1,200 in tokens in a two-hour demo"
last_failure:
  symptom: "Full 2026 Claude Code / AI tools budget exhausted by April, four months into the year, after a usage leaderboard drove adoption from 32% to 84%"
  detected_by: cost_alert
  time_to_why: unknown
  attributed_component: budget
  recurred: unknown
  their_words: "So if you're not actually able to draw a direct line to how much useful features and functionality you're shipping to your users, that trade becomes harder to justify. (COO Andrew Macdonald)"
harness_change:
  last_change: "Aug 2026: prompt-cache TTL moved from 5 minutes to 1 hour; interactive sessions capped at 400K tokens with medium reasoning effort by default; cheaper default model for subagents; CLI-resolved MCP tool calls instead of preloading schemas (saves 50K-70K tokens); code-mode batching; per-hour usage/cost visibility for engineers; open-weight model experiments"
  regression_detection: evals
  silent_regression_experienced: unknown
  would_pay_to_prevent: unknown
controls_owned (fleets): [mcp_servers, tool_allowlists, permissions, model_effort, budgets]
tooling_today: [Uber LLM gateway, MCP Gateway (auth, PII redaction, audit logs), agent identity tokens per hop, cost metrics dashboards (cost per 1K requests, per session, cache hit rate), uReview precision/recall dashboards, Arize (talk on agent eval; scope inside Uber unclear)]
coding_agent_traces_flow_to: other
can_reproduce_failed_run: unknown
has_compared_cohorts: unknown
most_wanted_question: "How much useful product output does each unit of token spend produce? (inferred from COO statement)"
data_constraints:
  cannot_leave: [customer_data]
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: ai_platform
credible_contract_size: unknown
automation_limits: "Every tool call traced back to the initiating human engineer via attested agent identity tokens; tool-level authorization by caller type (human, service, agent)"
would_allow_pause_stop_on_evidence: unknown
reaction:
  would_use_next_week: unknown
  does_not_believe: unknown
design_partner_candidate: unknown
referrals: []
quotes:
  - q: 1
    text: "So if you're not actually able to draw a direct line to how much useful features and functionality you're shipping to your users, that trade becomes harder to justify."
  - q: 10
    text: "The next phase, whatever we call it, will not be characterized by who spends the most tokens, but about how people use them as efficiently as possible."
sources:
  - https://www.forbes.com/sites/janakirammsv/2026/05/17/uber-burns-its-2026-ai-budget-in-four-months-on-claude-code/
  - https://fortune.com/2026/05/26/uber-coo-ai-spending-tokens-claude-code/
  - https://finance.yahoo.com/sectors/technology/articles/uber-coo-andrew-macdonald-says-130036457.html
  - https://fortune.com/2026/08/07/uber-ai-spending-tokenmaxxing-is-over-cto/
  - https://www.axios.com/2026/08/27/ai-uber-spending
  - https://www.uber.com/us/en/blog/efficient-software-factory/
  - https://www.zenml.io/llmops-database/building-a-managed-software-factory-with-agentic-ai
  - https://www.uber.com/us/en/blog/designing-mcp-gateway/
  - https://www.uber.com/us/en/blog/solving-the-agent-identity-crisis/
  - https://newsletter.port.io/p/how-uber-built-a-software-factory
  - https://www.uber.com/us/en/blog/ureview/
  - https://arize.com/blog/how-uber-evaluates-ai-agents-at-production-scale/
  - https://www.developersdigest.tech/blog/enterprise-ai-coding-budget-blowouts-2026
tags:
  harnesses_frameworks: stated
  runs_per_day: stated (weekly figures)
  failure_definition: inferred (from the metrics list in the efficiency blog)
  cost_per_failed_run: stated (per-engineer spend, not per failed run)
  last_failure.symptom: stated
  last_failure.detected_by: inferred (budget exhaustion surfaced by finance/CTO, not by an agent monitor)
  last_failure.attributed_component: inferred (budget/usage incentives; no model fault claimed)
  harness_change.last_change: stated
  harness_change.regression_detection: inferred (efficiency blog describes benchmark-driven model selection; uReview uses precision/recall dashboards and staged rollout)
  controls_owned: stated (MCP gateway auth/redaction, default model, effort, context cap) / inferred (budgets)
  tooling_today: stated
  coding_agent_traces_flow_to: inferred (in-house LLM/MCP gateways and audit logs; no Datadog/LangSmith export of Claude Code traces found)
  cannot_leave: inferred (MCP Gateway redacts PII from tool responses before they reach models)
  budget_owner: inferred (CTO-owned platform team ran the cost program; COO questioned the trade-off)
  automation_limits: stated
  quotes: stated (verbatim from search snippets)
```

## Evidence

- Uber rolled out Claude Code to roughly 5,000 engineers in December 2025; an internal leaderboard ranked teams by AI tool usage and adoption went from 32% (Feb) to 84% agentic users (Mar) (https://www.forbes.com/sites/janakirammsv/2026/05/17/uber-burns-its-2026-ai-budget-in-four-months-on-claude-code/; https://www.developersdigest.tech/blog/enterprise-ai-coding-budget-blowouts-2026).
- CTO Praveen Neppalli Naga disclosed in April 2026 that the full 2026 Claude Code budget was spent; typical per-engineer bills $150-250/month, heaviest $500-2,000; he burned $1,200 of tokens in a two-hour demo (https://finance.yahoo.com/sectors/technology/articles/uber-coo-andrew-macdonald-says-130036457.html).
- COO Andrew Macdonald called it a "head-exploding moment" and said greater token consumption was not producing a matching rise in useful features (https://fortune.com/2026/05/26/uber-coo-ai-spending-tokens-claude-code/).
- Commentators note the teams running leaderboards were disconnected from the team owning the AI budget line (inference by a third party, not Uber) (https://www.developersdigest.tech/blog/enterprise-ai-coding-budget-blowouts-2026).
- Fix: cost per 1,000 requests down ~34% from April peak, cost per session down 52% from June high, total spend flat since April while weekly agent requests grew 9.4x (https://www.axios.com/2026/08/27/ai-uber-spending).
- Harness changes that drove it: prompt cache TTL 5 min to 1 hour because engineers leave sessions idle; 400K-token session cap with medium effort by default; cheaper default models for subagents; MCP tools resolved via CLI instead of preloaded schemas (50K-70K tokens saved); code-mode batching (https://www.uber.com/us/en/blog/efficient-software-factory/; https://www.zenml.io/llmops-database/building-a-managed-software-factory-with-agentic-ai).
- Tracked fleet metrics: cost per user, requests per user, cost per 1K requests, tokens per request, cost per 1M tokens, cost per 1K sessions, cost per active session hour, prompt-cache hit rate (https://www.zenml.io/llmops-database/building-a-managed-software-factory-with-agentic-ai).
- Claude Code, Cursor and Uber's Minions add MCP servers through an internal CLI (AIFX); the MCP Gateway fronts 800+ servers / 5,000 tools with tool-level authorization, PII redaction of tool responses, and audit logs (https://newsletter.port.io/p/how-uber-built-a-software-factory; https://www.uber.com/us/en/blog/designing-mcp-gateway/).
- Agent identity system issues attested tokens per agent hop and traces every tool call back to the initiating human (https://www.uber.com/us/en/blog/solving-the-agent-identity-crisis/).
- Over 70% of PRs come from local or cloud agents; Uber's stated thesis is that agents produce working but low-quality code and instruction-based constraints do not enforce quality, so they use deterministic checks + LLM judge + bounded retries (https://newsletter.port.io/p/how-uber-built-a-software-factory).
- uReview (AI code review over ~65K diffs/week) was rolled out one team/assistant at a time with precision-recall dashboards and comment-address-rate logs "limiting the scope of potential regressions"; fixes were A/B tested (https://www.uber.com/us/en/blog/ureview/).
- Adjacent (not coding fleet): a voice agent incident slipped through offline evals and was caught only when average session length jumped from 4-5 turns to ~20; Uber then made tracing automatic at deployment (https://arize.com/blog/how-uber-evaluates-ai-agents-at-production-scale/).

## What this case says for Gate A

Uber is the clearest public example of a closed-harness fleet where the failure was economic, not functional: the incident was detected by budget exhaustion, and the root cause was incentives plus harness defaults (cache TTL, default model, context cap, MCP schema preloading), not the model. That is evidence that harness configuration changes move cost by 30-50% and that a platform team owns those knobs centrally. There is no public evidence of a silent quality regression in the coding fleet, nor of Claude Code OTel traces going to a third-party observability tool; Uber built gateways and its own metrics. Uber's in-house build habit (gateways, identity, uReview, Arize for product agents) makes it a hard buyer but a strong reference for "cost per session as a regression metric." Pain counter: cost pain yes; quality-regression pain unknown.
