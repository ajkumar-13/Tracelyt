# Proof G — Frozen self-replay of a recorded Claude Code run at R2 (executed 22 October 2026)

**Question (SPEC-02 §11).** Can a recorded coding-agent run be replayed deterministically from its cassette, with the model boundary served from fixtures and the tools executed live, such that the replay reproduces the recorded tool outputs and the final workspace, three times out of three?

**Answer: yes, at R2, with two disclosures.** The proofA session (11 model calls, 9 tool calls, one subagent delegation, two threads) replays in 3.2 seconds against the recorded 15.4 seconds of API time, three runs out of three bit-identical in final workspace, with every served model call verified against the recorded new input and every recorded tool result reproduced by live execution. The two disclosures are harness-configuration drift between the recording and the replay environment, and one asynchronous-notification timing difference that produced a twelfth, unanswerable request after the run had completed. Both are reported by the engine, not masked.

## 1. Setup
- Cassette: the raw-body side channel of the proofA recording (`OTEL_LOG_RAW_API_BODIES=file:`), 11 request/response pairs, committed scrubbed as `tests/fixtures/claude_code/rawbodies/`.
- Harness: Claude Code **2.1.289**, the recorded version, installed from the npm registry and pinned (the container's default binary had moved to 2.1.308).
- Replay server: `src/harness_engine/replay/server.py`, speaking the Messages API streaming protocol; `ANTHROPIC_BASE_URL` pointed at it. Matching: `match.py`, S1 positional cursor per conversation (keyed by `thread.previous_message_id`, or by the tool_result ids a non-threaded request answers), verified by three hashes under normalization profile `claude_code_v1` (`cassette.py`): exact, normalized, and **delta** (the new message only), with **config** (model, params, system, tools, betas) compared separately.
- Workspace: the recorded working directory, reset to its pre-run tree before each run (rules file, agent definition, hook settings kept; `calc.py` and bytecode removed). Tools run live: Write, Bash (`python3 calc.py`, the failing `div(1,0)` call), Task (the reviewer subagent), Read, Edit.
- Runner: `scripts/run_proof_g.py`; results: `docs/phase0/proofs/proof_g.json`.

## 2. Results (three runs)

| Measure (SPEC-02 §5 R2) | Run 1 | Run 2 | Run 3 |
|---|---|---|---|
| Fixture coverage (recorded model calls served) | 11/11 | 11/11 | 11/11 |
| Served-call verification level | delta ×11 | delta ×11 | delta ×11 |
| Tool-result agreement (recorded vs live execution, normalized) | 9/9 | 9/9 | 9/9 |
| Final workspace tree equals the recording | yes | yes | yes |
| Harness exit code / terminal reason | 0 / completed | 0 / completed | 0 / completed |
| Wall time | 3.2 s | 3.2 s | 3.2 s |
| Extra requests with no fixture | 1 (seq 12) | 1 | 1 |
| Configuration drift reported on | 11 calls | 11 calls | 11 calls |

Identical across runs: yes. **R2 frozen self-replay: pass** (coverage 100%, 3 of 3 identical, first divergence only at the post-completion request).

Shell steps: the four Bash results (two successful `python3 calc.py` runs, the ZeroDivisionError traceback, the rerun after the fix) agree on content and exit status with the recording. That is the R3 measurement (state-hash and exit-code agreement) observed through the model boundary, at 4/4, but on the same host with a reset tree rather than a fresh container from an image, so this proof claims **R2, with R3 agreement measured and the R3 isolation condition not met**.

## 3. Findings that change the specs
1. **Harness configuration is part of the replay manifest, not just the version.** Trial 1 pointed the pinned 2.1.289 binary at the replay server with a plain API key: the harness sent no `betas` (so no message threads), a different system-prompt variant, and 42 tools instead of the recorded 16 with deferred loading. Trial 2 inherited the recording's host configuration and still showed the same three differences, because the harness resolves feature flags and prompt variants remotely at startup and the replay base URL answered those lookups with 404. Same binary, different harness. SPEC-02 §2 run manifest now requires entrypoint, provider mode, API betas, the tool roster hash and the resolved feature-flag set (Claude Code emits `managed_settings_resolved`, which is the right capture point). The engine reports this as `config_drift` per call, separately from input divergence.
2. **Two verification keys, not one.** Comparing whole requests conflates three things: the new input (tool results, which is what environment replay must reproduce), the transport (threaded one-message requests versus full-history requests), and the harness configuration. The engine now verifies the new input (`delta`) and reports configuration drift alongside; a whole-request mismatch with equal delta is not a fixture miss. SPEC-02 §3 amended.
3. **Server-side conversation state is replayable when the replay server is the state.** Anthropic message threads (`thread.previous_message_id`) looked like the hard case in SPEC-02 §12 Q2. On replay the served response ids are the recorded ids, so the next request's `previous_message_id` is the conversation key, and a non-threaded harness is keyed by the tool_result ids instead. Both forms route to the same envelope. Q2 closed.
4. **Harness-generated identifiers are volatile and must be normalized.** Subagent ids, task output paths and session ids appear inside tool results (the Task tool's launch message). Profile `claude_code_v1` lists them; without that rule the subagent delegation step reads as a divergence.
5. **Asynchronous events are a real nondeterminism source.** In the recording, the subagent-completion notification arrived while the main agent was answering a `ReadNotifications` call and was embedded in that tool result; in the replay the subagent finished faster and the notification arrived after the final `end_turn`, producing a twelfth model call with no fixture. The harness ended normally; the engine reports the request as `extra_requests`. SPEC-02 §2 `nondeterminism.sources` gains `async_notification_timing`; replay runners should treat post-completion requests as non-blocking.
6. **Thinking content is already redacted by the side channel** (`<REDACTED>` with the signature intact). Replay serves it as recorded; nothing in the harness depended on the text. Reasoning blocks are therefore not a replay blocker for Claude Code at R2.

## 4. Limits of this proof
One session, one harness, one model, a short task with no network tools. Live tools were re-executed in the recorded path on the same host, not a fresh container. No branching, no counterfactual (Phase 2 and 3). The recorded run's `/compact` turn was not part of the cassette. Egress capture (`network[]`) and `fs_delta` were not exercised; final-tree hashing stood in for them.

## 5. Gate relevance
SPEC-02 §11 asked for R2 on 80% of recorded failures and R3 on 50% by the Phase 1 gate. This proof establishes the mechanism on one run at R2 (pass) with R3 agreement measured at 100% under reduced isolation. The Phase 1 benchmark (SPEC-07) runs the same procedure over the proofD and proofE cohorts next.
