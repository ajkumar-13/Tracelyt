# Proof G2 — Replay gate over recorded failure and success cohorts (executed 22 October 2026)

**Question (SPEC-02 §11 gate).** Over a cohort of recorded runs, what share replays at R2 (fixtures served and verified, tools live, final workspace identical, three of three runs the same)? The gate asks for R2 on at least 80% of recorded failures.

**Answer: 83% of failures (10 of 12) and 100% of successes (6 of 6); 16 of 18 overall.** Eighteen runs were recorded with the new recorder wrapper (`harness_engine.recorder`) and replayed three times each with the engine from Proof G. The two misses are both runs in which the agent, hunting for a test directory that did not exist, read the recorder's own capture files inside the workspace; the recorder now keeps captures outside the workspace, which removes that class.

## 1. Cohorts (re-recorded; Phase 0 recipes, `scripts/record_cohorts.py`)
| Cohort | Runs | Expected outcome | Fault injected | Recorded model calls |
|---|---|---|---|---|
| loop | 1 | failure | reliability drill: an 8× identical failing command | 9 |
| bypass | 1 | failure | verification skipped by instruction | 2 |
| control | 1 | success | none | 3 |
| S | 5 | success | none | 5 each |
| F1 | 5 | failure | permission fault: Bash not allowed, pytest denied headless | 9, 5, 5, 6, 10 |
| F2 | 5 | failure | context fault: rules file names a test suite that does not exist | 12, 8, 9, 9, 9 |

Harness: Claude Code 2.1.289 pinned for recording and replay; model `claude-haiku-4-5-20251001`; headless, `acceptEdits`. Recording wall time 419 s for 121 model calls; one replay pass over all 18 runs: 62 s.

## 2. Results (`proof_g2_replay_gate.json`)
| Measure | Value |
|---|---|
| Runs replayed at R2, three of three | 16 of 18 (89%) |
| Failures at R2 | **10 of 12 (83%)**: loop, bypass, F1 ×5, F2-2, F2-3, F2-4 |
| Successes at R2 | 6 of 6 (100%): control, S ×5 |
| Tool results reproduced by live execution (normalized) | 100 of 103 |
| Model calls served from fixtures | 121 of 121 (plus one post-turn side call per run with no fixture, as in Proof G) |
| Replay time versus recording | about 1/7 |

**The two misses.** F2-1 diverged at call 8 when the agent ran `find` over the workspace and listed `captures/` (the recorder's files, which differ between recording and replay by construction), then at call 9 read a file that only existed in the recording. F2-5 diverged at call 7 on `ls -la captures/`. Both are the observer appearing in the frame: the agent's search for the non-existent `tests/spec/` reached the instrumentation. The F2 fault makes this likely (the agent explores widely); the S and F1 runs never looked there.

## 3. What the gate run taught the recorder and the matcher
1. **Instrumentation must be invisible to the agent.** Two generations of this bug: a loose copy of the pre-run tree inside the workspace made pytest collect a duplicate test module in the first smoke recording (now a tar archive), and the capture directory itself showed up in `ls` output (block counts, entries) and was read by exploring agents. The recorder now writes to a sibling directory (`<workspace>.captures`) and routes hooks there through `QAR_CAPTURE_DIR`, which hook subprocesses inherit (OTEL variables are not inherited; custom ones are, verified).
2. **Listing metadata is environment, not state.** `ls -l` modification times and link counts (the parent directory's count rose as sibling runs were recorded) caused every S run to miss at its first call. Profile `claude_code_v1` normalizes them; file names and sizes are kept, and the final tree is still compared by content hash.
3. **Test-runner timings are noise**; normalized (`in 0.11s`).
4. **Post-turn side calls** (summary generation) arrive after the recorded turn and have no fixture; the harness tolerates the error and the run completes. Reported as `extra_requests`, never counted against R2.
5. **Cost of the gate.** Recording was the expensive part (API time); replaying 18 runs three times took under four minutes on one container. A nightly regression gate over hundreds of recorded failures is a small compute bill.

## 4. Limits
Same host, reset tree, no fresh container (R3 isolation not met; state agreement measured through tool results and final tree hashes). One harness and model; short tasks; no network tools; no branching. The misses were caused by the recorder's old layout, so the 83% understates what the current recorder would score, but we report what was measured.

## 5. Gate relevance
SPEC-02 §11: R2 on ≥ 80% of recorded failures, met (83%); R3 on 50%, not yet measured under isolation. Next: re-record with the sibling capture layout and run the same gate inside a fresh container per run (ADR-007 default), then extend to the OpenAI Agents SDK recordings.
