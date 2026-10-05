# Sourcegraph / Amp: thin public record on evals and incidents; threads are server-side and shareable, OTel support unverified

evidence_grade: C

```yaml
org: Amp (Sourcegraph spinout, Dec 2025)
role: harness vendor (Amp CLI, editor extensions, server-side threads)
track: vendor
date: 2026-10-05
interviewer: desk-research agent (vendor track)
method: desk
harnesses_frameworks: [Amp]
domain: coding
runs_per_day: unknown
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
  last_change: "CLI 0.0.1791201662-g90a14c published to npm 2026-10-05 (continuous release cadence)"
  regression_detection: unknown
  silent_regression_experienced: unknown
  would_pay_to_prevent: unknown
controls_owned (fleets): n/a (vendor); exposes (from CLI binary strings): [amp.permissions, amp.dangerouslyAllowAll, amp.mcpServers, managed settings file, thread visibility per repository origin, plugin API, skills]
tooling_today: unknown    # Sourcegraph hiring "ML & Agentic Systems Engineer" to set eval and monitoring standards (research/09)
coding_agent_traces_flow_to: other   # threads stored on ampcode.com and shareable (private, unlisted, workspace, group); customer OTel export unverified
can_reproduce_failed_run: unknown
has_compared_cohorts: unknown
most_wanted_question: unknown
data_constraints:
  cannot_leave: unknown
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: unknown
credible_contract_size: unknown
automation_limits: unknown
would_allow_pause_stop_on_evidence: unknown
would_emit_standard_signal: unknown   # binary bundles @opentelemetry/api and reads OTEL_EXPORTER_OTLP_ENDPOINT, but no documentation reachable to confirm a customer-facing export
reaction:
  would_use_next_week: unknown
  does_not_believe: unknown
design_partner_candidate: unknown
referrals: []
quotes:
  - q: 18
    text: "Change thread visibility (private, unlisted, workspace, group). Use --visibility to change who can access the thread."
sources:
  - https://registry.npmjs.org/@ampcode/cli
  - https://registry.npmjs.org/@ampcode/cli-linux-x64/-/cli-linux-x64-0.0.1791201662-g90a14c.tgz
  - https://registry.npmjs.org/@sourcegraph/amp
  - https://github.com/sourcegraph/amp-examples-and-guides
  - https://builtin.com/company/sourcegraph/jobs
tags:
  controls: stated (strings in the published CLI binary; undocumented here)
  coding_agent_traces_flow_to: stated (thread visibility string) / inferred (server-side storage)
  would_emit_standard_signal: unknown
  everything else: unknown (no reachable primary source)
```

## Evidence
- The Amp CLI moved from @sourcegraph/amp to @ampcode/cli; the npm package exists so "enterprises that want to manage distribution of the Amp CLI through internal package archives" can do so (https://registry.npmjs.org/@ampcode/cli).
- The published linux-x64 binary (version 0.0.1791201662-g90a14c, 2026-10-05) contains settings keys amp.permissions, amp.dangerouslyAllowAll and amp.mcpServers, and a docs link to "legacy-permissions-rules" and a "plugin-api" (https://registry.npmjs.org/@ampcode/cli-linux-x64/-/cli-linux-x64-0.0.1791201662-g90a14c.tgz; inspected with strings).
- The same binary exposes thread visibility levels "private, unlisted, workspace, group" and per-repository-origin default visibility, implying agent transcripts ("threads") live server-side at ampcode.com/threads/ (same source; inferred storage).
- The binary bundles @opentelemetry/api and reads OTEL_EXPORTER_OTLP_ENDPOINT plus "Path to a script that outputs OpenTelemetry headers"; it also contains Claude Code telemetry env names, so these strings may belong to an integration rather than Amp's own export. Not confirmed (same source).
- The official examples repo has guides on agent files and context management, no material on evals, telemetry or data retention (https://github.com/sourcegraph/amp-examples-and-guides).
- Sourcegraph lists an "ML & Agentic Systems Engineer" role around eval and monitoring standards (https://builtin.com/company/sourcegraph/jobs via docs/phase0/research/09-interview-targets.md).
- Not reachable: ampcode.com manual, news and security pages (egress-blocked); web-search budget exhausted. No Amp postmortem, ZDR statement or eval post could be verified.

## What this case says for Gate A
Almost nothing verifiable. Amp keeps threads server-side with team visibility, so it likely owns the data needed for its own regression analysis, and customers' visibility depends on Amp's sharing model rather than their own stack. The case should count as "no evidence", not as a negative. If Amp matters for the vendor track, it needs a live conversation (Quinn Slack or Thorsten Ball) or a re-run when ampcode.com is reachable.
