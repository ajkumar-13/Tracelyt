# 06. Quantitative evidence from surveys, telemetry reports and papers (2025–2026)

Desk-research substitute for the aggregate side of the 50-interview plan. This file answers the interview-guide questions (01-interview-guide.md) **in aggregate**, using published surveys, vendor telemetry reports and research papers. It does not replace the per-case YAML files in `cases/`; it is the denominator against which those cases should be read.

## Methods note

- **Collection date:** 2026-10-05. About 60 WebSearch queries and 6 WebFetch calls. The session's web-search budget ran out before the list below was complete (see "Gaps" at the end).
- **Access:** Following BRIEF.md, primary pages were fetched directly only on reachable domains (datadoghq.com, anthropic.com, github.com). Every other figure comes from **search-result snippets**, which are summaries produced by the search tool, and was not read on the primary page. Those figures are marked `snippet` in the confidence column. Before you cite one externally, open the primary URL and check it.
- **Confidence scale:**
  - **H**: fetched from the primary source, or the same figure appeared in several independent snippets with N and population stated.
  - **M**: one snippet from the primary publisher's page, with N stated.
  - **L**: secondary rewrite, a vendor blog with a small or unclear sample, or N not stated.
- **Population caveat.** Almost none of these sources sample our ICP (teams running long-horizon agents with harnesses they change). The populations are broad: developers in general, IT leaders, or customers of an observability vendor. Benchmark and paper numbers come from research traces, not from production fleets. Each row gives its population so a reader can discount it.
- **Rules applied:** no figure was invented. Where we found nothing credible, the table says **not found**. Figures that appeared in search snippets without a traceable source (for example, anecdotes about specific companies' AI budgets) were left out.

---

## Q1. Share of organizations with agents in production; run volumes

| Figure | Population | N | Source | Conf. |
|---|---|---|---|---|
| 57% have agents in production; 67% at orgs with 10k+ employees; 78% have active plans to put agents into production | LangChain "State of Agent Engineering" survey of professionals (engineers, PMs, leaders), fielded 18 Nov – 2 Dec 2025 | 1,340 (reported as "1,300+") | https://www.langchain.com/state-of-agent-engineering | M (snippet) |
| 23% of organizations are scaling at least one agentic AI system; another 39% are experimenting (62% at least experimenting) | McKinsey State of AI 2025, global executives (38% from companies with revenue above $1B) | 1,993 participants, ~105 countries | https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai | M (snippet) |
| Only 95 of 1,837 respondents (~5.2%) had agents live in production with real users | Cleanlab "AI Agents in Production 2025", software engineering leaders | 1,837 | https://cleanlab.ai/ai-agents-in-production-2025/ | M (snippet) |
| 50% have agentic AI in production for limited use cases; 44% in broad adoption across select departments; 23% mature enterprise-wide (categories overlap) | Dynatrace "Pulse of Agentic AI 2026", senior leaders at enterprises with revenue of $100M+ | 919 | https://www.dynatrace.com/news/press-release/pulse-of-agentic-ai-2026/ | M (snippet) |
| 19% significant investment in agentic AI, 42% conservative, 8% none, 31% wait-and-see/unsure | Gartner webinar poll, Jan 2025 | 3,412 attendees | https://www.gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-over-40-percent-of-agentic-ai-projects-will-be-canceled-by-end-of-2027 | M (snippet) |
| Agent-framework adoption: >9% of orgs (2025) to almost 18% (start of 2026); services using agent frameworks more than doubled | Datadog customers sending LLM telemetry (observed telemetry, not a survey) | ">1,000 customers" | https://www.datadoghq.com/state-of-ai-engineering/ | H (fetched) |
| 59% of agentic application requests touch a single service; only 18% involve 3+ service calls | Same Datadog telemetry | as above | https://www.datadoghq.com/state-of-ai-engineering/ | H (fetched) |
| Developer agent use: 14.1% daily, 9% weekly, 7.8% monthly or less; 52% don't use agents or stick to simpler AI; 38% have no plans to adopt | Stack Overflow Developer Survey 2025 | ~49,000 developers | https://survey.stackoverflow.co/2025/ai ; https://thenewstack.io/23-of-devs-regularly-use-ai-agents-per-stack-overflow-survey/ | M (snippet) |
| Software engineering is ~50% of agentic tool calls on Anthropic's API; other domains each "no more than a few percentage points" | Anthropic API sample (998,481 random tool calls) plus Claude Code sessions | ~1M tool calls | https://www.anthropic.com/research/measuring-agent-autonomy | H (fetched) |
| Claude Code: 99.9th-percentile turn duration rose from <25 min (late Sep 2025) to >45 min (early Jan 2026); median turn ~45 s | Claude Code telemetry | not stated | https://www.anthropic.com/research/measuring-agent-autonomy | H (fetched) |
| 79% of Claude Code conversations classified as automation (vs 49% on Claude.ai) | Anthropic Economic Index, software-development cut | 500,000 interactions | https://anthropic.com/research/impact-software-development | M (snippet) |
| 77% of 1P API (business) usage is automation; ~44% of API traffic is computer/math tasks | Anthropic Economic Index, Sept 2025 | 1M API transcripts (Aug 2025) | https://www.anthropic.com/research/anthropic-economic-index-september-2025-report | H (fetched) |
| GitHub Copilot coding agent opened >1M pull requests, May–Sep 2025; 43.2M PRs merged per month on GitHub overall; >180M developers | GitHub Octoverse 2025 (platform telemetry) | platform-wide | https://github.blog/news-insights/octoverse/octoverse-a-new-developer-joins-github-every-second-as-ai-leads-typescript-to-1/ | M (snippet) |
| E2B sandboxes: ~40k/month (Mar 2024) to ~15M/month (2025); 88 of the Fortune 100 signed up at the July 2025 Series A | E2B company disclosures, via a third-party blog | n/a | https://e2b.dev/about ; https://bex.co/blog/2026/09/06/e2b-scaling-cracks-idle-costs-suspend-latency | L |
| **Runs per day per organization** | — | — | **not found**. No survey reports run volumes per org. Datadog reports token growth (median customer >2x, p90 4x year over year) but not run counts. | — |

## Q2. Agent failure rates and how failure is defined

| Figure | Failure definition | Population / N | Source | Conf. |
|---|---|---|---|---|
| ~5% of LLM call spans returned an error (Feb 2026); ~60% of those were rate limits. 2% in March 2026 (~8.4M rate-limit errors) | API-level span error (infrastructure), **not** task failure | Datadog customers, >1,000 orgs | https://www.datadoghq.com/state-of-ai-engineering/ | H (fetched) |
| Best agent fully completed 30.3% of 175 tasks (Gemini 2.5 Pro); Claude 3.7 Sonnet 26.3%; GPT-4o 8.6% | Task not fully solved, in a simulated software company | TheAgentCompany (CMU) benchmark | https://www.theregister.com/2025/06/29/ai_agents_fail_a_lot/ | M (snippet) |
| ~58% single-turn success, falling to ~35% multi-turn | Task success on CRM business tasks | Salesforce CRMArena-Pro benchmark | https://arxiv.org/abs/2505.18878 | M (snippet) |
| 71.48% of agent-authored PRs merged (so ~28.5% not merged); among rejected PRs, 38% were reviewer-level (no human engagement) and 23% duplicates | PR closed without merge | >33,000 PRs from 5 coding agents on GitHub | https://arxiv.org/abs/2601.15195 | M (snippet) |
| 91.49% of visible resolutions of misalignment episodes required explicit user correction; 90.50% of episodes impose "effort and trust costs" rather than irreversible damage | Developer-agent misalignment episode (7 symptom classes) | 20,574 real coding-agent sessions, 1,639 repos | https://arxiv.org/abs/2605.29442 | M (snippet) |
| Severe test-disabling or false-approval behaviours in ~2% of SWE-chat sessions | Agent evades monitors or oversells success | Transluce analysis of SWE-chat sessions | https://x.com/TransluceAI/status/2084712533638995983 | L (secondary; post) |
| Users interrupt Claude Code in 5% of turns (new users) to ~9% (experienced); human interventions per internal session fell from 5.4 to 3.3 (Aug–Dec) | Human interrupt (a proxy for in-run failure) | Claude Code telemetry; 500k interruptions analysed | https://www.anthropic.com/research/measuring-agent-autonomy | H (fetched) |
| Gartner: >40% of agentic AI projects will be cancelled by end of 2027 (cost, unclear value, inadequate risk controls) | Project-level cancellation (a forecast) | Gartner analysis plus the 3,412-respondent poll | https://www.gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-over-40-percent-of-agentic-ai-projects-will-be-canceled-by-end-of-2027 | M |
| 95% of GenAI pilots delivered no measurable P&L impact | Project-level ROI, not run failure | MIT NANDA: 52 interviews, 153 leaders surveyed, 300 public deployments | https://mlq.ai/media/quarterly_decks/v0.1_State_of_AI_in_Business_2025_Report.pdf | M (snippet; methodology widely criticised) |
| Only 25% of AI initiatives deliver promised ROI | ROI | cited in Datadog report coverage; N not stated | https://investors.datadoghq.com/news-releases/news-release-details/ai-hitting-operational-limits-companies-rush-scale-datadog | L |
| **Production task-failure rate per run, self-reported by orgs** | — | — | **not found**. No survey asks orgs for the share of their production agent runs that fail. Available figures are API errors (Datadog), benchmark success rates, or project-level outcomes. | — |

**Failure-definition takeaway:** public sources use five incompatible definitions: API error, benchmark task failure, PR rejection, human interruption or correction, and project cancellation or ROI. No source uses the guide's "wrong output / no output / over budget / unsafe action / human had to intervene" framing at the level of individual runs.

## Q3. Time to root cause; who does the work

| Figure | Population / N | Source | Conf. |
|---|---|---|---|
| Incidents without decision-trace logging averaged **4.2 h** to resolve, vs under 1 h with full tracing. By class: permission-boundary 23 min, retrieval/context 41 min, tool-call/schema drift 54 min, planning 67 min, memory/long-chain drift 78 min | Sherlocks AI analysis of **73** production agent incidents, Jan–May 2026 (vendor blog) | https://www.sherlocks.ai/blog/why-ai-agents-fail-in-production | L |
| Automated attribution is weak. Best method identifies the responsible agent 53.5% of the time but the failure step only 14.2% (Who&When, 127 multi-agent systems) | Research benchmark | https://arxiv.org/abs/2505.00212 | M (snippet) |
| Best LLM gets 11% joint accuracy localizing errors in agent traces (Gemini 2.5 Pro) | TRAIL: 148 traces, 841 errors (GAIA + SWE-bench) | https://github.com/patronus-ai/trail-benchmark | H (fetched) |
| Best baseline gets 13.2% exact root-step accuracy on long traces (median 145 steps); the proposed RCTA method reaches 24.1% root-step and 51.1% responsible-role accuracy | LongRCA Bench: 1,140 failed trajectories, 5 domains | https://arxiv.org/abs/2608.15242 | M (snippet) |
| In failed CLI coding-agent runs, the decisive error comes early (median step 7 of 27), the recovery window is short (median 1 step), and the error usually surfaces much later | 1,184 failed trajectories (7 models, 3 scaffolds, Terminal-Bench) | https://arxiv.org/abs/2607.09510 | M (snippet) |
| 66% of developers spend more time fixing "almost-right" AI code; 45% say debugging AI code takes longer | Stack Overflow 2025, ~49k developers | https://survey.stackoverflow.co/2025/ai | M (snippet) |
| Human review of agent outputs is a top validation method for 47% (Dynatrace) and 59.8% of eval-running orgs (LangChain); 69% of agentic decisions are still human-verified (Dynatrace) | Dynatrace N=919; LangChain N=1,340 | https://www.dynatrace.com/news/press-release/pulse-of-agentic-ai-2026/ ; https://www.langchain.com/state-of-agent-engineering | M (snippet) |
| **Who does root-cause work (role distribution)** | — | **not found** as a survey statistic. The sources point to the developer or on-call engineer, plus human review, but give no distribution. | — |

## Q4. Component attribution (model vs prompt, context, tools, permissions, orchestration)

| Figure | Population / N | Source | Conf. |
|---|---|---|---|
| **MAST:** failures split into Specification/system design **41.77%**, Inter-agent misalignment **36.94%**, Task verification **21.30%** (14 modes; κ = 0.88) | 150 traces for taxonomy development; MAST-Data has 1,600+ annotated traces across 7 MAS frameworks | https://arxiv.org/abs/2503.13657 | M (snippet; the category split is from secondary coverage, so re-check the exact base) |
| **TRAIL:** 841 errors over 148 traces (5.68 per trace). Reasoning 590, Planning/coordination 220, System execution "rare". Formatting errors plus instruction non-compliance = 353 (~42%) | Patronus TRAIL benchmark | https://arxiv.org/abs/2505.08638 ; https://github.com/patronus-ai/trail-benchmark | M |
| **Model or Harness?** taxonomy: of 41 failure **modes**, 36 are model-side and 5 harness- or environment-side. Note this counts modes (types), not frequencies. Judge agreement κ = 0.76 | Built from benchmarks, system cards, reports and logged trajectories | https://arxiv.org/abs/2607.28802 | M (snippet) |
| **CLI coding-agent failures:** 57.9% of decisive errors are epistemic (false premises 30.7%) rather than competence or environment | 1,184 failed trajectories | https://arxiv.org/abs/2607.09510 | M (snippet) |
| **AgentErrorTaxonomy / AgentErrorBench:** five modules (memory, reflection, planning, action, system). Errors start early and cascade; memory and reflection errors propagate most | ALFWorld, GAIA, WebShop trajectories | https://arxiv.org/abs/2509.25370 | M (qualitative; module shares not retrieved) |
| **Faults in agentic AI repos:** 5 architectural dimensions, 13 symptom classes, 12 root-cause categories, validated with 145 practitioners | 385 faults sampled from 13,602 issues/PRs in 40 repos | https://arxiv.org/abs/2603.06847 | M (shares not retrieved) |
| **Coding-agent misalignment:** 7 cause categories. Constraint violations and inaccurate self-reporting are growing as a share of all misalignment over time | 20,574 sessions | https://arxiv.org/abs/2605.29442 | M |
| **Production incidents by class** (vendor): permission, retrieval/context, tool/schema, planning, memory. Untraceable reasoning cases were ~10% of incidents | 73 incidents | https://www.sherlocks.ai/blog/why-ai-agents-fail-in-production | L |
| Datadog: ~60% of LLM span errors (Feb 2026) were rate limits, i.e. infrastructure/budget rather than model | >1,000 customers | https://www.datadoghq.com/state-of-ai-engineering/ | H |
| Microsoft AI Red Team taxonomy v2.0 (Apr 2026): 7 failure-mode categories, including memory poisoning, cross-domain prompt injection, HITL bypass, MCP/plugin abuse | Qualitative, from 12 months of red teaming | https://www.microsoft.com/en-us/security/blog/2026/06/04/updating-taxonomy-failure-modes-agentic-ai-systems-year-red-teaming-taught-us/ | M (no frequencies) |
| **Practitioner self-attribution of their last failure (model vs non-model)** | — | **not found**. No survey asks this. | — |

**Reading:** on research traces, the large majority of failures are *not* pure model capability limits. MAST attributes ~58% to specification and inter-agent design plus ~21% to verification. TRAIL's largest bucket is formatting and instruction compliance, which sits at the prompt/harness boundary. However, "Model or Harness?" classes most failure *types* as model-side. Whether a failure is "model" or "non-model" depends on the taxonomy used. This supports the product thesis that attribution is the hard, valuable step, but it does not give an industry-wide share.

## Q5. Cost of failed runs; runaway-cost incidents

| Figure | Population / N | Source | Conf. |
|---|---|---|---|
| 85% of companies miss AI cost forecasts by >10%; nearly 1 in 4 miss by >50%; only 15% forecast within 10% | Benchmarkit × Mavvrik 2025 State of AI Cost Governance | 372 companies | https://www.mavvrik.ai/state-of-ai-cost-governance-report/ | M (snippet) |
| 62% say an unexpected AI cost altered a business decision this year; 40% of those needed board escalation; 84% report margin erosion | same | 372 | https://www.channelinsider.com/ai/mavvrik-state-of-ai-cost-governance/ | M (snippet) |
| 63 confirmed LLM-agent budget-overrun incidents across 21 orchestration frameworks (2023–2026), each tied to a GitHub issue and a dollar loss where reported; 8 mechanism clusters (κ = 0.837); retry loops dominate | Catalog of 110 cases | https://arxiv.org/abs/2606.04056 | M (snippet) |
| Gartner names "escalating costs" as a top reason for >40% of agentic projects being cancelled by 2027 | — | Gartner press release above | M |
| Datadog: 69% of input tokens are system prompts; only 28% of LLM spans use cached reads (structural cost waste) | >1,000 customers | https://www.datadoghq.com/state-of-ai-engineering/ | H |
| Pricing is a top-2 deal-breaker for adopting AI tools | Stack Overflow 2025, ~49k | https://survey.stackoverflow.co/2025/ai | M (snippet) |
| **Cost per failed run (money plus engineer time)** | — | **not found** as an aggregate. | — |

## Q6. Observability adoption; do coding-agent traces reach an observability stack?

| Figure | Population / N | Source | Conf. |
|---|---|---|---|
| 89% have observability for their agents; 62% have detailed tracing | LangChain, 1,340 | https://www.langchain.com/state-of-agent-engineering | M (snippet) |
| LLM observability in production / extensively / exclusively = **7%** combined; 47% investigating or POC | Grafana Observability Survey 2025, 1,255 | https://grafana.com/observability-survey/2025/ | M (snippet) |
| AI monitoring capability use rose from 42% (2024) to 54% (2025); only 4% not deploying or planning it | New Relic 2025 Observability Forecast, >1,700 IT and engineering staff, 23 countries | https://newrelic.com/blog/observability/top-trends-in-observability-the-2025-forecast-is-here | M (snippet) |
| Nearly half say monitoring AI workloads made their jobs harder; 76% use AI-powered observability | Splunk State of Observability 2025, 1,855 | https://www.splunk.com/en_us/blog/observability/state-of-observability-2025.html | M (snippet) |
| Fewer than one third of agents-in-production teams are satisfied with observability and guardrails; 28% satisfied with security/guardrails | Cleanlab, 95 production respondents (out of 1,837) | https://cleanlab.ai/ai-agents-in-production-2025/ | M (snippet) |
| Tools used for agent observability among agent developers: **Grafana + Prometheus 43%, Sentry 32%, LangSmith 12.5%** (existing DevOps stacks dominate) | Stack Overflow 2025, agent-using subset of ~49k | https://survey.stackoverflow.co/2025/ai | M (snippet; re-check the exact question wording) |
| Gartner: LLM observability investment reaches 50% of GenAI deployments by 2028, up from **15% today** (Mar 2026) | Analyst estimate | https://www.gartner.com/en/newsroom/press-releases/2026-03-30-gartner-predicts-by-2028-explainable-ai-will-drive-llm-observability-investments-to-50-percent-for-secure-genai-deployment | M |
| 71% are deploying AI agents faster than they can manage or govern them | Honeycomb survey (Sep 2026); N **not stated** | https://www.honeycomb.io/blog/honeycomb-unveils-new-ai-observability-features-close-gap-shipping-agents-understanding | L |
| 77% say open source/open standards matter to their observability strategy | Grafana 2026 survey, 1,363 | https://grafana.com/observability-survey/ | M (snippet) |
| Claude Code, Copilot, Codex CLI and Gemini CLI all export OpenTelemetry; vendor guides exist for CloudWatch, Grafana, Dash0 and others (capability, not adoption) | — | https://code.claude.com/docs/en/agent-sdk/observability ; https://aws.amazon.com/blogs/mt/analyzing-claude-code-usage-with-cloudwatch-and-opentelemetry/ | M |
| **Share of orgs piping coding-agent (Claude Code/Codex/Cursor) traces into an observability stack** | — | **not found.** No survey measures it. The closest proxies are the 43% Grafana/Prometheus figure (all agent observability, not coding agents) and the 7% LLM-observability-in-production figure. | — |
| Trust: 46% distrust AI accuracy vs 33% trust (3% "highly"); 87% worried about agent accuracy; 81% about agent security/privacy | Stack Overflow 2025, ~49k | https://stackoverflow.co/company/press/archive/stack-overflow-2025-developer-survey/ | M (snippet) |
| 90% of tech professionals use AI | DORA 2025, ~5,000 | https://cloud.google.com/blog/products/ai-machine-learning/announcing-the-2025-dora-report | M (snippet) |

## Q7. Data residency; self-hosted vs SaaS

| Figure | Population / N | Source | Conf. |
|---|---|---|---|
| 63% limit what data can be entered into GenAI; 61% limit which GenAI tools can be used; 48% admit entering non-public company info (2024 study). 27% had banned GenAI at least temporarily | Cisco Data Privacy Benchmark 2024 (privacy and security professionals; N not retrieved) | https://newsroom.cisco.com/c/r/newsroom/en/us/a/y2024/m01/organizations-ban-use-of-generative-ai-over-data-privacy-security-cisco-study.html | M (snippet) |
| Outright GenAI bans fell from 28% (2025) to 7% (2026) | Cisco 2026 Data and Privacy Benchmark | https://www.cisco.com/c/dam/en_us/about/doing_business/trust-center/docs/cisco-privacy-benchmark-study-2026.pdf | M (snippet) |
| Security/privacy is the #1 deal-breaker for adopting an AI tool; 81% concerned about agent data security/privacy | Stack Overflow 2025, ~49k | https://survey.stackoverflow.co/2025/ai | M (snippet) |
| Security is the #2 barrier at enterprises with 2k+ employees (24.9%) | LangChain, 1,340 | https://www.langchain.com/state-of-agent-engineering | M (snippet) |
| 61% run hybrid AI environments (public cloud plus private infrastructure plus third-party) | Mavvrik/Benchmarkit, 372 | https://www.mavvrik.ai/state-of-ai-cost-governance-report/ | M (snippet) |
| Galileo requires the enterprise tier for self-hosting; Langfuse is MIT and fully self-hostable, used by 63 of the Fortune 500 (vendor claim) | Vendor pricing and claims | https://www.braintrust.dev/articles/langfuse-alternatives-2026 ; https://www.firecrawl.dev/blog/best-llm-observability-tools | L |
| **Share that forbids prompts/code/tool outputs leaving their environment** | — | **not found.** No survey asks this specifically about agent telemetry. | — |
| **Self-hosted vs SaaS preference for LLM observability** | — | **not found** as a survey share. | — |

## Q8. Budget owners and contract sizes

| Figure | Population / N | Source | Conf. |
|---|---|---|---|
| Innovation budgets fell from ~25% to 7% of enterprise LLM spend; spend now comes from centralized IT and business-unit budgets | a16z CIO survey 2025, 100 CIOs | https://a16z.com/ai-enterprise-2025/ | M (snippet) |
| 70% say observability budgets rose in the past year | Dynatrace State of Observability 2025, 842 CIOs/CTOs | https://www.dynatrace.com/news/press-release/state-of-observability-2025/ | M (snippet) |
| Enterprise GenAI spend reached $37B in 2025; coding is the largest departmental category at $4.0B (55% of departmental AI spend) | Menlo Ventures, ~500 US enterprise decision-makers | https://menlovc.com/perspective/2025-the-state-of-generative-ai-in-the-enterprise/ | M (snippet) |
| Public list prices: Braintrust Pro $249/mo; LangSmith Plus $39/seat/mo; Galileo Pro $100/mo; enterprise tiers custom everywhere | Vendor pricing pages (via comparison articles) | https://dev.to/bean_bean/braintrust-vs-langsmith-is-249mo-worth-it-the-may-2026-math-2i2a ; https://www.morphllm.com/comparisons/braintrust-vs-galileo-vs-maxim | L |
| **Budget-owner distribution for AI observability/eval (platform vs observability vs security vs dev-productivity)** | — | **not found.** | — |
| **Typical enterprise contract size (ACV) for AI observability/eval** | — | **not found.** Every vendor uses custom enterprise pricing; we found no disclosed ACVs. | — |

## Q9. Evaluation and regression testing for prompt or agent changes

| Figure | Population / N | Source | Conf. |
|---|---|---|---|
| 52.4% run offline evals on test sets; 37.3% run online evals; 89% have observability, which leaves a gap of ~37 points between observability and evals | LangChain, 1,340 | https://www.langchain.com/state-of-agent-engineering | M (snippet) |
| Among orgs that run evals: human review 59.8%, LLM-as-judge 53.3% | LangChain, 1,340 | same | M (snippet) |
| 70% evaluate model outputs by manual testing; only 34% run automated evals; 15% have no formal evaluation | Vercel State of AI survey, Q4 2024 – Q1 2025 | 656 | https://vercel.com/i/what-are-llm-evals-developers-primer | M (snippet) |
| Validation methods: data-quality checks 50%, human review 47%, drift/anomaly monitoring 41% | Dynatrace, 919 | https://www.dynatrace.com/news/press-release/pulse-of-agentic-ai-2026/ | M (snippet) |
| 70% of regulated enterprises rebuild their agent stack every 3 months or faster (41% of unregulated), so harness changes are frequent | Cleanlab, 1,837 (production subset 95) | https://www.cio.com/article/4101921/ai-churn-has-it-rebuilding-tech-stacks-every-90-days.html | M (snippet) |
| **Share with evals gating CI on prompt/harness changes** | — | **not found** as a direct figure. Upper bound ≈ 34% (Vercel automated evals) to 52% (LangChain offline evals). | — |
| **Share shipping changes without evals** | — | Not directly measured. Proxies: ~48% run no offline evals (LangChain, inferred as 100 − 52.4); 15% have no formal evaluation (Vercel). | inferred |

## Q10. Sandbox acceptance for replaying agent runs

| Figure | Population / N | Source | Conf. |
|---|---|---|---|
| Sandbox infrastructure is widely adopted: E2B went from ~40k to ~15M sandboxes/month and reports 88 to 94 of the Fortune 100 signed up | Vendor disclosures | https://e2b.dev/about ; https://bex.co/blog/2026/09/06/e2b-scaling-cracks-idle-costs-suspend-latency | L |
| Only 0.8% of API agent actions appear irreversible; 80% of tool calls have at least one safeguard; 73% have a human in the loop | Anthropic, 998,481 tool calls | https://www.anthropic.com/research/measuring-agent-autonomy | H |
| Autonomous action by AI is the most-doubted AI capability in observability (77% see value, but 15% want stronger safeguards first) | Grafana 2026, 1,363 | https://grafana.com/blog/observability-survey-AI-2026/ | M (snippet) |
| Only 13% use fully autonomous agents; 64% mix autonomous and supervised | Dynatrace, 919 | https://www.dynatrace.com/news/press-release/pulse-of-agentic-ai-2026/ | M (snippet) |
| **Share that would allow third-party replay inside (or outside) their environment** | — | **not found.** No public survey asks this. Only interviews or design-partner conversations can answer it. | — |

---

## Implications for Gate A counters

The counters live in `02-synthesis-template.md`. Aggregate public data **cannot fill the three Gate A count counters** (regression they would pay to prevent; would host replay inside env; design-partner yes), because they measure an individual organization's willingness. The honest report is below.

| Counter | What aggregate evidence says | What we can honestly report |
|---|---|---|
| Interviews completed (target 50) | n/a | 0 live interviews. Desk cases plus this aggregate file. Report it as such; do not convert survey respondents into "interviews". |
| **Described a harness regression they would pay to prevent** (≥15 at 50; kill <4 at 20) | Indirect support for the pain only. Harness churn is high: 70%/41% rebuild their stack every ≤3 months (Cleanlab). ~48% run no offline evals and 63% no online evals (LangChain). Only 34% run automated evals (Vercel). Quality is the #1 barrier (32%, LangChain). Fewer than 1/3 of production teams are satisfied with observability (Cleanlab, n=95). **No source measures willingness to pay to prevent a harness regression.** | **Unknown / cannot be tallied from aggregates.** We may say: "conditions for silent harness regressions are widespread (frequent stack changes, roughly half without eval gates)". We may not claim a count. |
| **Would host replay inside their environment** (≥10; kill <2 at 20) | Sandboxes are mainstream infrastructure (E2B). Privacy/security is the #1 adoption deal-breaker (Stack Overflow 2025) and 63% restrict what data enters GenAI (Cisco 2024), which argues that replay would have to run inside the customer's environment. **No source asks about third-party replay.** | **Unknown.** Directional inference only: in-environment replay is the only plausible model for enterprises. Not a count. |
| **Design-partner candidates (yes)** (≥12) | Not measurable from public data. | **Unknown (0 confirmed).** |
| **Attributed last failure to a non-model component** (report share) | Research traces: MAST puts ~58% in specification plus inter-agent design and ~21% in verification. TRAIL's largest bucket is formatting and instruction compliance (~42%). In Datadog API errors, ~60% are rate limits (infra/budget). "Model or Harness?" counts most failure *modes* as model-side (36/41). **No practitioner self-attribution data.** | Report as: "**research-trace evidence: majority non-model (MAST); taxonomy-dependent; practitioner share not found**". Do not merge it into the case-file tally; show it as a separate benchmark line. |
| **Already pipe coding-agent traces to an observability stack** (report share) | Not measured. Proxies: 89% have *some* agent observability (LangChain; a self-selected LangChain audience). LLM observability in production is only **7%** (Grafana 2025). Gartner puts LLM observability investment at **15%** of GenAI deployments today. Among agent developers, Grafana+Prometheus 43%, Sentry 32%, LangSmith 12.5% (Stack Overflow). All major coding agents export OTel (capability). | Report as: "**coding-agent trace export share: not found**. General LLM-observability-in-production: 7% (Grafana, n=1,255) to 15% (Gartner); some agent observability: 89% (LangChain, n=1,340, self-selected)". The spread itself shows the denominator problem. |
| **Budget-owner distribution** (report) | Not found for AI observability/eval. LLM spend has moved from innovation budgets (25% to 7%) to central IT and business units (a16z). 70% saw observability budgets grow (Dynatrace). | Report as **"not found; directional: central IT / platform, with observability budgets growing"**. |

**Bottom line for Gate A:** the public record supports the *conditions* for the pain:
- frequent harness changes;
- roughly half of teams without eval gates;
- very poor automated root-cause localization (11–24% step accuracy);
- 4x longer resolution without traces (vendor, n=73);
- widespread cost-forecast misses (85%, n=372).

It does not supply any of the willingness counters. Gate A should be marked **"not evaluable from desk research"** for the pay, replay and design-partner counters, rather than passed or failed. The minimum live work needed is still a small set of conversations, roughly 10–20, aimed at those three counters.

## Gaps and follow-ups

- The web-search budget (200 calls per session) ran out before these were retrieved: UC Berkeley "Measuring Agents in Production" (practitioner survey), the LangChain 2024 report's production figure, Menlo agent-specific figures, MAST per-mode percentages from the full PDF, and the AgentErrorBench module shares. A follow-up session should pull these.
- Open the primary page and confirm every row marked `snippet` before external use. Priority: MAST category split, the Stack Overflow agent-observability tool shares, and the Grafana 2025 "7%".
