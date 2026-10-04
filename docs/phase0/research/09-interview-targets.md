# Customer-discovery target list: reliability infrastructure for production AI agents (as of 2026-10-04)

**How this was built.** WebFetch was blocked by the egress proxy for almost every domain, including langchain.com, medium.com, 8thlight.com and interrupt.langchain.com. The GitHub API was also limited to the user's own repo. So every claim below comes from web-search result snippets of the cited URL, plus GitHub issue search for pain signals.

**Legend**
- **(U)** means unverified: the source is secondary, the affiliation was inferred, or the snippet was ambiguous. Confirm before outreach.
- People's titles are as of the cited source and may be stale.
- Priority: **A** = contact first, **B** = next wave, **C** = monitor.
- I did not make up any names. Where no person was found, the table gives the role title to look for.

---

## Track 1 — Builders (open or custom harness)

| # | Organization | Evidence URL | Harness / framework | Role title to seek | Named person (public) | Pain signal | Pri |
|---|---|---|---|---|---|---|---|
| 1 | Uber | https://lawwu.github.io/transcripts/transcript_Bugs0dVcNI8.html ; https://aaif.io/blog/how-uber-runs-60000-ai-agent-tasks-per-week-with-mcp ; https://background-agents.com/summit/ | LangGraph (Validator, AutoCover) wrapped in Uber abstractions; "Minion" background-agent platform; uReview; Michelangelo agent platform | Developer Platform AI EM; Agent Platform (Michelangelo) lead | Sourabh Shirhatti, Matas Rastenis (Developer Platform, Interrupt talk); Nikhil Ramakrishnan (Minion talk at the Background Agents Summit) | About 60k agent tasks a week. Burned its 2026 AI budget in 4 months, mostly on Claude Code (https://www.forbes.com/sites/janakirammsv/2026/05/17/uber-burns-its-2026-ai-budget-in-four-months-on-claude-code/) | A |
| 2 | Stripe | https://background-agents.com/summit/sessions/alistair-gray/ ; https://blog.bytebytego.com/p/how-stripes-minions-ship-1300-prs | Custom "Minions": a blueprint harness mixing deterministic and agentic nodes on dev boxes. Reportedly started from a fork of Block's goose (U) | Developer Infrastructure / Minions tech lead | Alistair Gray (Minions); Scott MacVicar (Dev Infra, per the Claude Code case study) | 1,300+ unattended PRs a week with nobody watching the runs | A |
| 3 | Spotify | https://engineering.atspotify.com/2026/4/background-coding-agents-dataset-migrations-honk-part-4 | "Honk" on the Claude Agent SDK in Kubernetes pods; plan→code→review pipeline | Fleet Management / Honk platform lead | Max Charas, Marc Bruggmann (authors of the Honk series) | 650+ PRs a month. Directly exposed to upstream harness changes (see the Anthropic postmortem) | A |
| 4 | Ramp | https://builders.ramp.com/post/why-we-built-our-background-agent | "Inspect", built on OpenCode, Modal sandboxes and Cloudflare | Background-agent / DevEx lead | Zach Bruggeman (https://x.com/zachbruggeman/status/2010728444771074493) | Writes 30–40% of merged PRs; Ramp owns the harness | A |
| 5 | Monzo | https://background-agents.com/summit/sessions/suhail-patel/ ; https://www.infoq.com/news/2026/03/shipping-monzo/ | "Agent Chip", an internal harness (code generation, review, incident investigation) | Platform group / AI tooling lead | Suhail Patel (Principal Engineer, leads platform) | About 1,800 tasks a day and roughly 10% of merged PRs, inside a regulated bank | A |
| 6 | Salesforce | https://mastra.ai/customers/salesforce | Mastra: two production harnesses in `@salesforce/sfdx-agent-sdk`, chosen per model at runtime, for 100k developers | Agentforce DX / Vibes harness eng lead (no name found) | — | Swapping harnesses per model at runtime is exactly where a harness-change regression gate applies | A |
| 7 | PagerDuty | https://www.pagerduty.com/eng/inside-pagerdutys-sre-agent-how-we-built-deep-incident-investigation/ | LangGraph (bulk-synchronous-parallel sub-agent hypothesis fan-out) SRE agent | AI agent platform staff engineer | Micah Mayo (Staff SWE), Viktor Vasylkovskyi (Senior SWE) | Long-running, tool-heavy SRE agent with parallel sub-agents | A |
| 8 | Lyft | Interrupt 2026 session "Building Evals That Actually Matter in Production" (https://interrupt.langchain.com/recordings) | LangSmith evals; LLM-as-user simulator | Safety & Customer Care AI eng lead | Nick Ung | Public offline/online gap: 90% success on the simulator, poor in production | A |
| 9 | Coinbase | https://www.coinbase.com/blog/building-enterprise-AI-agents-at-Coinbase | LangGraph + LangSmith multi-agent developer support | Agent platform / developer support EM | Evan Kormos (EM; Interrupt 2026 talk "How Coinbase Scaled AI Support with a Multi-Agent System") | Talked publicly about going from "black box to glass box" observability | A |
| 10 | Clay | Interrupt 2026 recap (https://8thlight.com/insights/production-is-the-new-prototype-notes-from-langchain-interrupt-2026) | Claygent (custom; LangSmith user, U) | AI platform / Claygent eng lead | Jeff Barg | About 350M agent runs a month; 1B+ Claygent runs in total | A |
| 11 | Cisco (CX) | https://x.com/LangChain/status/1926368790062703043 | LangGraph, LangGraph Platform, LangSmith; supervisor architecture | CX AI platform architect | Carlos Pereira (Fellow & Chief Architect) | 60% of 1.8M support cases automated; frames AI "as runtime" | B |
| 12 | LinkedIn | https://www.infoworld.com/article/4054974/how-linkedin-built-an-agentic-ai-platform.html | LangGraph supervisor/sub-agents (Hiring Assistant, SQL Bot, cognitive memory agent) | Agent platform eng lead, Talent Solutions | Prashanthi Padmanabhan (VP Eng, Talent Solutions) | Hierarchical multi-agent system over 1B profiles | B |
| 13 | BlackRock | https://www.zenml.io/llmops-database/agentic-ai-architecture-for-investment-management-platform | LangGraph Aladdin Copilot; plugin registry fed by 50+ teams | Principal AI Engineer, Aladdin Copilot | Pedro Vicente Valdez. Brennan Rosales has since moved to a stealth startup per LinkedIn (U) | 50+ contributing teams make component attribution a real problem | B |
| 14 | J.P. Morgan Private Bank | https://www.zenml.io/llmops-database/multi-agent-investment-research-assistant-with-rag-and-human-in-the-loop | LangGraph supervisor ("Ask D.A.V.I.D.") | Investment research AI lead | David Odomirok, Zheng Xue | Stresses evaluation and human-in-the-loop because of the stakes | B |
| 15 | monday.com | Interrupt 2026 "Building Deep Agent Sidekick"; Code w/ Claude London session | Deep agent (LangGraph deepagents, U) + Claude | AI platform lead | Omri Bruchim | Rearchitected the Sidekick agent as it evolved | B |
| 16 | Rippling | Interrupt 2026 speaker list (https://www.langchain.com/blog/previewing-interrupt-2026-agents-at-enterprise-scale) | LangGraph (U) | Head of AI / agent platform | Ankur Bhatt (Head of AI) | — | B |
| 17 | LATAM Airlines | https://www.youtube.com/watch?v=RnLCl3ilRgo | LangGraph supervisor + 6 specialist agents | AI engineering lead | Nico Venegas, Claudio Urbina | Concierge agent with 4,000 daily users | B |
| 18 | Shopify | https://shopify.engineering/building-production-ready-agentic-systems | Custom agentic loop (Sidekick); LLM judges; GRPO | Sidekick / ML eng lead | Andrew McNamara, Ben Lafferty, Michael Garner | Tool sprawl; built just-in-time instructions to cope | B |
| 19 | Duolingo | https://blog.duolingo.com/agentic-workflows | "CodingAgent" library wrapping both Codex CLI and the Claude Code SDK (switched by one enum); 180+ MCP tools | DevXAI team lead | — | Swapping harnesses between two vendors → needs a regression gate | B |
| 20 | Instacart | https://openai.com/index/codex-now-generally-available/ | "Olive" background-agent platform on the Codex SDK | Olive / developer productivity lead | — | Tech-debt and feature-flag cleanup at scale | B |
| 21 | Genentech | https://background-agents.com/summit/ | Background agents for genomics and cloud infrastructure | Scientific computing / agent platform lead | Xiucheng Quek | Agents operating across science and cloud infrastructure | B |
| 22 | Box | https://openai.com/index/new-tools-for-building-agents/ | OpenAI Agents SDK | AI platform eng lead | (Aaron Levie gave an Interrupt 2026 keynote; for discovery, target the eng lead) | Permission-aware agents | B |
| 23 | AutonomyAI | https://pydantic.dev/case-studies/autonomyai | PydanticAI + Logfire; agents query their own traces | CTO / eng lead | — | Already self-detecting regressions (65 issues surfaced): a buyer who understands the category | B |
| 24 | Range | https://mastra.ai/customers/range | Mastra, 15+ agents in production (regulated financial advice) | Eng lead for the "Rai" agent | — | Regulated domain | C |
| 25 | Supermetrics | https://futureagi.com/blog/what-is-google-adk-2026/ | Google ADK + Vertex Agent Builder | Marketing Intelligence Agent eng lead | — | Agent fixes data-connection errors autonomously | C |

**Also qualifies**
- Klarna: LangGraph assistant for 85M users (https://blog.langchain.com/customers-klarna/); Martin Elwin's link to it is (U).
- Elastic: LangGraph AI Assistant.
- AppFolio: Realm-X on LangGraph (https://www.langchain.com/blog/customers-appfolio).
- Toyota: Kordel France and Ravi Chandu Ummadisetti, "ToyotaGPT".
- PwC: CrewAI Agent OS (https://crewai.com/case-studies/pwc-accelerates-enterprise-scale-genai-adoption-with-crewai).
- DocuSign: CrewAI Flows.
- Mozilla: Claude Agent SDK harness found 500+ Firefox bugs (U, secondary source).
- Asana: AI Teammates on Claude (U).
- Bridgewater ("Pat"), Etsy (gifting assistant), Abridge, Honeywell: all Interrupt 2026 speakers.

---

## Track 2 — Fleets (closed harness: Claude Code, Codex, Cursor, Devin, Copilot, Kiro)

| # | Organization | Evidence URL | Tools at scale | Role title to seek | Named person | Pain signal | Pri |
|---|---|---|---|---|---|---|---|
| 1 | Uber | https://www.forbes.com/sites/janakirammsv/2026/05/17/uber-burns-its-2026-ai-budget-in-four-months-on-claude-code/ | Claude Code (≈25% of commits in Q1 2026), Cursor; 5,000 engineers | Dev Platform / AI tooling governance | see Track 1 | Cost blowout; internal usage leaderboards | A |
| 2 | Stripe | https://claude.com/customers/stripe | Claude Code for 1,370 engineers (zero-config rollout) + Minions | Developer Infrastructure | Scott MacVicar | Fleet plus unattended agents together | A |
| 3 | Cloudflare | https://blog.cloudflare.com/internal-ai-engineering-stack/ | 93% of R&D on AI coding tools; 3,683 users; AI Gateway; 241B tokens in 30 days; AGENTS.md in 3,900 repos | Internal AI engineering stack owner | Rajesh Bhatia, Ayush Thakur, Scott Roe-Meschke | Merge requests up ~60% (5.6k → 8.7k a week) | A |
| 4 | Spotify | https://engineering.atspotify.com/2026/6/code-with-claude-coding-is-no-longer-the-constraint | Claude Code + Honk | DevEx / Backstage lead | Max Charas | — | A |
| 5 | Monzo | https://background-agents.com/summit/sessions/suhail-patel/ | Claude and Cursor under golden paths, sandboxing, MCP governance; conventions encoded as skills | Platform group | Suhail Patel | Regulated controls | A |
| 6 | Faire | https://cursor.com/blog/faire | Cursor Cloud Agents; 2,000+ autonomous runs a week; replaced its in-house "Samurai" | Principal Engineer, agent fleet | Luke Bjerring | Already built and abandoned its own harness, so knows the pain | A |
| 7 | Delivery Hero | https://www.businesswire.com/news/home/20260424082392/en/Delivery-Hero-Unveils-Herogen-Autonomous-AI-Agent-Unlocks-130-Person-Engineering-Output | "Herogen" on Claude; goal of 1 in 5 merged PRs; dedicated Claude tool-stack team | VP Tech Foundations | Rodrigue Schäfer; Julian Yu-Lang Chu (builder) | — | A |
| 8 | Salesforce | https://cursor.com/blog/topic/customers | Cursor (30%+ velocity gain) + the Mastra harness | DX platform | — | — | A |
| 9 | Goldman Sachs | https://www.forbes.com/sites/bernardmarr/2026/08/06/how-goldman-sachs-is-using-agentic-ai-for-software-engineering-at-scale/ | Devin, scaling from hundreds to thousands of agents alongside ~12k developers; Copilot; Claude for ops | CTO org / AI engineering platform | Marco Argenti (CIO) | Fleet-scale autonomous coders | B |
| 10 | Citi | https://www.americanbanker.com/news/citi-is-rolling-out-agentic-ai-to-its-40-000-developers | Devin + Copilot for 40k developers; 1M+ agent code reviews; "Arc" agent platform | Engineering productivity / Arc platform | David Griffiths (CTO) | — | B |
| 11 | Nubank | https://building.nu.com/enhancing-engineering-workflows-with-ai-a-real-world-experience/ | Devin, 6M-LOC ETL migration with a benchmark set | Data platform eng | — | Built its own eval set for the migrations | B |
| 12 | Coinbase | https://cursor.com/blog/topic/customers | Cursor (idea to production 90% faster) | DevEx | Evan Kormos (agents side) | — | B |
| 13 | NVIDIA | https://cursor.com/blog/topic/customers | Cursor across 30k developers; also hiring "Sr Staff SWE – AI Agent Platform" (https://jobs.nvidia.com/careers/job/893394980306) | AI Agent Platform | — | — | B |
| 14 | Rakuten | https://claude.com/customers/rakuten ; https://claude.com/customers/rakuten-qa | Claude Code (7-hour autonomous runs) + Claude Managed Agents across functions | AI/ML platform | Kenta Naruse (MLE) | — | B |
| 15 | Instacart | https://openai.com/index/codex-now-generally-available/ | Claude Code + Codex SDK (Olive) | DevProd | — | — | B |
| 16 | Cisco | https://openai.com/index/gartner-2026-agentic-coding-leader/ | Codex + GitHub/Sentry/MCP bug-triage workflow (40% lower time-to-patch, U) | Eng productivity | — | — | B |
| 17 | Brex | https://claude.com/blog/how-brex-improves-code-quality-and-productivity-with-claude-code | Claude Code (50% → 100% rollout) | DevEx | — | — | B |
| 18 | Doctolib | https://claude.com/code-with-claude/session/ldn-building-ai-native-at-enterprise-scale-monday-com-doctolib-and-delivery-hero | Claude Code at enterprise scale | Platform eng | — | — | B |
| 19 | Amazon / AWS | https://www.techtarget.com/searchsoftwarequality/news/366639129/AWS-Kiro-user-error-reflects-common-AI-coding-review-gap | Kiro / Amazon Q under an internal adoption mandate (reported 80% target, U) | Builder tools | — | Kiro deleted and recreated an environment → 13-hour Cost Explorer outage; FT reported ≥2 outages | B (hard to sell into) |
| 20 | Datadog | https://openai.com/index/gartner-2026-agentic-coding-leader/ | Codex | Eng Manager | Brad Carter | Also a possible partner or competitor (LLM Observability) | C |
| 21 | Mercado Libre | https://github.com/customer-stories/mercado-libre | Copilot for 9,000+ developers | DevEx | — | — | C |
| 22 | Accenture | https://www.getpanto.ai/blog/github-copilot-statistics | Copilot: 12k, planned 50k; also hiring "AgentOps Engineer" (https://www.accenture.com/us-en/careers/jobdetails?id=R00344460_en) | AgentOps | — | — | C |
| 23 | League | https://claude.com/customers/league | 98% Claude adoption | Eng lead | — | — | C |
| 24 | Satispay | https://claude.com/customers/satispay | 90% Claude Code adoption in 30 days | Eng lead | — | — | C |
| 25 | LG CNS / NTT DATA / Canva / Mizuho / NRI | https://claude.com/customers/lg-cns ; https://openai.com/index/ntt-data/ ; https://chatforest.com/builders-log/code-with-claude-tokyo-recap-rakuten-canva-japan-builder-guide/ | Claude Code / Codex | Delivery center heads | — | APAC cluster | C |

---

## Track 3 — Harness vendors and agent-product companies

| # | Organization | Relevant roles (URLs) | Named person | Public statements on internal reliability tooling | Pri |
|---|---|---|---|---|---|
| 1 | Cursor (Anysphere) | SWE, Agent Evaluation & Quality ("datasets, replay and scoring systems, dashboards, reliability alerts"): https://freehire.me/jobs/software-engineer-agent-evaluation-and-quality-anysphere-inc-doing-business-as-cursor-36yeqrfo ; EM, Evals: https://jobs.thrivecap.com/companies/anysphere-2/jobs/81393850-engineering-manager-evals ; SWE Core Services (agent backend reliability) | Naman Jain (CursorBench) | CursorBench uses "Cursor Blame" to trace committed code back to the agent request; runs online evals. Reportedly acquired Continue (U) | A |
| 2 | Cognition (Devin + Windsurf) | SWE Infrastructure (agent execution environments): https://jobs.ashbyhq.com/cognition/13fdacf7-b4dc-4b9a-ac43-addc87de79ec ; SRE "make sure Devin and Windsurf do not fail": https://workopia.io/jobs/9e7646b7d10bdc32cde42975a22a143a | Walden Yan (co-founder/CPO) | "At the core of reliability is context engineering" (https://cognition.com/blog/dont-build-multi-agents). Interviews ask whether an agent change made it "better or just different" | A |
| 3 | Factory | AI Engineer (Droid reliability at scale): https://jobs.ashbyhq.com/factory/2243dab2-62dc-4c64-b4bc-8f7314475607 | Eno Reyes, Matan Grinberg (co-founders) | Stopped running SWE-bench; uses behavior specs with rubrics; ships a "Reliability Droid" (https://www.zenml.io/llmops-database/enterprise-autonomous-software-engineering-with-ai-droids) | A |
| 4 | Lovable | Engineer – Agents & Evals: https://jobs.ashbyhq.com/lovable/9f4963e7-be14-4dd9-99ce-05df2f06e22d ; Data Scientist, Agent ("whether changes make the agent better or worse… agent telemetry into fixes"): https://www.dreamworkhq.com/job/8d77a78c-ed32-4ec2-93c1-96b3fa75d833 | — | That job description is close to the regression-gate pitch | A |
| 5 | Harvey | SWE, AI Platform (eval infra, context management, session state): https://jobs.ashbyhq.com/harvey/f47e1925-2a89-4264-8a1b-09cd9215f4dd ; SWE / Staff SWE, Agents: https://jobs.ashbyhq.com/harvey/fc038666-be6f-4365-be8d-fb46e520473d | Joey Wang (Eng Lead, Spectre) | Spectre internal cloud-agent platform (https://www.harvey.ai/blog/building-spectre-internal-collaborative-cloud-agent-platform) | A |
| 6 | Glean | SWE, Evals: https://job-boards.greenhouse.io/gleanwork/jobs/4712438005 ; MLE, LLM Evals & Observability ("agent observability… understand what changed and why"): https://job-boards.greenhouse.io/gleanwork/jobs/4669417005 ; MLE, Assistant Quality | — | Dedicated team for evals and agent observability | A |
| 7 | Cline | Senior Agent SWE ("evals, traces… recover from failures, production debugging"): https://freehire.me/jobs/senior-agent-software-engineer-cline-g4vchbur | Saoud Rizwan (CEO, U) | — | A- |
| 8 | Replit | No relevant posting found | Michele Catasta (U) | Agent 3 is long-running on Temporal. Public July 2025 incident: agent deleted SaaStr's production DB during a code freeze (https://swarmproof.github.io/agent-postmortems/2025-replit-prod-db-deletion/) | A (pain) |
| 9 | Decagon | Staff SWE, Agents: https://jobs.ashbyhq.com/decagon/834d9a8b-4f7f-416a-9953-05d93c326a5f ; Agent Deployment Engineer (regression-testing frameworks): https://zapply.jobs/jobs/ee9ff91e-5b27-423a-ae5d-02d272749cd9/ | — | Simulations, Agent Versioning, DuetBench (https://decagon.ai/blog/decagon-agent-versioning). Builds in-house | B |
| 10 | Sierra | SWE, Agent: https://jobs.ashbyhq.com/sierra/149f368c-52d5-408f-ba26-ad888f318a00 | Karthik Narasimhan (Head of Research) | τ-bench pass^k consistency metric; hyper-τ-bench released 2026-09-08. Strong in-house | B |
| 11 | Bolt.new (StackBlitz) | Staff Applied AI Engineer ("own the eval harness, turn failure modes into measurable improvements"): https://job-boards.greenhouse.io/stackblitz/jobs/4111216009 | Eric Simons (CEO) | — | B |
| 12 | Hebbia | Platform Engineer, Agents: https://builtin.com/job/platform-engineer-agents/6606050 ; Applied Research Engineer, Agents | George Sivulka (CEO) | — | B |
| 13 | Writer | Software Quality Engineer (AI agents): https://builtin.com/job/software-quality-engineer-uk/8233176 ; SWE Agents; Infra Engineer (SLOs) | — | — | B |
| 14 | Amp (Sourcegraph spinout, Dec 2025) | Sourcegraph ML & Agentic Systems Engineer (eval and monitoring standards); Tech Lead, Code Plane: https://builtin.com/company/sourcegraph/jobs | Quinn Slack, Thorsten Ball (U) | — | B |
| 15 | Augment Code | SWE, SRE (remote-agents infra): https://builtin.com/company/augment-code/jobs | — (Guy Gur-Ari, U) | Augment's own guide names "Agent Reliability Engineer" and "Agent Evaluation Engineer" as emerging roles (https://www.augmentcode.com/guides/agentic-engineering-operating-model) | B |
| 16 | Warp (Oz) | FDE: https://job-boards.greenhouse.io/warp/jobs/5749183004 ; SWE Enterprise Security (agent permissions, auditability): https://job-boards.greenhouse.io/warp/jobs/6163780004 | Zach Lloyd (CEO) | Oz cloud-agent orchestration (https://www.warp.dev/newsroom/2026/2/10/warp-launches-oz-the-orchestration-platform-for-cloud-coding-agents). Possible partner | B |
| 17 | Poolside | Member of Engineering (Evaluations): https://poolside.ai/careers/member-of-engineering-evaluations--ba11fe78-f6f6-4165-b76b-020a46ad8fee ; (Agent Experience, "owns the harness"); (Experiment Platform) | Eiso Kant (U) | — | B |
| 18 | Zed | AI Rust Engineer: https://zed.dev/jobs | Anant Goel (AI engineer) | Runs evals on every new model release (https://workos.com/blog/zed-anant-goel-evals-agent-context-aie-2026) | C+ |
| 19 | Sweep | Mostly GTM roles (U: the listing may be a different "Sweep") | William Zeng, Kevin Lu | — | C |
| 20 | Continue | Legacy SWE posts: https://www.continue.dev/join/software-engineer-5-plus-years | — | LinkedIn says "acquired by Cursor" (U) | C |
| 21 | Reflection AI | 51 roles, including FDEs for agentic systems: https://www.fastaijobs.com/companies/reflection | Misha Laskin (CEO) | Asimov code-comprehension agent | C |
| 22 | Magic | No relevant posting found | (Eric Steinberger, U) | — | C |
| 23 | Anthropic (Claude Code / Managed Agents) | Staff+ SWE, Claude Managed Agents: https://job-boards.greenhouse.io/anthropic/jobs/5395767008 ; SWE Systems – Claude Code (agent loop reliability): https://job-boards.greenhouse.io/anthropic/jobs/5218395008 ; Model Performance SWE, Claude Code: https://job-boards.greenhouse.io/anthropic/jobs/5098025008 | Boris Cherny (head of Claude Code), Cat Wu (product) | 2026-04-23 postmortem: 6 weeks of degradation came from 3 harness changes (reasoning effort, caching bug, system prompt), not the model (https://www.infoq.com/news/2026/05/anthropic-claude-code-postmortem/) | A (channel/partner) |
| 24 | OpenAI (Codex) | AI Systems Engineer, Codex Agents ("ablations across… harness behavior… observability across the agent stack"): https://openai.com/careers/ai-systems-engineer-codex-agents-san-francisco/ ; SWE, Codex Core Agents: https://openai.com/careers/software-engineer-codex-core-agents-san-francisco/ | Alexander Embiricos (Codex product lead); Thibault Sottiaux (now heads the core product org) | Codex runs on Temporal. OpenAI's Evals platform is being shut down 2026-11-30, with migration pointed at Promptfoo (U) | A (channel) |
| 25 | Google (Antigravity / ADK / Jules) | Not found; look for Antigravity/ADK eval & reliability SWE roles | Varun Mohan (head of Antigravity) | "Anatomy of Harness Engineering: evaluate, iterate, guard" (https://developers.googleblog.com/the-anatomy-of-harness-engineering-how-to-evaluate-iterate-and-guard-ai-coding-agents/); ADK Go 1.0 has native OTel | B |

**Adjacent agent-product companies hiring for this**
- Databricks: Staff SWE, Agent Quality — https://job-boards.greenhouse.io/databricks/jobs/6954585002 (U)
- Perplexity: SWE, Agent Infra — https://job-boards.greenhouse.io/perplexityai/jobs/4859811007
- Traversal: AI Agents Engineer — https://job-boards.greenhouse.io/traversal/jobs/4747105008
- Intercom: Fin Evals/Releases/Monitors, built in-house — https://www.intercom.com/blog/announcing-evals-and-releases/
- Vercel: v0, regression tests built from production failures
- Notion: 1M+ Custom Agents
- Workday: Agent Runtime role — https://workday.wd5.myworkdayjobs.com/en-US/Workday/job/Software-Engineer-Senior-Software-Engineer---AI-Platform--Agent-Runtime-_JR-0109507
- Netic: Agent Platform role
- Zed Financial (PH neobank): AI Engineer, Agent Infrastructure — https://jobs.ashbyhq.com/zedfinancial/f6f294eb-5659-46d0-a9c6-480e6eb4852b

**Competitors and build-vs-buy to note:** LangSmith, Pydantic Logfire, Datadog LLM Observability, Harness AI Evals (gates CD pipelines on eval results), and Mastra Studio. Decagon, Intercom and Sierra have built their own.

---

## Pain signals (for prioritising)

**Incidents**
- **Anthropic harness postmortem**, Apr 2026: three harness changes degraded Claude Code for six weeks; the model weights were not the cause.
- **AWS Kiro**: 13-hour Cost Explorer outage in Dec 2025, reported by the FT in Feb 2026; Amazon then added mandatory peer review.
- **PocketOS**, 2026-04-24: Cursor running Opus deleted the production DB and its backups in 9 seconds despite rules forbidding it (U; https://bex.co/blog/2026/07/11/vibe-coding-incident-guardrails).
- **Replit / SaaStr**, 2025: agent deleted a production DB during a code freeze.
- **Uber**: AI budget gone in 4 months.
- **Datadog State of AI Engineering 2026**: 5% of LLM spans errored in Feb 2026, 60% of them rate limits (https://www.datadoghq.com/state-of-ai-engineering/).

**GitHub issues with many participants** (look in the comment threads for company engineers)
- anthropics/claude-code:
  - #68619 — subagent infinite recursion and token burn, 34 comments.
  - #73829 — nested background agents looping for 6.5+ hours; filed by `bob-vistasecurity` (affiliation U).
  - #64080 — the harness ran duplicated parallel tool_use blocks, so 6 subagents became 24.
  - #58637 — zombie subagents send the stop hook into an infinite loop.
  - **#85422 — "Token-burn circuit breaker… per-source attribution (hooks, plugins, subagents)", 17 comments.** This is the component-attribution need stated directly.
  - #38239 (65 comments) and #42249 (45) — runaway token use.
  - #5385 (98 comments) and #63015 (29) — compaction failures.
  - #32699 — OTel stopped exporting after an auto-update, with Elastic APM.
  - #46204 — third-party OTel not initialising on enterprise managed accounts.
  - #31925 and #44818 — managed-settings enforcement bugs, filed by `saad-littera` and `rlaytoncivis` (affiliations U).
- langgraph #6731: agent loops until it hits the recursion limit, 30 comments.
- openai/codex #32753: "Multi-agent V2 regression: subagent instructions are no longer observable."

**Job titles**
- LangChain, "Agent Reliability Engineer, GTM": https://www.dreamworkhq.com/job/eac10893-a145-473c-b984-86c1ddb4ea2d
- Accenture, "AgentOps Engineer"
- Adobe, Senior SRE for agentic AI infrastructure (U)
- Tether, "AI Harness Engineer"
- Databricks, "Agent Quality"
- Cursor, "Agent Evaluation and Quality"

---

## Channels

**Communities**
- Latent Space Discord: agents and evals channels, Wednesday paper club.
- Anthropic Discord.
- OpenAI Developer Forum (community.openai.com).
- MCP contributor Discord and working groups: https://modelcontextprotocol.io/community/communication
- CNCF Slack `#otel-genai-instrumentation`. The GenAI SIG covers agent topics Mondays 09:00 PT; the agent semantic conventions now live in the `open-telemetry/semantic-conventions-genai` repo.
- LangChain community / LangSmith users.
- MLOps Community Slack.
- Pydantic/Logfire, Mastra, CrewAI and OpenHands communities.
- Agentic AI Foundation (Linux Foundation; home of goose).

**Conferences, Q4 2026 to Q1 2027 (plus Apr and Jun 2027)**
- AI Engineer NYC, Oct 12–14 (finance focus).
- GitHub Universe, Oct 28–29, SF.
- KubeCon NA, Nov 9–12, Salt Lake City: Observability Day on Nov 9, plus a new AI Inference + Agentic track.
- AI Engineer Code Summit, Nov 10–12, SF.
- QCon SF, Nov 16–20 (observability/SRE track).
- AI Coding Summit NYC, Nov 16–17.
- AWS re:Invent, Nov 30–Dec 4.
- NeurIPS, Dec 6–12, Sydney. The "Agents in the Wild" workshop is Dec 11; satellite workshops run in Atlanta and Paris on Dec 12–13.
- AI Engineer Europe, London, Feb 17–19, 2027.
- SREcon27 Americas, Seattle, Apr 12–14, 2027.
- AI Engineer World's Fair, Jun 29–Jul 2, 2027.
- Recurring events with 2027 dates not yet announced: Interrupt (2026 edition was May 13–14), Code w/ Claude (2026 was May, SF/London/Tokyo), and the Background Agents Summit run by Ona (2026 was May 6; speakers included Stripe, Uber, Harvey, Monzo, Cloudflare and Genentech — https://background-agents.com/summit/).

**Newsletters and podcasts**
- Latent Space (swyx, Alessio Fanelli).
- The Pragmatic Engineer (AI Tooling 2026 survey).
- Lenny's "How I AI" (has a Stripe Minions episode).
- Simon Willison's blog.
- Software Engineering Daily (has a Codex episode).
- ByteByteGo.
- InfoQ.
- LangChain newsletter.
- ZenML LLMOps Database: a useful index of case studies for finding more targets.

---

## Top 20 to contact first

| Rank | Organization | Why, in one line |
|---|---|---|
| 1 | Stripe (Alistair Gray) | 1,300 unattended PRs a week on a harness with deterministic nodes, plus a 1,370-engineer Claude Code fleet; needs first-divergence and attribution. |
| 2 | Uber (Nikhil Ramakrishnan / Sourabh Shirhatti) | Minion + LangGraph + 60k tasks a week, with a public cost blowout. |
| 3 | Spotify (Max Charas) | Honk on the Claude Agent SDK, so upstream harness changes (the April postmortem) hit it directly. |
| 4 | Ramp (Zach Bruggeman) | Owns its OpenCode-based harness, which writes 30–40% of merged PRs. |
| 5 | Monzo (Suhail Patel) | 1,800 agent tasks a day plus Claude/Cursor governance in a regulated bank. |
| 6 | Salesforce (DX harness team) | Chooses between two harnesses per model at runtime for 100k developers: a literal regression-gate use case. |
| 7 | Cloudflare (Rajesh Bhatia) | Platform team runs the fleet for 3,683 internal users through AI Gateway. |
| 8 | Faire (Luke Bjerring) | 2,000+ autonomous runs a week, after building and dropping its own harness. |
| 9 | Lyft (Nick Ung) | Has publicly described the offline-sim vs production gap. |
| 10 | PagerDuty (Micah Mayo) | LangGraph SRE agent with sub-agent fan-out, and an SRE-native buyer. |
| 11 | Delivery Hero (Rodrigue Schäfer) | Herogen targets 1 in 5 PRs, with a dedicated Claude tool-stack team. |
| 12 | Harvey (Joey Wang) | Spectre cloud agents, and is hiring for eval infra and session state. |
| 13 | Lovable | Hiring explicitly to tell whether agent changes are better or worse. |
| 14 | Cursor (Agent Eval & Quality team) | The open role is replay/scoring/alerts: either buys or sends cloud-agent customers your way. |
| 15 | Coinbase (Evan Kormos) | LangGraph agents with an observability focus, plus a Cursor fleet. |
| 16 | Duolingo (DevXAI) | Swaps Codex and Claude harnesses with one switch, which needs a regression gate. |
| 17 | Clay (Jeff Barg) | 350M agent runs a month. |
| 18 | Glean (LLM Evals & Observability) | Team mandate is "what changed and why." |
| 19 | Factory (Eno Reyes) | Long-running Droids, including a Reliability Droid, sold to enterprises. |
| 20 | Goldman Sachs (Marco Argenti) / Citi (David Griffiths) | Fleets of thousands of Devin agents: long sales cycle but large contracts. |

- **Alternates:** Instacart, Cognition, Cline, BlackRock, Rakuten.
- **Anthropic and OpenAI:** approach as partners or channels, not buyers.
- **Before outreach:** confirm every (U) row and current titles on LinkedIn.
