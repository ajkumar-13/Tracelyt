# Salesforce (Agentforce DX): a harness-agnostic agent SDK with two swappable harnesses (Mastra, Claude Agent SDK) whose telemetry coverage differs per harness

evidence_grade: B

Primary but thin. The best evidence is Salesforce's own published (closed-source, npm-distributed) package READMEs for `@salesforce/sfdx-agent-sdk`, `@salesforce/sfdx-agent-harness-mastra` and `@salesforce/sfdx-agent-harness-claude`, read directly from registry.npmjs.org, plus a Salesforce-engineer-filed Mastra GitHub issue. The Mastra customer page (https://mastra.ai/customers/salesforce) named in the target list could not be fetched and the web-search budget was exhausted, so volume claims (100k developers) are carried from the target list unverified. No failure story or eval practice is public.

```yaml
org: Salesforce
role: Agentforce DX / developer-experience agent platform (no named owner found; Mastra issue filer stephen-carter-at-sf)
track: builder
date: 2026-10-05
interviewer: desk
method: desk
harnesses_frameworks: ["@salesforce/sfdx-agent-sdk (harness-agnostic)", "@salesforce/sfdx-agent-harness-mastra (Mastra core/memory/mcp/libsql)", "@salesforce/sfdx-agent-harness-claude (Claude Agent SDK)", Cursor]
domain: coding
runs_per_day: unknown
failure_definition: unknown
failure_rate_estimate: unknown
cost_per_failed_run: unknown
last_failure:
  symptom: "unknown (no production incident public). Engineering-level failure classes documented in the SDK: boot-time restore failures (missing project dir, harness rejection, thread rehydration failure); unrecognized upstream chunk types after a Mastra/Claude SDK upgrade are dropped from the public stream and only logged at debug; Windows CI could not delete storage after Mastra shutdown (EBUSY)."
  detected_by: ci (Windows GitHub Actions for the EBUSY bug); otherwise unknown
  time_to_why: unknown
  attributed_component: environment (for the only concrete bug); production: unknown
  recurred: unknown
  their_words: "When a harness encounters a chunk type its adapter does not recognize (typically after an upstream Mastra / Claude SDK upgrade), the chunk is skipped on the public stream and surfaced via `LogBus.debug`"
harness_change:
  last_change: "~99 published versions of sfdx-agent-sdk between 2026-05-18 (0.1.0) and 2026-10-03 (0.97.0); harness protocol version is gated at manager creation"
  regression_detection: unknown (e2e tests referenced via connectivityResolver override; CI on GitHub Actions)
  silent_regression_experienced: unknown
  would_pay_to_prevent: unknown
controls_owned (fleets): [mcp_servers, permissions, hooks]
tooling_today: ["SDK LogBus (onLog)", "onTelemetry subscription", "wire-communication events (llm-request/llm-response, mcp-tool-call-completed, llm-retry)"]
coding_agent_traces_flow_to: unknown (SDK emits events to host-subscribed callbacks; destination not public)
can_reproduce_failed_run: partially (inferred: identity, threads, message history and session context persist to disk and are restored on restart; no stated replay)
has_compared_cohorts: unknown
most_wanted_question: unknown
data_constraints:
  cannot_leave: [tool_outputs]
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: unknown
credible_contract_size: unknown
automation_limits: "Tool approval flows built into the SDK; cancelTurn can stop a turn suspended awaiting approval; per-agent onToolResult hook for tool-result redaction"
would_allow_pause_stop_on_evidence: unknown
reaction:
  would_use_next_week: unknown
  does_not_believe: unknown
design_partner_candidate: unknown
referrals: []
quotes:
  - q: 1
    text: "It emits numeric-only, PII-free `llm-retry` telemetry when the Claude Agent SDK reports `api_retry`. Structured `llm-request` / `llm-response` events are **not implemented**: the model client is an opaque native subprocess with no capturable, parseable per-call format."
  - q: 2
    text: "It does **not** emit `llm-retry` telemetry because its stateless fetch layer has no observable retry attempt counter."
sources:
  - https://registry.npmjs.org/@salesforce%2fsfdx-agent-sdk
  - https://registry.npmjs.org/@salesforce%2fsfdx-agent-harness-mastra
  - https://registry.npmjs.org/@salesforce%2fsfdx-agent-harness-claude
  - https://github.com/mastra-ai/mastra/issues/17285
  - https://mastra.ai/customers/salesforce
tags:
  harnesses_frameworks: stated (package READMEs and dependencies)
  telemetry_asymmetry: stated (harness READMEs)
  harness_change.last_change: stated (npm time metadata)
  last_failure.symptom: stated (as documented failure classes, not incidents)
  cannot_leave: inferred (SDK ships a tool-result redaction hook and labels retry telemetry "PII-free")
  can_reproduce_failed_run: inferred
  100k_developers_and_runtime_per_model_choice: from 09-interview-targets.md, not re-verified
```

## Evidence
- `@salesforce/sfdx-agent-sdk` is described as "Harness-agnostic agentic infrastructure for Salesforce developer experience tooling"; closed source, "for use by Salesforce only" (https://registry.npmjs.org/@salesforce%2fsfdx-agent-sdk).
- Two concrete harness packages exist: a Mastra-backed harness and a "Claude Agent SDK-backed AgentHarness implementation" (https://registry.npmjs.org/@salesforce%2fsfdx-agent-harness-mastra ; https://registry.npmjs.org/@salesforce%2fsfdx-agent-harness-claude).
- Mastra harness depends on @mastra/core, @mastra/memory, @mastra/mcp, @mastra/libsql, openai, @anthropic-ai/sdk and Bedrock SDK; example default model id is `sfdc_ai__DefaultGPT5` (https://registry.npmjs.org/@salesforce%2fsfdx-agent-harness-mastra ; https://registry.npmjs.org/@salesforce%2fsfdx-agent-sdk).
- Telemetry coverage differs by harness: Mastra emits per-call `llm-request`/`llm-response` but no `llm-retry`; Claude emits `llm-retry` but no per-call request/response, only a pointer to a subprocess debug log ("wire-monitoring-not-supported") (same sources).
- After an upstream Mastra or Claude SDK upgrade, unrecognized chunk types are silently skipped on the public stream and only logged at debug level (https://registry.npmjs.org/@salesforce%2fsfdx-agent-sdk).
- Restore failures (missing project dir, harness rejection, thread rehydration failure) are queryable; corrupt JSON and harness-id mismatches are "silently dropped" with a warn (https://registry.npmjs.org/@salesforce%2fsfdx-agent-sdk).
- SDK has tool approval flows, `cancelTurn`, and an `onToolResult` hook for tool-result redaction (https://registry.npmjs.org/@salesforce%2fsfdx-agent-sdk).
- ~99 versions published from 2026-05-18 to 2026-10-03, i.e. very frequent harness-layer releases (npm time metadata, https://registry.npmjs.org/@salesforce%2fsfdx-agent-sdk).
- A Salesforce-affiliated engineer filed a Mastra bug found in Windows GitHub Actions CI (LibSQL handle kept open after shutdown), referenced from the harness README as forcedotcom/agentic-dx#429 (https://github.com/mastra-ai/mastra/issues/17285).

## What this case says for Gate A
This is the clearest public artifact of the exact problem our telemetry convention addresses: one product, two interchangeable harnesses, and each harness exposes a different, incomplete slice of telemetry (per-call LLM events on one, retry events on the other, a debug log file instead of spans for Claude). Upstream SDK upgrades can silently drop stream content, which is a textbook silent-regression mechanism, but there is no public statement that it has bitten them in production. Salesforce built its own abstraction layer and telemetry contract, so they are a candidate standards collaborator as much as a buyer. Pain, budget and replay counters stay unknown.
