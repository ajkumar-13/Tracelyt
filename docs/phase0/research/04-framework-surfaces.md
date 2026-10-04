# Tier A Agent Framework Instrumentation Reference (verified against source, 2026-10-04)

## How this was built and how far to trust it

I shallow-cloned each repo's default branch on 2026-10-03/04 and read or grepped the source. Unless something is marked **[UNVERIFIED]**, the names below are quoted straight from source at these commits. Items marked **[from memory]** come from my own knowledge and I did not re-read them in this pass.

| Framework | Repo @ commit (date) | Package version in tree |
|---|---|---|
| LangGraph | langchain-ai/langgraph @ 9a0394d (2026-10-03) | langgraph 1.2.12 |
| LangChain v1 (middleware/callbacks used by LangGraph agents) | langchain-ai/langchain @ 57236d5 (2026-10-02) | langchain 1.4.3, langchain-core ≥1.6.3 |
| Deep Agents | langchain-ai/deepagents @ f57c6f3 | deepagents 0.7.21 |
| OpenAI Agents SDK (Py) | openai/openai-agents-python @ 81f0ccf (2026-10-02) | 0.23.1 |
| Google ADK (Py) | google/adk-python @ 86a47f6 (2026-10-03) | 2.11.0 |
| PydanticAI | pydantic/pydantic-ai @ c68786e (2026-10-03) | main, after v2.0.0 (2026-06-23) |
| Claude Agent SDK (Py) | anthropics/claude-agent-sdk-python @ 9c69ce7 | 0.2.163 |
| OpenHands SDK | OpenHands/software-agent-sdk @ b347047 | openhands-sdk 1.51.0 |
| CrewAI | crewAIInc/crewAI @ 738c8e1 (2026-10-02) | 1.15.23 |
| Mastra | mastra-ai/mastra @ 6a721a8e (2026-10-04) | @mastra/core 1.75.0-alpha.3, @mastra/observability 1.18.3 |
| AutoGen | microsoft/autogen @ 027ecf0 (2026-04-06) | **maintenance mode** (README points to microsoft/agent-framework) |
| AG2 | ag2ai/ag2 @ 77fb2fb (2026-10-03) | ag2 1.1.2 (new `ag2/` package; the old `autogen/` tree is no longer in this repo) |
| Vercel AI SDK | vercel/ai @ 15f1a4d (2026-10-03) | ai 7.0.127, @ai-sdk/otel 1.0.127 |

URL convention: `https://github.com/<org>/<repo>/blob/main/<path>`. All paths below are relative to the repo root.

---

## 1. LangGraph (plus LangChain v1 agents and Deep Agents)

### (a) Native telemetry
- LangGraph emits **no OpenTelemetry spans of its own**. A grep for `opentelemetry` under `libs/` only hits a test. Tracing goes through LangChain callbacks: LangSmith tracer, or OTel via LangSmith/third-party callback handlers.
- Every node and task runs as a LangChain Runnable, so each one produces `on_chain_start`/`on_chain_end` callbacks with `run_id`/`parent_run_id`.
- Task metadata is injected into callback `metadata`. Source: `libs/langgraph/langgraph/pregel/_algo.py` L655-659 and L848-852. Keys: `"langgraph_step"`, `"langgraph_node"`, `"langgraph_triggers"`, `"langgraph_path"`, `"langgraph_checkpoint_ns"`.
- Deep Agents sets `"lc_agent_name"` in metadata (`libs/deepagents/deepagents/graph.py` ~L996-999) and sets `"recursion_limit": 9_999`.
- **`TracePolicy`** (`libs/langgraph/langgraph/types.py`) is a per-node trace transform:
  - Fields: `process_inputs: Callable | None` and `process_outputs: Callable | None`.
  - Helper `omit_payload()` returns `{}`.
  - The docstring says it is "Not intended to redact secrets"; it only affects the node's own run.

### (b) Hook and callback surface

**LangChain core `BaseCallbackHandler`** (`libs/core/langchain_core/callbacks/base.py` in langchain repo):
- Handler methods: `on_llm_start(serialized, prompts, *, run_id, parent_run_id, tags, metadata, **kw)`, `on_chat_model_start(serialized, messages: list[list[BaseMessage]], *, run_id, parent_run_id, tags, metadata)`, `on_llm_new_token`, `on_llm_end`, `on_llm_error`, `on_chain_start(serialized, inputs, *, run_id, parent_run_id, tags, metadata)`, `on_chain_end`, `on_chain_error`, `on_tool_start(serialized, input_str, *, run_id, parent_run_id, tags, metadata, inputs)`, `on_tool_end`, `on_tool_error`, `on_retriever_start(serialized, query, ...)`, `on_retriever_end`, `on_retriever_error`, `on_retry`, `on_agent_action`, `on_agent_finish`, `on_text`, `on_custom_event`.
- **New:** `on_stream_event(event: MessagesData, *, run_id, parent_run_id, tags)`. It fires for `stream_events(version="v3")` protocol events: `message-start`, `content-block-start/-delta/-finish`, `message-finish`.

**LangGraph-specific `GraphCallbackHandler`** (`libs/langgraph/langgraph/callbacks.py`, new):
- `on_interrupt(event: GraphInterruptEvent)` and `on_resume(event: GraphResumeEvent)`. Pass the handler through `config["callbacks"]`.
- `GraphInterruptEvent` fields: `run_id: UUID|None`, `status: GraphLifecycleStatus`, `checkpoint_id: str`, `checkpoint_ns: tuple[str,...]`, `interrupts: tuple[Interrupt,...]`.
- `GraphResumeEvent` has the same fields minus `interrupts`.
- `GraphLifecycleStatus = Literal["input","pending","done","interrupt_before","interrupt_after","out_of_steps"]`.

**Stream modes** (`types.py`): `StreamMode = Literal["values","updates","checkpoints","tasks","debug","messages","custom"]`. `stream(..., version="v2")` returns typed `StreamPart`s with `{type, ns, data}`.
- `values` → `ValuesStreamPart{type, ns, data, interrupts}`.
- `updates` → `{type, ns, data: dict[node, update]}`.
- `messages` → `data: (AnyMessage, metadata dict)`.
- `custom` → `data: Any`, written through `StreamWriter`.
- `checkpoints` → `CheckpointPayload{config, metadata: CheckpointMetadata, values, next: list[str], parent_config, tasks: list[CheckpointTask]}`.
  - `CheckpointTask{id, name, error?, result?, interrupts?, state}`.
- `tasks` → `TaskPayload{id, name, input, triggers: list[str], metadata?}` on start, and `TaskResultPayload{id, name, error: str|None, interrupts: list[dict], result: dict}` on finish.
- `debug` → `_DebugCheckpointPayload{step, timestamp, type:"checkpoint", payload}`, `_DebugTaskPayload{step, timestamp, type:"task", payload: TaskPayload}`, or `_DebugTaskResultPayload{..., type:"task_result"}`.
- The mappers are in `pregel/debug.py`: `map_debug_tasks`, `map_debug_task_results`, `map_debug_checkpoint`. Tasks tagged `TAG_HIDDEN` are skipped.

**LangChain v1 `AgentMiddleware`** (`libs/langchain_v1/langchain/agents/middleware/types.py`). This is the hook surface for `create_agent` and Deep Agents:
- Hooks: `before_agent(state, runtime)`, `before_model`, `after_model`, `after_agent`, `wrap_model_call(request: ModelRequest, handler)`, `wrap_tool_call(request, handler)`, plus async `a*` variants.
- `ModelRequest` fields: `model, messages, system_message, tool_choice, tools, response_format, state, runtime, model_settings`.
- `AgentState`: `messages`, `jump_to`, `structured_response`.

### (c) Concept mapping
- **Run start/end:** root `on_chain_start`/`on_chain_end` (`parent_run_id is None`). For create_agent, `before_agent`/`after_agent`.
- **Iteration/step:** a Pregel superstep is `CheckpointMetadata.step`, and `metadata["langgraph_step"]` appears on every child callback.
  - Limit: `config["recursion_limit"]`. The loop sets `self.stop = self.step + recursion_limit + 1` (`pregel/_loop.py` L1729).
  - Exceeding it raises `GraphRecursionError`. The lifecycle status is `"out_of_steps"`.
- **Model call:** `on_chat_model_start` + `on_llm_end(LLMResult)`.
  - Tokens are in `AIMessage.usage_metadata` (`input_tokens`/`output_tokens`/`total_tokens`) **[from memory]**.
  - Finish reason sits in provider-specific `response_metadata` **[from memory]**. It is not normalized.
- **Tool call:** `on_tool_start`/`on_tool_end`/`on_tool_error`; `ToolMessage` in state; `wrap_tool_call`.
- **MCP tool:** no distinct marker. `langchain-mcp-adapters` turns MCP tools into ordinary `BaseTool` **[from memory]**.
- **HITL/interrupt:**
  - `interrupt(value, *, response_schema=None)` raises `GraphInterrupt(interrupts)`, an internal `GraphBubbleUp`.
  - `Interrupt` fields: `value`, `id`, `response_schema`.
  - Resume with `Command(resume=...)`. `Command` fields: `graph`, `update`, `resume`, `goto`.
  - `NodeInterrupt` is deprecated. Static `interrupt_before`/`interrupt_after` still exist.
  - Interrupts show up in the `__interrupt__` key of values/updates, `StateSnapshot.interrupts`, the checkpoint pending write channel `"__interrupt__"` (`serde/types.py`), and `GraphCallbackHandler.on_interrupt`.
  - `HumanInTheLoopMiddleware` (`middleware/human_in_the_loop.py`): `HITLRequest{action_requests: list[ActionRequest{name,args,description?}], review_configs: list[ReviewConfig{action_name, allowed_decisions, args_schema?}]}`. `DecisionType = Literal["approve","edit","reject","respond"]`. `HITLResponse{decisions}`.
- **Subgraph/subagent:**
  - Subgraphs get a nested `checkpoint_ns`. Separators are `NS_SEP="|"` and `NS_END=":"`. Visible in streams through `ns` when `subgraphs=True`.
  - `ParentCommand` bubbles `Command(graph=Command.PARENT)`.
  - Deep Agents: a `task` tool (`middleware/subagents.py`, `TaskToolSchema{description, subagent_type}`). `SubAgent` TypedDict: `name, description, tools, model, middleware, interrupt_on, skills, permissions, response_format, system_prompt, mode: "isolated"|"fork"`.
  - Async subagent tools: `start_async_task`, `check_async_task`, `update_async_task`, `cancel_async_task`, `list_async_tasks`.
- **Context management:**
  - `langchain_core.messages.utils.trim_messages(..., strategy="first"|"last")` and `filter_messages`.
  - `SummarizationMiddleware(trigger=..., keep=("messages",N), token_counter, summary_prompt, trim_tokens_to_summarize)` replaces history by writing `RemoveMessage(id=REMOVE_ALL_MESSAGES)` plus new messages. That is only observable as a state diff in `updates` or checkpoints.
  - Deep Agents `_DeepAgentsSummarizationMiddleware` writes the state key `_summarization_event: SummarizationEvent{cutoff_index, summary_message: HumanMessage, file_path}` and offloads history to `/conversation_history/{session_id}.md`. It also exposes a `compact_conversation` tool.
  - Also: `ContextEditingMiddleware` (`context_editing.py`).
- **Memory:** short-term memory is the checkpointer per `thread_id`. Long-term memory is `BaseStore` (`langgraph.store`) **[from memory]**, which has no callbacks.
- **Retrieval:** `on_retriever_*` callbacks.
- **Checkpoint** (`libs/checkpoint/langgraph/checkpoint/base/__init__.py`):
  - `Checkpoint{v, id (uuid6, monotonic), ts, channel_values, channel_versions, versions_seen, updated_channels}`. `pending_sends` appears in `copy_checkpoint`.
  - `CheckpointMetadata{source: "input"|"loop"|"update"|"fork", step, parents: dict[ns, checkpoint_id], run_id, counters_since_delta_snapshot (beta)}`.
  - `CheckpointTuple(config, checkpoint, metadata, parent_config, pending_writes: list[(task_id, channel, value)])`.
  - Special write channels: `"__error__"`, `"__scheduled__"`, `"__interrupt__"`, `"__resume__"`, `"__pregel_tasks"`.
  - Config keys: `thread_id`, `checkpoint_ns`, `checkpoint_id`.
  - Saver API: `get_tuple`, `list(config, *, filter, before, limit)`, `put(config, checkpoint, metadata, new_versions)`, `put_writes(config, writes, task_id, task_path="")`, `delete_thread`, `delete_for_runs`, `copy_thread`, `prune`, `get_delta_channel_history`, plus async `a*` variants.
  - Graph API: `get_state`, `get_state_history`, `update_state` (creates a `"update"` or `"fork"` source), `bulk_update_state`. You restore or fork by invoking with `checkpoint_id` in the config.
  - `StateSnapshot(values, next, config, metadata, created_at, parent_config, tasks: tuple[PregelTask], interrupts)`.
- **Durability:** `Durability = Literal["sync","async","exit"]`, passed as the `durability=` argument of stream/invoke.
- **Stop reason:** none as an enum. It has to be inferred: normal end, `GraphRecursionError`, interrupt, `ModelCallLimitExceededError`, etc.
- **Budgets/limits:**
  - `recursion_limit`.
  - `ModelCallLimitMiddleware(thread_limit, run_limit, exit_behavior="end"|"error")` raises `ModelCallLimitExceededError`.
  - `ToolCallLimitMiddleware`.
  - `TimeoutPolicy(run_timeout, idle_timeout, refresh_on)` raises `NodeTimeoutError{node, timeout, run_timeout, idle_timeout, elapsed, kind}`.
- **Guardrails:** middleware such as `pii.py` and `_redaction.py`. No guardrail-specific event.
- **Errors/retries:** `RetryPolicy(initial_interval=0.5, backoff_factor=2.0, max_interval=128.0, max_attempts=3, jitter=True, retry_on)`, the `on_retry` callback, `ModelRetryMiddleware`/`ToolRetryMiddleware`, `NodeError`, `NodeCancelledError`.

### (d) Privacy
- `TracePolicy`/`omit_payload` per node.
- LangSmith client `hide_inputs`/`hide_outputs`/`anonymizer` (named in the TracePolicy docstring).
- No global content-capture flag in LangGraph itself.

### (e) Recommended insertion point
1. A `BaseCallbackHandler` subclass that also inherits `GraphCallbackHandler`, injected through `config["callbacks"]`. It inherits to subgraphs and gives the run tree plus interrupt/resume events.
2. Optionally, tap `stream_mode=["tasks","checkpoints"]` (or `debug`) for authoritative step and state events.
3. Optionally, wrap the checkpointer (a proxy `BaseCheckpointSaver`) to capture every `put`/`put_writes`. That is the most reliable source for state, interrupts, and errors.
4. For create_agent/Deep Agents, an `AgentMiddleware` with `wrap_model_call`/`wrap_tool_call` gives clean model and tool boundaries.

---

## 2. OpenAI Agents SDK (Python)

### (a) Native telemetry
Tracing is proprietary (not OTel). Model: `Trace` → `Span[SpanData]`, sent through `TracingProcessor`s. The default exporter goes to the OpenAI backend. There is no OTel import in `src/agents`.

`Trace.export()` (`tracing/traces.py`): `{"object":"trace", "id", "workflow_name", "group_id", "metadata"}`.

`Span.export()` (`tracing/spans.py` L398): `{"object":"trace.span", "id", "trace_id", "parent_id", "started_at", "ended_at", "span_data", "error"}`, with optional `metadata`. `SpanError` = TypedDict `{message, data}`.

Span data classes in `src/agents/tracing/span_data.py`, with `type` values, constructor fields, and `export()` keys:

| Class | `type` | Fields | export() |
|---|---|---|---|
| `AgentSpanData` | `agent` | `name, handoffs, tools, output_type, metadata` | `type,name,handoffs,tools,output_type` |
| `TaskSpanData` (one Runner run) | `task` | `name, usage, metadata` | exported as `{"type":"custom","name":"task","data":{"sdk_span_type":"task","name",usage?}}` |
| `TurnSpanData` (one loop turn) | `turn` | `turn:int, agent_name, usage, metadata` | `{"type":"custom","name":"turn","data":{"sdk_span_type":"turn","turn","agent_name",usage?}}` |
| `FunctionSpanData` | `function` | `name, input, output, mcp_data` | `type,name,input,output,mcp_data` |
| `GenerationSpanData` | `generation` | `input, output, model, model_config, usage` | same keys |
| `ResponseSpanData` | `response` | `response, input, usage` (+ `_response_id`) | `type,response_id,usage` |
| `HandoffSpanData` | `handoff` | `from_agent, to_agent` | same |
| `CustomSpanData` | `custom` | `name, data` | same |
| `GuardrailSpanData` | `guardrail` | `name, triggered` | same |
| `TranscriptionSpanData` | `transcription` | `input, input_format, output, model, model_config` | `type,input{data,format},output,...` |
| `SpeechSpanData` | `speech` | `input, output, output_format, model, model_config, first_content_at` | |
| `SpeechGroupSpanData` | `speech_group` | `input` | |
| `MCPListToolsSpanData` | `mcp_tools` | `server, result` | `type,server,result` |

Notes:
- Task and turn spans are **opt-in**: `TracingConfig{api_key, include_task_and_turn_spans}` (`tracing/config.py`), passed as `RunConfig.tracing`.
- `GenerationSpanData` is produced by the Chat Completions model (`models/openai_chatcompletions.py`). The Responses model produces `ResponseSpanData` (`models/openai_responses.py`).
- MCP tool calls are `FunctionSpanData` with `mcp_data={"server": <server log name>}` (`mcp/util.py` L841).
- Span error messages (verbatim) include: `"Error running tool"`, `"Max turns exceeded"`, `"Guardrail tripwire triggered"`, `"Error getting response"`, `"Error streaming response"`, `"Multiple handoffs requested"`, `"Invalid JSON"`, `"MCP server label not found"`.

### (b) Hook surface
- **`TracingProcessor`** (`tracing/processor_interface.py`): `on_trace_start(trace)`, `on_trace_end(trace)`, `on_span_start(span)`, `on_span_end(span)`, `shutdown()`, `force_flush()`. `TracingExporter.export(items)`.
  - Register with `add_trace_processor` (additive) or `set_trace_processors` (replaces the default). Also `set_tracing_disabled` and `flush_traces`.
- **`RunHooksBase`** (`lifecycle.py`):
  - `on_llm_start(context, agent, system_prompt, input_items)`, `on_llm_end(context, agent, response: ModelResponse)`.
  - `on_agent_start(context: AgentHookContext, agent)`, `on_agent_end(context, agent, output)`, `on_handoff(context, from_agent, to_agent)`.
  - `on_tool_start(context, agent, tool)`, `on_tool_end(context, agent, tool, result)`. For function tools the context is a `ToolContext` with `tool_call_id`, `tool_name`, `tool_arguments`.
- **`AgentHooksBase`**: `on_start`, `on_end`, `on_handoff(context, agent, source)`, `on_tool_start`, `on_tool_end`, `on_llm_start`, `on_llm_end`.
- **Stream events** (`stream_events.py`):
  - `RawResponsesStreamEvent` (`raw_response_event`).
  - `RunItemStreamEvent` (`run_item_stream_event`) with `name ∈ {"message_output_created","handoff_requested","handoff_occured"(sic),"tool_called","tool_search_called","tool_search_output_created","tool_output","reasoning_item_created","mcp_approval_requested","mcp_approval_response","mcp_list_tools"}`.
  - `AgentUpdatedStreamEvent`.

### (c) Concept mapping
- **Run:** a trace, or a `task` span when enabled. `on_agent_start`/`on_agent_end`.
- **Turn:** `turn` span, `RunResult._current_turn`.
- **Model call:** generation/response span. `ModelResponse{output, usage, response_id, request_id, raw_usage}`. `Usage{requests, input_tokens, input_tokens_details, output_tokens, output_tokens_details, total_tokens, request_usage_entries}`. There is no normalized finish reason; it lives inside the raw `Response` object.
- **Tool:** function span. Items `ToolCallItem` (`tool_call_item`) and `ToolCallOutputItem` (`tool_call_output_item`). Errors: span error `"Error running tool"`, `ToolTimeoutError{tool_name, timeout_seconds}`, `RunConfig.tool_error_formatter`.
- **MCP:** function span with `mcp_data`; `mcp_tools` span for list_tools; `MCPListToolsItem`, `MCPApprovalRequestItem`, `MCPApprovalResponseItem`; `MCPToolCancellationError`.
- **Approval/HITL:**
  - `FunctionTool.needs_approval`.
  - Approvals surface as `ToolApprovalItem` (`tool_approval_item`) in `RunResult.interruptions`.
  - `RunState` (`run_state.py`, `CURRENT_SCHEMA_VERSION="1.18"`) supports `get_interruptions()`, `approve(item, always_approve=False)`, `reject(...)`, `to_json()`, `to_string()`, and `from_string()`.
  - This serialized `RunState` is the SDK's checkpoint.
- **Handoff:** `Handoff{tool_name, tool_description, input_json_schema, on_invoke_handoff, agent_name, input_filter}`; `handoff` span; `HandoffCallItem`/`HandoffOutputItem`; `on_handoff`. `RunConfig`: `handoff_input_filter`, `nest_handoff_history`, `handoff_history_mapper`. Agents-as-tools give `AgentToolInvocation{tool_name, tool_call_id, tool_arguments}`.
- **Context management:**
  - `RunConfig.call_model_input_filter` (hook over `ModelInputData`).
  - `CompactionItem` (`compaction_item`).
  - `OpenAIResponsesCompactionSession(compaction_mode="auto", should_trigger_compaction=...)` (`memory/openai_responses_compaction_session.py`).
  - `SessionSettings`.
- **Memory:** `Session` protocol (`memory/session.py`): `session_id`, `session_settings`, `get_items(limit)`, `add_items(items)`, `pop_item()`, `clear_session()`.
  - Implementations: `SQLiteSession`, `OpenAIConversationsSession`, `OpenAIResponsesCompactionSession`.
  - Extensions: `AdvancedSQLiteSession`, `AsyncSQLiteSession`, `DaprSession`, `EncryptedSession`, `MongoDBSession`, `RedisSession`, `SQLAlchemySession`.
  - There are no read/write callbacks, so wrap the Session.
- **Retrieval:** only as hosted tools (FileSearch) or function spans.
- **Stop/termination:**
  - `max_turns` (`DEFAULT_MAX_TURNS = 10`, `run_config.py` L45) raises `MaxTurnsExceeded`.
  - `RunErrorHandlers{max_turns, model_refusal, invalid_final_output}` can convert errors into results (`run_error_handlers.py`, input `RunErrorHandlerInput{error, context}` and `RunErrorData`).
  - Other exceptions (`exceptions.py`): `AgentsException(run_data: RunErrorDetails)`, `ModelBehaviorError`, `ModelRefusalError(refusal)`, `ModelTimeoutError`, `UserError`, `InputGuardrailTripwireTriggered`, `OutputGuardrailTripwireTriggered`, `ToolInputGuardrailTripwireTriggered`, `ToolOutputGuardrailTripwireTriggered`.
  - `RunErrorDetails{input, new_items, raw_responses, last_agent, context_wrapper, input/output/tool_* guardrail results}`.
- **RunResult fields** (`result.py`): `input, new_items, raw_responses, final_output, input_guardrail_results, output_guardrail_results, tool_input_guardrail_results, tool_output_guardrail_results, context_wrapper`, plus `last_agent`, `max_turns`, `interruptions`, `last_response_id`, `to_input_list()`.
- **Guardrails** (`guardrail.py`, `tool_guardrails.py`): `InputGuardrail(guardrail_function, name, run_in_parallel=True)`, `OutputGuardrail`, `GuardrailFunctionOutput{output_info, tripwire_triggered}`, `ToolInputGuardrail`/`ToolOutputGuardrail` with behaviors `RejectContentBehavior{type:"reject_content",message}` and `RaiseExceptionBehavior`. Each guardrail run gets a `guardrail` span.
- **Retries:** `ModelRetrySettings{max_retries, backoff,...}` (`retry.py`).

### (d) Privacy
- `RunConfig.trace_include_sensitive_data` defaults from env `OPENAI_AGENTS_TRACE_INCLUDE_SENSITIVE_DATA` (default `"true"`). When off, spans are still created but inputs/outputs are dropped.
- Log flags `OPENAI_AGENTS_DONT_LOG_MODEL_DATA` and `OPENAI_AGENTS_DONT_LOG_TOOL_DATA` (both default true; `_debug.py`).
- `EncryptedSession` covers stored memory.

### (e) Insertion point
- A `TracingProcessor` via `add_trace_processor()`, so you don't replace the OpenAI exporter. Enable `include_task_and_turn_spans`.
- Add `RunHooks` to get tool_call_id and arguments, and handoffs.
- Wrap the `Session` for memory.
- Use `RunResult.interruptions` and `RunState` for HITL and checkpoints.

---

## 3. Google ADK (Python)

### (a) Native telemetry: OTel, GenAI semconv, two schema versions
Source: `src/google/adk/telemetry/`, files `tracing.py`, `_instrumentation.py`, `node_tracing.py`, `context.py`, `_schema_version.py`, `_token_usage.py`, `_metrics.py`.

- **Schema switch:** `ADK_TELEMETRY_SCHEMA_VERSION_OPT_IN`. Value 1 is `SCHEMA_VERSION_LEGACY`, the default. Value 2 is `SCHEMA_VERSION_SEMCONV_ALIGNED`, the default when `GOOGLE_CLOUD_AGENT_ENGINE_ID` is set.

Span names (verbatim):

| Span | When |
|---|---|
| `invocation` | v1 root, per runner invocation |
| `invoke_workflow {name}` / `invoke_workflow` | v2 root and nested workflows (`gen_ai.workflow.nested=True` only on nested ones) |
| `invoke_node {node.name}` | v2 plain workflow node |
| `invoke_agent {agent.name}` | every agent invocation |
| `call_llm` | v1 legacy per-LLM-call span (marked for removal in the migration plan) |
| `generate_content {model}` | native inference span, unless `opentelemetry-instrumentation-google-genai` already wraps the call |
| `execute_tool {tool.name}`, `execute_tool (merged)` | tool calls (merged = parallel batch) |
| `compact_events {trigger}` | event compaction |
| `create_cache`, `handle_context_caching` | Gemini context cache |
| `send_data` | live mode |
| `managed_agent_interaction` | managed agents |

Attributes (verbatim):
- **invoke_agent:** `gen_ai.operation.name="invoke_agent"`, `gen_ai.agent.description`, `gen_ai.agent.name`, `gen_ai.conversation.id` (session id).
- **execute_tool:** `gen_ai.operation.name="execute_tool"`, `gen_ai.tool.description`, `gen_ai.tool.name`, `gen_ai.tool.type` (class name), `gen_ai.agent.name`, `gen_ai.tool.call.id`, `error.type`, `gcp.mcp.server.destination.id` (MCP), `gcp.vertex.agent.tool_call_args`, `gcp.vertex.agent.tool_response`, `gcp.vertex.agent.event_id`, `gcp.vertex.agent.llm_request="{}"`, `gcp.vertex.agent.llm_response="{}"`.
- **call_llm:** `gen_ai.system="gcp.vertex.agent"`, `gen_ai.request.model`, `gcp.vertex.agent.invocation_id`, `gcp.vertex.agent.session_id`, `gcp.vertex.agent.event_id`, `gcp.vertex.agent.llm_request`, `gcp.vertex.agent.llm_response`, `gen_ai.request.top_p`, `gen_ai.request.max_tokens`, `gen_ai.usage.experimental.reasoning_tokens_limit`, `gen_ai.response.finish_reasons` (lowercased list).
- **Usage** (`_token_usage.py`): `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`, `gen_ai.usage.cache_read.input_tokens`, `gen_ai.usage.cache_creation.input_tokens`, `gen_ai.usage.reasoning.output_tokens`, `gen_ai.usage.experimental.system_instruction_tokens`.
- **Experimental semconv path:** `gen_ai.input.messages`, `gen_ai.output.messages`, `gen_ai.system_instructions`, `gen_ai.tool.definitions`. Log events `gen_ai.system.message`, `gen_ai.user.message`, `gen_ai.choice`, `gen_ai.client.inference.operation.details`.
- **Compaction:** `gen_ai.compaction.{trigger, token_threshold, summarizer_type, start_timestamp, end_timestamp, result_event_id, overlap_size, event_retention_size, event_count, compaction_interval}`.
- **Aggregates (experimental):** `adk.experimental.invoke_agent.{input_tokens,output_tokens,total_tokens,cache_read.input_tokens,reasoning.output_tokens,tool.input_tokens,skill.loads}` and the same set under `adk.experimental.invoke_workflow.*`. Also `gen_ai.invoke_agent.{duration,inference_calls,tool_calls}`, `gen_ai.execute_tool.duration`, `gen_ai.invoke_workflow.duration`.
- **Other:** `adk.experimental.root_agent.name`, `adk.experimental.context_cache.{hit,fingerprint,contents_count,invocations_used}`, `gen_ai.skill.{name,description,resource.name,source.uri}`, `gcp.vertex.agent.associated_event_ids`.

### (b) Hook surface
**Agent callbacks** (`agents/base_agent.py`, `agents/llm_agent.py`). Each one may be a list, sync or async.
- `before_agent_callback` / `after_agent_callback`: `(CallbackContext) -> Optional[types.Content]`. Returning Content short-circuits.
- `before_model_callback`: `(CallbackContext, LlmRequest) -> Optional[LlmResponse]`.
- `after_model_callback`: `(CallbackContext, LlmResponse) -> Optional[LlmResponse]`.
- `on_model_error_callback`: `(CallbackContext, LlmRequest, Exception) -> Optional[LlmResponse]`.
- `before_tool_callback`: `(BaseTool, dict args, ToolContext) -> Optional[dict]`.
- `after_tool_callback`: `(BaseTool, dict args, ToolContext, dict result) -> Optional[dict]`.
- `on_tool_error_callback`: `(BaseTool, dict, ToolContext, Exception) -> Optional[dict]`.
- `CallbackContext`/`ReadonlyContext` properties: `user_content, invocation_id, agent_name, state, session, user_id, run_config, custom_metadata, is_aborted`.

**`BasePlugin`** (`plugins/base_plugin.py`). These are global across all agents in an `App(plugins=[...])`:
- `on_user_message_callback(invocation_context, user_message)`, `before_run_callback(invocation_context)`, `on_event_callback(invocation_context, event)`, `after_run_callback(invocation_context)`.
- `before_agent_callback(agent, callback_context)`, `after_agent_callback`.
- `before_model_callback(callback_context, llm_request)`, `after_model_callback(callback_context, llm_response)`, `on_model_error_callback(callback_context, llm_request, error)`.
- `before_tool_callback(tool, tool_args, tool_context)`, `after_tool_callback(..., result)`, `on_tool_error_callback(..., error)`.
- `on_agent_error_callback(agent, callback_context, error)`, `on_run_error_callback(invocation_context, error)`, `close()`.

**Event stream:** `Runner.run_async(user_id, session_id, invocation_id=None, new_message, state_delta, run_config, yield_user_message, abort_signal)` yields `Event`s.

### (c) Concept mapping
- **Event** (`events/event.py`, `class Event(LlmResponse)`): `invocation_id, author, actions: EventActions, output, node_info, long_running_tool_ids, branch, isolation_scope, id, timestamp`.
  - Inherited `LlmResponse` fields: `model_version, content, grounding_metadata, partial, turn_complete, turn_complete_reason, interaction_status, finish_reason, error_code, error_message, interrupted, custom_metadata, usage_metadata, cache_metadata, citation_metadata, interaction_id, ...`.
- **EventActions** (`events/event_actions.py`): `skip_summarization, state_delta, artifact_delta: dict[str,int], transfer_to_agent, transfer_reason, escalate, requested_auth_configs, requested_tool_confirmations: dict[str, ToolConfirmation], compaction: EventCompaction{start_timestamp, end_timestamp, compacted_content}, end_of_agent, agent_state, rewind_before_invocation_id, route, render_ui_widgets, set_model_response`.
- **Run:** `invocation`/`invoke_workflow` span; `before_run_callback`/`after_run_callback`.
- **Step:** each LLM call is one step, and `max_llm_calls` counts these.
- **Model call:** `generate_content`/`call_llm` span; `LlmResponse.usage_metadata`, `finish_reason`, `error_code`/`error_message`.
- **Tool call:** `function_call`/`function_response` parts in `Event.content`; `execute_tool` span; tool callbacks.
- **MCP:** `McpToolset`; tool span carries `gcp.mcp.server.destination.id` **[the MCP HTTP exchange tracing gates were not inspected in depth]**.
- **HITL:**
  - Tool confirmation emits function call `adk_request_confirmation` with `ToolConfirmation{hint, confirmed, payload}` (`tools/tool_confirmation.py`) and sets `EventActions.requested_tool_confirmations`.
  - Credential requests use `adk_request_credential`. Workflow input uses `adk_request_input`. Long-running tools set `Event.long_running_tool_ids`.
  - API: `request_confirmation()` and `request_credential()` (`agents/context.py`).
- **Transfer/delegation:**
  - The `transfer_to_agent` function call results in `EventActions.transfer_to_agent` and `transfer_reason`.
  - `escalate` exits a loop agent.
  - `AgentTool` wraps an agent as a tool.
  - `Event.branch` gives the agent-tree path.
- **Context management:** `App.events_compaction_config: EventsCompactionConfig{summarizer, compaction_interval, overlap_size, token_threshold, event_retention_size}`. This produces a compaction event (`EventActions.compaction`) and a `compact_events` span. Also `App.context_cache_config`, and `RunConfig.context_window_compression` for live mode.
- **Memory:** `BaseMemoryService.add_session_to_memory`, `add_events_to_memory`, `add_memory`, `search_memory`. Implementations: `InMemory...`, `_SqliteMemoryService`, `VertexAiMemoryBankService`, `VertexAiRagMemoryService`. **No callbacks; wrap the service.**
- **Session/state:**
  - `Session{id, app_name, user_id, state, events, last_update_time}`.
  - State prefixes `app:`, `user:`, `temp:` (`sessions/state.py`).
  - `BaseSessionService.create_session`, `get_session`, `list_sessions`, `delete_session`, `append_event`.
- **Checkpoint/rewind:** the session event log is the durable record. `Runner.rewind_async(user_id, session_id, rewind_before_invocation_id)`. `App.resumability_config: ResumabilityConfig{is_resumable}` with `EventActions.agent_state`/`end_of_agent`.
- **Limits:** `RunConfig.max_llm_calls` (default `_DEFAULT_MAX_LLM_CALLS=500`, env `ADK_MAX_LLM_CALLS`) raises `LlmCallsLimitExceededError` (`agents/invocation_context.py`).
- **Stop reason:** `finish_reason`, `turn_complete_reason`, `end_of_agent`, `escalate`, exceptions.
- **Guardrails:** implemented as `before_model`/`before_tool` callbacks or plugins. No dedicated type.

### (d) Privacy
`TelemetryConfig` (`telemetry/context.py`, attached through `RunConfig.telemetry`) has these fields:
- `capture_message_content` (overrides `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT`).
- `genai_semconv_stability_opt_in` (overrides `OTEL_SEMCONV_STABILITY_OPT_IN`; `gen_ai_latest_experimental`).
- `adk_experimental_telemetry_opt_in` (`ADK_EXPERIMENTAL_TELEMETRY`).
- `experimental_features_opt_in` (`ADK_EXPERIMENTAL_TELEMETRY_FEATURES`).

Related controls:
- Legacy `gcp.vertex.agent.*` content is controlled by default-on `ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS`.
- The admin lock `ADK_TELEMETRY_IGNORE_RUN_CONFIG` overrides per-request settings.
- Inline binary data is summarized before tracing.

### (e) Insertion point
- A `BasePlugin` registered on `App(plugins=[...])`. It is global, sees every agent, model, tool and event, and has error hooks.
- Run it alongside ADK's native OTel spans (set a TracerProvider) and correlate by `invocation_id`/`event_id`.
- Wrap the Memory/Session services for read/write visibility.

---

## 4. PydanticAI (v2)

### (a) Native telemetry: OTel/Logfire
Source: `pydantic_ai_slim/pydantic_ai/_instrumentation.py`, `models/instrumented.py`, `capabilities/instrumentation.py`.

- **v2 migration:** `Agent(instrument=...)` became `Agent(capabilities=[Instrumentation(...)])` (`docs/migration.md`). `Agent.instrument_all()` still exists.
- **`InstrumentationSettings`** fields: `tracer`, `include_binary_content=True`, `include_content=True`, `include_model_request_parameters=True`, `version: Literal[2,3,4,5,6] = DEFAULT_INSTRUMENTATION_VERSION (5)`, `use_aggregated_usage_attribute_names=True`. Constructor also takes `tracer_provider` and `meter_provider`.

Version differences (docstring, verbatim in substance):
- **v1:** no longer accepted. Only 2–6 are valid; 2, 3 and 4 raise a deprecation warning. **[UNVERIFIED historical detail: v1 put messages in per-message OTel events.]**
- **v2:** "uses the newer OpenTelemetry GenAI spec": `gen_ai.system_instructions`, and `gen_ai.input.messages`/`gen_ai.output.messages` on model request spans, plus `pydantic_ai.all_messages` on agent run spans. Legacy names (`InstrumentationNames.for_version(2)`): agent span `agent run` with attr `agent_name`; tool span `running tool` with `tool_arguments` and `tool_response`; output function span `running output function`.
- **v3:** v2 plus thinking tokens. Names become `invoke_agent {agent_name}` with `gen_ai.agent.name`, and `execute_tool {tool_name}` with `gen_ai.tool.call.arguments` and `gen_ai.tool.call.result`.
- **v4:** v3 plus semconv multimodal parts (`type='uri'`/`'blob'`).
- **v5 (default):** `CallDeferred`/`ApprovalRequired` no longer mark spans as ERROR.
- **v6 (opt-in):** tool results use `role='tool'`.

Spans and attributes:
- Model request span: `chat {model_name}`, `gen_ai.operation.name='chat'`.
- Full attribute set observed: `gen_ai.system`, `gen_ai.provider.name`, `gen_ai.request.model`, `gen_ai.response.model`, `gen_ai.response.id`, `gen_ai.response.finish_reasons`, `gen_ai.input.messages`, `gen_ai.output.messages`, `gen_ai.system_instructions`, `gen_ai.tool.definitions`, `gen_ai.tool.name`, `gen_ai.tool.call.id`, `gen_ai.tool.call.arguments`, `gen_ai.tool.call.result`, `gen_ai.usage.*`, `gen_ai.aggregated_usage.*` (agent spans, custom namespace), `gen_ai.agent.name`, `gen_ai.agent.description`, `gen_ai.agent.call.id` (run id, also baggage), `gen_ai.conversation.id`, `model_request_parameters`, `operation.cost`, `final_result`, `pydantic_ai.all_messages`, `pydantic_ai.new_message_index`, `pydantic_ai.tool.deferral.name`, `pydantic_ai.tool.deferral.metadata`, `pydantic_ai.tool.failure_stage`, `pydantic_ai.variable_instructions`, `pydantic_ai.workspace.id`, `pydantic_ai.workspace.provider`, `logfire.msg`, `logfire.json_schema`.
- Metrics: `gen_ai.client.token.usage` (`gen_ai.token.type`) and `gen_ai.client.operation.time_to_first_chunk`.

### (b) Hook surface: Capabilities
`capabilities/abstract.py`, `AbstractCapability`. Every hook takes `ctx: RunContext`. Signatures from AST:
- `before_run(ctx)`, `after_run(ctx, *, result)`, `on_run_error(ctx, *, error)`, `wrap_run`.
- `before_node_run(ctx, *, node)`, `after_node_run(ctx, *, node, result)`, `on_node_run_error(ctx, *, node, error)`, `wrap_node_run`.
- `on_event(ctx, *, event)`, `wrap_run_event_stream`.
- `before_model_request(ctx, request_context) -> ModelRequestContext`, `after_model_request(ctx, *, request_context, response) -> ModelResponse`, `on_model_request_error(ctx, *, request_context, error)`, `wrap_model_request`.
- `before_tool_validate(ctx, *, call, tool_def, args)`, `on_tool_validate_error(..., error)`, `wrap_tool_validate`.
- `before_tool_execute(ctx, *, call, tool_def, args)`, `after_tool_execute(..., result)`, `on_tool_execute_error(..., error)`, `wrap_tool_execute`.
- `before_/after_/wrap_/on_..._error` for `output_validate` and `output_process`.
- `handle_deferred_tool_calls(ctx, *, requests) -> DeferredToolResults|None`.
- A functional `Hooks` capability (`capabilities/hooks.py`) registers these as decorators.

Stream events (`messages.py`, `event_kind`): `part_start`, `part_delta`, `part_end`, `final_result`, `enqueued_messages`, `function_tool_call`, `output_tool_call`, `function_tool_result`, `tool_availability_delta`, `output_tool_result`, `deferred_tool_requests`, `deferred_tool_results`, `custom`, `capability`, `agent_run_result`, and realtime_* kinds.

### (c) Concept mapping
- **Run graph** (`_agent_graph.py`): `UserPromptNode` → `ModelRequestNode` → `CallToolsNode` → (loop) → `End`. Iterate with `agent.iter()`. Steps are node runs.
- **Model call:** `ModelResponse{parts, usage: RequestUsage, model_name, timestamp, provider_name, provider_url, provider_details, provider_response_id, finish_reason, run_id, conversation_id, metadata, workspace_ref, state}`. `FinishReason = Literal['stop','length','content_filter','tool_call','error']`.
- **Usage:** `RunUsage{requests, tool_calls, input_tokens, cache_write_tokens, cache_read_tokens, input_audio_tokens, cache_audio_read_tokens, output_tokens, details}`.
- **Limits:** `UsageLimits{cost_limit, request_limit=50, tool_calls_limit, input_tokens_limit, output_tokens_limit, total_tokens_limit, per_request_input_tokens_limit, count_tokens_before_request}`. Exceeding one raises `UsageLimitExceeded(AgentRunError)`.
- **Tool errors/retries:** `ModelRetry` (tool asks the model to retry), `ToolRetryError`, `UnexpectedModelBehavior`, `IncompleteToolCall`, `ContentFilterError`, `ModelHTTPError`, `FallbackExceptionGroup`.
- **Approval/deferred** (`_deferred.py`):
  - Tools raise `ApprovalRequired` or `CallDeferred`. The run ends with output `DeferredToolRequests{calls, approvals, metadata}`.
  - Resume with `DeferredToolResults{calls, approvals: dict[id, bool|ToolApproved|ToolDenied], metadata}`.
  - `ToolApproved{override_args, kind='tool-approved'}`, `ToolDenied{message='The tool call was denied.', kind='tool-denied'}`.
- **Context management:** `ProcessHistory(processor)` capability, which replaced `history_processors=`. The docs call it "a thin wrapper over `before_model_request`". Processors take `list[ModelMessage]` (optionally with `RunContext`) and return the processed list. **No event is emitted** when history is trimmed.
- **Subagents:** no first-class concept. You delegate by calling another agent inside a tool (nested `invoke_agent` spans) **[pattern; no dedicated type]**.
- **Memory/retrieval:** none built in, apart from message history passed in by the caller.
- **Checkpoint:** no saver. `AgentRunResult.all_messages()`/`new_messages()` (+`_json`) is the replayable record. Durable execution comes from `TemporalAgent` (`durable_exec/temporal`), `DBOSAgent`, `PrefectAgent`.
- **AG-UI:** `AGUIAdapter`/`AGUIEventStream` (`ui/ag_ui`). There is also a `ui/vercel_ai` adapter.
- **Stop reason:** `final_result` event, `End` node, `DeferredToolRequests` output, or exceptions.

### (d) Privacy
`include_content=False`, `include_binary_content=False`, `include_model_request_parameters=False`. `ContentPolicy`/`span_include_content` fail closed.

### (e) Insertion point
A custom `AbstractCapability` registered in `Agent(capabilities=[...])`. It has the richest typed hooks of all the frameworks here. Run it together with the `Instrumentation` capability, or a custom TracerProvider/SpanProcessor, to get the OTel spans.

---

## 5. Claude Agent SDK (Python): pointer only
- Message types: `src/claude_agent_sdk/types.py`.
- `Message = UserMessage | AssistantMessage | SystemMessage | ResultMessage | StreamEvent | RateLimitEvent | ConversationResetMessage`.
- `SystemMessage` subclasses: `TaskStartedMessage`, `TaskProgressMessage`, `TaskNotificationMessage`, `TaskUpdatedMessage`, `MirrorErrorMessage`, `HookEventMessage`. `SessionMessage` is at L1779.
- `HookEvent`: `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `UserPromptSubmit`, `Stop`, `SubagentStop`, `PreCompact`, `Notification`, `SubagentStart`, `PermissionRequest`.
- Parser: `src/claude_agent_sdk/_internal/message_parser.py`.

---

## 6. OpenHands SDK (software-agent-sdk)

### (a) Native telemetry
- Laminar (`lmnr`) / OTel through `openhands-sdk/openhands/sdk/observability/laminar.py`.
- Enabled when any of `LMNR_PROJECT_API_KEY`, `OTEL_ENDPOINT`, `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT`, `OTEL_EXPORTER_OTLP_ENDPOINT` is set.
- Span names from `@observe(name=...)`: `conversation.run`, `conversation.arun`, `conversation.send_message`, `agent.step`, `agent.astep`, `acp_agent.step`, `acp_agent.astep`, `MCPToolExecutor.call_tool`, `conversation.ask_agent`, `conversation.generate_title`, `hook.execute.agent`, `hook.execute.prompt`.
- Tool executions are spans named after the **tool name** with `span_type="TOOL"` and metadata `{"tool_call_id"}` (`agent/agent.py` ~L1498). LLM calls use `span_type="LLM"`.
- Metadata key: `openhands.operation`. Env: `OPENHANDS_OBSERVABILITY_METADATA`, `OPENHANDS_OBSERVABILITY_TAGS`, `OPENHANDS_OBSERVABILITY_SPAN_NAME`, `OPENHANDS_OBSERVABILITY_PARENT_SPAN_CONTEXT`, `LMNR_SPAN_CONTEXT`.
- The attributes are Laminar's own, not gen_ai semconv **[UNVERIFIED: exact attribute names not enumerated]**.

### (b) Hook surface
- **Conversation callbacks:** `ConversationCallbackType = Callable[[Event], None]` (`conversation/types.py`), passed as `Conversation(callbacks=[...])`. Every persisted event flows through them. Also an `on_token` streaming callback.
- **Hooks** (`hooks/types.py`): `PreToolUse`, `PostToolUse`, `UserPromptSubmit`, `SessionStart`, `SessionEnd`, `Stop` (Claude-Code-style shell hooks). They produce `HookExecutionEvent`s.

### (c) Event types
`openhands-sdk/openhands/sdk/event/`. Base is `Event{id, timestamp, source, parent_id}`.

| Event | Fields |
|---|---|
| `MessageEvent` | `source, llm_message, llm_response_id, activated_skills, extended_content, sender, critic_result` |
| `ActionEvent` | `source, thought, reasoning_content, thinking_blocks, responses_reasoning_item, action, tool_name, tool_call_id, tool_call, llm_response_id, security_risk, critic_result, summary` |
| `ObservationEvent` (`ObservationBaseEvent{source, tool_name, tool_call_id}`) | `observation, action_id, extended_content` |
| `UserRejectObservation` | `rejection_reason, rejection_source, action_id` |
| `AgentErrorEvent` | `source, error, classification` |
| `SystemPromptEvent` | `source, system_prompt, tools, dynamic_context` |
| `Condensation` | `forgotten_event_ids, summary, summary_offset, llm_response_id, source` |
| `CondensationRequest` | `source` |
| `CondensationSummaryEvent` | `summary, source` |
| `ConversationErrorEvent` | `code, detail, classification` (`ErrorClassification{kind: FailureKind, retryable, user_action, error_id}`) |
| `ConversationStateUpdateEvent` | `source, key, value` |
| `HookExecutionEvent` | `hook_event_type, hook_command, tool_name, success, blocked, exit_code, stdout, stderr, reason, additional_context, error, action_id, message_id, hook_input` |
| `LLMCompletionLogEvent` | `filename, log_data, model_name, usage_id` |
| `ACPToolCallEvent` | `tool_call_id, title, status, tool_kind, raw_input, raw_output, content, is_error` |
| `StreamingDeltaEvent`, `TokenEvent` (`prompt_token_ids, response_token_ids`), `PauseEvent`, `InterruptEvent` | |

`Action` and `Observation` base classes (`tool/schema.py`): `Observation{content: list[TextContent|ImageContent], is_error}`.

**Concept mapping:**
- **Run:** `conversation.run()`. The loop is in `conversation/impl/local_conversation.py` `_run()`.
- **Iteration:** one `agent.step(...)` per loop pass. Limit `max_iteration_per_run` (default 500). When reached: `ConversationErrorEvent(code="MaxIterationsReached")` and status `ERROR`.
- **Budget:** `max_budget_per_run` is compared against `conversation_stats.get_combined_metrics().accumulated_cost`, which emits `code="MaxBudgetReached"`.
- **Status:** `ConversationExecutionStatus`: `idle`, `running`, `paused`, `waiting_for_confirmation`, `finished`, `error`, `stuck`, `deleting`. Terminal: FINISHED, ERROR, STUCK.
- **Model metrics:** `Metrics{costs, response_latencies, token_usages}`. `TokenUsage{model, prompt_tokens, completion_tokens, cache_read_tokens, cache_write_tokens, reasoning_tokens, context_window, per_turn_token, response_id}`.
- **Permission/confirmation:**
  - `ConfirmationPolicyBase`: `AlwaysConfirm`, `NeverConfirm`, `ConfirmRisky`.
  - `SecurityRisk`: `UNKNOWN`/`LOW`/`MEDIUM`/`HIGH`, set on `ActionEvent.security_risk` by the `security_analyzer` (`security/analyzer.py`, `llm_analyzer.py`, `grayswan/`, `defense_in_depth/`).
  - Flow: status goes to `WAITING_FOR_CONFIRMATION`, then `reject_pending_actions(reason)` produces a `UserRejectObservation`, or calling `run()` again counts as implicit approval.
- **Subagents:** `subagent/` registry. Tools `delegate` and `task` live in `openhands-tools/openhands/tools/{delegate,task}` **[internals not read]**.
- **Context compaction:** `LLMSummarizingCondenser(llm, max_size=240, max_tokens, keep_first=2, minimum_progress=0.1, hard_context_reset_max_retries=5, hard_context_reset_context_scaling=0.8)`. Also `NoOpCondenser`, `PipelineCondenser`. Compaction is a first-class `Condensation` event listing `forgotten_event_ids`, so it is fully observable.
- **Persistence/replay:** `EventLog` (`conversation/event_store.py`) stores files under `events/` plus `base_state.json`. `ConversationState{id, agent, workspace, persistence_dir, max_iterations, stuck_detection, execution_status, confirmation_policy, security_analyzer, activated_knowledge_skills, ..., blocked_actions, blocked_messages}`. Events carry `parent_id`, which enables branching (`state.active_branch()`, `Conversation.fork()`).

### Stuck detector, in detail (`conversation/stuck_detector.py`)
**Defaults** (`StuckDetectionThresholds`): `action_observation=4`, `action_error=3`, `monologue=3`, `alternating_pattern=6`.

**Scan window:** `MAX_EVENTS_TO_SCAN_FOR_STUCK_DETECTION = 20` events from `state.active_branch(limit=20)`, truncated to the events **after the last user `MessageEvent`**.

**`is_stuck()`:**
1. Returns False if the window has fewer events than `min(action_observation, action_error, monologue)`.
2. Collects the last `max(action_observation, action_error+1)` `ActionEvent`s and `ObservationBaseEvent`s, newest first.
3. Checks these scenarios in order:
   - **Scenario 1 (repeat action+observation):** the last N=4 actions are all `_event_eq` to the newest one, and the last 4 observations are all equal to each other.
   - **Scenario 2 (action-error):** the trailing streak where each action equals the newest action and each paired observation is an `AgentErrorEvent`. Stuck if the streak is `> action_error` (strictly more than 3).
   - **Scenario 3 (monologue):** walking back, count agent-source `MessageEvent`s until a user message or a non-message event. `CondensationSummaryEvent` is skipped, so it does not break the run. Stuck if count ≥ 3.
   - **Scenario 4 (alternating):** needs ≥6 events. Takes the last 6 actions and the last 6 `ObservationEvent|AgentErrorEvent`. Stuck if `a[i] == a[i+2]` and `o[i] == o[i+2]` for `i < 4`, i.e. an ABAB pattern.
   - **Scenario 5 (context-window error loop):** a stub that always returns False (TODO, issue #282).

**`_event_eq`** ignores ids:
- `ActionEvent`: compares `source`, `thought`, `action`, `tool_name`.
- `ObservationEvent`: compares `source`, `observation`, `tool_name`.
- `AgentErrorEvent`: compares `source`, `error`.
- `MessageEvent`: compares `source`, `llm_message`.
- Different types are never equal.

**Nudge:** `get_action_error_nudge()` fires once per streak, when the action-error streak is exactly `== action_error` (3). It is de-duplicated by `_last_nudged_error_event_id`. It injects `MessageEvent(source="environment", role="user")` with text: "You've called `{tool_name}` with the same arguments {threshold} times in a row and gotten the same error each time: {error}. Repeating the exact same call again will not work — review the error message and either correct the arguments or try a different approach."

**Loop integration** (`_check_stuck_or_nudge`, called before each `agent.step`): nudge first. Otherwise, if `is_stuck()`, set `execution_status = STUCK`; the next loop pass breaks.
- No dedicated "stuck" event is emitted. The only signal is the status change, probably through `ConversationStateUpdateEvent(key="execution_status")` **[UNVERIFIED that the status change emits that event]**, plus a log warning.
- A new user message resets FINISHED/STUCK to IDLE.
- Enabled by `stuck_detection=True` (default) and `stuck_detection_thresholds=...` on the Conversation.

### (d) Privacy
Laminar `ignore_inputs`/`ignore_output` per decorated function. `secret_registry.py` masks secrets **[mechanics not read]**. There is no global content-capture flag.

### (e) Insertion point
- A conversation callback (`callbacks=[fn]`) receiving every `Event`. This is the complete, typed, ordered log.
- Add an OTel/Laminar tracer for timing.
- Poll `state.execution_status` or watch state-update events for stuck/limit termination.

---

## 7. CrewAI

### (a) Native telemetry: two separate systems
1. **Anonymous product telemetry** (`lib/crewai/src/crewai/telemetry/telemetry.py`), exporting to `https://telemetry.crewai.com:4319`.
   - Span names: `Crew Created`, `Task Created`, `Task Execution`, `Tool Repeated Usage`, `Tool Usage`, `Tool Usage Error`, `Crew Individual Test Result`, `Crew Test Execution`, `Crew Execution`, `Flow Creation`, `Flow Plotting`, `Flow Execution`, `Crew Completed`, `Flow Completed`, `Flow Paused`, `Flow Method Failed`, `Environment Context`, `Human Feedback`, `Feature Usage`, `Template Installed`, plus deploy spans.
   - Content is included only when `crew.share_crew`.
   - Disable with `OTEL_SDK_DISABLED`, `CREWAI_DISABLE_TELEMETRY`, `CREWAI_DISABLE_TRACKING` (`lib/crewai-core/src/crewai_core/telemetry.py`).
   - It deliberately does **not** install a global TracerProvider.
2. **Event-driven execution tracing (OTel, gen_ai semconv)** (`telemetry/tracing/handlers.py`, `semantic_conventions.py`, `session.py`). A `TraceSession(execution_uuid, exporters, resource, attributes, processors, ...)` subscribes to the event bus and creates spans.
   - Span names: `execute crew`, `execute task`, `execute agent`, `call tool`, `execute flow`, `call method`, `call llm` (CLIENT), `agent reasoning`, `evaluate guardrail`, `query memory`, `retrieve memory`, `save memory`, `query knowledge`, `search knowledge`, `discover skills`, `connect mcp`, `execute mcp tool`, `a2a delegate`, `a2a conversation`, `a2a server task`, `a2a parallel delegate`.
   - Operation names: `invoke_workflow`, `execute_method`, `execute_task`.
   - gen_ai attributes: `gen_ai.operation.name, provider.name, request.{model,temperature,top_p,max_tokens,seed,stop_sequences,frequency_penalty,presence_penalty,stream,choice.count}, response.{id,model,finish_reasons}, usage.{input_tokens,output_tokens,cache_read.input_tokens,cache_creation.input_tokens,reasoning_tokens}, input.messages(.size), output.messages(.size), system_instructions, tool.{name,type,definitions,call.arguments,call.result}, agent.{id,name,description}, conversation.id, workflow.name, output.type`.
   - `crewai.*` attributes, for example: `crewai.event_name`, `crewai.subject`, `crewai.execution_uuid`, `crewai.crew.{id,key,name,process,inputs,output,usage_metrics,num_agents,num_tasks,execution_duration_ms}`, `crewai.task.*`, `crewai.agent.{role,key,llm_calls_count,execution_duration_ms}`, `crewai.tool.{from_cache,failure.code/message/policy/reason/retryable}`, `crewai.memory.*`, `crewai.knowledge.*`, `crewai.mcp.*`, `crewai.guardrail.*`, `crewai.policy.*`, `crewai.human_feedback.*`, `crewai.reasoning.*`, `crewai.skill.*`, `crewai.flow.*`, `crewai.method.*`.
   - **[UNVERIFIED: whether OSS users are expected to construct `TraceSession` directly; `execution.py` builds it from a hosted "grant".]**
3. Separately, `events/listeners/tracing/trace_listener.py` batches events for the CrewAI AMP platform.

### (b) Hook surface: event bus
- `crewai_event_bus` (`events/event_bus.py`): `.on(EventType)` decorator, `emit`, `aemit`, `register_handler`, `scoped_handlers()`. Subclass `BaseEventListener.setup_listeners(crewai_event_bus)`.
- Interception hooks: `@before_llm_call`, `@after_llm_call`, `@before_tool_call`, `@after_tool_call` (`hooks/decorators.py`). These produce `HookDispatchedEvent{interception_point, outcome, hook_count, duration_ms, abort_reason, abort_source}`.
- **`BaseEvent` fields:** `timestamp, source_fingerprint, source_type, fingerprint_metadata, task_id, task_name, agent_id, agent_role, event_id, parent_event_id, previous_event_id, triggered_by_event_id, started_event_id, emission_sequence`. These give a causal tree and an ordering.

Event classes with `type` strings (`events/types/*.py`):
- **Crew:** `crew_kickoff_started{inputs}`, `crew_kickoff_completed{output,total_tokens}`, `crew_kickoff_failed{error}`, train/test events. Base fields `crew_name, crew`.
- **Agent:** `agent_execution_started{agent,task,tools,task_prompt}`, `agent_execution_completed{agent,task,output}`, `agent_execution_error`, `lite_agent_execution_*`, `agent_evaluation_*`.
- **Task:** `task_started{context,task}`, `task_completed{output,task}`, `task_failed{error,error_type,task}`, `task_evaluation`.
- **LLM** (base `from_task, from_agent, model, call_id`): `llm_call_started{messages,tools,callbacks,available_functions,temperature,top_p,max_tokens,stream,seed,stop_sequences,...}`, `llm_call_completed{messages,response,call_type,usage,finish_reason,response_id}`, `llm_call_failed{error}`, `llm_stream_chunk{chunk,tool_call,call_type,response_id}`, `llm_thinking_chunk`.
- **Tool** (base `agent_key, agent_role, agent_id, tool_name, tool_args, tool_class, run_attempts, delegations, agent, task_name, task_id, plan_step_number, plan_step_description, ...`): `tool_usage_started`, `tool_usage_finished{started_at,finished_at,from_cache,output,failure}`, `tool_usage_error{error}`, `tool_failure_detected{failure,policy}`, `tool_validate_input_error`, `tool_selection_error`, `tool_execution_error`.
- **MCP** (base `server_name, server_url, transport_type, ...`): `mcp_connection_started/completed/failed`, `mcp_tool_execution_started{tool_name,tool_args}`, `mcp_tool_execution_completed{...,result,execution_duration_ms}`, `mcp_tool_execution_failed{...,error,error_type}`, `mcp_config_fetch_failed`.
- **Memory:** `memory_query_started{query,limit,score_threshold}`, `memory_query_completed{...,results,query_time_ms}`, `memory_query_failed`, `memory_save_started{value,metadata,agent_role}`, `memory_save_completed{...,save_time_ms}`, `memory_save_failed`, `memory_retrieval_started/completed{memory_content,retrieval_time_ms}/failed`.
- **Knowledge:** `knowledge_search_query_started`, `knowledge_query_started/completed/failed`, `knowledge_search_query_failed`. `KnowledgeRetrievalCompletedEvent{query, retrieved_knowledge}`; its type string was not captured by my regex **[UNVERIFIED]**.
- **Guardrail:** `llm_guardrail_started{guardrail,retry_count}`, `llm_guardrail_completed{success,result,error,retry_count}`.
- **Reasoning/planning:** `agent_reasoning_*`, `plan_step_*`, `step_observation_*`, `plan_refinement`, `plan_replan_triggered`, `goal_achieved_early`.
- **Flow:** `flow_started`, `flow_created`, `method_execution_started{method_name,state,params}`, `method_execution_finished`, `method_execution_failed`, `method_execution_paused`, `flow_finished`, `flow_failed`, `flow_paused`, `flow_input_requested`, `flow_input_received`, `human_feedback_requested{method_name,output,message,emit,request_id}`, `human_feedback_received{feedback,outcome,request_id}`, `conversation_message_added`, `conversation_turn_started/completed/failed`, `conversation_route_selected`.
- **Checkpoint:** `checkpoint_started/completed{checkpoint_id,duration_ms}/failed/pruned` (base `location, provider, trigger, branch, parent_id`), `checkpoint_fork_started/completed{branch,parent_branch,parent_checkpoint_id}`, `checkpoint_restore_started/completed{checkpoint_id,branch,parent_id,duration_ms}/failed`.
- **A2A** (many): `a2a_delegation_started/completed`, `a2a_conversation_*`, `a2a_message_sent`, `a2a_response_received`, `a2a_polling_*`, `a2a_streaming_*`, `a2a_connection_error`, `a2a_server_task_*`, etc.
- **Skills:** `skill_discovery_*`, `skill_loaded`, `skill_activated`, `skill_used`, `skill_load_failed`.
- **System:** `SIGTERM`, `SIGINT`, `SIGHUP`, `SIGTSTP`, `SIGCONT`.

### (c) Concept mapping
- **Limits:** `max_iter` (default 25), `max_rpm` (agent and crew), `max_execution_time`, `max_retry_limit`, `respect_context_window` (summarizes on overflow; no dedicated event **[UNVERIFIED]**), `guardrail` + `guardrail_max_retries` on Agent/Task, `tool_failure_policy`.
- **HITL:** `Task.human_input`. In Flows, `@human_feedback` emits `human_feedback_requested`/`received` and `flow_input_requested`/`received`.
- **Delegation:** `Process.hierarchical` with `manager_llm`/`manager_agent`. Delegation tools are named `Delegate work to coworker` and `Ask question to coworker` (`utilities/agent_utils.py`). They appear as tool events, and `ToolUsageEvent.delegations` counts them.
- **Memory:** unified `Memory` class (`memory/unified_memory.py`): `remember`, `remember_many`, `recall`, `forget`, `update`, `scope`, `slice`, `list_scopes`, `list_records`, `reset`. Fully evented.
- **Checkpoint:** `CheckpointConfig{location, on_events, provider, max_checkpoints, restore_from}`; `RuntimeState.checkpoint(location)`, `.fork(branch)`, `.from_checkpoint(config)`; `Crew.from_checkpoint`, `Crew.fork`. The snapshot is `RuntimeState.model_dump_json()` (`state/runtime.py`).

### (d) Privacy
Product telemetry content requires `share_crew`. The env opt-outs are listed above. The execution tracer has no content flag; I found no capture/redact settings in `handlers.py` **[UNVERIFIED]**.

### (e) Insertion point
A `BaseEventListener` subclass with handlers on `crewai_event_bus`. It is the most complete surface, and `parent_event_id`/`started_event_id` give span pairing. Optionally use `TraceSession` with your own exporter for gen_ai OTel spans.

---

## 8. Mastra

### (a) Native telemetry ("AI tracing")
Types: `packages/core/src/observability/types/tracing.ts`. Runtime: `observability/mastra` (@mastra/observability).

**`SpanType`:** `agent_run`, `scorer_run`, `classifier_evaluation`, `scorer_step`, `generic`, `model_generation`, `model_step`, `model_inference`, `model_chunk`, `mcp_tool_call`, `mcp_server_request`, `processor_run`, `tool_call`, `client_tool_call`, `provider_tool_call`, `workflow_run`, `workflow_step`, `workflow_conditional`, `workflow_conditional_eval`, `workflow_parallel`, `workflow_loop`, `workflow_sleep`, `workflow_wait_event`, `memory_operation`, `workspace_action`, `rag_ingestion`, `rag_embedding`, `rag_vector_operation`, `rag_action`, `graph_action`, `mapping`, `skill_resolution`, `skill_action`, `agent_signal`.

**Span fields:** `id, traceId, name, type, entityType, entityId, entityName, startTime, endTime, attributes, metadata, tags, input, output, errorInfo, requestContext, isEvent, isInternal, tracingPolicy, parent`.

**Attributes per type:**
- `AgentRunAttributes`: `conversationId, instructions, prompt, availableTools, maxSteps, resolvedVersionId, tripwireAbort`.
- `ModelGenerationAttributes`: `model, provider, tools, resultType, usage, usageIncomplete, costContext, parameters, streaming, finishReason, completionStartTime, responseModel, responseId, serverAddress, serverPort`.
- `ModelStepAttributes`: `stepIndex, usage, finishReason, isContinued, warnings`.
- `ModelInferenceAttributes`: `model, provider, stepIndex, usage, finishReason, streaming, ..., toolChoice, responseFormat`.
- `ToolCallAttributes`: `toolType, toolDescription, toolCallId, success`.
- `MCPToolCallAttributes`: `toolType, mcpServer, serverVersion, toolDescription, toolCallId, success`.
- `WorkflowStepAttributes`: `status, entryDescription, entryMetadata`.
- `MemoryOperationAttributes`: `operationType: 'recall'|'save'|'delete'|'update'|'observe'|'reflect', messageCount, embeddingTokens, semanticRecallEnabled, vectorResultCount, workingMemoryEnabled, lastMessages, inputTokens, selectedModel, multiThread`.

**Tracing events:** `TracingEventType`: `span_started`, `span_updated`, `span_ended`.

**OTel exporter** (`observability/otel-exporter/src/gen-ai-semantics.ts`):
- Operation mapping: model → `chat`, `model_step` → `agent_step`, tool/mcp/provider tool → `execute_tool`, `agent_run` → `invoke_agent`, `workflow_run` → `invoke_workflow`, `rag_embedding` → `embeddings`.
- Span name is `"${operation} ${identifier}"`.
- Attributes: standard `gen_ai.*` plus `mastra.span.type`, `mastra.agent_run.max_steps`, `mastra.model_step.{step_index,is_continued}`, `mastra.mcp_tool_call.{server_name,server_version}`, `mastra.workflow_run.status`, `mastra.workflow_step.{step_id,status,...}`, `mastra.workflow_loop.*`, `mastra.workflow_parallel.*`, `mastra.workflow_sleep.*`, `mastra.workflow_wait_event.*`, `mastra.metadata.*`, `mastra.tags`, `mastra.input`/`mastra.output`.

**Exporters** (`observability/*`): arize, arthur, braintrust, datadog, laminar, langfuse, langsmith, posthog, sentry, otel-exporter, otel-bridge, plus internal console/default/cloud/mastra-storage/mastra-platform.

### (b) Hook surface
- **`ObservabilityExporter`** (`types/core.ts`): `name`, `init?`, `exportTracingEvent(event)`, `addScoreToTrace?`. It extends `ObservabilityEvents`: `onTracingEvent?`, `onLogEvent?`, `onMetricEvent?`, `onScoreEvent?`, `onFeedbackEvent?`, `onDroppedEvent?`.
- `SpanOutputProcessor` (e.g. `SensitiveDataFilter`).
- Agent processors (`packages/core/src/processors`) act as middleware: input/output processors, `TokenLimiterProcessor`, `ToolCallFilter`, moderation, PII, prompt-injection.

### (c) Concept mapping
- **Steps:** `maxSteps`/`stopWhen`.
- **HITL/approval:** tool `requireApproval` emits stream chunks `tool-call-approval` and `tool-call-suspended`. Resolve with `approveToolCall()`/`declineToolCall()`/`resumeStream()`.
- **Guardrails:** processor `abort()` emits a `tripwire` chunk, recorded as `tripwireAbort` on the span.
- **Agent network:** `agent.network(...)` (`loop/network/index.ts`) emits chunks `routing-agent-start/end`, `agent-execution-start/end`, `workflow-execution-start/end/suspended`, `tool-execution-start/end/approval/suspended`, `network-execution-event-step-finish`, `network-execution-event-finish`, `network-validation-start/end`.
- **Workflow snapshot** (`workflows/types.ts` `WorkflowRunState`): `runId, status, result, error, requestContext, value, context (per-step SerializedStepResult), serializedStepGraph, activePaths, activeStepsPath, suspendedPaths, resumeLabels, waitingPaths, timestamp, tripwire, stepExecutionPath, tracingContext`.
  - `WorkflowRunStatus`: `running|success|failed|tripwire|suspended|waiting|pending|canceled|bailed|paused|skipped`.
  - Snapshots persist in storage and resume with `run.resume({step, resumeData})` **[resume API from memory]**.
- **Memory** (`memory/types.ts`): `lastMessages`, `semanticRecall`, `workingMemory`, `observationalMemory`, `generateTitle`. Traced as `memory_operation`.

### (d) Privacy
`hideInput`/`hideOutput` in TracingOptions, the `SensitiveDataFilter` span processor (`observability/mastra/src/span_processors/sensitive-data-filter.ts`), and internal-span policy.

### (e) Insertion point
A custom `ObservabilityExporter` (implement `exportTracingEvent`/`onTracingEvent`) registered in the Mastra observability config. Read the stream chunks for approval and network detail.

---

## 9. AutoGen (microsoft/autogen, maintenance mode) and AG2

### AutoGen core
`python/packages/autogen-core/src/autogen_core/_telemetry/`.

- **Runtime messaging spans** (`_tracing_config.py`): `f"autogen {operation} {destination}"`.
  - `MessagingOperation = "create"|"send"|"publish"|"receive"|"intercept"|"process"|"ack"`.
  - Destination is `"{type}.({key})-A"` for an agent or `"{type}.({source})-T"` for a topic.
  - Attributes: `messaging.operation`, `messaging.destination`, `messaging.message.envelope.size`, `messaging.message.type`.
  - Span kind: PRODUCER for create/send/publish, CONSUMER for the rest.
  - Disable with `AUTOGEN_DISABLE_RUNTIME_TRACING=true`.
- **GenAI spans** (`_genai.py`): `execute_tool {tool_name}`, `create_agent {agent_name}`, `invoke_agent {agent_name}`.
  - Attributes: `gen_ai.operation.name`, `gen_ai.system="autogen"`, `gen_ai.agent.{id,name,description}`, `gen_ai.tool.{call.id,name,description}`, `error.type`.
  - Callers: `tools/_base.py`, agentchat `_base_chat_agent.py`, `_chat_agent_container.py`, and the MCP workbench in autogen-ext.
  - **No `chat` span with tokens.** LLM data comes through structured logging instead.
- **Structured logging** (`logging.py`, logger `autogen_core.events`): `LLMCallEvent{messages, response, prompt_tokens, completion_tokens}`, `LLMStreamStartEvent`, `LLMStreamEndEvent`, `ToolCallEvent`, `MessageEvent`, `MessageDroppedEvent`, `MessageHandlerExceptionEvent`, `AgentConstructionExceptionEvent`.
- **AgentChat:**
  - Messages: `TextMessage`, `MultiModalMessage`, `StopMessage`, `HandoffMessage`, `ToolCallSummaryMessage`, `StructuredMessage`.
  - Events: `ToolCallRequestEvent`, `ToolCallExecutionEvent`, `CodeGenerationEvent`, `CodeExecutionEvent`, `UserInputRequestedEvent`, `MemoryQueryEvent`, `ModelClientStreamingChunkEvent`, `ThoughtEvent`, `SelectSpeakerEvent`, `SelectorEvent`.
  - `TaskResult{messages, stop_reason}`.
  - Termination conditions: `MaxMessageTermination`, `TextMentionTermination`, `TokenUsageTermination`, `HandoffTermination`, `TimeoutTermination`, `ExternalTermination`, `SourceMatchTermination`, `TextMessageTermination`, `FunctionCallTermination`, `StopMessageTermination`, `FunctionalTermination`.
  - Contexts (`model_context/`): `Buffered`, `HeadAndTail`, `TokenLimited`, `Unbounded`.
  - State: `save_state()`/`load_state()` **[from memory]**.
- **Insertion point:** pass a TracerProvider to the runtime, attach a `logging.Handler` to `autogen_core.events`, and consume the `run_stream()` messages.

### AG2 (ag2ai/ag2, new `ag2/` package, v1.1.2)
- OTel is opt-in through `TelemetryMiddleware(tracer_provider, capture_content=True, max_tool_result_chars, agent_name, provider_name, model_name, span_attributes)` (`ag2/middleware/builtin/telemetry.py`).
- Spans: `invoke_agent {agent}`, `chat {model}`, `execute_tool {name}`, `await_human_input {agent}`, `record_usage {kind}`.
- Attributes: `gen_ai.agent.name, operation.name, provider.name, request.model, response.model, response.finish_reasons, input.messages, output.messages, tool.{name,type,call.id,call.arguments,call.result}, usage.{input_tokens,output_tokens,cache_read_input_tokens,cache_creation_input_tokens,thinking_tokens}`.
  - Note the **non-standard** usage keys `cache_read_input_tokens` and `thinking_tokens`.
- AG2-specific keys (`ag2/_telemetry_consts.py`): `ag2.span.type ∈ {agent,llm,tool,human_input,usage,envelope,channel,task,agent_lifetime,agent_event}`, `ag2.usage.kind ∈ {"model_call","subtask","compaction","aggregation"}`, `ag2.usage.total_tokens`, `ag2.network.*`, `ag2.agent.*`, `ag2.error.*`, and the instrumenting module `opentelemetry.instrumentation.ag2`.
- Middleware hooks (`ag2/middleware/base.py`): `on_turn`, `on_tool_execution`, `on_llm_call`, `on_human_input`.
- Built-in middleware: `history_limiter`, `token_limiter`, `llm_retry`, `metrics`, `logging`.
- Also `ag2/compact.py`, `ag2/hitl.py`, `ag2/network/client/checkpoint.py` **[not read in detail]**.
- **Insertion point:** a custom middleware (or `TelemetryMiddleware` with your TracerProvider).

---

## 10. Vercel AI SDK (v7)

### (a) Native telemetry
In v7 the core emits typed lifecycle events. OTel lives in the separate package `@ai-sdk/otel`, which provides two `Telemetry` implementations:
- **`OpenTelemetry`** (`packages/otel/src/open-telemetry.ts`, semconv):
  - Root span `"{op} {modelId}"`, where `mapOperationName` maps `ai.generateText`/`ai.streamText`/`ai.generateObject`/`ai.streamObject` to `invoke_agent`, `ai.embed*` to `embeddings`, and `ai.rerank` to `rerank`.
  - Step span `step {n}`. Inference span `chat {modelId}`. Tool span `execute_tool {toolName}`. Also `embeddings {modelId}`, `rerank {modelId}`, `evaluate {modelId}`.
- **`LegacyOpenTelemetry`** (`legacy-open-telemetry.ts`): v4–v6 style names. The root span is the operationId (`ai.generateText`, `ai.streamText`, ...), steps are `ai.generateText.doGenerate`/`ai.streamText.doStream`/`ai.streamObject.doStream`, and tools are `ai.toolCall`.

Attributes:
- gen_ai: `gen_ai.operation.name, provider.name, system, agent.name (=functionId), request.{model,temperature,top_p,top_k,max_tokens,stop_sequences,frequency_penalty,presence_penalty,seed,stream}, response.{id,model,finish_reasons}, usage.{input_tokens,output_tokens,cache_read.input_tokens,cache_creation.input_tokens}, input.messages, output.messages, system_instructions, tool.{name,type,definitions,call.id,call.arguments,call.result}, output.type`.
- Metrics: `gen_ai.client.operation.{duration,time_to_first_chunk,time_per_output_chunk}`, `gen_ai.execute_tool.duration`.
- Legacy `ai.*`: `ai.operationId, ai.telemetry.functionId, ai.model.{id,provider}, ai.prompt(.messages/.tools/.toolChoice), ai.response.{text,toolCalls,finishReason,id,model,timestamp,msToFirstChunk,msToFinish,avgOutputTokensPerSecond,providerMetadata,reasoning}, ai.usage.{inputTokens,outputTokens,totalTokens,reasoningTokens,cachedInputTokens,inputTokenDetails.*,outputTokenDetails.*}, ai.toolCall.{name,id,args,result}, ai.settings.context.*, ai.stream.{firstChunk,finish}`.
- Node `diagnostics_channel` `"ai:telemetry"` with event types `generateText`, `streamText`, `step`, `languageModelCall`, `executeTool`, `embed`, `embedMany`, `rerank`, `generateSpeech`, `transcribe`, `streamTranscribe`, `experimental_evaluate`.

### (b) Hook surface
**`Telemetry` interface** (`packages/ai/src/telemetry/telemetry.ts`):
- `onStart`, `onStepStart`, `onLanguageModelCallStart`, `onLanguageModelCallEnd`, `onToolExecutionStart`, `onToolExecutionEnd`, `onStepEnd` (`onStepFinish` is deprecated), `onObjectStepStart/End`, `onEmbedStart/End`, `onRerankStart/End`, `onEnd`, `onAbort`, `onError`.
- Wrappers: `executeLanguageModelCall`, `executeTool`.
- Experimental evaluate/transcription callbacks.

Registration:
- Per call: `telemetry: { isEnabled, recordInputs, recordOutputs, functionId, includeRuntimeContext, includeToolsContext, integrations }` (`experimental_telemetry` is an alias).
- Globally: `registerTelemetry(...integrations)`, stored in `globalThis.AI_SDK_TELEMETRY_INTEGRATIONS`.

Event payloads:
- `LanguageModelCallStartEvent{provider, modelId, callId, tools, ...}`.
- `LanguageModelCallEndEvent{callId, finishReason, usage, content, responseId, providerMetadata, performance{responseTimeMs, effectiveOutputTokensPerSecond, outputTokensPerSecond, inputTokensPerSecond, effectiveTotalTokensPerSecond, timeToFirstOutputMs, timeBetweenOutputChunksMs}}`.
- `ToolExecutionStart/EndEvent{callId, messages, toolCall, toolContext, toolExecutionMs, toolOutput}`.

### (c) Concept mapping
- **Steps:** `stopWhen` (default `isStepCount(1)` in generateText; `stepCountIs` remains an alias). Helpers: `isStepCount`, `isLoopFinished`, `hasToolCall` (`generate-text/stop-condition.ts`).
- **`maxSteps`:** removed.
- **`ToolLoopAgent`** (`agent/tool-loop-agent.ts`): default `stopWhen: isStepCount(20)`.
- **Finish reasons:** `stop|length|content-filter|tool-calls|error|other`, plus `raw`.
- **Approval:** tool `needsApproval` (`provider-utils/src/types/tool.ts`) produces `tool-approval-request`/`tool-approval-response` content parts (`prompt/content-part.ts`); see `collect-tool-approvals.ts` and `resolve-tool-approval.ts`.
- **Context management:** `prepareStep` (which can rewrite messages per step) and `pruneMessages(...)` (`generate-text/prune-messages.ts`). No event is emitted for either.
- **MCP:** `@ai-sdk/mcp` tools are ordinary tools, with no MCP marker in the span.
- **No** memory, checkpoint, or subagent primitives in core. A subagent is a tool that calls another agent.
- **Errors/retries:** `maxRetries` **[from memory]**; `onError`, `onAbort`.

### (d) Privacy
`recordInputs` and `recordOutputs` (default true); `includeRuntimeContext` and `includeToolsContext` allow-lists.

### (e) Insertion point
Implement `Telemetry` and register it globally with `registerTelemetry()`. Add `@ai-sdk/otel` `OpenTelemetry` if you also want semconv spans.

---

## Coverage matrix

Legend:
- **N**: native telemetry span or attribute.
- **C**: callback, hook, event bus, or typed stream event.
- **K**: only through checkpoint/state/result inspection.
- **P**: partial or indirect.
- **X**: not observable, or the concept does not exist.

Column notes: LG = LangGraph plus LangChain v1 middleware and Deep Agents. OAI = OpenAI Agents SDK. PAI = PydanticAI. OH = OpenHands. AG = AutoGen / AG2, where those two differ.

| Concept | LG | OAI | ADK | PAI | Claude SDK | OH | CrewAI | Mastra | AutoGen / AG2 | Vercel AI |
|---|---|---|---|---|---|---|---|---|---|---|
| Agent run start/end | C (root chain cb) | N (trace/task) + C | N + C | N + C | C (ResultMessage, hooks) | N + C (status) | C + N | N + C | N (`invoke_agent`) / N | N + C |
| Iteration/step/turn | C (`langgraph_step`) + K | N (`turn`, opt-in) | P (LLM call count) | C (node hooks) | P | C (`agent.step` span) | P (`plan_step_*`) | N (`model_step`) | P / P (`on_turn`) | N (`step`) + C |
| Model call: model/tokens/finish | C (finish reason not normalized) | N (finish reason only raw) | N + C | N + C | C | C (Metrics; tokens yes, finish reason P) | C + N | N | P (log events, no finish reason) / N | N + C |
| Tool request/result/error | C + N via tracer | N + C | N + C | N + C | C (Pre/PostToolUse, PostToolUseFailure) | C (Action/Observation/AgentError) | C + N | N + C | N + C / N | N + C |
| MCP tool call (distinct) | X (plain tool) | N (`mcp_data`, `mcp_tools`) | N (`gcp.mcp.server.destination.id`) | P (generic tool) | C (tool name prefix **[from memory]**) | N (`MCPToolExecutor.call_tool`) | C + N | N (`mcp_tool_call`) | P (MCP workbench span) / X | X |
| Permission/approval/HITL | C (`on_interrupt`) + K | C (`interruptions`) + K (RunState) | C (event actions) | C (`DeferredToolRequests`, deferral attrs) | C (`PermissionRequest`, can_use_tool) | C (status, `UserRejectObservation`) | C (`human_feedback_*`) | C (stream chunks) | C (`UserInputRequestedEvent`) / N (`await_human_input`) | C (approval parts) |
| Subagent/handoff/delegation | P (ns, `task` tool) | N (`handoff`) + C | C (`transfer_to_agent`) | P (nested spans) | C (SubagentStart/Stop, Task*Message) | P (delegate tool) | C (delegation tools, A2A) | C (network chunks) | C (`HandoffMessage`) / N (network spans) | X |
| Context mgmt (trim/summarize/compact) | K (state diff; DA `_summarization_event`) | C (`CompactionItem`) | N + C (`compact_events`, `EventActions.compaction`) | X (silent processor) | C (`PreCompact`) | C (`Condensation`) | X **[UNVERIFIED]** | P (processor spans) | X / P (`usage.kind=compaction`) | X |
| Memory read/write | X (store not evented) | X (wrap Session) | X (wrap service) | X | X | X | C + N | N (`memory_operation`) | C (`MemoryQueryEvent`) / ? | X |
| Retrieval | C (`on_retriever_*`) | P (hosted tool) | P (memory/RAG tools) | X | X | X | C (knowledge_*) | N (`rag_*`) | P / ? | X (rerank/embed only) |
| State/checkpoint (list/restore/fork) | K (full API) | K (RunState JSON) | K (session events, rewind) | K (message JSON, durable exec) | K (session/transcript files) | K (EventLog, fork) | C + K (checkpoint events, fork) | K (`WorkflowRunState`) | K (save/load_state) / ? | X |
| Stop/termination reason | P (exceptions/status) | C (exceptions, error handlers) | P (finish_reason, escalate) | P (exceptions, `End`) | C (ResultMessage subtype **[from memory]**) | C (status + `ConversationErrorEvent.code`) | P | C (`WorkflowRunStatus`, finish chunk) | C (`TaskResult.stop_reason`) / ? | C (finishReason, onAbort) |
| Budget/limits | P (exceptions only) | C (`MaxTurnsExceeded`) | P (exception) | C (`UsageLimitExceeded`) | C (max_turns result **[from memory]**) | C (`MaxIterationsReached`/`MaxBudgetReached`) | X (`max_iter` silent **[UNVERIFIED]**) | P (`maxSteps` attr) | C (termination) / ? | P (stopWhen, no event) |
| Guardrails | P (middleware) | N (`guardrail` span) + C | P (callbacks) | P (output validate hooks) | P (hooks) | C (security_risk, blocked) | C + N | C (tripwire) | X / ? | X |
| Errors/retries | C (`on_*_error`, `on_retry`) | N (span error) | N (`error.type`) + C | N + C | C | C (AgentErrorEvent with classification) | C | N (`errorInfo`) | N (`error.type`) / N | C (onError) |

Loop/stuck detection is native **only in OpenHands**. LangGraph and ADK use count limits, not pattern detection.

---

## Framework-specific features that will not normalize cleanly

1. **LangGraph supersteps vs. turns.** A step is a Pregel superstep that can run many nodes in parallel; it is not an LLM turn. State changes are channel writes with reducers. Summarization is a `RemoveMessage(REMOVE_ALL_MESSAGES)` write, so you can only see it by diffing state. `checkpoint_ns` nesting (`|`, `:`) and `metadata.parents` form a namespace tree that does not match span parent/child. Interrupts are exceptions (`GraphBubbleUp`) that end the run, and resume is a new run on the same thread.
2. **Two delegation models in OpenAI Agents.** Handoffs transfer control (the conversation continues as a different agent, with `HandoffSpanData` only carrying `from_agent`/`to_agent`). Agents-as-tools nest instead. Task and turn spans are exported as `type:"custom"` with `sdk_span_type`, so anything keyed on `span_data.type` sees "custom". Sensitive-data toggling removes fields rather than redacting them.
3. **Dual model-span types in OpenAI Agents.** `GenerationSpanData` (Chat Completions, carries model/usage/input/output) and `ResponseSpanData` (Responses API, carries only response_id/usage, and the model is inside the raw response).
4. **ADK schema flip.** v1 (`invocation`, `call_llm`, `gcp.vertex.agent.*` JSON blobs) vs v2 (`invoke_workflow`, `invoke_node`). Spans are also created by `opentelemetry-instrumentation-google-genai` when it is installed, which overrides per-request settings. `EventActions` mixes control flow (`transfer_to_agent`, `escalate`, `route`, `rewind_before_invocation_id`) into data events. State keys carry scope semantics through the `app:`/`user:`/`temp:` prefixes.
5. **PydanticAI version knob.** Span names and attribute keys depend on `InstrumentationSettings.version` (2 vs 3+). Agent spans use the custom `gen_ai.aggregated_usage.*` to avoid double counting. Deferred tools end the run with an output value (`DeferredToolRequests`), not an interrupt event. From v5 on, deferral spans are UNSET rather than ERROR.
6. **OpenHands STUCK status.** It is a status, not an event. The nudge is injected as a synthetic user-role `MessageEvent(source="environment")`, which will look like user input unless the normalizer filters on `source`. Implicit approval works by calling `run()` again. Condensation removes events by id (`forgotten_event_ids`) rather than by range.
7. **CrewAI's two telemetry stacks.** Product telemetry (title-case span names) and event-driven OTel (lowercase names). Delegation is detectable only by tool name (`Delegate work to coworker`). Agent/task/crew are a three-level hierarchy that does not map to agent/turn. Flows add method-level `@start`/`@listen` semantics and their own pause/human-feedback events.
8. **Mastra splits model spans three ways.** `model_generation` vs `model_inference` vs `model_step`, and which one maps to `chat` depends on a feature flag (`isModelInferenceEnabled`). `client_tool_call` and `provider_tool_call` spans are reconstructed or back-dated. HITL and agent-network exist only as stream chunks. Workflow snapshot statuses (`bailed`, `tripwire`, `waiting`) have no common equivalent.
9. **AutoGen core traces messaging, not GenAI turns.** Runtime spans are `autogen send/publish/process` with messaging semconv. LLM tokens come only from the `LLMCallEvent` log records, without finish reason or model span. AG2 uses non-standard keys (`gen_ai.usage.cache_read_input_tokens`, `thinking_tokens`) and network/hub span types (`envelope`, `channel`, `agent_lifetime`).
10. **Vercel AI: two OTel name schemes.** Legacy `ai.*` vs semconv. `functionId` is mapped to `gen_ai.agent.name`. Approval is a message content part (`tool-approval-request`), not a lifecycle event. There is no persistent state, memory, or subagent concept.
11. **Claude Agent SDK.** Hook events (`PreCompact`, `PermissionRequest`, `SubagentStart/Stop`) are shell- and CLI-shaped. The SDK is a subprocess transport, so all timing is observed from outside.
12. **Context compaction is visible in very different ways:**
    - as an event: ADK `EventActions.compaction`, OpenHands `Condensation`, OpenAI `CompactionItem`, Deep Agents `_summarization_event`;
    - as a hook only: Claude `PreCompact`;
    - not at all: PydanticAI `ProcessHistory`, Vercel `prepareStep`/`pruneMessages`, LangChain `trim_messages`.

    A common model will need a "context_mutation" event that is inferred by diffing message lists for the frameworks that do not emit one.

## Items left unverified
- PydanticAI v1 format history.
- CrewAI `respect_context_window` summarization events and `max_iter` exhaustion events.
- Whether CrewAI `TraceSession` is a supported OSS entry point.
- Exact Laminar attribute names in OpenHands.
- Whether the OpenHands STUCK status emits a `ConversationStateUpdateEvent`.
- Internals of the OpenHands delegate/task tools.
- Exact attributes in ADK's MCP HTTP exchange tracing.
- Mastra `run.resume` signature.
- AutoGen `save_state`/`load_state`.
- The Vercel `maxRetries` default.
- Claude SDK `ResultMessage` subtype values.
- AG2 compaction, HITL and checkpoint internals.
- LangChain `usage_metadata`/`response_metadata` key names (from memory).
