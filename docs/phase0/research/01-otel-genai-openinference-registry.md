# Exact-field reference: OTel GenAI semantic conventions, OpenInference, and how they map (as of 2026-10-04)

Everything below comes from primary sources. I cloned the following:

- **OTel GenAI conventions:** `open-telemetry/semantic-conventions-genai`, `main` at commit `e07f4ebacb08f56db8c4c882d117720333fbca04` (2026-10-02 17:35 UTC).
- **OpenInference:** `Arize-ai/openinference`, `main` at commit `19363a0a6d978b8200ed5f73a00609f3f6cdf772` (2026-10-02 20:38 UTC).
- **Upstream OTel semconv:** `open-telemetry/semantic-conventions` at tag `v1.44.0`, sparse checkout of `model/gen-ai`, `model/mcp`, `model/openai` and `docs/gen-ai`, used for deprecation and "moved" context.

File paths are relative to each repo root. The equivalent raw URL for any file is `https://raw.githubusercontent.com/<owner>/<repo>/main/<path>`.

**What I could not fetch:**
- **GitHub REST/GraphQL API for the OTel repo:** refused, because the repo is not attached to this session. `gh api` and the GitHub MCP tools returned 403 or access denied. Plain `curl` of github.com issue pages returned 403 from the proxy.
- **Issue and PR pages:** I read them through WebFetch, which renders the HTML and summarises it with a small model. Titles, authors, dates, states and linked PRs are reliable. **Comment lists may be incomplete: WebFetch reported "no comments" on most issues, and I could not cross-check that through the API.**
- **PR diffs:** for PRs #445, #483 and #535 I fetched the branches with anonymous `git fetch origin pull/N/head`, so the attribute names quoted for those PRs are exact.
- **Issue templates:** `issues/new/choose` rendered as a sign-in page. Neither the repo nor `open-telemetry/.github` (cloned) contains an `ISSUE_TEMPLATE` directory.

---

# PART A — OpenTelemetry GenAI semantic conventions (`open-telemetry/semantic-conventions-genai`)

## A.0 Repo layout, status and migration context

- **Files read:**
  - Model: `model/manifest.yaml`, `model/gen-ai/{registry,spans,events,metrics,token-metrics,entities}.yaml`, `model/gen-ai/*.json` (8 JSON schemas), `model/mcp/{registry,common,spans,metrics}.yaml`, `model/openai/registry.yaml`, `model/aws-bedrock/registry.yaml`
  - Docs: `docs/gen-ai/*.md`, `docs/registry/attributes/*.md`, `docs/registry/entities/gen-ai.md`
  - Process: `reference/reports/*.md`, `CHANGELOG.md`, `changelog.d/*.md`, `CONTRIBUTING.md`, `RELEASING.md`, `.github/CODEOWNERS`, `.github/POLICIES.md`, `.github/PULL_REQUEST_TEMPLATE.md`, `.github/LABELS.md`, `versions.env`, `Makefile`, `README.md`
- **Every attribute, span, event, metric and entity in this repo has `stability: development`.**
  - Referenced core attributes (`error.type`, `server.*`, `exception.*`) are Stable.
  - Every doc page carries "Status: Development".
- **Migration:** at upstream `open-telemetry/semantic-conventions@v1.44.0`, every `gen_ai.*`, `mcp.*` and `openai.*` attribute is marked deprecated in:
  - `model/gen-ai/deprecated/registry-deprecated.yaml`
  - `model/mcp/deprecated/registry-deprecated.yaml`
  - `model/openai/deprecated/registry-deprecated.yaml`

  The note is "Moved to the OpenTelemetry GenAI semantic conventions repository", and `docs/gen-ai/README.md` upstream is titled "Moved: Generative AI semantic conventions".
- **Truly deprecated or removed upstream:**

  | Upstream attribute | Status |
  |---|---|
  | `gen_ai.system` | Replaced by `gen_ai.provider.name` |
  | `gen_ai.usage.prompt_tokens` | Replaced by `gen_ai.usage.input_tokens` |
  | `gen_ai.usage.completion_tokens` | Replaced by `gen_ai.usage.output_tokens` |
  | `gen_ai.prompt`, `gen_ai.completion` | Obsoleted: "Removed, no replacement at this time." |
  | `gen_ai.openai.request.seed` | Replaced by `gen_ai.request.seed` |
  | `gen_ai.openai.request.response_format` | Replaced by `gen_ai.output.type` |
  | `gen_ai.openai.request.service_tier` | Replaced by `openai.request.service_tier` |
  | `gen_ai.openai.response.service_tier` | Replaced by `openai.response.service_tier` |
  | `gen_ai.openai.response.system_fingerprint` | Replaced by `openai.response.system_fingerprint` |

- **`gen_ai.token.type` is gone from the new repo.** `changelog.d/374.breaking.md`: "Replace the `gen_ai.client.token.usage` histogram (and the `gen_ai.token.type` attribute it relied on) with separate per-direction, per-operation token usage histograms".
  - Old enum members (as they appear in the PR-base diff context): `input` ("Input tokens (prompt, input, etc.)") and `output` ("Output tokens (completion, response, etc.)").
  - The replacement dimension is `gen_ai.token.modality`.
- **Other renames:** `changelog.d/289.breaking.md` renames `gen_ai.usage.cache_creation.input_tokens` to `gen_ai.usage.cache_write.input_tokens`. `changelog.d/363.deprecation.md` deprecates `gen_ai.output.messages[].finish_reason` in favour of `gen_ai.response.finish_reasons`.
- **Dependency:** `model/manifest.yaml` depends on `https://opentelemetry.io/schemas/1.44.0` (`open-telemetry/semantic-conventions.git@v1.44.0[model]`). Weaver is pinned at `v0.26.1` in `versions.env`.

## A.1 Attribute registry: all 79 `gen_ai.*` attributes

Source: `model/gen-ai/registry.yaml` (rendered at `docs/registry/attributes/gen-ai.md`). All are `stability: development`. Types are weaver types (`any` means a complex/structured value with a JSON schema annotation).

### A.1.1 Provider, operation and output

**`gen_ai.provider.name`** — enum (open: custom values allowed).
- Brief: "The Generative AI provider as identified by the client or server instrumentation."
- Notes:
  - It "acts as a discriminator that identifies the GenAI telemetry format flavor specific to that provider".
  - It "SHOULD be set based on the instrumentation's best knowledge and may differ from the actual upstream provider".
- Members (id = value, all development):

  | Value | Definition |
  |---|---|
  | `openai` | OpenAI |
  | `gcp.gen_ai` | "Any Google generative AI endpoint"; may be used when the specific backend is unknown |
  | `gcp.vertex_ai` | Vertex AI; "Used when accessing the 'aiplatform.googleapis.com' endpoint." |
  | `gcp.gemini` | Gemini; "Used when accessing the 'generativelanguage.googleapis.com' endpoint. Also known as the AI Studio API." |
  | `anthropic` | Anthropic |
  | `cohere` | Cohere |
  | `azure.ai.inference` | Azure AI Inference |
  | `azure.ai.openai` | Azure OpenAI |
  | `ibm.watsonx.ai` | IBM Watsonx AI |
  | `aws.bedrock` | AWS Bedrock |
  | `perplexity` | Perplexity |
  | `x_ai` | xAI |
  | `deepseek` | DeepSeek |
  | `groq` | Groq |
  | `mistral_ai` | Mistral AI |
  | `moonshot_ai` | Moonshot AI |

**`gen_ai.operation.name`** — enum, open. Brief: "The name of the operation being performed."
- Note: if a predefined value applies but the system uses a different name, it is RECOMMENDED to document it in system-specific conventions and use the system-specific name; otherwise use the predefined value.

| Member | Brief |
|---|---|
| `chat` | Chat completion operation such as OpenAI Chat API |
| `generate_content` | Multimodal content generation operation such as Gemini Generate Content |
| `text_completion` | Text completions operation such as OpenAI Completions API (Legacy) |
| `embeddings` | Embeddings operation such as OpenAI Create embeddings API |
| `retrieval` | Retrieval operation such as OpenAI Search Vector Store API |
| `fetch_response` | Fetch a previously generated model response by its identifier, without performing inference, such as OpenAI Get a model response. Note: "Instrumentations SHOULD NOT report token usage (as attributes or metrics) for this operation." |
| `create_agent` | Create GenAI agent |
| `invoke_agent` | Invoke GenAI agent |
| `execute_tool` | Execute a tool |
| `invoke_workflow` | Invoke GenAI workflow |
| `plan` | Agent planning or task decomposition phase |
| `search_memory` | Search/query memories from a memory store |
| `create_memory` | Create new memory records |
| `update_memory` | Update existing memory records |
| `upsert_memory` | Create or update memory records without the caller choosing which |
| `delete_memory` | Delete memory records |
| `create_memory_store` | Create or initialize a memory store |
| `delete_memory_store` | Delete or deprovision a memory store |

**`gen_ai.output.type`** — enum. Brief: "Represents the content type requested by the client."
- Members:
  - `text` — Plain text
  - `json` — JSON object with known or unknown schema
  - `image` — Image
  - `speech` — Speech
- Note: it specifies the output modality, not the actual output format. Future details may go in `gen_ai.output.{type}.*`.

**`gen_ai.data_source.id`** — string. Brief: "The data source identifier." Example `H7STPQYOND`.
- Note: it "SHOULD match the identifier used by the GenAI system rather than a name specific to the external storage". It MAY be combined with `db.*`.

### A.1.2 Request (`gen_ai.request.*`)

| Attribute | Type | Brief (verbatim) | Examples |
|---|---|---|---|
| `gen_ai.request.model` | string | The name of the GenAI model a request is being made to. | `gpt-4` |
| `gen_ai.request.max_tokens` | int | The maximum number of tokens the model generates for a request. | `100` |
| `gen_ai.request.choice.count` | int | The target number of candidate completions to return. | `3` |
| `gen_ai.request.temperature` | double | The temperature setting for the GenAI request. | `0.0` |
| `gen_ai.request.top_p` | double | The top_p sampling setting for the GenAI request. | `1.0` |
| `gen_ai.request.top_k` | **int** | The top-K sampling setting for the GenAI request: restricts token generation at each step to the K most likely next tokens. Note: decoding parameter (Anthropic `top_k`, Cohere `k`, Google `topK`); OpenAI `top_logprobs` "MUST NOT be reported as `gen_ai.request.top_k`". This was double upstream (changelog 270). | `40` |
| `gen_ai.request.stop_sequences` | string[] | List of sequences that the model will use to stop generating further tokens. | `[forest, lived]` |
| `gen_ai.request.frequency_penalty` | double | The frequency penalty setting for the GenAI request. | `0.1` |
| `gen_ai.request.presence_penalty` | double | The presence penalty setting for the GenAI request. | `0.1` |
| `gen_ai.request.encoding_formats` | string[] | The encoding formats requested in an embeddings operation, if specified. | `['base64']`, `['float','binary']` |
| `gen_ai.request.seed` | int | Requests with same seed value more likely to return same result. | `100` |
| `gen_ai.request.stream` | boolean | Indicates whether the GenAI request was made in streaming mode. | — |
| `gen_ai.request.reasoning.level` | string | The reasoning or thinking effort level requested for a GenAI model. Note: SHOULD be the exact string sent to the provider. | `low`, `medium`, `high` |
| `gen_ai.request.previous_response.id` | string | The unique identifier of a previous response or interaction used to provide context for the current operation. Covers OpenAI `previous_response_id` and Google `previous_interaction_id`. | `resp_0123456789aBCdef`, `interaction-123` |
| `gen_ai.request.stream_cursor` | string | The cursor identifying the last streamed event already received, used to resume a streamed response from that position. Covers OpenAI `starting_after` and Google `last_event_id`. | `42`, `event-abc123` |

### A.1.3 Response (`gen_ai.response.*`)

| Attribute | Type | Brief | Examples |
|---|---|---|---|
| `gen_ai.response.id` | string | The unique identifier for the completion. | `chatcmpl-123` |
| `gen_ai.response.model` | string | The name of the model that generated the response. | `gpt-4-0613` |
| `gen_ai.response.finish_reasons` | string[] | Array of reasons the model stopped generating tokens, corresponding to each generation received. Note: positional per choice; if an expected reason was not received, report `error` for that position. | `[stop]`, `[stop, length]`, `[stop, length, error]` |
| `gen_ai.response.status` | enum | The lifecycle status of a generated response, as reported by the provider when the response is fetched or polled. Distinct from `finish_reasons`. | `completed`, `in_progress` |
| `gen_ai.response.time_to_first_chunk` | double | Time to first chunk in a streaming response, measured from request issuance, in seconds. | `0.5`, `1.2` |

`gen_ai.response.status` members:

| Member | Definition |
|---|---|
| `queued` | Accepted but generation has not started |
| `in_progress` | Still being generated |
| `completed` | Finished successfully |
| `incomplete` | Stopped before completion, e.g. token limit or content filter |
| `failed` | Generation failed with an error |
| `cancelled` | Cancelled before it completed |

There is no enum for `finish_reasons` on the attribute. The output-message JSON schema defines a `FinishReason` enum (now deprecated) with values `stop`, `length`, `content_filter`, `tool_call`, `compaction`, `error`.

### A.1.4 Usage (`gen_ai.usage.*`) and `gen_ai.token.modality`

All types are int.

| Attribute | Brief | Example |
|---|---|---|
| `gen_ai.usage.input_tokens` | The number of tokens used in the GenAI input (prompt). SHOULD include all input types, including cached. Report billed counts when both billed and consumed counts exist (Cohere). | 100 |
| `gen_ai.usage.cache_read.input_tokens` | The number of input tokens served from a provider-managed cache. (Included in input_tokens) | 50 |
| `gen_ai.usage.cache_write.input_tokens` | The number of input tokens written to a provider-managed cache. | 25 |
| `gen_ai.usage.text.input_tokens` | The number of text input tokens. | 100 |
| `gen_ai.usage.image.input_tokens` | The number of image input tokens. | 258 |
| `gen_ai.usage.audio.input_tokens` | The number of audio input tokens. | 120 |
| `gen_ai.usage.output_tokens` | The number of tokens used in the GenAI response (completion). | 180 |
| `gen_ai.usage.reasoning.output_tokens` | The number of output tokens used for reasoning (e.g. chain-of-thought, extended thinking). | 50 |
| `gen_ai.usage.text.output_tokens` | The number of text output tokens. | 180 |
| `gen_ai.usage.image.output_tokens` | The number of image output tokens. | 1290 |
| `gen_ai.usage.audio.output_tokens` | The number of audio output tokens. | 240 |
| `gen_ai.usage.text.cache_read.input_tokens` | The number of text input tokens served from a provider-managed cache. | 40 |
| `gen_ai.usage.image.cache_read.input_tokens` | The number of image input tokens served from a provider-managed cache. | 128 |
| `gen_ai.usage.audio.cache_read.input_tokens` | The number of audio input tokens served from a provider-managed cache. | 60 |

**`gen_ai.token.modality`** — enum. Brief: "The modality of the tokens being counted."
- Members: `text` (Text tokens), `image` (Image tokens), `audio` (Audio tokens), `unknown` (The modality is not known).
- Note: use `unknown` when the provider gives no breakdown.

### A.1.5 Conversation, agent, main agent, workflow and skill

| Attribute | Type | Brief | Examples |
|---|---|---|---|
| `gen_ai.conversation.id` | string | The unique identifier for a conversation (session, thread), used to store and correlate messages within this conversation. Only populate when an identifier is readily available. "a new UUID, a trace identifier, or a hash of request content SHOULD NOT be used as a fallback value." | `conv_5j66UpCpwteGg4YSxUnt7lPY` |
| `gen_ai.conversation.compacted` | boolean | Indicates whether the effective conversation context used for this operation is a compacted view of a prior conversation. Note: positive indicator only — set `true` only when reliably determined; "SHOULD NOT set it to `false`". | `true` |
| `gen_ai.agent.id` | string | The unique and stable identifier of the GenAI hosted agent resource. "It's NOT RECOMMENDED to record in-memory agent instance ids". | `asst_5j66UpCpwteGg4YSxUnt7lPY`, `arn:aws:bedrock:us-east-1:123:agent/42`, `urn:agent:projects-123:...:reasoningEngines:456` |
| `gen_ai.agent.name` | string | Human-readable name of the GenAI agent provided by the application. | `Math Tutor`, `Fiction Writer` |
| `gen_ai.agent.description` | string | Free-form description of the GenAI agent provided by the application. | `Helps with math problems` |
| `gen_ai.agent.version` | string | The version of the GenAI agent. | `1.0.0`, `2025-05-01` |
| `gen_ai.main_agent.id` | string | The unique and stable identifier of the top-level Generative AI agent in the process. "MUST NOT generate ... from an in-memory or process-local identifier." | as `gen_ai.agent.id` |
| `gen_ai.main_agent.name` | string | The human-readable name of the top-level Generative AI agent in the process. (A2A Agent Card `name`) | `Math Tutor` |
| `gen_ai.main_agent.description` | string | The free-form description of the top-level Generative AI agent in the process. (A2A Agent Card `description`) | |
| `gen_ai.workflow.name` | string | Human-readable name of the GenAI workflow provided by the application. MUST be low cardinality; must not be captured by default if no meaningful name exists (e.g. not "StateGraph"). | `multi_agent_rag`, `customer_support_pipeline` |
| `gen_ai.skill.name` | string | The name of the Agent Skill. | `code-review`, `pdf-processing` |
| `gen_ai.skill.description` | string | The description of the Agent Skill. (sensitive) | |
| `gen_ai.skill.source.uri` | string | The source URI for loading the skill. (sensitive; scrub credentials) | `https://skills.example.com/code-review`, `gs://...`, `file:///opt/skills/code-review` |
| `gen_ai.skill.resource.name` | string | The skill-relative name of the resource (script, reference, or asset) being accessed or executed. | `references/review_policy.md` |

### A.1.6 Tools

| Attribute | Type | Brief | Examples |
|---|---|---|---|
| `gen_ai.tool.name` | string | Name of the tool utilized by the agent. | `Flights` |
| `gen_ai.tool.call.id` | string | The tool call identifier. | `call_mszuSIzqtI65i1wAUOE8w5H4` |
| `gen_ai.tool.description` | string | The tool description. (sensitive) | `Multiply two numbers` |
| `gen_ai.tool.type` | string (not an enum) | Type of the tool utilized by the agent. Note defines: Extension (agent-side, calls external APIs), Function (client-side; agent generates params, client executes), Datastore (retrieval / knowledge). | `function`, `extension`, `datastore` |
| `gen_ai.tool.call.arguments` | any (`gen-ai-tool-call-arguments.json`) | Parameters passed to the tool call. Expected object; best-effort deserialize strings. | `{"location":"San Francisco?","date":"2025-10-01"}` |
| `gen_ai.tool.call.result` | any (`gen-ai-tool-call-result.json`) | The result returned by the tool call (if any and if execution was successful). | `{"temperature_range":{...},"conditions":"sunny"}` |
| `gen_ai.tool.definitions` | any (`gen-ai-tool-definitions.json`) | The list of tool definitions available to the GenAI agent or model. Non-required properties NOT RECOMMENDED by default. | function tool example |

### A.1.7 Retrieval, embeddings and memory

| Attribute | Type | Brief | Examples |
|---|---|---|---|
| `gen_ai.embeddings.dimension.count` | int | The number of dimensions the resulting output embeddings should have. | 512, 1024 |
| `gen_ai.retrieval.documents` | any (`gen-ai-retrieval-documents.json`) | The documents retrieved. | `[{"id":"doc_123","score":0.95},...]` |
| `gen_ai.retrieval.query.text` | string | The query text used for retrieval. (sensitive) | `What is the capital of France?` |
| `gen_ai.retrieval.top_k` | int | The maximum number of documents the retriever was asked to return for the query (also known as `k`, `limit`, or `max_num_results`). | 5 |
| `gen_ai.memory.store.id` | string | The unique identifier of the memory store. | `ms_abc123`, `user-preferences-store` |
| `gen_ai.memory.record.id` | string | The unique identifier of the memory record. | `mem_5j66UpCpwteGg4YSxUnt7lPY` |
| `gen_ai.memory.record.count` | int | The number of memory records relevant to the operation. Per-operation meaning: search = returned; create/update/upsert/delete = attempted. | 3 |
| `gen_ai.memory.query.text` | string | The search query used to retrieve memories. SHOULD NOT be captured by default; gate on opt-in such as `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT`. | `user dietary preferences` |
| `gen_ai.memory.records` | any (`gen-ai-memory-records.json`) | The memory records stored or retrieved in a memory operation. Same opt-in gating. | `[{"content":"User prefers dark mode","id":"mem_123","score":0.95},...]` |

### A.1.8 Content attributes

| Attribute | Type | Brief | Notes |
|---|---|---|---|
| `gen_ai.system_instructions` | any (`gen-ai-system-instructions.json`) | The system message or instructions provided to the GenAI model separately from the chat history. | Use only when the API separates system instructions; in-history instructions go in `gen_ai.input.messages`. Part types limited to text (+ GenericPart). |
| `gen_ai.input.messages` | any (`gen-ai-input-messages.json`) | The chat history provided to the model as an input. | Messages MUST be in the order sent. |
| `gen_ai.output.messages` | any (`gen-ai-output-messages.json`) | Messages returned by the model where each message represents a specific model response (choice, candidate). | One message = one choice. `finish_reasons` stays aligned to provider generations even if messages are filtered. |

### A.1.9 Evaluation and prompt

| Attribute | Type | Brief | Examples |
|---|---|---|---|
| `gen_ai.evaluation.name` | string | The name of the evaluation metric used for the GenAI response. | `Relevance`, `IntentResolution` |
| `gen_ai.evaluation.score.value` | double | The evaluation score returned by the evaluator. | 4.0 |
| `gen_ai.evaluation.score.label` | string | Human readable label for evaluation. Low cardinality. | `relevant`, `not_relevant`, `correct`, `incorrect`, `pass`, `fail` |
| `gen_ai.evaluation.explanation` | string | A free-form explanation for the assigned score provided by the evaluator. | |
| `gen_ai.prompt.name` | string | The name of the prompt that uniquely identifies it. | `analyze-code` |
| `gen_ai.prompt.version` | string | The version of the prompt template used. | `1.0.0`, `2025-05-01`, `prod`, `v2` |
| `gen_ai.prompt.variable` | template[string] (`gen_ai.prompt.variable.<key>`) | The variables supplied to the prompt template, the `<key>` being the variable name, the value being the variable value. | `gen_ai.prompt.variable.user_name="Alice"` |

### A.1.10 Provider-specific registries

**OpenAI** (`model/openai/registry.yaml`):
- `openai.request.service_tier` — enum: `auto` ("The system will utilize scale tier credits until they are exhausted."), `default`.
- `openai.api.type` — enum: `chat_completions`, `responses`.
- `openai.response.service_tier` — string, e.g. `scale`, `default`.
- `openai.response.system_fingerprint` — string, e.g. `fp_44709d6fcb`.

**AWS Bedrock** (`model/aws-bedrock/registry.yaml`):
- `aws.bedrock.guardrail.id` — string, e.g. `sgi5gkybzqak`.
- `aws.bedrock.knowledge_base.id` — string, e.g. `XFWUPB9PAW`.

### A.1.11 JSON schemas for structured attributes (`model/gen-ai/*.json`)

**`gen-ai-input-messages.json`** — `InputMessages` = array of `ChatMessage`.
- `ChatMessage` (additionalProperties: true): required `role` and `parts`.
  - `role`: `Role` enum `system | user | assistant | tool`, or any string.
  - `parts`: array, anyOf the part types below, in this order: TextPart, ToolCallRequestPart, ToolCallResponsePart, ServerToolCallPart, ServerToolCallResponsePart, BlobPart, FilePart, UriPart, ReasoningPart, CompactionPart, GenericPart.
  - `name`: string | null — "The name of the participant."
- Part types:

| Part | `type` const | Required | Other fields |
|---|---|---|---|
| TextPart | `text` | type, content | `content` string |
| ToolCallRequestPart | `tool_call` | type, name | `id` string\|null; `name` string; `arguments` (any) |
| ToolCallResponsePart | `tool_call_response` | type, response | `id` string\|null; `response` (any) |
| ServerToolCallPart | `server_tool_call` | type, name, server_tool_call | `id`, `name`; `server_tool_call`: GenericServerToolCall {type (req), additionalProperties} |
| ServerToolCallResponsePart | `server_tool_call_response` | type, server_tool_call_response | `id`; `server_tool_call_response`: GenericServerToolCallResponse {type (req)} |
| BlobPart | `blob` | type, modality, content | `mime_type` string\|null; `modality` Modality\|string; `content` string format binary (base64 in JSON) |
| FilePart | `file` | type, modality, file_id | `mime_type`, `modality`, `file_id` (pre-uploaded file id) |
| UriPart | `uri` | type, modality, uri | `mime_type`, `modality`, `uri` (not a base64 data URL) |
| ReasoningPart | `reasoning` | type, content | `content` string ("Reasoning/thinking content received from the model.") |
| CompactionPart | `compaction` | type | `id` string\|null ("Provider-assigned identifier for the compaction item or block."); `content` string\|null ("The unencrypted compacted conversation summary, when available.") |
| GenericPart | any string | type | additionalProperties: true |

- `Modality` enum: `image | video | audio | document`.

**`gen-ai-output-messages.json`** — `OutputMessages` = array of `OutputMessage`.
- Same parts and fields as `ChatMessage`, plus `finish_reason`: `FinishReason` | string | null, with **`"deprecated": true`** — "Deprecated: report finish reasons in `gen_ai.response.finish_reasons` instead."
- `FinishReason` enum: `stop | length | content_filter | tool_call | compaction | error`.

**`gen-ai-system-instructions.json`** — `SystemInstructions` = array of anyOf {TextPart, GenericPart}.

**`gen-ai-tool-definitions.json`** — `ToolDefinitions` = array of anyOf:
- `FunctionToolDefinition`: required `type` (const `function`) and `name`. Optional `description` string\|null (NOT RECOMMENDED by default) and `parameters` (JSON Schema draft-07 \| null, NOT RECOMMENDED by default).
- `GenericToolDefinition`: required `type` and `name`.

**`gen-ai-retrieval-documents.json`** — array of `RetrievalDocument` {`id` string\|null, `score` number\|null}, additionalProperties: true. Neither field is required (changelog 107).

**`gen-ai-memory-records.json`** — array of `MemoryRecord`: required `content` (any). Optional `id` string\|null, `metadata` object\|null ("Provider-specific metadata"), `score` number\|null. additionalProperties: true.

**`gen-ai-tool-call-arguments.json`** / **`gen-ai-tool-call-result.json`** — object, additionalProperties: true.

**Content capture rules** (`docs/gen-ai/gen-ai-spans.md` § "Capturing instructions, inputs, and outputs"):
- Instrumentations SHOULD NOT capture content by default and SHOULD provide an opt-in.
- Three patterns: (1) default — don't record; (2) record on span attributes; (3) upload externally and record references, via an optional in-process upload hook invoked regardless of sampling.
- If structured attributes are unsupported on spans, serialize to a JSON string on spans and keep the structured form on events.
- "TODO: document a common approach to record references to externally stored content."
- "Streaming chunks: TODO".
- The only env var named in the spec is `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT`, given as an example opt-in for memory content.

## A.2 Span definitions (`model/gen-ai/spans.yaml`, docs `gen-ai-spans.md` and `gen-ai-agent-spans.md`)

**Shared attribute groups:**
- **error group:** `error.type` — Conditionally Required "If the operation ended in an error." It SHOULD match the provider/client error code, exception name, or another low-cardinality id. Well-known value `_OTHER`.
- **common group:** `gen_ai.request.model` (CR "If available.") and `gen_ai.operation.name` (Required).
- **address group:** `server.address` (Recommended) and `server.port` (CR "If `server.address` is set.").
- **Span duration:** GenAI spans "SHOULD cover the duration of the operation ... including any retries".

### 1) `gen_ai.inference.client`

- **Kind:** CLIENT; MAY be INTERNAL for in-process models.
- **Name:** `{gen_ai.operation.name} {gen_ai.request.model}`.
- **Operation:** `chat`, `generate_content` or `text_completion`. Span requirement level: recommended.

| Level | Attributes |
|---|---|
| Required | `gen_ai.operation.name`, `gen_ai.provider.name` |
| Conditionally Required | `error.type` (If the operation ended in an error.); `gen_ai.conversation.id` (If and only if the instrumented library has one readily available, or the user application provides one through OpenTelemetry context or library-specific mechanisms.); `gen_ai.output.type` (When applicable and if the request includes an output format.); `gen_ai.prompt.name` (when a named prompt template is used); `gen_ai.prompt.version` (when `gen_ai.prompt.name` is set and a version is available); `gen_ai.request.choice.count` (If available, in the request, and !=1.); `gen_ai.request.model` (If available.); `gen_ai.request.seed` (If applicable and if the request includes a seed.); `gen_ai.request.stream` (If and only if the request is streaming. If unset, the request is assumed to be non-streaming.); `gen_ai.request.top_k` (If applicable.); `server.port` (If `server.address` is set.) |
| Recommended | `gen_ai.conversation.compacted` (when available); `gen_ai.request.frequency_penalty`; `gen_ai.request.max_tokens`; `gen_ai.request.presence_penalty`; `gen_ai.request.previous_response.id` (When available and if the request references a previous response.); `gen_ai.request.reasoning.level` (When applicable.); `gen_ai.request.stop_sequences`; `gen_ai.request.temperature`; `gen_ai.request.top_p`; `gen_ai.response.finish_reasons`; `gen_ai.response.id`; `gen_ai.response.model`; `gen_ai.response.time_to_first_chunk` (If the request was a streaming request.); `gen_ai.usage.input_tokens`; `gen_ai.usage.output_tokens`; `gen_ai.usage.reasoning.output_tokens` (When applicable.); "When applicable.": `gen_ai.usage.{text,image,audio}.input_tokens`, `gen_ai.usage.{text,image,audio}.output_tokens`, `gen_ai.usage.{text,image,audio}.cache_read.input_tokens`, `gen_ai.usage.cache_read.input_tokens`, `gen_ai.usage.cache_write.input_tokens`; `server.address` |
| Opt-In | `gen_ai.system_instructions`, `gen_ai.input.messages`, `gen_ai.output.messages`, `gen_ai.tool.definitions`, `gen_ai.prompt.variable` |
| Sampling-relevant | `gen_ai.provider.name`, `gen_ai.operation.name`, `server.address`, `server.port`, `gen_ai.request.model` |

**Inference refinements** (`span_refinements`):
- **`openai.inference.client`** — `gen_ai.provider.name` MUST be `"openai"` at span creation.
  - `gen_ai.request.model` becomes **Required**.
  - `openai.request.service_tier`: CR "If the request includes a service_tier and the value is not 'auto'."
  - `openai.response.service_tier`: CR "If the response was received and includes a service_tier."
  - `openai.response.system_fingerprint`: Recommended. `openai.api.type`: Recommended.
  - Field mappings: input_tokens ← `usage.input_tokens`; cache_read ← `usage.input_tokens_details.cached_tokens`; reasoning ← `usage.output_tokens_details.reasoning_tokens`; reasoning.level ← `reasoning.effort`.
- **`azure.ai.inference.client`** — provider `"azure.ai.inference"`.
  - `azure.resource_provider.namespace` = `Microsoft.CognitiveServices`.
  - `server.port`: CR "If not default (443)."
  - Usage comes from `prompt_tokens` / `completion_tokens`.
- **`anthropic.inference.client`** — provider `"anthropic"`.
  - `gen_ai.request.top_k`: Recommended.
  - `reasoning.level` ← `output_config.effort`.
  - `gen_ai.usage.input_tokens = input_tokens + cache_read_input_tokens + cache_write_input_tokens`.
- **`aws.bedrock.inference.client`** — provider `"aws.bedrock"`.
  - `top_k`: Recommended.
  - `aws.bedrock.guardrail.id`: **Required**. `aws.bedrock.knowledge_base.id`: Recommended.

### 2) `gen_ai.embeddings.client`

- **Kind:** CLIENT. **Name:** `{gen_ai.operation.name} {gen_ai.request.model}`. Operation: `embeddings`.
- **Required:** `gen_ai.operation.name`, `gen_ai.provider.name`.
- **CR:** `error.type`, `gen_ai.request.model` (If available.), `server.port`.
- **Recommended:** `gen_ai.request.encoding_formats`, `gen_ai.usage.input_tokens`, `gen_ai.embeddings.dimension.count`, `gen_ai.response.model`, `server.address`.

### 3) `gen_ai.retrieval.client`

- **Kind:** CLIENT. **Name:** `{gen_ai.operation.name} {gen_ai.data_source.id}`. Operation: `retrieval`.
- **Required:** `gen_ai.operation.name`.
- **CR:** `error.type`, `gen_ai.request.model` (If available.), `gen_ai.provider.name` (When applicable.), `gen_ai.data_source.id` (When applicable.), `server.port`.
- **Recommended:** `gen_ai.retrieval.top_k`, `server.address`.
- **Opt-In:** `gen_ai.retrieval.query.text`, `gen_ai.retrieval.documents`.

### 4) `gen_ai.fetch_response.client`

- **Kind:** CLIENT. **Name:** `{gen_ai.operation.name}` (the response id is high-cardinality, so it is excluded). Operation: `fetch_response`. No span `requirement_level` is declared.
- **Required:** `gen_ai.provider.name`, `gen_ai.operation.name`, `gen_ai.response.id`.
- **CR:** `error.type`, `gen_ai.request.stream_cursor` (When the fetch resumes a streamed response from a prior position.), `server.port`.
- **Recommended:** `gen_ai.response.model`, `gen_ai.response.status`, `gen_ai.response.finish_reasons`, `server.address`.
- **Opt-In:** `gen_ai.system_instructions`, `gen_ai.output.messages`, `gen_ai.tool.definitions`. `gen_ai.input.messages` is explicitly not set.
- **Refinement `openai.fetch_response.client`:**
  - `openai.api.type` SHOULD be `responses`.
  - `gen_ai.response.status` comes from the response `status`.
  - `finish_reasons` is derived from status: `max_output_tokens` → `length`; `content_filter` → `content_filter`; failed or cancelled → `error`.
  - `openai.response.service_tier`: CR.

### 5) `gen_ai.memory.client`

- **Kind:** CLIENT; MAY be INTERNAL for in-process memory. **Name:** `{gen_ai.operation.name}`.
- **Operation:** one of `create_memory_store`, `search_memory`, `create_memory`, `update_memory`, `upsert_memory`, `delete_memory`, `delete_memory_store`.
- **Required:** `gen_ai.operation.name`.
- **CR:**
  - `error.type`
  - `gen_ai.provider.name` (If the operation is handled by a named external GenAI provider or service.)
  - `gen_ai.memory.store.id` (If applicable.)
  - `gen_ai.memory.record.id` (When the operation applies to a specific memory record.)
  - `server.port`
- **Recommended:** `gen_ai.memory.record.count` (If the operation involves memory records and the count is available.), `server.address`.
- **Opt-In:** `gen_ai.memory.query.text`, `gen_ai.memory.records`.
- **Note:** for `delete_memory`, a missing `record.id` may mean "delete all".

### 6) `gen_ai.create_agent.client`

- **Kind:** CLIENT. **Name:** `create_agent {gen_ai.agent.name}`. Operation: `create_agent`.
- **Required:** `gen_ai.operation.name`, `gen_ai.provider.name`.
- **CR:**
  - `error.type`, `gen_ai.request.model` (If available.)
  - `gen_ai.agent.id` (If applicable.)
  - `gen_ai.agent.name` (If provided by the application.) — sampling-relevant
  - `gen_ai.agent.description` (If provided by the application.)
  - `gen_ai.agent.version` (If provided by the application.)
  - `server.port`
- **Recommended:** `server.address`.
- **Opt-In:** `gen_ai.system_instructions`.

### 7) `gen_ai.invoke_agent.client` (remote agent, e.g. OpenAI Assistants, Bedrock Agents)

- **Kind:** CLIENT.
- **Name:** `invoke_agent {gen_ai.agent.name}`, or `invoke_agent` if no name.
- **Required:** `gen_ai.operation.name`, `gen_ai.provider.name`.
- **CR:**
  - `error.type`
  - `gen_ai.agent.name` (When available.), `gen_ai.agent.description` (When available.), `gen_ai.agent.id` (If applicable.), `gen_ai.agent.version` (When available.)
  - `gen_ai.request.choice.count` (If available, in the request, and !=1.), `gen_ai.request.seed`, `gen_ai.output.type`
  - `gen_ai.conversation.id` (iff readily available…), `gen_ai.data_source.id` (If applicable.)
  - `server.port`
- **Recommended:**
  - `gen_ai.request.model` (If applicable — only if the library allows a single model per agent)
  - `gen_ai.request.max_tokens`, `gen_ai.request.temperature`, `gen_ai.request.top_p`, `gen_ai.request.stop_sequences`, `gen_ai.request.frequency_penalty`, `gen_ai.request.presence_penalty`, `gen_ai.request.previous_response.id`
  - `gen_ai.response.finish_reasons`
  - `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`, the full usage breakdown including cache_read and cache_write (When applicable.)
  - `server.address`
- **Opt-In:** `gen_ai.system_instructions`, `gen_ai.input.messages`, `gen_ai.output.messages`, `gen_ai.tool.definitions`.
- **Sampling-relevant:** `gen_ai.provider.name`, `gen_ai.operation.name`, `gen_ai.request.model`, `gen_ai.agent.name`, `server.address`, `server.port`.

### 8) `gen_ai.invoke_agent.internal` (in-process agent, e.g. LangChain, CrewAI)

- **Kind:** INTERNAL. Same naming as 7. Entity association: `gen_ai.main_agent`.
- **Required:** `gen_ai.operation.name`.
- **CR:** `error.type`, `gen_ai.agent.name`, `gen_ai.agent.description`, `gen_ai.conversation.id`, `gen_ai.data_source.id`, `gen_ai.output.type`, `gen_ai.request.choice.count`, `gen_ai.request.seed`.
- **Recommended:** `gen_ai.request.model` (If applicable.), `gen_ai.request.max_tokens`, `gen_ai.request.temperature`, `gen_ai.request.top_p`, `gen_ai.request.stop_sequences`, `gen_ai.request.frequency_penalty`, `gen_ai.request.presence_penalty`, `gen_ai.response.finish_reasons`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`.
- **Opt-In:** `gen_ai.system_instructions`, `gen_ai.input.messages`, `gen_ai.output.messages`, `gen_ai.tool.definitions`.
- **Not on this span:** `gen_ai.provider.name`, `gen_ai.agent.id` and `gen_ai.agent.version` were removed (changelogs 214, 242, 257). Cache and modality usage were removed (changelog 440).

### 9) `gen_ai.execute_tool.internal`

- **Kind:** INTERNAL. **Name:** `execute_tool {gen_ai.tool.name}`. Entity: `gen_ai.main_agent`.
- **Required:** `gen_ai.operation.name`, `gen_ai.tool.name`.
- **CR:** `error.type`, `gen_ai.agent.name` (When applicable.), `gen_ai.conversation.id` (If available.).
- **Recommended:** `gen_ai.tool.call.id` (If available.), `gen_ai.tool.description` (If available.), `gen_ai.tool.type` (If available.).
- **Opt-In:** `gen_ai.tool.call.arguments`, `gen_ai.tool.call.result`.
- **Sampling-relevant:** `gen_ai.operation.name`, `gen_ai.tool.name`, `gen_ai.tool.type`, `gen_ai.agent.name`.
- **Note:** MCP tool calls may instead be traced by MCP instrumentation. Do not record two spans for one call.

**Execute-tool refinements:**
- **`gen_ai.execute_tool.load_skill.internal`**
  - Name: `execute_tool {gen_ai.tool.name} {gen_ai.skill.name}`.
  - Attributes: `gen_ai.skill.name` CR (If the skill name is available.), sampling-relevant; `gen_ai.skill.description` Rec; `gen_ai.skill.source.uri` Rec.
  - Examples: ADK `load_skill`, OpenAI Agents `load_skill`, Strands `skills`, Agno `get_skill_instructions`.
- **`gen_ai.execute_tool.read_skill_resource.internal`**
  - Name: `execute_tool {tool} {skill} {resource}`, or `execute_tool {tool} {resource}`, or `execute_tool {tool}`.
  - Attributes: `gen_ai.skill.name` CR, `gen_ai.skill.resource.name` CR, `gen_ai.skill.description` Rec, `gen_ai.skill.source.uri` Rec.
- **`gen_ai.execute_tool.command.internal`**
  - Name variants include `execute_tool {gen_ai.tool.name} {process.executable.name}`.
  - Attributes:
    - `gen_ai.skill.name` CR, `gen_ai.skill.resource.name` CR, `gen_ai.skill.description` Rec, `gen_ai.skill.source.uri` Rec
    - `process.executable.name` CR (If the tool directly executes a single process and the executable name is available.)
    - `process.executable.path` Rec
    - `process.exit.code` CR (If the tool reports a single command or process exit code.)
  - It MAY additionally emit CLI client spans.

### 10) `gen_ai.invoke_workflow.internal`

- **Kind:** INTERNAL. **Name:** `invoke_workflow {gen_ai.workflow.name}`. Entity: `gen_ai.main_agent`.
- **Required:** `gen_ai.operation.name`.
- **CR:** `error.type`, `gen_ai.workflow.name` (When available.), `gen_ai.conversation.id`.
- **Opt-In:** `gen_ai.input.messages`, `gen_ai.output.messages`.
- **Note:** SHOULD NOT be reported for standalone agent invocations or for internal runner implementation details. Examples: ADK `Runner.run`, CrewAI `Crew.kickoff()`, LangGraph `*Graph*.invoke`, MS Agent Framework `Workflow*.run`, OpenAI Agents `Runner.run(starting_agent=...)`.

### 11) `gen_ai.plan.internal`

- **Kind:** INTERNAL. **Name:** `plan {gen_ai.agent.name}`, or `plan`. Entity: `gen_ai.main_agent`.
- **Required:** `gen_ai.operation.name`.
- **CR:** `error.type`, `gen_ai.agent.name` (When available.), sampling-relevant.
- **Note:** the LLM call that generates the plan is a child. Report only when planning can be reliably distinguished.

### Entity `gen_ai.main_agent` (`model/gen-ai/entities.yaml`)

- Identity: `gen_ai.main_agent.id` (Required).
- Description: `gen_ai.main_agent.name`, `gen_ai.main_agent.description` (Recommended).
- MUST NOT be emitted without a stable id.

## A.3 Events (`model/gen-ai/events.yaml`; docs `gen-ai-events.md`, `gen-ai-exceptions.md`)

None of these events defines a separate *body*. All fields, including content, are attributes. The doc says structured content should be recorded in structured form on events.

1. **`gen_ai.client.inference.operation.details`** — signal requirement level: **Opt-In**.
   - Brief: "Describes the details of a GenAI completion request including chat history and parameters." It "could be used to store input and output details independently from traces."
   - Attributes: `ref_group: span.gen_ai.inference.client`, i.e. exactly the inference span attribute set and requirement levels from A.2(1). That includes Required `gen_ai.operation.name` and `gen_ai.provider.name`, and Opt-In `gen_ai.system_instructions`, `gen_ai.input.messages`, `gen_ai.output.messages`, `gen_ai.tool.definitions`, `gen_ai.prompt.variable`.
2. **`gen_ai.evaluation.result`** — **Recommended**.
   - Brief: "captures the result of evaluating GenAI output... SHOULD be parented to GenAI operation span being evaluated when possible or set `gen_ai.response.id` when span id is not available."
   - Attributes:
     - `gen_ai.evaluation.name` — Required
     - `error.type` — CR
     - `gen_ai.evaluation.score.value` — CR (If applicable.)
     - `gen_ai.evaluation.score.label` — CR (If applicable.)
     - `gen_ai.evaluation.explanation` — Recommended
     - `gen_ai.response.id` — Recommended (When available.)
3. **`gen_ai.client.operation.exception`** — **Recommended**. Severity SHOULD be WARN (13).
   - Attributes:
     - `exception.type` — CR (Required if `exception.message` is not set, recommended otherwise.)
     - `exception.message` — CR (Required if `exception.type` is not set, recommended otherwise.)
     - `exception.stacktrace` — Recommended
   - It MAY optionally be populated with the span's attributes.

There are no other events on `main`. The agent lifecycle, state-change and tool-decision events are proposals only; see A.6.

## A.4 Metrics (`model/gen-ai/metrics.yaml`, `model/gen-ai/token-metrics.yaml`)

**Shared metric group `metric_attributes.gen_ai`:**
- `gen_ai.operation.name` — Required
- `gen_ai.provider.name` — Required
- `gen_ai.request.model` — CR If available
- `gen_ai.response.model` — Recommended
- `server.address` — Recommended
- `server.port` — CR if `server.address` is set

All metrics below are development.

| Metric | Instrument | Unit | Attributes | Bucket advice |
|---|---|---|---|---|
| `gen_ai.client.operation.duration` | histogram (double) | `s` | metric_attributes.gen_ai + `error.type` CR; `gen_ai.provider.name` relaxed to CR "If the operation involves a call to a GenAI provider." | [0.01, 0.02, 0.04, 0.08, 0.16, 0.32, 0.64, 1.28, 2.56, 5.12, 10.24, 20.48, 40.96, 81.92] |
| `gen_ai.client.operation.time_to_first_chunk` | histogram | `s` | metric_attributes.gen_ai (streaming only) | same as above |
| `gen_ai.client.operation.time_per_output_chunk` | histogram | `s` | metric_attributes.gen_ai (streaming only) | same as above |
| `gen_ai.server.request.duration` | histogram | `s` | metric_attributes.gen_ai + `error.type` | same as above |
| `gen_ai.server.time_per_output_token` | histogram | `s` | metric_attributes.gen_ai | [0.01, 0.025, 0.05, 0.075, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.75, 1.0, 2.5] |
| `gen_ai.server.time_to_first_token` | histogram | `s` | metric_attributes.gen_ai | [0.001, 0.005, 0.01, 0.02, 0.04, 0.06, 0.08, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0] |
| `gen_ai.invoke_workflow.duration` | histogram | `s` | `error.type` CR; `gen_ai.workflow.name` CR If available | [1, 5, 10, 30, 60, 120, 300, 600, 1800, 3600, 7200] |
| `gen_ai.invoke_agent.duration` | histogram | `s` | `error.type` CR; `gen_ai.agent.name` CR When available; `gen_ai.request.model` Rec If applicable | [0.1, 0.2, 0.4, 0.8, 1.6, 3.2, 6.4, 12.8, 25.6, 51.2, 102.4, 204.8, 409.6] |
| `gen_ai.invoke_agent.inference_calls` | histogram (int) | `{inference_call}` | `gen_ai.agent.name` Rec. Counts only the agent's own calls, including failed ones. | [1, 2, 4, 8, 16, 32, 64, 128] |
| `gen_ai.invoke_agent.tool_calls` | histogram (int) | `{tool_call}` | `gen_ai.agent.name` Rec. Client-side tools only. | [1, 2, 4, 8, 16, 32, 64, 128] |
| `gen_ai.execute_tool.duration` | histogram | `s` | `error.type` CR; `gen_ai.tool.name` Req; `gen_ai.tool.type` Rec If available; `gen_ai.agent.name` CR When applicable | [0.01 … 81.92] (as client duration) |
| `gen_ai.client.inference.usage.input_tokens` | **counter** (int) | `{token}` | metric_attributes.gen_ai + `gen_ai.token.modality` **Required**. Billable tokens MUST be reported. | — |
| `gen_ai.client.inference.usage.output_tokens` | counter | `{token}` | same; includes reasoning | — |
| `gen_ai.client.inference.usage.cache_read.input_tokens` | counter | `{token}` | same; subset of input | — |
| `gen_ai.client.inference.usage.cache_write.input_tokens` | counter | `{token}` | same; subset of input | — |
| `gen_ai.client.inference.usage.reasoning.output_tokens` | counter | `{token}` | same; subset of output | — |
| `gen_ai.client.inference.operation.input_tokens` | histogram (int) | `{token}` | metric_attributes.gen_ai (deliberately **no** modality) | [1, 4, 16, 64, 256, 1024, 4096, 16384, 65536, 262144, 1048576, 4194304, 16777216, 67108864] |
| `gen_ai.client.inference.operation.output_tokens` | histogram (int) | `{token}` | same | same |

- **OpenAI metric refinements** add `openai.response.service_tier` and `openai.response.system_fingerprint` (Rec) to `gen_ai.client.operation.duration` and to all 7 token metrics.
- **Removed:** `gen_ai.client.token.usage` (breaking change 374).

## A.5 MCP (`model/mcp/*.yaml`, docs `docs/gen-ai/mcp.md`, `docs/registry/attributes/mcp.md`)

### Attributes (all development)

**`mcp.method.name`** — enum. Brief: "The name of the request or notification method." Members (id → value):

| Id | Value |
|---|---|
| `notifications_cancelled` | `notifications/cancelled` |
| `initialize` | `initialize` |
| `notifications_initialized` | `notifications/initialized` |
| `notifications_progress` | `notifications/progress` |
| `ping` | `ping` |
| `resources_list` | `resources/list` |
| `resources_templates_list` | `resources/templates/list` |
| `resources_read` | `resources/read` |
| `notifications_resources_list_changed` | `notifications/resources/list_changed` |
| `resources_subscribe` | `resources/subscribe` |
| `resources_unsubscribe` | `resources/unsubscribe` |
| `notifications_resources_updated` | `notifications/resources/updated` |
| `prompts_list` | `prompts/list` |
| `prompts_get` | `prompts/get` |
| `notifications_prompts_list_changed` | `notifications/prompts/list_changed` |
| `tools_list` | `tools/list` |
| `tools_call` | `tools/call` |
| `notifications_tools_list_changed` | `notifications/tools/list_changed` |
| `logging_set_level` | `logging/setLevel` |
| `notifications_message` | `notifications/message` |
| `sampling_create_message` | `sampling/createMessage` |
| `completion_complete` | `completion/complete` |
| `roots_list` | `roots/list` |
| `notifications_roots_list_changed` | `notifications/roots/list_changed` |
| `elicitation_create` | `elicitation/create` ("Request from the server to elicit additional information from the user via the client") |

Other MCP attributes:
- `mcp.session.id` — string. Identifies MCP session. Example `191c4850af6c49e08843a3f6c80e5046`.
- `mcp.resource.uri` — string. "The value of the resource uri." Used for `resources/read`, `resources/subscribe`, `resources/unsubscribe`, `notifications/resources/updated`.
- `mcp.protocol.version` — string. Example `2025-06-18`.

### Common group `mcp.common.attributes`

- `mcp.method.name` — Required
- `gen_ai.tool.name` — CR "When operation is related to a specific tool."
- `gen_ai.operation.name` — Recommended: "SHOULD be set to `execute_tool` when the operation describes a tool call and SHOULD NOT be set otherwise."
- `gen_ai.prompt.name` — CR "When operation is related to a specific prompt."
- `gen_ai.prompt.variable` — Opt-In. Prompt arguments in `prompts/get` are recorded as `gen_ai.prompt.variable.<argument_name>`.
- `error.type` — CR "If and only if the operation fails". Value is the JSON-RPC code string, or `tool_error` when `CallToolResult.isError=true`.
- `mcp.protocol.version` — Recommended
- Network attributes:
  - `network.transport`: `tcp`/`quic` for HTTP, `pipe` for stdio
  - `network.protocol.name`: Rec when applicable (`http`, `websocket`)
  - `network.protocol.version`: Rec when applicable
  - `jsonrpc.protocol.version`: Rec "When it's not `2.0`."

### Status codes

- **Client:** `rpc.response.status_code` CR "If response contains an error code." All JSON-RPC error codes are errors.
- **Server:** same attribute, but `-32700`, `-32600`, `-32601`, `-32602` and `-32002` "SHOULD NOT be considered errors".

### Spans

Common trace group: mcp.common + `mcp.session.id` (Rec, when part of a session) + `mcp.resource.uri` (CR when the request includes a resource URI) + `jsonrpc.request.id` (CR "When the client executes a request.").

| Span | Kind | Name | Additional attributes |
|---|---|---|---|
| `mcp.client` | CLIENT | `{mcp.method.name} {target}`, where target = `gen_ai.tool.name` or `gen_ai.prompt.name`; else `{mcp.method.name}`. `mcp.resource.uri` is opt-in only. | `server.address` (Rec If applicable), `server.port` (Rec when address set), `rpc.response.status_code` (client semantics), `gen_ai.tool.call.arguments` / `gen_ai.tool.call.result` (Opt-In) |
| `mcp.server` | SERVER | same | `client.address` (Rec If applicable), `client.port` (Rec when client.address set), `rpc.response.status_code` (server semantics), `gen_ai.tool.call.arguments` / `gen_ai.tool.call.result` (Opt-In) |

- On error, the span status description SHOULD equal `JSONRPCError.message`.
- If outer GenAI instrumentation already traces the tool, MCP instrumentation SHOULD add its attributes to that span instead of creating a new one.

### Context propagation

- Inject into the MCP `params._meta` with **unprefixed** keys `traceparent`, `tracestate`, `baggage` (SEP-414).
- The server uses the extracted context as parent and links the ambient context.

### Metrics (histograms, unit `s`, buckets [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 30, 60, 120, 300])

- `mcp.client.operation.duration` — mcp.common + `mcp.resource.uri` (Opt-In) + client status + `server.address` / `server.port`.
- `mcp.server.operation.duration` — mcp.common + `mcp.resource.uri` (Opt-In) + server status.
- `mcp.client.session.duration` — `mcp.protocol.version`, network attributes, `error.type` (CR "If and only if session ends with an error."), `server.address` / `server.port`.
- `mcp.server.session.duration` — `mcp.protocol.version`, network attributes, `error.type`.

### Transport table

| Transport | Attributes |
|---|---|
| stdio | `network.transport=pipe` |
| Streamable HTTP | `tcp`/`quic`, `http`/`2`, protocol ≥ `2025-06-18` |
| HTTP+SSE | `tcp`, `http` `1.1`/`2`, protocol ≤ `2024-11-05` |
| websocket | `network.protocol.name=websocket` |
| gRPC | `http`/`2` |

## A.6 Open issues relevant to agent control events

All read through WebFetch of `https://github.com/open-telemetry/semantic-conventions-genai/issues/<n>`. All are **Open**. "No comments" means WebFetch rendered none; I could not verify that through the API.

| # | Title | Author / opened | Labels | Proposed names (verbatim) | Last activity (as rendered) |
|---|---|---|---|---|---|
| 35 | Semantic Conventions for Generative AI Agentic Systems (gen_ai.*) | dany-moshkovich, 2025-08-20 (predates the repo split; likely transferred) | area:agent-orchestration, enhancement | Umbrella for namespaces `gen_ai.task.*`, `gen_ai.action.*`, `gen_ai.agent.*`, `gen_ai.team.*`, `gen_ai.artifact.*`, `gen_ai.memory.*`; detailed specs are in external Google Docs | No comments seen; 2025-08-20 |
| 37 | Semantic Conventions for Generative AI Tasks (gen_ai.task.*) | dany-moshkovich, 2025-08-20 | area:agent-orchestration, enhancement | `gen_ai.task.id`, `gen_ai.task.parent.id`, `gen_ai.task.name`, `gen_ai.task.code.id`, `gen_ai.task.code.vendor`, `gen_ai.task.kind`, `gen_ai.task.tags`, `gen_ai.task.requester.id`, `gen_ai.task.requester.type`, `gen_ai.task.requester.role`, `gen_ai.task.request.id`, `gen_ai.task.state`, `gen_ai.task.status`, `gen_ai.task.input.goal`, `gen_ai.task.input.instructions`, `gen_ai.task.output.data.values`, `gen_ai.task.dependencies.ids`, `gen_ai.task.feedback.rating` ("and related"; WebFetch summarised, so the list may be partial) | No comments seen; 2025-08-20 |
| 51 | Add session.id attribute to GenAI semantic conventions | 91pavan, 2025-10-07 | enhancement; project "Stable GenAI Semantic Conventions", status "Post-stability" | Reuse the existing registry `session.id`, with the hierarchy "session.id > gen_ai.conversation.id > individual spans" | No comments seen; 2025-10-07 |
| 86 | Add skill span | clongbupt, 2026-03-13 | enhancement | span `gen_ai.skill {skill_name}`; `gen_ai.operation.name`=`invoke_skill`; `gen_ai.skill.name`, `gen_ai.skill.id`, `gen_ai.skill.version`, `gen_ai.skill.description`, `gen_ai.input.messages`, `gen_ai.output.messages` | No comments seen. Main has since taken a different route: `gen_ai.skill.{name,description,source.uri,resource.name}` on `execute_tool` refinements (changelog 469), with no `invoke_skill` operation, `gen_ai.skill.id` or `gen_ai.skill.version` |
| 159 | Add async/long-running agent lifecycle events: gen_ai.agent.paused / .resumed / .checkpointed | meshailabs, 2026-05-14 | area:agent | Events `gen_ai.agent.started`, `gen_ai.agent.paused`, `gen_ai.agent.resumed`, `gen_ai.agent.checkpointed`, `gen_ai.agent.completed`, `gen_ai.agent.failed`; attributes `gen_ai.agent.pause.reason` (human_input, external_system, rate_limit, scheduled_delay), `gen_ai.agent.checkpoint.id`, `gen_ai.agent.execution.id` | Linked PR **#445** (draft, last activity 2026-09-16; details below) |
| 181 | Add privacy-first context input evidence for agent traces | caioribeiroclw-pixel, 2026-05-20 | none | `gen_ai.context.input.id`, `.kind`, `.source.path`, `.source.uri`, `.content.hash` (SHA256), `.loaded_by` (native_discovery, retrieval_tool, …), `.activation` (always_on, on_demand, hook, …), `.scope` (repo_root, task, session, …), `.why_loaded`, `.expected_benefit`, `.duplicate.dedupe_key`, `.role`, `.risk`; aggregates `gen_ai.context.retrieval.*` (query.count, returned.chars, …). WebFetch abbreviated the field list. | No comments seen; 2026-05-20 |
| 187 | Add `invoke_node {node.name}` span for non-agent workflow nodes | RKest, 2026-05-22 | area:agent-orchestration | Operation `invoke_node`; span `gen_ai.invoke_node.internal` (INTERNAL), name `invoke_node {gen_ai.node.name}` / `invoke_node`; `gen_ai.node.name` (low-card, sampling-relevant), `gen_ai.node.execution.id`, `gen_ai.node.previous_execution.id` (array); event `gen_ai.client.workflow.node.invocation.details` | No comments seen; 2026-05-22 |
| 249 | Span + metric definitions principles for agents, inference, control plane | lmolkova (maintainer), 2026-06-04 | none | Naming rule `gen_ai.<operation-class>.<kind>` for spans and `gen_ai.[client.]<operation-class>.<measured-thing>` for metrics; `client` only on client spans; operation-class = nominalized verb or `<verb>_<target>`. Table includes `gen_ai.search_memory.client` and `gen_ai.manage_memory.client` (main currently uses a single `gen_ai.memory.client`). References PRs #201, #203, #215. | No comments seen |
| 254 | Semantic Conventions for Agent-to-Agent (A2A) Protocol Telemetry | pwkowalski, 2026-06-05 | none | `a2a.method.name`, `a2a.protocol.version`, `a2a.protocol.binding`, `a2a.message.id`, `a2a.message.referenced_task_ids` (string[]), `a2a.task.id`, `a2a.task.state`, `a2a.task.artifact_ids` (string[]), `a2a.agent.card.url` (client-only), `a2a.protocol.requested_extensions` (string[]), `a2a.protocol.activated_extensions` (string[], server-only); metrics `a2a.client.operation.duration`, `a2a.server.operation.duration`, `a2a.server.task.duration` (histograms, s), `a2a.server.task.in_progress` (UpDownCounter), `a2a.server.task.artifacts_count`, `a2a.server.task.message_count` (histograms). References issue #243 and PR #195. | Body edited 2026-06-12 |

**Related items I found while following links.** Names for #445, #483 and #535 are exact, taken from the PR branches via git.

**PR #445 "Add agent lifecycle events for async and long-running executions"** — meshailabs, opened 2026-08-09, **draft**, last activity 2026-09-16; resolves #159.
- Events: `gen_ai.agent.paused`, `gen_ai.agent.checkpointed`, `gen_ai.agent.resumed`.
- Attributes:
  - `gen_ai.agent.execution.id` — Required on all three events.
  - `gen_ai.agent.pause.id` — Required on paused; Rec on checkpointed "When the checkpoint is taken at a pause boundary."
  - `gen_ai.agent.pause.reason` — enum `human_input`, `external_system`.
  - `gen_ai.agent.checkpoint.id` — Required on checkpointed.
  - `gen_ai.agent.resumed_from.type` — enum `checkpoint`, `pause`; CR "When the resumed work begins a new active execution segment".
  - `gen_ai.agent.resumed_from.id` — same condition.
  - `gen_ai.agent.id` and `gen_ai.agent.name` — Rec.
- Dropped in review: `pause.deadline`, `pause.resolution`, the `pause.resolved` event, and the reasons `rate_limit`, `scheduled_delay`, `expired`.
- Maintainer review (lmolkova, 2026-08-27): the PR models only one durability pattern, and flat pointers cannot express checkpoint trees. Work is paused pending prototypes in opentelemetry-python-genai (LangGraph, then CrewAI and ADK).

**PR #483 "Define GenAI execution state-change events"** — Utkarsh-Sinha0, opened 2026-08-31, open, last activity 2026-09-25.
- Event `gen_ai.execution.state.changed`, with:
  - `gen_ai.execution.state.changed_key.count` (int) — Required
  - `gen_ai.execution.state.changed_keys` (string[]) — Opt-In; no values or sensitive keys
  - `gen_ai.execution.state.version` (string) — CR "When the instrumented runtime exposes a version"; MUST NOT be used in metrics, span names or sampling
- The event MUST NOT include state values, tool arguments or results, or hidden reasoning.

**PR #535 "Add telemetry for pre-execution tool call decisions"** — hippoley, opened 2026-09-23, open, last activity 2026-10-02.
- Linked issues: #320 (Agent Harness Hook Semantic Conventions) and #95 (MCP tool approval).
- Event `gen_ai.tool.call.decision` (recommended), with:
  - `gen_ai.tool.call.decision.outcome` — enum `allow` / `deny` / `require_approval`; Required
  - `gen_ai.tool.call.id` — Rec If available
  - `gen_ai.tool.name` — Rec If available
- "A denied tool call can produce this event without producing an `execute_tool` span."

**Other related issues:**
- **#477 "Agent vs workflow"** — lmolkova, 2026-08-26. Proposes merging the `invoke_agent` and `invoke_workflow` definitions.
- **#320 "Agent Harness Hook Semantic Conventions"** — michaelsafyan, 2026-06-18. Six hook stages: session init, pre-LLM, pre-tool, post-tool, post-LLM/turn stop, session end. No names proposed yet.
- **#95 "GenAI Sem Conv enhancement to capture MCP Tool approval"** — singankit, 2026-04-28. Labels area:tools, mcp. Body is "TODO: Add more details".

## A.7 Repo metadata and contribution process

- **Releases and tags:** **none**. `git ls-remote --tags` returned nothing, and the `/releases` page says "There aren't any releases here."
- **Schema URL:**
  - `model/manifest.yaml` has `schema_url: https://opentelemetry.io/schemas/gen-ai-dev/1.42.0-dev`, `stability: development`.
  - `README.md` § "Schema URL" says literally "TODO".
  - `RELEASING.md` describes the dev channel: tags `vX.Y.Z-dev`, schema under `https://opentelemetry.io/schemas/gen-ai-dev/X.Y.Z-dev`. Releases are published as GitHub prereleases with resolved-schema assets via the `release-dev.yml` workflow. `CHANGELOG.md` has only "Unreleased"; towncrier fragments live in `changelog.d/`.
- **CODEOWNERS:** `* @open-telemetry/semconv-genai-approvers`.
- **Maintainers** (`CONTRIBUTING.md`): Liudmila Molkova (lmolkova, Google), Trask Stalnaker (trask, Microsoft).
- **Approvers:** Aaron Abbott (aabmass, Google), Ankit Singhal (singankit, Microsoft), JWinermaSplunk (Splunk), Mike Goldsmith (MikeGoldsmith, Honeycomb), Minghui Zhang (Cirilla-zmh, Alibaba), Alex Hall (alexmojaki, Pydantic). Each approver is expected to drive at least 3 non-editorial PR reviews per rolling 3 months.
- **Merge policy** (`.github/POLICIES.md`): 1 approval for editorial changes; **2 approvals from two different companies** for non-editorial changes.
- **How to propose a new attribute.** There is no issue template. The flow is to open an issue, then a YAML PR:
  1. Edit `model/<namespace>/registry.yaml` (all attributes MUST be defined there) and the spans/metrics/events YAML. Syntax is the Weaver semconv YAML (`file_format: definition/2`). Complex attributes require a JSON schema annotation.
  2. Run `make generate-all` (Weaver via the `otel/weaver:v0.26.1` container) to regenerate `docs/registry/` and the embedded tables.
  3. Run `make check-policies` (shared OTel weaver policies from `open-telemetry/opentelemetry-weaver-packages`, plus a local rego policy in `policies/check/json-schema-annotations/`).
  4. Update `reference/scenarios/<lib>/` to prove the convention is capturable. Validation uses the `open-telemetry/semantic-conventions-conformance` runner.
  5. Add a towncrier fragment `changelog.d/<pr>.<type>.md`, where type is one of breaking, deprecation, component, enhancement, bugfix, clarification.
- **PR template** sections: Description, **Motivation** (user journey + prior art), **Prototype** (reference scenarios or an alternate prototype), and a checklist.
- **Label taxonomy:** `.github/LABELS.md` defines `area:agent`, `area:agent-orchestration`, `area:embeddings`, `area:evaluation`, `area:inference`, `area:mcp`, `area:memory`, `area:messages`, `area:retrieval`, among others.
- **Discussion venues:** CNCF Slack `#otel-genai-instrumentation` and the GenAI SIG meeting.

---

# PART B — OpenInference (`Arize-ai/openinference`)

**Files read:**
- Specs: `spec/README.md`, `spec/semantic_conventions.md`, `spec/traces.md`, `spec/configuration.md`, `spec/llm_spans.md`, `spec/embedding_spans.md`, `spec/decision_spans.md`, `spec/tool_calling.md`, `spec/multimodal_attributes.md`, `spec/annotations.md`
- Python package `python/openinference-semantic-conventions/src/openinference/semconv/{trace,resource}/__init__.py` (`version.py` = `0.1.41`)
- JS package `js/packages/openinference-semantic-conventions` (`@arizeai/openinference-semantic-conventions` 2.14.0)
- Converter `js/packages/openinference-genai/src/attributes.ts`

## B.1 Span kinds (`openinference.span.kind`, required on all spans)

The spec table in `semantic_conventions.md` lists **11** kinds:

| Kind | Definition |
|---|---|
| `LLM` | Call to a Large Language Model |
| `EMBEDDING` | Call to generate embeddings |
| `CHAIN` | Starting point or link between application steps |
| `RETRIEVER` | Data retrieval step |
| `RERANKER` | Reranking of input documents |
| `TOOL` | Call to an external tool or function invoked by an LLM or agent |
| `AGENT` | Encompasses calls to LLMs and Tools; a reasoning block that acts on tools using the guidance of an LLM |
| `GUARDRAIL` | Protects against jailbreaks; modifies or rejects responses |
| `EVALUATOR` | Evaluation of model outputs |
| `PROMPT` | Rendering of a prompt template |
| `DECISION` | Call to a decision model that scores or selects among candidate options rather than generating free text |

- The Python enum `OpenInferenceSpanKindValues` has **12** members: the 11 above plus `UNKNOWN`.
- `spec/traces.md` "Span Kind" still lists only 10 (no DECISION).

## B.2 Complete attribute constants (Python `trace/__init__.py`)

The spec table types and examples are in `spec/semantic_conventions.md` § Reserved Attributes.

**`SpanAttributes`:**

| Group | Attributes |
|---|---|
| Feedback | `annotations`, `evaluations`, `trace.annotations`, `trace.evaluations`, `session.annotations`, `session.evaluations` |
| Input / output | `input.value`, `input.mime_type`, `output.value`, `output.mime_type`, `input.images`, `output.images` |
| Embedding | `embedding.embeddings`, `embedding.invocation_parameters`, `embedding.model_name` |
| LLM core | `llm.function_call` (legacy), `llm.invocation_parameters`, `llm.input_messages`, `llm.output_messages`, `llm.model_name`, `llm.request.model_name`, `llm.response.model_name`, `llm.provider`, `llm.system` |
| Decision | `decision.model_name`, `decision.request.model_name`, `decision.response.model_name`, `decision.provider`, `decision.system`, `decision.token_count.input`, `decision.token_count.output` |
| Completions API | `llm.prompts`, `llm.choices` |
| Prompt template | `llm.prompt_template.template`, `llm.prompt_template.variables`, `llm.prompt_template.version` |
| Token counts | `llm.token_count.completion`, `llm.token_count.completion_details.audio`, `llm.token_count.completion_details.reasoning`, `llm.token_count.prompt`, `llm.token_count.prompt_details` (prefix), `llm.token_count.prompt_details.audio`, `llm.token_count.prompt_details.cache_input`, `llm.token_count.prompt_details.cache_read`, `llm.token_count.prompt_details.cache_write`, `llm.token_count.total` |
| Finish reason | `llm.finish_reason` |
| Cost (USD, float) | `llm.cost.completion`, `llm.cost.completion_details` (prefix), `llm.cost.completion_details.audio`, `llm.cost.completion_details.output`, `llm.cost.completion_details.reasoning`, `llm.cost.prompt`, `llm.cost.prompt_details` (prefix), `llm.cost.prompt_details.audio`, `llm.cost.prompt_details.cache_input`, `llm.cost.prompt_details.cache_read`, `llm.cost.prompt_details.cache_write`, `llm.cost.prompt_details.input`, `llm.cost.total` |
| Tools | `llm.tools`, `tool.name`, `tool.description`, `tool.parameters`, `tool.id` |
| Retrieval | `retrieval.documents` |
| Context | `metadata`, `tag.tags`, `session.id`, `user.id` |
| Span kind | `openinference.span.kind` |
| Agent / graph | `agent.name`, `graph.node.id`, `graph.node.name`, `graph.node.parent_id` |
| Prompt registry | `prompt.vendor`, `prompt.id`, `prompt.url` |

`llm.token_count.prompt_details.cache_input` exists in Python but not in the spec table; the spec only has the cost variant.

**Other classes:**
- **`AnnotationAttributes`:** `annotation.name`, `annotation.score`, `annotation.label`, `annotation.explanation`, `annotation.annotator_kind`, `annotation.identifier`, `annotation.metadata`.
- **`EvaluationAttributes`:** `evaluation.name`, `evaluation.score`, `evaluation.label`, `evaluation.explanation`, `evaluation.annotator_kind`, `evaluation.identifier`, `evaluation.metadata`.
- **`MessageAttributes`:** `message.role`, `message.content`, `message.contents`, `message.name`, `message.tool_calls`, `message.function_call_name` (legacy), `message.function_call_arguments_json` (legacy), `message.tool_call_id`.
- **`MessageContentAttributes`:**
  - `message_content.type` — values `text`, `image`, `audio`, `video`, `reasoning`, `tool_use`
  - `message_content.text`, `message_content.image`, `message_content.audio`, `message_content.video`
  - `message_content.id`, `message_content.signature`, `message_content.data` (Anthropic `redacted_thinking.data`), `message_content.encrypted_content` (OpenAI)
- **Media and documents:**
  - `ImageAttributes`: `image.url`
  - `AudioAttributes`: `audio.url`, `audio.mime_type` (legacy), `audio.transcript`
  - `VideoAttributes`: `video.url`
  - `DocumentAttributes`: `document.id`, `document.score`, `document.content`, `document.metadata`
- **`RerankerAttributes`:** `reranker.input_documents`, `reranker.output_documents`, `reranker.query`, `reranker.model_name`, `reranker.top_k`.
- **`EmbeddingAttributes`:** `embedding.text`, `embedding.vector`.
- **`ToolCallAttributes`:** `tool_call.id`, `tool_call.function.name`, `tool_call.function.arguments`, `tool_call.reasoning_signature`.
- **`PromptAttributes`:** `prompt.text`. **`ChoiceAttributes`:** `completion.text`.
- **`ToolAttributes`:** `tool.json_schema`, `tool.name`, `tool.description`.
- **Resource** (`resource/__init__.py`): `openinference.project.name`.
- **Spec-only reserved attributes:** `exception.escaped`, `exception.message`, `exception.stacktrace`, `exception.type`.

**Enums:**
- `OpenInferenceAnnotatorKindValues`: `HUMAN`, `LLM`, `CODE`.
- `OpenInferenceMimeTypeValues`: `text/plain`, `application/json`.
- `OpenInferenceLLMSystemValues` (Python): `openai`, `anthropic`, `cohere`, `mistralai`, `vertexai`, `typesafe`. The spec table additionally lists `xai`, `deepseek`, `amazon`, `meta`, `ai21`.
- `OpenInferenceLLMProviderValues`: `openai`, `anthropic`, `cohere`, `mistralai`, `google`, `azure`, `aws`, `xai`, `deepseek`, `groq`, `fireworks`, `moonshot`, `cerebras`, `perplexity`, `together`, `ollama`, `meta`, `zai`, `minimax`, `oracle`, `typesafe`.
- `OpenInferenceDecisionSystemValues`: `typesafe`, `openai`. `OpenInferenceDecisionProviderValues`: `typesafe`, `openai`.

**Per-kind requirements:**
- **LLM spans** (`llm_spans.md`): MUST have `openinference.span.kind`=`LLM` and `llm.system`.
- **EMBEDDING spans:** MUST have the kind, and the span name MUST be `"CreateEmbeddings"`. `llm.system` and `llm.provider` are not used.
- **DECISION spans:** MUST have the kind and `decision.system`. They SHOULD NOT set `llm.system`, `llm.provider`, `llm.*model_name` or `llm.token_count.*` (the transition note is non-normative).
- **Feedback objects:** each object MUST have `name` plus at least one of `score`, `label`, `explanation`.
  - Session-scoped feedback requires `session.id`.
  - Post-hoc feedback uses a carrier span (recommended kind `EVALUATOR`) with exactly one Span Link to the target.
  - `annotations.md` maps to OTel `gen_ai.evaluation.result`: `name`→`gen_ai.evaluation.name`, `score`→`gen_ai.evaluation.score.value`, `label`→`gen_ai.evaluation.score.label`, `explanation`→`gen_ai.evaluation.explanation`. `annotator_kind`, `identifier` and `metadata` have no equivalent.
- **Context attributes** propagated through the instrumentation context API: `session.id`, `user.id`, `metadata`, `tag.tags`, `llm.prompt_template.template`, `llm.prompt_template.variables`, `llm.prompt_template.version`.

## B.3 Flattened patterns (zero-based `<prefix>.<index>.<suffix>`)

- **Messages:** `llm.input_messages.{i}.message.role`, `llm.input_messages.{i}.message.content`, `.message.name`, `.message.tool_call_id`. `llm.output_messages.{i}.message.role` / `.content` likewise.
- **Multimodal or ordered content** (`llm.<input|output>_messages.{i}.message.contents.{j}.` + suffix):
  - `message_content.type`, `message_content.text`
  - `message_content.image.image.url`
  - `message_content.audio.audio.url`, `message_content.audio.audio.transcript`
  - `message_content.video.video.url`
  - `message_content.id`, `message_content.signature`, `message_content.data`, `message_content.encrypted_content`
  - `tool_call.id`, `tool_call.function.name`, `tool_call.function.arguments`, `tool_call.reasoning_signature` (for `tool_use` parts)
- **Tool calls:** `llm.output_messages.{i}.message.tool_calls.{k}.tool_call.id`, `.tool_call.function.name`, `.tool_call.function.arguments` (JSON string), `.tool_call.reasoning_signature`.
- **Tool results:** `llm.input_messages.{i}.message.role`=`tool`, plus `.message.content` and `.message.tool_call_id`.
- **Available tools:** `llm.tools.{i}.tool.json_schema`, `llm.tools.{i}.tool.name`, `llm.tools.{i}.tool.description`.
- **Completions:** `llm.prompts.{i}.prompt.text`, `llm.choices.{i}.completion.text`.
- **Images:** `input.images.{i}.image.url`, `output.images.{i}.image.url`.
- **Embeddings:** `embedding.embeddings.{i}.embedding.text`, `embedding.embeddings.{i}.embedding.vector` (MUST be float arrays; base64 is decoded).
- **Documents:** `retrieval.documents.{i}.document.{id|score|content|metadata}`, `reranker.{input|output}_documents.{i}.document.*`.
- **Feedback:** `annotations.{i}.annotation.*`, `evaluations.{i}.evaluation.*`, `trace.annotations.{i}.annotation.*`, `trace.evaluations.{i}.evaluation.*`, `session.annotations.{i}.annotation.*`, `session.evaluations.{i}.evaluation.*`.
- **Session, user and graph:**
  - `session.id`, `user.id` (context attributes)
  - `agent.name`
  - `graph.node.id`, `graph.node.name`, and `graph.node.parent_id` (unset or empty means root)

## B.4 Configuration env vars (`spec/configuration.md`)

All are bool with default False unless stated.

| Variable | Effect |
|---|---|
| `OPENINFERENCE_HIDE_LLM_INVOCATION_PARAMETERS` | Hides LLM invocation parameters |
| `OPENINFERENCE_HIDE_LLM_TOOLS` | Hides `llm.tools.*`; also hidden by HIDE_INPUTS |
| `OPENINFERENCE_HIDE_INPUTS` | Hides input.value, input.images, all input messages and tool definitions |
| `OPENINFERENCE_HIDE_OUTPUTS` | Hides output.value, output.images and all output messages |
| `OPENINFERENCE_HIDE_INPUT_MESSAGES` | Hides all input messages |
| `OPENINFERENCE_HIDE_OUTPUT_MESSAGES` | Hides all output messages |
| `OPENINFERENCE_HIDE_INPUT_IMAGES` | Hides images in input messages and `input.images` |
| `OPENINFERENCE_HIDE_INPUT_TEXT` | Hides text in input messages |
| `OPENINFERENCE_HIDE_PROMPTS` | Hides completions-API prompts |
| `OPENINFERENCE_HIDE_OUTPUT_TEXT` | Hides text in output messages |
| `OPENINFERENCE_HIDE_CHOICES` | Hides completions-API choices |
| `OPENINFERENCE_HIDE_EMBEDDING_VECTORS` | Deprecated; use the next one |
| `OPENINFERENCE_HIDE_EMBEDDINGS_VECTORS` | Replaces vectors with `"__REDACTED__"` |
| `OPENINFERENCE_HIDE_EMBEDDINGS_TEXT` | Replaces embedding text with `"__REDACTED__"` |
| `OPENINFERENCE_HIDE_RETRIEVAL_DOCUMENTS` | Python only; redacts `document.content` and `document.metadata`; implied by HIDE_OUTPUTS |
| `OPENINFERENCE_BASE64_IMAGE_MAX_LENGTH` | int, default 32,000 |
| `OPENINFERENCE_BLOB_UPLOADER` | str, default unset; names a `BlobUploader` registered in the `openinference_blob_uploader` entry-point group (experimental). Oversized base64 images are uploaded and the attribute records the returned URI. |

- Redaction placeholder: `"__REDACTED__"`.
- Precedence: code `TraceConfig` > env vars > defaults.
- Python `TraceConfig` fields: `hide_llm_invocation_parameters`, `hide_llm_tools`, `hide_inputs`, `hide_outputs`, `hide_input_messages`, `hide_output_messages`, `hide_input_images`, `hide_input_text`, `hide_output_text`, `hide_embeddings_vectors`, `hide_embeddings_text`, `base64_image_max_length`, `blob_uploader`, `hide_prompts`, `hide_choices`.
- JS uses `traceConfig: { hideInputs: true, ... }`.

## B.5 Instrumentors in the repo

**Python** (`python/instrumentation/*`, PyPI name = directory name; version from `src/**/version.py`):

| Package | Version |
|---|---|
| openinference-instrumentation-ag2 | 0.1.11 |
| -agent-framework | 0.1.12 |
| -agentspec | 0.1.14 |
| -agno | 1.0.13 |
| -anthropic | 3.0.1 |
| -autogen | 0.1.15 |
| -autogen-agentchat | 0.1.21 |
| -bedrock | 0.1.56 |
| -beeai | 0.1.29 |
| -claude-agent-sdk | 0.1.20 |
| -cohere | 0.1.13 |
| -crewai | 1.1.20 |
| -dspy | 0.1.47 |
| -google-adk | 1.0.2 |
| -google-genai | 1.4.10 |
| -groq | 0.1.31 |
| -guardrails | 0.1.26 |
| -haystack | 0.1.44 |
| -instructor | 0.1.28 |
| -langchain | 0.1.78 |
| -litellm | 0.1.48 |
| -llama-index | 4.5.4 |
| -mcp | 2.0.12 |
| -mistralai | 2.2.1 |
| -ollama | 0.1.11 |
| -openai | 0.1.63 |
| -openai-agents | 2.5.2 |
| -openlit | 0.1.18 |
| -openllmetry | 0.1.22 |
| -pipecat | 2.0.8 |
| -portkey | 0.1.21 |
| -pydantic-ai | 0.1.29 |
| -smolagents | 0.1.42 |
| -strands-agents | 0.1.10 |
| -together | 0.1.11 |
| -typesafe | 0.1.4 |
| -vertexai | 0.1.27 |

- `openinference-instrumentation-promptflow` contains only `examples/` (no package).
- Core packages: `python/openinference-instrumentation`, `python/openinference-semantic-conventions` (0.1.41).

**JS** (`js/packages/*`, npm):

| Package | Version |
|---|---|
| @arizeai/openinference-core | 2.8.0 |
| @arizeai/openinference-genai | 0.4.0 (converts OTel GenAI attributes to OpenInference) |
| @arizeai/openinference-instrumentation-anthropic | 0.2.11 |
| @arizeai/openinference-instrumentation-bedrock | 0.5.4 |
| @arizeai/openinference-instrumentation-bedrock-agent-runtime | 1.2.4 |
| @arizeai/openinference-instrumentation-beeai | 1.6.2 |
| @arizeai/openinference-instrumentation-claude-agent-sdk | 0.3.4 |
| @arizeai/openinference-instrumentation-langchain | 4.1.4 |
| @arizeai/openinference-instrumentation-langchain-v0 | 0.1.4 |
| @arizeai/openinference-instrumentation-mcp | 0.2.36 |
| @arizeai/openinference-instrumentation-openai | 4.3.2 |
| @arizeai/openinference-instrumentation-openai-agents | 0.3.2 |
| @arizeai/openinference-instrumentation-typesafe | 0.4.0 |
| @arizeai/openinference-semantic-conventions | 2.14.0 |
| @arizeai/openinference-tanstack-ai | 0.3.2 |
| @arizeai/openinference-vercel | 3.2.4 |

**Also present:**
- Java `java/instrumentation/`: `openinference-instrumentation-adk-java`, `-annotation`, `-langchain4j`, `-springAI`.
- Go `go/`: `openinference-instrumentation-anthropic-sdk-go`, `-openai-go`, plus semconv and instrumentation core.

---

# PART C — Mapping analysis

## C.1 OpenInference attribute → nearest `gen_ai.*`

"none" means no `gen_ai.*` equivalent exists. Where the official converter `js/packages/openinference-genai/src/attributes.ts` implements the mapping (in the gen_ai → OI direction), I note "(converter)".

| OpenInference | Nearest gen_ai.* | Fidelity and notes |
|---|---|---|
| `openinference.span.kind` | `gen_ai.operation.name` (+ span type) | Category vs operation. LLM↔`chat`/`text_completion`/`generate_content`; EMBEDDING↔`embeddings`; RETRIEVER↔`retrieval`; TOOL↔`execute_tool`; AGENT↔`invoke_agent`/`create_agent`/`plan`; CHAIN↔`invoke_workflow` (converter; an agent identity upgrades it to AGENT). RERANKER, GUARDRAIL, EVALUATOR, PROMPT, DECISION, UNKNOWN: none. gen_ai memory ops and `fetch_response`: no OI kind. |
| `input.value` | none (closest: `gen_ai.input.messages`; on tools `gen_ai.tool.call.arguments`) | Converter maps input.messages and tool.call.arguments → input.value |
| `input.mime_type` | none | |
| `output.value` | none (closest: `gen_ai.output.messages` / `gen_ai.tool.call.result`) | |
| `output.mime_type` | none (`gen_ai.output.type` is the *requested modality*, not the MIME type) | |
| `input.images` / `output.images` | none (BlobPart/UriPart with `modality: image` exist only inside messages) | |
| `embedding.embeddings`, `embedding.vector`, `embedding.text` | none | gen_ai never records vectors or embedding inputs |
| `embedding.model_name` | `gen_ai.request.model` / `gen_ai.response.model` on the embeddings span | |
| `embedding.invocation_parameters` | `gen_ai.request.encoding_formats`, `gen_ai.embeddings.dimension.count` | JSON blob vs discrete attributes |
| `llm.invocation_parameters` | `gen_ai.request.{max_tokens,temperature,top_p,top_k,seed,stop_sequences,frequency_penalty,presence_penalty,choice.count,stream,reasoning.level}` | JSON blob vs discrete attributes (converter builds the blob) |
| `llm.input_messages` (+ `.{i}.message.*`) | `gen_ai.input.messages` (+ `gen_ai.system_instructions` for API-separate system) | Flattened vs structured JSON; converter maps system_instructions to message 0, role `system` |
| `llm.output_messages` | `gen_ai.output.messages` | |
| `llm.model_name` | `gen_ai.response.model` (fallback `gen_ai.request.model`) | converter |
| `llm.request.model_name` | `gen_ai.request.model` | exact |
| `llm.response.model_name` | `gen_ai.response.model` | exact |
| `llm.system` | `gen_ai.provider.name` (old `gen_ai.system`, deprecated) | Value vocabularies differ (e.g. `vertexai` vs `gcp.vertex_ai`; `mistralai` vs `mistral_ai`; `xai` vs `x_ai`) |
| `llm.provider` | `gen_ai.provider.name` | gen_ai merges system and provider into one; `azure`→`azure.ai.openai`/`azure.ai.inference`, `aws`→`aws.bedrock`, `google`→`gcp.*` |
| `llm.function_call` (legacy) | ToolCallRequestPart in `gen_ai.output.messages` | |
| `llm.prompts`, `prompt.text` | TextPart in `gen_ai.input.messages` with operation `text_completion` | `gen_ai.prompt` is obsoleted upstream |
| `llm.choices`, `completion.text` | TextPart in `gen_ai.output.messages` | |
| `llm.prompt_template.template` | none | gen_ai identifies prompts by name and version, not template text |
| `llm.prompt_template.variables` | `gen_ai.prompt.variable.<key>` | JSON blob vs one attribute per key |
| `llm.prompt_template.version` | `gen_ai.prompt.version` | |
| `prompt.id` | `gen_ai.prompt.name` (nearest) | |
| `prompt.vendor`, `prompt.url` | none | |
| `llm.token_count.prompt` | `gen_ai.usage.input_tokens` | Both include cache; OI also tells instrumentations to fold Anthropic cache tokens in |
| `llm.token_count.completion` | `gen_ai.usage.output_tokens` | |
| `llm.token_count.total` | none (derivable) | |
| `llm.token_count.prompt_details.cache_read` | `gen_ai.usage.cache_read.input_tokens` | exact (converter) |
| `llm.token_count.prompt_details.cache_write` | `gen_ai.usage.cache_write.input_tokens` | exact; the converter still reads the old `gen_ai.usage.cache_creation.input_tokens` |
| `llm.token_count.prompt_details.cache_input` | none (ambiguous; nearest `cache_read`) | Python-only constant |
| `llm.token_count.prompt_details.audio` | `gen_ai.usage.audio.input_tokens` | |
| `llm.token_count.completion_details.audio` | `gen_ai.usage.audio.output_tokens` | |
| `llm.token_count.completion_details.reasoning` | `gen_ai.usage.reasoning.output_tokens` | |
| (none in OI) | `gen_ai.usage.{text,image}.*`, `*.cache_read.input_tokens` per modality, `gen_ai.token.modality` | gen_ai only |
| `llm.cost.*` (all 13) | none | gen_ai has no cost attributes |
| `llm.finish_reason` | `gen_ai.response.finish_reasons` | string vs string[] (converter takes the first element) |
| `llm.tools` / `llm.tools.{i}.tool.json_schema` | `gen_ai.tool.definitions` (FunctionToolDefinition) | OpenAI-format string vs `{type,name,description,parameters}` object |
| `tool.name` | `gen_ai.tool.name` | exact (converter) |
| `tool.description` | `gen_ai.tool.description` | exact |
| `tool.id` | `gen_ai.tool.call.id` | exact |
| `tool.parameters` | **conflict**: OI spec says "parameters definition" (schema, i.e. `gen_ai.tool.definitions[].parameters`), but the converter maps `gen_ai.tool.call.arguments` → `tool.parameters` | Flag for standards work |
| `tool.json_schema` | `gen_ai.tool.definitions[i]` | |
| `tool_call.id` | ToolCallRequestPart.`id` / `gen_ai.tool.call.id` | |
| `tool_call.function.name` | ToolCallRequestPart.`name` | |
| `tool_call.function.arguments` | ToolCallRequestPart.`arguments` | JSON string vs object |
| `tool_call.reasoning_signature` | none (GenericPart extension only) | |
| `message.role` | ChatMessage/OutputMessage.`role` | OI allows `function`/`agent`; gen_ai Role enum is system/user/assistant/tool, plus any string |
| `message.content` | TextPart.`content` | |
| `message.contents` | `parts` | |
| `message.name` | ChatMessage.`name` | |
| `message.tool_calls` | ToolCallRequestPart(s) | |
| `message.tool_call_id` | ToolCallResponsePart.`id` | |
| `message.function_call_name` / `_arguments_json` (legacy) | ToolCallRequestPart | |
| `message_content.type` | part `type` | `text`→`text`; `reasoning`→`reasoning`; `tool_use`→`tool_call`; `image`/`audio`/`video`→`blob`/`uri`/`file` + `modality` |
| `message_content.text` | TextPart / ReasoningPart `content` | |
| `message_content.image` / `image.url` | UriPart.`uri` or BlobPart.`content` (modality `image`) | |
| `message_content.audio` / `audio.url` / `audio.mime_type` | UriPart/BlobPart (modality `audio`), `mime_type` | |
| `audio.transcript` | none | |
| `message_content.video` / `video.url` | UriPart/BlobPart (modality `video`) | |
| `message_content.id` | none (CompactionPart.`id` and ServerToolCallPart.`id` are type-specific) | |
| `message_content.signature`, `.data`, `.encrypted_content` | none | Reasoning replay tokens are not modelled in gen_ai |
| `retrieval.documents` | `gen_ai.retrieval.documents` | |
| `document.id` / `document.score` | RetrievalDocument `id` / `score` | |
| `document.content` / `document.metadata` | none (allowed only through additionalProperties) | |
| `reranker.query` | none (nearest `gen_ai.retrieval.query.text`) | no rerank operation |
| `reranker.top_k` | none (nearest `gen_ai.retrieval.top_k`) | |
| `reranker.model_name` | none (nearest `gen_ai.request.model`) | |
| `reranker.input_documents` / `output_documents` | none (nearest `gen_ai.retrieval.documents`) | |
| `decision.system` / `decision.provider` | none (nearest `gen_ai.provider.name`) | no decision operation |
| `decision.model_name`, `decision.request.model_name`, `decision.response.model_name` | none (nearest `gen_ai.request.model` / `gen_ai.response.model`) | |
| `decision.token_count.input` / `.output` | none (nearest `gen_ai.usage.input_tokens` / `output_tokens`) | |
| `session.id` | `gen_ai.conversation.id` | converter maps conversation.id → session.id. Issue #51 proposes adopting OTel registry `session.id` as a level above conversation. |
| `user.id` | none in `gen_ai.*` | core OTel registry `user.id`, outside this repo |
| `agent.name` | `gen_ai.agent.name` | exact (converter) |
| (none in OI) | `gen_ai.agent.id`, `.description`, `.version`, `gen_ai.main_agent.*` | gen_ai only |
| `graph.node.id` | none (#187 proposes `gen_ai.node.execution.id`) | |
| `graph.node.name` | none (#187 proposes `gen_ai.node.name`; nearest merged is `gen_ai.workflow.name`) | |
| `graph.node.parent_id` | none (#187 proposes `gen_ai.node.previous_execution.id`) | gen_ai relies on span parentage |
| `metadata` | none | converter puts system_instructions in `metadata.gen_ai.system_instructions` in some paths |
| `tag.tags` | none | |
| `annotation.name` / `evaluation.name` | `gen_ai.evaluation.name` | documented in OI `annotations.md` |
| `annotation.score` / `evaluation.score` | `gen_ai.evaluation.score.value` | |
| `annotation.label` / `evaluation.label` | `gen_ai.evaluation.score.label` | |
| `annotation.explanation` / `evaluation.explanation` | `gen_ai.evaluation.explanation` | |
| `annotation.annotator_kind`, `.identifier`, `.metadata` (and evaluation.*) | none | |
| `annotations`, `evaluations`, `trace.*`, `session.*` feedback lists | `gen_ai.evaluation.result` event (one result per event; no trace or session scope) | |
| `exception.*` | core `exception.*` (+ `gen_ai.client.operation.exception` event) | |
| `openinference.project.name` (resource) | none (nearest core `service.name`) | |

**gen_ai-only concepts with no OpenInference attribute:**
- `gen_ai.conversation.compacted`, CompactionPart
- `gen_ai.memory.*` and the 7 memory operations
- `gen_ai.skill.*`, `gen_ai.workflow.name`, the `plan` operation, `gen_ai.main_agent` entity
- `gen_ai.response.status`, `gen_ai.response.time_to_first_chunk`
- `gen_ai.request.previous_response.id`, `gen_ai.request.stream_cursor`, `gen_ai.request.stream`, `gen_ai.request.reasoning.level`
- `gen_ai.output.type`, `gen_ai.data_source.id`, `gen_ai.tool.type`
- ServerToolCallPart / ServerToolCallResponsePart, FilePart
- All `mcp.*` attributes, and every metric (OpenInference defines no metrics)

## C.2 Agent-control concepts and whether either convention covers them

| Concept | OTel gen_ai (main) | OpenInference | Status |
|---|---|---|---|
| **Compaction** | **Partial:** `gen_ai.conversation.compacted` (boolean, positive-only, Rec on inference span); `CompactionPart` {`type`=`compaction`, `id`, `content`}; FinishReason `compaction` (deprecated field) | none | Only a marker exists. No compaction event or operation, trigger, strategy, before/after token counts, or link from summary to source turns. |
| **Permission / approval** | none merged. PR #535 proposes event `gen_ai.tool.call.decision` + `gen_ai.tool.call.decision.outcome` (`allow`/`deny`/`require_approval`); issues #95, #320. PR #445's `gen_ai.agent.pause.reason=human_input` is adjacent. | none (GUARDRAIL kind is content safety, not permission) | Absent in both |
| **Verification** (checking an agent's action or output: tests, assertions, self-check) | none (`gen_ai.evaluation.result` is quality scoring; `process.exit.code` exists on command-execution tools) | none (EVALUATOR kind and annotations are scoring) | Absent in both |
| **Stop reason** (why the agent loop or turn ended: max turns, budget, interrupt, hook stop, handoff) | Model-level only: `gen_ai.response.finish_reasons`, `gen_ai.response.status` (for fetched responses), `error.type` | Model-level only: `llm.finish_reason` | Agent-level stop reason absent in both (#320 names a "Post-LLM / Turn Stop" hook stage, no attributes) |
| **Checkpoint** | none merged. PR #445 (draft, paused): `gen_ai.agent.checkpointed`, `gen_ai.agent.checkpoint.id`, `gen_ai.agent.resumed_from.type`/`.id`, `gen_ai.agent.execution.id`; PR #483 `gen_ai.execution.state.changed`, `.state.version` | none | Absent in both |
| **Delegation identity** (who delegated to whom, on whose behalf, handoff source) | Partial: `gen_ai.agent.{id,name,version}` describe the *invoked/executing* agent; `gen_ai.main_agent.*` entity is the top-level agent; nesting comes only from span parentage. Proposals: #35/#37 `gen_ai.task.requester.{id,type,role}`, `gen_ai.task.parent.id`; #254 `a2a.*`. | Partial: `agent.name`, `graph.node.parent_id` (structural only) | No delegator/delegatee or principal attributes in either |
| **Context provenance** (which artifact entered context, how, and why) | none. Issue #181 proposes `gen_ai.context.input.*`; `gen_ai.data_source.id` and `gen_ai.retrieval.documents[].id` give only retrieval-level linkage. | none (`document.id` / `document.metadata` only) | Absent in both |
| **Memory provenance** (who or what wrote a memory, from which conversation or turn, when, trust level) | Operations are covered (`gen_ai.memory.*`, MemoryRecord {`content`, `id`, `metadata`, `score`}), but there are no provenance fields beyond free-form `metadata` | none (no memory concept at all) | Absent in both |

## URLs used

**Cloned (`git clone --depth 1`):**
- https://github.com/open-telemetry/semantic-conventions-genai.git (main @ e07f4eb)
- https://github.com/Arize-ai/openinference.git (main @ 19363a0)
- https://github.com/open-telemetry/semantic-conventions.git (tag v1.44.0, sparse)
- https://github.com/open-telemetry/.github.git (checked for org issue templates; none found)

**PR refs fetched with git:** `refs/pull/445/head`, `refs/pull/483/head`, `refs/pull/535/head` from open-telemetry/semantic-conventions-genai.

**Raw URL equivalents of the files cited:** `https://raw.githubusercontent.com/open-telemetry/semantic-conventions-genai/main/` + one of:
- `model/manifest.yaml`
- `model/gen-ai/registry.yaml`, `spans.yaml`, `events.yaml`, `metrics.yaml`, `token-metrics.yaml`, `entities.yaml`
- `model/gen-ai/gen-ai-input-messages.json`, `gen-ai-output-messages.json`, `gen-ai-system-instructions.json`, `gen-ai-tool-definitions.json`, `gen-ai-retrieval-documents.json`, `gen-ai-memory-records.json`, `gen-ai-tool-call-arguments.json`, `gen-ai-tool-call-result.json`
- `model/mcp/registry.yaml`, `common.yaml`, `spans.yaml`, `metrics.yaml`
- `model/openai/registry.yaml`, `model/aws-bedrock/registry.yaml`
- `docs/gen-ai/README.md`, `gen-ai-spans.md`, `gen-ai-agent-spans.md`, `gen-ai-events.md`, `gen-ai-exceptions.md`, `gen-ai-metrics.md`, `gen-ai-token-metrics.md`, `mcp.md`, `openai.md`, `anthropic.md`, `aws-bedrock.md`, `azure-ai-inference.md`
- `docs/registry/attributes/gen-ai.md`, `mcp.md`, `openai.md`, `aws.md`; `docs/registry/entities/gen-ai.md`
- `reference/README.md`, `reference/reports/*.md`
- `CONTRIBUTING.md`, `RELEASING.md`, `README.md`, `CHANGELOG.md`, `changelog.d/*.md`, `versions.env`, `Makefile`
- `.github/CODEOWNERS`, `.github/POLICIES.md`, `.github/PULL_REQUEST_TEMPLATE.md`, `.github/LABELS.md`, `.github/instructions/model-style.instructions.md`

**Upstream:** `https://raw.githubusercontent.com/open-telemetry/semantic-conventions/v1.44.0/` + one of:
- `model/gen-ai/deprecated/registry-deprecated.yaml`
- `model/mcp/deprecated/registry-deprecated.yaml`
- `model/openai/deprecated/registry-deprecated.yaml`
- `docs/gen-ai/README.md`

**OpenInference:** `https://raw.githubusercontent.com/Arize-ai/openinference/main/` + one of:
- `spec/README.md`, `semantic_conventions.md`, `traces.md`, `configuration.md`, `llm_spans.md`, `embedding_spans.md`, `decision_spans.md`, `tool_calling.md`, `multimodal_attributes.md`, `annotations.md`
- `python/openinference-semantic-conventions/src/openinference/semconv/trace/__init__.py`, `…/semconv/resource/__init__.py`, `…/semconv/version.py`
- `python/instrumentation/*/pyproject.toml` and `src/**/version.py`
- `js/packages/*/package.json`, `js/packages/openinference-genai/README.md`, `js/packages/openinference-genai/src/attributes.ts`

**Fetched with WebFetch:**
- Issues: https://github.com/open-telemetry/semantic-conventions-genai/issues/35, /37, /51, /86, /159, /181, /187, /249, /254, plus related /95, /320, /477, /483
- PRs: /pull/445, /pull/535
- https://github.com/open-telemetry/semantic-conventions-genai/releases
- https://github.com/open-telemetry/semantic-conventions-genai/issues/new/choose (rendered as a sign-in page; not usable)
