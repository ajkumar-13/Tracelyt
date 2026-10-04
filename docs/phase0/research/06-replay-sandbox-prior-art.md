# Prior art for the replay and regression layer (as of 2026-10-04)

## How this was researched, and what the tags mean

- **Primary source.** For most items I cloned the repository or downloaded the published PyPI wheel and read the code itself (the scratchpad holds about 40 clones). A tag like **[code]** or **[docs-repo]** means I read it there.
- **Mirrors blocked.** Every arXiv mirror I tried was blocked: arxiv.org, alphaxiv, huggingface.co, hyper.ai, semanticscholar and openalex. Most vendor sites were blocked too: e2b.dev, modal.com, docs.temporal.io, docs.langchain.com, docs.docker.com, criu.org and cursor.com.
- **Papers.** Paper text comes from verbatim abstract copies in GitHub mirror repos found with GitHub code search, plus the authors' own code repos where they exist. These are tagged **[abstract via mirror]** or **[author repo]**.
- **Search budget.** The WebSearch quota ran out early in this session. Two E2B numbers came from a search-result snippet of e2b.dev and are tagged **[search snippet]**.
- **Unverified.** Anything tagged **[UNVERIFIED]** comes from memory or from a source I could not fetch. Treat it as a lead, not a fact.

### Corrections to the October research archive (`docs/archive/research/03-standards-and-instrumentation.md` §C9)

1. **deepeval `record_cassette` does not exist** in `confident-ai/deepeval` at HEAD (2026-10-03). A grep of the whole repo, source, tests and docs, finds no "cassette", "vcr" or record/replay API. The only mention is an AI-generated tutorial page (theneuralbase.com). **Drop it from the prior-art list.**
2. **"agent-vcr" is two different projects.** `github.com/authoritydmc/agent-vcr` (v0.1.0) records Python tool, LLM and function calls. The PyPI package named `agent-vcr` is a different project, `github.com/jarvis2021/agent-vcr`, which records and replays MCP JSON-RPC traffic.
3. **AgentOps time travel is gone from the current SDK.** It existed in SDK 0.3.x. SDK 0.4.21 has no `time_travel` module; only the legacy `/v2/ttd/{id}` server route and dashboard UI remain.
4. **LangGraph "replay" is not deterministic.** The docs say it re-executes nodes after the checkpoint.
5. **OpenHands SDK `fork()` copies events but shares the same workspace.** The filesystem is not forked.
6. **Claude Agent SDK `fork_session()` does not copy file-history snapshots.** This is stated in the docstring.
7. **E2B now has native multi-fork** (`POST /sandboxes/{id}/fork`, 1 to 20 forks with full memory). **Daytona fork is a copy-on-write filesystem clone only**, and Daytona's open-source repo has been unmaintained since June 2026.

---

## 1. Record and replay libraries for LLMs and agents

### 1.1 pytest-llm-vcr (PyPI `pytest-llm-vcr` 0.6.0)

Repo: https://github.com/yashshah9/llm-vcr (HEAD 2026-09-19). PyPI: https://pypi.org/project/pytest-llm-vcr/. **[code]**

**Interception point.** An httpx transport (`VCRTransport`, sync and async, including `client.stream`). The API is the `@llm_vcr("name", matcher=..., sequential=...)` decorator, the `llm_vcr_client` fixture, `--llm-vcr-record`, `LLM_VCR_RECORD=true` and `LLM_VCR_CASSETTE_DIR` (default `tests/cassettes`). There is also an `llm-vcr diff` CLI.

**Cassette format** (YAML, `src/llm_vcr/cassette.py`):
```yaml
name: streaming_hello
interactions:
  - method: POST
    url: https://api.openai.com/v1/chat/completions
    request_headers: {...}
    request_body: {model:..., stream: true, messages: [...]}
    status_code: 200
    response_headers: {content-type: text/event-stream}
    response_body: null|{...}
    streaming: true
    chunks: ["data: {...}\n\n", "data: [DONE]\n\n"]
```

**Matching** (`src/llm_vcr/matching.py`, `cassette.py`, `transport.py`):
- **`exact` (default).** `request_key` is the first 16 hex characters of `sha256(json.dumps({method, url: normalize_url, body: normalize_body}, sort_keys=True))`.
  - `normalize_body` drops `DROP_KEYS = {"user","request_id","timestamp","created","seed","n"}`.
  - It collapses dated model ids: `-YYYY-MM-DD` and Anthropic's `-YYYYMMDD` are removed, and `MODEL_ALIASES` maps `chatgpt-4o-latest` to `gpt-4o`.
  - For `api.anthropic.com` the query string is stripped.
- **`semantic`.** Same as exact, plus: messages reduced to `role` + `content` + `name` + `tool_calls[].function.{name,arguments}` (tool-call ids dropped); tools reduced to `{type, function.{name,description,parameters}}` and **sorted by name**; Anthropic `metadata` and `tool_use`/`tool_result` ids ignored.
- **Ordering.** Default is first unused match (`_used` set). With `sequential=True` it keeps a cursor and raises `Out-of-order cassette request at step {i}` on mismatch.

**Streaming.** SSE stored as a list of raw event chunks and replayed in order. The authors list as a limitation: "Record mode for streaming stores chunks, not per-event timestamps."

**Stated limitations.** httpx only. "Sequential matching is opt-in; default matching is still hash-based."

### 1.2 agent-vcr (authoritydmc), v0.1.0

Repo: https://github.com/authoritydmc/agent-vcr (HEAD 2026-10-01). **[code]**

**Interception point.** Function-level, not HTTP. `@record_tool(name=..., call_type="tool")`, `use_cassette(path, record_mode, sensitive_keys, matchers, sequential=True)`, and the pytest fixture `agent_cassette` / `@pytest.mark.agent_vcr`. Record modes: `once`, `all`, `none`, `new_episodes`.

**Format** (YAML, `models.py`). Each interaction is `{request: {call_type: "tool|llm|function|http", name, payload, metadata}, response: {output, error, status: "success|error", duration_ms}, recorded_at}`.

**Matching** (`matchers.py`). `DEFAULT_MATCHERS = [match_call_type, match_name, match_payload]`, where payload equality is `json.dumps(sort_keys=True)`. With `sequential=True`, played indices are skipped; this is first-unplayed-match, not a strict cursor.

**Errors and limits.** A recorded error is replayed by raising `AgentVCRError(error)`, so the original exception type is lost. No streaming support and no branching.

### 1.3 PyPI `agent-vcr` = jarvis2021/agent-vcr (MCP record and replay)

Repo: https://github.com/jarvis2021/agent-vcr (HEAD 2026-02-09). **[code]**

**Format** (`.vcr` JSON). `format_version`, then `metadata{recorded_at, transport (stdio|sse), client_info, server_info, server_command, server_args, tags}`, then `session{initialize_request, initialize_response, capabilities, interactions[]}`. Each interaction is `{sequence, timestamp, direction, request (full JSON-RPC), response, notifications[], latency_ms}`.

**Matching** (README "Match Strategies"):

| Strategy | What it matches |
|---|---|
| `exact` | Full JSON, excluding `jsonrpc` and `id` |
| `method` | Method name only |
| `method_and_params` (default) | Method plus full params |
| `subset` | Method plus partial params (`fuzzy` is a deprecated alias) |
| `sequential` | Returns interactions in order |

**Other features.** Latency simulation (`--simulate-latency`, `--latency-multiplier`). Recordings are cross-language between Python and TypeScript.

**Why it matters.** This is the only prior art I found for recording the MCP session handshake and notifications. Those are exactly the fields our MCP step record needs (§8).

### 1.4 langchain-replay (sixty-north), 0.1.3

Repo: https://github.com/sixty-north/langchain-replay. **[code]**

**Design.** It records the LLM's *decisions*, not HTTP traffic. On replay it yields the recorded decisions **while really executing the tools**.
- Patching is done by swapping agent factories (`AgentFactoryRegistry.register("langchain.agents.create_agent")`) and optional chat-model methods (`[(ChatAnthropic, "ainvoke")]`).

**Format.** `recording.jsonl` with `RecordedTurn{phase, user_message, events[RecordedEvent{event_type,name,data}], response}` and `RecordedAskCall{prompt, response}`.

**Matching.** Purely sequential (`_turn_index`, `_index`). The prompt is **not** checked. `ReplayExhaustedError` is raised on overrun. Tools are re-executed from the recorded `on_tool_start` inputs.

**Stated limitations** (README, "Tests must be deterministic"): "records the LLM's *decisions*, not the universe those decisions were made in… recorded tool inputs are dispatched verbatim." Timestamps, `uuid4` and `tmp_path` values get baked into the recording.

### 1.5 vcrpy and pytest-recording applied to the OpenAI and Anthropic SDKs

**vcrpy** (https://github.com/kevin1024/vcrpy, HEAD 2026-07-04) **[code]**
- **Default matching.** `match_on=("method","scheme","host","port","path","query")` (`vcr/config.py`). **The body is not matched by default.** Every `POST /v1/messages` therefore matches the first unplayed interaction in file order, which is effectively sequential.
- **Other matchers.** `body` and `raw_body` exist. `allow_playback_repeats` defaults to False. `drop_unused_requests` defaults to False.
- **Record modes** (`vcr/record_mode.py`): `all`, `any`, `new_episodes`, `none`, `once`.
- **Streaming.** The httpx stub reads the whole stream (`b"".join(real_response.stream)`) and replays it as a single `httpx.ByteStream`. SSE event boundaries survive in the bytes, but timing and incremental delivery do not.
- **SDK coverage.** Both the OpenAI and Anthropic Python SDKs use httpx, so vcrpy works with them. Async needs vcrpy's httpx async stub.

**pytest-recording** (https://github.com/kiwicom/pytest-recording) **[code]**
- `@pytest.mark.vcr`, `--record-mode` (**default `"none"`**), `--block-network`, `--allowed-hosts`, `--disable-recording`.
- A `vcr_config` fixture shares configuration; there is one cassette directory per test module.

**LangSmith's use of vcrpy** (https://github.com/langchain-ai/langsmith-sdk, `python/langsmith/utils.py::with_cache`) **[code]**
- Turned on by setting `LANGSMITH_TEST_CACHE=path` (needs `langsmith[vcr]`).
- Configuration: `vcr.VCR(record_mode="new_episodes", match_on=["uri","method","path","body"], filter_headers=["authorization","Set-Cookie"])`, with the LangSmith API host ignored.
- One `{test_suite_id}.yaml` cassette per suite.
- This is LangSmith's only SDK "replay" mechanism.

### 1.6 deepeval `record_cassette`

**Not found** in https://github.com/confident-ai/deepeval at HEAD (2026-10-03). **[code, negative result]** Treat it as nonexistent.

### 1.7 Braintrust, LangSmith and Laminar "replay"

**Laminar** (https://github.com/lmnr-ai/lmnr-python, HEAD 2026-09-21) has a **real replay feature: debugger "rollouts"**. **[code]**
- **Configuration.** Environment variables `LMNR_DEBUG`, `LMNR_DEBUG_REPLAY_TRACE_ID`, `LMNR_DEBUG_CACHE_UNTIL` (a span-id needle) and `LMNR_DEBUG_SESSION_ID`.
- **Where it hooks in.** Per-provider wrappers (`instrumentation/{openai,anthropic,litellm,google_genai}/rollout.py`) call `rollout_sessions.cache(session_id, replay_trace_id, cache_until, input_hash)` before each live LLM call.
- **Outcome** (`sdk/debug/outcome.py`):
  - `hit`: serve the cached span.
  - `miss`: run live and latch a process-wide flag so every later call also runs live.
  - `live`: a transport or warm-up failure; run this one call live without latching.
- **Hash** (`sdk/debug/hash.py`): `hex(blake3(canonical_json(messages_without_system)))`. Canonical JSON sorts keys recursively and preserves array order. The number canonicalization `1.0` versus `1` is deliberately deferred.
- **The system message is excluded on purpose.** You can therefore edit the system prompt and still reuse cached downstream calls until the conversation itself diverges. This is a clear example of the match key defining which edits count as counterfactual.
- **Response reconstruction.** Cached spans are of type `"raw"` (full provider response) or `"genAi"` (normalized). Replayed responses have usage zeroed. Streaming is reconstructed by synthesizing provider stream events (e.g. Anthropic `RawContentBlockDeltaEvent`).

**LangSmith.** Only the `LANGSMITH_TEST_CACHE` vcrpy cache (§1.5) at the SDK level. Playground re-runs exist in the UI. **[UNVERIFIED: no fork-at-step API found]**

**Braintrust.** Playground "rerun a trace with modified prompt/model" exists per Braintrust marketing pages. **[UNVERIFIED: I found no SDK replay or cassette API]**

### 1.8 AgentOps time travel (how it worked)

Code: https://github.com/AgentOps-AI/agentops/blob/0.3.26/agentops/time_travel.py **[code]**

**Flow.**
1. The dashboard "Branch" modal (`app/dashboard/components/time-travel/BranchModal.tsx`) POSTs `/timetravel {name, projectId, sessionId}`, creating a "TTD".
2. The SDK's `fetch_time_travel_id(ttd_id)` GETs `{endpoint}/v2/ttd/{ttd_id}`.
3. It writes `agentops_time_travel.json` as `{"completion_overrides": {str({"messages": prompt.messages}): returns}}`.
4. It sets `Time_Travel_Debugging_Active: true` in `.agentops_time_travel.yaml`.

**Matching** (`find_cache_hit`). The code `eval()`s each key and returns a hit when the message list lengths are equal and **every message `content` is equal; role is ignored**. It matches by content, independent of order position. The user edits a cached completion in the UI, and the edited completion is injected the next time the agent sends an identical prompt prefix.

**Limitations visible in the code:**
- chat-message format only;
- no tool replay;
- no streaming;
- uses `eval` on keys;
- singleton global state.

**Status.** Removed from the 0.4.x SDK (0.4.21 has no `time_travel`). The server still has `@router.get("/ttd/{ttd_id}")` in `app/api/agentops/api/routes/v2.py`.

### 1.9 agent-replay (clay-good)

Repo: https://github.com/clay-good/agent-replay (TypeScript CLI, SQLite, HEAD 2026-09-06). **[code/README]**

**Trace format.** `{agent_name (required), agent_version, trigger, status, input, output, started_at, ended_at, total_*, error, tags, session_id, steps[]}`.
- Each step: `{step_number, step_type ∈ thought|tool_call|llm_call|retrieval|output|decision|error|guard_check, name, input, output, duration_ms, tokens_used, parent_step, caused_by_step, decision{options[{option,rationale,score}], chosen, rationale, confidence, decided_by: agent|user|policy}}`.
- Ingest paths: native JSON/JSONL, a hook adapter (Claude Code, Codex, Gemini CLI), stream translators, an OTLP receiver, and importers for Claude transcripts and Codex rollouts.

**Fork.** "A fork is a **branch point, not a simulation**: it copies steps 1..N… links it back (`parent_trace_id`, `forked_from_step`)… Nothing is re-executed — this tool never runs your agent for you."

**Regression gate** (`check --golden`). Structural comparison.
- Default fields: `step_count, step_types, step_names, tool_inputs, step_errors, status`. Opt-in fields: `model, decisions`.
- **Tool inputs are compared verbatim**, so a rephrased query counts as a regression.
- Runs are matched to golden entries by **agent name + hash of the input**. Empty inputs are never matched.
- Any matching golden entry passes. Fail-closed exit `2` when there is nothing to compare.

This is the most careful prior art on *trajectory-level* CI gating semantics.

### 1.10 agent-timetravel (akshay-mp)

Repo: https://github.com/akshay-mp/agent-timetravel (HEAD 2026-09-01). **[code]**

**Capture** is passive, via an OTLP receiver writing to SQLite. **Replay** is active, via interceptors that patch the OpenAI SDK, LangChain `BaseChatModel`/`BaseTool` and ADK.

**Modes** (`ReplayMode`):
- `FROZEN`: serve the recording; divergence raises.
- `BRANCH`: recorded up to the cursor, then live.
- `FULL_RERUN`: everything live, which answers "is this run reproducible?"

**Matching** (`replay.py`):
- A cursor over recorded spans. A hit requires `messages_hash` equality, plus `tools_hash` when both sides carry one.
- `hash_payload` is SHA-256 over stable JSON.
- **The model name is deliberately not matched**, so branches can swap models.
- Tools match by **name + args_hash, out of order** (`tool_intercept._find_tool_span`), and the cursor jumps.
- Frozen divergence raises `ReplayError("frozen replay divergence at cursor=…")`.

**Streaming.** "frozen streaming replay not yet supported… use non-streaming calls or mode=branch". Capture silently upgrades calls to `stream=True` in order to collect reasoning.

**State.** `checkpoint(name, payload)` lets user code skip side effects when a recorded snapshot is restored. `rollback/git.py` is a git-backed rollback: anchor `HEAD` plus `git stash`; restore runs `reset --hard <anchor>`, then `clean -fd`, then `stash pop`. The authors explicitly reject `git worktree` because it is "heavyweight and conflict[s] with agents that assume a single CWD".

**Manifest.** `reproducibility.py` records Python version, platform, packages and a `content_hash`.

### 1.11 OpenHands: EventStore, ReplayManager and the V1 SDK fork

**Legacy V0** (https://github.com/OpenHands/OpenHands/blob/1.0.0/openhands/controller/replay.py) **[code]**
- `ReplayManager` replays only **Actions** and drops `EventSource.ENVIRONMENT` events and `NullObservation`. Observations are regenerated by re-executing against the runtime.
- `wait_for_response` is overridden to False except for the last message.
- The docstring's stated limitation: "unexpected or even errorneous results could happen if 1) any action is non-deterministic, OR 2) if the initial state before the replay session is different from the initial state of the trajectory."
- Configuration: `replay_trajectory_path`.
- `EventStore` persists one JSON file per event under the conversation directory. Events carry `_id`, `_timestamp`, `_source`, `_cause`.

**V1 SDK** (https://github.com/OpenHands/software-agent-sdk, HEAD 2026-10-03) **[code]**
- `conversation.fork(conversation_id=None, agent=None, title=None, tags=None, reset_metrics=True, from_event_id=None)` deep-copies events (`path_to_root(from_event_id)`), `agent_state`, and activated skills/rules.
- `navigate_to(event_id)` re-roots HEAD in place. All branches stay on disk; the event store is a tree.
- **The fork reuses `workspace=self.workspace`, so the filesystem is not forked.**

### 1.12 LangGraph time travel

Docs: https://github.com/langchain-ai/docs/blob/main/src/oss/langgraph/use-time-travel.mdx. Code: `libs/checkpoint/langgraph/checkpoint/base/__init__.py`. **[docs-repo, code]**

**APIs.**
- `graph.get_state_history(config)` returns `StateSnapshot{values, next, config, metadata, created_at, parent_config, tasks, interrupts}` in reverse chronological order.
- Replay: `graph.invoke(None, snapshot.config)`, where the config carries `configurable.checkpoint_id`.
- Fork: `graph.update_state(config, values, as_node=...)`, then `invoke(None, fork_config)`.

**Checkpoint format.** `Checkpoint{v, id (unique, monotonically increasing), ts, channel_values, channel_versions, versions_seen, updated_channels}`.
- Metadata: `CheckpointMetadata{source: "input"|"loop"|"update"|"fork", step, parents, run_id}`.
- `pending_writes` / `put_writes` store successful node writes from a failed step.

**Semantics, quoted from the docs:**
- "Nodes before the checkpoint are not re-executed… Nodes after the checkpoint re-execute, including any LLM calls, API requests, and interrupts (which may produce different results)."
- "Replay re-executes nodes—it doesn't just read from cache."
- "`update_state` does **not** roll back a thread. It creates a new checkpoint that branches."
- Interrupts "are always re-triggered".
- Subgraphs without their own checkpointer form a single super-step: "You cannot time travel to a point between step_a and step_b."

**Takeaway.** LangGraph forks at the graph-state level, but nothing is replayed from a cache. It provides fork points, not deterministic replay.

---

## 2. Durable-execution journaling

### 2.1 Temporal

**Event history format** (exported JSON, e.g. `temporalio/ai-integrations/python/openai_agents/tests/histories/hello-workflow-history.json`) **[code]**. `events[]` with `{eventId, eventTime, eventType, taskId, <type>EventAttributes}`. A model call appears as:
- `EVENT_TYPE_ACTIVITY_TASK_SCHEDULED{activityId, activityType.name:"invoke_model_activity", taskQueue, input(payloads), scheduleToClose/StartToClose timeouts, retryPolicy, workflowTaskCompletedEventId}`
- then `…STARTED`
- then `…COMPLETED{result.payloads[{metadata.encoding:"json/plain", data:base64}], scheduledEventId, startedEventId, identity}`.

**Determinism constraints** (https://github.com/temporalio/documentation, `docs/encyclopedia/workflow/workflow-definition.mdx`) **[docs-repo]**:
- "When the Workflow's code replays, the Commands that are emitted are compared with the existing Event History… that Command is compared with the Event that is in the same location within the sequence. The Event in the sequence must be an ActivityTaskScheduled Event, where the Activity name is the same."
- Changes that are explicitly **not** non-determinism: changing timer durations (except to or from 0), and changing arguments to Activity Options.
- **So matching is positional + command-type + activity name. The activity input is not compared.**

**Limits** (`workflow-execution/limits.mdx`): history is capped at **51,200 events or 50 MB**, with a warning at 10,240 events or 10 MB.

**Reset, the fork primitive** (`event.mdx`): "A Reset terminates a Workflow Execution and creates a new Workflow Execution… The Event History is copied from the original execution up to and including the reset point." Valid reset points are `WorkflowTaskStarted|Completed|TimedOut|Failed`.

**Replay testing** (Python): `from temporalio.worker import Replayer`, then `await Replayer(workflows=[...], plugins=[OpenAIAgentsPlugin()]).replay_workflow(WorkflowHistory.from_json(id, json))`. `replay_workflows(histories, fail_fast=...)` replays many. Java names it `WorkflowReplayer`, Go uses `worker.NewWorkflowReplayer`. **[UNVERIFIED: the Java and Go names are from memory]**

**OpenAI Agents integration.** It moved out of `temporalio.contrib.openai_agents` into the standalone package `temporalio-openai-agents` (`from temporalio.openai_agents import OpenAIAgentsPlugin`). Repo: https://github.com/temporalio/ai-integrations/tree/main/python/openai_agents (HEAD 2026-10-02). **[code]**

- **Model calls are always activities**: `invoke_model_activity(input: ActivityModelInput) -> ModelResponse`.
  - `ActivityModelInput = {model_name, system_instructions, input (required), model_settings (required), tools, output_schema, handoffs, tracing (required), previous_response_id, conversation_id, prompt}`.
  - The journaled record is that full input plus the serialized `ModelResponse`.
  - The default OpenAI client uses `max_retries=0`, so Temporal owns retries.
  - `ModelActivityParameters` fields: `task_queue`, timeouts (`start_to_close` default 60s), `retry_policy`, `use_local_activity`, `streaming_topic`, `summary_override`, `priority`.
- **Tools:**
  - `activity_as_tool()` runs as a Temporal activity (journaled).
  - `@function_tool`/`FunctionTool` "execute in the workflow" (must be deterministic).
  - Hosted tools run inside the model call.
- **MCP.** `temporal_mcp_server("name")` with factories registered on the worker; MCP calls become activities.
- **Sandbox (pre-release).** Every `SandboxAgent` operation (exec, read, write, PTY) becomes an activity named like `"daytona-sandbox_session_exec"`. "Sandbox session state is serialized with the workflow."
- **Streaming (experimental).**
  - `invoke_model_activity_streaming` returns the **collected list of events**, so the journal stores the final event list.
  - Live events go to a `WorkflowStream` topic. "A partial attempt that fails mid-response leaves its emitted events on the stream and the retry attempt publishes a second sequence."
  - Streaming is incompatible with `use_local_activity`.

**Production evidence.** Cursor's cloud agents run their agent loop on Temporal: "more than 50 million actions per day across more than 7 million unique workflows". They "moved from 'eternal' agent workflows to multiple shorter ones". Source: https://cursor.com/blog/cloud-agent-lessons (2026-05-21, read via the archived copy at github.com/aintnorest/knowledge-base-intelligent-systems `archive/cursor-cloud-agent-lessons.html`). **[archived copy]**

### 2.2 Restate

**Protocol** (https://github.com/restatedev/service-protocol `service-invocation-protocol.md`, v3) **[docs-repo]**.
- The two sides are in either *Replaying* or *Processing* state. "When in replaying state, the service deployment cannot create new journal entries."
- v3 entry types: `InputEntryMessage 0x0400`, `OutputEntryMessage 0x0401`, `GetState 0x0800`, `SetState`, `ClearState`, `Sleep 0x0C00`, `Call 0x0C01`, `OneWayCall 0x0C02`, `Awakeable 0x0C03`, `RunEntryMessage 0x0C05` ("Run non-deterministic user provided code and persist the result"), `GetPromise`/`PeekPromise`/`CompletePromise`, `CancelInvocation`, `AttachInvocation`, `GetInvocationOutput`.

**Current protocol** (https://github.com/restatedev/sdk-shared-core, HEAD 2026-09-21) **[code]**. It splits the journal into **Commands** and **Notifications**.
- `ctx.run` emits `RunCommandMessage{result_completion_id, name}`.
- The SDK then sends `ProposeRunCompletionMessage{result_completion_id, oneof{value, failure}}`.
- The runtime journals the completion as `RunCompletionNotificationMessage`.

**Journal-mismatch detection** (`src/service_protocol/messages.rs`, `CommandMessageHeaderDiff`; error code `JOURNAL_MISMATCH = 570`):
- `CallCommandMessage` compares `service_name, handler_name, **parameter (bytes)**, key, headers, name, idempotency_key`. **Call arguments are compared byte-exact.**
- `RunCommandMessage` compares only `name` and `result_completion_id`. Closure inputs are not journaled.

**Fork.** CLI `restate invocations restart-as-new <inv>`: "runs from the start: nothing of the original execution is kept" (`cli/src/commands/invocations/restart_as_new.rs`). I found no restart from a journal prefix in the CLI. **[code]**

### 2.3 Inngest and AgentKit

**Step memoization** (https://github.com/inngest/inngest-js `packages/inngest/src/components/execution/engine.ts`) **[code]**
- Step state is keyed by `hashId(id) = sha1(id)` hex. Duplicate step ids are auto-indexed (with a warning about parallel indexing).
- A step counts as memoized when `stepState[hashedId]` exists.
- The function re-enters from the top on each invocation, and completed steps return their memoized results.
- **Matching is by step-ID hash, not by position.** The cost is that changing a step id breaks memoization.

**AgentKit** (https://github.com/inngest/agent-kit `packages/agent-kit/src/model.ts`, `agent.ts`) **[code]**
- When running inside an Inngest function, model inference goes through `step.ai.infer(stepID, {model, body})`, which is journaled.
- MCP tool calls are wrapped in `step.run(name, fn)`.
- A source comment: "TODO: Implement true token-by-token streaming… Currently using completed response chunking for streaming simulation."

### 2.4 DBOS

Repo: https://github.com/dbos-inc/dbos-transact-py (HEAD 2026-10-01). **[code]**

**Checkpoint table** `dbos.operation_outputs` (`dbos/_schemas/system_database.py`): `workflow_uuid, function_id (int, sequence), function_name, output, error, child_workflow_id, started_at_epoch_ms, completed_at_epoch_ms, serialization, application_name, retention_timestamp`, primary key `(workflow_uuid, function_id)`. Workflow inputs are stored in `workflow_input`.

**Replay check.** Positional by `function_id`. If the recorded `function_name` differs, the SDK raises `DBOSUnexpectedStepError` (`_sys_db.py::_check_operation_execution_txn`).

**Fork primitive.** `DBOS.fork_workflow(workflow_id, start_step, *, application_version=None, queue_name=None, queue_partition_key=None, replacement_children=None, timeout_seconds=None) -> WorkflowHandle`. It copies `operation_outputs` rows with `function_id < start_step` into a **new workflow id** and re-executes from `start_step`. The `application_version` parameter lets the fork run new code. **This is the closest production analogue to "reuse history until step k, then run live with new code".**

### 2.5 Trigger.dev

Source: https://github.com/triggerdotdev/trigger.dev `docs/how-it-works.mdx`, `docs/concurrency.mdx`. **[docs-repo]**
- No journal replay. Instead it uses **CRIU process checkpointing** at waitpoints: "the system uses CRIU… to create a checkpoint of the task's entire state, including memory, CPU registers, and open file descriptors."
- `wait.for`/`wait.until` checkpoint only after 60 s of waiting. `triggerAndWait` checkpoints the parent.
- Self-hosted deployments do not support checkpoints (`self-hosting/overview.mdx`: "Checkpoints ✅ / ❌").
- Idempotency is via `idempotencyKey` on triggers.

**Common limitation across §2.** Every engine journals only if the agent is authored inside it. Matching is positional plus name or type (Temporal, DBOS), or keyed by step id (Inngest). Restate alone compares call payload bytes.

---

## 3. Sandbox snapshot and fork APIs

| System | API names (verified) | State captured | Restore and fork | Isolation |
|---|---|---|---|---|
| **E2B** (`e2b` Python SDK, https://github.com/e2b-dev/E2B, HEAD 2026-10-02) **[code]** | `sbx.pause(keep_memory=None)`; `Sandbox.connect(id)` resumes; `sbx.beta_pause()`; `sbx.create_snapshot(name=None) -> SnapshotInfo` (persistent, survives deletion; `Sandbox.create(snapshot_id)`); `list_snapshots`, `delete_snapshot`; **`sbx.fork(timeout=None, count=None) -> List[Sandbox \| Exception]`** = `POST /sandboxes/{sandboxID}/fork`; `lifecycle={on_timeout: "kill"\|"pause" or {action, keep_memory}, auto_resume}` | Filesystem + memory + processes by default. `keep_memory=False` is "filesystem only… resuming such a sandbox cold-boots"; a test asserts a new `boot_id`. | Fork: "checkpointed in place (briefly paused, snapshotted with its full memory state, and resumed — its ID and expiration stay untouched) and `count` new sandboxes are created", count 1 to 20. Pause about **4 s/GiB RAM**, resume about **1 s**; paused sandboxes "kept indefinitely" **[search snippet of e2b.dev/docs/sandbox/persistence]**. Max sandbox lifetime 24 h (Pro) / 1 h (Hobby), per the SDK docstring. | Firecracker microVMs. https://github.com/e2b-dev/infra README: "Firecracker microVMs that resume from a snapshot"; orchestrator default `v1.14.1`. **[code]** Pricing **[UNVERIFIED]**. |
| **Modal** (`modal-client`, `py/modal/sandbox.py`, HEAD 2026-10-03) **[code]** | `sb.snapshot_filesystem(timeout=55, *, ttl=30*24*3600) -> Image`; `sb.snapshot_directory(path, ttl=…) -> Image`; `sb.mount_image(path, image)`; `Sandbox.create(image=…)`; memory: `sb._experimental_snapshot() -> SandboxSnapshot`, `Sandbox._experimental_from_snapshot(snapshot, name=…)`; create flag `_experimental_enable_snapshot` | Filesystem snapshot becomes an Image. The changelog says the default changed from indefinite retention to a 30-day `ttl`; pass `ttl=None` to keep forever. Memory snapshots are experimental (v2 path `snapshot_memory`, 165 s timeout). | A restore creates a **new** sandbox; v1 and v2 snapshots restore only onto the same backend. Latency **[UNVERIFIED]**. | gVisor (`runsc exec` referenced in sandbox.py). Pricing **[UNVERIFIED]**. |
| **Daytona** (PyPI `daytona` 0.220.0; the GitHub repo has been unmaintained since June 2026) **[code]** | `sandbox.fork(name=None)` (old `_experimental_fork` deprecated); `create_snapshot(name)`; `pause()`; `set_auto_pause_interval(min)`; `stop/start/archive`; `set_auto_archive_interval` | Fork: "copy-on-write clone… identical **filesystem**". Snapshot: "captures the Sandbox's filesystem". Pause: "freezing all running processes… retains its state in memory". | Fork is filesystem-only; memory survives only through an in-place pause. Latency **[UNVERIFIED]**. | **[UNVERIFIED]**: docstrings mention "sandbox classes that support pausing". |
| **Firecracker** (https://github.com/firecracker-microvm/firecracker/blob/main/docs/snapshotting/snapshot-support.md) **[docs-repo]** | `PATCH /vm {"state":"Paused"}`; `PUT /snapshot/create {snapshot_type:"Full"\|"Diff", snapshot_path, mem_file_path}`; `PUT /snapshot/load {snapshot_path, mem_backend{backend_path, backend_type:"File"\|"Uffd"}, track_dirty_pages, resume_vm}`; `PATCH /vm {"state":"Resumed"}` | "Guest memory" + "emulated HW state (both KVM and Firecracker emulated HW)". Disk files are "**managed by the users**". | Load maps memory `MAP_PRIVATE` with copy-on-write (fast, lazy). "Network connectivity is not guaranteed to be preserved after resume." Vsock connections are closed. Diff snapshots are still in developer preview. **Uniqueness:** "we consider resuming execution from the same state more than once insecure" (identifiers, RNG seeds, entropy pool, crypto tokens; see `random-for-clones.md`, VMGenID). | KVM microVM. Snapshot files are "trusted"; only a CRC64 check on the state file. |
| **gVisor** (https://github.com/google/gvisor/blob/master/g3doc/user_guide/checkpoint_restore.md, `fs_snapshot.md`, `rootfs_snapshot.md`) **[docs-repo]** | `runsc checkpoint --image-path=<dir> [--leave-running] [--compression=none\|flate-best-speed] [--exclude-committed-zero-pages] [--direct]`; `runsc create` then `runsc restore --image-path [--background] [--direct]`; `runsc wait --restore`; filesystem snapshots via `runsc fscheckpoint` (`--path=all-tmpfs`); rootfs tar snapshots | Whole-sandbox kernel and memory state. Filesystem snapshots capture overlay upper layers (disk-backed tmpfs). | Restore goes into a **new container**. `--background` starts execution before all pages are loaded. With `--network=host`, connected sockets "return `ECONNRESET`"; listeners are re-created. CPU-feature compatibility via the `dev.gvisor.internal.cpufeatures` annotation. GPU support via cuda-checkpoint. | User-space kernel; no KVM needed. |
| **CRIU / Docker** (https://github.com/checkpoint-restore/criu; https://github.com/docker/cli/blob/master/docs/reference/commandline/checkpoint.md) **[docs-repo]** | `docker checkpoint create\|ls\|rm`; `docker start --checkpoint <name> <ctr>` | Process tree, memory, file descriptors (CRIU). The filesystem is the container's own. | Docker: "an experimental feature"; needs CRIU ≥ 2.0; "focused on single-host use cases". Docker cannot restore into a different container (gVisor doc, Moby #37344). TCP is handled via libsoccr. | Container (namespaces). Fragile with external resources; criu.org "What cannot be checkpointed" **[not fetched]**. |
| **Kata Containers** (https://github.com/kata-containers/kata-containers/blob/main/docs/Limitations.md) **[docs-repo]** | none | n/a | "The runtime does not provide `checkpoint` and `restore` commands." | VM-based containers. |

**Suitability for replaying one coding-agent step.**
- **Firecracker or E2B fork** gives the highest fidelity: running dev servers, REPLs and background jobs survive. The costs are memory snapshot time proportional to RAM, the clone-uniqueness hazard, and the need for KVM.
- **gVisor** fits a runner deployed on the customer's own infrastructure: no KVM, a filesystem-only snapshot path, and full checkpoint/restore when processes matter.
- **Daytona fork** and **Modal `snapshot_filesystem`** give R3 (filesystem) only.
- **Docker/CRIU** is experimental and single-host.
- **Kata** has no checkpoint/restore.

---

## 4. Environment reproducibility for coding agents

**SWE-bench harness** (https://github.com/SWE-bench/SWE-bench, HEAD 2026-09-02) **[docs-repo, code]**
- Three image layers (`docs/guides/docker_setup.md`): "**Base image**… **Environment images**: Python environments for different configurations (~60 images)… **Instance images**: Specific dependencies for each evaluation task."
- `--cache_level none|base|env|instance` (default `env`).
- The 2026 harness takes each instance's image name from the dataset (`make_test_spec(d).image`) and can build from a task repo first. In `_build_before_eval`: "Without this a failed build is invisible: the image is pulled instead, so a stale published image can report a clean pass."
- Environments are pinned per repo version and per instance. **[UNVERIFIED: the exact pinning fields, e.g. `environment_setup_commit`, were not re-read in the 2026 code]**

**mini-swe-agent 2.4.6** (PyPI wheel) **[code]**
- `_ENVIRONMENT_MAPPING = {docker, singularity, local, swerex_docker, swerex_modal, bubblewrap, contree}`.
- `DockerEnvironment.execute` runs each command as an independent `docker exec -w cwd [-e…] <ctr> bash -lc <command>` via `subprocess.run`, and returns `{output, returncode, exception_info}`.
- **There is no persistent shell, so every step's effect is on the filesystem only. This makes prefix re-execution a viable reconstruction method** (see The Replay Gap, §5).
- SWE-agent proper uses a persistent SWE-ReX shell session. **[UNVERIFIED this session]**

**OpenHands runtime** (`openhands/runtime/utils/runtime_build.py` @1.0.0) **[code]**
- Runtime images are tagged `oh_v{version}_{lock_hash}` and `{lock_tag}_{source_hash}`, so they are content-addressed on the base image, lock files and source.
- Runtimes: Docker, Remote and Local. **[UNVERIFIED: the class list]**

**Claude Code checkpoints**
- From https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md **[docs-repo]**:
  - checkpoints are per-session "file-history backups";
  - `/rewind`, `/undo`, Esc Esc and `--rewind-files` exist;
  - "`/rewind` no longer restores or deletes files through symlinks or hard links";
  - "bounded checkpoint disk usage by pruning superseded file-history backups".
- Claude Agent SDK **[code]**:
  - `ClaudeAgentOptions.enable_file_checkpointing` "creates backups of files before they are modified";
  - `ClaudeSDKClient.rewind_files(user_message_id)` needs `extra_args={"replay-user-messages": None}`;
  - `fork_session(session_id, directory, up_to_message_id, title)` remaps UUIDs and "Forked sessions start without undo history (file-history snapshots are not copied)".
- Observed locally:
  - `~/.claude/shell-snapshots/snapshot-bash-<ts>-<id>.sh` (shopt settings, functions, aliases) is replayed before each Bash call. **This is part of the environment a replay must reproduce.**
  - Transcript JSONL entry types seen include `user`, `assistant`, `attachment`, `system`, `mode`, `queue-operation`, `last-prompt`, `cost-state`.
- What Claude Code checkpoints cover: only files changed by the edit tools. Bash side effects and external changes are not tracked. **[UNVERIFIED this session; it matches the published checkpointing docs]**
- Internal layout `~/.claude/file-history/<session>/<hash>@v<n>` with a `file-history-snapshot` transcript entry (`trackedFileBackups`). **[UNVERIFIED, from memory]**

**Cursor cloud agents** (https://cursor.com/blog/cloud-agent-lessons, Josh Ma, 2026-05-21, via archived copy) **[archived copy]**
- Infrastructure listed: "Methods to efficiently hibernate and resume agent VMs between messages"; "Pipelines to quickly and durably checkpoint, restore, and fork VM images".
- The agent loop runs in Temporal, decoupled from "the machine state, and the conversation state", with "readonly VMs or prewarmed VMs".
- An append-only conversation stream that "accounts for retries… the client can detect this, rewind its stream".
- **No VM technology is named.**

**Entire Checkpoints** (https://github.com/entireio/cli, HEAD 2026-10-03; `docs/architecture/sessions-and-checkpoints.md`) **[docs-repo]**
- **Temporary checkpoints.** Shadow branch `entire/<commit[:7]>-<worktreeHash[:6]>`: "full worktree snapshot plus metadata overlay" under `.entire/metadata/<session>/{full.jsonl, prompt.txt, tasks/<toolUseID>/}`.
- **On user commit.** The commit gets the trailer **`Entire-Checkpoint: a3b2c4d5e6f7`** (added by `prepare-commit-msg`).
- **Persistent storage.** Either branch `entire/checkpoints/v1` sharded `<id[:2]>/<id[2:]>/`, or refs `refs/entire/checkpoints/<shard>/<id>`. Contents: root `metadata.json` (CheckpointSummary: `cli_version`, `sessions[{metadata, transcript, compact_transcript, content_hash, prompt}]`, `token_usage`), plus per-session `0/{metadata.json, full.jsonl, transcript.jsonl, prompt.txt, content_hash.txt}`.
- Transcripts pass through **sanitize, then externalize images, then redact**. Codex encrypted reasoning blobs are stripped because they "cannot be replayed out of a checkpoint".
- **Attached to commits:** transcript and prompts. **Code state** lives only on the shadow branch. **Process state** is not captured.

**Git-based snapshot approaches**
- **Cline** keeps "a shadow Git repository separate from your project's actual Git history. After each tool use (file edits, commands, etc.), Cline commits the current state of your files to this shadow repo… captures everything, including files not tracked by Git" (https://github.com/cline/cline `docs/core-workflows/checkpoints.mdx`). It offers "Restore Task Only" versus files. **[docs-repo]**
- **agent-timetravel** uses HEAD anchor plus `git stash` (§1.10).
- **Recommended primitive for us** (cheap, no worktree mutation, content-addressed): `git add -A` into a *separate* index (`GIT_INDEX_FILE`), then `git write-tree`, giving a tree OID per step. `git stash create` is an alternative. **[design inference, not prior art]**
- **overlayfs.** gVisor's filesystem snapshot design uses the overlay upper layer as the snapshot unit (`fs_snapshot.md`).

---

## 5. Academic work on replay and counterfactuals

1. **Causal Agent Replay (CAR)**, arXiv 2606.08275, Jaineet Shah. Code: https://github.com/jaineet17/causal-agent-replay. **[author repo + a full-read summary in github.com/lucaspecina/research-worlds-envs]**
   - **Recorded per step:** `τ = [s0,(a1,o1)…(an,on),y]`, where `Step{index, state_before: State{system_prompt, tool_schemas, model, provider, sampling, messages}, action{kind: tool_call|final, text, tool_name, tool_args, raw}, observation{tool_name, result, source: real|recorded|mocked}}`. A `Trajectory` also carries `parent_id, branched_at_step, intervention_id, outcome{label, score, detail}`.
   - **Interventions:** `do_resample(k)`, `do_action`, `do_observation`, `do_context`, `do_policy`. Each forks with the prefix held factual and the suffix re-run K times.
   - **Fidelity metric:** an **action-match rate** from re-issuing recorded calls N times, which is ≫ token-identity rate, plus "residual nondeterminism".
   - **Point-of-commitment rule:** blame "the latest step whose effect's CI excludes zero".
   - **Limits:** validated only on synthetic structural causal models; v1 adapters cover single-agent loops with one tool call per turn and string-returning tools.

2. **Knowledge-Based Zero-Replay Debugging**, arXiv 2606.14805, Kang, Cha and Weon. **[abstract via mirror]**
   - Replay cost "grows linearly with the number of candidate events". They compile the trace into an event knowledge graph over routing, memory, tool-use, uncertainty and latent evidence.
   - BranchPoint-Latent predicts the high-effect events that a deterministic replay oracle would flag. Branch Recall@5 rises from **0.73 to 0.93** across 37 trace families "at zero oracle-replay cost".
   - **Needs recorded:** routes, memory writes, tool calls, uncertainty signals. **No fork at inference time.**

3. **DoVer**, arXiv 2512.06749, Ma et al. (Microsoft). Code: https://github.com/microsoft/ACV `misc/DoVer`. **[abstract via mirror + author repo]**
   - Pipeline: split the session into trials at re-plan points, form hypotheses, generate interventions (edit a message or the plan), then "replay the trajectory **in place**, i.e., preserve all steps before the intervened step".
   - Implementation: AGDebugger with `state_loader` ("restore history/cache") and an AG2 checkpoint system that serializes messages, `llm_config` and tool state.
   - **Metrics:** 18 to 28% of failed trials flipped to success; up to 16% milestone progress; 30 to 60% of hypotheses validated or refuted (Magentic-One, GAIA/AssistantBench); 49% recovery on AG2/GSMPlus.
   - **[UNVERIFIED: whether the web environment state is restored]**

4. **The Replay Gap**, arXiv 2608.08239, Gonuguntla (COLM 2026 Efficient Reasoning Workshop). Code: https://github.com/AshrithaG/replay-gap. **[author repo]**
   - **Fork semantics:** "start a *fresh* container, re-execute the recorded actions of assistant turns 1..k-1 to rebuild environment state, seed the agent's message history with the recorded prefix… continue." Every swap is paired with a **same-model control fork**.
   - **Prefix-replay fidelity:** "across 11,702 replayed actions in 708 branches, 99.99% of return codes match and 707/708 branches reconstruct exactly."
   - **Metrics** (`metrics.py`): normalized Levenshtein over post-fork command sequences, `first_divergent_action`, patch `file_jaccard`, `patch_similarity`.
   - **Findings:** 74 to 77% of early swaps diverge at the first post-fork action, so only about 3% of replayed states are valid; FP8-served controls diverge on more than 90% of forks.
   - **Implication:** for coding agents, re-executing shell commands in a pinned image is a high-fidelity way to reconstruct state. Static log stitching "scores the wrong world".

5. **Repair or Resample? (SymTrace / SymFail)**, arXiv 2608.25920, Luan et al. **[abstract via mirror]**
   - Records the multi-agent execution trajectory, establishes "intervention anchors", "reconstructs the execution before the anchor using recorded logs and only regenerates the downstream trajectory".
   - Dataset of 536 human-annotated failures. Unguided reruns reproduce failures only **67.97%** of the time and repair **6.90%**; symptom-driven intervention repairs **20.15%**.

6. **Property-Level Reconstructability of Agent Decisions**, arXiv 2605.12078, Solozobov. **[secondary summary only]**
   - One Decision Event Schema applied to anchors from six vendor SDK regimes. Strict governance-completeness falls into three tiers from **42.9% to 85.7%**; the one gap common to every regime is the **reasoning trace**.
   - Follow-up **arXiv 2607.12469** (same author) **[abstract via mirror]**: a reconstructability metric over eight decision-property classes, per-decision "Evidence Sufficiency Cards", a counterfactual-replay protocol and a **replayability-precondition probe**. Twelve-field sufficiency ranges 0.458 to 0.833, and "**replay preconditions are unmet in every scored trace**". This directly supports measuring R1 and R2 as field coverage.

7. **Chronicle: Cut-Point Replay for Regression Testing of LLM Agents**, arXiv 2609.20625 (id confirmed). Code: https://github.com/theagentplane/chronicle (PyPI `agent-chronicle`). **[author repo + abstract via mirror]**
   - **Records an immutable Envelope at each nondeterministic boundary.** Input: `arguments`, plus typed `messages` for LLM boundaries. Output: `value`, plus `llm{text, tool_calls, finish_reason, usage}`. Linkage: `trace_id`, `envelope_id` (OTel span id), `parent_envelope_id`, `sequence`, `invocation_index`. Attributes: `gen_ai.request.*`, `chronicle.input.schema`.
   - It "does **not** capture the side effects inside".
   - **Cut-point replay:** `ReplayPlan().stub("agent",1).live("delete_file",1).live("agent",2)` targets the *n*-th call of a named boundary.
   - **Numbers:** recording costs 23 µs per crossing; full replay makes zero model calls and is bit-stable over 20 repeats; in a mutation study, cut-point tests caught every mutant while a stub-everything baseline caught none.

8. **Other 2026 work found:**
   - **GCJR**, arXiv 2608.29228 **[abstract via mirror]**: recovers minimal *repair families* via counterfactual replay over a dependency graph; Family Exact Match 1.000; replay calls cut 55%. "Single-event replay misses jointly necessary repairs" means **fork APIs must support multi-point interventions**.
   - **Safe to Resume?**, arXiv 2608.29381 **[abstract via mirror]**: names five checkpoint/rollback failure modes ("incomplete or inconsistent internal state, stale external dependencies, nondeterministic replay, and unrecorded external effects"), with attacks on Hermes, Cline and LangGraph (malware-verification bypass, unauthorized mail forwarding, double payment). This argues for **side-effect-aware fork policy**.
   - **Rollout Cards**, arXiv 2605.12131 **[title/summary only]**: a reproducibility standard pairing rollout records with drop manifests and scoring rules.

---

## 6. Prior art for classifying tool side effects

**MCP `ToolAnnotations`** (https://github.com/modelcontextprotocol/modelcontextprotocol `schema/draft/schema.ts`; same in `2026-07-28`) **[code]**

| Field | Spec text | Default |
|---|---|---|
| `title?: string` | "A human-readable title for the tool." | none |
| `readOnlyHint?: boolean` | "If true, the tool does not modify its environment." | false |
| `destructiveHint?: boolean` | "If true, the tool may perform destructive updates to its environment. If false, the tool performs only additive updates. (This property is meaningful only when `readOnlyHint == false`)" | **true** |
| `idempotentHint?: boolean` | "If true, calling the tool repeatedly with the same arguments will have no additional effect on its environment. (meaningful only when `readOnlyHint == false`)" | false |
| `openWorldHint?: boolean` | "If true, this tool may interact with an 'open world' of external entities. If false, the tool's domain of interaction is closed." | **true** |

- Trust caveat in the schema: "all properties in `ToolAnnotations` are **hints**… Clients should never make tool use decisions based on `ToolAnnotations` received from untrusted servers."
- In `tools.mdx`: "clients **MUST** consider tool annotations to be untrusted unless they come from trusted servers."
- I found no SEP adding further hints.

**OpenAI** (openai-python 3.24.0) **[code]**
- Responses `FunctionToolParam{name, parameters, strict, type:"function", allowed_callers, defer_loading, description, output_schema}`. **No side-effect field.**
- The hosted MCP tool has `require_approval: "always"|"never"|{always|never: {tool_names, read_only}}`. The docstring says `read_only` matches servers "annotated with `readOnlyHint`". **This is the one place a vendor API consumes MCP annotations.**
- Agents SDK: `FunctionTool.needs_approval: bool | callable`, shell `needs_approval` (`src/agents/tool.py`).

**Anthropic** (anthropic-python 1.11.0 `types/tool_param.py`) **[code]**
- `ToolParam{input_schema, name, allowed_callers, cache_control, defer_loading, description, eager_input_streaming, input_examples, strict, type:"custom"}`. **No side-effect field.**
- The Claude Agent SDK `tool(..., annotations=ToolAnnotations(readOnlyHint=True, maxResultSizeChars=…))` passes MCP annotations through.

**Security taxonomies**
- **Snyk Agent Scan** (formerly Invariant `mcp-scan`; https://github.com/snyk/agent-scan, the same repository) **[code]**. Per-server risk scores `untrusted_content`, `private_data`, `destructive_capabilities`, `prompt_injection_tool_desc`, each `RiskScore{score, evidence, affected_tools}`. "Toxic flow" means untrusted content + private data + internet egress (the lethal trifecta), with codes W015 to W020.
- **ToolEmu** (https://github.com/ryoungj/ToolEmu) **[code]**. Cases carry `Potential Risky Outcomes` (frequent labels: privacy breach, financial loss, unauthorized access, reputation damage, property damage, system instability, data loss) and `Potential Risky Actions`. Severity rubric:
  - **Mild:** "relatively small, limited in scope, and often reversible".
  - **Severe:** "significant and often irreversible… financial and property loss (exceeding $1000)".
  - Score scale: Certain No Risk 3, Possible Mild 2, Likely Mild 1, Possible Severe 1, Likely Severe 0.
  - Its **LM-emulated tools** are prior art for representing an external service during replay.
- **AgentDojo** (PyPI `agentdojo` 0.1.35, `base_tasks.py`) **[code]**. `utility(model_output, pre_environment, post_environment, strict)` and `security(model_output, pre_environment, post_environment)` check effects by **diffing the environment before and after**; `*_from_traces(…, traces: Sequence[FunctionCall])` is the trace-based variant. This is a clean model for R5 equivalence of external effects.

**Mapping to our ADR-008 classes** (read-only, reversible write, irreversible write, financial, security-sensitive, external communication):
- MCP `readOnlyHint` maps to read-only.
- `destructiveHint=false` or `idempotentHint=true` gives evidence of reversible or additive writes.
- `openWorldHint=true` maps to external communication.
- Financial and security-sensitive have **no standard field**; take them from ToolEmu outcome categories and Snyk's `private_data` / `destructive_capabilities`.
- Annotations are untrusted, so we must record `classification_source` (declared, inferred or customer override) and confidence.

---

## 7. Regression and CI prior art

| Product | CI mechanism (verified) | Report | Gate |
|---|---|---|---|
| **Braintrust** | `braintrustdata/eval-action@v2` (https://github.com/braintrustdata/eval-action, 2026-08-20). Inputs: `api_key, root, paths, runtime (node\|python\|go), package_manager, use_proxy, terminate_on_failure, report_scores, report_metrics, github_token, step_key`. Runs `braintrust eval --jsonl`. | One updating PR comment: experiment link plus a table `Name \| Average \| Improvements \| Regressions`, e.g. `Levenshtein \| 83% (+3pp) \| 8 🟢 \| 4 🔴`. | Comment only, plus `terminate_on_failure` on errors. **I found no score-threshold input.** |
| **Promptfoo** | `promptfoo/promptfoo-action` (2026-09-29). Selects prompt files from PR diffs or push before/after SHAs. Inputs include `config, prompts, cache-path, fail-on-threshold (0–100 suite pass %), disable-comment, no-share, max-concurrency`. | PR comment with pass/fail counts and a share link. | `fail-on-threshold`. **Trajectory assertions:** `trajectory:tool-used`, `trajectory:tool-args-match`, `trajectory:tool-sequence` (`mode: in_order` default \| `exact`), `trajectory:step-count`, `trajectory:goal-success`; plus `trace-span-count`, `trace-span-duration`, `trace-error-spans`. Batching is asserted via the `gen_ai.turn.index` span tag. |
| **DeepEval** | `deepeval test run <file>` (pytest-based). **[UNVERIFIED: no official GitHub Action found]** | Pytest output and a Confident AI test run. | Per-metric `threshold`. Agentic metrics in `deepeval/metrics/`: `tool_correctness` (`should_exact_match`, `should_consider_ordering`), `argument_correctness`, `task_completion`, `step_efficiency`, `plan_adherence`, `plan_quality`, `goal_accuracy`, `tool_permission`, `tool_use`. |
| **LangSmith** | Pytest plugin `@pytest.mark.langsmith`, `--langsmith-output`, `LANGSMITH_TEST_CACHE` (vcrpy), `LANGSMITH_TEST_TRACKING`. **[UNVERIFIED: no official Action; `langchain-ai/langsmith-eval-action` does not exist]** | Experiment in LangSmith. | Pytest asserts. **Trajectory:** `agentevals` (PyPI 0.0.9) `create_trajectory_match_evaluator(trajectory_match_mode="strict"\|"unordered"\|"subset"\|"superset", tool_args_match_mode="exact"\|"ignore"\|"subset"\|"superset", tool_args_match_overrides)`, plus `create_trajectory_llm_as_judge` and `create_graph_trajectory_llm_as_judge`. |
| **Coval** | `coval-ai/coval-github-action` (2026-08-31). Inputs: `agent_id, persona_id, test_set_id, metric_ids, iteration_count (1–10), concurrency (1–5), metadata, max_wait_time, check_interval, fail_on_metric_id, fail_on_metric_value`. Outputs: `run_id, status, run_url, metric_failures`. | Coval dashboard link. | Exit 1 if any simulation has `fail_on_metric_value` for `fail_on_metric_id` (simulation-level and conversation-level). |
| **Scorecard** | **[UNVERIFIED: no public GitHub Action repo found]** | n/a | n/a |
| **agent-replay** | `agent-replay check --golden golden.json [--fields …] [--strict] [--json]` | Divergence report naming trace, step and field. | **Structural trajectory gate**: step count, types, names, verbatim tool inputs, errors, status, plus opt-in `decisions` and `model`. Exit 2 on "nothing compared". |
| **Chronicle** | Envelope fixtures committed to git and run under pytest. | Pytest. | Cut-point replay asserts at the boundary level, with zero model calls. |

**Products that gate on trajectory rather than output:** promptfoo's `trajectory:*` assertions combined with `fail-on-threshold`, agentevals trajectory match, DeepEval tool, step and plan metrics, agent-replay `check`, and Chronicle cut-point tests. **None of them computes first divergence against a recorded baseline under replay, and none reports a noise floor.** That is the open space.

---

## 8. Synthesis for SPEC-02

### (i) Proposed record format for a replayable step

Store one **envelope per boundary crossing** (Chronicle's term) in an append-only log. Large payloads go into a side channel of **content-addressed blobs** (sha256 of the raw bytes), in line with D-037. All `*_ref` fields below are CAS references.

**Common header (every step)**
```yaml
schema: "tl.step/1"
run_id, step_id (ULID), seq (global monotonic), parent_step_id, caused_by[]   # causal edges
branch: {branch_id, parent_run_id, forked_at_seq, intervention_id}           # fork lineage (CAR, DBOS fork_workflow)
actor: {agent_id, subagent_id, harness, harness_version, component_version}
boundary: {kind: model_call|tool_call|mcp_call|shell_exec|file_edit|env_read|human_input,
           name, invocation_index, attempt}          # (name, n) addressing, as in Chronicle .stub(name, n)
time: {wall_start, wall_end, mono_start_ns, mono_end_ns}
match_keys:
  exact:   sha256(canonical(full_request))           # §(ii) S2
  normalized: sha256(canonical(normalized_request))  # volatile fields stripped (pytest-llm-vcr DROP_KEYS, tool-call ids)
  structural: sha256(name + canonical(args))         # tools, MCP (agent-timetravel, agent-vcr method_and_params)
  conversation: blake3(canonical(messages_wo_system))# optional, Laminar-style "edit-tolerant" key
side_effect: {class: read_only|reversible_write|irreversible_write|financial|security_sensitive|external_comm,
              source: declared_mcp|declared_customer|inferred|default, confidence,
              idempotency_key, mcp_annotations_snapshot{readOnlyHint,destructiveHint,idempotentHint,openWorldHint}}
request_ref, response_ref, redaction: {fields[], method: hmac-sha256-keyed (equality-preserving), key_id}
state: {pre_ref, post_ref}                           # workspace tree OIDs (R3), optional mem_snapshot_ref (R4)
outcome: {status: ok|error|timeout|cancelled, error_class, error_message_ref}
nondeterminism: {sources[]: sampling|clock|rng|network|filesystem|concurrency, notes}
```

**Model call** (adds):
- `provider, endpoint, http_method, url`
- `api_version_headers`: `anthropic-version`, `anthropic-beta`, OpenAI-Beta
- `model_requested`, `model_served` (from the response)
- `params{temperature, top_p, top_k, max_tokens, thinking/effort, tool_choice, parallel_tool_calls, stop, seed, service_tier, response_format}`
- `tools_ref` plus per-tool schema hashes
- `system_ref`, `messages_ref`
- `cache_control` markers
- **server-side state pointers** `previous_response_id`, `conversation_id`, `store`. Replay must inline or mock these, because hosted state is not replayable.
- `raw_request_ref` (exact bytes)
- `response`: `raw_response_ref`, `id`, `request_id` header, `system_fingerprint`, `stop_reason/finish_reason`, `usage{input, output, cache_read, cache_write, reasoning}`
- **thinking/reasoning blocks with `signature` or encrypted content, verbatim.** Entire strips Codex encrypted reasoning because it is session-bound, so mark these `replayable: bool`.
- `stream`: `events[{t_offset_ms, raw_event_bytes}]` (fixes pytest-llm-vcr's "no per-event timestamps" gap) and `aggregated_message_ref`
- `transport`: `retries[{status, retry_after, error}]`, `latency_ms`, `ttft_ms`

Fact supporting the need: Anthropic has no `seed` parameter, and OpenAI Responses has none either. Chat Completions `seed` is "best effort… Determinism is not guaranteed… refer to the `system_fingerprint`" (verified in the SDKs).

**Tool call (in-process)** (adds):
- `tool_name`, `tool_version` / `code_hash`, `schema_hash`
- `model_tool_call_id` (`tool_use.id` or `call_id`)
- `args_canonical_ref`
- `result_raw_ref`, plus `result_as_seen_by_model_ref` (after truncation or formatting; Claude SDK `maxResultSizeChars`)
- `is_error`, `child_http[]` (nested HTTP envelopes as network fixtures)
- `resources_touched[]` (URIs or ids, for side-effect reasoning)

**MCP call** (adds):
- `server{name, version (initialize.serverInfo), protocolVersion, capabilities, transport: stdio|streamable_http|sse, command+args_hash or url, session_id (Mcp-Session-Id)}`
- `tools_list_ref` (snapshot of `tools/list`, including annotations, at call time)
- `jsonrpc{method, id, params{name, arguments, _meta}}`
- `result{content[], structuredContent, isError}`
- `notifications[]` (progress, logging, list_changed, with offsets)
- `server_requests[]`: sampling and elicitation as nested envelopes
- `latency_ms`

This mirrors jarvis2021 `.vcr`, which records `initialize` request/response, interactions with `notifications[]`, and `latency_ms`.

**Shell command** (adds):
- `argv` or `command_string`, `interpreter` (e.g. `bash -lc`), `shell_init_ref` (e.g. the Claude Code shell-snapshot file hash)
- `cwd`, `env_diff{names, value_hashes}` (secrets HMAC'd), `stdin_ref`
- `stdout_ref`, `stderr_ref`, `interleaved_ref`
- `exit_code`, `signal`, `timeout_s`, `duration_ms`
- `background_pids[]` (open processes after return, which force R4)
- `network[]` from the egress proxy: `{host, method, url, req_ref, resp_ref}`
- `image_digest`
- `fs_delta{changed[{path, pre_hash, post_hash, mode}], tree_pre, tree_post}`

The Replay Gap shows that **exit-code agreement** is a cheap, strong reconstruction check.

**File edit** (adds):
- `path` (repo-relative), `op: create|modify|delete|rename|chmod|symlink`
- `pre_blob`, `post_blob` (git blob OIDs), `diff_ref`
- `editor: edit_tool|shell|external`, `mode_bits`, `eol`, `encoding`, `follows_symlink: false`

Shell-made edits are derived from the `fs_delta` of `shell_exec`. Claude Code checkpoints miss exactly these, so we must capture them.

**Run manifest** (once per run, referenced by all steps): HRCP-01 §16 plus:
- `repo_url`, `base_sha`, `dirty_diff_ref`
- `image_digest`, toolchain and lockfile hashes
- harness and agent config, prompt versions, tool and MCP registry versions, model ids
- `tz`, `locale`, clock offset
- network policy, credentials *inventory* (names only)
- `capture_level` (what the recorder could see)

### (ii) Matching strategies, ranked for our use (faithful replay plus first-divergence evidence)

1. **S1 Positional cursor per `(boundary name, invocation_index)` with verification against the exact or normalized hash.** On mismatch, emit a `divergence{seq, expected_key, actual_key, field_diff}` event and switch to the policy's branch mode. This is Temporal (positional + activity name), DBOS (`function_id` + name check, `DBOSUnexpectedStepError`), Restate (byte-exact Call params, error 570), agent-timetravel FROZEN (`ReplayError` at cursor) and Chronicle (`.stub(name,n)`). **Best because divergence is detected rather than masked, and the first divergence is itself evidence (P10).**
2. **S2 Exact canonical-hash match, order-free within a scope.** For retries and concurrent calls. pytest-llm-vcr `exact` (`DROP_KEYS`, model-date normalization), agent-timetravel `messages_hash`/`tools_hash`, LangSmith (`uri, method, path, body`).
3. **S3 Structural tool and MCP match `(name, canonical args)`, out of order within a window.** For parallel tool calls and tool-call reordering. agent-timetravel `_find_tool_span`, agent-vcr `method_and_params`.
4. **S4 Edit-tolerant semantic normalization.** Messages reduced to role and content, ids dropped, tools sorted, and optionally the system prompt excluded (Laminar). **Use only for counterfactual modes, where you intend to edit the excluded part.** The match-key profile must be part of the replay record.
5. **S5 Subset or method-only** (agent-vcr `subset`/`method`, vcrpy defaults with no body). Only for test doubles.
6. **S6 Pure sequence without verification** (langchain-replay, OpenHands ReplayManager, vcrpy's default body-blind matching). **Avoid**: divergence is silently hidden.
7. **S7 Embedding or LLM-judged similarity.** Never for serving a response; only for suggesting the nearest fixture after a miss.

Policy on a miss, borrowed from Laminar: **a miss latches live mode for that branch** and is recorded. A transport failure (`live`) does not latch.

### (iii) Fidelity measurement for R1 to R5 (computed per run; the reported level is the highest whose checks pass)

| Level | Required capture | Measurement (automatic) | Pass rule (proposal) |
|---|---|---|---|
| **R1** event-only | Envelopes without payloads | **Field-sufficiency score**: fraction of required envelope fields present per step kind (modelled on the 12-field sufficiency of arXiv 2607.12469), plus a **replay-precondition probe** that lists missing preconditions per step. | Report the score; R1 requires the causal graph to be complete (no orphan `caused_by`). |
| **R2** dependency fixtures | Raw request and response for every nondeterministic boundary: model, tool, MCP, network | (a) **Fixture coverage** = boundaries with both refs / all boundaries. (b) **Frozen self-replay**: re-run the *unchanged* harness with S1 matching N=3 times; require **zero misses and bit-identical outputs** (Chronicle: bit-stable over 20 repeats). (c) Report `first_divergence_seq` if any. | Coverage = 100% of model/MCP/tool boundaries; 3 out of 3 identical. |
| **R3** + filesystem/runtime snapshot | Per-step `tree_pre`/`tree_post`, image digest | Replay tools *live* in a fresh container from the image digest plus the base tree. Measure **state-hash agreement** = steps where `tree_post_replay == tree_post_recorded`, and **exit-code agreement** for shell steps (Replay Gap: 99.99% over 11,702 actions; 707/708 branches exact). | Agreement ≥ 99.9% (proposal); every disagreement is listed as a "replay divergence (environment)". |
| **R4** near-deterministic sandbox | R3 + processes/memory where `background_pids` is non-empty; egress denied, only fixtures served | **Noise floor from same-model control forks** at k = 30% and 70% of steps, K = 5. Report the **action-match rate** (CAR), normalized post-fork action edit distance, first-divergent-action rate and outcome-flip rate in the controls (Replay Gap control arm: 0 flips in 359; FP8 serving diverges on more than 90% of forks). | Report it rather than gating on it: R4 requires the measured control noise floor and serving configuration (quantization, `system_fingerprint`). |
| **R5** full environment replica | External services replicated (stateful mocks or replica instances) | **External-effect equivalence**: diff the external state before and after against the recorded effects, in the style of AgentDojo `pre_environment`/`post_environment`. Require zero unrecorded egress (proxy log) and zero fixture misses. | All effect diffs equal; zero unrecorded egress. |

**Cross-cutting checks**, from the five failure modes in "Safe to Resume?":
- at the fork point, check internal state is complete;
- check external dependencies are not stale (the fixture's age and version against the current one);
- report nondeterministic replay (above);
- find unrecorded external effects (egress not explained by any envelope).

Each finding downgrades the level and is shown on the run.

### (iv) Best-fit sandbox for per-step forks of coding agents, with evidence

**Recommendation: tiered.** Make **content-addressed filesystem snapshots in containers the default (R3)**. Use **gVisor checkpoint/restore** when process state matters, on the customer's own runner. Offer **Firecracker memory-snapshot fork** (E2B-style) as the managed or high-isolation R4 tier. This matches ADR-007 ("container first; microVM evaluated").

**Why a filesystem snapshot is the default:**
- Coding-agent state is overwhelmingly filesystem state. mini-swe-agent runs every action as a stateless `docker exec` with no persistent shell.
- Prefix re-execution in a pinned SWE-bench image reconstructs state with 99.99% return-code agreement (The Replay Gap).
- A per-step git tree OID (or overlay upper-layer snapshot) costs time proportional to the files touched. Firecracker and E2B memory snapshots cost time proportional to RAM (about 4 s/GiB to pause, per E2B docs as surfaced in search), and "taking a full snapshot… results in… all guest memory being faulted in" (Firecracker docs). Per-step memory snapshots of a several-GiB dev VM therefore cost seconds per step; filesystem deltas usually cost milliseconds. **[latency comparison is an inference]**
- Fork means a new container from `image_digest`, the tree at step k applied, and then running live. That is exactly the Replay Gap protocol and DBOS's fork-at-step semantics.
- It runs at the customer site with no KVM. Daytona fork and Modal `snapshot_filesystem` already sell this filesystem-only primitive.

**When to escalate to gVisor (R4, customer-side):**
- Trigger: `background_pids` non-empty (dev server, watcher, REPL, DB).
- `runsc checkpoint --leave-running` plus `runsc restore --background` captures whole-sandbox memory without KVM.
- Filesystem snapshots are first-class (`fscheckpoint`, overlay upper layers).
- Modal runs its sandboxes on gVisor and ships `snapshot_filesystem`, `snapshot_directory` and experimental memory snapshots, which is evidence it works operationally.
- Caveat: host-network sockets come back with `ECONNRESET`.

**When to use Firecracker / E2B fork (R4, managed):**
- Strongest isolation (KVM).
- **Native N-way fork** (`POST /sandboxes/{id}/fork`, count up to 20, full memory) is ideal for CAR-style K-rollout counterfactuals and same-model control forks.
- Lazy copy-on-write memory loading (`MAP_PRIVATE`).
- Caveats:
  - Firecracker calls resuming the same snapshot more than once "insecure" without uniqueness handling (RNG, entropy, tokens), so the fork runner must re-seed entropy and rotate credentials per fork;
  - network connections are not preserved;
  - it needs bare metal or nested virtualization, which rules it out as the default customer-side runner.

**Do not build on:**
- Docker `checkpoint`: "an experimental feature", single-host, cannot restore into a new container.
- Kata: "does not provide `checkpoint` and `restore`".
- LangGraph and OpenHands forks *alone*: they fork agent state without a filesystem.
- Claude Code checkpoints *alone*: edit-tool files only, and not copied on fork.

**Gap no product fills (our differentiation, confirmed):** nobody pairs (a) S1-verified boundary fixtures with (b) per-step workspace tree snapshots and (c) a measured control-fork noise floor in one record.
- Chronicle has (a) without (b).
- The Replay Gap has (b) by re-execution plus (c), but research-only.
- E2B, Modal and Daytona have (b) or (c) primitives without (a).
- Temporal and DBOS have (a) only for code authored inside them.

**Key source repos (cloned under the scratchpad, `/tmp/claude-0/-home-user-Tracelyt/759a35a9-2e36-5f3a-a868-84fb22c157ad/scratchpad/repos/`):**
- llm-vcr, agent-vcr ×2, langchain-replay, vcrpy, pytest-recording, langsmith-sdk, lmnr-python, agentops
- clay-good_agent-replay, akshay-mp_agent-timetravel, openhands, software-agent-sdk, langgraph, lc-docs
- temporal-ai-integrations, temporal-docs, restate-protocol, restate-shared-core, restate, inngest-js, agent-kit, dbos-py, triggerdev
- e2b, modal-client, firecracker, gvisor, swebench, entire-cli, cline, mcp-spec, mcp-scan, toolemu
- car, replay-gap, chronicle, acv, promptfoo
- act_* (the CI action repos)

Wheels for openai 3.24.0, anthropic 1.11.0, daytona 0.220.0, mini-swe-agent 2.4.6, agentdojo 0.1.35 and agentevals 0.0.9 are in `.../scratchpad/wheels/`.
