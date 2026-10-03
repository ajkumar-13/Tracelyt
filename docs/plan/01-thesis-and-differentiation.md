# PLAN-01 — Thesis and Differentiation

## 1. The one-paragraph thesis

Production AI agents fail because of the system around the model, not the model. The industry has solved collection (89% of teams have observability, 71% of production teams have step-level tracing) and has commoditized clustering (seven vendors group failing traces into issues). What nobody has built is the engine that takes a fleet of agent runs and answers, with evidence: **which harness component caused this class of failure, where exactly the trajectories first diverged, can we reproduce it, does the proposed fix eliminate it on historical failures without introducing new ones, and should the harness be changed or the agent stopped next time**. We are building that engine, on an open event model and execution graph for harnesses, with replay as the proof mechanism, and we are building it for both the harnesses people build and the harnesses they buy.

## 2. Why now (evidence, October 2026)

1. **Failures are now harness failures.** Research consensus: "Model or Harness?" localizes 41 failure modes to component edges; Jarmak's 206-record monograph on coding agents finds many apparent model failures originate elsewhere; deepset shows harness-only changes move agents 20+ leaderboard positions; Governance Decay shows compaction raises constraint violations from 0% to 30% and fixes them with pinning. Sequoia names harnesses a scaling pillar.
2. **Fleets exist.** Cursor cloud agents run >50M actions per day across multi-day runs; Codex P99 users run >60 agent-hours per day; Devin merges 67% of PRs, so a third of fleet output fails; Copilot's coding agent opened >1M PRs in four months; Claude Code is a >$2.5B run-rate product whose median session is one human prompt followed by autonomous work.
3. **Incidents are the kill mechanism.** Gartner (May 2026): 40% of enterprises will demote or decommission autonomous agents by 2027 because of governance gaps found only after production incidents. Public incident catalogue: 1.67B-token loops, compaction double-billing, overnight $6,000 bills, production databases deleted, Anthropic's own weeks-long undetected degradation hitting ~30% of Claude Code users.
4. **Observability is saturated and consolidating.** Arize to Dynatrace ($915M), Galileo to Cisco, Langfuse to ClickHouse, Portkey to Palo Alto, Promptfoo to OpenAI, all in 2026. Gartner treats agent observability as a feature of the observability platform. Visibility is a feature now. The next layer is not.
5. **Standards have a hole exactly where we live.** OTel `gen_ai.*` defines agent, tool and memory operation names but has no convention, even in draft, for permission decisions, context compaction, context provenance, verification or stop reasons. The two proposals that come closest (issues #159 and #181) have no maintainer uptake. The hook contracts of Claude Code, Codex and Gemini CLI have converged, so one adapter covers three closed harnesses.
6. **The biggest vendors build this in-house and the rest cannot.** Cursor built checkpoint/fork VM pipelines, CursorBench from real sessions, and review agents "whose mistakes become future evaluation cases". Replit built self-testing loops. Everyone below that tier buys LangSmith or Braintrust and gets visibility, not a loop.

## 3. What we are not

Per HRCP-00 §4 and HRCP-02 §92, and sharpened by the research:

- Not LLM observability. Spans, dashboards and token cost are substrate we ingest and emit, never the product.
- Not an eval platform. Evals are an input. Testing on synthetic data before shipping is Patronus, Coval, Braintrust. We test on real history.
- Not an agent security firewall. Blocking at a gateway is Zenity, Noma, Palo Alto. We prevent by fixing the harness, and we hand our evidence to the firewalls.
- Not a gateway, memory platform, prompt CMS, agent builder, MCP marketplace, or IAM.
- Not a trace viewer with an AI chat bolted on.

## 4. The seven differentiators, ranked by defensibility

Ordered by how far anyone else is from shipping them, per `docs/archive/research/01` and `02`.

| # | Differentiator | Closest competitor | Their distance |
|---|---|---|---|
| 1 | **Branch-aware replay of recorded production runs**, pairing frozen model and tool fixtures with per-step environment snapshots, with disclosed fidelity levels | Laminar (re-run from a step, non-deterministic), LangGraph time travel (re-executes LLM calls), AgentOps (visual replay) | None of 17 observability platforms ship it. Largest open gap. |
| 2 | **Regression against production failures as a CI gate on harness changes**: "re-run last week's 500 failures against the new compaction policy, report success, cost, new failures, fixed failures" | Judgment Labs (validate fixes against production cases), Raindrop (announced pre-ship simulation), Cursor internally | Nobody ships it as a gate on prompt, tool schema, permission, retry, model or compaction changes. |
| 3 | **Computed first divergence** between success and failure cohorts, as a displayed primitive with confidence | Arize Signal ("common trajectory, affected cohort" in docs), Galileo Aggregate Agent Graph (path frequency) | Academic only. LongRCA best is 24% exact root step. Hard, therefore defensible. |
| 4 | **Component-level attribution on an execution graph** with provenance-typed edges (observed, reconstructed, inferred) and the observed/statistical/causal distinction enforced in product | LangSmith Engine and Arize Signal attribute to code and prompts, not to harness components; no vendor distinguishes edge provenance | Attribution exists; honest, component-level, evidence-typed attribution does not. |
| 5 | **Cross-harness control-event model**: compaction, permissions, verification, memory provenance, subagent delegation, stop reasons as typed events across open and closed harnesses, with fidelity disclosure | W&B weave-claude-code plugin (permissions and compaction, Claude Code only); Phoenix DECISION span kind; OpenLIT "harness engineering" branding without a schema | One plugin, one harness. We cover six frameworks plus three CLIs with one model. |
| 6 | **Harness Reliability Score and recommendations with replay-proven deltas**: a component scorecard ("your compactor drops 23% of declared state; your retry policy has no progress check") with each recommendation carrying a measured success and cost delta | Nobody | Requires 1 through 5. This is the product customers will talk about. |
| 7 | **Success-adjusted economics**: cost per verified success, loop waste, reread waste, subagent cost, by harness version | Datadog and LangSmith do cost per run or token | Nobody ties cost to verified outcomes and harness version. |

Everything else in HRCP-00 §50 (whole-harness semantics as vocabulary, single-run execution graphs, incident-first UI, policy-backed intervention) is either commodity or owned by a different buyer. We build them because the engine needs them, not because they differentiate.

## 5. Why the "complete engine" is the moat, and what that means concretely

HRCP-00 §37 is right that no single layer is a moat. The moat is the loop, for four compounding reasons:

**(a) Each stage makes the next stage's data better.** Detectors produce labeled failures. Incidents group them into cohorts. First divergence localizes them. Replay confirms or refutes the localization. Regression tells us whether the fix generalized. That last signal, "did the fix work in production", is the label nobody else collects. Over time it trains the attribution models, and the attribution models make replay cheaper by narrowing where to fork.

**(b) The failure corpus is unique by construction.** Execution graph + harness configuration + failure + first divergence + root component + fix + replay result + production outcome. Model labs do not have this (they have model I/O). Observability vendors have traces without fixes or outcomes. Eval vendors have synthetic cases. Only a system that runs the whole loop can collect it, and only with explicit data rights (HRCP-02 §60).

**(c) Replay infrastructure is slow to copy and gets more valuable with every fixture.** Fixture bundles, sandbox snapshots, side-effect classification of tools and MCP servers, network fixtures for external services: each is accumulated engineering that a trace-first vendor must start from zero. Cursor built it internally for one harness. We build it for all of them.

**(d) The standard is distribution, not protection.** Open instrumentors for six frameworks and three CLIs put our event model in the path of every agent built on them. Customers arrive with data already in our shape. We never need to win on schema; we need to be the best consumer of it.

What the moat is **not**: ClickHouse, the UI, the schema, the detectors (we open-source the basic ones), or a proprietary transport. If a competitor copies all of those they have a better observability tool and still no loop.

## 6. How we are different from each competitor class, in one sentence each

- **Observability platforms (Datadog, Dynatrace+Arize, Splunk+Galileo, Grafana, Honeycomb, New Relic):** they show what happened across your stack; we tell you which harness component caused it and prove the fix. We export incidents back into them and never ask customers to replace them.
- **LLM engineering platforms (LangSmith, Langfuse, Braintrust, W&B Weave):** they cluster failing traces and some open PRs against prompts and code; we attribute to harness components, reproduce on historical runs, and gate harness changes in CI. LangSmith Engine is the closest and is bound to LangChain's distribution.
- **Agent reliability newcomers (Raindrop, Laminar, Judgment Labs, Sentrial, Moda):** they detect and cluster silent failures; we add deterministic replay, regression gating, component attribution and the open event model. Laminar is the nearest in wedge and smallest in resources.
- **Eval and simulation (Patronus, Coval, Scorecard, Bespoke, HUD, Veris):** they test agents against synthetic worlds before shipping; we test harness changes against what actually broke in production.
- **Provenance and audit (Entire Checkpoints, Vorlon):** they record what the agent did for governance; we reconstruct why it failed and prevent recurrence. Entire's git-attached sessions are a capture source we should ingest.
- **Agent security (Zenity, Noma, Straiker, AIR, Palo Alto/Portkey, Okta):** they block unsafe actions at the gateway for the CISO; we remove the harness defect that made the action likely, and feed them evidence.
- **Platform vendors (Anthropic, OpenAI, Google, Microsoft, GitHub):** they ship usage and ROI analytics, raw traces and audit logs for their own agents; we work across all of them, which no single vendor will do, and we gate the harness changes their own postmortems show they lack.
- **Durable execution (Temporal, Restate, Inngest, DBOS):** they journal steps for crash recovery inside their runtime; we replay any harness, including ones not authored in an engine, and we use their journals as a Tier A capture source.

## 7. Target customers

Two ICP tracks from day one, one strategic track:

1. **Builders (open harness).** Teams running production agents on LangGraph, Agents SDK, ADK, PydanticAI, Claude Agent SDK, OpenHands, or custom loops, with runs over five minutes, five or more tools, persistent state, subagents, real-system mutation, verification gates, and repeated task classes (HRCP-00 §32). They can emit the full event model. They own their harness and can change it, so attribution is directly actionable.
2. **Fleets (closed harness).** Platform teams running Claude Code, Codex, Cursor, Devin or Copilot coding agents at scale, typically several at once (GitHub Agent HQ lets you assign one issue to three agents). They cannot change the vendor harness but they control the configuration around it: CLAUDE.md and rules files, hooks, permission policies, MCP servers, tool allowlists, model and effort settings, budgets, CI verification. Those are harness components too, and they regress.
3. **Harness vendors (strategic).** Cognition, Cursor, Factory, Replit, Sierra, and the model labs' own agent products. They have the problem at the largest scale, build partial solutions internally, and their adoption of the event model is the fastest route to standardization. Treat as design partners, not just prospects.

Domains: coding agents first because verification is objective and environments snapshot cleanly; API-driven workflow and back-office agents second because tasks repeat and external services can be mocked. Both are in scope from Phase 1 with a 100-engineer team. Horizontal "any agent" messaging waits until the regression gate is proven in both.

## 8. One-sentence definitions to test with customers

- "The reliability engine for the system around the model."
- "Find which harness component broke your agents, reproduce it, prove the fix on last week's failures, and stop it from coming back."
- "Harness engineering, with evidence."

The HRCP-00 §84 definition stands as the long form.
