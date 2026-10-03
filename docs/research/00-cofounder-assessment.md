# Cofounder Assessment: Harness Reliability Control Plane (HRCP)

**Date:** 3 October 2026
**Inputs:** HRCP-00, HRCP-01, HRCP-02 (in `docs/hrcp/`), plus ~170 web searches and ~100 page fetches across four research tracks (incumbents, emerging startups, standards and instrumentation feasibility, market and buyer evidence). Detailed track reports are in `docs/research/01` through `04`.
**Confidence legend:** facts come from vendor pages, GitHub, SEC filings, or press. Where a figure rests on a single aggregator or a search snippet it is marked *[single-source]*. Many primary sites were blocked by the sandbox proxy, so several figures are from search excerpts of the source page.

---

## 1. Verdict in one paragraph

The problem is real, large, and getting worse, and the three documents diagnose it more precisely than most funded competitors do. But the plan as written is a five-year platform roadmap with zero customer contact, and in the twelve months since the thesis was presumably formed the market moved hard: failure clustering is now shipped by seven vendors, two of them (LangSmith Engine, Arize Signal) already do "issue → root cause → PR", four of the named competitors were acquired by Datadog-class incumbents, and at least four funded startups (Raindrop, Laminar, Judgment Labs, Entire) sit directly on the wedge. Of the ten differentiators in HRCP-00 §50, I count three that are still genuinely open and defensible: **(a) deterministic replay and branching of recorded production agent runs, (b) a computed success-vs-failure first-divergence primitive, and (c) a cross-harness event model for context, memory, permissions and verification**. Everything else is commodity or soon will be. My recommendation is to proceed, but to collapse the plan to one 90-day wedge built around (a)+(b) for coding-agent fleets, drop the "control plane" framing from the company name, rename the project, and talk to twenty buyers before writing another spec.

---

## 2. What the documents get right (keep these)

These are better than most seed-stage thinking and are now backed by independent evidence:

1. **"Tracing is substrate, not product."** LangChain's State of Agent Engineering (n=1,340, Dec 2025) finds 89% of teams already have observability and 71.5% of in-production teams have full step-level tracing, yet *quality* is the #1 barrier to scaling. Collection is solved; failure analysis is not. *[snippet]*
2. **Harness, not model, is where failures originate.** This is now a research consensus: "Model or Harness?" (arXiv 2607.28802) localizes 41 failure modes to component edges; Jarmak's monograph (arXiv 2608.13867) catalogs 206 reliability practices for coding agents and concludes "many apparent model failures originate elsewhere in the system"; deepset (May 2026) shows harness-only changes move agents 20+ leaderboard positions. Sequoia named agent harnesses a scaling pillar; Hashimoto coined "harness engineering" in Feb 2026.
3. **Context compaction as a first-class failure surface.** Your flagship example in HRCP-00 §14 ("pin `account_region` during compaction") is literally the published remedy: "Governance Decay" (arXiv 2606.22528) shows compaction raises constraint violations from 0% to 30% (up to 59%) across 7 models and 1,323 episodes, and fixes it with *Constraint Pinning*; "Lost in Compaction" (arXiv 2608.11242) shows compactors retain only 17% of session constraints. Claude Code issue #32099 (Mar 2026) is a production instance: compaction dropped subagent results, the agent re-ran them, the user was double-billed. Anthropic closed it "not planned".
4. **Incident-first, not trace-first.** Gartner (May 2026) now predicts 40% of enterprises will demote or decommission autonomous agents by 2027 because of governance gaps "identified only after production incidents". Incidents, not model quality, are the kill mechanism.
5. **Immutable raw evidence vs versioned derived interpretations; observed vs statistical vs causal.** No competitor states this discipline publicly. It is a real differentiator in *trust*, which matters when you sell to the people who get blamed when an agent deletes a database.
6. **No gateway, no span pricing, telemetry is untrusted input, DECIDED/PROPOSED/OPEN, kill criteria.** All correct. Datadog now gives tool and agent spans away free and bills only LLM spans, which validates the "span pricing punishes rich instrumentation" argument.
7. **Coding agents as wedge.** Fleet scale arrived in 2026: Cursor cloud agents >50M actions/day with runs spanning days; Codex P99 users >60 agent-hours/day; Devin merge rate 67% (so roughly a third of fleet output fails); Claude Code run-rate >$2.5B with median sessions driven by a single human prompt. METR: <10% success on >4-hour tasks.

---

## 3. What the documents get wrong or leave dangerous (fix these)

### 3.1 Ratio problem: 14,000 words, zero customers
The three docs contain no named prospect, no interview quote, no field number. HRCP-02 §71 warns against "architecture astronautics" and then specifies 7 layers, 10 research streams, 8 specialized models, 9 phase gates and 8 further spec documents. The docs are themselves the thing they warn against. The single most valuable artifact you could add is a page of verbatim quotes from ten people who run agent fleets.

### 3.2 The harness-access paradox
The richest events in the Harness Event Model (context.compact, permission.denied, verify.failed, agent.spawned) exist only if the **harness emits them**. The highest-volume coding harnesses (Claude Code, Codex, Cursor, Devin) are closed; you capture what they expose. Open frameworks (LangGraph, CrewAI, Agents SDK) ship their own observability and are courted by every incumbent. So the customers who can actually emit HEM are **teams that build their own harness**. That is a real, growing and underserved segment (Agent SDK, OpenHands, LangGraph-based internal agents, "TrueForge"-style open harnesses), but it is narrower than the docs imply and must be stated explicitly in the ICP.

Partial mitigation: the standards track (section 5 below) finds Claude Code exposes hooks and OTel export that cover more than you'd expect, and W&B's `weave-claude-code` plugin already captures permission requests and compaction events from Claude Code. So Claude Code specifically is instrumentable deeper than Codex or Cursor.

### 3.3 First divergence needs homogeneous task populations
Trajectory alignment between successful and failed cohorts only works when the cohort shares a task class. It fails on heterogeneous one-off work. The benchmarks confirm how hard this is: on LongRCA Bench (1,140 real failed trajectories, median 145 steps), the best baseline reaches **13.2% exact root-step accuracy**, and the best method 24.1%. "Root-Cause Attribution Is a Search Problem" (arXiv 2609.13463) shows LLM diagnostic accuracy collapses as traces grow. This is good news (it is hard, so it is defensible) and a warning (do not promise it on day one). The ICP narrows again to **fleets doing repeated task classes**: coding agents on ticket queues, support agents, back-office agents. Say so.

### 3.4 Replay is demoted from differentiator to mechanism
For a coding agent with a repo SHA and a container image, "replay" is mostly "re-run with recorded model and tool outputs until divergence, then go live". The valuable product is **the regression suite built from last week's production failures**, run against a proposed harness change, as a CI gate. Deterministic fixture replay is an optimization that makes that suite cheaper and more stable. Cursor already built checkpoint/restore/fork VM pipelines internally and runs review agents "whose mistakes become future evaluation cases" (Arize write-up). That is the job to be done. Lead with the regression gate; let replay be plumbing.

### 3.5 Open-core chicken-and-egg
The open layer (OTel SDK, semantic conventions) is where incumbents are strongest and is already commoditized (`gen_ai.*` conventions are ingested by Datadog, Dynatrace, Grafana, Honeycomb, Weave, Langfuse, Laminar, OpenLIT). The proprietary layer (incident intelligence, specialized models) needs data volume you will not have for 18 months. You need a **paid wedge that works at N=1 customer** with their own data. The regression gate is that wedge; cross-customer intelligence is a later moat.

### 3.6 Economics are unsolved and the architecture should assume hybrid
Long-running agents produce enormous payloads. Storing raw evidence immutably for replay conflicts with "SaaS stays economic". HRCP-01 §73 treats customer-side payload retention as an option; it should be the **default architecture**: structural telemetry to you, payloads and snapshots stay in the customer's object store, replay runs in the customer's sandbox. This also neutralizes the "another observability vendor" objection and the data-residency objection in one move.

### 3.7 "Control plane" is a security buyer's word
Runtime control, kill switches, and agent firewalls are now a CISO-owned category with $100M+ rounds (Zenity $125M C, Noma $100M B, Straiker $64M A, AIR $50M seed) and $250M to $300M exits (Lakera to Check Point, Prompt Security to SentinelOne). Okta announced an agent kill switch at Oktane 2026. You are not going to out-sell them to security teams, and the developer buyer does not want a "control plane" from a seed startup. Keep developer-owned runtime control (pause, budget circuit breaker, deny tool) as a Phase 8 capability, but take it out of the company's category name.

### 3.8 Team and name
The repo is empty with one author; HRCP-02 §69 lists six specialties. Plan for 1 to 2 people for six months. Also, "Tracelyt" collides with Evidently AI's OSS `tracely` (an OpenTelemetry LLM tracing library in this exact category), plus tracely.io (crypto compliance) and a Tracely family-tracking app. Rename before anything is public.

---

## 4. Competitive landscape, October 2026

### 4.1 Consolidation happened
| Target | Acquirer | When | Notes |
|---|---|---|---|
| Arize AI | Dynatrace | agreed Aug 2026, closed 1 Oct 2026 | $915M *[snippet]* |
| Galileo | Cisco (Splunk) | closed 22 May 2026 | renamed "Splunk Agent Observability" |
| Langfuse | ClickHouse | 16 Jan 2026 | stays OSS; terms undisclosed |
| Portkey | Palo Alto Networks | closed 29 May 2026 | ~$117M to $140M per 10-K |
| W&B (Weave) | CoreWeave | 2025 | $1.7B; now "Forge / Agent Lens" |
| Promptfoo | OpenAI | 9 Mar 2026 | into "OpenAI Frontier" |
| Quotient AI | Databricks | 11 Mar 2026 | failure clustering → eval datasets |
| Helicone | Mintlify | Mar 2026 | maintenance mode *[single-source]* |
| Humanloop, Context.ai, Atla Insights | acqui-hired or shut | 2025 to Feb 2026 | category-is-hard signals |

Pattern: pure observability and eval independents exit at modest multiples into data platforms, APM vendors and model labs. Security-framed agent-control companies command the big rounds. Gartner's 2026 Observability MQ scores "ability to observe and govern AI agents" as a *feature of the observability platform*. There is no "agent reliability" Magic Quadrant.

### 4.2 Capabilities now commodity (shipped by five or more vendors)
- Single-run agent graph or decision-path view (Datadog, Langfuse, Phoenix, Galileo, Weave, Honeycomb, Dynatrace, Grafana, LangSmith).
- OTel `gen_ai.*` ingestion including `invoke_agent` and `execute_tool` spans.
- Coding-agent session tracing (LangSmith Trajectories, Weave Claude Code plugin, OpenLIT, Dynatrace, Laminar debugger, Langfuse coding-agent evaluator).
- Production trace → dataset → evaluator → CI gate.
- **Failure or topic clustering of production traces**: LangSmith Insights, Braintrust Topics, Arize Signal, Galileo Signals, Laminar Signals, HoneyHive, Datadog, Raindrop, Judgment Labs. 2026 is the year this commoditized.
- Chat or MCP assistants over the platform (Polly, Loop, Alyx, PXI, Seer).
- Gateway-level guardrails and budgets.

### 4.3 Who is closest to each HRCP differentiator
| HRCP concept | Closest shipped | Gap that remains |
|---|---|---|
| Incident-first UI | **LangSmith Engine** (beta May 2026): watches prod traces, clusters into named issues, root-causes against connected source code, opens a PR with a fix, proposes an evaluator, adds failing traces to dataset. **Arize Signal**: scheduled scan, ranked issues, RCA hypothesis, recommended change, PRs on Enterprise. | Both are trace-cluster-first, not incident-lifecycle. Neither links detection to runtime mitigation. Neither does component-level attribution against a harness model. |
| First divergence | Arize Signal docs mention "common trajectory, affected cohort"; Galileo **Aggregate Agent Graph** shows most-common paths and outliers across sessions; Honeycomb BubbleUp is a generic cohort diff. | **No vendor computes or displays an explicit earliest-divergence step between success and failure cohorts.** Academic only (LongRCA, MegaRCA, "canonical path deviation"). |
| Harness Event Model | **W&B weave-claude-code** captures subagents as `invoke_agent` spans, permission requests as `forge.permission_request` events, and compaction events. Phoenix added a DECISION span kind (1 Oct 2026). **OpenLIT rebranded as "Agent Harness Engineering" on 1 Oct 2026** (branding plus glossary, no event schema). | Only one plugin, one harness, no PII scrubbing. Nobody normalizes memory ops, verification steps, hook runs or permission decisions across Claude Code, Codex, LangGraph and Agents SDK. OpenLIT now owns the *term*. |
| Execution graph | Commodity for single runs. Cross-run aggregate: Galileo/Splunk only. | Cross-run causal graph with provenance-typed edges: nobody. |
| Branch-aware replay | AgentOps "time-travel" (visual, depth unverified, no 2026 funding); LangGraph checkpoint rewind (framework-bound); **Laminar** re-runs from any step (not deterministic). Durable-execution runtimes (Temporal $550M Series E at $12.55B, Restate, Inngest, DBOS) get replay as a byproduct. | **None of the 17 observability platforms ship fixture or deterministic replay with branching from a recorded production run.** Largest open gap. |
| Regression against production failures | Judgment Labs ($32M, Lightspeed): "validate fixes against real production cases". Raindrop ($50M total, CRV Series A Sept 2026 *[single-source]*): adding "simulate changes before they ship". Cursor does it internally. | Nobody ships "re-run last week's 500 failures against the new harness" as a CI gate for coding-agent harness changes. |
| Runtime control | Galileo Agent Control (deny/steer/warn/log/allow on tool I/O), Portkey/PANW MCP Gateway, LangSmith Fleet Agent Inbox, Okta kill switch, RuntimeAI. | Developer-owned control integrated with the recorder, driven by detector evidence: nobody. But see 3.7. |

### 4.4 Direct threats, ranked
1. **Raindrop** ("Sentry for AI agents"): $15M seed led by Lightspeed, Series A led by CRV Sept 2026, ~$50M total *[single-source]*. Background agents triage production traces into issues; now moving into pre-ship simulation. Best-funded pure-play on your detection and clustering pillars.
2. **LangSmith Engine**: already does issue → RCA against code → PR. Distribution via LangGraph. Does not do replay or harness-component attribution.
3. **Laminar** (YC S24, $3M seed Mar 2026, Apache-2.0, Rust): "record, re-run from any step, Signals clustering, long-running agents." Nearly identical wedge, tiny team. Watch or partner.
4. **Judgment Labs** ($32M, Lightspeed May 2026): Judgeval OSS, trajectory evals, validate fixes against production cases.
5. **Entire** (Thomas Dohmke, $60M seed at ~$300M, Felicis, Feb 2026): OSS "Checkpoints" attaches agent sessions to git commits. Owns "coding-agent flight recorder" mindshare and capital, but is provenance/governance, not reliability. Could add replay.
6. **W&B Weave / CoreWeave**: the only one modeling permissions and compaction from Claude Code today.
7. **Sentrial, Moda, ASHR (YC W26)**: "Datadog for agent reliability" clones; expect a dozen more.
8. **Platform vendors**: Claude Code analytics is usage/ROI only (no traces, no failures, no replay); OpenAI Frontier (Feb 2026) has agent identities, audit, success dashboards plus Promptfoo and Statsig; Vertex Agent Engine has traces, online eval, user simulator. None do cross-fleet failure detection, RCA to harness changes, replay, or regression gates. But each owns its harness and can fix loops and compaction at source, shrinking the externally visible failure surface over time.

---

## 5. Standards and instrumentation feasibility

**Standards: the vocabulary exists, the control events do not.**
- Every OpenTelemetry `gen_ai.*` span, attribute, metric and event is still **Development** status (experimental), now in its own `semantic-conventions-genai` repo. `invoke_agent`, `create_agent`, `execute_tool`, `gen_ai.tool.call.id/arguments/result`, `gen_ai.conversation.id`, structured opt-in input/output messages, and memory operation names (`create_memory`, `search_memory`, etc.) are defined. ADK, AutoGen, PydanticAI, Vercel AI SDK and the Linux Foundation's AGNTCY Observe SDK already emit them.
- **No convention exists, even in draft, for permission decisions, context compaction, context provenance, verification steps, checkpoint/pause/resume, or stop reasons beyond `finish_reasons`.** The two relevant proposals (issue #159 pause/resume/checkpoint events, May 2026; issue #181 privacy-first context-input evidence motivated by coding agents, May 2026) have no maintainer uptake. This is exactly the hole HEM fills, and the right move is to draft it as a `gen_ai.*` extension and upstream it, not to own a private schema.
- OpenInference has 11 span kinds (now including DECISION) and 40+ instrumentors including the Claude Agent SDK and MCP, but is a parallel vocabulary with no `gen_ai.*` mapping.
- MCP's 2026-07-28 revision adopted W3C `traceparent` in `_meta` (SEP-414) and rejected span transport inside the protocol. You get correlation, not recording.
- Nothing in OTel or OpenInference defines a **replayable record**. OTLP export is sampled, truncated at 60 KB, and flush-bounded. A recorder needs a loss-free side channel (raw bodies to disk, filesystem snapshots) that no standard specifies.

**Coding-agent instrumentability, ranked by depth a third party can reach today**

| Agent | Channels | Depth |
|---|---|---|
| Claude Code / Agent SDK | Native OTel (metrics, 20+ log events including `tool_decision`, `permission_mode_changed`, hook execution; beta spans with permission-wait child spans and subagent nesting; raw API bodies to disk). **33 hooks** including PreCompact/PostCompact, SubagentStart/Stop, PermissionRequest/PermissionDenied, Elicitation, InstructionsLoaded, StopFailure. SDK stream has `compact_boundary` messages. | **Deepest.** Near-complete model/tool/permission/subagent/compaction/stop coverage without forking the agent. Missing: compaction summary content via OTel, verification semantics. |
| OpenAI Codex CLI | Native OTel (events, traces, metrics); **12 hooks with the same stdin-JSON contract as Claude Code** (PreToolUse, PermissionRequest, PreCompact, PostCompact, SubagentStart/Stop, Stop, Interrupt). | **Deep** interactively; `codex exec` has no metrics and `codex mcp-server` has no OTel at all (issue #12913). |
| Gemini CLI | Native OTel aligned to `gen_ai.*`; 11 hooks including BeforeModel/AfterModel (can intercept LLM request/response) and advisory PreCompress. | **Deep for model and tool**, no subagent hooks. |
| Cursor | `hooks.json` only (shell, MCP, file read/edit, prompt, stop, agent thought; newer builds add tool/subagent/compact hooks). No OTel. | **Medium.** Tool, file and permission audit; no model-call visibility. |
| OpenHands SDK | Native OTel traces with tool I/O; event store supports resume/replay. | **Deep**, but it is a framework you embed. |
| Cline | Opt-in OTel logs and metrics, hashed content, no traces. | **Medium-shallow.** |
| Devin | REST API: session events, Session Insights. | **Shallow**, polling a closed system. |
| LangGraph, CrewAI, Agents SDK, PydanticAI, AutoGen, ADK, Mastra | SDK-level spans. | Routine model/tool/agent spans; **none expose compaction, permissions or checkpoint transitions as telemetry.** LangGraph "time travel" re-executes LLM calls and is explicitly non-deterministic. |

**Practical implication.** Claude Code, Codex and Gemini CLI have converged on a de facto stdin-JSON hook contract. One adapter plus an OTLP receiver covers three harnesses with tool calls, permission decisions, subagent spawns, compaction boundaries and stop reasons, with no agent modification. That materially softens the harness-access paradox in 3.2 for Claude Code specifically. Prior art to study and possibly build on: `o11y-dev/opentelemetry-hooks` (~40 stars, converts hook payloads from seven coding agents into OTel spans).

**Replay feasibility.** Fork-at-step-k replay, which the counterfactual-attribution papers assume (Causal Agent Replay, DoVer, "The Replay Gap"), requires *both* a frozen model-response cassette *and* a per-step environment snapshot. VCR-style tools (pytest-llm-vcr, agent-vcr) work at test time only. Durable-execution engines (Temporal, Restate, Inngest) journal steps only if the agent is authored inside them. Sandboxes (E2B pause/resume, Modal, Daytona) snapshot the environment but not harness state. Claude Code checkpoints miss Bash side effects and subagent edits. No product or standard offers the pairing. Coding agents remain the right first domain, but expect Level 2 to 3 fidelity (HRCP-01 §57) for a long time, not Level 4 to 5.

**Reusable taxonomies and benchmarks.** MAST (14 failure modes, 1,642 traces, NeurIPS 2025), TRAIL (Patronus, 148 traces, best model ~11% joint accuracy), AgentErrorTaxonomy/AgentDebug (17 error types, finds earliest critical error, failures cluster at steps 6 to 15), Who&When ("decisive step" formalism), "Model or Harness?" (41 modes on component edges), LongRCA Bench (1,140 real trajectories, public leaderboard). "Failure as a Process" (arXiv 2607.09510) finds 71% of *successful* CLI coding-agent trajectories hit at least one error; recovery, not error occurrence, separates success from failure. That is an argument for detectors on recovery behaviour (HRCP-01 §33) over detectors on error counts.

---

## 6. Market evidence

**For the thesis**
- Gartner (Jun 2025): >40% of agentic AI projects canceled by 2027. Gartner (May 2026): 40% of enterprises will demote or decommission autonomous agents by 2027 due to governance gaps surfaced by production incidents.
- Documented harness-level failures with real cost: Claude Code issue #4095 (Jul 2025) burned 1.67 billion tokens in 5 hours, ~$16K to $50K, 1,237 identical commands, retries continued past the usage-limit error; $1,800 two-night cron; $6,000 overnight automation; Weave's "582 doom-loop spirals in production"; Replit agent deleted a production DB; Claude Code `terraform destroy` on 2.5 years of data; Amazon Kiro deleted a prod environment causing a 13-hour AWS Cost Explorer outage; Claude Code deleted 48,218 files in 103 seconds (Sep 2026). A catalogue titled "Ten AI agents destroyed production, zero postmortems" exists.
- Anthropic's own Sept 2025 postmortem: a routing bug hit ~30% of Claude Code users and went undetected for weeks. Silent quality regression is real even for the harness vendor.
- Vendors build this in-house: Cursor (CursorBench, checkpoint/fork VMs, review agents whose mistakes become evals, hiring "Agent Evaluation & Quality"), Replit (Agent 3 self-testing), Cognition (89% of own code by Devin). Factory buys LangSmith. The job exists; only the biggest can build it.
- Heterogeneity: GitHub Agent HQ (Feb 2026) lets you assign an issue to Claude, Codex or Copilot "or all three" with per-session views only and no fleet view. Orgs running 3+ coding agents need a cross-vendor layer that no platform vendor will build.
- HN practitioners: cycled through LLM-observability vendors; what they wanted was "log completions and replay them", not datasets and scores.

**Against the thesis**
- Consolidation is fact, not forecast (section 4.1). Datadog gives agent and tool spans away free and its LLM-observability span volume nearly tripled QoQ in Q1 2026.
- Standalone revenue is small: LangChain ARR reportedly $12M to $16M *[unverified]* despite category leadership. Self-serve price points are $29 to $249 per month. Enterprise ACVs are undisclosed everywhere; Arize's were reportedly $50K to $100K.
- True agent penetration outside coding is low: Menlo says 16% of enterprise deployments are "true agents"; McKinsey ≤10% per function. The fleet buyer outside coding may be 1 to 2 years away.
- Cost is declining as a blocker (LangChain), which weakens a cost-blowup-led pitch.
- Crowded bottom: dozens of Show HN replay and debugger tools, 90+ vendors on market maps, seven hobby "agent flight recorder" repos on GitHub.
- Security may be where the budget actually is: the headline incidents (secret exfiltration, `rm -rf`, prompt injection in CI) are being sold as security, and that category pays.

---

## 7. What I would do: a 90-day plan that replaces Phases 0 to 3

**Wedge statement (test this wording):**
> When your coding-agent fleet starts failing, we tell you which harness change caused it and let you prove the fix against last week's failures before you ship it.

**Target buyer:** platform or AI-infrastructure lead at a company running ≥500 coding-agent sessions per day across Claude Code, Codex, Cursor or an in-house Agent SDK harness, with a repeated task class (ticket queue, migration, test generation).

**Weeks 1 to 3: twenty conversations, zero code.**
Use the HRCP-02 §49 question list. Add: "How many sessions per day? How many fail? Who finds out? Do you pipe Claude Code OTel into Datadog already? When you changed your system prompt or tool set last, how did you know it did not regress?" Record verbatim. Kill criterion: fewer than 5 of 20 describe an unprompted harness regression they would pay to prevent.

**Weeks 2 to 8: Proofs A to G from HRCP-02 §90, scoped to Claude Code hooks plus one open harness.**
Instrument Claude Code via hooks and OTel export, and one Agent SDK or LangGraph harness. Normalize both to a 20-event HEM v0.1 (not the full 24 domains). Build detectors D1 (doom loop), D4 (no progress), D5 (budget spiral), D6 (verification bypass), D8 (context explosion). Inject faults on a SWE-bench-style task set. Measure whether first divergence is findable at all, using LongRCA-Mini (200 trajectories, public labels) as a sanity benchmark rather than inventing HRCP-09 from scratch.

**Weeks 6 to 12: one design partner, one regression gate.**
Take one partner's real failures, build the fixture bundle (repo SHA, image, recorded model and tool outputs), re-run against a proposed harness change in their sandbox, produce the HRCP-02 §28 report. The deliverable is a GitHub check on a PR that touches harness files. Charge for it.

**Explicitly deferred:** specialized models, runtime control, enterprise policy engine, graph database, ClickHouse benchmarking at billions of events, HRCP-03 through HRCP-10 as full specs. Write one-page ADRs instead.

**Decisions to make now:**
1. Rename (Tracelyt collides).
2. Re-classify "control plane" from DECIDED category name to PROPOSED Phase 8 capability.
3. Make customer-side payload retention and customer-side replay sandboxes the default architecture.
4. Adopt the "Model or Harness?" taxonomy and LongRCA labels as the starting failure taxonomy instead of writing HRCP-05 from scratch.
5. Decide Laminar: compete, partner, or acqui-merge. Same wedge, Apache-2.0, three million dollars, two founders.

---

## 8. Revised kill criteria (adding to HRCP-02 §76)

Kill or pivot if, by day 90:
- fewer than 5 of 20 interviewees describe a harness regression they would pay to prevent;
- Claude Code plus one open harness cannot be normalized to a shared event model with <10% framework-specific exceptions;
- injected-fault first-divergence localization is below 40% top-3 accuracy on your own controlled benchmark (LongRCA's best is 24% exact on real data, so controlled should be far higher or the primitive is not viable);
- no design partner will let replay run in their environment;
- LangSmith Engine or Raindrop ships regression-against-production-failures as a CI gate before you do, *and* a prospect says it is good enough.

---

## 9. Bottom line

You have correctly identified the one layer of this market that is not yet commoditized and that the incumbents are structurally bad at: deterministic reproduction of agent failures and attribution to harness components. You have also written the plan as if you had five years and twenty engineers. Cut it to one wedge, one harness pair, one design partner, ninety days, and let the evidence decide whether the control plane ever gets built.
