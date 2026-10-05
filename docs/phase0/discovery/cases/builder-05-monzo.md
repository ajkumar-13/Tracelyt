# Monzo: "Agent Chip", an in-house harness in a regulated bank running 1,800+ tasks/day and ~10% of merged PRs; built in-house for guardrail control, per-task isolated access via Docker + single proxy; Incident Mode has caught engineer errors; a sibling Ops Agent is gated by message-by-message replay of a 100-conversation golden set

evidence_grade: B

Access note (pass 2, 2026-10-05): the primary source is now Monzo's own engineering post "Building Agent Chip: Monzo's in-house agentic tool" (monzo.com/blog, author Fabien Deshayes), reached through several search snippets; InfoQ's QCon London 2026 write-up of Suhail Patel's talk and Ona's Background Agents Summit recap are secondary. Monzo's "Ops Agent" post (customer operations, not coding) is used only for the evaluation-practice fields and is labelled as such. Every pass-1 "carried" fact is now verified or dropped. Grade B: primary, with volumes and architecture, but no concrete failed-run story and no statement on harness-change regression gating for Agent Chip itself.

```yaml
org: Monzo
role: Platform / developer tooling (public: Suhail Patel, Principal Engineer; Fabien Deshayes, blog author)
track: builder
date: 2026-10-05
interviewer: desk
method: desk
harnesses_frameworks: ["Agent Chip (in-house harness, built late 2025; Slack, Linear, GitHub and local clients)", "per-task Docker image + single isolated HTTP proxy", "Claude and Cursor also used by engineers (Ona recap)", "Monzo Ops Agent (customer operations, separate)"]
domain: coding
runs_per_day: "'routinely running more than 1800 tasks every day'; authoring ~10% of all merged PRs"
failure_definition: unknown
failure_rate_estimate: unknown
cost_per_failed_run: unknown
last_failure:
  symptom: "No agent failure story published. Inverse case stated: 'Agent Chip Incident Mode' has 'multiple times' caught errors from responding engineers that could have complicated or extended incident resolution"
  detected_by: unknown
  time_to_why: unknown
  attributed_component: unknown
  recurred: unknown
  their_words: ""
harness_change:
  last_change: "Decision to build Agent Chip in-house in late 2025 for 'full control over the guardrails'; harness iterated 'in partnership with their Security engineers'"
  regression_detection: evals (stated for the Ops Agent: component-level, answer-generation and end-to-end evals, golden set replayed message-by-message; unknown for Agent Chip)
  silent_regression_experienced: unknown
  would_pay_to_prevent: unknown
controls_owned (fleets): [permissions, tool_allowlists, mcp_servers, ci_checks]
tooling_today: [Agent Chip, Docker per-task images, isolated HTTP proxy, static analysis and data-flow controls on a 3,000+ microservice monorepo, CI checks created from incidents, observability systems reachable by the agent]
coding_agent_traces_flow_to: unknown
can_reproduce_failed_run: unknown (Ops Agent: yes, golden conversations are replayed message-by-message)
has_compared_cohorts: unknown (engineers generate "10 or 20 candidate implementations" and choose the best, per InfoQ)
most_wanted_question: unknown
data_constraints:
  cannot_leave: [customer_data]
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: ai_platform
credible_contract_size: unknown
automation_limits: "'know exactly what the agent can see and do, and constrain it appropriately'; per-task access selection; secrets isolated behind one proxy; incident fixes drafted by the agent while humans coordinate; 'quality checks must be high-signal and mandatory'"
would_allow_pause_stop_on_evidence: unknown
reaction:
  would_use_next_week: unknown
  does_not_believe: unknown
design_partner_candidate: unknown
referrals: [Suhail Patel, Fabien Deshayes]
quotes:
  - q: 6
    text: "authoring ~10% of all merged PRs at Monzo and is routinely running more than 1800 tasks every day"
  - q: 9
    text: "building gives them full control over the guardrails they need and the risks they need to manage, which subsequently gives them high confidence over what the harness can and cannot do"
    paraphrase: true
  - q: 9
    text: "The agent can be run on an environment specific docker image depending on the job assigned and is given a single isolated proxy to speak with over HTTP, which allows isolation of secrets and de-risks agent access to the outside world."
  - q: 1
    text: "'Agent Chip Incident Mode' catching errors from responding engineers that could have made incident resolution more complicated or extended their resolution time"
    paraphrase: true
  - q: 10
    text: "when an incident occurs due to a code bug, engineers immediately ask how to turn that bug into a CI check so it cannot recur"
    paraphrase: true
sources:
  - https://monzo.com/blog/building-agent-chip
  - https://www.infoq.com/news/2026/03/shipping-monzo/
  - https://ona.com/stories/background-agents-summit
  - https://monzo.com/blog/engineering-the-future-of-customer-operations-the-monzo-ops-agent
  - https://background-agents.com/summit/sessions/suhail-patel/
tags:
  harnesses_frameworks: stated (Monzo blog: clients, Docker, proxy; Ona recap: Claude and Cursor; model vendor and framework behind Agent Chip not stated)
  runs_per_day: stated (Monzo blog)
  last_failure.symptom: stated as the inverse (agent catching human errors); no agent-failure story found
  harness_change.last_change: stated (Monzo blog: built late 2025, iterated with Security)
  regression_detection: stated for the Ops Agent only; inferred-unknown for Agent Chip
  controls_owned: inferred (per-task access, proxy, Docker image per job, CI checks from incidents)
  tooling_today: stated (Monzo blog; InfoQ on static analysis and data-flow controls)
  cannot_leave: inferred (UK regulated bank; blog's "know exactly what the agent can see"; no explicit data-residency statement)
  budget_owner: inferred (platform-owned, built in partnership with Security)
  automation_limits: stated (Monzo blog; InfoQ)
  has_compared_cohorts: inferred from "10 or 20 candidate implementations" (InfoQ)
```

## Evidence
- Agent Chip "is authoring ~10% of all merged PRs at Monzo and is routinely running more than 1800 tasks every day"; "nearly all" engineers use at least one coding agent regularly (https://monzo.com/blog/building-agent-chip).
- It is "omnipresent": available across Slack, Linear, GitHub and locally, with access to "the vast majority of repositories, documentation and observability systems" (https://monzo.com/blog/building-agent-chip).
- Stated use cases: alert investigation ("automatic investigations of paging alerts in production"), prompt-via-Slack (PRs, bug fixes, reactive work), and a team responder that searches codebase and knowledge base before a human is needed (https://monzo.com/blog/building-agent-chip).
- Monzo chose to build in late 2025 because building "gives them full control over the guardrails they need and the risks they need to manage", giving "high confidence over what the harness can and cannot do" and fast iteration "in partnership with their Security engineers" (https://monzo.com/blog/building-agent-chip).
- Isolation: a "bundle" isolates the production agent enough to "pick and choose what access the agent has on a per task basis"; it runs on an environment-specific Docker image per job and talks to "a single isolated proxy ... over HTTP" that isolates secrets (https://monzo.com/blog/building-agent-chip).
- Incident Mode "pulls together context across systems, surfaces likely causes, and can draft a fix while humans are coordinating"; it has "multiple times" caught errors by responding engineers that could have extended resolution (https://monzo.com/blog/building-agent-chip).
- QCon London 2026 (Suhail Patel): the platform ships "hundreds of changes to production every day"; engineers can generate "10 or 20 candidate implementations within hours" and choose the best; generated code "slots into the platform" drawing on 3,000+ repositories; "quality checks must be high-signal and mandatory"; each incident-causing bug becomes a CI check (https://www.infoq.com/news/2026/03/shipping-monzo/).
- Background Agents Summit: Patel described how the opinionated platform (3,000+ microservices in a monorepo, static analysis, data-flow controls) made AI adoption practical, and "how to adopt AI tools inside a regulated organization without losing control" (https://ona.com/stories/background-agents-summit).
- Ops Agent (customer operations, separate system): a "golden set" of 100 SME-approved conversations is replayed "message-by-message" against the agent to measure it against a human benchmark "in a repeatable way"; three eval tiers: component-level (unit tests for prompts and guardrails), answer-generation (semantic similarity + LLM judges), end-to-end on anonymised real conversations (https://monzo.com/blog/engineering-the-future-of-customer-operations-the-monzo-ops-agent).

## What this case says for Gate A
Monzo is the clearest regulated-bank builder in the corpus: it owns the harness end to end, runs it at 1,800+ tasks a day against production observability and repositories, and states that control over "what the harness can and cannot do" was the reason to build rather than buy. That is the buyer profile for component attribution and in-environment replay, and the per-task Docker-plus-proxy design means replay inside their environment is technically natural. Monzo also already practises replay-based gating (golden set replayed message-by-message) for its Ops Agent, so the concept is understood internally; whether Agent Chip gets the same treatment is not stated. The gaps: no published agent failure, no root-cause time, no trace-sink named, no data-residency statement. The incident-to-CI-check reflex ("how do we turn that bug into a CI check") is a cultural match for CI regression gating of harness changes. Counts: silent_regression unknown, attribution unknown, traces unknown, cannot_leave customer_data (inferred).
