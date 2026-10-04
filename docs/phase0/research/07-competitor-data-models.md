# Competitive architecture teardown: data models and mechanisms (as of 2026-10-04)

## Method and legend

I shallow-cloned each primary repository and read its schemas, migrations, docs sources and changelogs. The commit used for each citation is listed below. Vendor marketing and docs sites for arize.com, raindrop.ai, docs.honeycomb.io and langchain.com/pricing were blocked by the network proxy. For those I used GitHub-hosted docs, npm and PyPI packages, or search excerpts. I ran out of web searches partway through, so a few items stay unverified and are marked.

- **[V]** I read it in a primary source during this session (code, migration, docs source, or package).
- **[S]** It comes from a search-engine excerpt of a vendor page.
- **[P]** It comes from the earlier Track-1 report (`docs/archive/research/01-incumbent-teardown.md`) and I did not re-check it.
- **[U]** Unverified, or my inference.

Commits used: langsmith-sdk `61793baa48` (2026-10-02); langchain-ai/docs `14cfa205d9` (2026-10-03); langfuse `f75c661dbe`; langfuse-docs `2202a04812`; langfuse-python `618e4702a8`; phoenix `9212a42a51` (2026-10-02); lmnr `5b71e45a2d` (2026-09-13); lmnr-ai/docs `c61c660484`; judgeval `04a1848fb9`; weave `9c633e8d0d`; weave-claude-code `483d5cba13`; agentops `f8e907b92d` (last commit 2026-06-25); entireio/cli `f3f598a473` (2026-10-03); rungalileo/docs-official `fbcb642722`; DataDog/documentation `addf4da61d`; openlit `897838a26e` (that commit is #1685); openllmetry `be498301c4`; open-telemetry/semantic-conventions-genai `e07f4ebacb` (2026-10-02).

---

## 0. Corrections to the earlier research (read these first)

1. **Replay exists in two products, so "nobody ships replay" is no longer true.**
   - **Laminar debugger** serves recorded LLM responses from a server-side cache. The cache key is `(trace_id, input hash)`, and the hash leaves out system messages. Replay runs from cache up to the first cache miss or up to `LMNR_DEBUG_CACHE_UNTIL`, then runs live. Tools are not stubbed. [V] [lmnr app-server/src/debugger/mod.rs](https://github.com/lmnr-ai/lmnr/blob/5b71e45a2d/app-server/src/debugger/mod.rs), [docs/debugger/caching.mdx](https://github.com/lmnr-ai/docs/blob/c61c660484/debugger/caching.mdx)
   - **LangSmith Engine fix validation** (private beta) replays an issue's trace inputs against a baseline deployment and then against a preview deployment built from the fix PR. It records each run as an experiment. It is input replay, not deterministic replay. [V] [engine.mdx](https://github.com/langchain-ai/docs/blob/14cfa205d9/src/langsmith/engine.mdx)
   - The real remaining gap is narrower: deterministic or fixture replay of **tools and environment**, plus branching from an arbitrary recorded step, across vendors and frameworks.
2. **Galileo Agent Control is open source.** It lives at `github.com/agentcontrol/agent-control` under Apache-2.0, and PyPI `agent-control-*` is at 8.11.0. [V]
   - The canonical actions are only `deny | steer | observe`. `allow`, `warn` and `log` are legacy aliases that fold into `observe`. [V] (agent_control_models/actions.py in the wheel)
3. **OpenLIT has a discrete harness schema.** It defines 68 `coding_agent.*` constants and a strict adapter contract. Covered: edit decisions, permission mode, subagent spawn and complete, git commit and PR, loop detection, session outcome enum. [V] [coding-agents-convention.md](https://github.com/openlit/openlit/blob/897838a26e/agent-guides/coding-agents-convention.md)
4. **Weave has server-side failure clustering.** Tables `intent_signatures` and `failure_signatures` feed `signature_cluster_runs` and `signature_clusters`. Weave also has server-side PII redaction (`pii-v1`). The Claude Code plugin itself still says "PII scrubbing … not yet implemented". [V]
5. **OTel GenAI semconv now standardizes harness concepts.**
   - Memory operations: `create_memory`, `search_memory`, `update_memory`, `upsert_memory`, `delete_memory`, plus memory stores.
   - Also: `plan`, `invoke_workflow`, `gen_ai.conversation.compacted`, `gen_ai.main_agent.*` and `gen_ai.skill.*`. All are at "development" stability. [V]
   - Upstream also has `genainormalizerprocessor` (alpha) in the OTel collector-contrib repo. It rewrites OpenInference and OpenLLMetry attributes into `gen_ai.*`, and Dynatrace ships it. That is a direct overlap with any normalizer we build. [V]
6. **Phoenix's `DECISION` span kind is not an agent decision.** It is "a call to a decision model that scores or selects among candidate options". Its attributes are `decision.*` (model, provider, token counts). [V] PR #16657
7. **Datadog ships Insights (RCA-like) and Patterns (clustering).** [V]
   - Insights types: inefficient prompt caching, large tool results, verbose output, tool-call retry loops, prompt rule violations. They auto-resolve when no longer seen.
   - Patterns uses UMAP + HDBSCAN.
8. **Langfuse added metric and evaluator alerts and an on-demand Assistant.** [V]
   - Monitors and alerts use a Prisma `Monitor` model with thresholds, window and cadence.
   - The Assistant runs code over thousands of observations in a sandbox, for example to "cluster the main error types". Still no automatic clustering worker.

---

## 1. LangSmith (LangChain)

### Data model [V]
- **`Run` / `RunBase`** ([schemas.py](https://github.com/langchain-ai/langsmith-sdk/blob/61793baa48/python/langsmith/schemas.py)):
  - Core fields: `id`, `name`, `start_time`, `run_type` (str), `end_time`, `extra` (holds `metadata`, `runtime`, `invocation_params`), `error`, `serialized`, `events: list[dict]`, `inputs`, `outputs`, `reference_example_id`, `parent_run_id`, `tags`, `attachments`.
  - `Run` adds: `session_id` (the project), `child_run_ids`, `child_runs`, `feedback_stats`, `app_path`, `manifest_id`, `status`, `prompt_tokens`, `completion_tokens`, `total_tokens`, `prompt_token_details`, `completion_token_details`, `first_token_time`, `total_cost`, `prompt_cost`, `completion_cost`, `*_cost_details`, `parent_run_ids`, `trace_id`, `dotted_order`, `in_dataset`.
- **`RunTypeEnum`** (deprecated; plain strings now): `tool, chain, llm, retriever, embedding, prompt, parser`.
- **`dotted_order`** is `{YYYYMMDDTHHMMSSffffffZ}{run-uuid}` segments joined by `.`, root to leaf. It sorts in execution order.
- **Context propagation** uses headers `langsmith-trace` (the dotted order), `langsmith-metadata`, `langsmith-tags`, `langsmith-project`, `langsmith-address`, `langsmith-replicas`, plus `baggage` ([run_trees.py](https://github.com/langchain-ai/langsmith-sdk/blob/61793baa48/python/langsmith/run_trees.py)).
- **Agent addressing (beta, new).** `address = "lrn:agents/{id}/environments/{local|development|staging|production}"` replaces project routing ([address.py](https://github.com/langchain-ai/langsmith-sdk/blob/61793baa48/python/langsmith/address.py)).
- **`ls_agent_type` ∈ {`root`,`middleware`,`subagent`,`compaction`}** ([_ls_agent_type.py](https://github.com/langchain-ai/langsmith-sdk/blob/61793baa48/python/langsmith/_internal/_ls_agent_type.py)).
- **Coding-agent metadata contract `coding-agent-v1`** ([coding-agent-metadata-contract.mdx](https://github.com/langchain-ai/docs/blob/14cfa205d9/src/langsmith/coding-agent-metadata-contract.mdx)):
  - Required on every run: `ls_agent_type`, `ls_agent_purpose`, `ls_integration` (`claude-code`, `openai-codex`, `deepagents-code`, `cursor`, `pi`, `opencode`, `copilot`), `ls_agent_runtime`, `thread_id`, `ls_trace_schema_version`.
  - Required where known: `ls_agent_version`, `git_branch`, `git_commit_sha`, `git_repo_url`, `working_directory`.
  - Per run type: `ls_model_name` and `ls_provider` on llm runs; `ls_tool_name` on tool runs; `ls_subagent_id` and `ls_subagent_type` on subagent runs.
  - Run types: `root`, `llm`, `tool`, `subagent`, `interrupted`.
- **Threads and trajectories** ([threads.mdx](https://github.com/langchain-ai/docs/blob/14cfa205d9/src/langsmith/threads.mdx), [trajectory-view-integrations.mdx](https://github.com/langchain-ai/docs/blob/14cfa205d9/src/langsmith/trajectory-view-integrations.mdx)):
  - A thread groups runs sharing metadata `session_id`, `thread_id` or `conversation_id`. It must be set on all runs, including children.
  - The Trajectory view needs `thread_id` plus `ls_agent_type:"root"`. Subagent runs render as a subagent action. Middleware and compaction runs are filtered out.
- **Feedback** (`FeedbackBase`): `id`, `run_id`, `trace_id`, `key`, `score`, `value`, `comment`, `correction`, `feedback_source{type: api|model, metadata, user_id}`, `session_id`, `comparative_experiment_id`, `feedback_group_id`, `extra`. `FeedbackConfig.type` is `continuous | categorical | freeform`.
- **Dataset and Example**:
  - `Example`: `id`, `dataset_id`, `inputs`, `outputs`, `metadata`, `split`, `attachments`, `source_run_id`, `created_at`, `modified_at`.
  - `Dataset`: `data_type`, `inputs_schema`, `outputs_schema`, `transformations`.
  - `TracerSession` is the project; it has `reference_dataset_id` for experiments.
- **OTel ingestion mapping** ([trace-with-opentelemetry.mdx](https://github.com/langchain-ai/docs/blob/14cfa205d9/src/langsmith/trace-with-opentelemetry.mdx)):

| Source attribute | LangSmith field |
|---|---|
| `langsmith.trace.name` | name |
| `langsmith.span.kind` | run_type |
| `langsmith.trace.id` / `langsmith.span.id` / `langsmith.span.parent_id` | trace_id / id / parent_run_id |
| `langsmith.span.dotted_order` | dotted_order |
| `langsmith.trace.session_id` / `langsmith.trace.session_name` | session |
| `langsmith.span.tags` | tags |
| `langsmith.metadata.{k}` | metadata |
| `gen_ai.system` | `metadata.ls_provider` |
| `gen_ai.operation.name` | run_type (chat/completion → llm, embedding → embedding) |
| `gen_ai.prompt.{n}.*`, `gen_ai.completion.{n}.*` | `inputs.messages` / `outputs.messages` |
| `gen_ai.input.messages`, `gen_ai.output.messages` | `inputs.messages` / `outputs.messages` |
| `gen_ai.tool.name` | `invocation_params.tool_name`, and run_type=tool |
| `gen_ai.request.*` | `invocation_params.*` |
| `gen_ai.usage.*` (incl. `details.reasoning_tokens`) | `usage_metadata.*` |
| `traceloop.entity.input` / `.output` / `.name` | inputs / outputs / name |
| `traceloop.span.kind`, `traceloop.llm.request.type` | run_type |
| `traceloop.association.properties.{k}` | metadata |
| OpenInference `input.value`, `output.value`, `openinference.span.kind`, `llm.system`, `llm.model_name`, `tool.name`, `llm.input_messages`, `llm.output_messages`, `llm.token_count.*`, `llm.invocation_parameters`, `llm.prompt_template.variables` (→ run_type prompt), `retrieval.documents.{n}.document.*` | matching inputs / outputs / metadata / usage fields |
| Logfire `prompt`, `all_messages_events`, `events` | inputs / outputs |
| events `gen_ai.content.prompt`, `gen_ai.content.completion`, `gen_ai.{system,user,assistant,tool}.message`, `gen_ai.choice` | messages |
| event `exception` | status=error, error |

- **Evaluators API** ([_runner.py](https://github.com/langchain-ai/langsmith-sdk/blob/61793baa48/python/langsmith/evaluation/_runner.py)): `evaluate(target, data, evaluators, summary_evaluators, metadata, experiment_prefix, max_concurrency, num_repetitions, …)`. A tuple of two experiments gives comparative evaluation.
- **Trajectory matching** is in AgentEvals: `create_trajectory_match_evaluator(trajectory_match_mode=strict|unordered|subset|superset)`, plus LLM-judge trajectory evaluators ([trajectory-evals.mdx](https://github.com/langchain-ai/docs/blob/14cfa205d9/src/langsmith/trajectory-evals.mdx)).

### Engine [V] ([engine.mdx](https://github.com/langchain-ai/docs/blob/14cfa205d9/src/langsmith/engine.mdx), [engine-notifications.mdx](https://github.com/langchain-ai/docs/blob/14cfa205d9/src/langsmith/engine-notifications.mdx))
- **Lifecycle:** detect → diagnose against traces and the connected repo → propose a fix PR → track matching traces and generate dataset examples → close → auto-reopen on recurrence.
- **Trace selection:** a dedicated pull of low-scoring traces per feedback key, and feedback-scored traces are prioritized.
- **Configuration:**
  - Code repo, and an optional Context Hub repo.
  - Preferences such as Tool Call Failures, Latency, Cost & Tokens, or custom text.
  - Analysis level: Reduced, Standard or Expanded.
  - Scope: at most two conditions, Run Name and/or Metadata.
  - An editable agent overview doc, which also accumulates "User Preferences" learned from user actions.
  - Linear, Slack and webhooks.
- **Issue fields** (webhook `issue.created`): `id`, `name`, `description`, `severity` (int), `tenant_id`, `tenant_name`, `session_id`, `session_name`, `url`.
  - `issue.trace.added` adds `trace{run_id, trace_id, start_time, comment}`.
  - UI-only fields: priority (Low/Medium/High), failure category tag (for example "Silent tool error", "Hallucination"), evidence traces with snippet and causing child run, Proposed Fix, Watch.
  - CLI statuses are `open | fixing | watching | completed | ignored` and priorities `urgent | high | medium | low`.
- **Validation (beta):**
  - Up to 5 traces are replayed against the baseline deployment. Multi-turn prior turns are included.
  - Verdicts are Reproduced, Not reproduced or Inconclusive, written as feedback `engine_issue_validation`.
  - The fix PR gets the `preview` label, and a preview deployment is built and replayed. Up to 3 fix attempts.
  - Replay marker: `config.configurable.__engine_validation_replay__ = true` and header `X-LangSmith-Source: engine`. A tool allowlist middleware is supplied.
- **Red Teaming (beta):** reads 25 traces plus the repo, forms hypotheses, and sends at most 2 probes per hypothesis. There are 10 issue classes: Content Policy, Instruction Hierarchy, Indirect Injection, Data Exposure, Auth Isolation, Tool Safety, Workflow Integrity, Session Integrity, Input Robustness, Reliability Safety.
- **Cost:** LSUs at $1 each. Initialization takes 45–60 LSU and recurring scans 15–22.5 LSU. The org default cap is 750 LSU per month. LangChain-managed inference only (no BYOK).

### Insights [V] ([insights.mdx](https://github.com/langchain-ai/docs/blob/14cfa205d9/src/langsmith/insights.mdx))
- Up to 1,000 traces per report. It uses a thinking model for clustering and a summarization model per trace.
- Summary prompt variables: `run.inputs`, `run.outputs`, `run.error`, `run.feedback`, `run.feedback.<key>`, `all_thread_messages`.
- User-defined string, number or bool attributes can be extracted; `filter_by: true` turns one into a pre-filter.
- Top-level categories can be predefined; subcategories are always automatic.
- Schedule is daily, weekly or cron. Cost is $1–2 per 1k threads with OpenAI models and $3–4 with Anthropic.

### Teardown rows

| Row | LangSmith |
|---|---|
| Product thesis | The full agent-engineering lifecycle: trace → Engine issue → PR → dataset → validation, tied to the LangChain runtime and deployments. |
| OSS components | SDKs (MIT), AgentEvals, openevals. Platform is proprietary; self-hosted needs a license [V/P]. |
| Instrumentation | `@traceable`, wrappers (`wrap_openai`…), LangChain callbacks, OTel exporter, Claude Code plugin `langsmith-tracing` driven by hooks [V]. |
| Wire protocol | REST batch and multipart ingest of run create/patch; OTLP endpoint; dotted-order headers [V]. |
| Event/span schema | Run, as listed above [V]. |
| Trace model | Run tree keyed by `trace_id` and ordered by `dotted_order` [V]. |
| Session model | Project = `session_id`. Thread = shared `thread_id`, `session_id` or `conversation_id` metadata [V]. |
| Agent representation | `ls_agent_type=root`; Agent addressing `lrn:agents/{id}/environments/{env}` (beta) [V]. |
| Subagent representation | `ls_agent_type=subagent`, `ls_subagent_id`, `ls_subagent_type` [V]. |
| Context representation | `ls_agent_type=compaction` runs, filtered from the Trajectory view. No context-window model [V]. |
| Memory representation | None in the run schema. Managed Deep Agents has memory docs [U]. |
| Tool representation | `run_type=tool`, `ls_tool_name`, `gen_ai.tool.name` mapping [V]. |
| Verification representation | Feedback keys. Engine `engine_issue_validation` feedback. Assertions on dataset examples [V]. |
| Storage | Proprietary "SmithDB" [P]. |
| Evaluation | `evaluate()`, online evaluators, annotation queues, trajectory match modes [V]. |
| Failure detection | Engine scans plus failure-category tags; Insights categories [V]. |
| Clustering | Insights (LLM hierarchical categorization). Engine clusters issues by severity; algorithm undisclosed [V/U]. |
| Replay | Engine fix validation replays inputs against deployments (Cloud-only beta). No step-level or deterministic replay [V]. |
| Regression | Engine reopens issues on recurrence; experiments compare baseline and fix [V]. |
| Root-cause analysis | Engine diagnosis against code, with the causing child run identified [V]. |
| Automated remediation | Engine opens the PR and revises it up to 3 times after preview verification [V]. |
| Runtime control | Via the LangGraph runtime and Fleet interrupts, not observability [P]. |
| Security | Engine security page; replay marker is treated as untrusted [V]. |
| Privacy | Coding-agent secret redaction snippet; Engine uses LangChain-managed LLM keys [V]. |
| Deployment | Cloud and self-hosted (Engine needs a Helm flag) [V]. |
| Pricing | Engine LSUs as above [V]; seats and traces per Track-1 [P]. |
| Moat | Owns the agent runtime and deployments, which is what makes replay and fix verification possible. |
| Known weakness | Validation only works for agents on LangSmith Cloud deployments. Scope filter is limited to 2 conditions. No BYOK. |
| What we should integrate | Ingest `ls_agent_type` and the coding-agent-v1 contract. Map dotted_order. Accept the Engine webhook payloads. |
| Never rebuild | Its trajectory-match evaluators; consume AgentEvals instead. |
| Still unaddressed | Replay of tools and environment; first-divergence analysis; frameworks outside LangGraph and its deployments. |

---

## 2. Langfuse (ClickHouse)

### Data model [V]
- **Observation types:** `SPAN, EVENT, GENERATION, AGENT, TOOL, CHAIN, RETRIEVER, EVALUATOR, EMBEDDING, GUARDRAIL`. Levels: `DEBUG|DEFAULT|WARNING|ERROR` ([observations.ts](https://github.com/langfuse/langfuse/blob/f75c661dbe/packages/shared/src/domain/observations.ts)).
- **`ObservationSchema`:** `id, traceId, projectId, environment, type, startTime, endTime, name, metadata, parentObservationId, level, statusMessage, version, model, internalModelId, modelParameters, input, output, completionStartTime, promptId/Name/Version, latency, timeToFirstToken, (provided)usageDetails, (provided)costDetails, input/output/totalCost, input/output/totalUsage, usagePricingTierId/Name, toolDefinitions, toolCalls, toolCallNames`.
  - The v4 `EventsObservationSchema` adds `userId, sessionId, isRootObservation, traceName, release, tags, bookmarked, public`.
- **v4 storage** is the ClickHouse `events_full` table (ReplacingMergeTree) ([0039_create_events_full.up.sql](https://github.com/langfuse/langfuse/blob/f75c661dbe/packages/shared/clickhouse/migrations/canonical/0039_create_events_full.up.sql)).
  - One row per observation, with trace-level fields denormalized onto it: `trace_name, user_id, session_id, tags, is_app_root`.
  - Experiment fields: `experiment_id/name/…, experiment_item_id, experiment_item_expected_output, experiment_item_root_span_id`.
  - Instrumentation source: `source, service_name, scope_name, telemetry_sdk_*`.
  - Full-text indexes on input and output. `SAMPLE BY xxHash32(trace_id)`.
- **Score** ([scores.ts](https://github.com/langfuse/langfuse/blob/f75c661dbe/packages/shared/src/domain/scores.ts)):
  - Fields: `id, projectId, environment, name, value, source (API|EVAL|ANNOTATION), authorUserId, comment, metadata, configId, queueId, executionTraceId, traceId, sessionId, datasetRunId, observationId, longStringValue, timestamp`.
  - `dataType` is one of `NUMERIC|CATEGORICAL|BOOLEAN|CORRECTION|TEXT`.
- **`langfuse.*` OTel attributes** ([attributes.ts](https://github.com/langfuse/langfuse/blob/f75c661dbe/packages/shared/src/server/otel/attributes.ts)):
  - Trace: `langfuse.trace.{name,tags,public,metadata,input,output}`, `user.id`, `session.id` (compat names `langfuse.user.id`, `langfuse.session.id`).
  - Observation: `langfuse.observation.{type,metadata,level,status_message,input,output,completion_start_time,model.name,model.parameters,usage_details,cost_details,prompt.name,prompt.version}`.
  - Environment and versioning: `langfuse.environment`, `langfuse.release`, `langfuse.version`.
  - Internal: `langfuse.internal.as_root`, `langfuse.internal.is_app_root`.
  - Experiments: `langfuse.experiment.{id,name,metadata,description,dataset.id,item.id,item.version,item.metadata,item.root_observation_id,item.expected_output}`.
  - Evaluators: `langfuse.evaluator.id`, `langfuse.evaluation.rule.id`, `langfuse.evaluator.execution.is_test`.
- **Type inference** is a priority-ordered mapper ([ObservationTypeMapper.ts](https://github.com/langfuse/langfuse/blob/f75c661dbe/packages/shared/src/server/otel/ObservationTypeMapper.ts)):
  1. A legacy Python SDK v3.3 override.
  2. `langfuse.observation.type`.
  3. `openinference.span.kind`: LLM→GENERATION, CHAIN, RETRIEVER, EMBEDDING, AGENT, TOOL, GUARDRAIL, EVALUATOR map to themselves.
  4. `gen_ai.operation.name`: chat, completion, text_completion, generate_content and generate → GENERATION; embeddings → EMBEDDING; invoke_agent and create_agent → AGENT; execute_tool → TOOL.
  5. `genkit:metadata:subtype`.
  6. Vercel `ai.*` operation IDs.
  7. `gen_ai.tool.name` or `gen_ai.tool.call.id` → TOOL.
  8. Flue: `flue.tool.*` → TOOL, `flue.task.*` → AGENT.
  9. LiveKit span names `agent_turn` and `start_agent_activity` → AGENT; `function_tool` → TOOL.
  10. Any model attribute → GENERATION.
- **Field mapping in the docs** ([OTel doc](https://github.com/langfuse/langfuse-docs/blob/2202a04812/content/integrations/native/opentelemetry/index.mdx)):
  - input: `langfuse.observation.input` | `gen_ai.prompt` | `input.value` | `mlflow.spanInputs` | `gen_ai.tool.call.arguments`.
  - output: the same pattern with `gen_ai.tool.call.result`.
  - model: `gen_ai.request.model` | `gen_ai.response.model` | `llm.model_name` | `model`.
  - usage: `gen_ai.usage.*` | `llm.token_count.*`. Cost: `gen_ai.usage.cost` (stored as `total`).
  - environment: `deployment.environment(.name)`.
  - Unmapped attributes go to `metadata.attributes.*`; resource attributes to `metadata.resourceAttributes.*`.
- **Agent graph inference** ([buildStepData.ts](https://github.com/langfuse/langfuse/blob/f75c661dbe/web/src/features/trace-graph-view/buildStepData.ts), [graphAvailability.ts](https://github.com/langfuse/langfuse/blob/f75c661dbe/web/src/features/traces/fns/graphAvailability.ts)):
  - The graph is available if any observation type is not SPAN, EVENT or GENERATION, or if a LangGraph `step` is non-zero. Otherwise it needs more than one distinct node name. The cap is 5,000 nodes.
  - Steps come from time-overlap grouping: an observation starting before any group member ends joins that group.
  - A child must sit at parent step + 1 or later; later observations get pushed.
  - Synthetic `__start__` and `__end__` nodes are added.
  - Two modes: "aggregated" (repeated names collapse, loops show as cycles) and "expanded" (a DAG from the hierarchy plus happened-before ordering between siblings).
  - LangGraph metadata `langgraph_node` / `langgraph_step` are used when present.
- **Evaluator templates** ([managed-evaluators.json](https://github.com/langfuse/langfuse/blob/f75c661dbe/worker/src/constants/managed-evaluators.json)), 23 in total:
  - Hallucination, Helpfulness, Relevance, Toxicity, Correctness, Contextrelevance, Contextcorrectness, Conciseness, User Distress, User Disagreement, Out-of-Scope Request.
  - Ragas: Answer Correctness, Answer Relevance, Answer Critic, Context Precision, Context Recall, Faithfulness (×2), Goal Accuracy, Simple Criteria, SQL Semantic Equivalence, Topic Adherence Classification, Topic Adherence Refusal.
  - Also "Jev as a judge" (TypeSafe decision model, added 2026-09-22) [V].
- **MCP server tools** (`/api/public/mcp`, streamable HTTP) ([web/src/features/mcp/server](https://github.com/langfuse/langfuse/tree/f75c661dbe/web/src/features/mcp/server)), grouped:
  - Observations: `listObservations` (has `isRootObservation`), `getObservation`, `getObservationFieldSchema`, `getObservationFilterSchema`, `getObservationFilterValues`.
  - Scores and score configs: `createScore`, `getScore`, `listScores`, and score-config CRUD.
  - Datasets and runs: `*Dataset*`, `*DatasetItem*`, `*DatasetRun*`.
  - Experiments: `listExperiments`, `listExperimentItems`.
  - Evaluators: `createEvaluator`, `testEvaluator`, `listManagedEvaluatorTemplates`, and `*EvaluationRule*` attach and detach.
  - Prompts: `createChatPrompt`, `createTextPrompt`, `getPrompt`, `updatePromptLabels`.
  - Other: `queryMetrics`, dashboards and widgets CRUD, annotation queues, comments, `getMedia`, models CRUD, `listAlerts`, `getAlert`, skills (`listSkills`, `loadSkill`), `submitFeedback`, `getHealth`.
- **Python SDK**: observation types `generation|embedding` (generation-like); `span|agent|tool|chain|retriever|evaluator|guardrail`; plus `event`. API: `start_observation`, `start_as_current_observation`, `@observe(as_type=…)`.

### Teardown rows

| Row | Langfuse |
|---|---|
| Product thesis | Open-source LLM engineering platform: tracing, evals, prompts. Agent-native access via MCP, CLI and skills rather than built-in AI triage. |
| OSS components | Core MIT with an `ee/` folder; SDKs MIT [V]. |
| Instrumentation | OTel-native SDK v4; Claude Code plugin using a Stop hook that parses transcripts; Codex and Cursor [V]. |
| Wire protocol | OTLP/HTTP `/api/public/otel` plus legacy ingestion API [V]. |
| Event/span schema | Observation, as listed above [V]. |
| Trace model | v4: trace = observations sharing `trace_id`; trace fields denormalized onto `events_full`; `is_app_root` marks a logical root [V]. |
| Session model | `session.id` / `langfuse.session.id` [V]. |
| Agent representation | Type `AGENT`; graph view [V]. |
| Subagent representation | Nested `AGENT` observations; no explicit subagent fields [V]. |
| Context representation | None [V]. |
| Memory representation | None [V]. |
| Tool representation | `TOOL` type; `tool_definitions`, `tool_calls`, `tool_call_names` columns [V]. |
| Verification representation | Scores (5 data types), `EVALUATOR` and `GUARDRAIL` types [V]. |
| Storage | ClickHouse + Postgres + S3 blob [V]. |
| Evaluation | LLM-as-judge rules, 23 templates, backfills, reusable evaluators, Jev [V]. |
| Failure detection | Threshold monitors and alerts on metrics and evaluator scores [V]. |
| Clustering | Not automatic; the Assistant does it on request in a sandbox [V]. |
| Replay | Playground for a single generation only [P]. |
| Regression | Experiments and dataset runs [V]. |
| Root-cause analysis | Manual, or the Assistant [V]. |
| Automated remediation | None (Assistant drafts prompts with approval) [V]. |
| Runtime control | None; `GUARDRAIL` is observed only [V]. |
| Security / privacy | Masking on the SDK side; self-hostable [P]. |
| Deployment | Cloud (US/EU/JP/HIPAA) and self-hosted [P]. |
| Pricing | Hobby free (50k units), Core $29, Pro $199, Teams add-on $300/mo, Enterprise $2,499; 100k units included plus graduated overage [V] ([PricingTable.tsx](https://github.com/langfuse/langfuse-docs/blob/2202a04812/components/home/pricing/PricingTable.tsx)). |
| Moat | OSS mindshare, ClickHouse backing, the widest OTel mapping table. |
| Known weakness | No automatic issue detection or replay; graph is inferred from timing heuristics. |
| What we should integrate | Read and write through OTel and the MCP server; use the type-mapper ordering as a reference. |
| Never rebuild | A generic trace store and UI. |
| Still unaddressed | Harness events, divergence, replay. |

---

## 3. Arize Phoenix / AX (Dynatrace)

### Data model [V] ([models.py](https://github.com/Arize-ai/phoenix/blob/9212a42a51/src/phoenix/db/models.py))
- **Project:** `name, description, gradient colors, trace_retention_policy_id`.
- **ProjectSession:** `session_id` (unique), `project_id`, `start_time`, `end_time`.
- **Trace:** `project_rowid, trace_id, project_session_rowid, start_time, end_time`.
- **Span:** `trace_rowid, span_id, parent_id, name, span_kind, start_time, end_time, attributes (JSON), events (JSON), status_code, status_message, cumulative_error_count, cumulative_llm_token_count_prompt/completion, llm_token_count_prompt/completion`.
- **Annotations** come in four kinds: `SpanAnnotation`, `TraceAnnotation`, `ProjectSessionAnnotation`, `DocumentAnnotation (document_position)`.
  - Each has `name, label, score, explanation, metadata, annotator_kind (LLM|CODE|HUMAN), identifier, source (API|APP), user_id`.
- **Datasets:**
  - `Dataset (name, metadata)`, `DatasetVersion`.
  - `DatasetExample (span_rowid` links to the source span`, external_id)`.
  - `DatasetExampleRevision (input, output, metadata, content_hash, revision_kind)`.
  - `DatasetSplit`, `DatasetLabel`.
- **Experiments:**
  - `Experiment (dataset_id, dataset_version_id, name, repetitions, metadata, is_ephemeral, project_name)`.
  - `ExperimentRun (repetition_number, trace_id, output, start/end, token counts, error)`.
  - `ExperimentRunAnnotation (…, trace_id, error)`.
- **`SpanKind`:** `TOOL, CHAIN, LLM, PROMPT, RETRIEVER, EMBEDDING, AGENT, RERANKER, EVALUATOR, GUARDRAIL, DECISION, UNKNOWN` ([schemas.py](https://github.com/Arize-ai/phoenix/blob/9212a42a51/src/phoenix/trace/schemas.py)).
- **DECISION** arrived in v20.19.0 on 2026-10-01 (PR #16657).
  - Definition: "decision model that scores or selects among candidate options".
  - It needs OpenInference semconv Python 0.1.40 / TS 2.13.0.
  - There are no decision-specific UI cards yet, and it is flagged experimental.
  - OpenInference defines `decision.model_name, decision.provider, decision.system, decision.request.model_name, decision.response.model_name, decision.token_count.input/output` ([OpenInference semconv](https://github.com/Arize-ai/openinference/blob/main/python/openinference-semantic-conventions/src/openinference/semconv/trace/__init__.py)).
- **Other 20.x changes:** v20.17 marks bash tool spans as errors on non-zero exit; v20.18 shows eval results in the trace tree. The PXI agent emits `pxi.approval.decision ∈ {accepted, rejected}` on gated tools ([CHANGELOG](https://github.com/Arize-ai/phoenix/blob/9212a42a51/CHANGELOG.md)).
- **OpenInference agent-relevant attributes:**
  - Graph and identity: `agent.name`, `graph.node.id`, `graph.node.name`, `graph.node.parent_id`, `session.id`, `user.id`.
  - Tools: `tool.name|id|description|json_schema|parameters`, `tool_call.id`, `tool_call.function.name|arguments`, `llm.tools`.
  - Messages and IO: `message.tool_call_id`, `input.value`, `output.value`.
  - Annotations as attributes: `trace.annotations`, `session.annotations`, `annotation.*`, `evaluation.*`.
- **Issue #11654 "Trajectory Evals"** [V via WebFetch]:
  - Open, labels `priority: highest`, `roadmap`, `size:L`, created 2026-02-20.
  - Sub-issues: spec (#11836); Python and TS agent-experiment examples (#11837/#11838); plumbing traceId to evaluators in Python and TS (#12167/#12329); end-to-end example (#12168); intermediate at-turn-N evaluation (#12169); **ATIF-to-trace conversion (#12170)**; passing trace ID through the clients (#12454/#12285).
  - Open question: "how do we expose trajectories at the end of an experiment".
- **Signal (AX)** [S]: a managed agent that scans on a default 6-hour schedule (configurable from 3 hours to monthly).
  - Each issue has: overview of the pattern, supporting traces, investigation, root-cause hypothesis, recommended prompt/code/config/eval change.
  - Sort by severity or last seen. PRs on Enterprise [P].
  - I could not reach the docs to get exact field names [U].

### Teardown rows

| Row | Arize Phoenix / AX |
|---|---|
| Product thesis | OSS tracing and evals (Phoenix) plus an enterprise "self-improving agents" platform (AX, Signal, Alyx), now inside Dynatrace. |
| OSS components | Phoenix is **Elastic License 2.0** [V]; OpenInference semconv and instrumentations are Apache [U]. |
| Instrumentation | OpenInference instrumentors; `phoenix.otel.register()` [V]. |
| Wire protocol | OTLP (gRPC/HTTP) [V]. |
| Event/span schema | OpenInference attributes stored in a JSON `attributes` column [V]. |
| Trace model | OTel span tree [V]. |
| Session model | `session.id` → ProjectSession [V]. |
| Agent representation | `AGENT` kind, `agent.name`, `graph.node.*` [V]. |
| Subagent representation | Nested AGENT spans plus `graph.node.parent_id` [V]. |
| Context representation | None [V]. |
| Memory representation | None [V]. |
| Tool representation | `TOOL` kind plus `tool.*` / `tool_call.*` [V]. |
| Verification representation | Annotations on span, trace, session and document; `EVALUATOR` and `GUARDRAIL` kinds [V]. |
| Storage | Postgres or SQLite [V]. |
| Evaluation | Phoenix evals, experiments with repetitions; trajectory evals still on the roadmap [V]. |
| Failure detection | AX Signal [S]. |
| Clustering | Signal groups recurring failures [S]. |
| Replay | Playground and experiment re-runs; no trace replay [U]. |
| Regression | Experiments on dataset versions [V]. |
| Root-cause analysis | Signal hypothesis; Alyx [S]. |
| Automated remediation | Signal recommends changes; PRs on Enterprise [S/P]. |
| Runtime control | None [U]. |
| Security / privacy | Self-host; RBAC [U]. |
| Deployment | OSS self-host; AX SaaS [V/S]. |
| Pricing | AX Free 25k spans; Pro $50 [P]. |
| Moat | OpenInference as a de facto convention; Dynatrace distribution. |
| Known weakness | ELv2 license; trajectory evals still not shipped. |
| What we should integrate | OpenInference ingestion, or use the upstream normalizer. ATIF if it is published. |
| Never rebuild | OpenInference instrumentors. |
| Still unaddressed | Harness events and cross-run divergence. |

---

## 4. Laminar

### Data model [V] (ClickHouse migrations in [frontend/lib/clickhouse/migrations](https://github.com/lmnr-ai/lmnr/tree/5b71e45a2d/frontend/lib/clickhouse/migrations); Apache-2.0)
- **`spans_v2`** ([33_spans_new_order_with_projection.sql](https://github.com/lmnr-ai/lmnr/blob/5b71e45a2d/frontend/lib/clickhouse/migrations/33_spans_new_order_with_projection.sql)):
  - Columns: `span_id, name, span_type UInt8, start_time, end_time, input/output/total_cost, model, session_id, project_id, trace_id, provider, input/output/total_tokens, user_id, path, input, output, size_bytes, status, attributes, request_model, response_model, parent_span_id, trace_metadata, trace_type, tags_array, events Array(Tuple(timestamp, name, attributes))`.
  - `span_type` codes: 0 DEFAULT, 1 LLM, 3 EXECUTOR, 4 EVALUATOR, 5 EVALUATION, 6 TOOL, 7 HUMAN_EVALUATOR, 8 EVENT. CACHED also exists.
  - `traces_agg` carries `signal_events Array(Tuple(event_id, signal_id, severity, payload))` and `cluster_ids` ([65](https://github.com/lmnr-ai/lmnr/blob/5b71e45a2d/frontend/lib/clickhouse/migrations/65_trace_signal_clusters.sql)).
- **Signals tables:**
  - `signal_runs (project_id, signal_id, job_id, trigger_id, run_id, trace_id, status, event_id, error_message, mode BATCH|REALTIME, input/cache_read/output tokens, signal_version)`. Status is PROCESSING, COMPLETED, FAILED or PENDING.
  - `signal_events (id, project_id, signal_id, trace_id, run_id, name, payload, timestamp, severity, summary, summaries, signal_version)`.
  - `signal_event_clusters (id, signal_id, name, level, centroid Array(BFloat16)[768] with HNSW cosine index, parent_id, num_signal_events, num_children_clusters, centroid_at_naming)`.
  - `events_to_clusters (event_id, cluster_id, content)`.
  - `signal_event_summaries`.
  - Also `notifications`, `notification_deliveries`, `labeling_queue_items`, `system_prompt_versions`.
- **Signals mechanism** ([signals/introduction.mdx](https://github.com/lmnr-ai/docs/blob/c61c660484/signals/introduction.mdx), [clusters.mdx](https://github.com/lmnr-ai/docs/blob/c61c660484/signals/clusters.mdx)):
  - Definition: prompt + JSON-schema output + trigger (root span ends, or a named span ends) + filters (default: more than 1000 tokens; error status; span name present).
  - Processing: the trace is compressed to about 10% of its size (system prompts deduped, plumbing dropped, short span refs kept). An agent with search and fetch-span tools then investigates.
  - Output: 0..N findings, each `{summary, severity: critical|warning|info, payload}`, which become signal events.
  - Modes: live or backfill.
  - Clustering: online, batched about every minute, at most 3 levels, named bottom-up by an LLM, scoped per Signal.
  - Query surface: SQL over `traces.clusters` and `signal_events.{clusters, leaf_clusters, cluster_details}`. Alerts on severity and payload filters. CLI and Terraform supported.
- **Debugger (`LMNR_DEBUG=true`)** ([debugger docs](https://github.com/lmnr-ai/docs/blob/c61c660484/debugger/process.mdx), [debugger/mod.rs](https://github.com/lmnr-ai/lmnr/blob/5b71e45a2d/app-server/src/debugger/mod.rs)):
  - Session state is kept in `.lmnr/debug-session.json`. Each run prints `LMNR_DEBUG_RUN {session_id, trace_id, replay_trace_id, cache_until, debugger_url, started_at}`.
  - A session timeline holds blocks: runs, evals, notes, CLI commands.
  - Replay cache key: `(project, replay_trace_id, cache_until needle, input_hash)`. The cache is warmed lazily from the original trace's LLM/CACHED spans.
  - Responses are `Raw{response}` (from `lmnr.sdk.raw.response`) or `GenAi{messages}`, with `finish_reasons` and `model`.
  - Lookup outcomes: `Hit` / `Miss` (live from then on) / `Live` (warmup timed out).
  - Supported clients: Python OpenAI, Anthropic, Google GenAI, LiteLLM; TS AI SDK through `wrapLanguageModel`.
  - The coding agent drives the loop using the `lmnr-skills` skill.
- **Agent identity inference ("checkpoints")** ([checkpoints/](https://github.com/lmnr-ai/lmnr/tree/5b71e45a2d/app-server/src/checkpoints)):
  - A conversation-start LLM span (exactly 2 input messages) has its system prompt stripped of dynamic content and hashed into a `version_hash`.
  - An LLM classifier decides "new agent (with a name)" or "modified version of an existing agent".
  - Results go to `system_prompt_versions`. Spans also carry `lmnr.span.agent_hash` and `lmnr.span.prompt_hash`.
- **Browser session replay:** rrweb events in `browser_session_events (event_id, trace_id, session_id, timestamp, event_type UInt8, data ZSTD, project_id, size_bytes)`, played with `rrweb-player`. Traces are flagged with `lmnr.internal.has_browser_session`.
- **SDK attributes** ([span-attribute-reference.mdx](https://github.com/lmnr-ai/docs/blob/c61c660484/tracing/structure/span-attribute-reference.mdx)):
  - Span: `lmnr.span.{type,input,output,path,ids_path,parent_path,parent_ids_path,instrumentation_source,sdk_version,language_version}`.
  - Association: `lmnr.association.properties.{session_id,user_id,rollout_session_id,trace_type,tags,metadata.<k>}`.
  - Internal: `lmnr.internal.{checkpoint,claude_code_proxy,has_browser_session,trace_input,…}`.
  - Costs: `gen_ai.usage.{input_cost,output_cost,cost}`.
  - Cache tiers: `gen_ai.usage.cache_creation.input_tokens.ephemeral_5m|1h`.

### Teardown rows

| Row | Laminar |
|---|---|
| Product thesis | A trace-native debugger and Signals engine built for coding agents to drive. |
| OSS components | Whole platform Apache-2.0 (Rust app-server, Next.js, ClickHouse) [V]. |
| Instrumentation | `@observe`, auto-instrumentation, Claude Code plugin (`lmnr-cli plugin add claude-code`, with an LLM proxy) [V]. |
| Wire protocol | OTLP plus a custom browser-events API [V]. |
| Event/span schema | `spans_v2` plus `lmnr.*` attributes [V]. |
| Trace model | Span tree plus `path` / `ids_path` arrays [V]. |
| Session model | `lmnr.association.properties.session_id`; separate debug sessions [V]. |
| Agent representation | Inferred from the system-prompt version hash plus an LLM classifier [V]. |
| Subagent representation | `path` grouping; "collapsed sub-agent cards" in the transcript [V]. |
| Context representation | Dedup of repeated system prompts; no compaction model [V]. |
| Memory representation | None [V]. |
| Tool representation | `span_type=TOOL` [V]. |
| Verification representation | Evaluations and human evaluator span types [V]. |
| Storage | ClickHouse + Postgres + Quickwit [V]. |
| Evaluation | Evals framework; evals inside debug sessions compare against the previous eval [V]. |
| Failure detection | Signals (agentic, full trace) [V]. |
| Clustering | Hierarchical online clustering with HNSW, 768-dimensional centroids [V]. |
| Replay | LLM-response prefix cache replay; browser rrweb replay [V]. |
| Regression | Clusters that appear new; eval deltas [V]. |
| Root-cause analysis | The coding agent reads traces via CLI or SQL [V]. |
| Automated remediation | Done by the user's coding agent, not by Laminar [V]. |
| Runtime control | None [V]. |
| Security / privacy | `pii-redactor` service in the repo [V-dir]. |
| Deployment | Cloud and self-host [V]. |
| Pricing | Signals billed by analysis tokens; tiers per Track-1 [P]. |
| Moat | Replay cache plus a loop that coding agents drive. |
| Known weakness | Tools and environment are not replayed; caching works with few SDKs; small company. |
| What we should integrate | Adopt the input-hash-excluding-system-prompt cache idea and import their signal events. |
| Never rebuild | rrweb browser replay. |
| Still unaddressed | Tool and environment fixtures; branching; harness events. |

---

## 5. Raindrop

### Data model [V] (npm `raindrop-ai` 0.9.1 MIT; `@raindrop-ai/query` 0.1.14; `@raindrop-ai/cursor` 0.0.8; PyPI `raindrop-ai` 0.0.73)
- **`TrackEvent`:** `{eventId?, event, properties?, featureFlags?, timestamp?, userId}`.
- **`AiTrackEvent`** adds `model?, convoId?, attachments?, usage?, input/output`.
- **`Attachment`:** `{attachment_id?, name?, value, role: input|output, type: code(language?)|text|image|iframe}`.
- **`SignalEvent`** is `BasicSignal{eventId, name ("thumbs_up"|"thumbs_down"|string), sentiment? POSITIVE|NEGATIVE, timestamp?, properties?, attachmentId?}` with `type` of `default|standard`, `feedback` (comment), `edit` (after), or `agent|agent_internal`.
- **`SelfDiagnoseOptions`:** `{eventId, description, category?, source?, sentiment?, properties?}`. The agent reports its own failure mid-run.
- **Subagents:** `SubagentDispatch{childEventId, name, parentEventId, dispatchSpanId?, carrier}` and `SubagentRun`.
- **Span attributes:**
  - Handoff: `raindrop.handoff.{childEventId,parentEventId,parentSpanId,mode,name,terminal}`.
  - Identity: `raindrop.agent.role`, `raindrop.eventId`, `raindrop.project_id`.
  - App version: `raindrop.app.{commit_sha,branch,commit_dirty}`.
  - Usage: `raindrop.usage.input_tokens.{cache_read,cache_write,non_cached}`, `raindrop.usage.output_tokens.{reasoning,non_reasoning,total}`.
  - Replay and eval: `raindrop.replay.row`, `raindrop.eval_correlation_id`.
  - Tools: `ai.prompt.tools`, mirrored from Traceloop `llm.request.functions.*`.
- **Query API:**
  - Signal type enum: `topic|regex|instrumented|metric|code`. Signal sentiment: `NEGATIVE|POSITIVE|NEUTRAL`.
  - Signal: `{id,type,name,description,createdAt,groupId,groupName,sentiment}`. SignalGroup: `{id,name,description,orgId,signalCount}`.
  - Event: `{id,eventName,userId,convoId,timestamp,userInput,assistantOutput,model,topics[],input/outputAttachments,signals[],errorSpans[{spanId,status,durationMs,spanType,spanName,outputPayload}],toolCalls[{toolName,status,durationMs,startedAt,spanId}],featureFlags}`.
- **Cursor plugin hooks:** `sessionStart, beforeSubmitPrompt, postToolUse, postToolUseFailure, afterAgentResponse, afterAgentThought, stop, preCompact, sessionEnd`.
- **Evals and replay:** `defineEvalSuite` / `runEvalSuite` and `replay(raindrop, {...})`. Replay calls the agent once per dataset row and pins commit identity.
- **"Issues" model** [S]: Issue Detection v2 layers "Stumbles" (single failures, including self-flagged ones), Issues and Signals, ranked by severity. Also a Triage Agent and an MCP server. I found no Issue object in the public Query SDK [U].

### Teardown rows (condensed)
- **Thesis:** "Sentry for agents". Silent-failure discovery driven by signals and user feedback.
- **OSS:** SDKs MIT only.
- **Instrumentation:** events SDK plus a Traceloop-based OTel pipeline. Integrations: Vercel AI SDK, OpenAI Agents, LangChain, Deep Agents, Pi, Cursor, Eve.
- **Wire:** `/v1/events` plus OTLP/HTTP JSON.
- **Session model:** `convoId`.
- **Subagents:** handoff attributes plus dispatch carriers.
- **Context:** the `preCompact` hook only.
- **Verification:** signals, feedback and edit signals.
- **Clustering:** topics (Deep Search) [S].
- **Replay:** eval replay of dataset rows (live).
- **RCA:** Triage Agent [S].
- **Runtime control:** none [S].
- **Moat:** user-signal semantics such as edit and thumbs signals.
- **Weakness:** proprietary backend; thin trace schema.
- **What we should integrate:** ingest `SignalEvent` and `selfDiagnose` as verification events.
- **Unaddressed:** harness causality.
- **Pricing:** [U].

---

## 6. Judgment Labs (Judgeval)

### Data model [V] ([judgment_attribute_keys.py](https://github.com/JudgmentLabs/judgeval/blob/04a1848fb9/src/judgeval/judgment_attribute_keys.py); Apache-2.0)
- **Core span attributes:** `judgment.span_kind`, `judgment.input`, `judgment.output`, `judgment.offline_mode`, `judgment.update_id`, `judgment.customer_id`, `judgment.customer_user_id`.
- **Agent identity:** `judgment.agent_id`, `judgment.parent_agent_id`, `judgment.agent_class_name`, `judgment.agent_instance_name`, `judgment.is_agent_entry_point`.
- **Cost and state:** `judgment.cumulative_llm_cost`, **`judgment.state_before`, `judgment.state_after`**, `judgment.pending_trace_eval`.
- **Usage:** `judgment.llm.provider|model`, `judgment.usage.{non_cached_input_tokens,cache_creation_input_tokens,cache_read_input_tokens,output_tokens,total_cost_usd}`.
- **Session and links:** `judgment.session_id`, `judgment.link.{source,target}_{trace,span}_id`.
- **`TraceSpan` API model:** `organization_id, project_id, user_id, timestamp, trace_id, span_id, parent_span_id, trace_state, span_name, span_kind, service_name, resource_attributes, span_attributes, duration, status_code, status_message, events, links`.
- **`@Tracer.observe(span_type=…)`** accepts `span` (default), `tool`, `agent`, `llm`…
- **AgentJudge:** `{judge_id, name, prompt (rubric), model (LiteLLM id), score_type numeric|binary|categorical, categories, min_score, max_score, major/minor_version}`.
- **"Validate against production cases"** works through offline tests ([offline_test_runner.py](https://github.com/JudgmentLabs/judgeval/blob/04a1848fb9/src/judgeval/offline_tests/offline_test_runner.py)):
  - `TestConfig{dataset_id, judges}`; then `client.offline_tests.run(test_config, agent_function?, judge_versions[{name|judge_id, tag|version|major/minor}], dataset_version, pass_condition_fn, assert_test)`.
  - Without an agent function, the judges score each example's stored production trace (`offline_trace_id`).
  - With one, the agent reruns per example under `OfflineTracer` and the judges score the new trace.
  - Judge versions are pinned; unlisted judges default to the `prod` tag.
- **Other:** SQL over a virtual schema such as `telemetry.traces`; MCP `discover_schema`.
- **Trajectory evaluator types:** I found no dedicated trajectory-match evaluators. "Agent judges" are LLM rubric judges with trace context [V-negative].

**Rows (condensed):**
- **Thesis:** a continuous-improvement stack — judges produce "behaviors" that accumulate.
- **Session model:** `judgment.session_id`.
- **Agents:** agent and parent-agent IDs.
- **Memory and context:** `state_before` and `state_after` are the only state capture found in any vendor [V].
- **Evaluation:** versioned agent judges, online and offline.
- **Regression:** offline tests with pinned judge versions plus `assert_test` for CI.
- **Replay:** reruns the agent per example (live).
- **Integrate:** `state_before`/`state_after` and parent-agent linkage.
- **Pricing and deployment:** [U].

---

## 7. W&B Weave / CoreWeave Forge AgentLens

### Data model [V]
- **`CallSchema`** ([trace_server_interface.py](https://github.com/wandb/weave/blob/9c633e8d0d/weave/trace_server/trace_server_interface.py)): `id, project_id, op_name, display_name, trace_id, parent_id, thread_id, turn_id, started_at, attributes, inputs, ended_at, exception, output, summary, wb_user_id, wb_run_id, wb_run_step(_end), deleted_at, expire_at, storage_size_bytes`.
- **Agent spans table** (`AgentSpanSchema`, [agents/types.py](https://github.com/wandb/weave/blob/9c633e8d0d/weave/trace_server/agents/types.py)): `trace_id, span_id, parent_span_id, span_name, span_kind, status_code, operation_name, provider_name, agent_name/id/description/version, eval_*, parent_call_id, request/response_model, response_id, token columns, cost columns (input/output/cache_read/cache_creation/total_cost_usd), reasoning_content, conversation_id/name, tool_name, tool_type…`.
  - The canonical `weave.*` keys each have `gen_ai.*` aliases ([agents/semconv.py](https://github.com/wandb/weave/blob/9c633e8d0d/weave/trace_server/agents/semconv.py)): `weave.compaction.{summary,items_before,items_after}`, `weave.parent_call.{id,trace_id}`, `weave.eval.*`, `weave.reasoning_content`, `weave.artifact_refs`, `weave.content_refs`, `weave.object_refs`.
  - Server op `weave.genai.turn_ended` drives scoring events.
- **Causal ordering** ([causal_order.py](https://github.com/wandb/weave/blob/9c633e8d0d/weave/trace_server/agents/causal_order.py)): each `execute_tool` is placed right after the model span whose output named its `tool_call_id`, instead of trusting clocks across processes.
- **Insights clustering** ([041](https://github.com/wandb/weave/blob/9c633e8d0d/weave/trace_server/migrations/041_add_signature_tables.up.sql), [043](https://github.com/wandb/weave/blob/9c633e8d0d/weave/trace_server/migrations/043_add_signature_cluster_tables.up.sql), [insights/README.md](https://github.com/wandb/weave/blob/9c633e8d0d/weave/trace_server/insights/README.md)):
  - `intent_signatures (signature, category, language, sentiment, vector, conversation_id, trace_id, agent_name, turn_cost_usd…)`.
  - `failure_signatures (signature, failure_reason, category, severity, vector, current_trace_id, affected_trace_ids[], evidence_span_ids[]…)`.
  - A judge emits up to 8 signatures per turn.
  - `signature_cluster_runs (signature_type intent|failure, config SHAs, window, status)` → `signature_clusters (topic_id, centroid, label, description, occurrence_count)`.
  - Cost is attributed with apportioned and attributed math.
- **PII:** server-side `pii-v1` detectors for EMAIL_ADDRESS, PHONE_NUMBER, US_SSN, CREDIT_CARD (Luhn), plus credential redaction ([sensitive_data/detectors.py](https://github.com/wandb/weave/blob/9c633e8d0d/weave/trace_server/sensitive_data/detectors.py)).
- **Claude Code plugin** `@coreweave/forge-claude-code` on `@coreweave/forge-sdk 0.1.0-beta.0`, Apache-2.0 ([genaiSpans.ts](https://github.com/wandb/weave-claude-code/blob/483d5cba13/src/genaiSpans.ts), [hooks.json](https://github.com/wandb/weave-claude-code/blob/483d5cba13/hooks/hooks.json)):
  - **Hooks consumed (21):** SessionStart, SessionEnd, UserPromptSubmit, Stop, StopFailure, PreToolUse, PostToolUse, PostToolUseFailure, SubagentStart, SubagentStop, PermissionRequest, PermissionDenied, Notification, PreCompact, PostCompact, InstructionsLoaded, ConfigChange, WorktreeCreate, WorktreeRemove, TeammateIdle, TaskCompleted. A local daemon receives them over a socket.
  - **Span model:** Conversation (`gen_ai.conversation.id`) → Turn (`invoke_agent`) → chat spans, Tool spans (`execute_tool`), and SubAgent (`invoke_agent`). Teammates (agent teams) are correlated through `teamCoordinator`.
  - **GenAI attributes:** `gen_ai.operation.name, gen_ai.agent.name|id, gen_ai.conversation.id, gen_ai.response.model|id|finish_reasons, gen_ai.usage.input_tokens|output_tokens|cache_read.input_tokens|cache_creation.input_tokens, gen_ai.input.messages, gen_ai.output.messages, gen_ai.system_instructions, gen_ai.provider.name, error.type`.
  - **Forge extensions:** `forge.claude_code.cwd`, `forge.claude_code.source`, `forge.claude_code.plugin.version`, `forge.claude_code.orphan_reason`, `forge.claude_code.subagent.spawning_tool_call_id`, `forge.integration.name|version`, `forge.integration.meta.*`.
  - **Compaction:** `weave.compaction.summary|items_before|items_after`, set on the turn.
  - **Span events:** `forge.permission_request` (attribute `forge.permission.suggestions`) and `forge.permission_resolved` (attribute `forge.permission.approved`: bool).
  - The README says "PII scrubbing … not yet implemented".

**Rows (condensed):**
- **Thesis:** agent-native observability on OTel GenAI semconv, with CoreWeave distribution.
- **Session model:** thread_id and turn_id, conversation_id.
- **Subagents:** `invoke_agent` plus `spawning_tool_call_id` [V].
- **Context:** compaction columns [V].
- **Permissions:** span events [V].
- **Clustering:** intent and failure signatures [V].
- **Replay:** none found [U].
- **Moat:** the most complete Claude Code harness capture; GPU-cloud bundling.
- **Weakness:** one harness only; plugin SDK in beta.
- **What we should integrate:** adopt `forge.*` and `weave.compaction.*` names as normalizer inputs, and copy the causal tool ordering idea.
- **Unaddressed:** memory, verification, cross-harness coverage.

---

## 8. AgentOps

### Data model [V] ([agentops/semconv](https://github.com/AgentOps-AI/agentops/tree/f8e907b92d/agentops/semconv); MIT)
- **Span kinds:** `workflow, session, task, operation, agent, tool, llm, chain, text, guardrail, http, unknown`.
- **Event-style kinds:** `agent.action, agent.thinking, agent.decision, llm.call, workflow.step`.
- **Agent attributes:** `agent.id|name|role|tools|models|reasoning`, `tools`, `handoffs`, `from_agent`, `to_agent`.
- **Tool attributes:** `tool.id|name|description|parameters|result|status`.
- **Workflow attributes:** about 50 `workflow.*` keys, including `workflow.memory_type` and `workflow.session.*`.
- **Other:** `agentops.tags`, `trace.id`, `span.id`, `parent.id`, `group.id`.
- **LLM attributes:** legacy `gen_ai.prompt` / `gen_ai.completion` and `gen_ai.usage.prompt_tokens`.
- **Storage:** ClickHouse `otel_traces` (standard OTel exporter schema) plus Supabase.
- **"Session replay"** is a waterfall UI over spans (`session-replay.tsx`).
- **"Time travel"** is the `ttd` table from 2024 ([migration](https://github.com/AgentOps-AI/agentops/blob/f8e907b92d/app/supabase/migrations/20240802043420_add_ttd_table.sql)): `ttd_id, branch_name, session_id, llm_id, prompt jsonb, completion jsonb, model, tokens, params, returns`.
  - It stores named LLM prompt/completion overrides per branch, which amounts to LLM-call fixture overrides.
  - I found no current SDK code path for it [V-negative], so it is likely legacy.
  - Last commit was 2026-06-25, so the project looks slow-moving.

**Rows (condensed):** Thesis is agent session analytics. Replay is a visual waterfall, plus legacy LLM override branches. Moat is minimal. Treat it as a semconv source only. Do not rebuild it.

---

## 9. Entire (Thomas Dohmke)

### Data model [V] ([entireio/cli](https://github.com/entireio/cli/tree/f3f598a473), MIT, about 5.2k stars)
- **Capture:** hooks installed per agent: `.claude/settings.json`, `.cursor/hooks.json`, `.codex/hooks.json`, `.opencode/plugins/entire.ts`, `.pi/extensions/entire/index.ts`. Also Antigravity, Factory Droid, Copilot CLI, and an "external agent protocol".
- **Commit linkage:** git trailers `Entire-Checkpoint: <id>` (a 26-character ULID, or 12-hex legacy) and `Entire-Attribution: 73% agent (146/200 lines)`.
  - Commits are matched to sessions by worktree plus process-ancestry identity (`proclive`). The nearest ancestor agent wins.
- **Storage:**
  - Active state: `.git/entire-sessions/<id>.json`.
  - Ephemeral shadow branch: `entire/<commit[:7]>-<worktreeHash[:6]>`. Code snapshots there are **not redacted**.
  - Persistent store: either the `entire/checkpoints/v1` branch sharded `<id[:2]>/<id[2:]>/`, or refs `refs/entire/checkpoints/<shard>/<id>`.
- **Checkpoint tree:**
  - `metadata.json` (CheckpointSummary).
  - Per-session directories `0/`, `1/`… holding `metadata.json`, `full.jsonl` (the redacted raw transcript), `transcript.jsonl` (compacted), `prompt.txt`, `content_hash.txt`.
  - `tasks/<tool-use-id>/{agent-<agent-id>.jsonl, task.json}` for subagents.
- **Session `metadata.json` fields** ([api/checkpoint/metadata.go](https://github.com/entireio/cli/blob/f3f598a473/api/checkpoint/metadata.go)):
  - Identity: `cli_version, checkpoint_id, session_id, strategy, created_at, branch, commit_sha`.
  - Progress and files: `checkpoints_count, save_step_count, files_touched[]`.
  - Agent and turn: `agent, model, turn_id, is_task, tool_use_id`.
  - Transcript offsets: `checkpoint_transcript_start, compact_transcript_start`.
  - Usage: `token_usage{input_tokens, cache_creation_tokens, cache_read_tokens, output_tokens, api_call_count, subagent_tokens}`.
  - Skills: `skill_events_version, skill_events[]`.
  - `session_metrics{duration_ms, turn_count, context_tokens, context_window_size}`.
  - **`summary{intent, outcome, learnings{repo[], code[{path,line,end_line,finding}], workflow[]}, friction[], open_items[]}`**.
  - Attribution and review: `initial_attribution`, `prompt_attributions`, `kind`, review and investigate fields.
- **Attribution fields:** `agent_lines, agent_removed, human_added, human_modified, human_removed, total_committed, total_lines_changed, agent_percentage, metric_version`.
- **Summary-level fields:** `sessions[], token_usage, combined_attribution, has_review, has_investigation, imported`.
- **Redaction:** Betterleaks and/or goredact scanners, custom rules, optional PII, and an optional OpenAI Privacy Filter ([docs/security-and-privacy.md](https://github.com/entireio/cli/blob/f3f598a473/docs/security-and-privacy.md)).

**Rows (condensed):**
- **Thesis:** git-native provenance of agent sessions.
- **Session model:** Session to Checkpoints.
- **Subagents:** task checkpoints keyed by `tool_use_id`.
- **Context:** `context_tokens` / `context_window_size`.
- **Memory:** "learnings" as a durable artifact.
- **Verification:** none.
- **Replay:** `entire session resume` restores the transcript (no re-execution).
- **Storage:** inside the customer's own git.
- **Moat:** git-native and vendor-neutral, with a well-known founder.
- **Weakness:** no runtime telemetry or OTel; shadow branches are unredacted.
- **What we should integrate:** read the `Entire-Checkpoint` trailer and checkpoint refs to join production incidents to the session and commit that produced the code.
- **Never rebuild:** commit-provenance capture.

---

## 10. Galileo Agent Control (Splunk)

### Data model [V] (PyPI `agent-control-models` / `-sdk` / `-server` / `-evaluators` 8.11.0, Apache-2.0; repo [agentcontrol/agent-control](https://github.com/agentcontrol/agent-control); Galileo docs [concepts/agent-control/overview.mdx](https://github.com/rungalileo/docs-official/blob/fbcb642722/concepts/agent-control/overview.mdx))
- **`ControlDefinition`:** `{name, description, enabled, execution: server|sdk, scope, condition, action, tags, template?, template_values?}`.
- **`ControlScope`:** `{step_types: ["llm","tool",…], step_names[], step_name_regex (RE2), stages: ["pre","post"]}`.
- **`ConditionNode`:** a leaf is `{selector{path: "input"|"output"|"context.user_id"|"name"|"type"|"*"}, evaluator{name, config}}`; composites use `and_`, `or_`, `not_`.
- **`ControlAction`:** `{decision: deny|steer|observe, steering_context{message}}`. Legacy `allow|warn|log` become `observe`.
- **`Step`** (the object evaluated): `{type, name, input, output, context, tools}`.
- **`EvaluatorResult`:** `{matched, confidence, message, metadata, error}`.
- **`ControlMatch`:** `{control_execution_id, control_id, control_name, action, result, steering_context}`.
- **Templates:** parameter types `string|string_list|enum|boolean|regex_re2`.
- **Integration points:**
  - `@control()` decorator.
  - Integrations: Google ADK plugin, Strands plugin and steering, LangChain, CrewAI.
  - OTel sink and Galileo bridge handler.
  - Built-in evaluators: regex, list, JSON, SQL; Galileo Luna evaluators through `agent-control-evaluator-galileo`.
  - Server is Postgres plus REST plus UI.

**Rows (condensed):** Thesis is a centralized runtime guardrail plane. Runtime control is **yes**: pre/post on LLM and tool steps with deny and steer. Moat is Splunk/Cisco distribution. Weakness: it evaluates per step only, with no trajectory or state awareness. Integrate by emitting `ControlMatch` as a verification/control event in our schema, and possibly call it as an enforcement backend. Never rebuild the policy DSL; reuse or interoperate. Still unaddressed: incident-driven automatic control creation.

---

## 11. Datadog LLM / Agent Observability

### Data model [V] (DataDog/documentation `hugo/content/en/llm_observability`)
- **Span kinds** ([terms](https://github.com/DataDog/documentation/blob/addf4da61d/hugo/content/en/llm_observability/quickstart/terms/_index.md)): `llm`, `workflow`, `agent` (these three can be root), `tool`, `task`, `embedding`, `retrieval`.
- **SDK** ([sdk.md](https://github.com/DataDog/documentation/blob/addf4da61d/hugo/content/en/llm_observability/instrument/sdk.md)): `LLMObs.enable`, decorators `@llm @workflow @agent @tool @task @embedding @retrieval`, `LLMObs.annotate`, `annotation_context`, `export_span`, `submit_evaluation(_for)` with `label, metric_type, value, span, span_with_tag_value, ml_app`, `submit_feedback`, `inject_distributed_headers` / `activate_distributed_headers`, `register_processor`.
- **OTLP mapping** ([otel_instrumentation.md](https://github.com/DataDog/documentation/blob/addf4da61d/hugo/content/en/llm_observability/instrument/otel_instrumentation.md)):

| Source | Datadog field |
|---|---|
| `service.name` | `ml_app` |
| `gen_ai.operation.name`: chat, generate_content, text_completion, completion | span.kind `llm` |
| `gen_ai.operation.name`: embeddings | `embedding` |
| `gen_ai.operation.name`: execute_tool | `tool` |
| `gen_ai.operation.name`: invoke_agent, create_agent | `agent` |
| `gen_ai.operation.name`: rerank, unknown, or default | `workflow` |
| `gen_ai.provider.name`, falling back to `gen_ai.system` | `meta.model_provider` |
| `gen_ai.tool.name` | span name |
| `gen_ai.tool.call.id` | `metadata.tool_id` |
| `gen_ai.tool.definitions` | `meta.tool_definitions` |
| `gen_ai.tool.call.arguments` / `.result` | `input.value` / `output.value` |
| `gen_ai.conversation.id` | `session_id` |
| OTel span links | `span_links[]`; same-trace links are drawn as Execution Graph edges |
| `gen_ai.system_instructions` | prepended to input as system messages |

- **Insights** ([insights.md](https://github.com/DataDog/documentation/blob/addf4da61d/hugo/content/en/llm_observability/investigate/insights.md)):
  - Types: Cost (inefficient prompt caching, large tool results, verbose model output); Reliability (tool call retry loops, prompt rule violations).
  - Each insight has evidence spans, a recommended fix with validation guidance, and an investigation trail.
  - Statuses: For Review, In Progress, Completed, Ignored, Automatically Resolved. Resurfaces on recurrence. Jira/Linear links; "Fix with Bits"; MCP.
- **Patterns** ([patterns.md](https://github.com/DataDog/documentation/blob/addf4da61d/hugo/content/en/llm_observability/investigate/patterns.md)): LLM summaries, then embeddings from a self-hosted OSS model, then UMAP + HDBSCAN, then LLM topic naming.
- **Trace-level LLM judges:** templates for goal completion and tool-use correctness, using `{{spans[i].meta.…}}` variables.
- **"AI Agents Console":** not found in these docs [U].

**Rows (condensed):** Moat is APM correlation and the installed base. Replay none. Runtime control none [P]. Pricing [P]. Integrate by accepting its span-kind enum as a source vocabulary. Unaddressed: harness events, cross-trace execution graph (cross-trace links are stored but not drawn).

---

## 12. OpenLIT

### Data model [V]
- **#1685 "Align README, docs, and package metadata to agent harness engineering"**, merged 2026-10-01 (commit `897838a26e`).
  - The glossary defines the harness as "tools, context, prompts, memory, hooks, guardrails, and feedback loops" ([glossary.mdx](https://github.com/openlit/openlit/blob/897838a26e/docs/latest/concepts/glossary.mdx)).
- **Coding-agent schema** ([coding-agents-convention.md](https://github.com/openlit/openlit/blob/897838a26e/agent-guides/coding-agents-convention.md), [coding_agent.go](https://github.com/openlit/openlit/blob/897838a26e/sdk/go/semconv/coding_agent.go)):
  - **Resource:** `coding_agent.client` (cursor|claude-code|codex|windsurf), `coding_agent.session.id`, `coding_agent.agent.parent_id`, `coding_agent.content_capture_mode` (minimal|metadata_only|full), `coding_agent.hook.cli.version`, `coding_agent.signal_source` (hook|native), `code.cwd`, `vcs.repository.url.full`, `vcs.ref.head.name`, `gen_ai.user.name`, `gen_ai.conversation.id`, `terminal.type`.
  - **Span types:** `coding_agent.session` (rollups: outcome, duration_ms, cost_usd, tool_call_count, subagent_count, lines.*, edit.accept/reject_count, commit_count, pr_count, user.classification, `coding_agent.policy.permission_mode`, `coding_agent.vcs.dirty`); `coding_agent.llm.turn` (`turn.kind` prompt|response|thought, `llm.thought.text/duration_ms`); `coding_agent.tool.call` (`tool.duration_ms`, `errored`, `iteration`, `group.id`, `triggering_llm_request_id`, `mcp.server.name|scope|transport`, `sandboxed`, `command`); `coding_agent.edit.decision` (decision accept|reject|auto_accept|revert, source user_interactive|policy|hook, `edit.tool.name`, `lines.added/removed`, `code.file.path`); `coding_agent.subagent` (`subagent.type`, `agent.parent_id`, spawning `gen_ai.tool.call.id`); `coding_agent.git.commit` and `coding_agent.git.pull_request`.
  - **Events:** `coding_agent.session.start|end`, `coding_agent.subagent.spawned|completed`, `coding_agent.loop.detected` (with `coding_agent.loop.pattern` such as edit_revert_edit or tool_retry), `coding_agent.session.loop.compact`, `coding_agent.session.permission_mode_changed`, `coding_agent.skill.activated`, `coding_agent.mcp.connection`, `coding_agent.llm.turn.retry_exhausted`.
  - **Also:** `coding_agent.linkage_confidence`. Session outcome enum: completed, merged, committed, abandoned_no_change, abandoned_with_change, cancelled.
  - **Mapping from Claude Code native telemetry:** `claude_code.user_prompt`, `tool_result`, `api_request`, `api_error`, `tool_decision`, `compaction`, `permission_mode_changed`, `skill_activated`, `mcp_server_connection` events each map to canonical spans or events.
- **Python semcov** ([semcov/__init__.py](https://github.com/openlit/openlit/blob/897838a26e/sdk/python/src/openlit/semcov/__init__.py)):
  - Memory: `gen_ai.memory.{operation,type,search.query,search.top_scores,…}`.
  - Agents: `gen_ai.agent.{goal,role,task,thinking,step_count,failed_steps,memory,…}`.
  - Workflow and team: `gen_ai.workflow.*`, `gen_ai.team.*`.
  - Guardrails: `guard.{verdict,score,phase,action,denied,…}`, `gen_ai.agent.threat.*`.
  - Context: `gen_ai.framework.context.count|size`.
  - MCP: about 100 `mcp.*` keys.
  - Prompt versioning: `openlit.agent.version_hash`.
- **Harness concepts that have attributes:** tools, hooks, permissions/policy, guardrails, memory (framework-level), context (size and compaction event), subagents, prompts (version hash), VCS outcomes.
  - **No attributes for:** verification and test outcomes, or feedback loops.

**Rows (condensed):** Apache-2.0; Grafana's instrumentation path; also an eBPF controller (OBI). Moat is breadth of instrumentation plus a strict coding-agent contract. Weakness is analysis depth: no clustering or replay found. Integrate by mapping `coding_agent.*` into our normalizer. It is the closest existing thing to a harness event model.

---

## 13. Traceloop OpenLLMetry [V] ([semconv_ai](https://github.com/traceloop/openllmetry/blob/be498301c4/packages/opentelemetry-semantic-conventions-ai/opentelemetry/semconv_ai/__init__.py))
- **Attributes:** `traceloop.span.kind` (`workflow|task|agent|tool|unknown`), `traceloop.workflow.name`, `traceloop.entity.{name,path,version,input,output}`, `traceloop.association.properties.*`, `traceloop.prompt.{managed,key,version,version_name,version_hash,template,template_variables}`, `traceloop.correlation.id`.
- **Agent workflow extensions:** `gen_ai.task.{id,name,kind,input,output,parent.id,status(success|failure)}`, `gen_ai.workflow.{nodes,edges}`.
- **Custom operation names:** `execute_task`, `llm_request`, `vector_db_retrieve`.
- **Instrumentations (32):** agno, alephalpha, anthropic, bedrock, chromadb, cohere, crewai, google-generativeai, groq, haystack, lancedb, langchain, litellm, llamaindex, marqo, mcp, milvus, mistralai, ollama, openai, openai-agents, pinecone, qdrant, replicate, sagemaker, together, transformers, vertexai, voyageai, watsonx, weaviate, writer.
- **Rows:** instrumentation only; no backend analysis (Traceloop SaaS is separate [U]). Never rebuild; ingest it.

## 14. Honeycomb, Grafana, Dynatrace (attributes the agent views rely on)
- **Honeycomb Agent Timeline** [V] ([honeycombio/aws-workshop guide.md](https://github.com/honeycombio/aws-workshop/blob/main/guide.md)):
  - `gen_ai.conversation.id` groups turns; `gen_ai.agent.name` names the lane; `invoke_agent`, `chat` and `execute_tool` spans.
  - Messages panel reads `gen_ai.input.messages` / `gen_ai.output.messages` **as span attributes**. Strands needs `OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental,gen_ai_span_attributes_only`; message events do not render.
- **Dynatrace** [V] ([dt-obs-genai agent-signals.md](https://github.com/Dynatrace/dynatrace-for-ai/blob/main/skills/dt-obs-genai/references/agent-signals.md)):
  - Uses `gen_ai.operation.name` (execute_tool, invoke_agent, create_agent), `gen_ai.tool.name`, `gen_ai.agent.name`, `gen_ai.conversation.id`, `gen_ai.provider.name`, `gen_ai.request.model`, `span.status_code`.
  - Smartscape extracts a `GENAI_AGENT` entity.
  - Its collector distribution bundles `genainormalizerprocessor`.
- **Grafana Agent Observability** [V] ([grafana/agento11y llms.txt](https://github.com/grafana/agento11y/blob/main/llms.txt)):
  - Uses `gen_ai.agent.name|version`, `gen_ai.conversation.id`, `gen_ai.operation.name`, `gen_ai.provider.name`, usage keys including `gen_ai.usage.cache_read_input_tokens` / `cache_write_input_tokens`, and the metrics `gen_ai.client.token.usage`, `gen_ai.client.operation.duration`, `gen_ai.client.time_to_first_token`, `gen_ai.client.tool_calls_per_operation`.
  - Extensions: `agento11y.generation.id`, `agento11y.generation.parent_generation_ids`, `agento11y.framework.name`, `agento11y.gen_ai.request.thinking.*`.
  - Coding-agent plugins: Claude Code, Codex, Copilot CLI, Cursor, OpenCode, Pi, Vibe, Kiro.

## 15. Reference: OTel GenAI semconv (development stability) and the upstream normalizer [V]
- **Registry** ([registry.yaml](https://github.com/open-telemetry/semantic-conventions-genai/blob/e07f4ebacb/model/gen-ai/registry.yaml)):
  - `gen_ai.operation.name` values: `chat, generate_content, text_completion, embeddings, retrieval, execute_tool, create_agent, invoke_agent, invoke_workflow, plan, create_memory, search_memory, update_memory, upsert_memory, delete_memory, create_memory_store, delete_memory_store, fetch_response`.
  - Agents: `gen_ai.agent.{id,name,description,version}`, `gen_ai.main_agent.{id,name,description}`.
  - Conversation: `gen_ai.conversation.{id,compacted}`.
  - Tools: `gen_ai.tool.{name,type,description,definitions,call.id,call.arguments,call.result}`.
  - Skills: `gen_ai.skill.{name,description,resource.name,source.uri}`; skill spans `gen_ai.execute_tool.load_skill.internal`, `read_skill_resource.internal`, `command.internal`.
  - Memory: `gen_ai.memory.{store.id,record.id,record.count,records,query.text}`.
  - Retrieval, evaluation and prompts: `gen_ai.retrieval.*`, `gen_ai.evaluation.{name,score.value,score.label,explanation}`, `gen_ai.prompt.{name,version,variable}`, `gen_ai.workflow.name`, `gen_ai.data_source.id`.
  - Response: `gen_ai.response.status`, `gen_ai.request.reasoning.level`.
  - MCP: `mcp.method.name`, `mcp.session.id`, `mcp.protocol.version`, `mcp.resource.uri`.
- **`genainormalizerprocessor`** (alpha, [contrib](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/processor/genainormalizerprocessor)):
  - Built-in sources `openinference` and `openllmetry`, plus user-defined `mappings` and `value_mappings`; type coercion; targets schema `1.40.0`.
  - OpenInference kinds to operation names: LLM→chat, EMBEDDING→embeddings, CHAIN→invoke_agent, RETRIEVER and RERANKER→retrieval, TOOL→execute_tool, AGENT→invoke_agent, PROMPT→text_completion.
  - Other OpenInference renames: `agent.name`→`gen_ai.agent.name`, `session.id`→`gen_ai.conversation.id`.
  - Traceloop kinds: workflow→invoke_workflow, task and agent→invoke_agent, tool→execute_tool.
  - Other Traceloop renames: `traceloop.entity.name`→`gen_ai.agent.name`, `traceloop.entity.input/output`→`gen_ai.input/output.messages`.

---

## 16. Schema union for the normalizer (grouped by concept)

| Concept | Canonical target (OTel GenAI where it exists) | Vendor names to map in |
|---|---|---|
| Trace / span / parent | OTel `trace_id`, `span_id`, `parent_span_id` | LangSmith `trace_id`/`id`/`parent_run_id`/`dotted_order`/`langsmith.span.{id,parent_id,dotted_order}`/`langsmith.trace.id`; Langfuse `traceId`/`id`/`parentObservationId`/`langfuse.internal.as_root`/`is_app_root`; Phoenix `parent_id`; Laminar `lmnr.span.path`/`ids_path`/`parent_ids_path`; Weave `trace_id`/`parent_id`/`weave.parent_call.{id,trace_id}`; AgentOps `trace.id`/`span.id`/`parent.id`/`group.id`; Judgment `judgment.link.*`; Datadog `parent_id`/`span_links[]`; Grafana `agento11y.generation.parent_generation_ids` |
| Span kind / operation | `gen_ai.operation.name` | LangSmith `run_type`/`langsmith.span.kind` (llm, chain, tool, retriever, embedding, prompt, parser); Langfuse `type`/`langfuse.observation.type` (10 values); OpenInference `openinference.span.kind` (12 values incl. DECISION); Laminar `lmnr.span.type`/`span_type` (DEFAULT, LLM, TOOL, EXECUTOR, EVALUATOR, EVALUATION, HUMAN_EVALUATOR, EVENT, CACHED); Traceloop `traceloop.span.kind` (workflow, task, agent, tool); AgentOps span kinds plus `agent.action`/`agent.thinking`/`agent.decision`; Judgment `judgment.span_kind`; Datadog `meta.span.kind` (7 kinds); OpenLIT `coding_agent.llm.turn`/`tool.call`/`edit.decision`/`subagent`/`git.*`; Weave `weave.operation.name` |
| Session / conversation / thread | `gen_ai.conversation.id` | LangSmith metadata `thread_id`/`session_id`/`conversation_id`; Langfuse `session.id`/`langfuse.session.id`; OpenInference `session.id`; Laminar `lmnr.association.properties.session_id`; Weave `thread_id`/`weave.conversation.{id,name}`; Raindrop `convoId`; Judgment `judgment.session_id`; Datadog `session_id`; OpenLIT `coding_agent.session.id`; AgentOps `workflow.session_id`; Entire `session_id`; MCP `mcp.session.id` |
| Turn | (none) | Weave `turn_id` and `weave.genai.turn_ended`; LangSmith root run with `ls_agent_type=root`; Entire `turn_id`/`turn_count`; Forge Turn = `invoke_agent`; OpenLIT `coding_agent.llm.turn.kind` |
| Project / app / environment | `service.name`, `deployment.environment.name` | LangSmith `session_name`/`address lrn:agents/…/environments/…`; Langfuse `langfuse.environment`/`release`/`version`; Datadog `ml_app`; Raindrop `raindrop.project_id`; Judgment `judgment.project_id` |
| Agent identity | `gen_ai.agent.{id,name,description,version}`, `gen_ai.main_agent.*` | LangSmith `ls_agent_runtime`/`ls_agent_version`/`ls_integration`/`ls_agent_purpose`; OpenInference `agent.name`; AgentOps `agent.{id,name,role,tools,models}`; Judgment `judgment.agent_{id,class_name,instance_name}`/`is_agent_entry_point`; Laminar `lmnr.span.agent_hash` (inferred); Weave `weave.agent.*`; Raindrop `raindrop.agent.role`; OpenLIT `coding_agent.client`/`coding_agent.agent.{id,type}`; Forge `forge.integration.{name,version}`; Traceloop `traceloop.entity.name` |
| Subagent / handoff | (none; nested `invoke_agent`) | LangSmith `ls_agent_type=subagent`, `ls_subagent_id`, `ls_subagent_type`; Forge `forge.claude_code.subagent.spawning_tool_call_id`; OpenLIT `coding_agent.agent.parent_id`, `subagent.type`, `subagent.spawned/completed`, `linkage_confidence`; Raindrop `raindrop.handoff.{parentEventId,childEventId,parentSpanId,mode,name,terminal}`; Judgment `judgment.parent_agent_id`; AgentOps `handoffs`/`from_agent`/`to_agent`; OpenInference `graph.node.{id,parent_id,name}`; Entire `is_task`/`tool_use_id`/`tasks/<id>`; Traceloop `gen_ai.task.parent.id` |
| Tool | `gen_ai.tool.{name,type,description,definitions,call.id,call.arguments,call.result}` | LangSmith `ls_tool_name`; Langfuse `tool_definitions`/`tool_calls`/`tool_call_names`; OpenInference `tool.*`, `tool_call.*`, `llm.tools`, `message.tool_call_id`; Laminar `span_type=TOOL`; AgentOps `tool.{id,name,parameters,result,status}`; OpenLIT `coding_agent.tool.{duration_ms,errored,iteration,group.id,triggering_llm_request_id,sandboxed,command}`/`gen_ai.tool.*`; Raindrop `ai.prompt.tools`, `toolCalls[]`; Traceloop `llm.request.functions.*`; Datadog `metadata.tool_id`, `meta.tool_definitions` |
| MCP | `mcp.method.name`, `mcp.session.id`, `mcp.resource.uri` | OpenLIT `coding_agent.mcp.{server.name,scope,transport}` plus ~100 `mcp.*`; Traceloop `mcp.request.*`/`mcp.response.value` |
| Skills | `gen_ai.skill.*`, skill spans | OpenLIT `coding_agent.skill.activated`; Entire `skill_events[]` |
| LLM model / provider | `gen_ai.provider.name`, `gen_ai.request.model`, `gen_ai.response.model` | `gen_ai.system`; LangSmith `ls_provider`/`ls_model_name`; OpenInference `llm.provider`/`llm.system`/`llm.model_name`; Judgment `judgment.llm.{provider,model}`; Langfuse `langfuse.observation.model.name`; Datadog `meta.model_provider/model_name` |
| Messages / IO | `gen_ai.input.messages`, `gen_ai.output.messages`, `gen_ai.system_instructions` | `gen_ai.prompt(.n.*)`, `gen_ai.completion(.n.*)`; OpenInference `input.value`/`output.value`/`llm.input_messages`/`llm.output_messages`; Langfuse `langfuse.observation.input/output`; Laminar `lmnr.span.input/output`; Traceloop `traceloop.entity.input/output`; Judgment `judgment.input/output`; Raindrop `userInput`/`assistantOutput`; Weave `inputs`/`output`; MLflow `mlflow.spanInputs/Outputs` |
| Reasoning | `gen_ai.usage.reasoning.output_tokens` | `weave.reasoning_content`; OpenLIT `coding_agent.llm.thought.{text,duration_ms}`; AgentOps `agent.thinking`/`agent.reasoning`; Raindrop `afterAgentThought` hook |
| Usage / tokens | `gen_ai.usage.{input_tokens,output_tokens,cache_read.input_tokens,cache_write.input_tokens,reasoning.output_tokens}` | Variant cache names: `cache_creation.input_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens`, `cache.read_input_tokens`. Deprecated `gen_ai.usage.prompt_tokens`/`completion_tokens`. OpenInference `llm.token_count.*`. Raindrop `raindrop.usage.*`. Judgment `judgment.usage.*`. Entire `token_usage{…, subagent_tokens}` |
| Cost | (none standard) | `gen_ai.usage.cost`/`input_cost`/`output_cost`; Langfuse `cost_details`; LangSmith `total_cost`; Weave `*_cost_usd`; Judgment `judgment.usage.total_cost_usd`/`cumulative_llm_cost`; OpenInference `llm.cost.*`; OpenLIT `coding_agent.session.cost_usd` |
| Context / compaction | `gen_ai.conversation.compacted` (bool) | LangSmith `ls_agent_type=compaction`; Weave `weave.compaction.{summary,items_before,items_after}`; OpenLIT `coding_agent.session.loop.compact` event, `gen_ai.framework.context.{count,size}`, `gen_ai.request.context_window`; Entire `session_metrics.context_tokens`/`context_window_size`; hooks PreCompact/PostCompact/preCompact; Laminar system-prompt dedup |
| Memory | `gen_ai.operation.name ∈ {create,search,update,upsert,delete}_memory`, `gen_ai.memory.{store.id,record.id,record.count,records,query.text}` | OpenLIT `gen_ai.memory.{operation,type,search.query,search.top_scores,…}`; AgentOps `workflow.memory_type`; Judgment `judgment.state_before`/`state_after`; Entire `summary.learnings` |
| Prompt version | `gen_ai.prompt.{name,version}` | Langfuse `langfuse.observation.prompt.{name,version}`; Traceloop `traceloop.prompt.*`; OpenInference `llm.prompt_template.*`; OpenLIT `openlit.agent.version_hash`; Laminar `lmnr.span.prompt_hash`, `system_prompt_versions` |
| Permission / policy / control | (none) | Forge events `forge.permission_request` (`forge.permission.suggestions`) and `forge.permission_resolved` (`forge.permission.approved`); OpenLIT `coding_agent.policy.permission_mode`, `session.permission_mode_changed`, `edit.decision(.source)`; Phoenix `pxi.approval.decision`; Agent Control `ControlMatch{control_id,control_name,action deny/steer/observe,result{matched,confidence}}`; OpenLIT `guard.{verdict,action,denied,phase}`; Langfuse `GUARDRAIL`; LangSmith Engine `__engine_validation_replay__` |
| Verification / evaluation | `gen_ai.evaluation.{name,score.value,score.label,explanation}` | LangSmith feedback `{key,score,value,comment,correction,feedback_source}`; Langfuse score `{name,value,dataType,source,configId}`; Phoenix annotation `{name,label,score,explanation,annotator_kind}` and `annotation.*`/`evaluation.*`; Datadog `submit_evaluation{label,metric_type,value}`; Judgment ScorerData/AgentJudge; Raindrop `SignalEvent`/`selfDiagnose`; Laminar `signal_events{payload,severity}`; Engine `engine_issue_validation` |
| Error / status | OTel `status.code`, `error.type` | Langfuse `level`/`statusMessage`; LangSmith `error`/`status`; Datadog `meta.error.*`; OpenLIT `coding_agent.tool.errored`; Raindrop `errorSpans[]`; Phoenix `cumulative_error_count`; Traceloop `gen_ai.task.status` |
| Loop / failure patterns | (none) | OpenLIT `coding_agent.loop.{detected,pattern}`; Datadog Insight "tool call retry loops"; Weave `failure_signatures`; Laminar signals and clusters; Engine issues; Raindrop Stumbles [S] |
| Session outcome | (none) | OpenLIT `coding_agent.session.outcome` (completed, merged, committed, abandoned_*, cancelled); Entire `summary.{intent,outcome,friction,open_items}`; LangSmith `interrupted` run type |
| Code / VCS | `vcs.repository.url.full`, `vcs.ref.head.name`, `code.file.path` | LangSmith `git_branch`, `git_commit_sha`, `git_repo_url`, `working_directory`; Raindrop `raindrop.app.{commit_sha,branch,commit_dirty}`; OpenLIT `code.cwd`, `coding_agent.vcs.dirty`, `git.commit.sha`, `git.pull_request.url`; Forge `forge.claude_code.cwd`; Entire trailers `Entire-Checkpoint`/`Entire-Attribution` and `files_touched`/attribution fields |
| Replay / debug | (none) | Laminar `replay_trace_id`, `cache_until`, `lmnr.association.properties.rollout_session_id`, `lmnr.internal.checkpoint`; Raindrop `raindrop.replay.row`; Engine `__engine_validation_replay__`/`X-LangSmith-Source: engine`; AgentOps `ttd{ttd_id,branch_name,llm_id}`; Judgment `judgment.offline_mode`/`offline_trace_id` |
| Experiments / datasets | (none) | Langfuse `langfuse.experiment.*`; Weave `weave.eval.*`; LangSmith `reference_example_id`/`source_run_id`; Phoenix `DatasetExample.span_rowid`/`ExperimentRun.trace_id`; Raindrop `raindrop.eval_correlation_id` |
| Issues / clusters | (none) | Engine issue `{id,name,description,severity,session_id,url}` and trace link; Laminar `signal_event_clusters{name,level,parent_id,num_signal_events}`; Weave `signature_clusters{label,description,occurrence_count}`; Datadog Insight `{type,severity,status}`; Raindrop Signal/SignalGroup |

---

## 17. Implications for us (short)

- **Wedge.** Build a normalizer whose canonical layer is OTel GenAI. Use `genainormalizerprocessor` for OpenInference and OpenLLMetry rather than competing with it. Add mappings for the harness namespaces nobody normalizes across vendors: `coding_agent.*`, `forge.*`, `weave.compaction.*`, `ls_agent_type`, `raindrop.handoff.*`, `judgment.state_*`, and Agent Control `ControlMatch`.
  - Then propose upstream the missing concepts: permission, verification outcome, turn, session outcome, loop.
- **Replay positioning.** Laminar covers prefix LLM caching for a dev loop. LangSmith covers input replay against deployments. Nobody yet offers tool/environment fixture replay, branching from step N in production runs, or replay across frameworks.
- **Watch next:** ATIF ("ATIF to trace conversion", Phoenix #12170, not yet resolved), the OTel memory and plan operations, and Engine's replay beta going GA.
- **Not verified:** Arize Signal exact fields, Raindrop Issues object, Datadog "Agents Console", and pricing for Raindrop, Judgment, Weave and Datadog. Docs sites were blocked or my search budget ran out.

Scratch clones are under `/tmp/claude-0/-home-user-Tracelyt/759a35a9-2e36-5f3a-a868-84fb22c157ad/scratchpad/r/` and `/rd`, `/ac` if you want to re-check anything. I created no files in the project repo.