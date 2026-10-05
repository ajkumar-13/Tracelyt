# Coinbase: about 2,400 developers on Cursor plus Copilot and Claude Code behind an internal model router, review scaled by risk tier

evidence_grade: C (vendor case study plus press interviews and a Coinbase blog post visible only through search snippets; no incident or postmortem detail)

```yaml
org: Coinbase
role: unknown (public voices are Rob Witoff, Head of Platform, and Brian Armstrong, CEO)
track: fleet
date: 2026-10-05
interviewer: desk
method: desk
harnesses_frameworks: [Cursor, GitHub Copilot, Claude Code, internal OpenAI-compatible model router, internal MCP servers (GitHub, Linear)]
domain: coding
runs_per_day: unknown (inferred to be large: >2,400 developers on Cursor; "most engineers" run 5 to 10 agents at a time)
failure_definition: unknown
failure_rate_estimate: unknown
cost_per_failed_run: unknown
last_failure:
  symptom: unknown (no Coinbase-internal incident is public; the HiddenLayer "CopyPasta" disclosure is a demonstrated risk class against Cursor, not a Coinbase incident)
  detected_by: unknown
  time_to_why: unknown
  attributed_component: unknown
  recurred: unknown
  their_words: ""
harness_change:
  last_change: unknown
  regression_detection: unknown
  silent_regression_experienced: unknown
  would_pay_to_prevent: unclear
controls_owned: [mcp_servers, model_effort, ci_checks]   # inferred: the DevX team builds MCP servers and runs a model router; review is tiered by risk
tooling_today: [Cursor, Copilot, Claude Code, OpenAI-compatible router (>1,500 daily users), internal MCP integrations]
coding_agent_traces_flow_to: unknown (the router could be a natural capture point; inferred only)
can_reproduce_failed_run: unknown
has_compared_cohorts: unknown
most_wanted_question: ""
data_constraints:
  cannot_leave: [unknown]
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: dev_productivity   # inferred: the tools and router are owned by DevX/Platform (Witoff is Head of Platform)
credible_contract_size: unknown
automation_limits: "Cryptography and other security-sensitive code stay mainly human-led, with line-by-line review; internal prototyping is effectively fully automated (stated by Witoff via press)."
would_allow_pause_stop_on_evidence: unknown
reaction:
  would_use_next_week: ""
  does_not_believe: ""
design_partner_candidate: unknown
referrals: []
quotes:
  - q: 10
    text: "leaning as hard as we can into AI"
sources:
  - https://cursor.com/blog/coinbase
  - https://www.coinbase.com/blog/Tools-for-Developer-Productivity-at-Coinbase
  - https://cointelegraph.com/news/over-95-of-coinbases-code-is-now-written-with-ai
  - https://www.tradingview.com/news/cointelegraph:475ab94d4094b:0-over-95-of-coinbase-s-code-is-now-written-with-help-of-ai/
  - https://techcrunch.com/2025/08/22/coinbase-ceo-explains-why-he-fired-engineers-who-didnt-try-ai-immediately
  - https://www.entrepreneur.com/business-news/coinbase-ceo-fired-software-engineers-who-didnt-adopt-ai/496250
  - https://www.coindesk.com/tech/2025/09/06/coinbase-s-go-to-ai-coding-tool-found-vulnerable-to-copypasta-exploit
tags:
  harnesses_frameworks: stated
  runs_per_day: inferred
  controls_owned: inferred
  automation_limits: stated (press interview)
  budget_owner: inferred
  quotes: stated (Armstrong via Entrepreneur snippet)
```

## Evidence
- More than 2,400 developers use Cursor as part of an "agent-first" engineering model. Some teams cut idea-to-production time from 20 days to under 2 (https://cursor.com/blog/coinbase).
- Cursor's case study says 75% of all PRs are created by agents, and the average engineer merges 55% more PRs than at the start of the year (https://cursor.com/blog/coinbase).
- Coinbase writes product and technical requirements explicitly for agents. These living documents guide execution and serve as evaluation frameworks after implementation (https://cursor.com/blog/coinbase).
- Coinbase's own blog says it has enabled Cursor, Copilot and Claude Code. Engineers can try new tools on foundation models through an OpenAI-compatible router that more than 1,500 engineers use daily. DevX built MCP servers, for example GitHub and Linear (https://www.coinbase.com/blog/Tools-for-Developer-Productivity-at-Coinbase).
- Head of Platform Rob Witoff told Cointelegraph that 95–100% of code is written by or with LLMs, up from 40% in February, and that most engineers run 5 to 10 agents at once (https://cointelegraph.com/news/over-95-of-coinbases-code-is-now-written-with-ai).
- Witoff described a "wide spectrum" of AI use by risk. Cryptography and security-sensitive code is reviewed line by line by humans (https://www.tradingview.com/news/cointelegraph:475ab94d4094b:0-over-95-of-coinbase-s-code-is-now-written-with-help-of-ai/).
- In 2025 the CEO mandated that all engineers onboard to Cursor and Copilot within a week, and fired engineers who had not done so without a good reason (https://techcrunch.com/2025/08/22/coinbase-ceo-explains-why-he-fired-engineers-who-didnt-try-ai-immediately).
- HiddenLayer's "CopyPasta License Attack" showed Cursor could be steered by hidden instructions in files such as LICENSE.txt, spreading injected code across a codebase. The press framed it as a risk to Coinbase because Cursor was used by "every Coinbase engineer". No Coinbase incident was reported (https://www.coindesk.com/tech/2025/09/06/coinbase-s-go-to-ai-coding-tool-found-vulnerable-to-copypasta-exploit).

## What this case says for Gate A
Coinbase is a strong ICP shape: multiple closed harnesses, a central DevX/Platform team, its own MCP servers, and a model router that is a natural place to capture telemetry. Mandated adoption plus 75% agent-authored PRs means harness changes (rules, MCP servers, model routing) spread fleet-wide almost at once. Still, the public record holds no incident, regression or telemetry-destination evidence, so it counts as zero on every pain counter. The CopyPasta disclosure points to a rules-file and context-poisoning risk class that a flight recorder could detect, but it is a researcher demo, not Coinbase's own experience. Given its regulated custody business, data-residency constraints are likely but not public.
