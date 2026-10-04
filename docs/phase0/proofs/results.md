# Engineering Proofs A to G — Results (4 October 2026)

All numbers come from `scripts/run_proofs.py` over real Claude Code 2.1.289 captures in `tests/fixtures/claude_code/`, and are enforced as tests in `tests/test_proof_gates.py`. Model under test for the agent runs: `claude-haiku-4-5-20251001`. Everything is reproducible from the repository.

## Fixture inventory

| Set | Runs | What they are |
|---|---|---|
| proofA | 1 session (plus a resumed `/compact` segment) | Write code, run it, hit a `ZeroDivisionError`, delegate to a `reviewer` subagent, fix, rerun; then manual compaction |
| proofD | 3 | `loop`: eight byte-identical failing shell commands by instruction (retry storm). `bypass`: asked to skip tests; the agent obeyed CLAUDE.md and ran them anyway (a control in practice). `control`: the task done properly |
| proofE | 15 | Same task class, three cohorts of five: **S** (success), **F1** (injected permission fault: Bash removed from the allowlist so pytest is denied headlessly), **F2** (injected context fault: CLAUDE.md points at a non-existent test directory) |

## Proof A — capture a complex Claude Code execution

Met. See `proof-A-claude-code-capture.md`. Three channels (hooks, OTel logs, SDK stream) plus the raw-body side channel were sufficient for G3 reconstruction. Finding that changed the specs: the PostCompact hook carries the full compaction summary, and the SDK `compact_boundary` carries token counts and the preserved message segment.

## Proof B — normalize into the v0.1 model with few framework-specific exceptions

| Measure | Value | Gate |
|---|---|---|
| Native records outside v0.1, all records | 55.7% | — |
| Native records outside v0.1, excluding the HOOK and configuration domains deferred to v0.2 (`hook_registered`, `hook_execution_*`, `managed_settings_resolved`, `plugin_loaded`) | **3.5%** | < 10% ✔ |
| Remaining exceptions | `assistant_response` (duplicates `api_response_body`; dropped by design) | |

Honest reading: the 55.7% headline is inflated by our own instrumentation (22 registered hooks produce 44 `hook_registered` records per session). The HOOK domain is real telemetry and will be a v0.2 domain with these exact fields. The second open harness (LangGraph or Agents SDK) half of Proof B is specified in SPEC-06 and not yet executed; the v0.1 model was checked against the framework surface report (`research/04`) for representability but no second-framework capture exists in this repository yet. **Proof B is half met.**

## Proof C — visualize context changes and verification gates

Graph for the proofA run: 64 nodes, 117 edges, **fidelity G3**. Edges by relation and provenance:

| Relation | Source | Count |
|---|---|---|
| parent_of | runtime (shared run or turn id) | 63 |
| approved_by, produces | runtime (tool_call_id) | 9 + 9 |
| delegated_to, returned_to | runtime (agent_instance_id) | 2 + 1 |
| loaded_into | runtime (InstructionsLoaded) | 3 |
| requested_by | normalizer (latest model.response in agent instance) | 7 |
| compacted_from | normalizer (precedes compaction) | 23 |

Runs with a verification event reach **G4**. No inferred edges are added by this code, so G5 does not occur. Visualization is a Phase 1 Flight Recorder deliverable; the graph structure and fidelity computation exist and are tested. **Met at the data-model level, not yet as a UI.**

## Proof D — detect injected failures with zero false positives on controls

| Run | Findings |
|---|---|
| proofD/loop (8 identical failing commands) | **D1** doom loop, **D3** retry storm, **D4** no progress, **D5** budget spiral, D6 (policy: no verification before stop) |
| proofD/bypass, proofD/control | none |
| S-1 to S-5 (control cohort) | **none, 0/5 false positives** |
| F1-1 to F1-5 (pytest denied) | **D6** verification bypass on 5/5, severity high ("attempted but blocked"); **D7** permission storm on the 3/5 runs that had two or more denials |
| F2-1 to F2-5 (wrong test path) | none (the agents recovered; one or two failed tool calls each, below the D3 threshold) |

Verification events come from the harness-independent verification adapter (D-038): a pytest invocation that completes is `verify.passed`, that fails is `verify.failed`, that is denied is `verify.abstained`. Without it no coding harness reports verification at all.

D6 is defined at the policy level ("the run ended without a passed verification"). It does not distinguish F1-1, F1-3 and F1-5, where the agent claimed completion, from F1-2 and F1-4, where it honestly reported that tests could not run. A claim classifier is a separate, later detector. Gate: zero false positives on controls ✔; injected loop and bypass detected ✔.

## Proofs E and F — compare cohorts and find the injected first divergence

| Comparison | First divergence (agreement across all failed × success pairs) | Observed upstream input difference | Primary hypothesis | Correct |
|---|---|---|---|---|
| S vs F1 | `permission.denied:Bash` at position 0, agreement 1.0 | none | **permission** | top-1 ✔ |
| S vs F2 | `context.provenance.loaded:project_instructions:<hash>` at position 0, agreement 1.0 | project instructions content hash differs in every failed vs every successful run | **context_builder**, mechanism visible downstream as exploratory `find`/`ls` calls | top-1 ✔ |
| Single failed run vs success cohort (leave-one-out) | | | | **10/10 in top-3** (gate ≥ 70%) ✔ |

How it works: trajectories are abstracted to tokens (event type, tool or verifier name, outcome; content never enters a token, only the instruction-file content hash does), aligned pairwise by longest common subsequence, the first non-matching token in the failed run is recorded, candidates are ranked by pair agreement, and observed input differences between cohorts (instruction hashes, tool-definition hashes, model, harness config hash) are checked before attributing. Correlation is reported as a hypothesis with an agreement fraction, never as proven cause.

Honest reading: these are controlled, single-fault cohorts on one task class with five runs each. The F2 divergence is found at the input, which is exactly where a release-correlation system would also find it. The hard case, a divergence that appears mid-trajectory with identical inputs, is represented only by F1 here. LongRCA's 24% exact-step result on real heterogeneous trajectories remains the realistic expectation for production data; this proof shows the machinery works and the evidence contract is honest, not that the research problem is solved.

## Proof G — replay a recorded failure

Not executed in this phase. Prerequisites are in place: the raw-body side channel captured 11 complete request/response pairs for the proofA run (the replay cassette), chained by `thread.previous_message_id`; tool inputs and outputs are hashed and referenced; the fixture repository state is a git-free directory that can be snapshotted. The replay manifest, matching rules and fidelity measurement are specified in SPEC-02 from the prior-art report (`research/06`). **Gate criterion for Proof G (R2 on 80%, R3 on 50%) is open.**

## Gate A/B status from the proofs

| Criterion | Status |
|---|---|
| Proof B under 10% exceptions | Met for Claude Code (3.5% excluding HOOK domain); second harness pending |
| Proof D detected with zero false positives | Met |
| Proof F top-3 at least 70% | Met (100% on controlled cohorts) |
| Proof G R2 on 80%, R3 on 50% | Open |

## Findings for the specifications

1. The event model needs a `source_name_hash` on provenance events so instruction files are comparable across runs (added).
2. Iteration numbering must tolerate hooks firing before the OTel record of the model response is flushed (implemented as carry-over of unresolved tool requests).
3. The same denial is reported by two channels (`permission_denied` in the stream, `tool_decision reject` in OTel); detectors must dedupe on `tool_call_id` (implemented).
4. OTel `compaction.pre_tokens` (5421) disagrees with the SDK `compact_boundary.pre_tokens` (32800) for the same compaction; the semantics differ and are kept as separate fields until confirmed with the vendor.
5. `/compact` spawns a subagent in 2.1.289 (a second `SubagentStop` with the summary as its last message). Compaction is itself a delegation and should be modelled as one.
6. Every OTel record carries `user.email`, `user.account_id`, `user.account_uuid`, `user.id`, `organization.id` by default. The adapter strips them unless told otherwise; 1,014 attribute values were removed from the proofA run alone.
