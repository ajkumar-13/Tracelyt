# Proof A — Capture a complex Claude Code execution (real run, 4 October 2026)

**Setup.** Claude Code CLI 2.1.289, headless (`claude -p`), model `claude-haiku-4-5-20251001`, isolated project with 22 hook events configured to dump their stdin JSON, OTel exporters set to OTLP/HTTP JSON pointed at a 30-line local receiver, `OTEL_LOG_RAW_API_BODIES=file:` enabled. Task: write `calc.py`, run it, trigger a `ZeroDivisionError`, delegate review to a project-defined `reviewer` subagent, fix, rerun. Then `/compact` on the resumed session.

Fixtures (scrubbed) in `tests/fixtures/claude_code/`: `hooks.jsonl` (26 + 5 events), `stream.jsonl` and `stream_compact.jsonl` (Agent SDK stream), `otlp/` (10 log batches, 9 metric batches, plus compaction batches), `rawbodies/` (request and response bodies plus `index.jsonl`), `transcript/` (session JSONL, subagent JSONL and meta), `stream_json_shapes.json`, `transcript_shapes.json`.

## 1. Channels observed, and what each uniquely provides

| Channel | Observed events | Unique contribution |
|---|---|---|
| **Hooks** (stdin JSON) | SessionStart, InstructionsLoaded, UserPromptSubmit, PreToolUse ×9, PostToolUse ×8, **PostToolUseFailure** ×1, **PermissionRequest** ×3 (first run), SubagentStart, SubagentStop, Stop, SessionEnd, **PreCompact**, **PostCompact** | Context provenance (`InstructionsLoaded.file_path`, `memory_type`, `load_reason`); permission requests with `permission_suggestions`; **full `compact_summary` text in PostCompact**; `last_assistant_message` on Stop and SubagentStop; `agent_transcript_path`; synchronous, can block or rewrite |
| **OTel logs** (OTLP) | `managed_settings_resolved`, `hook_registered` ×22, `plugin_loaded`, `hook_execution_start/complete` ×24, `user_prompt`, `api_request` ×11, `api_request_body`/`api_response_body` ×11, `assistant_response`, `tool_decision` ×9, `tool_result` ×9, `subagent_completed` | Per-request tokens, cost, ttft, `request_id`, `agent.name`, `query_source`; `tool_decision.source` (config/hook/user...); `tool_result.error_type`; `body_ref` pointers to raw bodies; `event.sequence` ordering; `message.uuid` linking to transcript entries |
| **OTel metrics** | `session.count`, `lines_of_code.count`, `cost.usage`, `token.usage`, `code_edit_tool.decision`, `active_time.total` | Fleet aggregates; `query_source` and `agent.name` split subagent cost |
| **Raw bodies** (`file:` side channel) | 11 request + 11 response JSON files with an `index.jsonl` | The exact Messages API payload: `model`, `messages`, `system`, `tools`, `betas`, `thinking` budget, `context_management` edits, `thread.previous_message_id`. This is the replay cassette. |
| **Agent SDK stream** (`stream-json`) | `system/init`, `hook_started/hook_response`, `assistant` text/thinking/tool_use, `user` tool_result, `permission_denied`, `task_started/progress/updated/notification/summary`, `post_turn_summary`, `thinking_tokens`, `rate_limit_event`, `autocompact_state`, `active_goal`, **`compact_boundary`**, `result` | `compact_boundary.compact_metadata`: `trigger`, `pre_tokens`, `post_tokens`, `cumulative_dropped_tokens`, `duration_ms`, `preserved_segment {head_uuid, anchor_uuid, tail_uuid}`, `preserved_messages`; `result` carries `total_cost_usd`, `usage`, `modelUsage`, `permission_denials`, `terminal_reason` |
| **Transcript JSONL** | entry types `user`, `assistant`, `attachment`, `system`, `queue-operation`, `atis-latch`, `last-prompt`, `cost-state`; subagent file plus `.meta.json` | `parentUuid` chain, `isSidechain`, `agentId`, `toolUseResult`, `requestId`, `apiBlockIndex`, `thinkingDurationMs`, `toolDenialKind`; format explicitly unstable |

**No traces were exported** by 2.1.289 with `CLAUDE_CODE_ENHANCED_TELEMETRY_BETA=1` and `OTEL_TRACES_EXPORTER=otlp`. Spans described in the docs as beta are not available in this build or need a flag not yet identified. Logs plus hooks were sufficient to reconstruct the execution.

## 2. Identity and correlation keys that make the graph buildable

- `session_id` (hooks, OTel `session.id`, stream, transcript `sessionId`) is the run.
- `prompt_id` / `prompt.id` scopes one user turn.
- `tool_use_id` joins PreToolUse → PostToolUse(Failure) → OTel `tool_decision` → `tool_result` → transcript `toolUseResult` → raw response body `tool_use` block.
- `agent_id` (hooks) and `agentId` (transcript) identify the subagent instance; `agent.name`/`agent_type` the definition; the subagent's `api_request` events carry `agent.name=reviewer`; the parent's `Task` tool_use_id is the delegation edge.
- `request_id` joins `api_request`, `assistant_response`, `api_response_body`; `request_body_id` joins request and response bodies; `message.uuid` joins OTel events to transcript entries; `thread.previous_message_id` in the request body chains consecutive model calls.
- `event.sequence` gives a monotonic order within the session.
- Compaction: `compact_boundary.uuid` plus `preserved_segment` identify exactly which transcript entries survived.

Conclusion: observed edges (`parent_of`, `requested_by`, `approved_by/blocked_by`, `delegated_to/returned_to`, `produces`) are fully derivable; reconstructed `compacted_from` is derivable from `preserved_segment` plus the summary text; graph fidelity G3 is achievable for Claude Code via hooks plus OTel logs plus the side channel, without the transcript.

## 3. Findings that change the specs

1. **PostCompact exposes the full summary text** (`compact_summary`). The research track assumed summary content was only in the unstable transcript. This makes context-lineage detection (declared-state survival) feasible on Claude Code through a supported interface. SPEC-01 CONTEXT.compact gets a `summary_ref` populated from the hook; SPEC-06 Tier B coverage for compaction becomes "full" on Claude Code.
2. **`compact_boundary` gives pre/post tokens and the preserved segment** without any content. Structural compaction telemetry is available in metadata-only mode.
3. **PII is in every OTel record by default:** `user.email`, `user.account_id`, `user.account_uuid`, `user.id` (device hash), `organization.id`, `ccr.session.id`. Any collector we ship must strip or hash these before egress unless the customer opts in. SPEC-05 redaction rules must name these attributes explicitly.
4. **`tool_decision.source`** distinguishes `config`, hook, and user decisions. Combined with `PermissionRequest.permission_suggestions` this gives a complete permission chain for the PERMISSION domain.
5. **The raw-body side channel is a usable replay cassette** out of the box: full request including `tools` and `system`, full response, chained by `thread.previous_message_id`. R2 fidelity for Claude Code is a file copy, not an engineering project.
6. **`subagent_completed`** reports `total_tokens`, `total_tool_uses`, `duration_ms`, `model_swapped`, `is_async`. Delegation cost attribution needs no inference.
7. **Verification has no signal of its own.** Test runs appear only as `Bash` tool calls with `error_type=ShellError` on failure. The verification adapter (PLAN-12 §4) is required even on the deepest harness.
8. **Headless permission denials are observable** (`permission_denied` in the stream, `PermissionRequest` hook with no answer) and are a realistic source of the "permission storm" pattern in unattended fleets.
9. **Hook registration and execution are themselves telemetry** (`hook_registered`, `hook_execution_*` with durations and blocking counts). Hook events belong in the v0.2 HOOK domain with these fields.

## 4. Gaps remaining on Claude Code

- No spans in this build; iteration boundaries must be derived from `api_request` sequence per `prompt.id`.
- No explicit stop reason beyond `result.terminal_reason` and `SessionEnd.reason` (`other`); per-turn `stop_reason` is inside the raw response body.
- Compaction `trigger` observed only as `manual`; auto-compaction fields assumed identical, unverified.
- OTEL_* variables are not inherited by hook subprocesses; a hook adapter must find the receiver by its own configuration.

## 5. Gate relevance

Proof A target: capture a complex coding-agent execution with the v0.1 model. **Met** for Claude Code at G3 fidelity with the channels above. Normalization into v0.1 (Proof B) proceeds in `src/harness_engine/adapters/claude_code/`.
