# SPEC-01 — Telemetry and Execution Graph, v0.1

**Version:** 0.1.0 · **Status:** APPROVED v0.1 (founder approval 2026-10-05; Phase 1 baseline) · **Owner:** Capture & Standards with Execution Graph · **Depends on:** PLAN-11, PLAN-12, research 01, 02, 03, 04 · **Machine-readable form:** `src/harness_engine/model/events.py`, JSON Schema in `docs/specs/schema/` (generated) · **Validated against:** real Claude Code 2.1.289 captures (Proofs A, D, E) · **Decision log:** §12 · **Open questions:** §13

## 1. Purpose and first principles

This specification defines the events a harness emits or an adapter reconstructs, the identity that ties them together, how content is referenced without being carried, how events become a graph with provenance-typed edges, and how completeness is disclosed as a fidelity level.

1. **Events sit on interfaces.** A harness is a set of components joined by interfaces. Every event names its owning component and, where meaningful, the counterpart across the interface (§6). Attribution to a component is therefore structural, not inferred.
2. **Three epistemic classes, never mixed.** Observed facts carry runtime identifiers and live in events. Reconstructed facts (ordering, content addressing) and inferred facts (detectors, attribution) live only on graph edges with a `source` (§9).
3. **Content never travels in an event.** Content is referenced by SHA-256 and size (`PayloadRef`); the bytes stay where the customer keeps them (PLAN-11 P15, P16).
4. **Small and correct.** Nine domains and 31 event types in v0.1 (D-034). Unknown native events are preserved as `unknown` with their native name and attributes; they are never dropped.
5. **Idempotent normalization.** Event ids are derived deterministically from stable native identifiers so that re-normalizing the same evidence yields the same ids (PLAN-11 P18).
6. **Every emitter has a published coverage matrix and every run a fidelity level** (§10, PLAN-11 P10, D-032).

## 2. Relationship to OpenTelemetry GenAI and OpenInference

OTel `gen_ai.*` (Development status throughout; 79 attributes, 11 span definitions, 3 events on `main` as of 2026-10-02) covers inference, embeddings, retrieval, memory operations, `create_agent`, `invoke_agent`, `invoke_workflow`, `plan`, `execute_tool`, and a boolean `gen_ai.conversation.compacted` marker. It has no convention for permission decisions (PR #535 proposes `gen_ai.tool.call.decision`), agent lifecycle (PR #445, paused), execution state change (PR #483), context provenance (issue #181), verification, agent-level stop reasons, delegation identity or compaction detail. OpenInference adds span kinds and flattened message attributes but none of those concepts either (research 01 §C.2).

Every event in this spec therefore has two external names (ADR-002):
- **Proposal form** `gen_ai.*`: reuses an existing or proposed OTel name where one exists, otherwise a name we will propose through the GenAI SIG.
- **Registry form** `harness.*`: the name in the registry we govern (PLAN-06 Track 2), stable regardless of upstream outcome.

The reference implementation emits the internal type and both forms (`NAMING` in `events.py`). A normalizer accepts either, plus OpenInference, plus native adapter formats.

## 3. Envelope

Every event carries (`Event` in `events.py`):

| Field | Type | Req | Meaning |
|---|---|---|---|
| `event_id` | string(32 hex) | R | Deterministic: sha256 of stable native parts (run id, native type, timestamp or sequence, correlation keys) |
| `type` | enum §5 | R | One of the 31 v0.1 types or `unknown` |
| `native_type` | string | Rec | The emitter's own name, always preserved (e.g. `hook.PostCompact`, `otel.claude_code.tool_decision`) |
| `timestamp` | RFC 3339 UTC | R | Emitter time; adapters that have no timestamp (SDK stream) align to a timestamped channel and say so in `source_channel` |
| `sequence` | int | Rec | Emitter-monotonic order when available (Claude Code `event.sequence`) |
| `identity` | §4 | R | Execution identity |
| `versions` | §4.3 | Rec | Harness, model, prompt, policy, tool definitions, commit, image |
| `component` | enum §6 | R | Owning component |
| `counterpart` | enum §6 | Rec | Component across the interface |
| `parent_event_id` | string | Opt | For derived events (verification adapter output points at its source) |
| `correlation` | map | Rec | Shared identifiers that make merging and graph edges observed: `tool_call_id`, `request_id`, `message_id`, `message_uuid`, `request_body_id`, `turn_id`, `child_agent_instance_id`, `boundary_uuid`, `content_hash` |
| `status` | enum | Rec | `ok`, `error`, `denied`, `cancelled`, `unknown` |
| `attrs` | object | R | Per-type attributes (§5), validated against the per-type model |
| `payload_refs` | map name→PayloadRef | Opt | `prompt`, `input`, `output`, `error`, `summary`, `request_body`, `response_body`, `result`, `final_message` |
| `capture_tier` | A, B, C | R | How the event was obtained (PLAN-05 §4) |
| `source_channel` | string | R | e.g. `claude_code.hooks`, `claude_code.otel_logs`, `claude_code.sdk_stream`, `verification_adapter`; merged events join channels with `+` |
| `schema_version` | string | R | `0.1.0` |

`PayloadRef` = `{sha256, size_bytes, media_type, uri?, redaction: none|partial|full|hashed}`. The `uri` is customer-side and optional; the hash is the identity.

## 4. Identity and versions

### 4.1 Identity (`Identity`)
`organization_id`, `project_id`, **`run_id`** (required; the semantic execution, which for a CLI session is the session), `session_id` (long-lived container of runs if distinct), `agent_definition` (e.g. `reviewer`, `main`), `agent_instance_id` (runtime instance; subagents get their own; `main` for the root), `parent_agent_instance_id`, `iteration`, `turn_id` (human-prompt scope), `trace_id`, `span_id`.

Rules: never conflate `trace_id`, `run_id`, `session_id`, `agent_definition`, `agent_instance_id`, `turn_id` (PLAN-12 §7). An OTel trace may not equal a run. `gen_ai.agent.id` in OTel is a vendor resource id, not an instance; `agent_instance_id` has no upstream equivalent yet and is proposed as `gen_ai.agent.instance.id`.

### 4.2 Iteration
An iteration opens at each model response within an agent instance; the tool activity that response triggers belongs to it. Adapters must tolerate hook records that precede the flushed model-response record (observed in Claude Code; Proof results §Findings 2): unresolved tool requests carry into the next iteration.

### 4.3 Versions (`Versions`)
`harness` (e.g. `claude-code@2.1.289`), `harness_config_hash` (hash of rules files, settings, hooks, MCP config), `model`, `prompt`, `policy`, `tools` (hash of tool definitions presented), `code_commit`, `runtime_image`. Regression analysis is unreliable without these (PLAN-11 P19).

## 5. Event types, attributes, and external names

Attribute tables are normative; the pydantic models are the machine-readable source. "Obs." = observed on Claude Code 2.1.289 in Phase 0. Requirement: R required, Rec recommended, O optional.

### 5.1 RUN
| Type | Attributes | Proposal form | Registry form |
|---|---|---|---|
| `run.started`, `run.resumed` | `source` (startup, resume, clear, compact, fork) Rec; `entrypoint` (cli, sdk, ci, api) Rec; `permission_mode` Rec; `cwd_hash` O; `task` O (usually a PayloadRef) | root `invoke_agent` span start; PR #445 `gen_ai.agent.started` / `gen_ai.agent.resumed` | `harness.run.started`, `harness.run.resumed` |
| `run.completed`, `run.failed`, `run.aborted` | `stop_reason` (§5.9 enum) R; `total_turns`, `duration_ms`, `total_cost_usd`, `input_tokens`, `output_tokens`, `cache_read_tokens`, `cache_creation_tokens`, `num_permission_denials` Rec; `terminal_reason` (native) Rec | `gen_ai.agent.completed` / `.failed`; usage via `gen_ai.usage.*` | `harness.run.completed` … |

Obs.: SessionStart/SessionEnd hooks; SDK `result` (usage, `permission_denials`, `terminal_reason`).

### 5.2 LOOP
| Type | Attributes | Proposal | Registry |
|---|---|---|---|
| `iteration.started`, `iteration.completed` | `iteration` R; `state_hash_before`, `state_hash_after`, `budget_remaining_tokens`, `budget_remaining_usd`, `progress_signal` (progress, no_change, unknown) O | new: `gen_ai.agent.iteration` (int) on spans/events; state hashes align with PR #483 `gen_ai.execution.state.*` | `harness.iteration.started`, `.completed` |

Obs.: human-turn boundaries via `prompt_id`; model-response boundaries via `api_request`.

### 5.3 MODEL
| Type | Attributes | Proposal | Registry |
|---|---|---|---|
| `model.request` | `model` R; `provider`, `request_id`, `client_request_id`, `max_tokens`, `thinking_budget_tokens`, `num_messages`, `num_tools`, `tools_hash`, `system_hash`, `previous_message_id`, `context_tokens_estimate`, `query_source` Rec | `gen_ai.inference.client` span: `gen_ai.request.model`, `gen_ai.request.max_tokens`, `gen_ai.request.previous_response.id`, `gen_ai.tool.definitions` (hash only in our profile), `gen_ai.system_instructions` (hash only) | `harness.model.request` |
| `model.response` | `model` R; `request_id`, `message_id`, `input_tokens`, `output_tokens`, `cache_read_tokens`, `cache_creation_tokens`, `thinking_tokens`, `cost_usd`, `duration_ms`, `ttft_ms`, `finish_reason`, `num_tool_calls`, `retry_attempt`, `error_type` Rec | `gen_ai.response.id`, `gen_ai.response.model`, `gen_ai.response.finish_reasons`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`, `gen_ai.usage.cache_read.input_tokens`, `gen_ai.usage.cache_write.input_tokens`, `gen_ai.usage.reasoning.output_tokens`, `gen_ai.response.time_to_first_chunk`, `error.type` | `harness.model.response` |

Obs.: OTel `api_request`, `api_request_body`, `api_response_body`, `api_error`, `api_retries_exhausted`; SDK `assistant.message.stop_reason`; raw bodies via side channel. Profile note: our profile records `tools_hash` and `system_hash`, never the content attributes, unless the customer opts in.

### 5.4 TOOL and MCP
| Type | Attributes | Proposal | Registry |
|---|---|---|---|
| `tool.requested` | `tool_name` R; `tool_call_id` R; `tool_source` (builtin, mcp, plugin) Rec; `mcp_server`, `mcp_tool` CR when mcp; `side_effect_class` (§5.4.1) Rec; `input_hash`, `input_size_bytes` Rec; `file_path_hash`, `command_binary` O | `gen_ai.execute_tool.internal` span start: `gen_ai.tool.name`, `gen_ai.tool.call.id`, `gen_ai.tool.type`; MCP via `mcp.method.name=tools/call`; new: `gen_ai.tool.side_effect` enum | `harness.tool.requested` |
| `tool.authorized`, `tool.rejected` | `tool_name` R; `tool_call_id` R; `decision` (allow, deny, ask, defer) R; `source` (§5.6 enum) R; `rule`, `reason` O | **PR #535** event `gen_ai.tool.call.decision` with `gen_ai.tool.call.decision.outcome` ∈ allow, deny, require_approval; new attribute `gen_ai.tool.call.decision.source` | `harness.tool.decision` |
| `tool.started` | as `tool.requested` | span start | `harness.tool.started` |
| `tool.completed`, `tool.failed` | `tool_name`, `tool_call_id`, `success` R; `duration_ms`, `output_hash`, `output_size_bytes`, `error_type`, `error_message_hash`, `exit_code` Rec; `files_created`, `files_modified`, `lines_added`, `lines_removed` O | span end; `error.type`; `process.exit.code` | `harness.tool.result` |

5.4.1 **Side-effect class** (ADR-008; aligned with MCP tool annotations `readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`): `read_only`, `reversible_write`, `irreversible_write`, `financial`, `security_sensitive`, `external_communication`, `unknown`. Adapters classify builtin tools by table and shell commands by binary; unknown stays unknown.

Obs.: PreToolUse, PostToolUse, PostToolUseFailure hooks; OTel `tool_decision` (`decision`, `source` ∈ config, hook, user_permanent, user_temporary, user_abort, user_reject), `tool_result` (`success`, `error_type`, sizes).

### 5.5 CONTEXT
| Type | Attributes | Proposal | Registry |
|---|---|---|---|
| `context.build` | reserved in v0.1 (no emitter observed) | — | `harness.context.build` |
| `context.compact` | `trigger` (auto, manual, policy, unknown) R; `tokens_before`, `tokens_after`, `tokens_dropped`, `duration_ms` Rec; `policy_version` O; `preserved_head_id`, `preserved_anchor_id`, `preserved_tail_id`, `num_preserved_messages` Rec; `custom_instructions_present` O; `declared_keys_total`, `declared_keys_surviving` O; payload ref `summary` Rec | new event `gen_ai.context.compaction` (`gen_ai.context.compaction.trigger`, `.tokens.before`, `.tokens.after`, `.summary.ref`); sets `gen_ai.conversation.compacted=true` on the next inference span | `harness.context.compact` |
| `context.provenance.loaded` | `source_kind` (project_instructions, user_instructions, local_instructions, rule, skill, memory, tool_result) R; `source_id_hash` R; `source_name_hash` Rec; `load_reason` Rec; `content_hash`, `tokens` Rec | **issue #181** `gen_ai.context.input.id`, `.kind`, `.content.hash`, `.loaded_by`, `.activation`, `.scope` | `harness.context.input` |

Obs.: PreCompact (`trigger`, `custom_instructions`), PostCompact (`trigger`, **`compact_summary`** full text), SDK `compact_boundary.compact_metadata` (`pre_tokens`, `post_tokens`, `cumulative_dropped_tokens`, `duration_ms`, `preserved_segment`, `preserved_messages`), OTel `compaction` (`pre_tokens` disagrees with the SDK figure; kept as `native_pre_tokens`), InstructionsLoaded (`file_path`, `memory_type`, `load_reason`).

### 5.6 PERMISSION
| Type | Attributes | Proposal | Registry |
|---|---|---|---|
| `permission.requested` | `actor`, `resource`, `action` Rec; `tool_call_id` Rec; `decision=pending`; `num_suggested_rules` O | `gen_ai.tool.call.decision.outcome=require_approval` | `harness.permission.requested` |
| `permission.granted` | `decision=granted`; `source`; `rule`; `policy_version` | `outcome=allow` | `harness.permission.granted` |
| `permission.denied` | `decision=denied` R; `source` R; `reason`, `classifier_verdict` Rec | `outcome=deny`; new `gen_ai.tool.call.decision.reason` | `harness.permission.denied` |

Decision source enum: `config`, `hook`, `user`, `user_permanent`, `user_temporary`, `user_abort`, `user_reject`, `classifier`, `policy`, `headless_default`, `unknown`.

Obs.: PermissionRequest (`permission_suggestions`), PermissionDenied (`denial_reason`, `classifier_verdict` per docs), SDK `permission_denied`, OTel `permission_mode_changed`.

### 5.7 AGENT (delegation)
| Type | Attributes | Proposal | Registry |
|---|---|---|---|
| `agent.spawned` | `child_agent_instance_id` R; `child_agent_definition` Rec; `via_tool_call_id`, `is_async`, `model`, `task_hash`, `shared_context_hashes`, `budget_tokens` O | `gen_ai.invoke_agent.internal` span with `gen_ai.agent.name`; new `gen_ai.agent.instance.id` and `gen_ai.agent.parent.instance.id`; issue #37 `gen_ai.task.requester.*` | `harness.agent.spawned` |
| `agent.returned`, `agent.cancelled` | `child_agent_instance_id` R; `total_tokens`, `total_tool_uses`, `duration_ms`, `model_swapped`, `result_hash`, `status` Rec | span end; usage | `harness.agent.returned` |

Obs.: SubagentStart/SubagentStop (`agent_id`, `agent_type`, `agent_transcript_path`, `last_assistant_message`), OTel `subagent_completed` (`total_tokens`, `total_tool_uses`, `duration_ms`, `is_async`, `model_swapped`). Note: `/compact` spawns a subagent in 2.1.289; compaction is itself a delegation.

### 5.8 VERIFICATION
| Type | Attributes | Proposal | Registry |
|---|---|---|---|
| `verify.requested`, `verify.evidence`, `verify.passed`, `verify.failed`, `verify.abstained` | `claim` or `claim_hash` R; `evaluator` (pytest, build, lint, human, llm_judge, harness_adapter, …) R; `policy`, `threshold` O; `outcome` (passed, failed, abstained, pending) R; `evidence_hashes` Rec; `exit_code`, `tests_total`, `tests_failed` O | new event `gen_ai.verification` (`gen_ai.verification.claim`, `.evaluator`, `.outcome`, `.evidence.refs`); distinct from `gen_ai.evaluation.result`, which scores quality rather than checks a claim | `harness.verify.*` |

Obs.: no harness emits verification. The verification adapter (D-038) derives these from observed verifier invocations; `source_channel=verification_adapter`, `parent_event_id` points at the tool result. A blocked verifier invocation is `verify.abstained`.

### 5.9 STOP
| Type | Attributes | Proposal | Registry |
|---|---|---|---|
| `stop` | `reason` R ∈ success, verified_success, agent_declared_complete, budget_exhausted, timeout, no_progress, policy_stop, human_stop, fatal_error, external_dependency, max_turns, unknown; `declared_by` (agent, harness, human, policy, budget, error) Rec; `verification_present` Rec (derived); `native_reason` Rec | new attribute `gen_ai.agent.stop.reason` on the `invoke_agent` span, distinct from model-level `gen_ai.response.finish_reasons` | `harness.stop` |

Obs.: Stop hook (`last_assistant_message`), SDK `result.terminal_reason`, SessionEnd `reason`.

### 5.10 `unknown`
`native_type` R; `attrs.native` holds the emitter's attributes with content fields removed. Used in v0.1 for the HOOK domain (`hook_registered`, `hook_execution_start/complete` with `hook_event`, `hook_name`, `num_hooks`, `num_success`, `num_blocking`, `total_duration_ms`) and configuration records (`managed_settings_resolved`, `plugin_loaded`, `skill_activated`, `mcp_server_connection`), all of which become v0.2 domains with these fields.

## 6. Components and interfaces

Components (also the component dimension of the failure taxonomy, D-035; SPEC-03 adds `grader` and `third_party` per research 05 §13): `model`, `planner`, `loop`, `context_builder`, `compactor`, `memory`, `retrieval`, `tool`, `mcp`, `permission`, `hook`, `sandbox`, `state`, `delegation`, `verification`, `artifact`, `budget`, `stop`, `environment`, `human`, `external_dependency`, `unknown`.

Each event type has a default (component, counterpart) in `INTERFACES`: e.g. `tool.requested` = (model → tool), `tool.authorized` = (permission → tool), `tool.completed` = (tool → context_builder), `context.compact` = (compactor → context_builder), `agent.spawned` = (delegation → loop), `verify.passed` = (verification → stop). Adapters may override when the harness reports otherwise.

## 7. Content and privacy profile

- Default profile is **structural**: hashes and sizes only. `prompt`, `tool_input`, `tool_output`, `response`, `summary` travel only as PayloadRefs whose bytes stay customer-side.
- Attributes known to identify a person or account are stripped by adapters unless the customer opts in: on Claude Code `user.email`, `user.account_id`, `user.account_uuid`, `user.id`, `organization.id`, `ccr.session.id` (1,014 values stripped from one 11-call run in Proof A).
- Shell commands are reduced to `command_binary`; file paths to hashes.
- SPEC-05 governs redaction, secret detection and retention.

## 8. Cross-channel merge (normative for adapters that read several channels)

Two records describe the same fact only when they share an exact identifier: `tool_call_id` for tool and permission events; `request_id` or `message_id` for model responses; `request_body_id` for model requests; `turn_id` for turn starts; (`turn_id`, `boundary_uuid`) for compactions, with ordinal pairing when one channel lacks both; `child_agent_instance_id` for delegation, with definition-name plus proximity when one channel lacks the instance id. Attributes are unioned with first-non-null wins by channel priority (hooks, then OTel logs, then SDK stream). A merged event lists all channels in `source_channel`. Nothing else may be merged.

## 9. Execution graph

Nodes are events. Edges carry `rel`, `source`, `confidence`, `method`, `evidence`.

| Relation | Source | Method |
|---|---|---|
| `parent_of` | runtime | shared `run_id` or `turn_id` |
| `approved_by`, `blocked_by`, `requires`, `produces` | runtime | shared `tool_call_id` |
| `delegated_to`, `returned_to` | runtime | `agent_instance_id` |
| `loaded_into` | runtime | provenance event in run |
| `verified_by` | normalizer | verification adapter |
| `requested_by` | normalizer (0.95) | latest `model.response` in the agent instance; becomes runtime when the response body lists the `tool_use` id |
| `compacted_from` | normalizer (0.9) | precedes the compaction in the run; refined by `preserved_segment` ids where available |
| `derived_from`, `reads_from`, `writes_to`, `retrieved_from` | content_addressing | hash match between tool output, context item, memory record |
| `caused_by`, `influenced_by`, `likely_caused_by` | detector, statistical_inference, reasoning_model, human_analyst | always with confidence; never from this spec's normalizer |

Edge sources from `runtime`, `normalizer` and `content_addressing` are observed or reconstructed; `detector`, `statistical_inference`, `reasoning_model`, `human_analyst` are inferred (PLAN-11 P3, P4).

## 10. Fidelity levels (per run, computed, displayed)

| Level | Condition |
|---|---|
| G1 | tree only |
| G2 | every tool request is closed by a result or a block (observed edges complete) |
| G3 | G2 and context provenance present; every compaction carries a summary ref and token counts |
| G4 | G3 and a verification evidence chain exists |
| G5 | G4 and inferred edges present |

Replay fidelity R1 to R5 is defined in SPEC-02. Proof A run: G3; runs with verification: G4.

## 11. Coverage matrix (v0.1, observed and documented)

| Domain | Claude Code (Tier B) | Codex CLI (Tier B) | Gemini CLI (Tier B) | Cursor (Tier C) | Tier A instrumentors |
|---|---|---|---|---|---|
| RUN, STOP | full (hooks, SDK result) | full (hooks, rollout) | full (telemetry) | sessionStart/End, stop | full |
| LOOP | derived from model responses | derived | derived | — | native where the framework exposes steps |
| MODEL | full incl. raw bodies via side channel | full (otel) | full (telemetry, `logPrompts` default true) | model name only | full |
| TOOL/MCP | full | full | full | shell, MCP, file hooks | full |
| CONTEXT | compaction full (summary in PostCompact); provenance via InstructionsLoaded | PreCompact/PostCompact | PreCompress (advisory), chat_compression | preCompact (newer builds) | none emit compaction natively; instrumentor must wrap the compactor |
| PERMISSION | full | full (PermissionRequest hook, tool_decision) | tool decisions | shell/MCP decisions | framework-specific (approval interrupts) |
| AGENT | full (hooks + subagent_completed) | SubagentStart/Stop | none | subagent hooks (newer) | handoff/subagent spans |
| VERIFICATION | adapter only | adapter only | adapter only | adapter only | adapter only |

Details and field-level evidence: research 02, 03, 04; SPEC-06 carries the adapter contracts.

## 12. Decision log
- 2026-10-04 Nine domains, 31 types for v0.1 (D-034). HOOK and configuration records preserved as `unknown` pending v0.2.
- 2026-10-04 Proposal names reuse PR #535 for tool decisions and issue #181 for context provenance rather than inventing parallel names.
- 2026-10-04 Iteration opens at model response; unresolved tool requests carry forward (Proof D finding).
- 2026-10-04 `source_name_hash` added to provenance events so instruction files compare across runs (Proof F finding).
- 2026-10-04 OTel `compaction.pre_tokens` kept as native field because it disagrees with the SDK boundary figure.

## 13. Open questions
1. Whether `agent_instance_id` should be proposed as `gen_ai.agent.instance.id` or folded into PR #445's `gen_ai.agent.execution.id`.
2. Semantics of Claude Code OTel `compaction.pre_tokens` vs SDK `compact_boundary.pre_tokens` (5421 vs 32800 observed).
3. Whether `context.build` should exist in v0.1 at all; no emitter observed.
4. How to represent `/compact`'s internal subagent: as delegation (observed) or hidden inside the compaction event.
5. Verification claim classification (did the agent *claim* completion) is out of scope for v0.1 events; decide whether a `claim_asserted` boolean belongs on `stop`.
