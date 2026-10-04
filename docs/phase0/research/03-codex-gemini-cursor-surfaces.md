# Instrumentation field reference: OpenAI Codex CLI, Google Gemini CLI, Cursor (as of 2026-10-04)

## How this was verified

- **Codex:** read from a shallow clone of `openai/codex` at commit `b8dceb0d4f29e49e73daa08f57fcf5181186f354` (2026-10-04).
- **Gemini CLI:** read from a clone of `google-gemini/gemini-cli` at commit `fb972b2f87fe7d5b06d37eac711490162d98de2c` (2026-10-02), package version `0.64.0-nightly.20260929.gd75234cae`.
- **Blocked sites:** developers.openai.com, cursor.com, docs.cursor.com and geminicli.com all returned 403 from the egress proxy. The WebSearch budget was used up.
- **Cursor:** comes only from third-party GitHub sources, mostly empirical captures. The sources are listed in §C.

**Marking used below:**
- ✅ = read in source code or schema
- 📄 = vendor docs inside the repo
- 🔬 = third-party live capture
- ⚠️ = unverified or inferred

Bare paths are clones in the scratchpad: `/tmp/claude-0/-home-user-Tracelyt/759a35a9-2e36-5f3a-a868-84fb22c157ad/scratchpad/{codex,gemini,cursor}`.

---

# A. OpenAI Codex CLI (`openai/codex`)

## A1. Hooks

**Sources:**
- https://github.com/openai/codex/tree/main/codex-rs/hooks/src (`lib.rs`, `types.rs`, `engine/*.rs`, `events/*.rs`)
- Generated JSON Schemas for every input and output: https://github.com/openai/codex/tree/main/codex-rs/hooks/schema/generated (`<event>.command.input.schema.json` / `.output.schema.json`)
- Config structs: `codex-rs/config/src/hook_config.rs`
- `docs/config.md` §"Lifecycle hooks"
- Feature flag `hooks` (`Feature::CodexHooks`) is `Stage::Stable` and `default_enabled: true` (`codex-rs/features/src/lib.rs`).

### Event names

The `HOOK_EVENT_NAMES` constant in `lib.rs` lists 12 events:

```
PreToolUse, PermissionRequest, PostToolUse, PreCompact, PostCompact, SessionStart, SessionEnd, UserPromptSubmit, SubagentStart, SubagentStop, Stop, Interrupt
```

- **Events whose matchers are honoured:** PreToolUse, PermissionRequest, PostToolUse, PreCompact, PostCompact, SessionStart, SessionEnd, SubagentStart, SubagentStop.
- **Events whose matchers are ignored:** UserPromptSubmit, Stop, Interrupt.

### Config format ✅

There are two equivalent shapes, and both can be present in each config layer. Codex warns if one layer uses both.

**1. `hooks.json`** in each config layer's folder (`~/.codex/hooks.json`, project `.codex/hooks.json`, and plugin `hooks/hooks.json`). The struct is `HooksFile { description?, hooks: HookEventsToml }` with `deny_unknown_fields`:

```json
{"description":"…","hooks":{"PreToolUse":[{"matcher":"^Bash$","hooks":[{"type":"command","command":"python3 /tmp/pre.py","timeout":10,"statusMessage":"checking","additionalContextLimit":4096}]}]}}
```

**2. `config.toml` `[hooks]`** (`HooksToml`, the same events flattened plus a `state` map):

```toml
[[hooks.PreToolUse]]
matcher = "^Bash$"
[[hooks.PreToolUse.hooks]]
type = "command"
command = "…"
timeout = 10
[hooks.state."/path/hooks.json:pre_tool_use:0:0"]
enabled = false
trusted_hash = "sha256:…"
```

**Handler types** (`HookHandlerConfig`, tagged by `type`):

| `type` | Fields | Notes |
|---|---|---|
| `command` | `command`, `commandWindows` (alias `command_windows`), `timeout` (seconds), `async` (bool), `statusMessage`, `additionalContextLimit` | |
| `mcp_tool` | `server`, `tool`, `input` (object; must be TOML-representable), `timeout`, `statusMessage` | Not supported for SessionEnd |
| `prompt` | none | Parsed, then **skipped**: "prompt hooks are not supported yet" |
| `agent` | none | Parsed, then **skipped**: "agent hooks are not supported yet" |

**Timeouts** (`normalize_command_hook`): the default is 600 s (minimum 1). For SessionEnd and Interrupt the default is 1 s and the cap is 3 s. `async: true` is forced to run synchronously for SessionEnd.

**Matchers** (`engine/matcher.rs`):
- `""` or `"*"` matches everything.
- A pattern made only of `[A-Za-z0-9_|]` is treated as an exact or `|`-alternation literal.
- Anything else is a Rust regex.

**Tool names in hook payloads** (`core/src/tools/hook_names.rs`):
- The canonical `tool_name` is what goes in stdin. Shell/exec is `Bash`, with `tool_input: {"command": <cmd>}`.
- `apply_patch` has matcher aliases `Write` and `Edit`, and `tool_input: {"command": <patch>}`.
- `spawn_agent` has matcher alias `Agent`.
- MCP tools are `mcp__<server>__<tool>`.
- Any other function tool uses its flattened name and its raw arguments.

**Plugin hook env:** `PLUGIN_ROOT`, `CLAUDE_PLUGIN_ROOT`, `CLAUDE_PLUGIN_DATA`.

**Sources and trust:**
- `HookSource` values: `system|user|project|mdm|session_flags|plugin|cloud_requirements|cloud_managed_config|legacy_managed_config_file|legacy_managed_config_mdm|unknown`.
- Non-managed hooks only run if `trust_status` is `Trusted` (hash stored in `[hooks.state."<key>"].trusted_hash`) or `bypass_hook_trust` is set.
- `HookTrustStatus` values: `managed|untrusted|trusted|modified`.

**`allow_managed_hooks_only`** (📄 `docs/config.md`; ✅ `config_requirements.rs`):
- A top-level key in **`requirements.toml` only**. Putting it in `config.toml` has no effect.
- When true, user, project and session hooks are ignored. Managed hooks are kept: requirements-level `[hooks]` (`ManagedHooksRequirementsToml { managed_dir, windows_managed_dir, <events> }`) and the managed config layers.

**Legacy `notify`:** `config.toml` `notify = [argv…]` runs a program with the JSON `{"type":"agent-turn-complete","thread-id","turn-id","cwd","client"?,"input-messages":[…],"last-assistant-message"}` as its final argv argument (`hooks/src/legacy_notify.rs`). It is fire-and-forget.

### Common stdin fields (from the generated schemas) ✅

| Field | Type | Present in |
|---|---|---|
| `session_id` | string (thread id) | all |
| `transcript_path` | string \| null | all |
| `cwd` | string | all |
| `hook_event_name` | const | all |
| `model` | string | all except SessionEnd |
| `permission_mode` | `default\|acceptEdits\|plan\|dontAsk\|bypassPermissions` | all except Pre/PostCompact and SessionEnd |
| `turn_id` | string ("Codex extension") | all turn-scoped events (not SessionStart or SessionEnd) |
| `agent_id`, `agent_type` | string, optional | PreToolUse, PermissionRequest, PostToolUse, Pre/PostCompact, UserPromptSubmit; **required** on SubagentStart/Stop |

### Per-event fields ✅

| Event | Extra input fields | Output fields and decision semantics |
|---|---|---|
| **SessionStart** | `source`: `startup\|resume\|clear\|compact\|fork` | `continue`, `stopReason`, `suppressOutput`, `systemMessage`, `hookSpecificOutput{hookEventName,additionalContext}` |
| **UserPromptSubmit** | `prompt` | Universal fields plus `decision:"block"` with `reason` (required), and `hookSpecificOutput.additionalContext` |
| **PreToolUse** | `tool_name`, `tool_input` (any), `tool_use_id` | `decision: approve\|block` with `reason`, and `hookSpecificOutput{permissionDecision: allow\|deny\|ask, permissionDecisionReason, updatedInput, additionalContext}`. See rules 1–5 below. |
| **PermissionRequest** | `tool_name`, `tool_input` (no `tool_use_id`) | `hookSpecificOutput.decision{behavior: allow\|deny, message}`. See rules 6–8 below. |
| **PostToolUse** | `tool_name`, `tool_input`, `tool_response` (any), `tool_use_id` | `decision:"block"` with `reason`, `continue`/`stopReason`, `hookSpecificOutput{additionalContext, updatedMCPToolOutput}`. See rules 9–11 below. |
| **PreCompact** | `trigger`: `manual\|auto` | `continue`, `stopReason`, `suppressOutput`, `systemMessage` (`PreCompactOutcome{should_stop, stop_reason}`) |
| **PostCompact** | `trigger`: `manual\|auto` | Same as PreCompact |
| **SubagentStart** | (`agent_id` and `agent_type` required) | `hookSpecificOutput.additionalContext` plus universal fields |
| **SubagentStop** | `agent_transcript_path` (str\|null), `last_assistant_message`, `stop_hook_active` | `decision:"block"` with `reason` keeps the subagent going |
| **Stop** | `last_assistant_message` (str\|null), `stop_hook_active` (bool) | `decision:"block"` with `reason` (required) feeds the reason back as a continuation prompt (`continuation_fragments`); `continue:false` stops |
| **SessionEnd** | `reason`: const `"other"` | No output schema. Fire-and-forget, 1–3 s |
| **Interrupt** | (has `turn_id`, `permission_mode`) | `systemMessage` only |

**PreToolUse decision rules:**
1. `permissionDecision:"deny"` requires a non-empty `permissionDecisionReason`.
2. `permissionDecision:"allow"` is **only** accepted together with `updatedInput` (input rewrite).
3. A bare `allow`, `ask`, `decision:"approve"`, `continue:false`, `stopReason` or `suppressOutput` is rejected as "unsupported" and **fails open**.
4. Exit code 2 with a stderr reason blocks.
5. The block message to the model is `"Command blocked by PreToolUse hook: {reason}. Command: {cmd}"`.

**PermissionRequest rules:**
6. It runs **before** the guardian/user approval UI. Folding: any deny wins, otherwise the last allow wins, otherwise there is no verdict.
7. `updatedInput`, `updatedPermissions`, `interrupt:true`, `continue:false`, `stopReason` and `suppressOutput` are rejected.
8. Exit code 2 with stderr means deny.

**PostToolUse rules:**
9. `block` turns the tool result into an error for the model, carrying the reason.
10. Feedback text **replaces the model-visible output** (`PostToolUseFeedbackOutput`). Exit code 2 with stderr gives feedback.
11. `updatedMCPToolOutput` and `suppressOutput` are rejected.

**Exit codes:**
- 0 means stdout is parsed as JSON if it looks like JSON.
- 2 means block, using stderr as the reason (PreToolUse, PermissionRequest, PostToolUse, Stop, UserPromptSubmit).
- Any other code is a non-blocking error entry. Hook output above 2,500 tokens is spilled (`DEFAULT_HOOK_OUTPUT_TOKEN_LIMIT`).

### Hook run observability ✅

Each run emits `HookStartedEvent` and `HookCompletedEvent` `{turn_id?, run: HookRunSummary}`. `HookRunSummary` fields:
- `id`, `event_name`, `handler_type` (`command|mcp_tool|prompt|agent`), `execution_mode` (`sync|async`), `scope` (`thread|turn`)
- `source_path`, `source`, `display_order`
- `status` (`running|completed|failed|blocked|stopped`), `status_message`
- `started_at`, `completed_at`, `duration_ms`
- `entries[{kind: warning|stop|feedback|context|error, text}]`

These events reach app-server clients as `hook/started` and `hook/completed`. They are **not** written to the rollout. Metrics: `codex.hooks.run`, `codex.hooks.run.duration_ms`.

### Known hook gaps (GitHub issues, open unless noted)

- #49736 PreToolUse is not invoked for `spawn_agent`, so a deny cannot block a sub-agent spawn.
- #50304 No terminal hook fires when compaction fails or is cancelled after PreCompact.
- #46765 An interrupted synchronous PostToolUse emits `hook/started` without `hook/completed`.
- #45293 PreToolUse is silently skipped (fails open) when the cwd no longer exists.
- #38850 Code Mode (`functions.exec`) nested shell results do not fire PostToolUse.
- #42511 Cancelled Code Mode nested calls leave PreToolUse stuck at "Running".
- #47925 Hooks from Agent Plugins 1.0 plugins are never loaded.
- #41979 Request for opt-in fail-closed PreToolUse.
- #43184 Request for one quiescence-aware terminal event per tool call.
- #46337 / #43003 Requests for PreCompact to replace history (#46678 is closed).

## A2. OpenTelemetry

**Sources:**
- https://github.com/openai/codex/blob/main/codex-rs/otel/README.md
- `otel/src/events/session_telemetry.rs`, `otel/src/events/shared.rs`, `otel/src/tool_result.rs`, `agent_response.rs`, `guardian_assessment.rs`, `skill_invocation.rs`, `metrics/names.rs`
- Config: `codex-rs/config/src/types.rs` (`OtelConfigToml`)

### `config.toml` `[otel]` ✅

| Key | Default | Notes |
|---|---|---|
| `environment` | `"dev"` | Resource env tag |
| `exporter` (logs) | `none` | `none`, `statsig`, `{ otlp-http = {endpoint, headers{}, protocol = "binary"\|"json", tls{ca-certificate, client-certificate, client-private-key}} }`, or `{ otlp-grpc = {endpoint, headers, tls} }` |
| `trace_exporter` | `none` | Same options |
| `metrics_exporter` | **`statsig`** | Same options. **By default metrics go to OpenAI's Statsig**, so set this explicitly. |
| `log_user_prompt` | `false` | When false, `codex.user_prompt.prompt` = `"[REDACTED]"` |
| `log_agent_responses` | `false` | Enables `codex.agent_response` (text capped at 65,536 bytes) |
| `log_guardian_assessments` | `false` | Enables `codex.guardian_assessment` |
| `tool_result.max_bytes` | `2048` | Byte cap on `codex.tool_result.output` in logs |
| `span_attributes` | `{}` | Added to every exported span |
| `tracestate.<member>.<k>=<v>` | `{}` | Upserted into W3C tracestate |

### Metadata on every log event ✅

`event.name`, `event.timestamp`, `conversation.id`, `app.version`, `auth_mode`, `originator`, `user.account_id`, `user.email`, `terminal.type`, `model`, `slug`.

Trace-safe events carry the same set **minus `user.account_id` and `user.email`**. Logs and traces use separate targets (`OTEL_LOG_ONLY_TARGET` and `OTEL_TRACE_SAFE_TARGET`). Several events split fields between the log and trace variants, as noted below.

### Log and trace events ✅

| `event.name` | Fields |
|---|---|
| `codex.conversation_starts` | `provider_name`, `auth.env_openai_api_key_present`, `auth.env_codex_api_key_present`, `auth.env_codex_api_key_enabled`, `auth.env_provider_key_name`, `auth.env_provider_key_present`, `auth.env_refresh_token_url_override_present`, `reasoning_effort`, `reasoning_summary`, `context_window`, `auto_compact_token_limit`, `approval_policy`, `sandbox_policy`. Log only: `mcp_servers` (comma-joined). Trace only: `mcp_server_count` |
| `codex.api_request` | `duration_ms`, `http.response.status_code`, `error.message`, `attempt`, `auth.header_attached`, `auth.header_name`, `auth.retry_after_unauthorized`, `auth.recovery_mode`, `auth.recovery_phase`, `endpoint`, the `auth.env_*` fields above, `auth.request_id`, `auth.cf_ray`, `auth.error`, `auth.error_code`, `auth.agent_id`, `auth.task_id` |
| `codex.websocket_connect` | Same as `api_request` plus `success`, `auth.connection_reused` |
| `codex.websocket_request` | `duration_ms`, `success`, `error.message`, `auth.env_*`, `auth.connection_reused`, `auth.agent_id`, `auth.task_id` |
| `codex.sse_event` | `event.kind` (SSE type, e.g. `response.output_item.done`), `duration_ms`, `error.message`. On completion (`event.kind=response.completed`): `input_token_count`, `output_token_count`, `cached_token_count`, `cache_write_token_count`, `reasoning_token_count`, `tool_token_count` (**bug: set to `usage.total_tokens`**, issue #40208), `ttft_ms`, `service_tier`, `model_reasoning_effort` |
| `codex.user_prompt` | Log: `prompt_length`, `prompt` (redacted unless `log_user_prompt`). Trace: `prompt_length`, `text_input_count`, `image_input_count`, `local_image_input_count` |
| `codex.tool_decision` (log only) | `tool_name`, `tool_namespace`, `call_id`, `decision` (opaque string from `ReviewDecision`: approved, approved_execpolicy_amendment, approved_for_session, approved_mcp_policy_amendment, network_policy_amendment, denied, timed_out), `source` (`AutomatedReviewer\|Config\|User`, optional) |
| `codex.sandbox_outcome` | `tool_name`, `call_id`, `outcome`, `initial_duration_ms`, `escalated_duration_ms` |
| `codex.tool_result` | Common: `tool_result_seq`, `tool_name`, `tool_namespace`, `call_id`, `product_sku`, `duration_ms`, `success`, `output_truncated`. Log only: `agent_name`, `arguments` (full), `output` (≤ `tool_result.max_bytes`), `mcp_server`, `mcp_server_origin`. Trace only: `arguments_length`, `output_length`, `output_line_count`, `tool_origin` (`builtin\|mcp`), `mcp_tool` (bool) |
| `codex.turn_ttft` | `duration_ms` |
| `codex.turn_cost` (log only) | `turn.id`, `usage.estimated_usd`, `turn.interrupted`, `speed`, `reasoning_effort`. Emitted only by the **app-server** `turn_cost_worker`, which polls backend `analytics/codex/turn-costs`. ⚠️ Not emitted by `codex exec` |
| `codex.startup_phase` | `startup.phase`, `startup.status`, `duration_ms` |
| `codex.auth_recovery` | `auth.mode`, `auth.step`, `auth.outcome`, `auth.request_id`, `auth.cf_ray`, `auth.error`, `auth.error_code`, `auth.recovery_reason`, `auth.state_changed` |
| `codex.plugin_install_elicitation_sent`, `codex.plugin_install_suggestion` | Plugin ids and types |
| `codex.skill_invocation` | `conversation.id`, `turn.id`, `user.id`, `user.account_id`, `skill.name`, `skill.scope`, `skill.plugin_id`, `skill.invocation_type` (`explicit\|implicit`), `model`, `app.version`, `originator`, `auth_mode` |
| `codex.agent_response` (opt-in) | `agent.type` (`main\|subagent`), `turn.id`, `item.id`, `parent.conversation.id`, `parent.turn.id`, `root.turn.id`, `initiating.agent.path`, `response`, `response_length`, `response_truncated`. Final-answer messages only |
| `codex.guardian_assessment` (opt-in) | `review.id`, `turn.id`, `item.id`, `status`, `outcome` (`allow\|deny`, or absent on error/timeout), `risk_level`, `user_authorization`, `started_at_ms`, `completed_at_ms`, `rationale`, `rationale_length`, `rationale_truncated` |

### Spans ✅

**Root and turn spans:**
- `session_loop`, `session_init` and its children, `thread_spawn`.
- `turn` (otel.name = the task span name, e.g. `session_task.turn`) with `thread.id`, `turn.id`, `model`, `codex.turn.reasoning_effort`, and `codex.turn.token_usage.{input_tokens, cached_input_tokens, cache_write_input_tokens, non_cached_input_tokens, output_tokens, reasoning_output_tokens, total_tokens}`.
- `session_task.run`, `run_turn`, `run_turn.prepare_sampling_request_input`, `run_turn.collect_post_sampling_state`, `stream_request`, `receiving_stream`.

**Model response span:** `handle_responses`, with `otel.name` set to the response type (`created|completed|function_call|message_from_<role>|reasoning|compaction|…`), `tool_name`, `from`, `codex.request.reasoning_effort`, `gen_ai.usage.input_tokens`, `gen_ai.usage.cache_read.input_tokens`, `gen_ai.usage.cache_write.input_tokens`, `gen_ai.usage.output_tokens`, `codex.usage.reasoning_output_tokens`, `codex.usage.total_tokens`.

**MCP call span:** `mcp.tools.call` (kind client) with `rpc.system=jsonrpc`, `rpc.method=tools/call`, `mcp.server.name`, `mcp.server.origin`, `mcp.transport`, `mcp.connector.id`, `mcp.connector.name`, `tool.name`, `tool.call_id`, `conversation.id`, `session.id`, `turn.id`, `server.address`, `server.port`, `codex.mcp.target.id`, `codex.mcp.server_user_flow.triggered`, `error.type`, `codex.mcp.error.code`. A separate `mcp.http.request` span also exists.

**Other spans:** `agents_md.discover`, `agents_md.load` (field `max_total`), `agents_md.refresh`, `mcp.runtime.*`, `turn_context.build`, `world_state.build`, `shell_snapshot`, `app_server.request`.

### Metrics (`otel/src/metrics/names.rs`) ✅

- **API, SSE and WebSocket:** `codex.api_request`, `codex.api_request.duration_ms` (tags `status`, `success`); `codex.sse_event`, `codex.sse_event.duration_ms` (`kind`, `success`); `codex.websocket.request`, `codex.websocket.request.duration_ms`, `codex.websocket.event`, `codex.websocket.event.duration_ms`, `codex.websocket.continuation` (`mode`, `phase`, `reason`).
- **Responses API timing:** `codex.responses_api_overhead.duration_ms`, `codex.responses_api_inference_time.duration_ms`, `codex.responses_api_engine_{iapi,service}_{ttft,tbt}.duration_ms`.
- **Turn:** `codex.turn.e2e_duration_ms`, `codex.turn.ttft.duration_ms`, `codex.turn.ttfm.duration_ms`, `codex.turn.network_proxy`, `codex.turn.memory`, `codex.turn.tool.call`, `codex.turn.token_usage` (histogram, `token_type`), `codex.turn.cost_microusd` (tags `turn.id`, `conversation.id`, `turn.interrupted`, `speed`, `reasoning_effort`), `codex.turn.unified_exec.running_processes`.
- **Tools:** `codex.tool.call`, `codex.tool.call.duration_ms` (tags `tool`, `success`, `product_sku`), `codex.tool.unified_exec` (`tty`).
- **Multi-agent:** `codex.multi_agent.spawn.failure`, `codex.multi_agent.spawn.phase.duration_ms`.
- **Guardian:** `codex.guardian.review`, `codex.guardian.review.duration_ms`, `codex.guardian.review.ttft.duration_ms`, `codex.guardian.review.token_usage`.
- **Goals:** `codex.goal.{created,resumed,completed,budget_limited,usage_limited,blocked,token_count,duration_s}`.
- **Hooks:** `codex.hooks.run`, `codex.hooks.run.duration_ms`.
- **Thread:** `codex.thread.started`, `codex.thread.skills.{enabled_total,kept_total,description_truncated_chars,truncated}`, `codex.thread.tools.{namespaces_total,fragment_bytes}`.
- **Other:** `codex.startup.phase.duration_ms`, `codex.startup_prewarm.*`, `codex.process.start`, `codex.artifact.operation.*`, `codex.plugins.*`, `exec_server_client_requests_total`.

### Trace propagation ✅ (`otel/src/trace_context.rs`)

- **Inbound:** env `TRACEPARENT` and `TRACESTATE` set the parent context. App-server JSON-RPC requests carry an optional `trace: {traceparent, tracestate}` (`app-server-protocol/src/rpc.rs`).
- **Outbound:** injected into MCP requests (`params._meta.traceparent` / `tracestate`, `rmcp-client/src/trace_context.rs`), the exec-server, code-mode gRPC, and Responses WebSocket client metadata (`ws_request_header_traceparent`).

### Known OTel gaps

- #12913 (closed via #13083) said `codex exec` emitted no metrics and `codex mcp-server` emitted no telemetry. **#33668 (open):** `codex exec` still does not export the `codex.turn.token_usage` metric. Tokens are only available as log and span attributes.
- #40208 `tool_token_count` reports total tokens (confirmed in source).
- #47192 Turn spans close with status `UNSET` whatever the outcome. There is no `codex.turn.outcome`.
- #37317 Per-event `handle_responses` spans make up about 49% of trace volume.
- #30552 Invalid inherited `OTEL_*` env crashes app-server startup.
- Compaction analytics (`CompactionAnalyticsDetails{active_context_tokens_before, compaction_summary_tokens, cached_input_tokens, cache_write_input_tokens, …}`) go only to OpenAI's internal analytics (`codex_compaction_event`). **They are not exported to user OTel.**

## A3. Session rollout files and SDK events

### Rollout files ✅

**Location:** `~/.codex/sessions/YYYY/MM/DD/rollout-<timestamp>-<thread_id>.jsonl`, or `…_<rollout_id>.jsonl` after `thread/revert`. Files may be compressed as **`.jsonl.zst`** (`rollout/src/compression.rs`, `RolloutLineReader` reads both).

**Line envelope** (`history/src/lib.rs` `RolloutLine`): `{"timestamp", "ordinal"?, "type": <snake_case>, "payload": …}`. Entry types (`history/src/rollout_payload.rs`):

| `type` | Payload |
|---|---|
| `session_meta` | `SessionMeta` plus `git`: `creator_user_id`, `creator_account_id`, `session_id` (root thread id), `id`, `forked_from_id`, `forked_from_ordinal_exclusive`, `parent_thread_id`, `timestamp`, `cwd`, `runtime_workspace_roots`, `originator`, `cli_version`, `source`, `thread_source`, `agent_nickname`, `agent_role` (alias `agent_type`), `agent_path`, `model_provider`, `base_instructions`, `dynamic_tools`, `selected_capability_roots`, `memory_mode`, `history_mode`, `history_base`, `subagent_history_start_ordinal`, `multi_agent_version`, `context_window`, … |
| `turn_context` | `turn_id`, `root_turn_id`, `disabled_plugin_ids`, `cwd`, `workspace_roots`, `current_date`, `timezone`, `approval_policy`, `approvals_reviewer`, `sandbox_policy`, `permission_profile`, `active_permission_profile`, `network`, `file_system_sandbox_policy`, `model`, `comp_hash`, `personality`, `collaboration_mode`, `multi_agent_mode`, `realtime_active`, `effort`, `summary`, … |
| `response_item` | Raw Responses API item plus optional `metadata`. Persisted kinds: message, agent_message, reasoning, local_shell_call, function_call/_output, custom_tool_call/_output, tool_search_call/_output, web_search_call, image_generation_call, configuration_update, compaction, context_compaction, additional_tools. **AGENTS.md content appears as a user-role message starting with `# AGENTS.md instructions for <dir>` and wrapped in `<INSTRUCTIONS>…</INSTRUCTIONS>`** (`core/src/context/user_instructions.rs`). |
| `token_usage_record` | `thread_id`, `turn_id`, `session_id`, `root_turn_id`, `response_id`, `usage`, `turn_token_usage`, `thread_token_usage`. Each `TokenUsage` is `{input_tokens, cached_input_tokens, cache_write_input_tokens, output_tokens, reasoning_output_tokens, total_tokens}`. |
| `compacted` | `message` (**summary text**), `replacement_history`, `guardian_history`, `retained_context`, `mcp_resource_origins`, `window_number`, `first_window_id`, `previous_window_id`, `window_id`, `compaction_response_id`, `latest_token_usage_record`, `resume_metadata` |
| `event_msg` | Filtered `EventMsg` (see the next table) |
| `inter_agent_communication`, `inter_agent_communication_metadata{trigger_turn}`, `world_state`, `retained_context`, `security_risk_score`, `realtime_item` | Multi-agent, state and realtime items |

**Which `event_msg` types are persisted** (`rollout/src/policy.rs`):

| Rule | Event types |
|---|---|
| Always | `token_count` (`{info:{total_token_usage,last_token_usage,model_context_window}, rate_limits}`), `turn_started` (`turn_id`, `root_turn_id`, `trace_id`, `started_at`, `model_context_window`, `collaboration_mode_kind`), `turn_complete` (`turn_id`, `last_agent_message`, `error`, `started_at`, `completed_at`, `duration_ms`, `time_to_first_token_ms`), `turn_aborted` (`reason`: `interrupted\|replaced\|review_ended\|budget_limited`, plus timing), `thread_goal_updated`, `thread_rolled_back`, `thread_settings_applied` |
| Legacy history mode only | `user_message`, `agent_message`, `agent_reasoning`, `agent_reasoning_raw_content`, `patch_apply_end`, `context_compacted`, `mcp_tool_call_end`, `web_search_end`, `image_generation_end`, `sub_agent_activity`, `entered_review_mode`, `exited_review_mode` |
| Paginated history mode | `item_completed` for everything. Command output is truncated to 64 KiB and MCP results to 64 KiB. |
| **Never persisted** | Approvals (`exec_approval_request`, `apply_patch_approval_request`, `request_permissions`), `guardian_assessment`, `exec_command_begin/end`, `mcp_tool_call_begin`, hook started/completed, `turn_diff`, `collab_*` begin/end, deltas, `raw_response_*`, errors and warnings |

### Raw request and response bodies ✅

With env **`CODEX_ROLLOUT_TRACE_ROOT=<dir>`** set, Codex writes a local bundle (`rollout-trace/README.md`):
- `manifest.json` (trace_id, rollout_id, root_thread_id)
- `trace.jsonl` containing raw events: `RolloutStarted`, `RolloutEnded`, `ThreadStarted`, `ThreadEnded`, `CodexTurnStarted`, `CodexTurnEnded`, `InferenceStarted{inference_call_id, thread_id, codex_turn_id, model, provider_name, request_payload}`, `InferenceCompleted{response_id, upstream_request_id, response_payload}`, `InferenceFailed`, `InferenceCancelled`, `ToolCallStarted`, `McpToolCallCorrelationAssigned`, `ToolCallRuntimeStarted`, `ToolCallRuntimeEnded`, `ToolCallEnded`, `CodeCellStarted`, `CodeCellInitialResponse`, `CodeCellEnded`, `CompactionRequestStarted{compaction_id, model, request_payload}`, `CompactionRequestCompleted{response_payload}`, `CompactionRequestFailed`, `CompactionInstalled{checkpoint_payload}`, `AgentResultObserved`, `ProtocolEventObserved`
- `payloads/*.json` holding the full request and response bodies

### `codex exec --json` and the TS SDK (`runStreamed`) ✅

Sources: `sdk/typescript/src/events.ts`, `items.ts`, `codex-rs/exec/src/exec_events.rs`.

**Events:**
- `thread.started{thread_id}`
- `turn.started{}`
- `turn.completed{usage:{input_tokens, cached_input_tokens, cache_write_input_tokens, output_tokens, reasoning_output_tokens}}`
- `turn.failed{error:{message}}`
- `item.started`, `item.updated`, `item.completed` `{item}`
- `error{message}`

**Item types:**
- `agent_message{id,text}`, `reasoning{id,text}`
- `command_execution{id,command,aggregated_output,exit_code?,status: in_progress|completed|failed|declined}` (the TS type omits `declined`)
- `file_change{id,changes[{path,kind:add|delete|update}],status}`
- `mcp_tool_call{id,server,tool,arguments,result?{content,structured_content,_meta},error?{message},status}`
- `web_search{id,query}`, `todo_list{id,items[{text,completed}]}`, `error{id,message}`
- Rust also emits `collab_tool_call{tool: spawn_agent|send_input|wait|close_agent, sender_thread_id, receiver_thread_ids, prompt, agents_states{id:{status,message}}, status}`, which is **missing from the TS SDK types**.

This stream carries no model name, stop reason, approval events or cost.

## A4. App-server JSON-RPC (alternative capture surface) ✅

Source: `codex-rs/app-server-protocol/src/protocol/common.rs` and `v2/*.rs`. Start it with `codex app-server`. There is **no `codex mcp-server` subcommand** in the current CLI enum.

### Notifications

| Area | Methods |
|---|---|
| Thread | `thread/started`, `thread/status/changed`, `thread/archived`, `thread/deleted`, `thread/unarchived`, `thread/closed`, `thread/reverted`, `thread/name/updated`, `thread/goal/updated`, `thread/goal/cleared`, `thread/queue/changed`, `thread/settings/updated`, `thread/environment/{connected,disconnected}` |
| Tokens | `thread/tokenUsage/updated{threadId, turnId, tokenUsage:{total, last: TokenUsageBreakdown{totalTokens, inputTokens, cachedInputTokens, cacheWriteInputTokens, outputTokens, reasoningOutputTokens}, modelContextWindow}}` |
| Turn | `turn/started` and `turn/completed` `{threadId, turn:{id, items, itemsView, status: completed\|interrupted\|failed\|inProgress, error, startedAt, completedAt, durationMs}}`; `turn/diff/updated{threadId, turnId, diff}` (unified diff); `turn/plan/updated`; `turn/moderationMetadata` |
| Hooks | `hook/started`, `hook/completed` `{threadId, turnId?, run: HookRunSummary}` |
| Items | `item/started{item, threadId, turnId, startedAtMs}`, `item/completed{item, threadId, turnId, completedAtMs}` |
| Deltas | `item/agentMessage/delta`, `item/plan/delta`, `item/reasoning/{summaryTextDelta,summaryPartAdded,textDelta}`, `item/commandExecution/outputDelta`, `item/commandExecution/terminalInteraction`, `item/fileChange/{outputDelta,patchUpdated}`, `item/mcpToolCall/progress` |
| Auto-review | `item/autoApprovalReview/started`, `item/autoApprovalReview/completed{reviewId, targetItemId, decisionSource, review, action, startedAtMs, completedAtMs}`, `autoApprovalReview/strictReviewRequired` |
| Approvals | `serverRequest/resolved{threadId, requestId}` |
| Compaction | `thread/compacted{threadId, turnId}` |
| Model | `model/rerouted`, `model/verification`, `model/safetyBuffering/updated` |
| Raw (opt-in) | `rawResponseItem/completed{threadId, turnId, item: ResponseItem}` and `rawResponse/completed{threadId, turnId, responseId, usage, usageMetadata{amount, metadata}}`. Enabled with `thread/start.experimentalRawEvents`. |
| Other | `mcpServer/startupStatus/updated`, `account/rateLimits/updated`, `error`, `warning`, `configWarning`, `deprecationNotice`, … |

### `ThreadItem` variants (v2 `item.rs`)

- `userMessage`, `hookPrompt`, `agentMessage{text, phase, memoryCitation, delivery, questions}`, `functionCallOutput`, `plan`, `reasoning{summary[], content[]}`
- `commandExecution{sandboxType, modelContext, command, cwd, processId, source, status, commandActions, aggregatedOutput, exitCode, durationMs}`
- `fileChange{changes, status}`
- `mcpToolCall{server, tool, status, arguments, appContext, pluginId, readOnlyHint, result, error, durationMs}`
- `dynamicToolCall`
- `collabAgentToolCall{tool, status, senderThreadId, receiverThreadIds, prompt, model, reasoningEffort, agentsStates}`
- `subAgentActivity{kind, agentThreadId, agentPath}`
- `webSearch`, `imageView`, `sleep`, `imageGeneration`, `enteredReviewMode`, `exitedReviewMode`, `contextCompaction{id}`

### Server requests (approval surface)

- `item/commandExecution/requestApproval{kind, threadId, turnId, itemId, startedAtMs, approvalId, environmentId, reason, networkApprovalContext, command, cwd, commandActions, additionalPermissions, proposedExecpolicyAmendment, proposedNetworkPolicyAmendments, availableDecisions}`. Responses: `accept|acceptForSession|acceptWithExecpolicyAmendment|…|decline|cancel`.
- `item/fileChange/requestApproval{threadId, turnId, itemId, startedAtMs, reason, grantRoot}`
- `item/permissions/requestApproval{…, permissions}`
- `item/tool/requestUserInput`, `mcpServer/elicitation/request`, `item/tool/call` (dynamic tools)
- Legacy v1: `applyPatchApproval`, `execCommandApproval`

## A5. Approvals and sandbox ✅

**Approval policy** (`AskForApproval`, kebab-case): `untrusted`, `on-request` (default; alias `on-failure`), `granular{sandbox_approval, rules, skill_approval, request_permissions, mcp_elicitations}`, `never`.

**Approvals reviewer:** `user` (default) or `auto_review` (alias `guardian_subagent`).

**Sandbox mode:** `read-only` (default), `workspace-write`, `danger-full-access`. `NetworkAccess` is `restricted|enabled`. Requirements can constrain `allowed_approval_policies`, `allowed_sandbox_modes` and `allowed_approvals_reviewers`.

**Where approval decisions surface:**
- OTel `codex.tool_decision` (decision and `source` = User, Config or AutomatedReviewer).
- `codex.sandbox_outcome`.
- `codex.guardian_assessment` (opt-in).
- App-server approval requests and `serverRequest/resolved`, plus auto-review notifications.
- The PermissionRequest hook.
- **Not in rollout files.**

## A6. Subagents, compaction, and what Codex does not expose

**Subagents:**
- Tools are `spawn_agent`, `send_input`, `wait`, `close_agent`.
- Each child is its own thread with its own rollout file. The child's `session_meta` has `parent_thread_id`, `agent_nickname`, `agent_role` and `agent_path`, and `turn_context.root_turn_id` is set.
- Hooks: SubagentStart and SubagentStop (internal and system subagents skip start hooks). Child turns run SubagentStop instead of Stop (`core/src/hook_runtime.rs`).
- OTel: `codex.agent_response` lineage fields, and the `codex.multi_agent.spawn.*` metrics.

**Compaction:**
- Hooks give only `trigger` (`manual|auto`) plus common fields. There are **no token counts and no summary content in hooks**.
- The app-server `thread/compacted` carries only `{threadId, turnId}`.
- The **summary text** is in the rollout `compacted.message`. Tokens before and after can be inferred from the surrounding `token_count` and `token_usage_record` entries (`compacted.latest_token_usage_record`).
- Full compaction request and response bodies are only available via `CODEX_ROLLOUT_TRACE_ROOT`.

**Not observable:**
- No turn-level outcome status on spans.
- Stop reason only as TurnAborted `reason` or `turn.failed`.
- No explicit "rules files loaded" event: AGENTS.md shows up as `agents_md.load` spans plus the injected message in the rollout.
- No test or verification semantics: tests are just shell commands.
- Cost is only via the app-server worker.
- Approvals are not persisted to rollouts.
- `codex exec` has no OTLP token metric (#33668).

---

# B. Google Gemini CLI (`google-gemini/gemini-cli`)

**Sources:**
- `docs/cli/telemetry.md` 📄: https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/telemetry.md
- `docs/hooks/reference.md` 📄: https://github.com/google-gemini/gemini-cli/blob/main/docs/hooks/reference.md
- Source ✅: `packages/core/src/telemetry/{types.ts, loggers.ts, metrics.ts, trace.ts, sdk.ts, telemetryAttributes.ts, constants.ts, billingEvents.ts}` and `packages/core/src/hooks/{types.ts, hookTranslator.ts, hookRunner.ts}`

## B1. Telemetry settings (`settings.json` → `telemetry`) 📄 ✅

| Setting | Env var | Default | Notes |
|---|---|---|---|
| `enabled` | `GEMINI_TELEMETRY_ENABLED` | false | |
| `traces` | `GEMINI_TELEMETRY_TRACES_ENABLED` | false | Detailed span attributes and payloads |
| `target` | `GEMINI_TELEMETRY_TARGET` | `local` | `gcp` or `local` |
| `otlpEndpoint` | `GEMINI_TELEMETRY_OTLP_ENDPOINT` | `http://localhost:4317` | |
| `otlpProtocol` | `GEMINI_TELEMETRY_OTLP_PROTOCOL` | `grpc` | `grpc` or `http` |
| `outfile` | `GEMINI_TELEMETRY_OUTFILE` | | Overrides the endpoint |
| `logPrompts` | `GEMINI_TELEMETRY_LOG_PROMPTS` | **true** | |
| `useCollector` | `GEMINI_TELEMETRY_USE_COLLECTOR` | false | |
| `useCliAuth` | `GEMINI_TELEMETRY_USE_CLI_AUTH` | false | GCP only |

Also: `GEMINI_CLI_SURFACE` (User-Agent tag), and `OTLP_GOOGLE_CLOUD_PROJECT` / `GOOGLE_CLOUD_PROJECT`.

**Resource attributes:** `service.name=gemini-cli`, `service.version=process.version` (⚠️ the Node version, not the CLI version), `session.id`.

**Common attributes on every log** (`getCommonAttributes`): `session.id`, `installation.id`, `interactive`, `user.email` (if available), `auth_type`, `experiments.ids`. ⚠️ The docs claim `active_approval_mode` is a common attribute. **It is not in the source.**

**Payload gating:**
- `function_args`, `prompt`, `request_text`, `response_text`, `hook_input`, `hook_output`, `stdout` and `stderr` need `logPrompts`.
- `gen_ai.input.messages`, `gen_ai.output.messages` and span input/output need **both** `traces` **and** `logPrompts`.
- Span attributes are truncated to 10,000 characters.

## B2. Log events (source-verified field lists) ✅

| `event.name` | Fields (in addition to the common attributes) |
|---|---|
| `gemini_cli.config` | `model`, `embedding_model`, `sandbox_enabled`, `core_tools_enabled`, `approval_mode`, `api_key_enabled`, `vertex_ai_enabled`, `log_user_prompts_enabled`, `file_filtering_respect_git_ignore`, `debug_mode`, `mcp_servers`, `mcp_servers_count`, `mcp_tools`, `mcp_tools_count`, `output_format`, `extensions`, `extensions_count`, `extension_ids`, `auth_type`, `worktree_active`, `github_*` (📄) |
| `gemini_cli.user_prompt` | `prompt_length`, `prompt_id`, `auth_type`, `prompt` (if logPrompts) |
| `gemini_cli.tool_call` | `function_name`, `function_args` (if logPrompts), `duration_ms`, `success`, `decision` (`accept\|reject\|modify\|auto_accept`), `prompt_id`, `tool_type` (`native\|mcp`), `content_length`, `mcp_server_name`, `extension_name`, `extension_id`, `start_time`, `end_time`, `metadata` (diff stats `model_/user_added/removed_lines/chars`, plus the full response data if logPrompts), `error`, `error.message`, `error_type`, `error.type`. **There is no tool call id in the log record**; only the span has `gen_ai.tool.call_id`. |
| `gemini_cli.api_request` | `model`, `prompt_id`, `role` (LlmRole), `request_text` (if logPrompts) |
| `gemini_cli.api_response` | `model`, `duration_ms`, `input_token_count`, `output_token_count`, `cached_content_token_count`, `thoughts_token_count`, `tool_token_count`, `total_token_count`, `prompt_id`, `auth_type`, `status_code`, `http.response.status_code`, `finish_reasons`, `role`, `response_text` (if logPrompts) |
| `gemini_cli.api_error` | `error.message`, `error`, `error.type`, `model`, `model_name`, `duration`, `duration_ms`, `status_code`, `http.response.status_code`, `prompt_id`, `auth_type`, `role` |
| `gen_ai.client.inference.operation.details` (semantic twin of the request, response and error records) | `gen_ai.operation.name`, `gen_ai.provider.name` (`gcp.vertex_ai` or `gcp.gen_ai`), `gen_ai.request.model`, `gen_ai.response.model`, `gen_ai.response.id`, `gen_ai.response.finish_reasons`, `gen_ai.request.{temperature, top_p, top_k, choice.count, seed, frequency_penalty, presence_penalty, max_tokens, stop_sequences}`, `gen_ai.output.type`, `gen_ai.system_instructions`, `gen_ai.input.messages`, `gen_ai.output.messages` (both gated), `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`, `server.address`, `server.port` |
| `gemini_cli.chat_compression` | **`tokens_before`, `tokens_after` only.** No trigger, no summary, no model. Also emitted with before = after when compression fails. Issue #23445: bypasses the buffer wrapper. |
| `gemini_cli.agent.start` | `agent_id`, `agent_name` |
| `gemini_cli.agent.finish` | `agent_id`, `agent_name`, `duration_ms`, `turn_count`, `terminate_reason` (`ERROR\|TIMEOUT\|GOAL\|MAX_TURNS\|ABORTED\|ERROR_NO_COMPLETE_TASK_CALL`) |
| `gemini_cli.agent.recovery_attempt` | `agent_id`, `agent_name`, `reason` (same enum), `duration_ms`, `success`, `turn_count` (the docs list `attempt_number` and `error_type`; ⚠️ the source differs) |
| `gemini_cli.hook_call` | `hook_event_name`, `hook_type` (`command\|runtime`), `hook_name` (sanitized unless logPrompts), `duration_ms`, `success`, `exit_code`, `error`, plus `hook_input`, `hook_output`, `stdout`, `stderr` if logPrompts |
| `gemini_cli.conversation_finished` | `approvalMode`, `turnCount` |
| `loop_detected` (**no `gemini_cli.` prefix**) | `loop_type` (`consecutive_identical_tool_calls\|chanting_identical_sentences\|llm_detected_loop`), `prompt_id`, `count`, `confirmed_by_model`, `analysis`, `confidence` |
| `loop_detection_disabled` | `prompt_id` |
| `gemini_cli.llm_loop_check` | `prompt_id`, `flash_confidence`, `main_model`, `main_model_confidence` |
| `gemini_cli.next_speaker_check` | `prompt_id`, `finish_reason`, `result` |
| `gemini_cli.model_routing` | `decision_model`, `decision_source`, `routing_latency_ms`, `failed`, `approval_mode`, `reasoning`, `error_message`, `enable_numerical_routing`, `classifier_threshold` |
| `gemini_cli.network_retry_attempt` | `attempt`, `max_attempts`, `error_type`, `delay_ms`, `model` |
| `gemini_cli.chat.content_retry` | `attempt_number`, `error_type`, `retry_delay_ms`, `model` |
| `gemini_cli.chat.content_retry_failure` | `total_attempts`, `final_error_type`, `total_duration_ms`, `model` |
| `gemini_cli.chat.invalid_chunk` | `error.message` |
| `gemini_cli.tool_output_truncated` | `tool_name`, `original_content_length`, `truncated_content_length`, `threshold`, `lines`, `prompt_id` |
| `gemini_cli.tool_output_masking` | `tokens_before`, `tokens_after`, `masked_count`, `total_prunable_tokens` |
| `gemini_cli.file_operation` | `tool_name`, `operation` (`create\|read\|update`), `lines`, `mimetype`, `extension`, `programming_language` |
| `gemini_cli.plan.approval_mode_switch` (the docs say `approval_mode_switch`) | `from_mode`, `to_mode` |
| `gemini_cli.plan.approval_mode_duration` | `mode`, `duration_ms` |
| `gemini_cli.plan.execution` | `approval_mode` |
| `gemini_cli.conseca.verdict` and `gemini_cli.conseca.policy_generation` | `verdict`, `decision`, `reason`, `tool_name`, `user_prompt`, `policy`, `tool_call`, `verdict_rationale`, `error` |

**Other events:**
- `flash_fallback`, `ripgrep_fallback`, `web_fetch_fallback_attempt{reason}`, `malformed_json_response{model}`, `slash_command{command, subcommand, status, extension_id}`, `slash_command.model{model_name}`, `rewind{outcome}`, `ide_connection{connection_type}`, `edit_strategy`, `edit_correction`
- Extension install, uninstall, update, enable and disable events
- `startup_stats{phases, os_platform, os_release, is_docker}`, `keychain.availability`, `token_storage_initialization`, `onboarding.start`, `onboarding.success`
- Billing (`billingEvents.ts`): `gemini_cli.credits_used{model, credits_consumed, credits_remaining}`, `overage_menu_shown`, `overage_option_selected`, `empty_wallet_menu_shown`, `credit_purchase_click`, `api_key_updated`
- Browser-agent events

**LlmRole values:** `main`, `subagent`, `utility_tool`, `utility_compressor`, `utility_summarizer`, `utility_router`, `utility_loop_detector`, `utility_next_speaker`, `utility_edit_corrector`, `utility_autocomplete`, `utility_fast_ack_helper`, `utility_state_snapshot_processor`. This tags which internal LLM call each API event belongs to.

## B3. Metrics (`metrics.ts`) ✅

- **Session and tools:** `gemini_cli.session.count`, `gemini_cli.tool.call.count` (`function_name`, `success`, `decision`, `tool_type`), `gemini_cli.tool.call.latency`
- **API and tokens:** `gemini_cli.api.request.count` (`model`, `status_code`, `error_type`), `gemini_cli.api.request.latency`, `gemini_cli.token.usage` (`model`, `type`: `input|output|thought|cache|tool`)
- **Files:** `gemini_cli.file.operation.count`, `gemini_cli.lines.changed`
- **Chat:** `gemini_cli.chat_compression` (`tokens_before`, `tokens_after`), `gemini_cli.chat.invalid_chunk.count`, `gemini_cli.chat.content_retry.count`, `gemini_cli.chat.content_retry_failure.count`, `gemini_cli.network_retry.count`
- **Routing and commands:** `gemini_cli.model_routing.latency`, `gemini_cli.model_routing.failure.count`, `gemini_cli.slash_command.model.call_count`
- **Hooks:** `gemini_cli.hook_call.count`, `gemini_cli.hook_call.latency`
- **Agents:** `gemini_cli.agent.run.count` (`agent_name`, `terminate_reason`), `gemini_cli.agent.duration`, `gemini_cli.agent.turns`, `gemini_cli.agent.recovery_attempt.count`, `gemini_cli.agent.recovery_attempt.duration`
- **Browser agent:** `gemini_cli.browser_agent.*` (connection, tools, vision, task, cleanup)
- **GenAI semantic conventions:** `gen_ai.client.token.usage`, `gen_ai.client.operation.duration`
- **Performance:** `gemini_cli.startup.duration`, `gemini_cli.memory.usage`, `gemini_cli.cpu.usage`, `gemini_cli.event_loop.delay`, `gemini_cli.tool.queue.depth`, `gemini_cli.tool.execution.breakdown` (`phase`), `gemini_cli.token.efficiency`, `gemini_cli.api.request.breakdown`, `gemini_cli.performance.{score,regression,regression.percentage_change,baseline.comparison}`
- **UI and misc:** `gemini_cli.ui.flicker.count`, `gemini_cli.ui.slow_render.latency`, `gemini_cli.exit.fail.count`, `gemini_cli.plan.execution.count`, `gemini_cli.keychain.availability.count`, `gemini_cli.token_storage.type.count`, `gemini_cli.overage_option.count`, `gemini_cli.credit_purchase.count`, `gemini_cli.onboarding.{start,success,duration}`

## B4. Traces ✅ (`trace.ts`, `constants.ts`)

**Tracer:** `gemini-cli`. The span name equals `GeminiCliOperation`. Operations actually used:
- `agent_call` (`agents/agent-tool.ts`; sets `gen_ai.agent.name` and `gen_ai.agent.description` to the subagent's)
- `llm_call` (`core/loggingContentGenerator.ts`; `gen_ai.request.model`, `gen_ai.prompt.name` = prompt id, `gen_ai.system_instructions`, `gen_ai.tool.definitions`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`)
- `schedule_tool_calls`
- `tool_call` (`gen_ai.tool.name`, `gen_ai.tool.call_id`, `gen_ai.tool.description`)

`user_prompt` and `system_prompt` are defined but unused.

**Every span** carries `gen_ai.operation.name`, `gen_ai.agent.name=gemini-cli`, `gen_ai.agent.description` and `gen_ai.conversation.id` (= session id). It also gets `gen_ai.input.messages` and `gen_ai.output.messages` when traces and logPrompts are both on. Status is OK or ERROR, with the exception recorded.

**Propagation:**
- `HttpInstrumentation` is registered, so outbound Node `http` requests get W3C headers. ⚠️ Not verified that the GenAI SDK's fetch is covered.
- **Inbound `TRACEPARENT` is not supported.** Issue #25919 is closed as "completed", but at commit `fb972b2` no code reads `TRACEPARENT` (repo-wide grep returns nothing).
- Issue #23054 (closed) reported fragmented trace ids in non-interactive mode.

## B5. Hooks ✅ 📄

**Config:** `settings.json` → `hooks.{EventName}: [{matcher?, sequential?, hooks: [{type: "command", command, name?, description?, timeout? (ms, default 60000), env?}]}]`.
- Layers, highest precedence first: project `.gemini/settings.json`, user `~/.gemini/settings.json`, system `/etc/gemini-cli/settings.json`, extensions.
- `hooksConfig.{enabled (default true), disabled: [names], notifications (default true)}`.
- `HookType` is `command` or `runtime` (runtime is in-process, for SDK and extensions).
- Project hooks need trust (`trusted_hooks.json`, keyed by `name:command`).
- **Matchers:** regex for tools, exact string for lifecycle events. MCP tools are named `mcp_<server>_<tool>`.
- **Hook process env:** `GEMINI_PROJECT_DIR`, `GEMINI_CWD`, `GEMINI_SESSION_ID`, `GEMINI_PLANS_DIR`, `CLAUDE_PROJECT_DIR` (alias).

**Exit codes:** 0 means stdout JSON is parsed. 2 means block, with stderr as the reason. Any other code is a warning and execution continues.

**Base input:** `session_id`, `transcript_path`, `cwd`, `hook_event_name`, `timestamp`.

**Common output:** `continue`, `stopReason`, `suppressOutput`, `systemMessage`, `decision` (`allow|deny|block|ask|approve`), `reason`, `hookSpecificOutput`.

| Event | Input | Output and semantics |
|---|---|---|
| `SessionStart` | `source`: `startup\|resume\|clear` | `hookSpecificOutput.additionalContext` (first history turn in interactive mode; prepended to the prompt otherwise), `systemMessage`. Advisory only; never blocks. |
| `SessionEnd` | `reason`: `exit\|clear\|logout\|prompt_input_exit\|other` | `systemMessage`. Best effort; not awaited. |
| `BeforeAgent` | `prompt` | `additionalContext` is appended to the prompt. `decision: deny` blocks and discards the prompt. `continue:false` blocks but keeps it in history. Exit 2 means deny. |
| `AfterAgent` | `prompt`, `prompt_response`, `stop_hook_active` | `decision: deny` with `reason` sends the reason as a new prompt (retry). `continue:false` stops. `hookSpecificOutput.clearContext` clears LLM memory. |
| `BeforeModel` | `llm_request{model, messages[{role: user\|model\|system, content}], config{temperature, maxOutputTokens, topP, topK, stopSequences, candidateCount, presencePenalty, frequencyPenalty, …}, toolConfig{mode, allowedFunctionNames}}` | **Can modify:** `hookSpecificOutput.llm_request` (partial override: model, messages, config). **Can short-circuit:** `hookSpecificOutput.llm_response`, a synthetic response that skips the LLM call. `decision: deny` or exit 2 aborts the turn. |
| `BeforeToolSelection` | `llm_request` | `hookSpecificOutput.toolConfig{mode: AUTO\|ANY\|NONE, allowedFunctionNames[]}`. Allow-lists from multiple hooks are unioned; `NONE` wins. `decision`, `continue` and `systemMessage` are not supported. |
| `AfterModel` | `llm_request`, `llm_response{text?, candidates[{content{role:"model", parts: string[]}, finishReason: STOP\|MAX_TOKENS\|SAFETY\|RECITATION\|OTHER, index, safetyRatings}], usageMetadata{promptTokenCount, candidatesTokenCount, totalTokenCount}}` | Fires **per streamed chunk**. `hookSpecificOutput.llm_response` replaces the chunk. `deny` discards and blocks. `continue:false` kills the loop. |
| `BeforeTool` | `tool_name`, `tool_input`, `mcp_context?{server_name, tool_name, command, args, cwd, url, tcp}`, `original_request_name?` | `decision: deny\|block` with `reason` returns a tool error to the agent (the turn continues). `hookSpecificOutput.tool_input` is merged into and overrides the arguments. `continue:false` kills the loop. |
| `AfterTool` | `tool_name`, `tool_input`, `tool_response{llmContent, returnDisplay, error?}`, `mcp_context?`, `original_request_name?` | `deny` with `reason` replaces the result. `additionalContext` is appended. `tailToolCallRequest{name, args}` chains another tool whose result replaces this one. |
| `PreCompress` | `trigger`: `manual\|auto` | `systemMessage`. Asynchronous and advisory; **cannot block or modify. There are no token counts and no summary.** |
| `Notification` | `notification_type`: `ToolPermission`, `message`, `details` | `systemMessage`. Observability only. |

**Call sites:**
- BeforeModel, AfterModel and BeforeToolSelection fire in `core/geminiChat.ts`.
- BeforeAgent and AfterAgent fire in `core/client.ts` (the main client). ⚠️ Whether they fire for subagents is unverified.
- PreCompress fires in `context/chatCompressionService.ts`.
- Hook inputs have **no `agent_id`, `model` or `prompt_id`** (#21615 "Hooks: Attach agent information" is closed, but no such fields exist in the types).

## B6. Session, prompt and compression ids, plus file surfaces ✅

**Ids:**
- `session.id` / `gen_ai.conversation.id` is the session.
- `prompt_id` (= `gen_ai.prompt.name`) is per user prompt and is on `user_prompt`, `api_*`, `tool_call`, loop and next-speaker events.
- Agent runs have `agent_id` and `agent_name`.

**Compression internals:** `ChatCompressionInfo{originalTokenCount, newTokenCount, compressionStatus}`. Status values: `COMPRESSED`, `COMPRESSION_FAILED_INFLATED_TOKEN_COUNT`, `COMPRESSION_FAILED_TOKEN_COUNT_ERROR`, `COMPRESSION_FAILED_EMPTY_SUMMARY`, … This is emitted in-process as `GeminiEventType.ChatCompressed`.

**Transcript files:** `~/.gemini/tmp/<project_hash>/chats/session-<ts>-<id>.jsonl`. Subagent transcripts are nested under the parent session id folder, with `kind:"subagent"`.
- `ConversationRecord{sessionId, projectHash, startTime, lastUpdated, messages[], summary?, directories?, kind?: main|subagent}`
- `MessageRecord{id, timestamp, content, type: user|info|error|warning|gemini, toolCalls?[{id, name, args, result, status, timestamp, agentId?, …}], thoughts?, tokens?{input, output, cached, thoughts, tool, total}, model?}`

**Headless `--output-format stream-json`:**
- `init{session_id, model}`
- `message{role, content, delta?}`
- `tool_use{tool_name, tool_id, parameters}`
- `tool_result{tool_id, status, output?, error?}`
- `error{severity, message}`
- `result{status, error?, stats{total_tokens, input_tokens, output_tokens, cached, input, duration_ms, tool_calls, models{}}}`

---

# C. Cursor hooks

**Primary schema:** cursor.com/docs/agent/hooks (also cursor.com/docs/reference/hooks) was **unreachable** (403). The authoritative-looking evidence used instead:

1. **griddynamics/rosetta** `docs/hooks/cursor.md`, https://github.com/griddynamics/rosetta/blob/main/docs/hooks/cursor.md. It cites cursor.com/docs/reference/hooks and has **live captures on Cursor 3.9.16** (Runs 1–4, 2026-06-29/30). 🔬
2. **sondera-ai/sondera-coding-agent-hooks** `crates/hooks/cursor/src/types.rs` (Rust serde types citing cursor.com/docs/hooks). ✅ third-party
3. **entireio/cli** `cmd/entire/cli/agent/cursor/AGENT.md` (probe of `agent` CLI `2026.02.13-41ac335`, 2026-03-02). 🔬
4. **CorridorSecurity/hookshot** `cursor/types.go` (2026-08) and `docs/reference-cursor.md`. Note that its reference doc uses an older `decision` field while `types.go` uses `permission`.
5. **johnlindquist/cursor-hooks** `src/types.ts` and `schema/hooks.schema.json` (Oct 2025; only 6 early events, `version: 1`). Superseded.
6. **endorlabs/cursor-hook-examples** `.cursor/hooks.json` (Dec 2025).

## C1. `hooks.json` format

```json
{"version":1,"hooks":{"<eventName>":[{"command":"path/or/shell","type":"command","timeout":60,"loop_limit":null,"failClosed":false,"matcher":"Shell"}]}}
```

- **Locations:** project `.cursor/hooks.json`, user `~/.cursor/hooks.json`, enterprise `/Library/Application Support/Cursor/hooks.json` (macOS), `/etc/cursor/hooks.json` (Linux), `C:\ProgramData\Cursor\hooks.json` (Windows).
- `type` is `command` or `prompt`. Several handlers per event are allowed and run in parallel 🔬.
- **Fail-open by default.** With `failClosed:true`, a crash, timeout, invalid output or **empty output** blocks 🔬.
- **Hook env:** `CURSOR_PROJECT_DIR`, `CURSOR_VERSION`, `CURSOR_USER_EMAIL`, `CURSOR_TRANSCRIPT_PATH`, `CURSOR_CODE_REMOTE`, `CLAUDE_PROJECT_DIR`, plus vars set by `sessionStart.env` (these reach hook processes only, not the agent's shell 🔬).
- **Exit codes:** 0 parses stdout JSON. 2 blocks; if stdout also holds JSON, that raw text becomes the reason unparsed 🔬. Any other code fails open.
- **Output is flat snake_case. There is no `hookSpecificOutput` wrapper** 🔬.

**Matcher targets:**

| Hook(s) | Matcher is compared against |
|---|---|
| `preToolUse`, `postToolUse`, `postToolUseFailure` | Tool type: `Shell`, `Read`, `Write`, `Grep`, `Task`, `MCP:<tool>` |
| `subagentStart`, `subagentStop` | Subagent type |
| `beforeShellExecution`, `afterShellExecution` | Command text |
| `beforeMCPExecution`, `afterMCPExecution` | MCP tool name |
| `beforeReadFile` | `Read` or `TabRead` |
| `afterFileEdit` | `Write` or `TabWrite` |

## C2. Common input (all agent hooks)

**Documented:**
- `conversation_id` (stable across turns)
- `generation_id` (changes with every user message; `""` at sessionStart)
- `model` (the legacy slug of the **currently selected** model, e.g. `"default"`, `"composer-2.5-fast"`; not the model actually served)
- `model_id`, `model_params[{id, value}]`
- `hook_event_name` (camelCase), `cursor_version`, `workspace_roots[]`, `user_email`
- `transcript_path` (`…/agent-transcripts/<id>.jsonl`; `null` early in a session and always `null` in CLI `-p` mode)

**Observed but undocumented** 🔬:
- `session_id`, equal to `conversation_id`
- On `afterAgentResponse` and the following `stop` and `beforeSubmitPrompt`: `input_tokens`, `output_tokens`, `cache_read_tokens`, `cache_write_tokens`

## C3. Events

| Event | Input (in addition to common) | Output and permission semantics |
|---|---|---|
| `sessionStart` | `session_id`, `is_background_agent`, `composer_mode` (`agent\|ask\|edit`) | `additional_context` (reaches the model 🔬), `env{}` |
| `sessionEnd` | `session_id`, `reason` (`completed\|aborted\|error\|window_close\|user_close`), `duration_ms`, `is_background_agent`, `final_status`, `error_message?` | Fire-and-forget |
| `beforeSubmitPrompt` | `prompt`, `attachments[{type: file\|rule, file_path}]` (**rules loaded = context provenance**) | `continue` (bool), `user_message` |
| `preToolUse` | `tool_name`, `tool_input` (object; e.g. Shell `{command, cwd, timeout}`, Read `{file_path}`), `tool_use_id` (Shell: UUID; Read and Grep: `tool_…`; the CLI form is `call_x\nctc_x`), `cwd`, `agent_message?` | `permission`: `allow\|deny` (`ask` is accepted but not enforced), `user_message`, `agent_message`, `updated_input` (rewrite ✅🔬). On deny, **`user_message` reaches the model** via `postToolUseFailure.error_message`; `agent_message` was not observed reaching it 🔬. |
| `postToolUse` | `tool_name`, `tool_input`, `tool_output` (JSON string, shape depends on tool), `tool_use_id`, `cwd`, `duration` (ms, float) | `additional_context`, `updated_mcp_tool_output` (MCP only) |
| `postToolUseFailure` | `tool_name`, `tool_input`, `tool_use_id`, `cwd`, `error_message`, `failure_type` (`timeout\|error\|permission_denied`), `is_interrupt`, `duration` | None |
| `beforeShellExecution` | `command`, `cwd`, `sandbox`, `timeout?` | `permission`: `allow\|deny\|ask` (`ask` behaved like deny with no UI 🔬), `user_message`, `agent_message` |
| `afterShellExecution` | `command`, `output`, `duration`, `sandbox` | Fire-and-forget |
| `beforeMCPExecution` | `tool_name`, `tool_input` (JSON string), `url?` or `command?` (identifies the server) | `permission`: `allow\|deny\|ask`, `user_message`, `agent_message` |
| `afterMCPExecution` | `tool_name`, `tool_input`, `result_json`, `duration` | Fire-and-forget |
| `beforeReadFile` | `file_path`, `content`, `attachments` | `permission`: `allow\|deny`, `user_message` |
| `afterFileEdit` | `file_path`, `edits[{old_string, new_string}]` (`[]` for new files 🔬) | None |
| `afterAgentResponse` | `text` (plus observed token fields) | Fire-and-forget |
| `afterAgentThought` | `text`, `duration_ms?` | Fire-and-forget |
| `stop` | `status` (`completed\|aborted\|error`), `loop_count` (plus observed tokens) | `followup_message`: auto-submits a follow-up, capped by `loop_limit` (older docs: max 5) |
| `subagentStart` | `subagent_id`, `subagent_type` (docs: `generalPurpose\|explore\|shell`; observed `"general-purpose"`), `task`, `parent_conversation_id`, `tool_call_id`, `subagent_model`, `is_parallel_worker`, `git_branch?` | `permission`: `allow\|deny`, `user_message` |
| `subagentStop` | `subagent_id` (🔬), `subagent_type`, `status` (`completed\|error\|aborted`), `task`, `description`, `summary?`, `duration_ms`, `message_count`, `tool_call_count`, `loop_count`, `modified_files?`, `agent_transcript_path` | `followup_message` (only when completed) |
| `preCompact` | `trigger` (`auto\|manual`), `context_usage_percent`, `context_tokens`, `context_window_size`, `message_count`, `messages_to_compact`, `is_first_compaction` | `user_message` only (cannot block). **No post-compaction hook, no tokens-after, no summary.** |
| `beforeTabFileRead` (Tab) | `file_path`, `content` | `permission`: `allow\|deny` |
| `afterTabFileEdit` (Tab) | `file_path`, `edits[{old_string, new_string, range{start_line_number, start_column, end_line_number, end_column}, old_line, new_line}]` | None |
| `workspaceOpen` (app) | Common subset | `pluginPaths[]` |

**Gaps, versions and notes:**
- In CLI `agent -p` (headless) mode, **`beforeSubmitPrompt` and `stop` do not fire**; only session and tool hooks do 🔬 (entireio, CLI 2026.02.13).
- `sessionEnd`, the MCP hooks and `beforeReadFile` deny remain unverified 📄.
- ⚠️ The exact Cursor version that introduced sessionStart, sessionEnd, preToolUse, postToolUse, subagentStart/Stop and preCompact could not be confirmed, because the changelog is blocked. Evidence: these events are absent from johnlindquist's types (Oct 2025, ~Cursor 1.7) and present in the entireio probe (Feb–Mar 2026) and rosetta (3.9.16, June 2026).

## C4. Other Cursor capture surfaces

**Transcripts:** `~/.cursor/projects/<sanitized-path>/agent-transcripts/<conversation_id>.jsonl` (IDE nests it as `<id>/<id>.jsonl`). Lines look like `{role, message:{content:[{type:"text"|"tool_use", name, input}]}}`. Tool-use blocks carry **no id** 🔬.

**CLI `--output-format stream-json`** (jnarowski/agentcmd docs, ⚠️ third-party):
- `system/init{session_id, model, permissionMode, cwd, apiKeySource}`
- `user`, `assistant{message, session_id, timestamp_ms}`
- `tool_call` with subtype `started` or `completed`: `{call_id, tool_call{<x>ToolCall{args, result}}, model_call_id, session_id, timestamp_ms}`
- `result{subtype: success|error, is_error, duration_ms, duration_api_ms, result, session_id, request_id}`. No tokens.

**Cloud / Background Agents API** (third-party clients, e.g. https://github.com/raycast/extensions/blob/main/extensions/cursor-agents/src/cursor.ts and simstudioai/sim):
- `https://api.cursor.com/v0/agents`: `POST` to launch, `GET` to list.
- `GET /v0/agents/{id}` returns `{id, status: CREATING|RUNNING|FINISHED|ERROR|EXPIRED, source{repository, ref}, target{branchName, url, prUrl, autoCreatePr}, name, createdAt, summary}`.
- `GET /v0/agents/{id}/conversation` returns `{id, messages[{id, type: user_message|assistant_message, text}]}`.
- `POST /v0/agents/{id}/followup`, `DELETE /v0/agents/{id}`, `GET /v0/models`.
- **No tool-level or event-stream API was found.** ⚠️ Webhooks (`statusChange`) are unverified.

**Admin usage API:** `POST https://api.cursor.com/teams/filtered-usage-events` (evidence: apache/devlake fixtures, getsentry/abacus). Rows look like `{timestamp, model, kind, maxMode, requestsCosts, isTokenBasedCall, tokenUsage{inputTokens, outputTokens, cacheWriteTokens, cacheReadTokens, totalCents}, userEmail, isChargeable, isHeadless, chargedCents, conversationId}`. **This is the only cost source, and it joins to the hooks' `conversation_id`.**

**OpenTelemetry:** Cursor has no native OTel export. No evidence of one was found. ⚠️

---

# D. Coverage matrices

**Legend:** OTel = native OpenTelemetry; Hook; File = local transcript or rollout; API = RPC/stream/HTTP API; ✗ = not available.

## D1. Codex CLI

| Concept | Surface and exact fields |
|---|---|
| Run start/end | Hook `SessionStart{source}` / `SessionEnd{reason:"other"}`. OTel `codex.conversation_starts`, span `session_loop`. File `session_meta`. API `thread/started`, `thread/closed`. exec `thread.started` |
| Iteration / turn | OTel span `turn` (`turn.id`, token fields). Hook `UserPromptSubmit`, `Stop` (both have `turn_id`). File `turn_started`, `turn_complete`, `turn_aborted`, `turn_context`. API `turn/started`, `turn/completed` |
| Model request (model, tokens, stop reason) | OTel `codex.api_request`, `codex.sse_event` (`response.completed` tokens), span `handle_responses` (`gen_ai.usage.*`). File `token_usage_record`, `token_count`. API `thread/tokenUsage/updated`, `rawResponse/completed`. **Stop/finish reason: ✗** (only turn-level abort reason or error) |
| Tool request / decision / result | Hook `PreToolUse`, `PermissionRequest`, `PostToolUse`. OTel `codex.tool_decision`, `codex.tool_result`, `codex.sandbox_outcome`. File `function_call`, `function_call_output`. API `item/*` and approval requests |
| MCP call | OTel span `mcp.tools.call`; `codex.tool_result{mcp_server, mcp_tool}`. Hook `tool_name=mcp__srv__tool`. API `mcpToolCall` item. File (paginated `item_completed`) |
| Permission decision and source | OTel `codex.tool_decision.source` (User, Config, AutomatedReviewer), `codex.guardian_assessment` (opt-in). Hook `PermissionRequest`. API approval requests, `serverRequest/resolved`, `item/autoApprovalReview/*`. File ✗ (not persisted) |
| Subagent spawn / return | Hook `SubagentStart`, `SubagentStop{agent_transcript_path, last_assistant_message}`. File (child rollout `parent_thread_id`, `agent_role`). API `collabAgentToolCall`, `subAgentActivity`. OTel `codex.agent_response` lineage, `codex.multi_agent.spawn.*` |
| Compaction: trigger | Hook `PreCompact` / `PostCompact{trigger}` |
| Compaction: tokens before/after | File (infer from `token_count` / `token_usage_record` around `compacted`). OTel ✗ (internal analytics only) |
| Compaction: summary content | File `compacted.message`. Raw request/response via `CODEX_ROLLOUT_TRACE_ROOT` |
| Context provenance (rules) | OTel spans `agents_md.discover` / `agents_md.load`. File (AGENTS.md injected message, `turn_context`). No dedicated event |
| Verification (tests run) | ✗ semantic. Infer from Bash `command` in hooks, OTel or file |
| Stop reason | File/API `turn_aborted.reason`, `turn/completed.status`, `turn.failed`. Hook `Stop.last_assistant_message`. Span status ✗ (#47192) |
| Cost | OTel `codex.turn_cost` / `codex.turn.cost_microusd` (app-server only, from backend) |
| Raw request/response bodies | File (`CODEX_ROLLOUT_TRACE_ROOT` `payloads/`). API `rawResponseItem/completed` (opt-in). File `response_item` (items, not full bodies) |
| Propagation (traceparent) | OTel: inbound `TRACEPARENT`/`TRACESTATE` env and app-server `trace` field; outbound to MCP `_meta`, exec-server, Responses WebSocket |

## D2. Gemini CLI

| Concept | Surface and exact fields |
|---|---|
| Run start/end | Hook `SessionStart{source}` / `SessionEnd{reason}`. OTel `gemini_cli.config`, `gemini_cli.session.count`, `conversation_finished{approvalMode, turnCount}`. File `ConversationRecord`. Stream `init` / `result` |
| Iteration / turn | Hook `BeforeAgent` / `AfterAgent`. OTel `user_prompt{prompt_id}`. Span `agent_call` (subagents only). ⚠️ No per-turn root span |
| Model request (model, tokens, stop reason) | OTel `api_request`, `api_response{*_token_count, finish_reasons}`, `gen_ai.client.inference.operation.details`, span `llm_call`, metric `token.usage`. Hook `BeforeModel`, `AfterModel` (`finishReason`, `usageMetadata`). File `tokens` |
| Tool request / decision / result | Hook `BeforeTool`, `AfterTool`. OTel `tool_call{decision, success, duration_ms}` (no call id in the log), span `tool_call{gen_ai.tool.call_id}`. File `toolCalls`. Stream `tool_use` / `tool_result` |
| MCP call | OTel `tool_call{tool_type:"mcp", mcp_server_name}`. Hook `mcp_context`, `tool_name mcp_<srv>_<tool>` |
| Permission decision and source | OTel `tool_call.decision` (`accept\|reject\|modify\|auto_accept`), `approval_mode_switch`, `conseca.verdict`. Hook `Notification{ToolPermission}` (observability only). Source of auto-accept: partial (`auto_accept` only, no policy-rule id) ⚠️ |
| Subagent spawn / return | OTel `agent.start` / `agent.finish{terminate_reason, turn_count, duration_ms}`, `agent.recovery_attempt`, span `agent_call`, role `subagent`. File (nested subagent chats). Hook ✗ (no subagent events or agent ids) |
| Compaction: trigger | Hook `PreCompress{trigger}` |
| Compaction: tokens before/after | OTel `chat_compression{tokens_before, tokens_after}` |
| Compaction: summary content | ✗ in OTel or hooks. ⚠️ Possibly visible in the transcript or history; unverified |
| Context provenance (rules) | ✗ (GEMINI.md files not in telemetry). `gemini_cli.config` lists MCP servers and extensions only |
| Verification (tests run) | ✗ semantic. Infer from `run_shell_command` args |
| Stop reason | OTel `finish_reasons`, `agent.finish.terminate_reason`, `loop_detected`, `next_speaker_check`. Stream `result.status` |
| Cost | ✗ for API key and Vertex. Billing `credits_used{credits_consumed}` only for credit plans |
| Raw request/response bodies | OTel `gen_ai.input.messages` / `gen_ai.output.messages` (needs traces and logPrompts), `request_text`, `response_text`. Hook `BeforeModel` / `AfterModel` (text-only stable format) |
| Propagation (traceparent) | Outbound HTTP via `HttpInstrumentation` (⚠️). Inbound `TRACEPARENT` ✗ (#25919 closed but not implemented on main) |

## D3. Cursor

| Concept | Surface and exact fields |
|---|---|
| Run start/end | Hook `sessionStart{session_id, composer_mode, is_background_agent}` / `sessionEnd{reason, duration_ms, final_status}`. API Cloud agent `status` |
| Iteration / turn | Hook `beforeSubmitPrompt` / `stop{status, loop_count}` (+ `generation_id`). **Not in CLI `-p` mode** |
| Model request (model, tokens, stop reason) | Hook common `model`/`model_id` (the selected model). Tokens are undocumented, observed on `afterAgentResponse` and `stop`. Stop reason ✗ (only `stop.status`). API usage events (`tokenUsage`, `model`) |
| Tool request / decision / result | Hook `preToolUse` / `postToolUse` / `postToolUseFailure` (`tool_use_id`, `duration`), plus granular shell, read and edit hooks. File transcript `tool_use` (no ids). API CLI stream-json `tool_call` |
| MCP call | Hook `beforeMCPExecution` / `afterMCPExecution{url\|command, tool_name, result_json, duration}`, `MCP:<tool>` in `preToolUse` |
| Permission decision and source | Hook output `permission` (your own decision). The final user approval decision ✗. `failure_type:"permission_denied"` on `postToolUseFailure` |
| Subagent spawn / return | Hook `subagentStart` / `subagentStop` (full fields in C3) |
| Compaction: trigger | Hook `preCompact{trigger}` |
| Compaction: tokens before/after | Before only: `preCompact{context_tokens, context_window_size, context_usage_percent, messages_to_compact}`. After ✗ |
| Compaction: summary content | ✗ |
| Context provenance (rules) | Hook `beforeSubmitPrompt.attachments[{type:"rule", file_path}]`, `beforeReadFile` |
| Verification (tests run) | ✗ semantic. Infer from `Shell` command and output |
| Stop reason | Hook `stop.status`, `sessionEnd.reason`, `subagentStop.status` |
| Cost | API admin `filtered-usage-events{totalCents, chargedCents, conversationId}` |
| Raw request/response bodies | ✗. Only `afterAgentResponse.text`, `afterAgentThought.text`, transcript |
| Propagation (traceparent) | ✗ |

---

## Unverified items and caveats

- **Cursor:**
  - Every Cursor field is second-hand: either from third-party docs that quote cursor.com/docs/reference/hooks, or from live captures. **Re-check against cursor.com when it is reachable.**
  - `ask` semantics, `agent_message` delivery, and the `subagent_type` spelling are conflicting or observed-only.
  - The token fields on `stop` and `afterAgentResponse` are undocumented.
  - Cloud Agents webhooks and API versioning are unverified.
- **Codex:**
  - Whether `codex exec` emits `codex.turn_cost` is unverified; it was only found in app-server.
  - App-server field names are camelCase on the wire (Rust `rename_all = "camelCase"` is assumed from the TS bindings), whereas the hook and rollout JSON are snake_case.
- **Gemini:**
  - Whether BeforeAgent and AfterAgent fire for subagents is unverified.
  - Whether outbound `traceparent` reaches the Gemini API (fetch versus http) is unverified.
  - The docs and source disagree on: the common attribute `active_approval_mode`, the `approval_mode_switch` event name, and the `agent.recovery_attempt` fields. The source was used in each case.
