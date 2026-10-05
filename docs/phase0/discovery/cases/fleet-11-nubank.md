# Nubank: held-out migration benchmark for a 6M-line Devin fleet, and a security team that vetted 2,000+ coding-agent skills (1,500+ risks found, ~1,000 fixed) before they reached developers

evidence_grade: B (pass 2: Nubank's own engineering blog and an AI Engineer World's Fair talk by its Product Security Manager give primary, specific detail on how it governs the skills, rules and MCP servers fed to coding agents; the Devin fleet facts remain vendor-published. No incident or postmortem is public, so not A.)

```yaml
org: Nubank
role: unknown (public: Jose Carlos Castro, Senior Product Manager, in the Devin story; Lucas Palma, Product Security Manager, and Paulo Martins, Lead Security Engineer, for the skills program)
track: fleet
date: 2026-10-05
interviewer: desk (no interview)
method: desk
harnesses_frameworks: [Devin (Cognition), internal "skills" marketplace for AI coding tools (skills, plugins, MCP servers, agent rules), Skill Vetter (internal security scanner), LangGraph/LangChain + LangSmith for the customer-facing agent platform (builder side)]
domain: coding
runs_per_day: "unknown; the ETL migration covered >6M lines and ~100,000 data-class implementations run as parallel Devin sessions; >2,000 skills vetted for the internal marketplace"
failure_definition: "For the migration: not completing a subtask on the held-out evaluation set (inferred). For the skills program: a skill carrying hardcoded credentials, destructive shell commands or excessive permissions (stated risk classes)."
failure_rate_estimate: "unknown in absolute terms; fine-tuning 'doubled task completion scores' on the held-out set; 1,500+ risks in 2,000+ skills"
cost_per_failed_run: unknown
last_failure:
  symptom: "Skills submitted to the internal marketplace contained hardcoded credentials and destructive shell commands buried in instructions meant for coding agents (found by scanning, not from a production incident)"
  detected_by: ci
  time_to_why: unknown
  attributed_component: prompt   # skills = instruction/context bundles; the rules file layer of the harness
  recurred: yes   # 1,500+ findings across 2,000+ skills
  their_words: "what happens when the instructions and capabilities given to AI become dependencies themselves"
harness_change:
  last_change: "Skill Vetter in CI and PR workflow for every skill; expansion planned to MCP servers, plugins, agent rules and third-party marketplace entries. Earlier: fine-tuned Devin on prior manual migrations; Devin wrote its own scripts for common subtasks."
  regression_detection: evals   # held-out migration benchmark for Devin; CI scanning for skills
  silent_regression_experienced: unknown
  would_pay_to_prevent: unclear
controls_owned (fleets): [rules_files, mcp_servers, tool_allowlists, ci_checks]   # stated: a security-reviewed marketplace gates skills, with MCP servers, plugins and agent rules next
tooling_today: [Devin, held-out migration benchmark from historic human migrations, Skill Vetter (regex scanners + LLM behavioral review, local and CI), internal skills marketplace, vulnerability-management system fed by standardized reports, LangSmith (builder-side agents)]
coding_agent_traces_flow_to: unknown   # LangSmith traces the customer-facing agent platform, not coding agents (inferred)
can_reproduce_failed_run: unknown
has_compared_cohorts: yes   # fine-tuned vs base Devin on the held-out set
most_wanted_question: unknown
data_constraints:
  cannot_leave: unknown   # regulated bank; skills pipeline keeps controls "inside the workflow engineers already use", but no statement on telemetry
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: security   # inferred for the skills program (Product Security owns it); the Devin program's owner is not public
credible_contract_size: unknown
automation_limits: "Engineers review and merge Devin's PRs; skills that fail vetting are remediated or blocked before distribution; policies can require remediation or block distribution"
would_allow_pause_stop_on_evidence: conditional   # inferred: they already block skills on evidence in CI
reaction:
  would_use_next_week: unknown
  does_not_believe: unknown
design_partner_candidate: unknown
referrals: []
quotes:
  - q: 9
    text: "Rather than engineers having to work across several files and complete an entire migration task 100%, they could just review Devin's changes, make minor adjustments, then merge their PR"
  - q: 12
    text: "what happens when the instructions and capabilities given to AI become dependencies themselves"
  - q: 12
    text: "Skills, plugins, MCP servers, and agent instructions can influence generated code, expose credentials, grant excessive permissions, or execute destructive commands."
    paraphrase: true
sources:
  - https://devin.ai/customers/nubank/
  - https://x.com/cognition_labs/status/1866579175743820116
  - https://building.nubank.com/when-ai-skills-become-supply-chain-dependencies-2/
  - https://ai.engineer/speakers/lucas-palma
  - https://www.zenml.io/llmops-database/security-review-system-for-ai-skills-in-developer-workflows
  - https://daily.dev/posts/we-vetted-2000-ai-skills-before-they-reached-developers-lucas-palma-nubank-gncebirg9
  - https://building.nu.com/building-ai-agents-for-131-million-customers/
  - https://building.nu.com/enhancing-engineering-workflows-with-ai-a-real-world-experience/
tags:
  harnesses_frameworks: stated (Devin story; skills blog; ZenML summary of the Nubank agent-platform talk for LangGraph/LangSmith)
  runs_per_day: stated (6M lines, 100k data classes, 2,000+ skills); "parallel sessions" inferred
  failure_definition: inferred (migration) / stated (skills risk classes)
  failure_rate_estimate: stated (doubling; 1,500+ risks)
  last_failure.*: stated (risk classes, CI/PR detection, counts); attributed_component inferred (skills are instruction bundles)
  harness_change: stated
  regression_detection: stated (held-out benchmark; CI scanning)
  controls_owned: stated (skills now; MCP servers, plugins, agent rules planned)
  has_compared_cohorts: inferred (fine-tuned vs base on held-out set)
  budget_owner: inferred
  would_allow_pause_stop_on_evidence: inferred
  automation_limits: stated
  quotes: q9 verbatim (Devin page snippet); q12 first quote verbatim (blog snippet); second q12 quote is the search tool's rendering, marked paraphrase
```

## Evidence

- Devin fleet: Nubank split a >6M-line, eight-year-old ETL monolith into sub-modules; ~100,000 data-class implementations, each migrated separately; manual estimate >1,000 engineers over 18 months (https://devin.ai/customers/nubank/).
- Nubank collected prior manual migrations, used some to fine-tune Devin and held the rest back as a benchmark evaluation set; on that set fine-tuning doubled task-completion scores and cut per-subtask time from ~40 to ~10 minutes; reported 12x engineering-hour efficiency and >20x cost savings; Cognition says ~1.5 years became ~2 months (https://devin.ai/customers/nubank/; https://x.com/cognition_labs/status/1866579175743820116).
- Devin built "classical tools and scripts" it reused on common subtasks; engineers "review Devin's changes, make minor adjustments, then merge their PR" (https://devin.ai/customers/nubank/).
- Skills program (Nubank engineering blog): the security team asked "what happens when the instructions and capabilities given to AI become dependencies themselves" and built a system that reviewed more than 2,000 AI skills before they could reach developers; skill creators submit via pull requests and an automated "Skill Vetter" evaluates and classifies risk before the skill appears in the internal marketplace; the goal was to make controls "operate inside the workflow engineers already use" rather than a separate approval gate. Led by Paulo Martins (Lead Security Engineer); presented by Lucas Palma (Product Security Manager) at the AI Engineer World's Fair, San Francisco (https://building.nubank.com/when-ai-skills-become-supply-chain-dependencies-2/; https://ai.engineer/speakers/lucas-palma).
- Findings: over 1,500 risks across 2,000+ skills, "ranging from hardcoded credentials to destructive shell commands buried in instructions meant for coding agents"; roughly 1,000 remediated quickly; a handful blocked outright (https://daily.dev/posts/we-vetted-2000-ai-skills-before-they-reached-developers-lucas-palma-nubank-gncebirg9).
- Mechanism: hybrid of deterministic regex scanners and LLM-based behavioral review; developers can scan locally; CI repeats the checks and posts findings in the PR; policies can require remediation or block distribution; standardized reports feed the existing vulnerability-management system; the same framework is being extended to MCP servers, plugins, agent rules and third-party marketplace entries (https://www.zenml.io/llmops-database/security-review-system-for-ai-skills-in-developer-workflows).
- Builder-side context: Nubank's customer-facing agent platform is described as four layers (core engine, LLM-as-judge and online evaluation, LangGraph/LangChain developer experience, LangSmith observability), run "evals-first" (https://building.nu.com/building-ai-agents-for-131-million-customers/; https://www.zenml.io/llmops-database/building-an-ai-private-banker-with-agentic-systems-for-customer-service-and-financial-operations).
- Earlier Nubank blog (Clojure Conj 2024 talk) covers LLM code generation for Clojure in general, with no governance detail (https://building.nu.com/enhancing-engineering-workflows-with-ai-a-real-world-experience/).
- Not public: any production incident caused by a coding agent, cost overruns, telemetry destinations for coding agents, or data-residency rules for agent transcripts.

## What this case says for Gate A

Nubank is the strongest public example of a fleet operator treating the harness layer (skills, rules, MCP servers, plugins) as a governed artifact: every skill passes a CI scanner before distribution, and the plan is to extend the gate to MCP servers and agent rules. It also built a held-out regression set before scaling Devin. Both are the behaviours Tracelyt wants to productize, done in-house for security risk classes (credentials, destructive commands, over-permissioning) rather than for behavioural regressions. That is both validation and a warning: a sophisticated team will build the security gate itself, so the gap to sell is behavioural attribution and replay, not scanning. The 1,500+ findings count toward "non-model failure modes in the harness" but not toward "silent regression experienced", because they were caught pre-distribution. Data constraints and willingness to pay remain unknown; the Product Security team (Palma, Martins) is the natural live-interview target.
