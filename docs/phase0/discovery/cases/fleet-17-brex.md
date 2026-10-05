# Brex: per-directory CLAUDE.md plus a stale-docs CI check, self-hosted Cursor agent pipelines that migrated 180 microservices in a month, a named failure mode (agents that cannot read CI and review-bot feedback "produce output that looks correct but isn't"), and CrabTrap, an open-source network proxy that logs every agent request and LLM-judges the risky 2%

evidence_grade: B (pass 2: four Brex-authored engineering posts and an open-source repository give primary, specific detail on failure modes, controls and audit logging; no production postmortem or regression incident is public, so not A)

```yaml
org: Brex
role: unknown (named: Hércules Gimenes, SWE Lead, Product AI; Sumeet Marwaha, Head of Data & Analytics; Pedro Franceschi, co-founder and CEO; David Horn, leads AI at Brex)
track: fleet
date: 2026-10-05
interviewer: desk (no interview)
method: desk
harnesses_frameworks: [Claude Code (interactive and headless), Cursor (self-hosted custom agents in a multi-agent migration pipeline), Claude Agent SDK (AI oncall engineer), MCP servers, CrabTrap (internal, open-sourced HTTP/HTTPS policy proxy with LLM judge), Signadot sandboxes for testing across engineers and agents]
domain: coding
runs_per_day: unknown (500+ Micronaut microservices; one engineer migrated 180 services in a month; "dozens of gRPC migrations" across a 400+ service monorepo; oncall agent runs per ticket)
failure_definition: "Agent 'finishes its changes, hits a wall of automated feedback it can't read, and stops. Or worse, it keeps going without that feedback and produces output that looks correct but isn't.' (Brex engineering blog)"
failure_rate_estimate: unknown
cost_per_failed_run: "unknown in money; before the closed-loop platform, engineers spent 'afternoons copying error logs and relaying automated feedback'"
last_failure:
  symptom: "On a live monorepo with real CI and review bots, coding agents could not read CI failures or bot comments; they stalled or produced plausible-looking but incorrect output"
  detected_by: manual
  time_to_why: unknown
  attributed_component: verification   # the feedback loop between agent and CI/review bots; environment contributes
  recurred: yes   # described as a general failure mode across migrations until the platform closed the loop
  their_words: "produces output that looks correct but isn't"
harness_change:
  last_change: "Closed-loop platform that forwards CI failures, review-bot comments and test results to agents in isolated remote dev environments (Slack message → environment with agent and toolchain); self-hosted Cursor agent pipeline that writes, builds and self-corrects; CrabTrap network policies derived from observed agent behaviour; per-directory CLAUDE.md with a CI check for stale docs"
  regression_detection: ci   # stated for docs drift and for agent PRs (CI + review bots); nothing described for agent-behaviour regressions
  silent_regression_experienced: unknown
  would_pay_to_prevent: unclear
controls_owned (fleets): [rules_files, ci_checks, mcp_servers, tool_allowlists, permissions]   # stated: CLAUDE.md tree (Product AI), docs-drift CI, MCP servers, CrabTrap allow/deny rules and LLM-judge policies, isolated remote environments
tooling_today: [Claude Code, Cursor, Claude Agent SDK, CLAUDE.md per directory, /submit-pr and other slash commands, Brex Explorer (text-to-SQL via Claude Code + MCP), CrabTrap (PostgreSQL audit log of every request and decision), Datadog (logs/metrics consumed by the oncall agent), Linear, Glean, Snowflake, Signadot]
coding_agent_traces_flow_to: other   # stated: CrabTrap logs every agent network request and decision to PostgreSQL; Datadog is used for application logs; no statement that agent traces reach Datadog
can_reproduce_failed_run: partially   # inferred: agents run in isolated remote environments with full toolchain and the audit log, but no replay is described
has_compared_cohorts: yes   # stated: 3 engineers / 50 services / one quarter vs 1 engineer / 180 services / one month (32x per capita)
most_wanted_question: unknown
data_constraints:
  cannot_leave: unknown   # fintech; agents hold real credentials, which is why egress is policed; no statement on transcripts leaving
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: dev_productivity   # inferred: Product AI team and platform engineering own the tooling; CEO sponsors the security approach
credible_contract_size: unknown
automation_limits: "Migrations run 'end-to-end without human intervention until final review'; CrabTrap passes routine requests on static rules and routes high-risk actions (e.g., sending email) to an LLM judge; fallback mode is deny when the judge is unavailable; 'you're the reviewer of the changes that Claude introduces'"
would_allow_pause_stop_on_evidence: yes   # stated for network actions: CrabTrap denies requests on policy evidence
reaction:
  would_use_next_week: unknown
  does_not_believe: unknown
design_partner_candidate: unknown
referrals: []
quotes:
  - q: 1
    text: "the agent finishes its changes, hits a wall of automated feedback it can't read, and stops. Or worse, it keeps going without that feedback and produces output that looks correct but isn't."
  - q: 21
    text: "the network layer was an untapped enforcement point"
  - q: 21
    text: "every request an agent makes is an opportunity to intercept, reason about, and make a policy decision"
  - q: 9
    text: "Having up-to-date documentation is something you can trust—it's so powerful"
  - q: 9
    text: "Instead of being in the driver's seat, you're the reviewer of the changes that Claude introduces. You're guiding the vision and direction."
sources:
  - https://claude.com/blog/how-brex-improves-code-quality-and-productivity-with-claude-code
  - https://www.brex.com/journal/building-autonomous-agents-for-technical-tasks
  - https://www.brex.com/journal/agent-automations-for-big-migrations
  - https://www.brex.com/journal/how-we-built-an-ai-oncall-engineer
  - https://github.com/brexhq/crabtrap
  - https://venturebeat.com/orchestration/brex-assumes-its-ai-agents-could-do-anything-so-it-watches-the-network-not-the-code
  - https://venturebeat.com/orchestration/brex-built-its-ai-agent-policy-by-watching-what-agents-actually-do-not-by-writing-rules-first
  - https://www.zenml.io/llmops-database/autonomous-ai-agents-for-engineering-tasks-with-closed-loop-feedback-systems
  - https://www.signadot.com/case-studies/brex-uses-signadot-to-scale-developer-testing-across-100s-of-engineers/
  - https://claude.com/customers/brex
tags:
  harnesses_frameworks: stated (Anthropic blog; Brex journal posts; CrabTrap README; Signadot case title)
  runs_per_day: stated counts (500+, 180, 400+, dozens)
  failure_definition / last_failure: stated (Brex journal, via snippets); attributed_component inferred (feedback loop = verification/environment)
  detected_by: inferred (engineers were relaying logs by hand)
  harness_change.last_change: stated
  regression_detection: stated (CI, review bots, docs-drift check); absence of behaviour gate inferred
  controls_owned: stated
  coding_agent_traces_flow_to: stated (CrabTrap PostgreSQL audit trail) ; "other" because it is not an observability vendor
  can_reproduce_failed_run: inferred
  has_compared_cohorts: stated (before/after per-capita comparison)
  budget_owner: inferred
  automation_limits: stated (Brex journal, CrabTrap README: fallback deny; VentureBeat: LLM judge for high-risk actions, ~2%)
  would_allow_pause_stop_on_evidence: stated for network actions
  quotes: q1 and q9 verbatim via snippets/fetched page; q21 verbatim from VentureBeat snippets
```

## Evidence

- Anthropic blog (30 Oct 2025): 50% Claude Code adoption heading to 100%; "Each major directory in the monorepo now has its own CLAUDE.md file containing domain-specific context" (Mastercard integration, banking regulations); the Product AI team "implemented CI/CD checks that verify when code changes might outdate documentation, prompting updates"; custom commands such as /submit-pr preload git status and PR data; headless mode built a submission agent in hours; Brex Explorer is text-to-SQL on Claude Code + MCP (https://claude.com/blog/how-brex-improves-code-quality-and-productivity-with-claude-code).
- Brex journal, "Building autonomous agents for technical tasks: 5 lessons learned": on a live monorepo with real CI and review bots, the agent "finishes its changes, hits a wall of automated feedback it can't read, and stops. Or worse, it keeps going without that feedback and produces output that looks correct but isn't." Brex built a platform that reads a Slack message describing a bug or refactor, spins up a dedicated remote environment with an agent and full toolchain, and forwards CI failures, bot comments and test results back to the agent; it ran "dozens of gRPC migrations" across a 400+ service monorepo "without human intervention until final review" (https://www.brex.com/journal/building-autonomous-agents-for-technical-tasks; https://www.zenml.io/llmops-database/autonomous-ai-agents-for-engineering-tasks-with-closed-loop-feedback-systems).
- Brex journal (Jul 2026), "Agent automations for big migrations": Micronaut is used across 500+ Kotlin microservices; migrating 50 services from Micronaut 3 to 4 took three engineers a full quarter; a pipeline of "custom self-hosted AI agents in Cursor that are capable of writing, building, and dynamically self-correcting code" let one engineer migrate 180 services in one month, a 32x per-capita acceleration (https://www.brex.com/journal/agent-automations-for-big-migrations).
- CrabTrap (github.com/brexhq/crabtrap, MIT): "An HTTP/HTTPS proxy that sits between AI agents and external APIs, evaluating every outbound request against security policies before it reaches the internet." Agents connect via HTTP_PROXY/HTTPS_PROXY; TLS is terminated with per-host certificates; static prefix/exact/glob rules are checked first, then an LLM judge evaluates against natural-language policies; "Every request and decision is logged to PostgreSQL for a complete audit trail"; defaults: 30 s judge timeout, fallback deny, 50 req/s per IP, circuit breaker after 5 consecutive LLM failures (https://github.com/brexhq/crabtrap).
- Franceschi to VentureBeat: "the network layer was an untapped enforcement point" and "every request an agent makes is an opportunity to intercept, reason about, and make a policy decision"; policies are derived from observed agent behaviour rather than written up front; roughly 2% of requests reach the LLM judge, the rest pass on static rules; the motivation was that agents need real credentials and "traditional guardrails couldn't contain what those agents were doing with them" (snippet rendering) (https://venturebeat.com/orchestration/brex-assumes-its-ai-agents-could-do-anything-so-it-watches-the-network-not-the-code; https://venturebeat.com/orchestration/brex-built-its-ai-agent-policy-by-watching-what-agents-actually-do-not-by-writing-rules-first).
- Brex journal, "How we built an AI oncall engineer": a Slack-resident agent runs inside a Claude SDK session, pulls Datadog logs and metrics, Linear tickets, Glean docs, Snowflake data and the codebase, and posts root cause, affected customer, evidence with citations, open assumptions and a next step; 30–45 minutes of context gathering became about three minutes (https://www.brex.com/journal/how-we-built-an-ai-oncall-engineer).
- Signadot publishes a case study on Brex scaling developer testing "across 100s of engineers and agents" (title only) (https://www.signadot.com/case-studies/brex-uses-signadot-to-scale-developer-testing-across-100s-of-engineers/).
- Builder-side context: Brex runs Claude on Amazon Bedrock for expense automation (94% compliance rate vs 70% industry standard; 75% of expense transactions automated) (https://claude.com/customers/brex).
- Not public: a production incident caused by a coding agent, a regression traced to a CLAUDE.md or Cursor-agent change, cost events, or whether agent transcripts reach Datadog.

## What this case says for Gate A

Brex is now one of the best-documented fleets: it names a concrete non-model failure mode (agents blind to CI and review-bot feedback that "produce output that looks correct but isn't"), fixed it by engineering the feedback loop rather than by prompting, and governs agents at the network layer with a full audit log of every request and decision. It also owns the rules-file tree and gates docs drift in CI. What it does not have, publicly, is any gate on behavioural regressions when CLAUDE.md files, Cursor agent pipelines or CrabTrap policies change, and no stated replay. The CrabTrap log is a partial flight recorder (network only) and shows Brex's instinct is to build; a product would have to add the step-level trace, divergence analysis and attribution it lacks. Counts as attributed_component = verification (non-model) and has_compared_cohorts = yes; silent regression remains unknown.
