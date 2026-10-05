# SPEC-06 — Integration Framework (adapters and instrumentors), v0.1

**Version:** 0.1.0 · **Status:** APPROVED v0.1 (founder approval 2026-10-05; Phase 1 baseline) · **Owner:** Capture & Standards · **Depends on:** SPEC-01, SPEC-05, research 02, 03, 04 · **Reference implementation:** `src/harness_engine/adapters/claude_code/` (Tier B), `src/harness_engine/normalize/` (merge, verification adapter)

## 1. Tiers and contract summary
| Tier | Definition | Contract |
|---|---|---|
| A | Native instrumentation inside an open harness or framework | Emits SPEC-01 events directly (both `gen_ai.*` and `harness.*` forms) via OTLP plus side-channel PayloadRefs; full control-event coverage where the framework exposes the concept; publishes a coverage matrix |
| B | Hook and OTel adapters for closed harnesses | Consumes the harness's hooks, native OTel export and SDK streams; merges on exact identifiers (SPEC-01 §8); strips PII; computes fidelity; publishes a coverage matrix with known gaps |
| C | API and log adapters | Consumes vendor APIs or files; skeleton coverage (run, tool, cost); fidelity G1 to G2 |
| Adjunct | Verification and version adapters | Harness-independent: CI results, test runners, git, image digests, registries → `verify.*` events and `versions` |

Every adapter: deterministic event ids; `native_type` preserved; unknown records kept as `unknown`; a versioned PII strip list; a conformance test capture; and two permanent maintainers across all Tier B adapters because closed harnesses ship weekly (PLAN-03).

## 2. Tier B: the shared CLI hook contract
Claude Code (33 events), Codex (12 events, generated JSON schemas in `codex-rs/hooks/schema/generated/`) and Gemini CLI (11 events) have converged on stdin-JSON lifecycle hooks with `hookSpecificOutput` decision controls. One adapter binary handles all three:
- **Input**: the hook payload on stdin, tagged with the event name from `argv[1]` and a wall-clock timestamp (Claude Code payloads carry no timestamp).
- **Output**: exit 0 and empty stdout (observe-only). The adapter never blocks, rewrites or injects in Phase 1; SPEC-04 governs later decision use.
- **Sink**: append-only local JSONL (default) or POST to a localhost receiver; never a remote endpoint directly (SPEC-05 T12).
- **Identity**: `session_id` → `run_id`; `prompt_id`/`turn_id` → `turn_id`; `agent_id` → `agent_instance_id`; `tool_use_id` → `tool_call_id`.
- **PII**: hooks carry none beyond paths and content; paths are hashed, content becomes PayloadRefs with bytes left in the customer store.

Field mapping per harness is in research 02 (Claude Code), 03 (Codex, Gemini CLI, Cursor). Observed Claude Code mapping is implemented in `adapters/claude_code/hooks.py`.

## 3. Tier B: OTel receiver
An OTLP/HTTP (JSON and protobuf) receiver on localhost accepts the harness's native export. Claude Code: `claude_code.*` log events and metrics (no spans in 2.1.289). Codex: `codex.*` events and spans (`session_loop`, `turn`, `handle_responses` with `gen_ai.usage.*`, `mcp.tools.call`); gaps: `codex exec` has no metrics, `codex mcp-server` has no OTel. Gemini CLI: `gemini_cli.*` events incl. `api_response{finish_reasons}`, `tool_call{decision}`, `chat_compression{tokens_before,tokens_after}`, `agent.start/finish{terminate_reason}`. The receiver strips the per-harness PII attribute list before anything else.

## 4. Tier B: side channel
Claude Code `OTEL_LOG_RAW_API_BODIES=file:<dir>` writes request and response bodies plus `index.jsonl` (`request_file`, `response_file`, `request_id`, `message_id`, `message_uuid`); Codex `CODEX_ROLLOUT_TRACE_ROOT` writes `payloads/`. These are the R2 cassettes (SPEC-02) and stay customer-side; events reference them by hash.

## 5. Coverage matrices (observed and documented, v0.1)

### 5.1 Closed harnesses (Tier B/C)
| Concept | Claude Code | Codex CLI | Gemini CLI | Cursor |
|---|---|---|---|---|
| Run start/end | hooks SessionStart/End; SDK result | hooks; `codex.conversation_starts`; `session_loop` span; rollout `session_meta` | hooks; `gemini_cli.config`, `conversation_finished{approvalMode,turnCount}` | hooks `sessionStart{session_id,is_background_agent}`/`sessionEnd{reason,duration_ms,final_status}` |
| Iteration/turn | prompt_id; derived from model responses | `turn` span (`turn.id`); hooks carry `turn_id` | `BeforeAgent`/`AfterAgent`; `user_prompt{prompt_id}`; no per-turn root span | `beforeSubmitPrompt`/`stop{status,loop_count}`; not in `-p` mode |
| Model: model, tokens, finish | `api_request` (tokens, cost, ttft); finish reason via SDK stream or raw body | `codex.api_request`, `codex.sse_event`, `handle_responses` (`gen_ai.usage.*`); **finish reason absent** | `api_response{*_token_count, finish_reasons}`; `BeforeModel`/`AfterModel` can read and override | `model` only; tokens undocumented; finish reason absent |
| Tool request/decision/result | full (hooks + `tool_decision{source}` + `tool_result{error_type}`) | full (hooks + `codex.tool_decision{source: User,Config,AutomatedReviewer}`, `codex.tool_result`, `codex.sandbox_outcome`) | `BeforeTool`/`AfterTool`; `tool_call{decision: accept,reject,modify,auto_accept; success; duration_ms}` (no call id in the log) | `preToolUse`/`postToolUse`/`postToolUseFailure{tool_use_id,duration,failure_type}` plus shell/read/edit hooks |
| MCP | tool name `mcp__srv__tool` | `mcp.tools.call` span; `tool_result{mcp_server,mcp_tool}` | `tool_call{tool_type:"mcp", mcp_server_name}` | `beforeMCPExecution`/`afterMCPExecution{tool_name,result_json,duration}` |
| Permission decision + source | full incl. `permission_suggestions`, `classifier_verdict`, `permission_mode_changed` | `PermissionRequest`; `tool_decision.source`; `guardian_assessment` (opt-in); not persisted to file | `tool_call.decision`; `approval_mode_switch`; source partial (`auto_accept` without rule id) | hook output `permission` is our own decision; final user decision not exposed; `failure_type:"permission_denied"` |
| Subagent | SubagentStart/Stop (`agent_id`, `agent_type`, transcript path, last message); `subagent_completed` (tokens, tool uses, duration) | SubagentStart/Stop; rollout `parent_thread_id`, `agent_role`; `codex.multi_agent.spawn.*` | `agent.start/finish{terminate_reason,turn_count,duration_ms}`, `agent.recovery_attempt`; **no hooks, no agent ids** | `subagentStart/Stop` (newer builds) |
| Compaction trigger | PreCompact/PostCompact `trigger` | PreCompact/PostCompact `trigger` | `PreCompress{trigger}` (advisory) | `preCompact` (newer builds) |
| Compaction tokens | SDK `compact_boundary` (`pre_tokens`, `post_tokens`, `cumulative_dropped_tokens`, `preserved_segment`); OTel `compaction` (differs) | infer from `token_count` around `compacted` | `chat_compression{tokens_before,tokens_after}` | none |
| Compaction summary | **PostCompact `compact_summary`** (full text) | rollout `compacted.message`; raw bodies via trace root | none in OTel or hooks | none |
| Context provenance | InstructionsLoaded (`file_path`, `memory_type`, `load_reason`) | spans `agents_md.discover`/`agents_md.load`; AGENTS.md in `turn_context` | none (GEMINI.md not in telemetry) | none |
| Verification | adapter only | adapter only | adapter only | adapter only |
| Stop reason | SDK `result.terminal_reason`; SessionEnd `reason` | `turn_aborted.reason`, `turn/completed.status`, `turn.failed` | `finish_reasons`, `agent.finish.terminate_reason`, `loop_detected`, `next_speaker_check` | `stop.status` only |
| Cost | `cost.usage` metric, `api_request.cost_usd` | `codex.turn_cost` (app-server only) | none for API key or Vertex; `credits_used` on credit plans | none |
| Raw bodies | `OTEL_LOG_RAW_API_BODIES=file:` | `CODEX_ROLLOUT_TRACE_ROOT` payloads; `rawResponseItem/completed` (opt-in) | `gen_ai.input/output.messages` (needs traces and logPrompts), `BeforeModel`/`AfterModel` | none |
| Propagation | TRACEPARENT to Bash children, API, MCP | inbound TRACEPARENT; outbound to MCP `_meta`, exec-server | outbound HTTP only; inbound not implemented | none |

### 5.2 Open frameworks (Tier A targets; research 04 matrix)
Native model/tool/agent spans are routine (LangGraph via callbacks, OpenAI Agents SDK trace processors, ADK and PydanticAI and Mastra and Vercel native OTel, OpenHands native OTel, CrewAI event bus). The control events we add through instrumentors, with the framework insertion point:
| Concept | Insertion point per framework |
|---|---|
| Compaction | LangGraph: state diff at summarization nodes, Deep Agents `_summarization_event`; OpenAI Agents SDK `CompactionItem`; ADK `compact_events`/`EventActions.compaction`; OpenHands `Condensation` event; PydanticAI history processors (silent, wrap); Mastra processor spans; Vercel `prepareStep`/`pruneMessages` (wrap, no event) |
| Permission/approval | LangGraph `on_interrupt`; Agents SDK `interruptions` + `RunState`; ADK event actions; PydanticAI `DeferredToolRequests`/`ToolApproved`/`ToolDenied`; OpenHands confirmation mode and `UserRejectObservation`; CrewAI `human_feedback_*`; Vercel `tool-approval-request/response` parts |
| Delegation | LangGraph namespaces and `task` tool; Agents SDK `handoff` spans; ADK `transfer_to_agent`; Claude Agent SDK SubagentStart/Stop; CrewAI delegation tools; AutoGen `HandoffMessage`; Mastra network chunks |
| State/checkpoint | LangGraph `get_state_history`/`checkpoint_id`; Agents SDK `RunState`; ADK session events and rewind; OpenHands EventLog `fork()` (shares workspace); Mastra `WorkflowRunState`; CrewAI checkpoint events |
| Stop reason and limits | Agents SDK `MaxTurnsExceeded`; PydanticAI `UsageLimitExceeded`; OpenHands `MaxIterationsReached`/`MaxBudgetReached`; AutoGen `TaskResult.stop_reason`; Vercel `stopWhen` (no event; wrap) |
| Verification | adapter only, everywhere |
| Memory | CrewAI and Mastra `memory_operation` native; others require wrapping the store (LangGraph store, Agents SDK Session, ADK memory service) |

Framework-specific exceptions that resist normalization (research 04): finish reasons not normalized across frameworks (LangGraph callbacks, OpenHands partial); MCP calls indistinguishable from plain tools in LangGraph and Vercel; CrewAI `max_iter` silent; PydanticAI history processors silent. Each becomes an instrumentor wrap with `source_channel=instrumentor.<framework>` and a coverage-matrix entry.

## 6. Verification adapter (D-038)
Derives `verify.*` from observed verifier invocations (pytest, unittest, npm test, go test, cargo test, make test, lint and typecheck, build) and from CI results and git state. `parent_event_id` links to the tool result; `source_channel=verification_adapter`. A blocked invocation is `verify.abstained`. Phase 1 adds CI webhooks (GitHub checks) and test-report parsers (JUnit XML) for `tests_total`/`tests_failed`.

## 7. Version adapter
Computes `versions.harness_config_hash` from rules files, settings, hooks and MCP config at run start; captures image digest, commit SHA, dirty-diff hash, tool-definition hash from the first model request, model id, policy version. Without it, release correlation and regression are unreliable (PLAN-11 P19).

## 8. Conformance and maintenance
Each adapter ships a captured test session and its expected event list (as `tests/fixtures/claude_code/` does), a coverage matrix, a PII strip list and a changelog pinned to harness versions. Adapter breakage on a new harness release is a P1 for the two maintenance engineers; the coverage matrix is re-measured on every supported release.

## 9. Open questions
1. Whether to ship the hook adapter as one binary for Claude Code, Codex and Gemini CLI or three thin scripts (shared contract argues for one).
2. Cursor cloud agents: no public session-event API found; Tier C remains hooks-only.
3. Devin: REST session events and Session Insights only; polling cadence and cost.
4. Entire Checkpoints as a Tier C source for commit-attached sessions.
