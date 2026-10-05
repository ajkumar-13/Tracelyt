# Cloudflare: 3,683 internal users route 241B tokens a month through AI Gateway, with LLM-generated AGENTS.md in ~3,900 repos and an AI code reviewer in CI

evidence_grade: B

Primary source is Cloudflare's own engineering post "The AI engineering stack we built internally — on the platform we ship" (April 20, 2026). blog.cloudflare.com is egress-blocked and the session's web-search budget ran out mid-case, so the facts below come from search snippets of that post and of rewrites. The post has specific numbers but, as far as the snippets show, no incident narrative, hence B rather than A.

```yaml
org: Cloudflare
role: unknown (target list names Rajesh Bhatia, Ayush Thakur, Scott Roe-Meschke as authors/owners; not verified in snippets)
track: fleet
date: 2026-10-05
interviewer: desk (no interview)
method: desk
harnesses_frameworks: [unspecified "AI coding tools" (agent names not exposed in the snippets), AI Gateway, Workers AI, MCP Server Portals (13 servers, 182+ tools), Cloudflare Access, AI Code Reviewer in CI/CD, Engineering Codex, Backstage]
domain: coding
runs_per_day: "unknown per day; 20.18M AI Gateway requests and 241.37B tokens in a 30-day period; 47.95M AI requests; 295 teams"
failure_definition: unknown
failure_rate_estimate: unknown
cost_per_failed_run: unknown
last_failure:
  symptom: "Reported (via a secondary summary) that coding agents submitted PRs that looked plausible but were wrong because repo context in AGENTS.md had drifted"
  detected_by: unknown
  time_to_why: unknown
  attributed_component: context
  recurred: unknown
  their_words: ""
harness_change:
  last_change: "Automated system reads Backstage, detects a repo's language/frameworks, maps them to internal engineering rules and has an LLM open a PR with a tailored AGENTS.md (~3,900 repos); AI Code Reviewer reads AGENTS.md on every MR and flags when a change makes it stale"
  regression_detection: ci
  silent_regression_experienced: unknown
  would_pay_to_prevent: unknown
controls_owned (fleets): [rules_files, mcp_servers, tool_allowlists, model_effort, budgets, ci_checks]
tooling_today: [Cloudflare AI Gateway (central LLM routing, logs, spend limits product), Workers AI, MCP Server Portals, Cloudflare Access (zero-trust auth), AI Code Reviewer, Engineering Codex, Backstage]
coding_agent_traces_flow_to: other
can_reproduce_failed_run: unknown
has_compared_cohorts: unknown
most_wanted_question: unknown
data_constraints:
  cannot_leave: unknown
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: ai_platform
credible_contract_size: unknown
automation_limits: unknown
would_allow_pause_stop_on_evidence: unknown
reaction:
  would_use_next_week: unknown
  does_not_believe: unknown
design_partner_candidate: unknown
referrals: []
quotes: []
sources:
  - https://blog.cloudflare.com/internal-ai-engineering-stack/
  - https://www.webpronews.com/cloudflares-ai-stack-fuels-93-engineer-adoption-inside-the-platform-powering-241-billion-tokens-monthly/
  - https://tekai.dev/references/2026-04-22-cloudflare-internal-ai-engineering-stack
  - https://dosu.dev/blog/a-stale-agents-md-is-worse-than-no-agents-md
  - https://developers.cloudflare.com/cloudflare-one/access-controls/ai-controls/mcp-portals/
  - https://blog.cloudflare.com/ai-gateway-spend-limits/
  - https://github.com/Chipagosfinest/software-factory/blob/main/docs/production-case-studies-state-of-play-2026-07-16.md
tags:
  harnesses_frameworks: stated (components); unknown (which vendor agents)
  runs_per_day: stated (monthly totals)
  last_failure.symptom: inferred (from dosu.dev's summary of the Cloudflare post; not seen verbatim in a Cloudflare snippet)
  last_failure.attributed_component: inferred (stale context file)
  harness_change.last_change: stated (AGENTS.md generation, reviewer reading AGENTS.md) per snippets
  harness_change.regression_detection: inferred (AI reviewer in CI is the only stated gate)
  controls_owned: stated (rules files, MCP portals, gateway routing, CI reviewer) / inferred (budgets, model choice via central gateway)
  coding_agent_traces_flow_to: inferred (requests route through Cloudflare's own AI Gateway, which logs; i.e. in-house "other")
  budget_owner: inferred (internal AI engineering platform team)
```

## Evidence

- In the 30 days before the April 2026 post, 93% of Cloudflare R&D (3,683 users, 60% company-wide) used AI coding tools on infrastructure built on Cloudflare's own platform over 11 months (https://blog.cloudflare.com/internal-ai-engineering-stack/; https://www.webpronews.com/cloudflares-ai-stack-fuels-93-engineer-adoption-inside-the-platform-powering-241-billion-tokens-monthly/).
- 241.37B tokens and 20.18M requests routed through AI Gateway in the period; 295 teams using agentic tools (https://www.webpronews.com/cloudflares-ai-stack-fuels-93-engineer-adoption-inside-the-platform-powering-241-billion-tokens-monthly/).
- Stack: Cloudflare Access for zero-trust auth, AI Gateway for central LLM routing, Workers AI for on-platform inference, MCP Server Portals aggregating 13 servers / 182+ tools, AI Code Reviewer in CI/CD, Engineering Codex for standards (https://tekai.dev/references/2026-04-22-cloudflare-internal-ai-engineering-stack).
- AGENTS.md files were generated across ~3,900 repos by an automated system that reads Backstage metadata, maps frameworks to internal rules and opens an LLM-written PR (https://dosu.dev/blog/a-stale-agents-md-is-worse-than-no-agents-md).
- The AI Code Reviewer reads AGENTS.md on every merge request and flags architectural drift that requires an AGENTS.md update in the same change (https://dosu.dev/blog/a-stale-agents-md-is-worse-than-no-agents-md).
- A secondary summary says Cloudflare's agents "regularly submitted pull requests that looked plausible but were fundamentally wrong because the local repo context had drifted" (paraphrase by dosu.dev, not verified against the primary) (https://dosu.dev/blog/a-stale-agents-md-is-worse-than-no-agents-md).
- 4-week rolling average of merge requests rose from ~5,600/week to 8,700+, with a peak week of 10,952 (https://www.webpronews.com/cloudflares-ai-stack-fuels-93-engineer-adoption-inside-the-platform-powering-241-billion-tokens-monthly/).
- Next stated phase: cloud background agents on Durable Objects plus sandbox containers; no later first-party results found as of July 2026 (https://github.com/Chipagosfinest/software-factory/blob/main/docs/production-case-studies-state-of-play-2026-07-16.md).
- Cloudflare sells AI Gateway spend limits externally under the headline "Your AI bill is out of control" (https://blog.cloudflare.com/ai-gateway-spend-limits/).

## What this case says for Gate A

Cloudflare is a fleet where the platform team owns nearly every control (rules files generated centrally, MCP portal, gateway routing, CI reviewer) and already has a full request log of agent traffic in its own gateway. That makes it the strongest public example of "the rules file is a fleet-wide harness artifact that drifts and needs gating," and they built a CI check for exactly that. But it is also a vendor of the gateway and observability layer, so it is more likely to build than buy, and its telemetry stays on its own platform. No public silent-regression story or replay interest was found; pain counters remain unknown. Treat as a design reference and possible competitor-adjacent, not a likely buyer.
