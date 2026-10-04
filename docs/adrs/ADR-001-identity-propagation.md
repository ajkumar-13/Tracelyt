# ADR-001 — Execution identity and propagation
**Status:** accepted (v0.1) · **Date:** 2026-10-04 · **Deciders:** Data Plane, Capture & Standards
## Context
Runs span processes (harness, subprocesses, MCP servers, subagents). Claude Code does not pass OTEL_* variables to subprocesses or hooks; it propagates W3C `traceparent` to Bash children, the Anthropic API and HTTP MCP servers. OTel `gen_ai.agent.id` is a vendor resource id, not a runtime instance.
## Options
A. Rely on OTel trace context only. B. Define our own identity set carried in OTel baggage plus adapter-side correlation on native ids. C. Proprietary propagation header.
## Decision
B. `run_id`, `session_id`, `agent_definition`, `agent_instance_id`, `parent_agent_instance_id`, `turn_id`, `iteration` are first-class (SPEC-01 §4). Tier A instrumentors propagate them as OTel baggage keys `harness.run_id`, `harness.agent_instance_id`, `harness.turn_id`, `harness.policy_version`, `harness.harness_version`. Tier B adapters correlate on native ids (`session_id`, `prompt_id`, `agent_id`, `tool_use_id`, `request_id`, `message_id`). Trace ids are recorded but never used as the run identity.
## Reasons
Proof A showed every observed edge is derivable from native ids; OTel trace context alone cannot represent delegation or turns.
## Consequences
Adapters must publish their id mapping; the merge rules in SPEC-01 §8 depend on these ids being exact.
## Rollback
If OTel adopts `gen_ai.agent.execution.id` (PR #445) with instance semantics, map ours onto it.
