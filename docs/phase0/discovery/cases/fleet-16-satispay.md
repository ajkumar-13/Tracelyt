# Satispay: EU payments company at 90% Claude Code adoption and 75% of monthly code generated with Claude, selected on a 30-day real-ticket evaluation where review quality (not generation speed) decided; budget-level spend with free model choice, Claude as first-pass reviewer before humans

evidence_grade: B (pass 2: Satispay's own newsroom release (May 2026) plus the Anthropic customer story with the CTO's named quotes and Italian trade-press coverage of the release. Specific on evaluation and rollout mechanics; no incident, telemetry or data-residency detail, so not A.)

Replacement note (pass 1): target row 16 (Cisco, Codex) was replaced because its evidence sits on openai.com (egress-blocked); a builder-track Cisco CX case exists. Satispay is row 24 of the same Track 2 list.

```yaml
org: Satispay
role: unknown (named: Fabio Rapposelli, CTO, joined 2025)
track: fleet
date: 2026-10-05
interviewer: desk (no interview)
method: desk
harnesses_frameworks: [Claude Code (Opus or Sonnet, 1M-token context), internal subagents (Java scaffolding, modernization patterns), MCP server for data-transformation Lambda generation, issue-to-PR automation pilot, agentic fraud-investigation pilot]
domain: coding
runs_per_day: unknown (~20 requests a day from finance, legal, marketing and operations after launch; issue-to-PR pilot running)
failure_definition: unknown
failure_rate_estimate: unknown
cost_per_failed_run: unknown
last_failure:
  symptom: unknown
  detected_by: unknown
  time_to_why: unknown
  attributed_component: unknown
  recurred: unknown
  their_words: ""
harness_change:
  last_change: "Modernization approaches packaged into subagents 'so the next team inherits the work'; MCP-connected agent generating AWS Lambdas from specs; Claude used as a first automated review pass before human review"
  regression_detection: manual   # stated for selection: a 30-day head-to-head on real tickets; inferred: no ongoing gate described for subagent or MCP changes
  silent_regression_experienced: unknown
  would_pay_to_prevent: unclear
controls_owned (fleets): [model_effort, budgets, mcp_servers, rules_files]   # stated: budget managed at organizational level "rather than per-seat"; engineers pick Opus or Sonnet; IT ships Claude Code through the managed device fleet; subagents hold reusable patterns
tooling_today: [Claude Code, subagents, MCP servers, managed device fleet (IT)]
coding_agent_traces_flow_to: unknown
can_reproduce_failed_run: unknown
has_compared_cohorts: yes   # stated: 30-day comparison of two tools on real tickets, six dimensions
most_wanted_question: unknown
data_constraints:
  cannot_leave: unknown   # regulated payments; release stresses "highest security standards" but names no telemetry rule
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: unknown   # spend held at organizational level; which function owns it is not stated
credible_contract_size: unknown
automation_limits: "'engineers own what lands in the repository'; fraud-investigation pilot keeps a human in the loop for critical decisions; 'The model is an accelerator, not an authority.'"
would_allow_pause_stop_on_evidence: unknown
reaction:
  would_use_next_week: unknown
  does_not_believe: unknown
design_partner_candidate: unknown
referrals: []
quotes:
  - q: 21
    text: "The model is an accelerator, not an authority."
  - q: 9
    text: "We're moving to a model where the engineer becomes an engineering manager of agents."
  - q: 16
    text: "Claude Code's output, both the code it wrote and the reviews it produced, was considered best across the board."
  - q: 9
    text: "l'ingegnere diventa sempre più il responsabile di un team di agenti: i profili junior riescono a operare al di sopra della loro esperienza perché l'AI fornisce un valido supporto, mentre il controllo finale resta saldamente nelle mani delle persone"
sources:
  - https://claude.com/customers/satispay
  - https://www.satispay.com/it-it/newsroom/satispay-accelera-con-claude-anthropic-ai/
  - https://www.01net.it/satispay-claude-anthropic-75-codice-ai/
  - https://arenadigitale.it/2026/05/22/satispay-accelera-con-claude-il-75-del-codice-generato-dallai-e-50-di-nuove-funzionalita-nel-primo-semestre-2026/
  - https://www.aziendabanca.it/notizie/fintech-insurtech/satispay-claude
tags:
  harnesses_frameworks: stated
  runs_per_day: stated (20 requests/day; pilots)
  harness_change.last_change: stated (subagents, MCP) ; first-pass review stated in the Italian release coverage
  regression_detection: stated (selection) / inferred (no ongoing gate)
  controls_owned: stated
  has_compared_cohorts: stated
  automation_limits: stated
  quotes: English quotes verbatim from the fetched claude.com page via summarizer; Italian quote verbatim from the 01net snippet of Satispay's release
```

## Evidence

- Satispay ran a structured 30-day evaluation in mid-2025 of Claude Code against another AI coding tool on real tickets across its Java/Spring services, scoring code generation quality, refactoring, adherence to internal patterns, multi-file context, test generation and documentation; Claude "won on every dimension except IDE integration" (https://claude.com/customers/satispay).
- Satispay's own release says the decisive criterion "was not generation speed, but the quality of reviews": Claude "identified real problems and explained their causes at a level engineers recognized as genuinely useful" (snippet rendering) (https://www.satispay.com/it-it/newsroom/satispay-accelera-con-claude-anthropic-ai/).
- Results: >90% of engineers use Claude Code; >75% of code committed each month is generated with Claude; an 18-month technical roadmap closed in 7 months; the core payment service's Java 8→21 and Spring upgrade took under four days against a four-week estimate; ~50% more features released in H1 2026 (https://claude.com/customers/satispay; https://arenadigitale.it/2026/05/22/satispay-accelera-con-claude-il-75-del-codice-generato-dallai-e-50-di-nuove-funzionalita-nel-primo-semestre-2026/).
- Engineers use Claude to write new code, modify services, navigate unfamiliar parts of the codebase and do "a first automated review pass before the human one" (Italian coverage of the release) (https://www.01net.it/satispay-claude-anthropic-75-codice-ai/).
- Engineers choose Opus or Sonnet with the full 1M-token context; budget is managed at organizational level rather than per seat "to eliminate task justification delays"; IT ships Claude Code through the managed device fleet so it is available on an engineer's first day (https://claude.com/customers/satispay).
- Reusable patterns (Java scaffolding, modernization approaches) are packaged as internal subagents; an MCP-connected agent generates AWS Lambda functions from specs, cutting 3–5 days to under an hour (https://claude.com/customers/satispay).
- Pilots: issue-to-PR automation (Claude drafts PRs from tickets) and agent-led fraud investigation with a human loop for critical decisions; the operating principle is "engineers own what lands in the repository"; AI proficiency was added to the engineering performance framework (https://claude.com/customers/satispay).
- Scale: ~6M consumers and 450k+ merchants. Rapposelli joined as CTO in 2025 to a team "weighted toward earlier-career engineers" on legacy Java/Spring services (https://claude.com/customers/satispay; https://www.aziendabanca.it/notizie/fintech-insurtech/satispay-claude).
- Not public: incidents, cost events, observability stack, data-residency rules for agent traffic, or any gate on changes to subagents and MCP servers after the initial selection.

## What this case says for Gate A

Satispay did a disciplined cohort comparison once, at tool selection, and chose on review quality rather than speed; that signals a team that values evidence about agent behaviour. After selection the harness kept changing (subagents, an MCP server, model choice left free under a shared budget, Claude inserted as first-pass reviewer) with no described regression gate, which is the pattern Tracelyt targets. The company-authored release is a primary source for the adoption facts, but nothing public describes a failure, a silent regression or a telemetry destination, so no pain counter moves. A regulated payments operator with budget-level spend and free model selection is a credible buyer of cost-plus-quality attribution; whether code or transaction data may leave the environment needs a live conversation with the CTO.
