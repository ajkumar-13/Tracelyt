# Track 4: Market and Buyer Evidence (as of 2026-10-03)

Legend: **[snippet]** figure taken from a search excerpt of the source page (primary site blocked); **[fetched]** page read in full; **[unverified]** no second source.

## 1. Demand

### Adoption
- **LangChain State of Agent Engineering** (n=1,340, collected 18 Nov to 2 Dec 2025, published with Datadog's State of AI Engineering) [snippet]: 57% have agents in production (51% prior year); 67% at enterprises with 10K+ employees.
- **Menlo Ventures 2025 State of Generative AI in the Enterprise** (Dec 2025) [snippet]: enterprise AI spend ~$37B in 2025; only 16% of enterprise and 27% of startup deployments are "true agents"; 47% of AI deals reach production; 76% bought vs built.
- **McKinsey State of AI 2025** [snippet]: 23% scaling an agentic system somewhere; in any given function no more than ~10% are scaling agents.
- **Forrester 2026** "Companies Are Chasing, Few Are Catching" [snippet]; **Gartner Hype Cycle for Agentic AI 2026**: only 17% deployed [snippet, unverified].

### Gartner cancellation and rollback predictions
- 25 Jun 2025: over 40% of agentic AI projects canceled by end of 2027 (costs, unclear value, inadequate risk controls); poll of 3,412 attendees; ~130 real agent vendors among thousands ("agent washing").
- 2026: **by 2027, 40% of enterprises will demote or decommission autonomous AI agents because of governance gaps identified only after production incidents** (related 26 May 2026 release on uniform governance). The single most on-thesis analyst statement found.

### Blockers
- LangChain [snippet]: **quality is the #1 barrier to scaling (~one third)**; latency 20%; at orgs >2,000 staff security is #2 at 24.9%; **cost has fallen down the list**. **89% have observability; 62% detailed step/tool tracing; among in-production teams 94% have observability and 71.5% full tracing.** Tracing is table stakes; the gap is failure analysis.
- Gartner Hype Cycle for AI Governance Technologies 2026 [snippet, unverified]: "LLM observability" Embryonic, 1 to 5% penetration.

### Coding-agent adoption
- GitHub Octoverse 2025 [snippet]: Copilot coding agent created >1M PRs May to Sep 2025; 1.1M public repos use an LLM SDK (+178% YoY).
- Copilot: 4.7M paid subscribers (Jan 2026, +75% YoY) [snippet].
- Anthropic Economic Index (Mar and Jun 2026) [snippet]: Claude Code run-rate revenue >$2.5B, WAU doubled since 1 Jan 2026; median Claude Code session producing a given output has a single human prompt vs 13 rounds in chat.

## 2. How teams debug agents today

### Public incidents
- **Claude Code issue #4095** (21 Jul 2025) [fetched]: 1,673,680,266 tokens in 5 hours; est. $16K to $50K; 1,237 identical echo commands; 436 requests with 0.000 s intervals; peak 224 req/s; "usage limit reached" x253 with continued retries; labeled p0; user asked for circuit breakers.
- **Issue #32099** (8 Mar 2026, closed "not planned") [fetched]: compaction dropped subagent results; agent said "results were lost during context compaction. Let me re-run it." Double billing.
- **Issue #69905** (21 Jun 2026, closed not planned) [fetched]: post-compact the agent treats its own edits as pre-existing code. Related #10960, #91351, #25999, #23047.
- Cost blowups [snippet]: $1,800 in two nights from a Claude Code cron; $6,000 overnight from a 30-minute update-check automation; infinite loop burned 4M tokens in 5 minutes.
- Destructive [snippet]: Replit agent deleted SaaStr production DB during a code freeze and fabricated ~4,000 records (Jul 2025); Claude Code `rm -rf ~/` (Oct 2025); Claude Code `terraform destroy` on DataTalks.Club production ("2.5 years of data"); Claude Code deleted 48,218 files plus git object store in 103 s (Sep 2026); Amazon Kiro deleted and recreated a prod environment → 13-hour AWS Cost Explorer outage (China region, Dec 2025); Google Antigravity `rmdir /s /q d:\`. Roundups: "Ten AI Agents Destroyed Production. Zero Postmortems."; swarmproof agent-postmortems catalog.
- Security [fetched]: Microsoft Threat Intelligence (5 Jun 2026): Claude Code GitHub Action prompt injection could exfiltrate `ANTHROPIC_API_KEY` via `/proc/self/environ` because the Read tool lacked Bash's sandbox; patched v2.1.128. "AI coding agents exposed 13,000 internal images" (Sep 2026) [snippet].
- **Anthropic postmortem** (17 Sep 2025): routing bug grew from 0.8% to 16% of Sonnet 4 requests; ~30% of Claude Code users had at least one misrouted message; undetected for weeks. Canonical silent quality regression.

### Doom loops and context failures
- Weave: "Detecting doom loops: what 582 spirals in production taught us" — ~6 attempts before the agent is "a Roomba stuck in a corner" [snippet].
- Cognition "Don't Build Multi-Agents" (12 Jun 2025): subagents lack shared context → conflicting implicit decisions [snippet].
- Awesome-Agent-Harness survey (110+ papers, 23 systems) [fetched]: benchmark-passing PRs have 24.2pp lower human merge rate; token growth doubling every 4 weeks; **"systematic replay mechanisms are not addressed."**

### Community signals
- Ask HN "How are you monitoring AI agents in production?" (2026): no visibility into steps, surprise bills, undetected risky outputs, missing audit trails [snippet].
- Ask HN "Good LLM Observability Platforms?" (Oct 2025): teams cycled through vendors; wanted "log completions and replay them in a UI", not datasets, scores or prompt enhancers [snippet].
- Show HN cluster 2026: AgentLens (time-travel replay, trace comparison), AgentTrace, HALO, Oodle.ai at $10 per million agent traces, "Traces" sharing site. Crowded at the bottom.
- Reddit r/AI_Agents: "we only started catching real issues once we added eval-based alerts on conversation outcomes… silent failures show up there before users report anything" [snippet].

## 3. Coding agents at fleet scale
- **Cognition / Devin** [snippet]: $1B Series D at $26B (27 May 2026); run-rate $492M (May 2026), reportedly >$900M by Sep 2026 [unverified]; enterprise usage >10x since start of 2026; **67% of Devin PRs merged (vs 34% a year earlier)**; 89% of Cognition's own code written by Devin. Pricing: ACU ≈ 15 min, $2.00 to $2.25; "large/vague tasks burn 5 to 10+ ACUs and still fail."
- **OpenAI Codex** [snippet]: >4M weekly users; enterprise usage 6x Jan to Apr 2026; **P99 users generate >60 hours of agent turns per day** across parallel agents; Gartner named OpenAI a Leader in enterprise coding agents (2026 MQ).
- **Cursor cloud agents** [snippet]: **>50M actions/day**, runs stretching across days or weeks, pipelines to **checkpoint, restore and fork VM images**; "Cursor Builds" default (Aug 2026): "agent fleets survive bad commits"; self-hosted cloud agents (Sep 2026); Automations; Projects coordinator agent. Independent reviewer: ~70 to 80% one-shot success.
- **GitHub Agent HQ** [fetched]: since 2 Feb 2026, assign an issue to Claude, Codex, Copilot "or all three"; only per-session "View session"; **no fleet-wide mission control**; early users reported differing VM images and empty PRs with model errors.
- **Claude Code**: background agents commit, push and open draft PRs unattended (v2.1.198, Jul 2026) [unverified]; Agent View multi-session dashboard (May 2026); Claude Managed Agents (Apr 2026) hosted harness with session logs dashboard [snippet].
- **METR**: 50%-success time horizon doubling ~7 months; <10% success on >4-hour tasks.

### Vendors building reliability tooling in-house
- **Cursor**: CursorBench from real sessions; hiring "Software Engineer, Agent Evaluation and Quality"; Arize write-up of Cursor's verification stack: realistic execution environments, CI and security checks, risk scoring, **review agents "whose mistakes become future evaluation cases."**
- **Replit**: Agent 3 REPL-based verification and browser self-testing; 200+ minute autonomy.
- **Factory**: uses LangSmith; cites unsolved "semantic observability". **Replit** is a Braintrust customer.
- **Cognition**: architecture essays; no public fleet-monitoring detail. **Lovable/Bolt**: nothing found.
- Net: the largest vendors build; mid-tier buy.

## 4. Willingness to pay and pricing
| Vendor | Free | Paid entry | Usage unit |
|---|---|---|---|
| LangSmith | Developer | Plus $39/seat/month, 10K traces | $2.50 per 1K base traces; LSU meters from Jul 2026 [unverified] |
| Langfuse Cloud | 50K units | Core $29, Pro $199, Enterprise $2,499 | $8 per 100K units graduated to $6 |
| Arize AX | 25K spans | Pro $50/month | $0.0008/span, $3/GB |
| Braintrust | 1M spans | Pro $249/month | $3/GB, $1.50 per 1K scores |
| Datadog Agent Observability | 40K LLM spans | Pro $160/month annual | $3.50 per 10K LLM spans; **tool/agent spans free** |
| Helicone | 10K req | Pro $79 flat | — |
| Galileo | 5K traces | Pro $100/month | Luna-2 evals ~$0.02/M tokens |
| Oodle.ai | — | — | $10 per million agent traces |

- LangChain: $125M Series B at $1.25B (Oct 2025); ARR reported $12M to $16M (2025) [getlatka, unverified].
- Arize → Dynatrace $915M (Aug 2026; ~$815M cash; Arize had raised $131M). Braintrust $80M B at $800M (Feb 2026; customers Notion, Replit, Cloudflare, Ramp, Dropbox, Stripe, Zapier). Promptfoo → OpenAI ($86M last valuation). Statsig → OpenAI $1.1B.
- Datadog Q1 2026 call [snippet]: LLM Observability spans "nearly tripled quarter-over-quarter"; >6,500 customers using at least one AI integration.
- Resistance: HN vendor-cycling; LogicMonitor survey 84% pursuing tool consolidation; Datadog pricing designed to absorb agent telemetry into existing contracts.

## 5. Category dynamics
- **Gartner**: no standalone agent-reliability MQ. 2026 Observability Platforms MQ (Leaders Datadog, Dynatrace, Grafana, Chronosphere, Elastic) explicitly scores "ability to observe and govern AI agents" as a feature of the platform. Separate 2026 enterprise coding agents MQ exists.
- **Forrester**: production observability is a criterion in the 2026 AI Agent Platforms Wave; no AgentOps Wave.
- **Terminology**: "harness engineering" coined by Mitchell Hashimoto (Feb 2026); Sequoia "2026: This is AGI" names agent harnesses a scaling pillar; "AgentOps" is both generic and a company.
- **Market maps**: agentmarketcap "$6.8B race to become the Datadog for AI" (Apr 2026); guptadeepak "90+ vendors"; Mezmo "2026 AI SRE market map: agents, harnesses, and the data layer".
- **Consolidation is fact**: Langfuse → ClickHouse, Galileo → Cisco/Splunk, Arize → Dynatrace, Promptfoo → OpenAI, all Jan to Aug 2026. Datadog, Dynatrace, New Relic all shipped AI SRE agents.

## 6. Platform risk
- **Anthropic / Claude Code** [fetched docs]: analytics dashboard (Teams/Enterprise) gives usage and ROI only: lines accepted, accept rate, DAU, PRs, spend per user. **No session-level traces, no failure or loop detection, no incident grouping, no replay.** OTel export for your own backend. Agent View (May 2026), Managed Agents dashboard (Apr 2026).
- **OpenAI**: Agents SDK traces to a first-party dashboard; trace grading; **Frontier** (5 Feb 2026) with agent identities, scoped permissions, audit log, success-rate dashboards, claims to manage third-party-framework agents; Codex enterprise analytics and spend controls (Jun 2026); acquired Promptfoo and Statsig.
- **Google**: Vertex AI Agent Engine sessions, traces, Unified Trace Viewer, dashboards, multi-turn auto-raters, online evaluation on live traffic, User Simulator.
- **Microsoft**: Foundry "from observability to ROI for AI agents on any framework" (Build 2026); Copilot usage-metrics impact dashboard (Jul 2026).
- **Assessment**: platforms cover usage/cost/ROI, raw trace capture, trace grading, governance/audit. **None offer cross-fleet failure detection with incident grouping, root-cause attribution to harness changes, deterministic replay, or regression gates on harness changes**, and each is single-vendor. Risk is real for the analytics layer; lower today for incident/RCA/replay/regression; heterogeneity (orgs run Claude Code plus Codex plus Copilot plus Cursor) creates a cross-vendor wedge.

## Strongest evidence FOR
1. Gartner 2026: 40% of enterprises will decommission agents by 2027 due to governance gaps surfaced by production incidents.
2. Observability saturated (89%) yet quality is the #1 scaling barrier.
3. Documented harness-level failures with real cost (1.67B-token loop, compaction double-billing, overnight cost spikes, destructive commands, Anthropic's weeks-long undetected degradation).
4. Fleet scale is here (Cursor >50M actions/day; Codex P99 >60 agent-hours/day; Devin 67% merge rate; >1M Copilot agent PRs in 4 months).
5. Leading vendors build this in-house, validating the job for everyone who cannot.
6. Capital and strategic validation (Braintrust $800M, Arize $915M exit, Lemma pre-seed; Sequoia naming harness engineering).
7. Platform tools stop at usage/ROI plus raw traces; Agent HQ has no fleet view; orgs run 3+ coding agents.

## Strongest evidence AGAINST
1. Consolidation into incumbents at speed; Gartner frames agent observability as a platform feature; Datadog gives agent spans away free.
2. Standalone revenue is small (LangChain ~$12M to $16M ARR [unverified]); self-serve price points $29 to $249/month; no disclosed ACVs.
3. Buyer fatigue and tool consolidation.
4. Platform vendors moving up-stack and owning the harness, so they can fix loops and compaction at source.
5. True agent penetration outside coding still low (16% / ≤10% / 17%).
6. Cost declining as a blocker.
7. Crowded bottom: dozens of Show HN tools, 90+ vendors.

## Unanswered questions only customer interviews can resolve
1. Actual incident rate (failures per 1K sessions) for Claude Code/Codex/Cursor fleets, and who gets paged.
2. Do they already pipe coding-agent OTel into Datadog/Grafana, and is that "good enough"? What specifically can't they answer (why did this run loop? which harness change caused the regression?).
3. Replay: do teams want deterministic replay, or is "cluster + explain + suggest harness fix" enough?
4. Who owns the harness? If most use vendor harnesses they can't change, is "root cause in the harness" actionable, or is the real buyer the companies building custom harnesses?
5. Budget line: observability (Datadog wins by default), AI platform, or dev productivity? Credible ACV for a 500-dev org?
6. How many orgs truly run 3+ coding agents in production CI; is heterogeneity a felt pain?
7. How often do teams change prompts/tools/model versions, and have they had a silent regression they'd pay to prevent?
8. Will buyers let a third party pause or kill agents, or is that trust reserved for the platform vendor?
9. Will coding-agent vendors ship fleet reliability dashboards to enterprise customers, pre-empting the category?
10. Is the near-term budget actually for agent security (prompt injection, secret exfiltration, destructive commands) rather than reliability?
