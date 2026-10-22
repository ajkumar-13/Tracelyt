# Proof B, second harness: OpenAI Agents SDK under a Tier A instrumentor (scripted run, 22 October 2026)

**Setup.** `openai-agents` 0.24.0 (Python), isolated venv, no API key and no network. Every model turn comes from `ScriptedModel` (`src/harness_engine/adapters/openai_agents/scripted_model.py`), a real `agents.Model` subclass that opens and fills a `generation` span the way the SDK's Chat Completions model does. Everything else is the SDK's own code. That covers `Runner.run` and `Runner.run_streamed`, function tools, an input guardrail, a handoff, `needs_approval` interruptions with `RunState.approve/reject` and resume, `RunHooks` and `AgentHooks`, a model-emitted `compaction` output item, and `OpenAIResponsesCompactionSession` with a fake `responses.compact` client. The OpenAI trace exporter is replaced by our processor (`set_trace_processors`), so nothing leaves the process.

**Scenario** (`scripts/capture_openai_agents.py`):
- **Trace 1.** `triage` (input guardrail `no_account_numbers`) calls `lookup_order`, which opens a custom span `orders.db_lookup`, then hands off to `billing`.
  - `billing` calls `ledger_balance`, which raises.
  - `billing` then requests `refund_order` and `close_account`, both `needs_approval=True`, so the run ends with two interruptions.
  - We approve the refund and reject the closure, then resume from `RunState`. The refund runs and the final turn returns a `compaction` item plus the answer.
- **Trace 2.** A streamed single-agent run on an `OpenAIResponsesCompactionSession`, which compacts after the turn.

**Fixtures** in `tests/fixtures/openai_agents/scenario1/`:
- `raw.jsonl`: 98 native records. These are SDK `export()` dicts for traces and spans, plus content-free hook, approval and wrap records. Trace and span ids are renumbered.
- `events.jsonl`: 52 merged v0.1 events.
- `stats.json`.

Tests replay `raw.jsonl` with the system interpreter (`tests/test_openai_agents_adapter.py`).

## 1. What the SDK exposes vs what v0.1 needs

| v0.1 domain | SDK surface (0.24.0) | Instrumentor result |
|---|---|---|
| RUN | `Trace` start/end; `task` span per `Runner.run` (on by default in 0.24.0, exported as `custom` with `sdk_span_type`); on resume the trace is **reattached without trace start/end** | `run.started` from the trace. `run.completed`/`run.failed` from each task span end. `run.resumed` from a task span that opens on a trace whose end was already seen. |
| LOOP | `turn` span with the SDK's `turn` counter (continues across resume) | `iteration.started/completed`; `Identity.iteration` = the SDK turn number (native, no derivation) |
| MODEL | `generation` span (model, usage, input, output = `Response` dump); `response` span on the Responses model; `on_llm_start/on_llm_end` (`ModelResponse.response_id`, `request_id`, usage) | `model.request` + `model.response`. `finish_reason` is not exposed, so it is read off the output item types (`tool_use` when function calls are present, else `end_turn`). |
| TOOL | function span (name, input, output, `mcp_data`, error `Error running tool (non-fatal)`) **without a call id**; `on_tool_start/on_tool_end` with `ToolContext.tool_call_id` | `tool.requested` comes from the `function_call` output items. `tool.started` and `tool.completed`/`tool.failed` come from the function span, joined to `call_id` by (name, arguments) and confirmed against the hook's `tool_call_id`. |
| PERMISSION | `FunctionTool.needs_approval` → `ToolApprovalItem` in `RunResult.interruptions`; `RunState.approve/reject`. **No callback and no span event** | `permission.requested` from the interruption, plus the function span the SDK closes with neither output nor error. `permission.granted`/`permission.denied` come from the instrumented `approve`/`reject`. |
| AGENT | `agent` span per agent segment; `handoff` span (`from_agent`, `to_agent`); `on_handoff`, `on_agent_start/end` | `agent.spawned` is emitted when the target agent span opens, so the child id is the exact span id; `via_tool_call_id` is the handoff `function_call`. `agent.returned` is emitted at the target's final agent span end. |
| CONTEXT | `compaction` output item → `CompactionItem` (inside the generation output only); `OpenAIResponsesCompactionSession` → `responses.compact`, **no span and no hook** | `context.compact` from the output item (`compaction_item_id`, summary ref of `encrypted_content`). Session compaction is captured by wrapping `client.responses.compact`, which also gives tokens and preserved item count. |
| VERIFICATION | none (guardrails are policy checks on input/output, not task verification) | not emitted; the adapter-only verification path (SPEC-06 §6) applies as for every harness |
| STOP | final output (last generation with a message and no calls; `on_agent_end(output)`); errors on the task span (`Max turns exceeded`, ...) | `stop` (`agent_declared_complete`, `final_message` ref) plus `run.completed`; a task-span error gives `stop` (`max_turns` or `fatal_error`) plus `run.failed`. An interrupted segment gets `run.completed` with `terminal_reason=interrupted:tool_approval` and no `stop`. |

**Identity.**
- `run_id` = `trace_id`, and `session_id` = trace `group_id`.
- `agent_instance_id` = agent span id. `agent_definition` = agent name.
- `parent_agent_instance_id` comes from the handoff.
- On a `RunState` resume, the SDK opens a new agent span for the interrupted agent. The instrumentor keeps the original instance id, because it is the same logical instance, and keeps the new span id in `Identity.span_id`.
- `Versions.harness = openai-agents@0.24.0`. `Versions.model` comes from the generation span.
- Every event is capture tier A. Channels are `openai_agents.tracing` and `openai_agents.hooks`.
- Inputs, outputs, results, final messages and summaries are `PayloadRef` (sha256 plus size) only. The hook recorder stores only digests, never content.

**Merge.** The two channels merge on exact identifiers: `tool_call_id`, `response_id`, the turn span id, `child_agent_instance_id`, `compaction_item_id` and the final agent instance. 94 channel events became 52, in 26 merged groups. Every tool result in the main run has `source_channel = openai_agents.hooks+openai_agents.tracing`.

## 2. Measured v0.1 exception rate

Definitions:
- **Native signal:** one trace, one span, one hook callback, one approval record (interruption, approve, reject) or one wrapped `responses.compact` call.
- **Mapped:** produced at least one v0.1 event.
- **Structural:** consumed into v0.1 identity or correlation, or deduplicated against a sibling signal, without an event of its own. These are the root agent span, the interrupted agent span, trace end when task spans exist, and `on_agent_start` without a handoff.
- **Unmapped:** kept as `unknown` with `native_type` preserved.

| | Signals | Mapped | Structural | Unmapped |
|---|---|---|---|---|
| Tracing | 31 | 24 | 5 | 2 |
| Hooks + approvals + wrap | 39 | 35 | 4 | 0 |
| **Total** | **70** | **59** | **9** | **2** |

**v0.1 exception rate = 2 / 70 = 2.9%**. Tracing alone is 2 / 31 = 6.5%. Both are under the 10% gate, enforced by `test_gate_proof_b_openai_agents_exception_rate_under_10_percent`. For comparison, Claude Code is at 3.5% excluding the HOOK domain.

Unmapped native signals:
1. `span.guardrail` (`no_account_numbers`, `triggered=false`). v0.1 has no guardrail event. Mapping it to `verify.*` would conflate input policy with task verification, and mapping it to `permission.*` would misstate the actor.
2. `span.custom:orders.db_lookup`. These are application-defined custom spans, which no fixed schema can type.

Spans that exist but were not exercised would also be `unknown`: `mcp_tools`, `transcription`, `speech`, `speech_group`, output and tool guardrails.

## 3. Coverage matrix row (SPEC-06 §5.1 format)

| Concept | OpenAI Agents SDK 0.24.0 (Tier A instrumentor) |
|---|---|
| Run start/end | trace start; task span per `Runner.run` (end → run.completed/failed); resume reattaches the trace with no trace start/end, detected by a task span after trace end |
| Iteration/turn | `turn` span with native `turn` number (default on in 0.24.0; `TracingConfig.include_task_and_turn_spans`) |
| Model: model, tokens, finish | generation span `model`, `usage`; `response_id` in output and `ModelResponse`; **finish reason absent** (derived from output item types) |
| Tool request/decision/result | `function_call` output items (call id); function span (no call id, error `Error running tool (non-fatal)`); hooks `on_tool_start/end` with `tool_call_id` (failure visible only as the SDK default error string) |
| MCP | function span `mcp_data.server`; `mcp_tools` span (unknown in v0.1); not exercised |
| Permission decision + source | `needs_approval` → `RunResult.interruptions`; `RunState.approve/reject` (instrumented); no callback, no span event; rejection on resume emits nothing |
| Subagent | `handoff` span (`from_agent`, `to_agent`) + next agent span; `on_handoff`; agents-as-tools not exercised |
| Compaction trigger | model-emitted `compaction` output item (no trigger field); session compaction via `should_trigger_compaction` (no event) |
| Compaction tokens | none natively; the `responses.compact` wrap gives the compact call's usage |
| Compaction summary | `encrypted_content` (opaque; ref only) |
| Context provenance | none (instructions are a string on the agent; no load event) |
| Verification | adapter only |
| Stop reason | final output; task span error (`Max turns exceeded`, ...); `RunErrorHandlers` |
| Cost | tokens only (task/turn/generation usage); no cost |
| Raw bodies | generation span `input`/`output` when `trace_include_sensitive_data` (default on); removed, not redacted, when off |
| Propagation | in-process only (proprietary tracing, no OTel context) |

SPEC-06 has no per-harness row for the OpenAI Agents SDK. §5.2 is per concept and already names the right insertion points, so it was left unchanged. This row is the input for a §5.2 Tier A matrix.

## 4. Gaps and shape findings

1. **Function spans carry no tool call id.** The join to `call_id` goes through the generation output by (name, arguments). It is exact for distinct calls. Two identical calls in one turn would be matched in order, so the hooks channel's `ToolContext.tool_call_id` is the authority.
2. **Approvals have no event.**
   - A pending approval is a function span that ends with `output=None` and `error=None` and never runs the body. A tool that returns `None` may well have the same shape, so the instrumented `record_interruptions` is the exact source and the span shape only corroborates it.
   - A rejection made through `RunState.reject` before resume produces **no span and no hook** in 0.24.0. The only trace is a `ToolCallOutputItem` with the rejection message. The instrumented `reject()` is the only capture point.
   - The SDK sets a span error (`... was manually rejected by user.`) only on the in-span rejection branch of `_maybe_execute_tool_approval`. The mapper handles that branch (→ `permission.denied`), but the resume path in this scenario did not take it.
3. **Trace end is not run end.** An interrupted run ends its trace, and the resume reattaches it silently. Run boundaries come from task spans. With `include_task_and_turn_spans=False`, the instrumentor falls back to trace end and cannot see the resume.
4. **No compaction event.**
   - Server-side compaction is visible only as a `compaction` item inside the generation output. It has no trigger, no token counts and an opaque `encrypted_content`.
   - `OpenAIResponsesCompactionSession` emits nothing at all. It needed a client wrap, which is SPEC-06's "wrap" insertion point.
5. **Handoffs are transfers, not calls.** Control never returns to `triage`. `agent.returned` is paired at the end of the target's last agent span so that delegation edges close, and `AgentSpawned`/`AgentReturned` keep the parent as owner. Agents-as-tools, the nesting model, were not exercised.
6. **Hooks cannot see tool failure.** `on_tool_end` receives the model-facing string, so failure is recognized only by the SDK's default `failure_error_function` text. A custom error function hides it from hooks, and only the span error remains.
7. **The finish reason is not normalized.** Generation span output holds the provider `Response`, but the SDK has no `finish_reason` field.
8. **Sensitive-data toggling removes fields.** With `trace_include_sensitive_data=False`, the function span `input`/`output` and generation `input`/`output` are dropped. The join then falls back to tool name order, and the hooks channel (digests computed in-process) becomes the only source of input and output hashes.

Not exercised in 0.24.0 with this scenario:
- MCP servers (`mcp_tools`, `mcp_data`).
- Output and tool guardrails, and a tripwire that actually triggers.
- `MaxTurnsExceeded` and `RunErrorHandlers`.
- Agents-as-tools.
- The `response` span: the scripted model mirrors the Chat Completions path. The mapper handles `response` but it has no fixture.
- The realtime and voice spans.

All of these exist in 0.24.0. `CompactionItem`, `needs_approval`, `RunResult.interruptions`, `RunState.approve/reject` and `OpenAIResponsesCompactionSession` all exist and were exercised.

## 5. What the SDK would need to emit natively

1. `tool_call_id` on `FunctionSpanData` (and on `HandoffSpanData`), so the span tree joins to model output without matching on arguments.
2. Approval spans or events: `approval_requested`, plus `approval_decided {decision, source, always}` on `RunState.approve/reject` and on in-run approval callbacks.
3. A compaction span from both the model path (`CompactionItem`) and `OpenAIResponsesCompactionSession`, with `{trigger, tokens_before, tokens_after, preserved_items}`.
4. A `run_resumed` signal, or a trace start with `resumed=true`, when a trace is reattached from `RunState`.
5. A normalized `finish_reason` on generation and response spans.
6. Guardrail outcome as a typed event that SPEC-01 can adopt. This is the main v0.2 candidate from this harness, alongside Claude Code's HOOK domain.
