# Track 1: Incumbent Competitor Teardown (as of 2026-10-03)

Legend: **[V]** verified from a reachable primary source (GitHub, SEC, docs); **[S]** from a search excerpt of the vendor page; **[U]** unverified or third-party only. Many vendor sites were blocked by the research sandbox.

## Consolidation wave
| Target | Acquirer | Timing | Terms |
|---|---|---|---|
| Arize AI | Dynatrace | agreed Aug 2026, closed 1 Oct 2026 | $915M [S] |
| Galileo | Cisco (Splunk) | intent 9 Apr 2026, closed 22 May 2026, renamed "Splunk Agent Observability" 7 Aug 2026 | undisclosed [S] |
| Langfuse | ClickHouse | 16 Jan 2026 | undisclosed; stays OSS [V] |
| Portkey | Palo Alto Networks | agreed 30 Apr, closed 29 May 2026 | ~$117M to $140M per PANW 10-K [V] |
| W&B (Weave) | CoreWeave | 2025 | $1.7B; Weave now "CoreWeave Forge / Agent Lens" [V] |
| Promptfoo | OpenAI | 9 Mar 2026 | into "OpenAI Frontier" [S] |
| Helicone | Mintlify | Mar 2026 | maintenance mode [U] |

## Per-vendor findings

### LangSmith (LangChain)
- Trajectories view (2026): flattens nested runs in a thread into an ordered action sequence; covers LangGraph, OpenAI and Claude Agent SDKs, Codex, Claude Code, Cursor [S].
- Insights Agent: stratified sampling of up to 1,000 threads, dual semantic plus behavioral feature extraction (tool-call counts, retries, errors), weighted hierarchical clustering, LLM-judge labeling; ~$1 to $4 per 1,000 threads [community writeup, U-adjacent].
- **LangSmith Engine** (public beta 13 May 2026): watches production traces, clusters recurring failures into named issues, diagnoses root cause against traces and connected source code, opens a PR with a fix, proposes an online evaluator, adds failing traces to offline dataset [S]. Most complete shipped RCA loop among all vendors.
- Replay: run comparison across prompts and models; LangGraph checkpoint time travel in Studio (framework-bound). No fixture or deterministic replay of recorded runs.
- Runtime control via the runtime, not observability: LangSmith Fleet (Agent Inbox approvals), Managed Deep Agents interrupts, LLM Gateway spend limits [S].
- Harness modeling: Context Hub, SmithDB, sandboxes GA; no memory, permission or verification event model found.
- Pricing: Developer free (5k traces); Plus $39/seat/month incl. 10k base traces; overage $2.50 per 1k base traces (14-day), $5 per 1k extended (400-day) [S].
- Proprietary platform; SDKs MIT.

### Langfuse (ClickHouse)
- Agent Graph view (beta, inferred from timing/nesting); v4 data model rebuilt around every agent step (Aug 2026) [S]. Timeline view.
- **No automatic clustering, no RCA worker.** Instead "agent-native": MCP server, CLI 1.0, Claude Code skill so coding agents investigate via Langfuse [S].
- Replay: open-in-playground only (single step).
- Pricing: Core $29/month, Pro $199, each incl. 100k units; overage $8 per 100k graduated to $6 [S]. MIT core with `ee/` folder; 35.3k stars [V].

### Arize AX / Phoenix (Dynatrace)
- Phoenix node-based agent graph; **DECISION span kind added platform-wide v20.19.0 (1 Oct 2026)**; bash-tool spans marked error on non-zero exit (v20.17.0) [V].
- **Signal** (AX): scheduled scan of a project's traces, groups recurring failures into ranked issues with supporting traces, investigation, root-cause hypothesis, recommended prompt/code/config/eval change; PRs on Enterprise [S]. Docs reference "the common trajectory, affected cohort" — closest shipped language to cohort analysis, but no success-vs-failure divergence computation found.
- Trajectory Evals: roadmap issue #11654 (Feb 2026) "in progress / highest priority" [V]. Alyx 2.0 planning agent; PXI agent and MCP server [S/V].
- Pricing: AX Free 25k spans; **Pro $50/month incl. 50k spans + 10GB, then $0.0008/span + $3/GB** (Sept 2026) [S]; enterprise typically $50K to $100K/year [S].
- **Phoenix is Elastic License 2.0, not Apache** [V]; 11.7k stars. Post-acquisition licensing continuity unverified.

### Braintrust
- Topics: BERTopic-style clustering (UMAP + HDBSCAN + c-TF-IDF) with Task / Issues / Sentiment facets [S]. Loop agent explains traces, finds similar logs, generates scorers and datasets [S]. Core strength is production trace → test case → CI scorer.
- No agent-run replay, no multi-agent graph, no runtime control found.
- Pricing: Pro $249/month incl. 5GB and 50k scores; $3/GB; $1.50 to $2.50 per 1k scores [S].
- **$80M Series B led by ICONIQ (Feb 2026) at ~$800M valuation, $121M total** [S]. Independent.

### HoneyHive
- Trajectory View; HoneyHive v2 (5 May 2026) [S]. Claims span clustering (mechanism unknown). CI regression gating. $7.4M raised. No replay, RCA or control found.

### Galileo / Splunk Agent Observability
- Agent Graph with issue analytics on nodes; **Aggregate Agent Graph View** showing most-common paths across sessions, component performance and outliers [S] — closest shipped thing to a cross-run execution graph.
- Insights Engine upgraded to Signals (auto-generated metrics from observed failures) [S].
- **Agent Control** (replaces Protect, deprecated June 2026): checks model and tool inputs/outputs; decisions deny / steer / warn / log / allow; claimed Apache-2.0 open source March 2026 but no repo found on github.com/rungalileo [V-negative].

### Laminar
- Signals: natural-language failure description → run against every trace → online hierarchical clustering, denormalized onto the traces table in ClickHouse [V, docs PR #220].
- Coding-agent debugger (`LMNR_DEBUG=true`) traces a run; Claude Code/Cursor/Codex reads it via CLI, edits code, re-runs. Browser session replay for browser agents. Not deterministic replay.
- Pricing: Free 1GB; Hobby $30/month; Pro $150/month, $1.50/GB; Signals billed by analysis tokens [S]. Apache-2.0, Rust, 3.3k stars [V]. $3M seed Mar 2026 led by Atlantic.vc, YC S24 [S].

### Respan (ex Keywords AI)
- Gateway plus observability; evaluation agent localizes root causes to specific decisions and promotes capability evals into regression checks [S]. Team $198/month annual [S]. $5M Mar 2026 (Gradient, YC) [S].

### Portkey (Palo Alto / Prisma AIRS)
- Gateway-centric: 50+ guardrails, MCP Gateway (auth, access control, identity forwarding), Agent Gateway, per-key budgets [V]. No trajectory graph, clustering, replay or RCA. Gateway MIT 13.1k stars [V].

### OpenLIT
- OTel traces including Claude Code, Cursor, Codex, Windsurf sessions [V]. Rule Engine for runtime behavior control [V].
- **PR #1685 merged 1 Oct 2026 repositions OpenLIT as "Agent Harness Engineering"** (tools, context, prompts, memory, hooks, guardrails, feedback loops) with a Concepts glossary, Prompt Hub, Context storage, Vault. Branding plus glossary; **no discrete harness event schema** [V]. Apache-2.0, 2.8k stars.

### Datadog "Agent Observability" (renamed from LLM Observability, Sept 2026)
- Decision-path / execution graph, AI Agents Console fleet view, infinite-loop detection; frameworks: OpenAI Agents SDK, LangGraph, CrewAI, Bedrock, Google ADK [V/S]. No replay. Prompt-injection and PII detection (detect, not block).
- Pricing: Free 40k LLM spans; Pro $160/month incl. 100k LLM spans; $3.50 per 10k annual; **only LLM spans billed, tool/agent/retrieval spans free** [S].

### W&B Weave (CoreWeave Forge / Agent Lens)
- Rebuilt June 2026 "agent-native": sessions, turns, steps as first-class objects rolling up into agents; built on OTel GenAI semconv [S].
- **`weave-claude-code` plugin captures subagents as nested `invoke_agent` spans preserving the spawning tool-call id, permission requests as `forge.permission_request` events, and context-window compaction events** [V]. PII scrubbing "not yet implemented". The most explicit harness-event modeling shipped by any vendor.
- ARIA (GA 30 Jun 2026): coding agent over experiment and agent observability data [S]. Weave SDK Apache-2.0.

### Maxim AI
- Tracing, persona simulation, CI evals; Bifrost gateway (budgets, virtual keys, MCP) Apache-2.0 [V]. $3M seed 2024; no later round found [S].

### Sentry
- Agent Insights (runs, tool calls, cost); April 2026 auto-instrumentation for major SDKs [S]. Seer Agent (Apr 2026) RCA → PR, exposed via MCP/CLI [S]. Not agent-failure-specific clustering.

### New Relic
- Agentic AI Monitoring, Ground Truth MCP, SRE Agent for infra RCA; Agentic Platform (24 Feb 2026) [S]. Nothing agent-trajectory-specific.

### Dynatrace (+ Arize)
- AI Observability GA with Bedrock AgentCore, LangChain/LangGraph, ADK, OpenAI Agents SDK, MCP, CrewAI, PydanticAI, Microsoft Agent Framework, **Claude Code, GitHub Copilot SDK** [V]. Davis causal RCA over topology. Post-Arize gains Signal and Alyx.

### Grafana / Honeycomb
- Grafana AI Observability public preview 21 Apr 2026 on `gen_ai.*` spans; OpenLIT as instrumentation path; continuous output evaluation alerts [S].
- Honeycomb Agent Observability (12 May 2026): **Agent Timeline** renders multi-agent, multi-trace workflows as one view; AI Ecosystem fleet view; MCP calls first-class [S]. BubbleUp is a generic cohort-difference feature, not productized for trajectories [U].

## Concept-by-concept: closest shipped thing
| HRCP concept | Closest shipped | Remaining gap |
|---|---|---|
| First divergence (success vs failure cohort) | Arize Signal "common trajectory, affected cohort"; Galileo Aggregate Agent Graph; Honeycomb BubbleUp; LangSmith Insights behavioral clustering | No vendor computes or displays an explicit earliest-divergence step. Academic only. |
| Harness Event Model | Weave Claude Code plugin (permissions, compaction, subagents); Phoenix DECISION kind; OpenLIT "Agent Harness Engineering" branding | One plugin, one harness, no PII scrubbing. Nobody normalizes memory ops, verification, hooks, permissions across harnesses. OpenLIT owns the term. |
| Execution graph | Datadog decision path, Langfuse Agent Graph, Phoenix graph, Galileo Agent Graph + Aggregate, Harness.io "AgentTrace" | Single-run graphs are commodity. Cross-run aggregate: Galileo only. Provenance-typed causal edges: nobody. |
| Branch-aware / deterministic replay | AgentOps time-travel (depth unverified); LangGraph checkpoint rewind; Laminar re-run from step | **None of the 17 platforms ship fixture or deterministic replay with branching from a recorded production run.** Largest gap. |
| Incident-first UI | LangSmith Engine, Arize Signal, Galileo Signals, Braintrust Topics, Laminar Signals | Trace-cluster-first, not incident lifecycle; no linkage to runtime mitigation. |

## Commodity (five or more vendors)
Single-run agent graph; OTel `gen_ai.*` ingestion; coding-agent session tracing; production trace → dataset → evaluator → CI gate; topic/failure clustering (seven vendors in 2026); chat/MCP assistants; gateway guardrails and budgets; per-span/unit/GB pricing with free tiers.

## Not shipped well by anyone
1. Deterministic or fixture replay and branching of recorded production runs.
2. Computed success-vs-failure first-divergence primitive.
3. Cross-harness event model for context, memory, permissions, verification.
4. Closed loop from detected incident to runtime mitigation (the Arize→Dynatrace, Galileo→Splunk and Portkey→PANW deals are attempts to assemble this).
5. Subagent supervision (May 2026 cluster of six Claude Code issues: dispatch fabrication, silent stalls, no abort/timeout, scope expansion).
6. CI gating on trajectory shape rather than final output.

## Unverified items to re-check
Trajectories/Engine UI semantics; Galileo Agent Control OSS status; Phoenix license continuity under Dynatrace; Weave "signals" internals; HoneyHive/Maxim/Weave pricing; AgentOps replay depth and company health.
