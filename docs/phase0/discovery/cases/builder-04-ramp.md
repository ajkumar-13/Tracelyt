# Ramp: "Inspect", an OpenCode-based background agent on Modal sandboxes that writes 30% (Jan 2026) rising to 75% of merged PRs; verification is "feedback is everything", traces go to Braintrust, but no public failure or regression story

evidence_grade: B

Access note (pass 2, 2026-10-05): Ramp's primary post (builders.ramp.com "Why We Built Our Own Background Agent"), the Modal write-up, The Pragmatic Engineer deep-dive, InfoQ's January 2026 news item, Linear's customer story and three ZenML LLMOps-database summaries were all reached through search snippets (direct fetch is egress-blocked). Anthropic's Ramp customer page was fetched directly in pass 1. Every "carried, not re-verified" fact from pass 1 is now either snippet-verified or dropped. Grade B rather than A because no primary source describes a concrete failed run, its detection, or how Inspect changes are regression-tested.

```yaml
org: Ramp
role: Background-agent / DevEx (public: Zach Bruggeman; Jason Quense; Rahul Sengottuvelu)
track: builder
date: 2026-10-05
interviewer: desk
method: desk
harnesses_frameworks: [Inspect (built on OpenCode, server-first, "works with all the frontier models"), Modal Sandboxes with filesystem snapshots, Cloudflare Durable Objects + Agents SDK control plane (one SQLite DB per session), Claude Code, MCP servers (Datadog, Sentry, Snowflake)]
domain: coding
runs_per_day: "unknown sessions/day; 'hundreds of parallel sessions'; share of merged PRs: ~30% (Jan 2026, frontend+backend, 'past week'), 'about 40%' and 'over half' in later summaries, 75% per Linear customer story; 80% of Inspect itself written by Inspect"
failure_definition: "inferred: agent output that cannot be proven correct; Ramp frames the agent as a control system where 'feedback is everything' and the agent must 'observe reality: tests, telemetry'"
failure_rate_estimate: unknown
cost_per_failed_run: "unknown; one reconstructed work item across eight sessions used ~5.6M tokens and cost $93 (Pragmatic Engineer); Ramp says sessions are 'effectively free' on the infra side"
last_failure:
  symptom: "No concrete failed-run story published. Closest: in the separate Ramp Labs 'self-maintaining' agentic monitoring system, alert noise became a problem and agents produced duplicate work; reproducing complex conditions against a live deployment 'proved difficult'"
  detected_by: unknown
  time_to_why: unknown
  attributed_component: unknown
  recurred: unknown
  their_words: "subtle failure modes are rarely apparent from static code review alone"
harness_change:
  last_change: "Adoption of Inspect for 'most of its code' in Nov 2025; image registry rebuilt every 30 minutes so sandboxes are at most 30 minutes stale (continuous environment change)"
  regression_detection: unknown
  silent_regression_experienced: unknown
  would_pay_to_prevent: unknown
controls_owned (fleets): [mcp_servers, tool_allowlists, ci_checks]
tooling_today: [Sentry, Datadog, LaunchDarkly, Braintrust, GitHub, Slack, Buildkite (all wired into Inspect), Modal, Cloudflare Durable Objects, VS Code server + VNC/Chromium in sandbox]
coding_agent_traces_flow_to: other (Braintrust is wired into Inspect; Datadog/Sentry are read by the agent, not stated as trace sinks)
can_reproduce_failed_run: partially
has_compared_cohorts: unknown
most_wanted_question: unknown
data_constraints:
  cannot_leave: unknown
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: dev_productivity
credible_contract_size: unknown
automation_limits: "Each session is a disposable sandboxed VM; human review before merge; Inspect is 'built for internal use where all employees are trusted' (Open-Inspect README)"
would_allow_pause_stop_on_evidence: unknown
reaction:
  would_use_next_week: unknown
  does_not_believe: unknown
design_partner_candidate: unknown
referrals: [Zach Bruggeman, Jason Quense, Rahul Sengottuvelu]
quotes:
  - q: 9
    text: "One useful way to think about agents: they're control systems. Generating output is easy. Feedback is everything."
  - q: 9
    text: "It wrote 30% of merged frontend + backend PRs in the past week. It's powered by @opencode, @modal and @CloudflareDev."
  - q: 15
    text: "subtle failure modes are rarely apparent from static code review alone"
    paraphrase: true
  - q: 1
    text: "1+ million lines of AI-suggested code implemented in just 30 days"
sources:
  - https://builders.ramp.com/post/why-we-built-our-background-agent
  - https://x.com/zachbruggeman/status/2010728444771074493
  - https://x.com/eglyman/status/2010776124037743088
  - https://x.com/rahulgs/status/2010734250203455862
  - https://modal.com/blog/how-ramp-built-a-full-context-background-coding-agent-on-modal
  - https://newsletter.pragmaticengineer.com/p/why-ramp-built-inspect
  - https://infoq.com/news/2026/01/ramp-coding-agent-platform/
  - https://linear.app/customers/ramp
  - https://www.zenml.io/llmops-database/building-an-internal-background-coding-agent-with-full-development-environment-integration
  - https://www.zenml.io/llmops-database/building-a-full-context-background-coding-agent-with-sandboxed-development-environments
  - https://www.zenml.io/llmops-database/agentic-system-for-autonomous-code-monitoring-and-maintenance
  - https://ramplabs.substack.com/p/self-maintaining
  - https://claude.com/customers/ramp
  - https://github.com/ColeMurray/background-agents
tags:
  harnesses_frameworks: stated (Bruggeman and Sengottuvelu posts name OpenCode, Modal, Cloudflare; InfoQ/Pragmatic Engineer name Durable Objects, SQLite per session; claude.com names Claude Code + MCP)
  runs_per_day: stated (30% in Bruggeman post, Jan 2026; 75% in Linear story; "over half" in ZenML summary; "hundreds of parallel sessions" in InfoQ snippet)
  failure_definition: inferred (from Glyman's "control systems / feedback" framing and the Modal post's verification loop)
  cost_per_failed_run: stated (Pragmatic Engineer: $93 / 5.6M tokens for eight sessions; "effectively free" claim is Ramp's, caveat is the author's)
  last_failure.symptom: stated for the Ramp Labs monitoring system (noise, duplicate work, reproduction difficulty), which is a different Ramp agent, not Inspect
  last_failure.their_words: paraphrase from ZenML summary of the Modal post
  harness_change.last_change: stated (Linear story: Nov 2025 decision; ZenML: 30-minute image rebuilds)
  regression_detection: unknown (Braintrust is listed as wired in, but no source says what it gates)
  tooling_today: stated (Ramp builders post via ZenML snippet: "wired into Sentry, Datadog, LaunchDarkly, Braintrust, GitHub, Slack, and Buildkite")
  coding_agent_traces_flow_to: inferred (Braintrust is an eval/observability product and is listed among the integrations; the source does not say traces are stored there)
  can_reproduce_failed_run: inferred (sandbox snapshots and "reproduce bugs end-to-end against live code" are stated capabilities for the agent; nothing says a past failed session can be replayed)
  automation_limits: stated (Open-Inspect README on Ramp's trust model; Modal post on disposable sandboxes)
  budget_owner: inferred
```

## Evidence
- Inspect "wrote 30% of merged frontend + backend PRs in the past week" and "is powered by @opencode, @modal and @CloudflareDev" (Zach Bruggeman, Jan 2026) (https://x.com/zachbruggeman/status/2010728444771074493).
- Rahul Sengottuvelu: Inspect "works with all the frontier models", has "a cloud hosted version of vscode, chromium, and terminal" and "all the tooling and skills a ramp engineer would have" (https://x.com/rahulgs/status/2010734250203455862).
- CEO Eric Glyman frames agents as control systems: "Generating output is easy. Feedback is everything"; Inspect translates English into code "and then observe[s] reality: tests, telemetry" (https://x.com/eglyman/status/2010776124037743088).
- Each session is a Modal Sandbox holding a full dev environment (Postgres, Redis, Temporal, RabbitMQ, Ramp services), OpenCode as the agent, a VS Code server, web terminal, and VNC + Chromium for visual verification; backend work can run tests, review telemetry and query feature flags (https://modal.com/blog/how-ramp-built-a-full-context-background-coding-agent-on-modal ; https://builders.ramp.com/post/why-we-built-our-background-agent).
- Control plane on Cloudflare Durable Objects with the Agents SDK; every session gets its own SQLite database so "hundreds of parallel sessions" cannot affect each other; a queue routes prompts from four clients into one running session (https://infoq.com/news/2026/01/ramp-coding-agent-platform/ ; https://newsletter.pragmaticengineer.com/p/why-ramp-built-inspect).
- Inspect is "wired into Sentry, Datadog, LaunchDarkly, Braintrust, GitHub, Slack, and Buildkite"; the image registry rebuilds each repo image every 30 minutes and sessions start from snapshots, so code is at most 30 minutes stale (https://www.zenml.io/llmops-database/building-an-internal-background-coding-agent-with-full-development-environment-integration ; https://builders.ramp.com/post/why-we-built-our-background-agent).
- Reason for building: local machines could run only one or two agent sessions; Ramp "strongly recommend[s]" OpenCode because it is server-first with TUI and desktop as clients (https://newsletter.pragmaticengineer.com/p/why-ramp-built-inspect ; https://infoq.com/news/2026/01/ramp-coding-agent-platform/).
- Cost: one work item reconstructed across eight sessions used roughly 5.6 million tokens and cost $93; Ramp says sessions are "effectively free" on infrastructure, which the Pragmatic Engineer author questions at scale (https://newsletter.pragmaticengineer.com/p/why-ramp-built-inspect).
- In Nov 2025 Ramp "made the call to hand most of its code" to Inspect, which "now writes three of every four PRs Ramp merges"; 80% of Inspect was written by Inspect (https://linear.app/customers/ramp ; https://infoq.com/news/2026/01/ramp-coding-agent-platform/).
- The sandbox lets the agent "reproduce bugs end-to-end against live code"; "subtle failure modes are rarely apparent from static code review alone" (ZenML summary of the Modal post) (https://www.zenml.io/llmops-database/building-a-full-context-background-coding-agent-with-sandboxed-development-environments).
- Separate Ramp Labs system for self-maintaining code monitoring: alert "noise became a problem", triage was added to adjust or remove noisy monitors and record PR links to prevent duplicate work; "reproducing complex conditions against a live deployment proved difficult, while code-based integration tests worked better" (https://ramplabs.substack.com/p/self-maintaining ; https://www.zenml.io/llmops-database/agentic-system-for-autonomous-code-monitoring-and-maintenance).
- Claude Code connected to Datadog and Sentry via MCP for incident response ("up to 80% reduction in incident investigation time"); "1+ million lines of AI-suggested code implemented in just 30 days" (https://claude.com/customers/ramp).
- Open-Inspect, a public clone, notes Ramp's design "was built for internal use where all employees are trusted and have access to company repositories" (https://github.com/ColeMurray/background-agents).

## What this case says for Gate A
Ramp is a strong-shape builder: it owns an open-source-based harness (OpenCode fork plus its own control plane), runs hundreds of parallel sessions, and the harness now produces most merged code, so any change to prompts, skills, sandbox images or model routing is a production change with wide blast radius. The verification philosophy ("feedback is everything", reproduce against live code) is the same thesis as replay and first-divergence analysis. Braintrust is already wired in, which means an eval and trace incumbent exists and we would need to interoperate rather than replace. What is missing publicly, and keeps this at grade B: no named failed run, no root-cause time, no statement of how Inspect changes are gated before rollout, and nothing on whether code or traces may leave Ramp. The Ramp Labs note that reproducing conditions against live deployments "proved difficult" is a small but direct signal that reproduction is the hard part even for a team with full sandboxes. Counts: silent_regression unknown, attribution unknown, traces to Braintrust (other), cannot_leave unknown.
