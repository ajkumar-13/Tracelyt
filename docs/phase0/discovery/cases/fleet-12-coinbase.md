# Coinbase: ~2,400 developers on Cursor plus Copilot and Claude Code behind an internal model router; 95–100% of code written with LLMs, engineers supervising 3–10 agents each, and an internal rule that agents be "observable end-to-end" and "auditable down to inputs and decision traces"

evidence_grade: B (pass 2: three Coinbase-authored engineering blog posts plus on-record interviews with the Head of Platform, now CTO; specific on tooling and governance posture, silent on coding-agent incidents and telemetry)

```yaml
org: Coinbase
role: unknown (public voices: Rob Witoff, Head of Platform then CTO from mid-2026; Brian Armstrong, CEO; Varsha Mahadevan, Senior Engineering Manager)
track: fleet
date: 2026-10-05
interviewer: desk (no interview)
method: desk
harnesses_frameworks: [Cursor (IDE agents and cloud agents), GitHub Copilot, Claude Code, Cody, JetBrains, internal OpenAI-compatible model router, internal MCP servers (GitHub, Linear), CB-GPT internal AI application platform, LangGraph/LangChain for enterprise process agents, qa-ai-agent]
domain: coding
runs_per_day: "unknown; >2,400 developers on Cursor; >1,500 engineers use the router daily; 'most engineers run 5 to 10 agents at once' (2026); agents produce 75% of PRs"
failure_definition: unknown
failure_rate_estimate: unknown
cost_per_failed_run: unknown
last_failure:
  symptom: unknown (no Coinbase coding-agent incident is public; HiddenLayer's CopyPasta disclosure is a demonstrated attack on Cursor, not a Coinbase incident)
  detected_by: unknown
  time_to_why: unknown
  attributed_component: unknown
  recurred: unknown
  their_words: ""
harness_change:
  last_change: "Model router and MCP servers run by DevX; 'training engineers on how to leverage different models for varied use cases'; agent-first engineering model with requirements documents written for agents"
  regression_detection: manual   # inferred: human review tiered by risk; requirement docs used as evaluation frameworks after implementation; nothing automated is described for coding agents
  silent_regression_experienced: unknown
  would_pay_to_prevent: unclear
controls_owned (fleets): [mcp_servers, model_effort, ci_checks, permissions]   # stated: DevX owns MCP servers and the router; review depth varies by risk tier; the enterprise-agent standard requires versioning, observability and auditability
tooling_today: [Cursor, Copilot, Claude Code, OpenAI-compatible router, internal MCP servers, CB-GPT (35-50 apps), LangGraph code-first agents with evaluation and human-in-the-loop as first-class concerns, qa-ai-agent]
coding_agent_traces_flow_to: unknown   # the router is a natural capture point (inferred); the enterprise-agent standard demands "observable end-to-end" but names no stack
can_reproduce_failed_run: unknown
has_compared_cohorts: unknown
most_wanted_question: unknown
data_constraints:
  cannot_leave: unknown   # regulated custody business; enterprise agents must be "hosted in our infrastructure"
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: dev_productivity   # inferred: DevX/Platform owns tools and router; Witoff (Platform, now CTO) is the executive sponsor
credible_contract_size: unknown
automation_limits: "Core cryptography: top cryptographers 'research and review every single line'; AI used heavily to test and check for vulnerabilities; internal prototyping '100 percent automated'; core system management 'somewhere in the middle' (Witoff)."
would_allow_pause_stop_on_evidence: unknown
reaction:
  would_use_next_week: unknown
  does_not_believe: unknown
design_partner_candidate: unknown
referrals: []
quotes:
  - q: 21
    text: "When we're writing core cryptography, our top cryptographers carefully research and review every single line. We use AI heavily to test and check code for vulnerabilities, but it's much more manual than internal prototyping, which is now 100 percent automated."
  - q: 9
    text: "hosted in our infrastructure, versioned through our pipelines, observable end-to-end, evaluated in a repeatable way, and auditable down to inputs and decision traces"
    paraphrase: true
  - q: 10
    text: "The more tools and instructions you load into a prompt, the more 'context noise' you introduce, making outputs harder to reproduce and individual steps harder to unit test or gate in CI."
    paraphrase: true
sources:
  - https://www.coinbase.com/blog/Tools-for-Developer-Productivity-at-Coinbase
  - https://www.coinbase.com/blog/building-enterprise-AI-agents-at-Coinbase
  - https://www.coinbase.com/blog/How-We-are-Improving-Product-Quality-at-Coinbase-with-AI-agents
  - https://cursor.com/blog/coinbase
  - https://cointelegraph.com/news/over-95-of-coinbases-code-is-now-written-with-ai
  - https://www.neweconomies.co/p/coinbase
  - https://www.bankless.com/read/brian-armstrong-says-40-of-coinbases-daily-code-is-ai-generated
  - https://techcrunch.com/2025/08/22/coinbase-ceo-explains-why-he-fired-engineers-who-didnt-try-ai-immediately
  - https://crypto.news/coinbase-names-new-cto-after-14-workforce-cut/
  - https://claude.com/customers/coinbase
  - https://cointelegraph.com/news/coinbase-preferred-ai-coding-tool-hijacked-new-virus
  - https://www.zenml.io/llmops-database/building-enterprise-ai-agents-with-code-first-approach-for-trust-and-auditability
tags:
  harnesses_frameworks: stated (Coinbase blog for Cursor/Copilot/Claude Code/router/MCP; CIO.com snippet for Cody/JetBrains; Coinbase enterprise-agents blog for LangGraph; claude.com for CB-GPT)
  runs_per_day: stated (2,400 via Cursor; 1,500 via Coinbase blog; 5-10 agents via Cointelegraph; 75% PRs via Cursor)
  harness_change.last_change: stated
  regression_detection: inferred
  controls_owned: stated (router, MCP, tiered review, enterprise-agent standard); permissions inferred from the standard's auditability requirement
  budget_owner: inferred
  automation_limits: stated (Witoff via Cointelegraph)
  quotes: q21 verbatim (Cointelegraph snippet); q9 and q10 near-verbatim renderings of the Coinbase enterprise-agents blog via snippets, marked paraphrase
```

## Evidence

- Coinbase's DevX blog: the company "enabled a variety of common coding tools" (Cursor, Copilot, Claude Code); engineers experiment with new tools "directly on foundation models through an OpenAI compatible router that is now used daily by more than 1,500 engineers"; DevX built MCP servers "like Github and Linear integrations" and trains engineers "on how to leverage different models for varied use cases"; every engineer had used Cursor by February 2025 (https://www.coinbase.com/blog/Tools-for-Developer-Productivity-at-Coinbase).
- Cursor case study: >2,400 developers in an "agent-first engineering model"; 75% of PRs created by agents; engineers merge 55% more PRs; idea-to-production cut from 20 days to under 2 on some teams; requirements documents written for agents serve "as evaluation frameworks after implementation"; sprint planning and team sizes were redesigned (https://cursor.com/blog/coinbase).
- Armstrong (2025): 40% of daily code AI-generated, on track for 50% by October; engineers were given one week to onboard to Cursor and Copilot and some who did not were fired (https://www.bankless.com/read/brian-armstrong-says-40-of-coinbases-daily-code-is-ai-generated; https://techcrunch.com/2025/08/22/coinbase-ceo-explains-why-he-fired-engineers-who-didnt-try-ai-immediately).
- Witoff to Cointelegraph (2026): 95–100% of code written by or with LLMs, up from 40% in February; most engineers run 5–10 agents at once; agents do work equivalent to ~1,200 employees; review depth is a "wide spectrum" from line-by-line cryptography review to fully automated prototyping (https://cointelegraph.com/news/over-95-of-coinbases-code-is-now-written-with-ai).
- Witoff was named CTO after a 14% workforce cut in May 2026; in a September 2026 interview he said 98–99% of code is written by agents, engineers moved "from writing code by hand to supervising 3–10 agents each in a single year", and every employee gets a weekly AI feedback agent (https://crypto.news/coinbase-names-new-cto-after-14-workforce-cut/; https://www.neweconomies.co/p/coinbase).
- Coinbase's enterprise-agent standard (Agentic AI Tiger Team, six weeks): agents must be "hosted in our infrastructure, versioned through our pipelines, observable end-to-end, evaluated in a repeatable way, and auditable down to inputs and decision traces"; code-first LangGraph was chosen over low-code because prompt "context noise" makes outputs "harder to reproduce and individual steps harder to unit test or gate in CI"; observability, evaluation and human-in-the-loop are "first-class concerns" (https://www.coinbase.com/blog/building-enterprise-AI-agents-at-Coinbase; https://www.zenml.io/llmops-database/building-enterprise-ai-agents-with-code-first-approach-for-trust-and-auditability).
- qa-ai-agent takes natural-language test requests ("log into coinbase test account in Brazil, and buy 10 BRL worth of BTC"); goal "10x our testing effort at 1/10 the cost"; after two months of results Coinbase began deprecating manual tests it supplants (https://www.coinbase.com/blog/How-We-are-Improving-Product-Quality-at-Coinbase-with-AI-agents).
- CB-GPT, an internal platform, hosts 35–50 AI applications; Claude is consumed through Google Cloud with AWS Bedrock as a second cloud; support chatbot carries "financial compliance guardrails" (https://claude.com/customers/coinbase).
- HiddenLayer's "CopyPasta License Attack" hides instructions in LICENSE.txt/README.md that Cursor copies into generated code, worst in Cursor's auto-run mode; press tied it to Coinbase because Cursor was its preferred tool. No Coinbase incident was reported (https://cointelegraph.com/news/coinbase-preferred-ai-coding-tool-hijacked-new-virus).
- Not public: any coding-agent incident, cost incident, OTel export, rules-file ownership, or which data may leave.

## What this case says for Gate A

Coinbase is the archetype fleet: mandated adoption, three closed harnesses plus an internal router and MCP servers owned by a central DevX team, and agents producing three quarters of PRs with engineers each supervising several. Its own engineering standard for enterprise agents already asks for exactly what Tracelyt sells (versioned, observable end-to-end, repeatably evaluated, auditable to inputs and decision traces), but it was written for internal LangGraph agents, and nothing says the same bar is applied to Cursor or Claude Code sessions. The gap between that standard and the coding-agent fleet is the pitch. Still no public failure, regression or telemetry fact, so every pain counter stays at zero; the router is the obvious instrumentation point but that is inference. The custody business makes in-environment hosting likely, consistent with "hosted in our infrastructure" for enterprise agents. Witoff's platform organization is the live-interview target.
