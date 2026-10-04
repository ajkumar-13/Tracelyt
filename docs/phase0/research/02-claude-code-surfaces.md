# Claude Code instrumentation reference: hooks, OTel, Agent SDK, transcripts (CLI 2.1.289, 2026-10-04)

## Sources and how to read the tags

**Docs:** these pages, fetched as raw `.md` on 2026-10-04:
- https://code.claude.com/docs/en/hooks
- https://code.claude.com/docs/en/hooks-guide
- https://code.claude.com/docs/en/monitoring-usage
- https://code.claude.com/docs/en/env-vars
- https://code.claude.com/docs/en/settings-reference
- https://code.claude.com/docs/en/sessions
- https://code.claude.com/docs/en/claude-directory
- https://code.claude.com/docs/en/checkpointing
- https://code.claude.com/docs/en/sub-agents
- https://code.claude.com/docs/en/permissions
- https://code.claude.com/docs/en/permission-modes
- https://code.claude.com/docs/en/auto-mode-config
- https://code.claude.com/docs/en/cli-reference
- https://code.claude.com/docs/en/headless (`/agent-sdk/headless` returns 404)
- https://code.claude.com/docs/en/model-config
- https://code.claude.com/docs/en/costs
- https://code.claude.com/docs/en/analytics
- https://code.claude.com/docs/en/agent-sdk/{overview,typescript,python,hooks,permissions,observability,sessions,session-storage,cost-tracking}

**Type definitions:**
- npm `@anthropic-ai/claude-agent-sdk@0.3.289`, file `sdk.d.ts`
- `anthropics/claude-agent-sdk-python` main branch, file `src/claude_agent_sdk/types.py` (pyproject 0.2.163)

**Repo:** `anthropics/claude-code` `CHANGELOG.md` and `examples/hooks/`. The repo has no docs folder. `examples/hooks` holds only `bash_command_validator_example.py`.

**Tags used below:**
- **[D]** documented.
- **[T]** in type definitions only.
- **[O]** I observed it on the local `claude` 2.1.289 in this container. I ran `claude -p` with stream-json and logging hooks on all main events, then a manual `/compact`.
- **[U]** unverified or inferred.

## 1. Hooks

### 1.1 Config schema in settings.json [D]

Shape:
```
{"hooks": {"<Event>": [ {"matcher": "<str>", "hooks": [ <handler>, ... ]} ]}}
```

**Where hooks can be defined:**
- `~/.claude/settings.json`
- `.claude/settings.json`
- `.claude/settings.local.json`
- managed policy
- plugin `hooks/hooks.json` (has an optional top-level `description`)
- skill frontmatter (`hooks:`): stays registered for the rest of the session once the skill is invoked
- subagent frontmatter (`hooks:`): active only while that subagent runs; a `Stop` hook there becomes `SubagentStop`

**Merge and control rules:**
- Hooks merge across levels.
- The same handler defined in several settings files runs once.
- All matching hooks run in parallel.
- `disableAllHooks` (cannot disable managed hooks unless set at the managed level) and `allowManagedHooksOnly` control which hooks run.
- `allowedHttpHookUrls` and `httpHookAllowedEnvVars` restrict HTTP hooks.
- Workspace trust: an interactive session waits for the trust dialog. `-p` and SDK sessions treat the folder as trusted.
- Frontmatter hooks in a project subagent need explicit trust, and `-p` does not count as trust (v2.1.218+).

**Common handler fields:**

| Field | Notes |
|---|---|
| `type` | `"command"`, `"http"`, `"mcp_tool"`, `"prompt"`, or `"agent"` |
| `if` | Exactly one permission rule, such as `"Bash(git *)"` or `"Edit(*.ts)"`. Evaluated only on `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PermissionRequest`, `PermissionDenied`. On any other event, a hook with `if` set never runs |
| `timeout` | Seconds. Defaults: 600 for command, http and mcp_tool; 30 for prompt; 60 for agent. Command/http/mcp_tool drop to 30 on `UserPromptSubmit`, `PreModelSwitch` and `PostModelSwitch`, and to 10 on `MessageDisplay`. `SessionEnd` has a shared 1.5 s budget, raised to the largest per-hook `timeout` (cap 60 s) or set with `CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS` |
| `statusMessage` | Spinner text |
| `once` | Honored only in skill frontmatter |

**Per-type fields:**
- **command:** `command`, `args` (exec form: no shell; placeholders substituted as plain strings), `async`, `asyncRewake` (runs in background; exit 2 wakes Claude), `shell` (`"bash"` or `"powershell"`).
- **http:** `url`, `headers` (`$VAR`/`${VAR}` interpolation, only for names in `allowedEnvVars`), `allowedEnvVars`. The body is POSTed as `Content-Type: application/json`.
- **mcp_tool:** `server` (a plugin server is named `plugin:<plugin>:<server>`), `tool`, `input` (string values support `${path}` substitution, such as `"${tool_input.file_path}"`). `isError: true` counts as a non-blocking error.
- **prompt:** `prompt` (`$ARGUMENTS` is replaced by the input JSON; if absent, the JSON is appended), `model`, `continueOnBlock`.
- **agent** (experimental): `prompt`, `model`. Up to 50 turns. No `continueOnBlock`.

**Which events accept which hook types:**

| Events | Allowed types |
|---|---|
| `PermissionDenied`, `PostToolBatch`, `PostToolUse`, `PostToolUseFailure`, `PreToolUse`, `Stop`, `SubagentStop`, `TaskCompleted`, `TaskCreated`, `TeammateIdle`, `UserPromptExpansion`, `UserPromptSubmit` | All 5 |
| `PermissionRequest` | command, http, mcp_tool, prompt (agent is skipped, v2.1.280+) |
| `ConfigChange`, `CwdChanged`, `DirectoryAdded`, `Elicitation`, `ElicitationResult`, `FileChanged`, `InstructionsLoaded`, `MessageDisplay`, `Notification`, `PostCompact`, `PostModelSwitch`, `PreCompact`, `PreModelSwitch`, `SessionEnd`, `StopFailure`, `SubagentStart`, `WorktreeCreate`, `WorktreeRemove` | command, http, mcp_tool |
| `SessionStart`, `Setup` | command, mcp_tool only. mcp_tool is skipped at launch, before MCP is up |

### 1.2 Matcher rules [D]

**How a matcher string is interpreted:**
- `"*"`, `""`, or omitted matches everything.
- A string of only letters, digits, `_`, `-`, space, `,` and `|` is an exact match, or a list split on `|` or `,`.
- Anything else is a JavaScript regex tested with `RegExp.test`, unanchored.
- `FileChanged` and `StopFailure` use a narrower exact set (letters, digits, `_`, `|`).
- A matcher on an event without matcher support is silently ignored.
- MCP tools are named `mcp__<server>__<tool>`; plugin MCP tools are named `mcp__plugin_<plugin>_<server>__<tool>`. A bare `mcp__memory` matches nothing; write `mcp__memory__.*`.

| Event | Matches on | Values |
|---|---|---|
| `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PermissionRequest`, `PermissionDenied` | `tool_name` | |
| `SessionStart` | `source` | `startup`, `resume`, `clear`, `compact`, `fork` |
| `Setup` | `trigger` | `init`, `maintenance` |
| `SessionEnd` | `reason` | `clear`, `resume`, `logout`, `prompt_input_exit`, `other` (`bypass_permissions_disabled` removed in v2.1.234) |
| `Notification` | `notification_type` | `permission_prompt`, `idle_prompt`, `auth_success`, `elicitation_dialog`, `elicitation_url_dialog`, `elicitation_complete`, `elicitation_response`, `agent_needs_input`, `agent_completed`, `quota_auto_resume_fired`, `quota_auto_resume_stale`, `quota_auto_resume_disabled` |
| `SubagentStart`, `SubagentStop` | `agent_type` | `general-purpose`, `Explore`, `Plan`, custom names; plugin agents as `^plugin:name$` |
| `PreCompact`, `PostCompact` | `trigger` | `manual`, `auto` |
| `PreModelSwitch`, `PostModelSwitch` | canonical name derived from `to_model` | |
| `ConfigChange` | `source` | `user_settings`, `project_settings`, `local_settings`, `policy_settings`, `skills` |
| `DirectoryAdded` | `source` | `slash_command`, `register_repo_root` |
| `FileChanged` | literal filenames, split on `\|` | This also builds the watch list |
| `StopFailure` | `error` | `rate_limit`, `overloaded`, `authentication_failed`, `oauth_org_not_allowed`, `account_on_hold`, `billing_error`, `invalid_request`, `model_not_found`, `server_error`, `max_output_tokens`, `cloud_credential_error` (v2.1.267+), `unknown` |
| `InstructionsLoaded` | `load_reason` | `session_start`, `nested_traversal`, `path_glob_match`, `include`, `compact` |
| `UserPromptExpansion` | `command_name` | |
| `Elicitation`, `ElicitationResult` | `mcp_server_name` | |
| `UserPromptSubmit`, `PostToolBatch`, `Stop`, `TeammateIdle`, `TaskCreated`, `TaskCompleted`, `WorktreeCreate`, `WorktreeRemove`, `MessageDisplay`, `CwdChanged` | none | |

### 1.3 Common input fields [D][T][O]

| Field | Type | Presence |
|---|---|---|
| `session_id` | string | always |
| `transcript_path` | string | always. Written asynchronously and may lag; use `last_assistant_message` on Stop/SubagentStop |
| `cwd` | string | always. Follows `cd` and worktrees; `${CLAUDE_PROJECT_DIR}` does not |
| `hook_event_name` | string | always |
| `prompt_id` | string (UUID) | after the first user input; equals OTel `prompt.id`. v2.1.196+ |
| `permission_mode` | `"default"`, `"plan"`, `"acceptEdits"`, `"auto"`, `"dontAsk"`, `"bypassPermissions"` | not on all events. Manual mode is sent as `"default"`. [O] present on UserPromptSubmit, PreToolUse, PostToolUse, PostToolBatch and Stop; absent on SessionStart, SessionEnd and MessageDisplay |
| `effort` | `{"level": "low"\|"medium"\|"high"\|"xhigh"\|"max"}` | tool-use-context events (PreToolUse, PostToolUse, Stop, SubagentStop, …) on models that support effort. [O] also on PostToolBatch |
| `agent_id` | string | only inside a subagent |
| `agent_type` | string | inside a subagent, or on the main thread of a `--agent` session |
| `scratchpad_dir` | string | v2.1.257+ [D][O]. **Not declared** in TS `BaseHookInput` (0.3.289) or Python `BaseHookInput` [T] |

Only `SessionStart` receives `model`.

### 1.4 Environment for hook processes [D]

**Variables Claude Code sets:**
- `CLAUDE_PROJECT_DIR`, `CLAUDE_PLUGIN_ROOT`, `CLAUDE_PLUGIN_DATA`, `CLAUDE_PLUGIN_OPTION_<KEY>`. These are also usable as placeholders, such as `${CLAUDE_PROJECT_DIR}`.
- `CLAUDE_ENV_FILE`: SessionStart, Setup, CwdChanged and FileChanged only.
- `CLAUDE_EFFORT`.
- `CLAUDE_CODE_SESSION_ID`: matches `session_id` and updates on `/clear`.
- `CLAUDE_CODE_REMOTE`: `"true"` in cloud sessions.
- `CLAUDE_CODE_REMOTE_SESSION_ID`: cloud sessions.
- `CLAUDE_CODE_BRIDGE_SESSION_ID`: during Remote Control (v2.1.199+).
- `TRACEPARENT`: when tracing and propagation are on.

**Removed or absent:**
- All `OTEL_*` variables are stripped from every subprocess (v2.1.128+).
- `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1` strips credentials.
- There is no `$CLAUDE_MODEL`.

**Knobs that affect hooks:**
- `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`: default 8; `0` disables the cap.
- `CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS`.
- `CLAUDE_CODE_DISABLE_PERMISSION_PROMPT_NOTIFY_HOOKS`.
- `CLAUDE_CODE_DEBUG_LOG_LEVEL=verbose`, with `--debug-file`; the default debug log path is `~/.claude/debug/<session-id>.txt`.

Hooks run without a controlling TTY. To ring the terminal, use the `terminalSequence` output field instead of `/dev/tty`.

### 1.5 Exit codes, stdout parsing, HTTP results [D]

**Exit codes:**
- **Exit 0:** stdout is parsed as JSON if it starts with `{` and ends with `}`; otherwise it is plain text. Plain stdout becomes context only on `UserPromptSubmit`, `UserPromptExpansion`, `SessionStart` and `PostModelSwitch`; elsewhere it goes to the debug log. Stderr on exit 0 goes to the debug log only.
- **Exit 2:** blocking. JSON cannot override it. The block reason is the JSON reason if one is given, otherwise stderr. If the JSON fails validation, exit 2 still blocks (v2.1.214+).
- **Any other exit code:** if the JSON is valid it alone decides the outcome; otherwise it is a non-blocking error. Exit 1 does **not** block.

**Other outcomes:**
- Schema-invalid or unparseable JSON is a non-blocking `<hook> hook error`.
- **Timeout:** the hook is cancelled and its output discarded. On `PreToolUse` a timed-out command/http/mcp_tool hook lets the call continue, while an SDK callback that times out *blocks* the call. On `UserPromptSubmit` an SDK callback timeout blocks the prompt. On `PreModelSwitch` a timeout blocks the switch.
- **HTTP hooks:** 2xx with an empty body is success. 2xx with a JSON body is parsed like command output. Any other body, non-2xx status, or connection failure is a non-blocking error. HTTP status alone cannot block.
- **Size caps:** `additionalContext`, `systemMessage`, `initialUserMessage` and plain stdout are each capped at 10,000 characters. Over the cap, the output is saved to a file in the session directory and replaced by its path plus a 2,000-character preview.

**What exit 2 does, per event:**

| Event | Exit 2 effect |
|---|---|
| `PreToolUse` | blocks the tool call |
| `UserPromptSubmit` | blocks the prompt |
| `UserPromptExpansion` | blocks the expansion |
| `Stop`, `SubagentStop`, `TeammateIdle` | keep it running |
| `TaskCreated` | rolls back the task |
| `TaskCompleted` | prevents completion |
| `ConfigChange` | blocks the change (not for `policy_settings`) |
| `PostToolBatch` | stops the loop |
| `PreCompact` | blocks compaction |
| `PreModelSwitch` | blocks the switch |
| `Elicitation` | denies |
| `ElicitationResult` | turns the response into decline |
| `WorktreeCreate`, `WorktreeRemove` | any nonzero exit fails |
| `PostToolUse`, `PostToolUseFailure` | stderr is shown to Claude |
| `PermissionRequest` | not honored |
| `PermissionDenied`, `Notification`, `Setup`, `InstructionsLoaded`, `StopFailure` | ignored |
| `SubagentStart`, `SessionStart`, `SessionEnd`, `CwdChanged`, `FileChanged`, `PostCompact`, `PostModelSwitch` | stderr is shown to the user only |
| `DirectoryAdded` | stderr goes to the debug log |
| `MessageDisplay` | the original text is shown |

### 1.6 Universal JSON output fields [D][T]

| Field | Meaning |
|---|---|
| `continue` | Default `true`. `false` stops Claude and takes precedence over decisions |
| `stopReason` | Shown to the user when `continue:false`; stays in the conversation |
| `suppressOutput` | Accepted, **no effect** |
| `systemMessage` | Shown to the user. In the SDK and stream-json it can arrive as `SDKInformationalMessage` (v2.1.227+) |
| `terminalSequence` | OSC 0/1/2/9/99/777 and BEL only. Interactive sessions only; ignored in `-p` and the SDK |
| `decision`, `reason` | Top level. `decision` is `"block"`; the TS type also allows `"approve"`, a deprecated PreToolUse form |
| `hookSpecificOutput` | Must include `hookEventName` |

Python SDK callbacks write `continue_` and `async_` instead of `continue` and `async`. An async SDK callback returns `{async: true, asyncTimeout?}`.

### 1.7 Per-event input and output

Every event also receives the common fields from §1.3.

**SessionStart**
- Input: `source`; optional `model`, `agent_type`, `session_title`.
- On `source` `resume` or `fork` with at least one response (v2.1.251+): `seconds_since_last_response`, `context_tokens`, `prompt_cache_likely_expired`, `estimated_cache_write_usd` [D][T][O].
- `source:"fork"` was reported as `"resume"` before v2.1.214.
- Output (`hookSpecificOutput`): `additionalContext`, `initialUserMessage` (`-p` only), `sessionTitle` (ignored on clear and compact), `watchPaths`, `reloadSkills`.
- Plain stdout becomes context.

**Setup**
- Input: `trigger` (`init` or `maintenance`).
- All JSON output is discarded.
- In `-p` runs, output is visible only in `hook_response` events.

**InstructionsLoaded**
- Input: `file_path`, `memory_type` (`User`, `Project`, `Local`, `Managed`), `load_reason`, optional `globs`, `trigger_file_path`, `parent_file_path`.
- No output is honored.

**UserPromptSubmit**
- Input: `prompt` (pastes expanded, possibly inside `<pasted_content id=…>` lines), `session_title`.
- Output: top-level `decision:"block"` and `reason` (shown to the user, not to Claude); `hookSpecificOutput` with `additionalContext`, `sessionTitle`, `suppressOriginalPrompt`.
- Also fires for scheduled tasks, background-subagent reports, and peer messages.

**UserPromptExpansion**
- Input: `expansion_type` (`slash_command` or `mcp_prompt`), `command_name`, `command_args`, `command_source`, `prompt`.
- Output: `decision`, `reason`, `additionalContext`.

**MessageDisplay**
- Input: `turn_id`, `message_id` (not the API `msg_` ID), `index`, `final`, `delta`.
- In `-p` and the SDK it fires once per message with `index:0`, `final:true` [D][O].
- Output: `displayContent`. Display only; the transcript keeps the original.

**PreToolUse**
- Input: `tool_name`, `tool_input` (file paths are absolute), `tool_use_id`, and for MCP tools `mcp_server` `{name, source}` (v2.1.274+).
- Output (`hookSpecificOutput`):
  - `permissionDecision`: `allow`, `deny`, `ask`, or `defer`. Precedence is deny > defer > ask > allow.
  - `permissionDecisionReason`.
  - `updatedInput`: replaces the whole input.
  - `additionalContext`.
- Deny and ask rules are still evaluated after the hook.
- `"ask"` forces a prompt even in auto mode.
- `"defer"` works only in `-p` with exactly one tool call in the turn. The result then has `stop_reason:"tool_deferred"` and `deferred_tool_use{id,name,input}`; if the tool is gone at resume, `tool_deferred_unavailable`.
- `AskUserQuestion` and `ExitPlanMode` need `allow` plus `updatedInput`.
- Does not fire for `EndConversation` or for `@`-mentions.

**Tool input shapes [D]:**
- Bash and PowerShell: `command`, `description`, `timeout`, `run_in_background`.
- Write: `file_path`, `content`.
- Edit: `file_path`, `old_string`, `new_string`, `replace_all`.
- Read: `file_path`, `offset`, `limit`.
- Glob: `pattern`, `path`.
- Grep: `pattern`, `path`, `glob`, `output_mode`, `-i`, `multiline`.
- WebFetch: `url`, `prompt`.
- WebSearch: `query`, `allowed_domains`, `blocked_domains`.
- Agent: `prompt`, `description`, `subagent_type`, `model`.
- AskUserQuestion: `questions`, `answers`.
- ExitPlanMode: `plan`, `planFilePath` (both injected).

**PermissionRequest**
- Input: `tool_name`, `tool_input` (no `tool_use_id`), `mcp_server`, `permission_suggestions[]`.
- Output: `hookSpecificOutput.decision` with:
  - `behavior`: `allow` or `deny`
  - `updatedInput` (allow only)
  - `updatedPermissions` (allow only)
  - `message` (deny only)
  - `interrupt` (deny only)
- Permission update entries:
  - `type`: `addRules`, `replaceRules`, `removeRules`, `setMode`, `addDirectories`, or `removeDirectories`.
  - Fields: `rules[{toolName,ruleContent?}]`, `behavior`, `mode`, `directories`.
  - `destination`: `session`, `localSettings`, `projectSettings`, or `userSettings`; the TS type also has `cliArg`.
- Runs alongside `canUseTool`; whichever answers first wins. In a no-prompt session with no decision, the call is auto-denied.

**PostToolUse**
- Input: `tool_input`, `tool_response` (the tool's structured output), `tool_use_id`, `duration_ms`, `mcp_server`.
- Bash responses can carry `tool_response.bashEditDiff`, a beta (v2.1.269+): `{changedFiles, files, moreFiles, unavailable, skipped, shared}`.
- Agent `tool_response`:
  - completed: `status` (`completed` or `async_launched`), `agentId`, `content`, `resolvedModel`, `modelsUsed`, `totalTokens` (final request only), `totalDurationMs`, `totalToolUseCount`, `usage`.
  - async_launched: `status`, `agentId`, `description`, `prompt`, `outputFile`, `resolvedModel`.
- Output: `decision:"block"`, `reason`, `additionalContext`, `classifierContext` (v2.1.236+, capped at 2,000 characters), `updatedToolOutput` (must match the tool's output shape), `updatedMCPToolOutput` (deprecated).
- OTel spans and events capture the *original* output, before the hook rewrites it.

**PostToolUseFailure**
- Input: `tool_name`, `tool_input`, `tool_use_id`, `error`, `is_interrupt`, `duration_ms`, `mcp_server`.
- Not fired for validation failures or permission denials.
- Output: `additionalContext`.

**PostToolBatch**
- Input: `tool_calls[]` of `{tool_name, tool_input, tool_use_id, tool_response}`. Here `tool_response` is the serialized `tool_result` content the model sees.
- Output: `additionalContext`. `decision:"block"` or `continue:false` stops the loop.

**PermissionDenied**
- Auto mode only.
- Input: `tool_name`, `tool_input`, `tool_use_id`, `reason`, `mcp_server`. The `reason` is a matched rule such as `[Data Exfiltration]`, text starting `Auto mode could not evaluate this action…`, or `Classifier unavailable`.
- Output: `hookSpecificOutput.retry:true`. It is ignored for denials with no classifier verdict, and prompt/agent hooks cannot set it.

**Notification**
- Input: `message`, `title?`, `notification_type`.
- Only `terminalSequence` is honored.

**SubagentStart**
- Input: `agent_id`, `agent_type`.
- Also fires on subagent resume and for each message an in-process teammate handles.
- Output: `additionalContext`, injected into the subagent.

**SubagentStop**
- Input: `stop_hook_active`, `agent_id`, `agent_type` (empty string for internal agents), `agent_transcript_path`, `last_assistant_message`, `background_tasks`, `session_crons`.
- Output: same as Stop.
- With `SubagentHandback` (v2.1.271+), the report is in that tool's `tool_input.message`, not in `last_assistant_message`.

**Stop**
- Input: `stop_hook_active`, `last_assistant_message`, `background_tasks[]`, `session_crons[]`.
  - `background_tasks[]` entries: `id`, `type`, `status`, `description`, and optionally `command`, `agent_type`, `server`, `tool`, `name`.
  - `session_crons[]` entries: `id`, `schedule`, `recurring`, `prompt`.
- Output: `decision:"block"` with `reason` (required), or `hookSpecificOutput.additionalContext`.
- Hooks can continue the turn at most 8 times in a row.

**StopFailure**
- Input: `error`, `error_details?`, `last_assistant_message?` (the API error string).
- Only `terminalSequence` is honored.

**TaskCreated / TaskCompleted**
- Input: `task_id`, `task_subject`, `task_description?`, `teammate_name?`, `team_name?` (deprecated).
- TaskCreated is blocked by exit 2 or `decision:"block"`.
- TaskCompleted is blocked by exit 2; `continue:false` applies only when triggered by a teammate.

**TeammateIdle**
- Input: `teammate_name`, `team_name` (deprecated).
- Controlled by exit 2 or `continue:false`.

**ConfigChange**
- Input: `source`, `file_path?`.
- `decision:"block"`; `reason` is accepted but never shown.

**CwdChanged**
- Input: `old_cwd`, `new_cwd`.
- Output: `watchPaths`, `systemMessage`.

**DirectoryAdded**
- Input: `directory`, `source`.
- Runs asynchronously.

**FileChanged**
- Input: `file_path`, `event` (`change`, `add`, or `unlink`).
- Output: `watchPaths`.

**WorktreeCreate**
- Input: `name`.
- Output: a command hook prints the path as the last line of stdout; an HTTP hook returns `hookSpecificOutput.worktreePath`.

**WorktreeRemove**
- Input: `worktree_path`.
- Controlled by exit code only.

**PreCompact**
- Input: `trigger`, `custom_instructions` (string, or `null` for auto).
- Can block with exit 2 or `decision:"block"`.

**PostCompact**
- Input: `trigger`, `compact_summary`.
- Observational only.

**PreModelSwitch** (v2.1.251+)
- Input: `from_model`, `to_model`, `requested_model`, `source` (`command`, `picker`, or `sdk`), `context_tokens`, `prompt_cache_warm`, `cache_ttl` (`5m` or `1h`), `estimated_cache_write_usd`, `pricing` (`configured`, `catalog`, or `default`).
- Output: `permissionDecision` (allow, deny, or ask; ask counts as deny outside interactive `/model`), `permissionDecisionReason`, or `decision:"block"`.

**PostModelSwitch**
- Input: same as PreModelSwitch, plus `source` values `auto` and `resume`.
- Output: `additionalContext`.

**SessionEnd**
- Input: `reason`.
- No output is honored.

**Elicitation**
- Input: `mcp_server_name`, `message`, `mode?` (`form` or `url`), `url?`, `elicitation_id?`, `requested_schema?`.
- Output: `action` (`accept`, `decline`, or `cancel`), `content`.

**ElicitationResult**
- Input: `mcp_server_name`, `action`, `content?`, `mode?`, `elicitation_id?`.
- Output: `action`, `content` override.

### 1.8 Async hooks and LLM-judged hooks [D]

**Async hooks:**
- `async: true` on a command hook runs it in the background. Decision fields have no effect.
- `additionalContext` and `systemMessage` are delivered on the next turn.
- `timeout` is not enforced, except with `asyncRewake`.
- In `-p`, still-running async hooks are killed at teardown with outcome `cancelled`.

**Prompt and agent hooks:**
- The model must return `{"ok": bool, "reason": str, "impossible": bool}`.
- On Stop and SubagentStop, `ok:false` feeds the reason back to Claude, unless `impossible` is set.
- On PreToolUse, `ok:false` denies the call and ends the turn, unless `continueOnBlock:true`.
- On PostToolUse, `ok:false` ends the turn, unless `continueOnBlock`.
- On PostToolBatch, UserPromptSubmit and UserPromptExpansion, `ok:false` ends the turn.
- On PostToolUseFailure and TaskCreated, the reason becomes a tool error.
- On PermissionRequest and PermissionDenied, `ok:false` has no effect.

### 1.9 Hook events in the Agent SDK [D][T]

**TypeScript:**
- `HookEvent` covers all 33 events above.
- `HookCallback(input, toolUseID, {signal}) => Promise<HookJSONOutput>`.
- `HookCallbackMatcher {matcher?, hooks[], timeout?}` (seconds).

**Python** (`types.py` main, `HookEvent`): only `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `UserPromptSubmit`, `Stop`, `SubagentStop`, `PreCompact`, `Notification`, `SubagentStart`, `PermissionRequest`.
- `SessionStart` and `SessionEnd` are available only as shell hooks loaded through `setting_sources`.
- Python `BaseHookInput` declares only `session_id`, `transcript_path`, `cwd` and `permission_mode`. `agent_id` and `agent_type` come through a mixin on tool-lifecycle hooks only.

## 2. OpenTelemetry (https://code.claude.com/docs/en/monitoring-usage)

I could not see console-exporter output in this container (likely policy), so this section is **[D]** only, not observed.

### 2.1 Enabling and exporting

**Required and per-signal switches:**
- `CLAUDE_CODE_ENABLE_TELEMETRY=1` is required.
- `OTEL_METRICS_EXPORTER`: `otlp`, `prometheus` (port 9464), `console`, `none`. Comma-separated values allowed.
- `OTEL_LOGS_EXPORTER`: `otlp`, `console`, `none`.
- `OTEL_TRACES_EXPORTER`: needs `CLAUDE_CODE_ENHANCED_TELEMETRY_BETA=1` (alias `ENABLE_ENHANCED_TELEMETRY_BETA`).

**Transport:**
- `OTEL_EXPORTER_OTLP_PROTOCOL`: `grpc`, `http/json`, `http/protobuf`. There is no default.
- `OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_EXPORTER_OTLP_HEADERS`.
- Per-signal variants: `OTEL_EXPORTER_OTLP_{METRICS,LOGS,TRACES}_{PROTOCOL,ENDPOINT,HEADERS}`. Per-signal headers merge with the generic ones.
- mTLS: `CLAUDE_CODE_CLIENT_CERT`, `CLAUDE_CODE_CLIENT_KEY`, `CLAUDE_CODE_CLIENT_KEY_PASSPHRASE` and `NODE_EXTRA_CA_CERTS` for http; `OTEL_EXPORTER_OTLP_CLIENT_KEY`, `OTEL_EXPORTER_OTLP_CLIENT_CERTIFICATE` and `OTEL_EXPORTER_OTLP_CERTIFICATE` for grpc.
- `OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE`: default `delta`.

**Intervals and timeouts:**
- `OTEL_METRIC_EXPORT_INTERVAL`: default 60000.
- `OTEL_LOGS_EXPORT_INTERVAL`: default 5000.
- `OTEL_TRACES_EXPORT_INTERVAL`: default 5000.
- `CLAUDE_CODE_OTEL_FLUSH_TIMEOUT_MS`: default 5000.
- `CLAUDE_CODE_OTEL_SHUTDOWN_TIMEOUT_MS`: default 2000.
- `CLAUDE_CODE_OTEL_DIAG_STDERR=1` writes exporter errors to stderr (v2.1.179+).

**Dynamic headers:**
- `otelHeadersHelper` setting: a script that prints a JSON object of headers. http protocols only.
- Refreshed every `CLAUDE_CODE_OTEL_HEADERS_HELPER_DEBOUNCE_MS`, default 1740000.

**Identity and service name:**
- `OTEL_RESOURCE_ATTRIBUTES` (comma-separated key=value, no spaces, percent-encode) and `OTEL_SERVICE_NAME`.
- Custom keys never override built-in attributes, except `vcs.*`.

**Where variables are honored:**
- Exporter, endpoint and content variables are ignored in project and local settings (v2.1.282+). Off values still apply there.
- Managed `OTEL_EXPORTER_OTLP_*` values strip developer-set per-signal endpoints, protocols and credentials (v2.1.217+).
- When managed settings decide the destination, a developer-set `BETA_TRACING_ENDPOINT` is removed (v2.1.251).

**SDK specifics:**
- Do **not** use the `console` exporter under the SDK; it writes to stdout, which is the SDK channel.
- TypeScript `env` *replaces* `process.env`; Python merges.

### 2.2 Content and detail gates (everything below is off by default)

| Variable | Adds |
|---|---|
| `OTEL_LOG_USER_PROMPTS=1` | `prompt`/`prompt_text` on `user_prompt`; `user_prompt` on the interaction span; detailed-beta content |
| `OTEL_LOG_ASSISTANT_RESPONSES` | `response` on `assistant_response` (v2.1.193+). If unset, falls back to `OTEL_LOG_USER_PROMPTS`; set `0` to keep responses redacted |
| `OTEL_LOG_TOOL_DETAILS=1` | `tool_parameters`/`tool_input` on tool events; full `error`; MCP, skill and agent names; span `file_path`, `full_command`, `skill_name`, `subagent_type`; real attribution names on metrics (v2.1.273); `vcs.ref.head.*`; refusal `category`; `server_name` |
| `OTEL_LOG_TOOL_CONTENT=1` | The `tool.output` span event (tracing required) |
| `OTEL_LOG_RAW_API_BODIES` | `=1`: inline `api_request_body`/`api_response_body` events, truncated. `=file:<dir>`: untruncated `<dir>/<uuid>.request.json` and `<dir>/<request_id>.response.json` files, `body_ref`, and `<dir>/index.jsonl` (v2.1.274+) |
| `OTEL_LOG_MANAGED_SETTINGS=1` | Redacted settings and a SHA-256 digest on `managed_settings_resolved` (v2.1.274+) |
| `ENABLE_BETA_TRACING_DETAILED=1` + `BETA_TRACING_ENDPOINT` | The `claude_code.hook` span and content attributes. Logs and traces go to `BETA_TRACING_ENDPOINT` instead. Interactive CLI needs an org allowlist; `-p` and the SDK do not. Ignored in project and local settings |

### 2.3 Cardinality controls and attributes on every signal

**Cardinality switches:**

| Variable | Default | Controls |
|---|---|---|
| `OTEL_METRICS_INCLUDE_SESSION_ID` | true | `session.id`, `ccr.session.id` |
| `OTEL_METRICS_INCLUDE_VERSION` | false | `app.version` |
| `OTEL_METRICS_INCLUDE_ACCOUNT_UUID` | true | `user.account_uuid`, `user.account_id` |
| `OTEL_METRICS_INCLUDE_ENTRYPOINT` | false | `app.entrypoint`: `cli`, `sdk-cli`, `sdk-ts`, `sdk-py`, `claude-vscode`, `claude-in-slack` |
| `OTEL_METRICS_INCLUDE_RESOURCE_ATTRIBUTES` | true | Puts `OTEL_RESOURCE_ATTRIBUTES` keys on datapoints |
| `OTEL_METRICS_INCLUDE_REPOSITORY` | false | `vcs.repository.url.full`, `vcs.owner.name`, `vcs.repository.name`, `vcs.provider.name` (v2.1.269+) |

**Always included when available:** `organization.id`, `user.id` (an install-scoped random ID from `~/.claude.json`), `user.email`, `terminal.type`. Gateway sessions add `user.groups` and `identity.source: gateway-oidc`.

**Events only, never metrics:** `prompt.id`, `workspace.host_paths`, `workflow.run_id`, `workflow.name`.

**Resource block:**
- `service.name`: `claude-code`, or `claude-code-desktop` for the Desktop Code tab.
- `service.version`, `os.type`, `os.version`, `host.arch`, `wsl.version`.
- Meter name: `com.anthropic.claude_code`.

### 2.4 Metrics

| Name | Unit | Extra attributes |
|---|---|---|
| `claude_code.session.count` | none | `start_type` (`fresh`, `resume`, `continue`, `agents_view`) |
| `claude_code.lines_of_code.count` | none | `type` (`added` or `removed`), `model` (v2.1.172+) |
| `claude_code.pull_request.count` | none | (includes MCP-created PRs, v2.1.129+) |
| `claude_code.commit.count` | none | |
| `claude_code.cost.usage` | USD | `model`, `query_source` (`main`, `subagent`, `auxiliary`), `speed` (`fast`), `effort`, `agent.name`, `skill.name`, `plugin.name`, `marketplace.name`, `mcp_server.name`, `mcp_tool.name` |
| `claude_code.token.usage` | tokens | `type` (`input`, `output`, `cacheRead`, `cacheCreation`; `input` excludes cache) plus the same attributes as cost |
| `claude_code.code_edit_tool.decision` | none | `tool_name` (`Edit`, `Write`, `NotebookEdit`), `decision` (`accept` or `reject`), `source`, `language` |
| `claude_code.active_time.total` | s | `type` (`user` or `cli`) |

- With `prometheus` as the only exporter, the units are dropped.
- Redaction placeholders are `"custom"` and `"third-party"`.
- There are no `gen_ai.usage.*` attributes. To get the GenAI input total, add `input` + `cacheRead` + `cacheCreation`.

### 2.5 Log events

Every event carries the standard attributes plus `event.name`, `event.timestamp` (ISO 8601), `event.sequence` (per-process counter starting at 0; sort by timestamp first) and `prompt.id`. Attribute types are as documented; "string bool" means the value is `"true"` or `"false"`.

**`claude_code.user_prompt`**
- `prompt_length`
- `prompt` (redacted)
- `prompt_text` (v2.1.287+)
- `message.uuid` (v2.1.214+)
- `command_name`, `command_source` (`builtin`, `custom`, or `mcp`)

**`claude_code.assistant_response`** (v2.1.193+)
- `response_length`
- `response` (redacted)
- `model`, `request_id`, `message.uuid`, `query_source`
- Text blocks only; no thinking or tool_use.

**`claude_code.tool_result`**
- `tool_name`, `tool_use_id`, `success` (string bool), `duration_ms`, `error_type`
- `error` (needs DETAILS)
- `decision_type` (always `accept`), `decision_source` (`config`, `hook`, `user_permanent`, `user_temporary`)
- `tool_input_size_bytes`, `tool_result_size_bytes`, `mcp_server_scope`
- `vcs.ref.head.revision`, `vcs.ref.head.name`, `vcs.ref.head.type` (needs DETAILS)
- `tool_parameters`, a JSON string (needs DETAILS). By tool:
  - Bash: `bash_command`, `full_command`, `timeout`, `description`, `dangerouslyDisableSandbox`, `git_commit_id`, `git_branch`
  - MCP: `mcp_server_name`, `mcp_tool_name`
  - Skill: `skill_name`
  - Agent: `subagent_type`
- `tool_input` (needs DETAILS): each value capped at 512 characters, about 4K characters total.

**`claude_code.api_request`**
- `model`, `cost_usd`, `cost_usd_micros` (int), `duration_ms`
- `input_tokens`, `output_tokens`, `cache_read_tokens`, `cache_creation_tokens`
- `request_id`, `client_request_id`, `speed`, `query_source`, `effort`
- attribution attributes
- Numeric values are emitted as numbers (v2.1.122+).

**`claude_code.api_error`**
- `model`, `error`, `status_code` (number), `duration_ms`
- `attempt`: total attempts; 11 by default when retries are exhausted
- `request_id`, `client_request_id`, `speed`, `query_source`, `effort`
- attribution attributes
- Emitted only once, after the final attempt.

**`claude_code.api_refusal`**
- `model`, `request_id`, `query_source`, `speed`, `attempt`, `effort`
- `server_fallback_hop`, `has_category`, `has_explanation` (booleans)
- `category` (needs DETAILS)
- attribution attributes

**`claude_code.api_retries_exhausted`**
- `model`, `error`, `status_code`, `total_attempts`, `total_retry_duration_ms`, `speed`

**`claude_code.api_request_body`**
- `body` or `body_ref`, `body_length`, `body_truncated`, `model`, `query_source`, `request_body_id` (v2.1.274+)
- Thinking content is always redacted.

**`claude_code.api_response_body`**
- `body` or `body_ref`, `body_length`, `body_truncated`, `model`, `query_source`, `request_id`
- `request_body_id`, `message.id`, `message.uuid` (v2.1.274+)
- File-mode `index.jsonl` fields: `timestamp`, `session_id`, `query_source`, `model`, `request_id`, `message_id`, `message_uuid`, `request_file`, `response_file`.

**`claude_code.tool_decision`**
- `tool_name` (the literal `"mcp_tool"` for user MCP tools), `tool_use_id`
- `decision` (`accept` or `reject`)
- `tool_source` (`builtin`, `mcp`, `sdk_host_builtin_mcp`; v2.1.214+)
- `source`:
  - `config`: rules, flags, mode, session grant, safe tool, or a failed prompt request
  - `hook`
  - `user_permanent`
  - `user_temporary`
  - `user_abort`
  - `user_reject`
- `tool_parameters` (needs DETAILS)
- There is **no** `classifier` source value in OTel; which `source` an auto-mode classifier verdict reports is **[U]**. `classifier` exists only as SDK `decision_reason_type`.

**`claude_code.permission_mode_changed`**
- `from_mode`, `to_mode`
- `trigger`: `shift_tab`, `exit_plan_mode`, `auto_gate_denied`, or `auto_opt_in`; absent for SDK-originated changes.

**`claude_code.auth`**
- `action`, `success`, `auth_method`, `error_category`, `status_code` (string)

**`claude_code.mcp_server_connection`**
- `status` (`connected`, `failed`, `disconnected`), `transport_type`, `server_scope`, `duration_ms`, `error_code`
- `is_plugin`, `plugin_id_hash`, `plugin.name`
- `server_name`, `error` (need DETAILS)

**`claude_code.internal_error`**
- `error_name`, `error_code`
- Not emitted on Bedrock, Vertex or Foundry, or with `DISABLE_ERROR_REPORTING`.

**`claude_code.plugin_installed`**
- `marketplace.is_official`, `install.trigger`, `plugin.name`, `plugin.version`, `marketplace.name`

**`claude_code.plugin_loaded`**
- `plugin.name`, `marketplace.name`, `plugin.version`
- `plugin.scope`, `enabled_via`, `plugin_id_hash`
- `has_hooks`, `has_mcp`, `host_owned_mcp`
- `skill_path_count`, `command_path_count`, `agent_path_count`, `safe_mode`

**`claude_code.skill_activated`**
- `skill.name` (`custom_skill` when redacted)
- `invocation_trigger` (`user-slash`, `claude-proactive`, `nested-skill`)
- `skill.source`, `skill.kind`, `plugin.name`, `marketplace.name`

**`claude_code.at_mention`**
- `mention_type` (`file`, `directory`, `agent`, `mcp_resource`, `peer`)
- `success`

**`claude_code.hook_registered`**
- `hook_event`, `hook_type`
- `hook_source` (`userSettings`, `projectSettings`, `localSettings`, `flagSettings`, `policySettings`, `pluginHook`)
- `safe_mode`, `hook_matcher` (needs DETAILS), `plugin.name`, `plugin_id_hash`

**`claude_code.hook_execution_start`**
- `hook_event`, `hook_name` (such as `PreToolUse:Write`), `num_hooks`
- `managed_only`, `hook_source` (`policySettings` or `merged`), `safe_mode`
- `hook_definitions` (needs detailed beta and DETAILS)

**`claude_code.hook_execution_complete`**
- All the start fields, plus:
- `num_success`, `num_blocking`, `num_non_blocking_error`, `num_cancelled`, `total_duration_ms`
- `stdout_chars`, `additional_context_chars`, `system_message_chars`, `initial_user_message_chars`, `num_outputs_persisted` (v2.1.280+)

**`claude_code.hook_plugin_metrics`**
- `plugin_id`, `hook_event`, and up to 20 keys matching `^[a-z][a-z0-9_]{0,39}$`
- Official-marketplace plugins only.

**`claude_code.compaction`**
- `trigger`, `success`, `duration_ms`, `pre_tokens`, `post_tokens`, `error`
- `precompute_reuse` (`hit`, `miss_custom_instructions`, `miss_hook`, `miss_not_ready`; manual only; v2.1.153+)
- **No summary text.**

**`claude_code.subagent_completed`**
- `agent_type` (`custom` when redacted), `agent.source`, `is_built_in`, `is_async`
- `total_tokens`: final request only
- `total_tool_uses`, `duration_ms`, `model`
- `final_model`, `model_swapped` (v2.1.212+)
- `plugin_id_hash`, `plugin.name`

**`claude_code.feedback_survey`**
- `event_type`, `appearance_id`, `survey_type`, `response`, `enabled_via_override` (bool)

**`claude_code.retention_sweep`** (v2.1.227+)
- `result` (`complete` or `skipped`), `period_days`, `used_default`
- `skip_reason`: `user_source_disabled`, `settings_unknowable`, or `settings_invalid_key_set`
- `transcripts_deleted`, `transcripts_exempted_desktop`, `session_files_deleted`, `artifacts_deleted`
- `files_retained_fresh`, `files_past_cutoff`, `error_count`

**`claude_code.managed_settings_resolved`** (v2.1.274+)
- `managed_settings.trigger` (`startup`, `change`, `refused`)
- `error.type`: `helper_failed`, `policy_invalid`, `provider_not_allowed`, `consent_rejected`, `force_refresh_failed`, `gateway_rejected`, `version_below_minimum`, `_OTHER`
- `managed_settings.sources[]`, `managed_settings.source_behavior`
- `managed_settings.helper.state`, `managed_settings.helper.applied`, `managed_settings.helper.entry`, `managed_settings.helper.path`
- `managed_settings.resolved_sha256`, `managed_settings.settings` (cut at 8 KB), `managed_settings.settings_truncated` (bool)

**`claude_code.system_prompt`**
- Detailed beta with `OTEL_LOG_USER_PROMPTS=1` only.
- The full system prompt, sent once per distinct prompt and again after compaction.

**Joining events to transcripts:** `message.uuid` matches transcript `uuid`; `request_id` matches `requestId`; `tool_use_id` matches hook `tool_use_id`. The docs call these joins "version-specific rather than a stable contract".

### 2.6 Spans (beta)

Every span carries the standard attributes and `span.type`. `llm_request`, `tool.execution` and `hook` set status ERROR on failure; others end UNSET. Tracing is beta and span names and attributes may change.

**`claude_code.interaction`**
- `user_prompt` (redacted), `user_prompt_length`
- `interaction.sequence`
- `parent.source` (`env` or `none`; v2.1.268+)
- `interaction.duration_ms`

**`claude_code.llm_request`**
- `model`, `gen_ai.system` (`anthropic`), `gen_ai.request.model`
- `query_source` (detailed beta only); `query_source_safe` (v2.1.268+; values such as `agent.custom` or `agent.builtin.general-purpose`)
- `agent_id`, `parent_agent_id`, `workflow.run_id`, `workflow.name`
- `speed`, `effort` (v2.1.274+)
- `llm_request.context` (`interaction`, `tool`, `standalone`)
- `duration_ms`, `ttft_ms`, `first_content_ms` (v2.1.268+)
- `input_tokens`, `output_tokens`, `cache_read_tokens`, `cache_creation_tokens`
- `request_id`, `gen_ai.response.id`, `client_request_id`, `attempt`, `success`
- `status_code`, `error`, `error_class` (v2.1.268+)
- `response.has_tool_call`, `stop_reason`, `gen_ai.response.finish_reasons`
- Span event `gen_ai.request.attempt` with `attempt` and `client_request_id`.

**`claude_code.tool`**
- `tool_name`, `tool_name_safe`
- `bash_command_class`, `bash_argv0` (v2.1.268+)
- `duration_ms` (includes the permission wait), `result_tokens`
- `agent_id`, `parent_agent_id`, `workflow.run_id`, `workflow.name`
- `tool_use_id`, `gen_ai.tool.call.id`
- `file_path`, `full_command`, `skill_name`, `subagent_type` (need DETAILS)
- Span event `tool.output` (needs `OTEL_LOG_TOOL_CONTENT=1`):
  - Recorded for Read and Bash; Edit and Write also need DETAILS; MCP, WebFetch and WebSearch need v2.1.283+.
  - Attributes: `content`, `output`, `diff`, `file_path`, `bash_command`.
  - A truncated attribute adds `<attr>_truncated` and `<attr>_original_length`.
  - Not recorded for: error returns, non-text Read results, or backgrounded WebFetch/WebSearch calls.

**`claude_code.tool.blocked_on_user`**
- `duration_ms`, `decision` (`accept` or `reject`), `source`

**`claude_code.tool.execution`**
- `duration_ms`, `tool_use_id`, `gen_ai.tool.call.id`, `success`, `error` (full message with DETAILS), `error_class`

**`claude_code.hook`** (detailed beta only)
- `hook_event`, `hook_name`, `num_hooks`, `hook_definitions` (needs DETAILS), `duration_ms`
- `num_success`, `num_blocking`, `num_non_blocking_error`, `num_cancelled`

**Detailed-beta content attributes:**
- `new_context`: interaction or llm_request, gated by USER_PROMPTS; tool, gated by TOOL_CONTENT.
- `system_reminders`, `system_prompt_preview` (first 500 characters), `user_system_prompt` (once per session), `response.model_output`: all on llm_request, gated by USER_PROMPTS.
- `tool_input` on tool, gated by DETAILS.

**Hierarchy:**
- `interaction` contains `llm_request`, `hook` and `tool`. `tool` contains `blocked_on_user` and `execution`.
- Subagent `llm_request` and `tool` spans nest under the parent's Agent `claude_code.tool` span.
- A deferred tool, resumed later, rejoins the original turn's trace.

### 2.7 Propagation [D]

**Outbound:**
- Bash, PowerShell and hook subprocesses get `TRACEPARENT`, set from the active tool execution span.
- Model requests to the Anthropic API carry `traceparent` from the `llm_request` span, and the API's `traceresponse` header is recorded as a span link.
- HTTP MCP requests carry `traceparent`.
- This happens only when `ANTHROPIC_BASE_URL` is unset or points at Anthropic. Set `CLAUDE_CODE_PROPAGATE_TRACEPARENT=1` for proxies (v2.1.152+).
- Never sent to third-party providers.

**Inbound:**
- `-p` and SDK sessions read `TRACEPARENT` and `TRACESTATE` (v2.1.110+), so `interaction` becomes a child of the caller's span.
- Log records then carry `trace_id` and `span_id` even with no traces exporter (v2.1.212/214 fixes).
- The TypeScript and Python SDKs auto-inject these from the active span, unless you set them yourself in `env`.
- Interactive sessions ignore inbound `TRACEPARENT`.

### 2.8 Limits [D]

- `CLAUDE_CODE_OTEL_CONTENT_MAX_LENGTH`: default 61440 UTF-16 units (60 KB), marker included (v2.1.214+). It is clamped to `OTEL_ATTRIBUTE_VALUE_LENGTH_LIMIT`, `OTEL_LOGRECORD_ATTRIBUTE_VALUE_LENGTH_LIMIT` or `OTEL_SPAN_ATTRIBUTE_VALUE_LENGTH_LIMIT` if smaller.
- `tool_input` on events: 512 characters per value, about 4K total.
- `full_command` in `tool_parameters` is untruncated.
- `managed_settings.settings`: 8 KB.

### 2.9 Redacted by default and never exported

**Redacted unless opted in:** prompts, responses, tool arguments, tool content, raw bodies, MCP server and tool names for user-configured servers, custom agent, skill and plugin names, and third-party plugin names.

**Never exported** [D]: raw file contents and code in metrics and events (spans are a separate path). Thinking is excluded from `assistant_response` and redacted from raw bodies "regardless of other settings".

**Not exported by any documented signal** [D/U]:
- The compaction summary text (it is in the `PostCompact` hook and in the transcript instead).
- Hook stdout or stderr content (only character counts).
- Per-retry events (only the final `api_error`).

`PostToolUse` `updatedToolOutput` rewrites are invisible to OTel, which records the original output.

## 3. Agent SDK

### 3.1 `SDKMessage` union, verbatim from `sdk.d.ts` 0.3.289 [T]

```
SDKAssistantMessage | SDKUserMessage | SDKUserMessageReplay | SDKResultMessage | SDKSystemMessage | SDKPartialAssistantMessage | SDKCompactBoundaryMessage | SDKStatusMessage | SDKAPIRetryMessage | SDKControlRequestProgressMessage | SDKModelRefusalFallbackMessage | SDKModelRefusalNoFallbackMessage | SDKLocalCommandOutputMessage | SDKHookStartedMessage | SDKHookProgressMessage | SDKHookResponseMessage | SDKPluginInstallMessage | SDKToolProgressMessage | SDKAuthStatusMessage | SDKTaskNotificationMessage | SDKTaskStartedMessage | SDKTaskUpdatedMessage | SDKTaskProgressMessage | SDKBackgroundTasksChangedMessage | SDKThinkingTokensMessage | SDKSessionStateChangedMessage | SDKWorkerShuttingDownMessage | SDKCommandsChangedMessage | SDKNotificationMessage | SDKFilesPersistedEvent | SDKToolUseSummaryMessage | SDKMemoryRecallMessage | SDKRateLimitEvent | SDKElicitationCompleteMessage | SDKPermissionDeniedMessage | SDKPromptSuggestionMessage | SDKMirrorErrorMessage | SDKInformationalMessage | SDKConversationResetMessage
```

The docs page's union omits `SDKControlRequestProgressMessage` and both refusal-fallback types. The type comment says: "Consumers should ignore types and subtypes they do not recognize: the set grows over time."

Every message has `uuid` and `session_id`.

**Conversation messages:**
- **`assistant`:** `message` (a `BetaMessage`, emitted once per content block; `stop_reason` and `usage` are not final), `parent_tool_use_id`, `error?` (an `SDKAssistantMessageError` enum, same values as StopFailure), `aborted?`, `timestamp?`, `context_usage?`, `request_id?` [T], `user_message_uuid?`, `user_message_uuids?`, `resume_reason?`.
- **`user`:** `message`, `parent_tool_use_id`, `isSynthetic?`, `shouldQuery?`, `client_composed?`, `tool_use_result?` (structured tool output), `priority?` (`now`, `next`, `later`), `origin?`, `pasted_content?`, `inline_pastes?`. A replay adds `isReplay: true` and a required `uuid`.
- **`stream_event`:** `event` (`BetaRawMessageStreamEvent`), `parent_tool_use_id` (always null), `ttft_ms?`, plus the `user_message_uuid*` fields. Requires `includePartialMessages`.

**`result`, subtype `success`:**
- Timing and counts: `duration_ms`, `duration_api_ms`, `is_error`, `api_error_status?`, `num_turns`, `result`, `stop_reason`, `ttft_ms?`, `ttft_stream_ms?`, `first_content_frame_ms?`, `request_sent_wall_ms?`.
- Uploads to claude.ai only: `first_stream_post_*`, `first_text_post_*`.
- Cost and usage:
  - `total_cost_usd`: cumulative across turns in streaming input; an estimate.
  - `usage` (`NonNullableUsage`): main loop only.
  - `modelUsage{[model]: ModelUsage}`.
- `permission_denials[]` of `{tool_name, tool_use_id, tool_input}`.
- Other fields: `queued_turn_count?`, `structured_output?`, `deferred_tool_use?`, `terminal_reason?`, `result_index?`, `local_command?`, `fast_mode_state?`, `fast_mode_disabled_reason?`, `origin?`, `user_message_uuid(s)?`, `resume_reason?`.

**`result`, error subtypes** `error_max_turns`, `error_during_execution`, `error_max_budget_usd`, `error_max_structured_output_retries`:
- Same core fields, plus `errors: string[]`.
- `startup_failure_reason?`: `org_pin_api_key_conflict`, `provider_not_allowed`, `org_verify_failed`, `org_pin_mismatch`, `managed_settings_invalid`, `remote_settings_required_unavailable`, `gateway_signin_required`, `gateway_access_denied`, `proxy_invalid`, `temp_dir_unusable`, `cwd_unavailable`, `shell_tool_missing`, `session_held_by_background`, `worktree_resume_refused`, `worktree_unverified`, `cli_version_too_old`, `bypass_root`.
- No `result` field.

**`terminal_reason` values:** `completed`, `max_turns`, `tool_deferred`, `aborted_streaming`, `aborted_tools`, `hook_stopped`, `stop_hook_prevented`, `background_requested`, `blocking_limit`, `rapid_refill_breaker`, `prompt_too_long`, `image_error`, `model_error`, `api_error`, `malformed_tool_use_exhausted`, `budget_exhausted`, `structured_output_retry_exhausted`, `tool_deferred_unavailable`, `turn_setup_failed`.

**`ModelUsage` fields:** `inputTokens`, `outputTokens`, `thinkingTokens?`, `cacheReadInputTokens`, `cacheCreationInputTokens`, `webSearchRequests`, `costUSD`, `contextWindow`, `maxOutputTokens`, `canonicalModel?`, `provider?`, `costBasis?` (`list`, `managed`, `unknown`).

**`Usage` fields:** `input_tokens`, `output_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens`, `cache_creation{ephemeral_5m_input_tokens, ephemeral_1h_input_tokens}`, `server_tool_use`, `service_tier`, `speed`, `inference_geo`, `iterations`, `output_tokens_details{thinking_tokens}`.

**System messages (`type:"system"`), by subtype:**
- **`init`:** `agents?`, `apiKeySource`, `betas?`, `claude_code_version`, `cwd`, `tools`, `mcp_servers[{name,status,source?}]`, `mcp_server_errors?` (headless docs), `model`, `permissionMode`, `slash_commands`, `terminal_slash_commands?`, `output_style`, `skills`, `plugins[{name,path,version?}]`, `plugin_errors?`, `fast_mode_state?`, `fast_mode_disabled_reason?`, `effort?`, `capabilities?` (`interrupt_receipt_v1`, `interrupt_cancel_queued_v1`, `mcp_tool_ui_meta_v1`).
- **`compact_boundary`:** `compact_metadata{trigger, pre_tokens, post_tokens?, duration_ms?, preserved_segment?{head_uuid,anchor_uuid,tail_uuid}, preserved_messages?{anchor_uuid,uuids[]}}`.
- **`status`:** `status` (`compacting`, `requesting`, or null), `permissionMode?`, `compact_result?` (`success` or `failed`), `compact_error?`.
- **`api_retry`:** `attempt`, `max_retries`, `retry_delay_ms`, `error_status` (number or null), `error` (enum), `no_response?{waited_ms, retry_wait_ms}`.
- **`control_request_progress`:** `request_id`, `status` (`started` or `api_retry`), `attempt?`, `max_retries?`, `retry_delay_ms?`, `error_status?`.
- **`model_refusal_fallback`:** `trigger:"refusal"`, `direction`, `scope?`, `original_model`, `fallback_model`, `request_id`, `api_refusal_category?`, `api_refusal_explanation?`, `retracted_message_uuids?`, … [T]
- **`model_refusal_no_fallback`:** `original_model`, `request_id`, `api_refusal_category?`, `api_refusal_explanation?`, `refused_user_message_uuid?`, `content`.
- **`local_command_output`:** `content`. Never emitted.
- **`hook_started`:** `hook_id`, `hook_name`, `hook_event`. Needs `includeHookEvents`, except for SessionStart and Setup, which are always included. Notification, SessionEnd, PreCompact and PostCompact never produce `hook_started`.
- **`hook_progress`:** the same three, plus `stdout`, `stderr`, `output`.
- **`hook_response`:** the same three, plus `output`, `stdout`, `stderr`, `exit_code?`, `outcome` (`success`, `error`, `cancelled`).
- **`plugin_install`:** `status`, `name?`, `error?`.
- **`task_notification`:** `task_id`, `tool_use_id?`, `status` (`completed`, `failed`, `stopped`), `output_file`, `summary`, `ambient?`, `usage?{total_tokens, tool_uses, duration_ms}`, `resource_links?`.
- **`task_started`:** `task_id`, `tool_use_id?`, `description`, `task_type?` (`local_bash`, `local_agent`, `remote_agent`), `is_backgrounded?`, `spawn_depth?`, `ambient?`.
- **`task_progress`:** `task_id`, `tool_use_id?`, `description`, `subagent_type?`, `usage`, `last_tool_name?`, `summary?`.
- **`task_updated`:** `task_id`, `patch{status?, description?, end_time?, total_paused_ms?, error?, is_backgrounded?}`.
- **`background_tasks_changed`:** `tasks[{task_id, task_type, description, ambient?}]`.
- **`thinking_tokens`:** `estimated_tokens`, `estimated_tokens_delta`, `user_message_uuid?`.
- **`session_state_changed`** [T]: `state` (`idle`, `running`, `requires_action`). Per the type comment, `idle` is the authoritative signal that the turn is over.
- **`worker_shutting_down`:** `reason`.
- **`commands_changed`:** `commands: SlashCommand[]`.
- **`notification`** [T]: `key`, `text`, `priority` (`low`, `medium`, `high`, `immediate`), `color?`, `timeout_ms?`.
- **`files_persisted`:** `files[{filename, file_id}]`, `failed[{filename, error}]`, `processed_at`.
- **`memory_recall`** [T]: `mode` (`select` or `synthesize`), `memories[{path, scope: personal|team|organization, content?}]`.
- **`elicitation_complete`** [T]: `mcp_server_name`, `elicitation_id`.
- **`permission_denied`:** `tool_name`, `tool_use_id`, `agent_id?`, `decision_reason_type?`, `decision_reason?`, `message`. Best-effort; `result.permission_denials` is authoritative.
- **`mirror_error`:** `error`, `key{projectKey, sessionId, subpath?}`.
- **`informational`:** `content`, `level` (`info`, `notice`, `suggestion`, `warning`), `tool_use_id?`, `prevent_continuation?`.

**Other top-level types:**
- **`tool_progress`:** `tool_use_id`, `tool_name`, `parent_tool_use_id`, `elapsed_time_seconds`, `task_id?`, `heartbeat?` (every 30 s), `subagent_type?`, `subagent_retry?{agent_id, attempt, max_retries, retry_delay_ms, error_status, error_category}`.
- **`tool_use_summary`:** `summary`, `preceding_tool_use_ids`.
- **`auth_status`:** `isAuthenticating`, `output[]`, `error?`.
- **`rate_limit_event`:** `rate_limit_info{status, resetsAt?, utilization?, errorCode?, canUserPurchaseCredits?, hasChargeableSavedPaymentMethod?}`.
- **`prompt_suggestion`:** `suggestion`.
- **`conversation_reset`:** `new_conversation_id`, `trigger?`, `user_message_uuid?`, `timestamp?`.

**`origin` (`SDKMessageOrigin`) kinds:**
- `human`
- `channel{server}`
- `peer{from, fromMode?, name?, fromSession?, senderTaskId?, body?, verifiedPeerPid?}`
- `task-notification{subkind?: scheduled-trigger|peer-send-message, fireReason?}`
- `coordinator`
- `auto-continuation`
- `unclassified`
- The type also has `observer` and `observer-activity` [T].

**Undeclared fields and messages seen on the 2.1.289 stream-json wire [O]:**
- Top-level types `active_goal{value}` and `autocompact_state{value:{enabled, effective_window, threshold, enforced, source}}`.
- System subtypes `post_turn_summary{summarizes_uuid, status_category, status_detail, needs_action}` and `task_summary{detail}`.
- Extra `init` keys: `analytics_disabled`, `messaging_socket_path`, `per_turn_effort_active`, `product_feedback_disabled`, `scratchpad_path`, `startup_timing`, `view_mode`.
- Extra `result` keys: `subagent_stats`, `process_turn_index`, `turn_start_resume_kind`, `time_to_request_*`, `time_origin_ms`, `input_attachments_detail`, `flag_fetch_kick`, `warm_spare_claimed`.
- `assistant.wire_tool_inputs`.
- `compact_metadata.cumulative_dropped_tokens`.
- Treat all of these as unstable.

**Python SDK** (`types.py`): the `Message` union is `UserMessage | AssistantMessage | SystemMessage(subtype, data) | ResultMessage | StreamEvent | RateLimitEvent | ConversationResetMessage`. System subclasses include `TaskStarted/Progress/Notification/Updated`, `MirrorErrorMessage` and `HookEventMessage`. `ResultMessage` has `model_usage`, `terminal_reason`, `origin`, `deferred_tool_use` and `api_error_status`.

### 3.2 Options in TypeScript (Python uses snake_case) [D]

**Hooks and permissions:**
- `hooks`, `includeHookEvents`.
- `canUseTool`, `permissionMode`, `allowDangerouslySkipPermissions`, `permissionPromptToolName`.
- `permissionPrompts`: `'host'` or `'none'` (v2.1.259+).
- `allowedTools` (auto-approve, not a restriction), `disallowedTools` (a bare name removes the tool; a scoped rule denies even in bypass).

**Context and settings:**
- `mcpServers`, `strictMcpConfig`.
- `settingSources` (`user`, `project`, `local`; default all; `[]` means none; managed always loads), `settings`, `managedSettings`.
- `systemPrompt`: a string, a string array, `{type:'custom', prompt, snapshot?}`, or `{type:'preset', preset:'claude_code', append?, excludeDynamicSections?, snapshot?}`.
- `agents` (`AgentDefinition`), `agent`, `forwardSubagentText`, `agentProgressSummaries`.

**Sessions:**
- `resume`, `resumeSessionAt`, `resumeDropsTurn`, `forkSession`, `continue`, `sessionId`, `persistSession`.
- `sessionStore`, `sessionStoreFlush`, `loadTimeoutMs`.

**Limits:**
- `maxTurns`.
- `maxBudgetUsd`: counts only this call's spend; ends with subtype `error_max_budget_usd`.
- `taskBudget`.

**Streaming and output:** `includePartialMessages`, `outputFormat`, `promptSuggestions`, `verbatimPrompts`.

**Environment and process:**
- `env`: replaces the environment; spread `process.env`. `CLAUDE_AGENT_SDK_CLIENT_APP` sets the User-Agent.
- `enableFileCheckpointing`, `cwd`, `additionalDirectories`, `projectConfigRoot`.

**Model:** `model`, `fallbackModel`, `effort`, `thinking`, `title`.

**Tools and plugins:** `tools`, `toolAliases`, `toolConfig`, `plugins`, `skills`, `sandbox`.

**Debugging:** `stderr`, `debug`, `debugFile`.

**`Query` methods:**
- `interrupt`
- `rewindFiles(userMessageId, {dryRun})`, returning `{canRewind, error?, filesChanged?, insertions?, deletions?, skippedLinks?}`
- `setPermissionMode`, `setModel`, `applyFlagSettings`
- `getContextUsage`, `mcpServerStatus`
- `initializationResult`, `reinitialize`
- `stopTask`, `streamInput`, `close`

**Session helpers:**
- `listSessions` → `{sessionId, summary, lastModified, fileSize, customTitle, firstPrompt, gitBranch, cwd, tag, createdAt}`
- `getSessionMessages(id, {dir, limit, offset, includeSystemMessages})` → `{type, uuid, session_id, message, parent_tool_use_id, parent_agent_id}`
- `getSubagentMessages`, `getSessionInfo`, `renameSession`, `tagSession`, `forkSession`

### 3.3 `canUseTool` and `PermissionResult` [D][T]

**Signature:**
```
(toolName, input, {signal, suggestions?, blockedPath?, mcpServer?{name,source}, decisionReason?, defaultToNo?, suppressAlwaysAllowRule?, toolUseID, agentID?, requestId}) => Promise<PermissionResult | null>
```
Return `null` only if you already sent the `control_response` out of band.

**Result shape:**
```
{behavior:"allow", updatedInput?, updatedPermissions?, toolUseID?, decisionClassification?}
| {behavior:"deny", message, interrupt?, toolUseID?, decisionClassification?}
```
`decisionClassification` is `'user_temporary' | 'user_permanent' | 'user_reject'`. It is [T] only and undocumented; it likely feeds the OTel decision `source` [U].

**Python:** `PermissionResultAllow(updated_input, updated_permissions)` and `PermissionResultDeny(message, interrupt)`. The context is `ToolPermissionContext(signal, suggestions, tool_use_id, …)`.

**Wire request (`can_use_tool`):** `decision_reason_type`, which is one of `rule`, `mode`, `subcommandResults`, `permissionPromptTool`, `hook`, `asyncAgent`, `sandboxOverride`, `workingDir`, `safetyCheck`, `classifier`, `other`, plus `classifier_approvable` [T].

**`PermissionMode`:** `default`, `acceptEdits`, `bypassPermissions`, `plan`, `dontAsk`, `auto`. `manual` is accepted as an alias in the CLI and frontmatter.

## 4. Transcript JSONL

### 4.1 Location and lifecycle [D]

- Main transcript: `~/.claude/projects/<project>/<session-id>.jsonl`. `<project>` is the cwd with non-alphanumeric characters replaced by `-`; names over 200 characters are truncated and hashed.
- Subagents: `<project>/<session-id>/subagents/agent-<agentId>.jsonl`, plus an `agent-<agentId>.meta.json` sidecar [O]. The sidecar holds `agentType`, `description`, `toolUseId`, `spawnDepth`, `requestShape`, `requestNonInteractive`, `model`.
- Large tool outputs: `<project>/<session-id>/tool-results/`.
- Checkpoint snapshots: `~/.claude/file-history/<session>/`.
- Set-aside copies: `<session>.orphaned-<timestamp>-<suffix>.jsonl` and `<session>.jsonl.superseded-<timestamp>`.

**Configuration:**
- `CLAUDE_CONFIG_DIR` moves the root; `CLAUDE_CODE_PROJECT_DIR_NAME` names the project directory (v2.1.234+).
- `cleanupPeriodDays`: default 30, minimum 1, `0` rejected.
- `desktopSessionCleanupPeriodDays`.
- `CLAUDE_CODE_TRANSCRIPT_LOCAL_GC=1` trims files over 5 MB after compaction, in `-p` and the SDK (v2.1.287+).
- `CLAUDE_CODE_SKIP_PROMPT_HISTORY` and `--no-session-persistence` stop writes.
- `claude purge` removes data.
- The SDK `sessionStore` mirrors entries; subagent keys use subpath `subagents/agent-<id>`.

### 4.2 Official stability warnings, verbatim [D]

- sessions page: "Each line is a JSON object for a message, tool use, or metadata entry. The entry format is internal to Claude Code and changes between versions, so scripts that parse these files directly can break on any release. To build on session data, use `/export` or the script interfaces instead."
- monitoring page: "The transcript entry format is internal to Claude Code and changes between versions, so a pipeline that joins on these fields can break on any release; treat the joins as version-specific rather than a stable contract".
- `sdk.d.ts` (`SessionStoreEntry`): "a large discriminated union over `type` … That union is CLI-internal and not part of the SDK API surface … every entry has a string `type` discriminant, most carry a `uuid` and ISO `timestamp`".

### 4.3 Entry shapes observed on 2.1.289 [O; undocumented, may change]

**Common fields on message entries:** `type`, `uuid`, `parentUuid` (null at the root and after a compact boundary), `sessionId`, `timestamp`, `isSidechain`, `cwd`, `gitBranch`, `version`, `entrypoint`, `userType`. Subagent files add `agentId`.

**`user` entries:**
- Core: `message{role, content}`, `promptId`, `permissionMode`, `isMeta`, `origin`, `promptSource`, `turnOrigin`, `turnPosition`.
- Tool results: `toolUseResult` (the structured tool output; equals SDK `tool_use_result` and hook `tool_response`), `sourceToolAssistantUUID`, `toolEndsTurn`.
- Other: `serverClassifierContext`.
- Compact summary entries: `isCompactSummary: true` and `isVisibleInTranscriptOnly: true`.

**`assistant` entries:**
- `message` (the API message: `id`, `model`, `content`, `stop_reason`, `stop_details`, `usage`, `context_management`, …).
- `requestId`, `effort`, `perTurnEffort`, `thinkingDurationMs`, `apiBlockIndex`, `attributionAgent`, `attributionMcpServer`, `attributionMcpTool`, `advisorModel`, `wireToolInputs`, `serverClassifierRequest`.
- There is one entry per content block. The docs confirm the last one is the `message.uuid` that the next turn's `parentUuid` chains from.

**Other entry types:**
- `attachment` (`attachment`, `rendered*`).
- `system`, subtype `stop_hook_summary`: `hookCount`, `hookInfos`, `hookErrors`, `hookAdditionalContext`, `preventedContinuation`, `stopReason`, `toolUseID`, `level`, `hasOutput`.
- `system`, subtype `compact_boundary`: `compactMetadata{trigger, preTokens, postTokens, durationMs, cumulativeDroppedTokens}`, `logicalParentUuid`, `content:"Conversation compacted"`, `slug`. The sub-agents docs show `compactMetadata{trigger, preTokens}`.
- Metadata-only entries: `queue-operation`, `last-prompt{lastPrompt, leafUuid}`, `mode`, `cost-state{totalCostUSD, modelUsage, totalAPIDuration, totalLinesAdded, …}`, `atis-latch`.
- No `summary` entry type appeared in my sample [U]. The SDK fold mentions `customTitle`, `aiTitle`, `tag` and `summaryHint` fields.

**Joining:** use `uuid`, `parentUuid`, `requestId` and `tool_use` IDs, consistent with OTel `message.uuid`, `request_id` and `tool_use_id`. Transcripts also record effort per assistant message (v2.1.212).

## 5. Subagents

**Definition** (https://code.claude.com/docs/en/sub-agents): `.claude/agents/*.md`, `~/.claude/agents/`, plugins, the `--agents` JSON flag, or the SDK `agents` option. Hot-reloaded.

**Frontmatter fields** (camelCase; unknown fields are silently ignored):
- `name` (required; becomes hook `agent_type`; no `:`)
- `description` (required)
- `tools`, `disallowedTools`
- `model` (`sonnet`, `opus`, `haiku`, `fable`, a full ID, or `inherit`)
- `permissionMode` (ignored in auto mode and for plugin agents)
- `maxTurns`
- `skills`, `mcpServers`, `hooks`
- `memory` (`user`, `project`, `local`)
- `background`, `omitClaudeMd` (v2.1.271+), `effort`
- `isolation` (`worktree`)
- `color`, `initialPrompt`
- `experimental.cacheTtl` (`5m` or `1h`)

The SDK `AgentDefinition` adds `prompt` and `criticalSystemReminder_EXPERIMENTAL`.

**In hooks:**
- `SubagentStart` and `SubagentStop` as in §1.7.
- Tool hooks fired inside a subagent carry `agent_id` and `agent_type`.
- Frontmatter `Stop` becomes `SubagentStop`.
- To inject into the parent after a subagent returns, use `PostToolUse` on `Agent`.

**In OTel:**
- `agent_id` and `parent_agent_id` on `llm_request` and `tool` spans (v2.1.139 and v2.1.145).
- Subagent spans nest under the parent's Agent `claude_code.tool` span.
- `query_source`:
  - Metrics: `subagent`.
  - Events: the subagent name.
  - Spans: `query_source` (detailed beta) and `query_source_safe`, such as `agent.custom`.
- `agent.name` on cost and token metrics.
- The `subagent_completed` event.
- Roll up cost with `query_source="subagent"`. That category also includes agent-hook requests.
- API requests carry `x-claude-code-agent-id` and `x-claude-code-parent-agent-id` headers (v2.1.139).

**In SDK streams:**
- Messages carry `parent_tool_use_id`.
- Text and thinking appear only with `forwardSubagentText` / `--forward-subagent-text`; all depths from v2.1.219.
- `task_started.spawn_depth`; `canUseTool.agentID`; `permission_denied.agent_id`.

**In transcripts:**
- Separate `subagents/agent-<id>.jsonl` files with `isSidechain` and `agentId`.
- Unaffected by main-conversation compaction.
- Have their own `compact_boundary` entries.
- Deleted with the parent session.
- Checkpoints do **not** restore subagent edits, except a foreground forked skill.

## 6. Permissions

**Modes:**
- `default` (labeled Manual)
- `acceptEdits`
- `plan`
- `auto`
- `dontAsk`
- `bypassPermissions`

`permissions.disableBypassPermissionsMode` and `permissions.disableAutoMode` (value `"disable"`) block modes.

**Rule syntax:**
- `Tool` or `Tool(specifier)`. `Bash(*)` equals `Bash`.
- `*` matches any text. A trailing ` *` also matches the bare command. `:*` is a suffix alias.
- `WebFetch(domain:x)`, `Read(./path)`.
- Parameter matching (deny and ask only): `Tool(param:value)`, such as `Agent(model:opus)` or `Bash(run_in_background:true)`. A tool's primary content field cannot be matched this way.
- Tool-name globs: in deny and ask, `"*"` and `"mcp__*"`. In allow, only after a literal `mcp__<server>__` prefix.
- MCP rules with parentheses in settings are skipped.

**Evaluation order** (from the SDK docs):
1. hooks
2. deny rules
3. ask rules
4. mode
5. allow rules
6. `canUseTool` (or deny in `dontAsk` / `permissionPrompts:'none'`)

A hook `allow` does not bypass deny or ask rules.

**Decision sources in OTel:** `config`, `hook`, `user_permanent`, `user_temporary`, `user_abort`, `user_reject`. There is no `classifier` value in OTel.

**Auto mode classifier:**
- **Model:** runs on Sonnet 5 by default. Falls back to the session model (or Opus on Fable). A server-side configured model takes precedence.
- **What it sees:** user messages, non-read-only tool calls, and CLAUDE.md. Tool results are stripped. `PostToolUse` `classifierContext` adds context.
- **Rule handling on entry:** broad allow rules (`Bash(*)`, interpreter wildcards, package-manager run commands, `Agent`, `Monitor`) are dropped while in auto mode.
- **Fallback to prompting:** after 3 blocks in a row or 20 total; not configurable.
- **No-verdict denials** do not count toward those thresholds and do not appear in Recently denied.
- **Server-side classifier review:** v2.1.271–282 depending on surface; turn off with `CLAUDE_CODE_AUTO_MODE_SERVER=0`. It stops the turn after 10 responses in a row with no verdict.
- **Subagents** are checked at spawn, on each action, and on their final report.
- **Hooks and SDK:** the `PermissionDenied` hook (§1.7); the SDK `permission_denied` message with `decision_reason_type` `"classifier"`; denial reasons such as `[Data Exfiltration]`.

## 7. Compaction

**Hooks:**
- `PreCompact {trigger, custom_instructions}` can block. Blocking a recovery compaction surfaces the context-limit error.
- `PostCompact {trigger, compact_summary}`.
- `SessionStart` then fires with `source:"compact"`, and `model` is present [O].
- `InstructionsLoaded` fires with `load_reason:"compact"`.

**Observed order for a manual `/compact` [O]:**
1. `system/status{status:"compacting"}`
2. PreCompact hook
3. SessionStart(compact) hook
4. PostCompact hook
5. `system/status{status:null, compact_result:"success"}`
6. `system/init`
7. `system/compact_boundary{compact_metadata{trigger:"manual", pre_tokens, post_tokens, cumulative_dropped_tokens, duration_ms}}`
8. A replayed synthetic user message holding the summary ("This session is being continued from a previous conversation…")
9. `result{num_turns:0, local_command:"compact"}`

**Where the summary text is available:**
- `PostCompact.compact_summary`.
- The transcript `user` entry with `isCompactSummary:true`.
- The SDK replayed user message (`isSynthetic`).
- `getSessionMessages`.
- **Not** in OTel: the `compaction` event carries only counts. Detailed beta re-emits `claude_code.system_prompt` after compaction.

**Controls:**
- `autoCompactEnabled`, `DISABLE_AUTO_COMPACT`, `DISABLE_COMPACT`.
- `autoCompactWindow` / `/autocompact` / `--autocompact` / `CLAUDE_CODE_AUTO_COMPACT_WINDOW` (100000–1000000).
- `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` (can only lower the threshold; also applies to subagents).
- Native-1M models compact at about 967K by default.
- `/compact [instructions]`; the rewind menu's Summarize from here / up to here.
- SDK `status:"compacting"` and `getContextUsage()`.

## 8. Checkpoints (https://code.claude.com/docs/en/checkpointing)

**What gets snapshotted:**
- One checkpoint per prompt that starts a turn. Messages that join a running turn are not checkpointed.
- Only edits made by Claude's file-editing tools.
- Snapshots kept for the 100 most recent checkpoints, plus each file's first snapshot. Stored in `~/.claude/file-history/<session>/`, saved with the conversation, and swept after `cleanupPeriodDays`.

**`/rewind` (or Esc Esc) actions:**
- Restore code and conversation
- Restore conversation
- Restore code
- Summarize from here
- Summarize up to here
- Never mind

**Not tracked or restored:**
- Bash file changes
- Subagent edits (except a foreground forked skill)
- External or other-session edits
- Symlinked or hard-linked paths (skipped; `skippedLinks` in the SDK, v2.1.216+)

**Controls:** `fileCheckpointingEnabled` and `CLAUDE_CODE_DISABLE_FILE_CHECKPOINTING`. In the SDK: `enableFileCheckpointing`, `rewindFiles()`, and the `files_persisted` message.

## 9. CHANGELOG.md scan for 2026

2026 covers v2.1.0 (2026-01-07) through v2.1.289 (2026-10-03); v2.0.77 shipped on 2026-01-06. Date anchors: 2.1.50 = 02-20, 2.1.100 = 04-10, 2.1.150 = 05-23, 2.1.200 = 07-03, 2.1.250 = 08-27. Additions only; bug fixes omitted.

**Hooks:**

| Version | Change |
|---|---|
| 2.1.0 | Hooks in agent, skill and command frontmatter; `once`; prompt/agent hooks from plugins |
| 2.1.2 | SessionStart `agent_type` |
| 2.1.3 | Tool hook timeout raised from 60 s to 10 min |
| 2.1.9 | PreToolUse `additionalContext` |
| 2.1.10 | `Setup` |
| 2.1.33 | `TeammateIdle`, `TaskCompleted` |
| 2.1.47 | `last_assistant_message` |
| 2.1.49 | `ConfigChange` |
| 2.1.50 | `WorktreeCreate`, `WorktreeRemove` |
| 2.1.63 | HTTP hooks |
| 2.1.69 | `InstructionsLoaded`; `agent_id`/`agent_type` on hooks |
| 2.1.76 | `Elicitation`, `ElicitationResult`, `PostCompact` |
| 2.1.78 | `StopFailure` |
| 2.1.83 | `CwdChanged`, `FileChanged` |
| 2.1.84 | `TaskCreated`; HTTP WorktreeCreate |
| 2.1.85 | `if` field; AskUserQuestion via `updatedInput` |
| 2.1.89 | `defer`; `PermissionDenied`; 10K output cap moved to file |
| 2.1.94 | UserPromptSubmit `sessionTitle` |
| 2.1.105 | PreCompact can block |
| 2.1.118 | `mcp_tool` hooks |
| 2.1.119 | `duration_ms` |
| 2.1.121 | `updatedToolOutput` for all tools |
| 2.1.133 | `effort`/`CLAUDE_EFFORT` |
| 2.1.139 | `args` exec form; `continueOnBlock` |
| 2.1.141 | `terminalSequence` |
| 2.1.145 | `background_tasks`/`session_crons` |
| 2.1.152 | `MessageDisplay`; SessionStart `reloadSkills` and `sessionTitle` |
| 2.1.163 | Stop/SubagentStop `additionalContext` |
| 2.1.196 | `prompt_id` (per the docs) |
| 2.1.207 | Shell-form `${user_config.*}` rejected |
| 2.1.214 | SessionStart `source:"fork"`; `if` `dir/**` semantics changed |
| 2.1.219 | `DirectoryAdded` |
| 2.1.236 | `classifierContext` (per the docs) |
| 2.1.251 | `PreModelSwitch`, `PostModelSwitch`; resume staleness and cost fields |
| 2.1.257 | `scratchpad_dir` (per the docs) |
| 2.1.269 | `bashEditDiff` (per the docs) |
| 2.1.274 | `mcp_server` provenance (per the docs) |
| 2.1.280 | Agent hooks are no longer run on PermissionRequest |

**OpenTelemetry:**

| Version | Change |
|---|---|
| 2.1.41 | `speed` |
| 2.1.85 | `tool_parameters` gated behind DETAILS |
| 2.1.97 / 2.1.98 | Bash `TRACEPARENT` |
| 2.1.101 | Beta tracing honors the content gates |
| 2.1.110 | Inbound `TRACEPARENT`/`TRACESTATE` in `-p` and the SDK |
| 2.1.111 | `OTEL_LOG_RAW_API_BODIES` |
| 2.1.117 | `command_name`, `command_source`, `effort` |
| 2.1.119 | `tool_use_id`, `tool_input_size_bytes` |
| 2.1.121 | `stop_reason`, `gen_ai.response.finish_reasons`, `user_system_prompt` |
| 2.1.122 | `at_mention`; numeric attributes emitted as numbers |
| 2.1.126 | `invocation_trigger` |
| 2.1.128 | `OTEL_*` stripped from subprocesses |
| 2.1.129 | PR count includes MCP |
| 2.1.139 / 2.1.145 | `agent_id`/`parent_agent_id` on spans |
| 2.1.152 | `app.entrypoint`; `CLAUDE_CODE_PROPAGATE_TRACEPARENT` |
| 2.1.157 | `tool_decision.tool_parameters` |
| 2.1.161 | Resource attributes as metric labels |
| 2.1.172 | LOC metric `model` |
| 2.1.193 | `assistant_response` |
| 2.1.202 | `workflow.run_id`, `workflow.name` |
| 2.1.214 | `message.uuid`, `client_request_id`, `tool_source`; `CLAUDE_CODE_OTEL_CONTENT_MAX_LENGTH` |
| 2.1.217 | Managed endpoint lock |
| 2.1.227 | `retention_sweep` (per the docs) |
| 2.1.268 | `*_safe`, `error_class`, `first_content_ms`, `parent.source`, `bash_*` (per the docs) |
| 2.1.269 | `OTEL_METRICS_INCLUDE_REPOSITORY`; `vcs.ref.head.*` |
| 2.1.273 | Real names on metrics with DETAILS |
| 2.1.274 | Span `effort`; `managed_settings_resolved`; raw-body `index.jsonl`, `request_body_id`, `message.id` |
| 2.1.280 | Hook output-size attributes |
| 2.1.282 | Project/local settings ignore OTel enable/endpoint/content variables |
| 2.1.283 | `tool.output` for MCP/WebFetch/WebSearch |
| 2.1.287 | `prompt_text` |

**SDK and headless:**

| Version | Change |
|---|---|
| 2.1.19 | `queued_command` replay |
| 2.1.45 | `SDKRateLimitEvent` |
| 2.1.49 | Model info effort fields |
| 2.1.51 | `CLAUDE_CODE_ACCOUNT_UUID`, `CLAUDE_CODE_USER_EMAIL`, `CLAUDE_CODE_ORGANIZATION_UUID` |
| 2.1.111 / 2.1.128 / 2.1.283 | init `plugin_errors` (2.1.283 adds `path`) |
| 2.1.132 | `CLAUDE_CODE_SESSION_ID` in Bash |
| 2.1.153 | `thinking_tokens` (per the docs) |
| 2.1.203 | `background_tasks_changed` (per the docs) |
| 2.1.205 | `capabilities` (per the docs) |
| 2.1.211 | `--forward-subagent-text` |
| 2.1.212 | `set_model` applies mid-turn; effort recorded in transcripts |
| 2.1.219 | `mcp_server_errors`; nested subagent forwarding; `fast_mode_disabled_reason` |
| 2.1.227 | `systemMessage` as `SDKInformationalMessage` (per the docs) |
| 2.1.259 | `permissionPrompts` (per the docs) |
| 2.1.267 | `cloud_credential_error` |
| 2.1.287 | `CLAUDE_CODE_TRANSCRIPT_LOCAL_GC` (per the docs) |

## Caveats for building a closed harness

1. A nested `claude -p` launched from a Claude Code Bash tool reported the **parent's** `session_id` in its hooks unless `--session-id` was passed [O, this cloud container only; general behavior unverified]. Pass `--session-id` explicitly.
2. `scratchpad_dir`, `compact_metadata.cumulative_dropped_tokens`, `session_state_changed`, `memory_recall`, `notification`, and the observed `active_goal`, `autocompact_state`, `post_turn_summary` and `task_summary` messages are either undocumented or type-only. Parse them defensively.
3. The Python SDK hook surface covers only 10 events. Use shell hooks loaded through `setting_sources`, or the TypeScript SDK, for the full set.
4. OTel tracing is beta. `query_source` on spans needs detailed beta tracing; use `query_source_safe` otherwise.

All downloaded sources are in `/tmp/claude-0/-home-user-Tracelyt/759a35a9-2e36-5f3a-a868-84fb22c157ad/scratchpad/`: `docs/*.md`, `npm/package/sdk.d.ts`, `py_types.py`, and test runs and hook logs in `hooktest/`.