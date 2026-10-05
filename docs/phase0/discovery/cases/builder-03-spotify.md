# Spotify: Honk (Claude Agent SDK) background agent; names "passes CI but functionally incorrect" as the worst failure and admits prompts evolve by trial and error with no structured evals

evidence_grade: A

Primary four-part Honk series on engineering.atspotify.com (Parts 1-4), a Code with Claude 2026 talk, and a QCon London 2026 talk. Spotify's own posts give a failure taxonomy, verifier design, judge veto rate and an explicit statement about missing evals. Direct fetch was blocked; facts are from search snippets of the primary posts, with secondary summaries flagged.

```yaml
org: Spotify
role: Fleet Management / Honk platform (public: Max Charas, Marc Bruggmann, Niklas Gustavsson)
track: builder
date: 2026-10-05
interviewer: desk
method: desk
harnesses_frameworks: [Honk (Claude Agent SDK in Kubernetes pods), earlier in-house agentic loop on LLM APIs, Claude Code, Fleet Management / Fleetshift, Backstage, local MCP verifiers, MLflow]
domain: coding
runs_per_day: "unknown runs; 650+ merged PRs/month by mid-2026; 1,500+ merged since July 2025; judge stats cover thousands of sessions"
failure_definition: "Stated three modes: (1) no PR produced, (2) PR fails CI, (3) PR passes CI but is functionally incorrect (most serious)"
failure_rate_estimate: "Judge vetoed ~25% of sessions; agent course-corrected in ~half of vetoed cases. Early PR success ~20-30% rising to ~80% with LLM-as-judge (secondary)"
cost_per_failed_run: unknown
last_failure:
  symptom: "Agent 'too ambitious': refactored code or disabled flaky tests outside prompt scope; PRs that pass CI but are functionally wrong, hard to spot in review across thousands of components"
  detected_by: ci
  time_to_why: unknown
  attributed_component: verification
  recurred: yes
  their_words: "the agent gets creative and decides to change things outside the scope of the prompt" (paraphrase of snippet)
harness_change:
  last_change: "Moved from custom agent loop to Claude Code / Agent SDK; added deterministic verifiers (format/build/test via MCP) then an LLM judge on diff+prompt; judge later reported removed as models and harness matured (secondary)"
  regression_detection: manual
  silent_regression_experienced: unknown
  would_pay_to_prevent: unknown
controls_owned (fleets): [rules_files, mcp_servers, tool_allowlists, ci_checks]
tooling_today: [MLflow traces, GCP log upload, LLM-as-judge, Backstage, Fleetshift]
coding_agent_traces_flow_to: other (MLflow; logs to GCP)
can_reproduce_failed_run: unknown
has_compared_cohorts: no ("does not yet have structured ways to evaluate which prompts or models perform best")
most_wanted_question: "inferred: which prompt or model performs best (stated gap)"
data_constraints:
  cannot_leave: unknown
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: dev_productivity
credible_contract_size: unknown
automation_limits: "Agent runs in sandboxed K8s pods with limited permissions; human review of PRs; judge gate before PR"
would_allow_pause_stop_on_evidence: unknown
reaction:
  would_use_next_week: unknown
  does_not_believe: unknown
design_partner_candidate: unknown
referrals: [Max Charas, Marc Bruggmann, Niklas Gustavsson]
quotes:
  - q: 1
    text: "passes CI but is functionally incorrect"
    paraphrase: true
  - q: 2
    text: "Spotify does not yet have structured ways to evaluate which prompts or models perform best"
    paraphrase: true
sources:
  - https://engineering.atspotify.com/2025/11/spotifys-background-coding-agent-part-1
  - https://engineering.atspotify.com/2025/11/context-engineering-background-coding-agents-part-2
  - https://engineering.atspotify.com/2025/12/feedback-loops-background-coding-agents-part-3
  - https://engineering.atspotify.com/2026/4/background-coding-agents-dataset-migrations-honk-part-4
  - https://engineering.atspotify.com/2026/6/code-with-claude-coding-is-no-longer-the-constraint
  - https://www.zenml.io/llmops-database/building-reliable-background-coding-agents-with-verification-loops
  - https://github.com/ogarciacar/evolution-of-agentic-engineering/pull/76
  - https://www.zenml.io/llmops-database/scaling-ai-driven-code-automation-and-engineering-productivity-at-spotify
  - https://www.ninetwothree.co/blog/honk-spotify-ai-infrastructure
  - https://www.infoq.com/news/2026/03/spotify-honk-rewrite/
tags:
  failure_definition: stated
  failure_rate_estimate: stated (veto rate, primary); inferred-secondary (20-30% -> 80%)
  last_failure.symptom: stated
  attributed_component: inferred (Spotify's fix was verification layers; root causes stated as low test coverage, scope creep, agent unable to run builds)
  detected_by: stated (CI/verifiers + judge)
  recurred: inferred (described as recurring behaviour, not one incident)
  regression_detection: stated (prompts evolve by trial and error, no structured evals)
  coding_agent_traces_flow_to: stated (MLflow traces, GCP logs)
  has_compared_cohorts: stated
  judge_removed: secondary claim, unverified in primary
  budget_owner: inferred
```

## Evidence
- Honk runs on the Claude Agent SDK in Kubernetes pods, plugged into Fleetshift and Backstage (https://engineering.atspotify.com/2026/6/code-with-claude-coding-is-no-longer-the-constraint).
- 650+ merged PRs a month by mid-2026; 1,500+ merged since the July 2025 rollout (https://grindengineer.substack.com/p/how-spotify-uses-ai-agents-to-rewrite-its-entire-codebase ; https://engineering.atspotify.com/2025/11/spotifys-background-coding-agent-part-1).
- Three failure modes: no PR; PR fails CI; PR passes CI but is functionally incorrect, "the most serious" because it erodes trust (https://engineering.atspotify.com/2025/12/feedback-loops-background-coding-agents-part-3).
- Causes named: little or no test coverage, agent "gets creative" outside prompt scope, agent cannot work out how to run builds/tests (https://engineering.atspotify.com/2025/12/feedback-loops-background-coding-agents-part-3).
- LLM judge (diff + original prompt) added after agents refactored code or disabled flaky tests out of scope; vetoes ~25% of sessions, agent self-corrects in ~half of those (https://www.zenml.io/llmops-database/building-reliable-background-coding-agents-with-verification-loops ; https://github.com/ogarciacar/evolution-of-agentic-engineering/pull/76).
- Spotify "doesn't yet have structured ways to evaluate which prompts or models perform best"; prompts evolve by trial and error; structured evals are future work (https://engineering.atspotify.com/2025/11/context-engineering-background-coding-agents-part-2).
- Tooling: CLI runs the agent, runs formatting/linting via local MCP, evaluates diffs with LLM-as-judge, uploads logs to GCP and captures traces in MLflow (https://engineering.atspotify.com/2025/11/context-engineering-background-coding-agents-part-2).
- Moving from the custom loop to Claude Code removed the need for users to pre-select files via git-grep; benefits from built-in todo lists and subagents (https://engineering.atspotify.com/2025/11/context-engineering-background-coding-agents-part-2).
- Dataset migrations (Part 4): a human-written migration guide omitted mappings the agent needed; explicit field-mapping tables fixed it; 240 automated PRs (https://engineering.atspotify.com/2026/4/background-coding-agents-dataset-migrations-honk-part-4).
- Secondary: LLM-as-judge took PR success from ~20-30% to ~80%; judge later removed as models and harness matured (https://www.zenml.io/llmops-database/scaling-ai-driven-code-automation-and-engineering-productivity-at-spotify ; https://www.ninetwothree.co/blog/honk-spotify-ai-infrastructure).

## What this case says for Gate A
Spotify is the best public builder evidence that silent, non-model failures exist: their worst failure class is a PR that passes CI but is wrong, and they attribute causes to verification gaps, scope creep and context (a migration guide that omitted mappings). They openly say they cannot tell which prompt or model is better, which is close to the regression-gating problem we target. They already capture traces in MLflow, so an OTel-shaped flight recorder fits their stack. Two caveats: their fix was to build verifiers and a judge in-house (they may keep building), and there is no public statement on budget, willingness to pay, or whether code and traces may leave their GCP environment.
