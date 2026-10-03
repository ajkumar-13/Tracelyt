# Track 2: Emerging Agent-Reliability Startups and Category Dynamics (as of 2026-10-03)

Legend: **[single-source]** rests on one aggregator or press snippet; **[unverified]** could not be corroborated. Capability codes: R replay, G regression/CI, C root cause or clustering, K runtime control.

## Direct overlap with the HRCP wedge

**Laminar** (YC S24; $3M seed Mar 2026 led by Atlantic Labs with YC, AAL). One-line tracing; Agent Debugger re-runs from any step with prior context; browser session replay; Signals clustering. Positioned at long-running agents. R, C. No G or K. **Threat: high. Same wedge, tiny team.**

**Raindrop** ("Sentry for AI agents"). $15M seed led by Lightspeed (Figma Ventures, Vercel Ventures, founders of Replit/Cognition/Notion); Series A led by CRV ~18 Sept 2026, total ~$50M [single-source]. Background agents triage production traces into issues with step-by-step explanations; expanding to "simulating changes before they ship". C strong, G early. **Threat: very high on detection and clustering.**

**Sentrial** (YC W26, "Datadog for Agent Reliability"). SDK wrapper; detects loops, hallucinations, tool misuse, quality regressions; RCA and fix recommendations. Claims $30K MRR in batch [single-source].

**Moda** (YC W26). Diagnose failures → generate validated fixes → ship. C, light G.

**ASHR.io** (YC W26). Evals plus observability, multimodal. Early.

**Judgment Labs**. $32M seed plus Series A, both led by Lightspeed (May 2026). Judgeval OSS SDK: tracing plus agent-judge evals over full trajectories; "validate fixes against real production cases". C, G. **Threat: high.**

**Quotient AI** → acquired by Databricks (11 Mar 2026). Analyzed full agent traces, auto-clustered signals into eval datasets feeding RL loops. Folded into Genie / Agent Bricks. Signal: failure clustering → regression dataset is being absorbed by platforms early.

**Relai** (RELAI Inc., Soheil Feizi). $6.9M total (June 2026, .406 Ventures). Verifiable continual learning: failures, traces, evals → learning environments; RCA; in-loop regression controls. Launch stage.

**AgentOps** (Agency AI). $2.6M pre-seed Aug 2024; no later round found. Session replays, step-by-step execution graphs, "time-travel debugging" (visual, not deterministic re-execution). Pricing: free 50K events; Pro $49/month for 500K events [single-source]. Owns the "AgentOps" term.

**Entire** (Thomas Dohmke, ex GitHub CEO). Launched 10 Feb 2026; **$60M seed at ~$300M valuation led by Felicis** (Madrona, M12, Basis Set). OSS CLI "Checkpoints" attaches agent sessions (prompts, decisions, execution context) to git commits. Governance and provenance framing. Recording only so far. **Threat: high on "coding-agent flight recorder" mindshare and capital.**

**Vorlon** "AI Agent Flight Recorder" (RSAC, 25 Mar 2026). Cross-SaaS audit trail for SecOps. Uses the exact term; different buyer.

**Lemma**. $2.3M pre-seed (Matrix, YC) for "silent AI agent failures in production".

**OSS and indie**: AgenticLedger (proxy flight recorder), agent-replay (SQLite time-travel: replay, diff, fork), agent-timetravel (OTel in, replay out, branch and diff), unworldly (audit trail for Claude Code/Cursor/Devin/Cline), AgentLens, ChainWatch, airblackbox, NoireBox. Undo (classic time-travel debugger) integrated with Claude Code/Codex in 2026; Replay.io shipped Replay MCP. Signal of demand; crowded at the bottom.

## Agent testing, simulation, regression
| Company | Funding | What ships |
|---|---|---|
| Coval (ex-Waymo eval) | $3.3M seed; **$28M Series A 24 Jun 2026 (Norwest)**; $31M total | Simulation and monitoring for voice and chat agents |
| Scorecard (ex-Waymo/Uber AV sim) | $3.75M seed | Tens of thousands of tests daily in virtual environments |
| Patronus AI | **$50M Series B 26 Jun 2026 (Greenfield; Lightspeed, Datadog)**; $70M total; "15x YoY revenue" | Eval judges; "Digital World Models" synthetic environments for long-horizon agent testing |
| Braintrust | $80M B Feb 2026 at $800M | Evals, Brainstore, Loop |
| Confident AI (DeepEval) | $2.2M seed | OSS regression and A/B testing |
| Okareo | $700K pre-seed [single-source] | Pivoted from generic eval to user simulation |
| Freeplay | ~$8.9M total | Prompt mgmt, evals |
| HoneyHive | $7.4M | Agent evals and observability |
| LangWatch | €1M | Agent simulation testing |
| Maxim AI | $3M seed | Simulation, evals, Bifrost gateway |
| Hamming, Cekura, Bluejay, Roark | $2M to $4.5M each | Voice agent testing |
| Guardrails AI / Snowglobe | acquired by Harvey 2026 | Persona and scenario simulation |
| HUD (YC W25) | — | OSS RL environments for computer-use agents |
| Veris AI | — | Stateful simulations, tool mocks |
| Bespoke Labs | **$40M Series A Jul 2026 (Wing, 8VC)** | Simulated firms for long-horizon agent training and testing |
| Promptfoo | $23M raised; acquired by OpenAI 9 Mar 2026 | OSS eval and red-team CI; 25% of F500 |

## Runtime guardrails, control planes, kill switches (security-owned)
| Company | Status |
|---|---|
| Invariant Labs | acquired by Snyk, 24 Jun 2025 |
| Lakera | acquired by Check Point, ~Sept 2025, est. $300M |
| Prompt Security | acquired by SentinelOne, Aug 2025, ~$250M |
| Aim Security → Cato; Apex → Tenable | 2025 |
| Noma Security | $100M Series B Jul 2025 (Evolution Equity) |
| Zenity | **$125M Series C ~3 Aug 2026 (Norwest)**; $185M total |
| Straiker | $64M Series A 29 Jun 2026; $85M total |
| AIR Security | **$50M seed 1 Sept 2026 (Sequoia, Greenoaks)**; inline firewall vetting agent skills, plugins, MCP servers |
| Pillar, Lasso, Operant, Astrix | $9M to $28M; MCP security gateways, shadow-agent control planes |
| RuntimeAI, JetStream | Kill switch <100ms, fleet-wide stop, budget circuit breakers [funding unverified] |
| Okta | AI kill switch announced Oktane 2026, GA by end-2026 |
| Portkey | acquired by Palo Alto Networks, closed May 2026 |
| Regulatory | "AI Kill Switch Act" introduced 23 Jul 2026 (Lieu/Moran) |

Aggregate: one analysis puts agentic-AI security at $3.6B Crunchbase funding and $96B M&A into RSAC 2026 [single-source, broad definition].

## Observability newcomers vs incumbents
- Langfuse → ClickHouse (Jan 2026); Helicone → Mintlify (maintenance); Galileo → Cisco/Splunk (May 2026); W&B → CoreWeave ($1.7B); Arize $70M C (Feb 2025) then → Dynatrace; LangChain $125M B at $1.25B (Oct 2025); Traceloop $6.1M seed ("stop AI agents from going rogue"); Comet Opik; Pydantic Logfire; Lunary, Keywords AI, Langtrace, Evidently (no 2025–26 news found).
- Fiddler "Agentic Observability"; Datadog AI Agents Console, Trace Cluster Map, acquired Adaptive ML (RL post-training, Jun 2026); Dynatrace coding-agent monitoring (Claude Code, Gemini CLI, Codex CLI, OpenCode, Copilot SDK); Dash0 AI Coding Insights; MintMCP Agent Monitor; XTrace.
- Durable execution: **Temporal $550M Series E at $12.55B (Sept 2026)**; Restate $20M A; Inngest AgentKit; DBOS; Trigger.dev $16M; Mastra $22M. Replay as a runtime byproduct.

## Coding-agent-specific reliability tooling (thin)
Entire (provenance), Dynatrace, Dash0, MintMCP, XTrace (telemetry dashboards), OSS audit trails. **No funded startup found doing production regression testing of coding-agent harness changes or replay of Claude Code/Codex/Devin runs.**

## Shutdowns and pivots
Humanloop (shut Sept 2025 after Anthropic acqui-hire), Context.ai (shut after OpenAI acqui-hire), Atla Insights (shut 16 Feb 2026), Athina → Gooseworks pivot, Helicone maintenance mode, Okareo narrowed to simulation. "Four of the category's most recognized platforms acquired or shut down as independents within 11 months."

## Threat map
**Tier 1, direct overlap, funded, shipping:** Raindrop, Laminar, Judgment Labs, Sentrial/Moda, Entire.
**Tier 2, adjacent, could expand:** Braintrust, LangSmith (Engine, LangGraph time travel), Patronus/Coval/Scorecard/Veris/Bespoke/HUD, Datadog/Dynatrace/Dash0/Fiddler, durable-execution engines, AgentOps.
**Tier 3, control is security-owned:** Zenity, Noma, Straiker, AIR, RuntimeAI, Okta, Vorlon, Portkey/PANW, Lasso, Pillar.

**Gaps unfilled (Oct 2026):** deterministic replay plus diff of production runs coupled with clustering and regression CI; regression of harness changes against recorded production incidents as a CI gate; coding-agent reliability beyond telemetry and provenance; developer-owned runtime control integrated with the recorder; incident-management semantics for agents; multi-hour runs.

**Unverified:** Raindrop Series A amount and lead; Braintrust B; Portkey price; Helicone status; Quotient raise; AgentOps pricing; category totals; Sentrial MRR; status of Keywords AI, Lunary, Langtrace, Evidently, Operant, RuntimeAI.
