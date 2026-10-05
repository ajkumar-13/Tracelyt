# Uber: in-house agent platform (Minion, LangGraph tools, MCP Gateway) at 60k tasks/week, failures framed as cost and context, not correctness

evidence_grade: B

Primary sources exist (Uber engineering blog posts on the software factory, MCP Gateway, uReview; Interrupt and Background Agents Summit talks), but they are mostly blocked to direct fetch and were read via search snippets. They are rich on cost/context failure modes and thin on incident-level postmortems or harness-change gating.

```yaml
org: Uber
role: Developer Platform / Michelangelo agent platform (public talks: Nikhil Ramakrishnan, Sourabh Shirhatti, Matas Rastenis)
track: builder
date: 2026-10-05
interviewer: desk
method: desk
harnesses_frameworks: [Minion (in-house background agent), LangGraph (Validator, AutoCover), uReview (multi-agent code review), MCP Gateway + Registry, Michelangelo agent platform, Claude Code, Cursor]
domain: coding
runs_per_day: "~8,600 (60,000+ agent task executions per week via MCP Gateway; 1,500 monthly active agents)"
failure_definition: unknown (public framing is cost per session, wrong answer, slow ungrounded search)
failure_rate_estimate: unknown
cost_per_failed_run: unknown (one cited 2-hour coding session cost $1,200; secondary press)
last_failure:
  symptom: "Ungrounded agent repeatedly expanded context searching 'one more location'; took 20m09s and got the answer wrong vs 38s correct when grounded via the context graph. Separately, 100+ installed tools added 50K-70K tokens of schema overhead re-sent every turn."
  detected_by: unknown (cost analysis is the visible lens; inferred dashboard/cost review)
  time_to_why: unknown
  attributed_component: context
  recurred: unknown
  their_words: "An ungrounded agent fails slowly rather than cheaply, repeatedly sending an expanding context window to search one more location"
harness_change:
  last_change: "Automatic compaction at 400k tokens even on 1M-context models; reasoning effort default Medium; cache TTL 5 min -> 1 h for interactive sessions; subagents routed to cheaper model by default"
  regression_detection: unknown (uReview uses offline evals/F1 across model configs and per-category confidence thresholds from developer feedback; no public gate for harness config changes)
  silent_regression_experienced: unknown
  would_pay_to_prevent: unknown
controls_owned (fleets): [mcp_servers, tool_allowlists, model_effort, budgets]
tooling_today: [MCP Gateway logging/metrics/tracing, AI Gateway, AI Guard (redaction), Agent Registry, PII Redactor service]
coding_agent_traces_flow_to: other (in-house gateway logging/tracing; vendor not named)
can_reproduce_failed_run: unknown
has_compared_cohorts: yes (grounded vs ungrounded runs; model pairings for uReview)
most_wanted_question: unknown
data_constraints:
  cannot_leave: [customer_data]
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: dev_productivity
credible_contract_size: unknown
automation_limits: "Third-party MCP servers get 'significantly more rigorous security scrutiny'; per-employee $1,500/month/tool spend cap (June 2026)"
would_allow_pause_stop_on_evidence: unknown
reaction:
  would_use_next_week: unknown
  does_not_believe: unknown
design_partner_candidate: unknown
referrals: [Nikhil Ramakrishnan, Sourabh Shirhatti, Matas Rastenis, Will Bond, Ameya Ketkar]
quotes:
  - q: 1
    text: "An ungrounded agent fails slowly rather than cheaply, repeatedly sending an expanding context window to search one more location"
  - q: 2
    text: "Managing third-party software proved significantly more challenging than our internal servers."
sources:
  - https://www.uber.com/us/en/blog/efficient-software-factory/
  - https://ona.com/stories/background-agents-summit
  - https://background-agents.com/summit/sessions/nikhil-ramakrishnan/
  - https://aaif.io/blog/how-uber-runs-60000-ai-agent-tasks-per-week-with-mcp
  - https://www.zenml.io/llmops-database/scaling-model-context-protocol-mcp-infrastructure-for-enterprise-agentic-ai
  - https://www.speakeasy.com/blog/uber-enterprise-ai-playbook
  - https://lawwu.github.io/transcripts/transcript_Bugs0dVcNI8.html
  - https://www.uber.com/us/en/blog/ureview/
  - https://www.zenml.io/llmops-database/ai-powered-code-review-system-at-scale
  - https://moneywise.com/news/news/uber-ai-budget-claude-code-spending
  - https://startupfortune.com/uber-burned-its-entire-2026-ai-budget-by-april-then-fixed-it/
tags:
  runs_per_day: stated (60k/week; per-day is arithmetic)
  last_failure.symptom: stated
  last_failure.attributed_component: inferred (Uber frames both failures as context/tool-schema bloat, not model quality)
  harness_change.last_change: stated
  regression_detection: inferred (uReview offline eval stated; no harness-change gate described)
  coding_agent_traces_flow_to: inferred (gateway tracing stated; destination not named)
  cannot_leave: inferred (PII redaction on every tool call stated)
  budget_owner: inferred (Developer Platform owns; budget overrun was a company-level finance story)
  has_compared_cohorts: stated
```

## Evidence
- MCP Gateway handles 60,000+ agent task executions per week; 1,500 monthly active agents; 5,000+ engineers, 10,000+ services (https://aaif.io/blog/how-uber-runs-60000-ai-agent-tasks-per-week-with-mcp).
- Minion background agent produces about 11% of PRs; Uber started with migrations, CI improvements and review routing, not codegen (https://background-agents.com/summit/sessions/nikhil-ramakrishnan/ ; https://ona.com/stories/background-agents-summit).
- With 100+ tools installed, pre-loading definitions "added approximately 50K-70K tokens of schema overhead to the initial prompt, which was subsequently re-sent on every context turn" (https://ona.com/stories/background-agents-summit).
- Grounded agent answered a data query in 38 s correctly; ungrounded took 20 min 9 s and was wrong; context graph has 24M nodes / 80M edges from 30+ systems (https://software-factories.port.io/uber ; https://www.uber.com/us/en/blog/efficient-software-factory/).
- Harness knobs changed for cost: compaction at 400k tokens even on 1M models, reasoning effort default Medium, cache TTL 5 min to 1 h, subagents default to a cheaper model; cost per session cut 52% while weekly agent requests grew 9.4x (https://www.uber.com/us/en/blog/efficient-software-factory/ ; https://docs.bswen.com/blog/2026-09-09-uber-software-factory-ai-agent-cost-lessons/).
- MCP Gateway provides authorization, rate limiting, PII redaction and "logging, metrics, tracing" out of the box; third-party MCP servers get stricter scrutiny (https://www.zenml.io/llmops-database/scaling-model-context-protocol-mcp-infrastructure-for-enterprise-agentic-ai ; https://www.speakeasy.com/blog/uber-enterprise-ai-playbook).
- uReview: secondary grader prompt scores each comment; thresholds per assistant/language/category set from developer feedback and evaluations; best F1 from Claude-4-Sonnet generator + o4-mini-high grader; 75% of comments marked useful (https://www.zenml.io/llmops-database/ai-powered-code-review-system-at-scale ; https://www.uber.com/us/en/blog/ureview/).
- Validator/AutoCover are LangGraph agents with sub-agents mixing LLM prompts and deterministic linters; ~21,000 developer hours saved (https://lawwu.github.io/transcripts/transcript_Bugs0dVcNI8.html).
- Company exhausted its 2026 AI tools budget by April; adoption went 32% to 84%; $1,500/month per-tool cap from June 2026 (secondary press) (https://moneywise.com/news/news/uber-ai-budget-claude-code-spending ; https://startupfortune.com/uber-burned-its-entire-2026-ai-budget-by-april-then-fixed-it/).

## What this case says for Gate A
Uber is the strongest public example of a builder who treats harness configuration (compaction threshold, effort, cache TTL, subagent model routing, tool loading) as a tunable surface, and every one of those knobs is a regression-gate candidate. But Uber's public story frames failures as cost and latency, and its fixes were measured with cost dashboards, not correctness gates; there is no public account of a silent regression after a harness change. Their failures are clearly non-model (context and tool schema), which supports component attribution. They already have gateway-level tracing in-house, so a flight recorder competes with internal build, and any replay would have to sit behind their PII redaction. Treat as a strong interview target, not as evidence of pain-to-pay.
