# SPEC-02 — Replay, Simulation and Regression, v0.1

**Version:** 0.1.0 · **Status:** APPROVED v0.1 (founder approval 2026-10-05; Phase 1 baseline) · **Owner:** Replay & Sandbox with Regression & CI · **Depends on:** SPEC-01, SPEC-05, research 06 · **Validated so far:** R2 cassette capture exists for Claude Code (Proof A side channel); replay execution not yet run (Proof G open)

## 1. Purpose and position
Replay is the proof mechanism behind the regression gate (PLAN-11 P11, D-031), never a standalone feature. Deterministic replay of recorded fixtures until divergence, then controlled live branching, with fidelity disclosed per run (P10). Everything executes customer-side by default (P15; SPEC-05 §6).

## 2. What must be captured: the replayable step record
One envelope per boundary crossing, append-only, with payloads as content-addressed blobs in the side channel (D-037). Research 06 §8(i) gives the full record; the normative core:

**Common header:** `run_id`, `step_id`, `seq`, `parent_step_id`, `caused_by[]`, `branch {branch_id, parent_run_id, forked_at_seq, intervention_id}`, `actor {agent_instance_id, harness, harness_version, component_version}`, `boundary {kind: model_call|tool_call|mcp_call|shell_exec|file_edit|env_read|human_input, name, invocation_index, attempt}`, `time {wall_start, wall_end, mono_start_ns, mono_end_ns}`, `match_keys {exact, normalized, structural, conversation}`, `side_effect {class, source: declared_mcp|declared_customer|inferred|default, confidence, idempotency_key, mcp_annotations_snapshot}`, `request_ref`, `response_ref`, `redaction {fields, method: hmac-sha256-keyed, key_id}`, `state {pre_ref, post_ref}` (workspace tree ids, R3), `outcome {status, error_class, error_message_ref}`, `nondeterminism {sources[]}`.

**Model call adds:** provider, endpoint, API version headers (`anthropic-version`, `anthropic-beta`), `model_requested`, `model_served`, params (temperature, top_p, top_k, max_tokens, thinking/effort, tool_choice, parallel_tool_calls, stop, seed, service_tier, response_format), `tools_ref` with per-tool schema hashes, `system_ref`, `messages_ref`, cache-control markers, **server-side state pointers** (`previous_response_id`, `conversation_id`, `thread.previous_message_id`) which replay must inline or mock because hosted state is not replayable, `raw_request_ref`, response `id`, `request_id`, `system_fingerprint`, stop reason, usage, reasoning blocks verbatim with a `replayable` flag (encrypted or session-bound reasoning is not), streamed events with offsets, transport retries, latency and ttft. Fact: Anthropic has no `seed`; OpenAI Responses has none; Chat Completions `seed` is best-effort. Determinism comes from the cassette, not the provider.

**Tool call adds:** `tool_name`, `tool_version`/`code_hash`, `schema_hash`, `model_tool_call_id`, `args_canonical_ref`, `result_raw_ref`, `result_as_seen_by_model_ref`, `is_error`, nested `child_http[]`, `resources_touched[]`.
**MCP call adds:** server `{name, version, protocolVersion, capabilities, transport, session_id}`, `tools_list_ref` snapshot incl. annotations, JSON-RPC request and result, `notifications[]`, nested `server_requests[]` (sampling, elicitation), latency.
**Shell adds:** `argv`/`command_string`, interpreter, shell-init ref, `cwd`, `env_diff` (names and value hashes), stdin/stdout/stderr refs, `exit_code`, signal, timeout, duration, `background_pids[]` (force R4), egress `network[]` from the proxy, `image_digest`, `fs_delta {changed[{path, pre_hash, post_hash, mode}], tree_pre, tree_post}`.
**File edit adds:** path, op, `pre_blob`, `post_blob`, diff ref, editor (edit tool, shell, external). Shell-made edits derive from `fs_delta`; Claude Code checkpoints miss exactly these.
**Run manifest:** PLAN-12 §16 plus `repo_url`, `base_sha`, `dirty_diff_ref`, `image_digest`, toolchain and lockfile hashes, harness and agent config, prompt versions, tool and MCP registry versions, model ids, `tz`, `locale`, clock offset, network policy, credentials inventory (names only), `capture_level`.

Phase 0 status: Claude Code's `OTEL_LOG_RAW_API_BODIES=file:` plus hooks already yield model-call envelopes (raw request and response, `thread.previous_message_id`, tool inputs and outputs by hash). Shell `fs_delta` and `network[]` require the collector's workspace snapshotter and egress proxy (Phase 1).

## 3. Matching strategy (normative)
Ranked per research 06 §8(ii):
1. **S1 Positional cursor per `(boundary name, invocation_index)` verified against the exact or normalized hash.** On mismatch emit `divergence {seq, expected_key, actual_key, field_diff}` and switch to the policy's branch mode. Divergence is detected, not masked, and is itself evidence. (Temporal, DBOS, Restate, Chronicle pattern.)
2. **S2 Exact canonical hash, order-free within a scope** for retries and concurrency.
3. **S3 Structural `(name, canonical args)`** for parallel and reordered tool calls.
4. **S4 Edit-tolerant normalization** (ids dropped, tools sorted, optionally system prompt excluded) **only for counterfactual modes**; the match-key profile is recorded.
5. S5 subset or method-only: test doubles only. **S6 pure sequence without verification: forbidden** (hides divergence). S7 similarity: suggestion after a miss only, never to serve a response.
A fixture miss **latches live mode for that branch** and is recorded; a transport failure does not latch.

## 4. Replay modes
Exact fixture replay; partial replay; **branch replay** (history until divergence, then controlled live execution, branch captured); live shadow replay; counterfactual replay (alternative model, tool version, policy, instruction file). Branch replay is Phase 3; Phase 2 ships exact and partial.

## 5. Fidelity levels R1 to R5 and their measurement (per run; highest level whose checks pass)
| Level | Required capture | Measurement | Pass rule (proposal) |
|---|---|---|---|
| R1 event-only | envelopes without payloads | field-sufficiency score per step kind; replay-precondition probe listing missing preconditions | causal graph complete (no orphan `caused_by`) |
| R2 dependency fixtures | raw request and response for every nondeterministic boundary (model, tool, MCP, network) | fixture coverage; **frozen self-replay** of the unchanged harness 3 times with S1 matching: zero misses, bit-identical outputs; `first_divergence_seq` if any | coverage 100% of model/MCP/tool boundaries; 3 of 3 identical |
| R3 + filesystem/runtime snapshot | per-step `tree_pre`/`tree_post`, image digest | replay tools live in a fresh container from image plus base tree; **state-hash agreement** and **exit-code agreement** for shell steps (Replay Gap: 99.99% over 11,702 actions) | agreement ≥ 99.9%; every disagreement listed as environment divergence |
| R4 near-deterministic sandbox | R3 plus process and memory state where `background_pids` non-empty; egress denied, fixtures served | noise floor from same-model control forks (k = 30% and 70% of steps, K = 5): action-match rate, normalized post-fork edit distance, first-divergent-action rate, outcome-flip rate | reported, not gated; requires the measured noise floor and serving configuration |
| R5 full environment replica | external services replicated or stateful mocks | external-effect equivalence (pre/post environment diff, AgentDojo style); zero unrecorded egress; zero fixture misses | all effect diffs equal; zero unrecorded egress |
Cross-cutting checks (from "Safe to Resume?"): internal state complete at the fork point; external dependencies not stale; nondeterministic replay reported; unrecorded external effects (egress not explained by any envelope) found. Each finding downgrades the level and is shown on the run.

## 6. Side-effect classification (ADR-008)
Classes per SPEC-01 §5.4.1, aligned with MCP tool annotations (`readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`) and recorded with their source (declared by MCP, declared by customer, inferred, default) and confidence. Replay policy per class: read-only executes live or from fixture; reversible writes execute in the sandbox; irreversible, financial, external-communication and security-sensitive calls are served from fixtures or mocks and never executed; unknown is treated as irreversible.

## 7. Sandbox and runner (ADR-007 direction)
Tiered: **content-addressed filesystem snapshots in containers as the default (R3)** because coding-agent state is overwhelmingly filesystem state and prefix re-execution in a pinned image reaches 99.99% return-code agreement; **gVisor checkpoint/restore** when process state matters, on the customer's runner; **Firecracker memory-snapshot fork** (E2B-style multi-fork, 1 to 20 forks with full memory) as the managed or high-isolation R4 tier. Daytona fork is copy-on-write filesystem only and its OSS repo has been unmaintained since June 2026; Modal snapshots restore into a new sandbox; Claude Agent SDK `fork_session()` does not copy file snapshots; OpenHands `fork()` shares the workspace. Network deny-by-default; credentials never mounted; quotas and wall-clock limits; outputs sanitized; every replay audited.

## 8. Incident to regression case
`incident → fixture bundle (manifest + envelopes + blobs) → expected behaviour (outcome, verification requirements, forbidden side effects) → control set (successful runs of the same task class)`. Cases carry data rights (SPEC-05 §8).

## 9. Regression run and report
Baseline harness vs candidate harness over the case suite (production failures, customer cases, synthetic cases, security cases, performance cases, policy cases). Report: verified success delta, cost delta, latency delta, new failures, fixed failures, behaviour change (trajectory distance), verification change, per-case fidelity level, Pareto view (never a single score). CI check on pull requests touching harness files (rules files, hooks, settings, prompts, tool schemas, model config); merge-gate mode optional. Phase 3 adds recommendations as replay experiments with attached deltas.

## 10. Corrections carried from research 06
deepeval has no record/replay API; "agent-vcr" is two unrelated projects; AgentOps time travel is gone from the current SDK; LangGraph replay re-executes nodes; Laminar serves cached LLM responses keyed by `(trace_id, input hash)` with system messages excluded and tools not stubbed; LangSmith Engine fix validation is input replay, not deterministic replay. The remaining gap is narrower than the archive claimed and is exactly this spec: deterministic replay of **tools and environment** plus branching from an arbitrary recorded step, across vendors.

## 11. Proof G plan (Phase 1 week 1)
Replay the proofA session at R2: serve the 11 recorded model responses by S1 cursor from the side-channel cassette, execute the tools live in a fresh container from the fixture tree, compare tool outputs and final file state, report first divergence and fidelity. Then run frozen self-replay three times. Gate: R2 on 80% of recorded failures, R3 on 50%.

## 12. Open questions
1. Egress proxy design for `network[]` capture on customer machines.
2. How to inline Anthropic `thread.previous_message_id` server-side state for replay.
3. Whether to store envelopes separately from SPEC-01 events or as event payload refs (current direction: envelopes are the payload layer; events reference them).
