# Phase 1 — Kickoff Charter and Tracker

**Phase:** 1, Open Flight Recorder and Reliability Signal (PLAN-04 M2 to M9). **Started:** 22 October 2026. **Target exit:** Gate B (Developer Utility) and Gate C (Reliability Signal).
**Entry state:** Phase 0 closed on 5 October 2026 with the engineering and specification criteria met, the name, license, Laminar posture and SPEC v0.1s decided, and the discovery program answered from the public record (`docs/phase0/99-gate-report.md`). Carried in: Proof G (replay) not executed; replay hosting and willingness to pay not observable; eighteen design-partner candidates named.
**Operating rule:** the open recorder is the product; every week ends with something a developer can install or a number a partner can check.

## 1. Purpose of Phase 1 in one paragraph
Ship the open-source recorder developers install (`install → instrument → run → inspect` in under ten minutes), get the event model into the first frameworks and CLIs, prove that detectors find real failures on partner traffic, prove that recorded runs replay deterministically enough to anchor a regression gate, and land the first design partners streaming production structural telemetry. The commercial lead is the regression gate (D-031); Phase 1 builds the evidence it stands on: recorder, graph fidelity, detectors with published precision, and replay at R2/R3.

## 2. Team reality and sequencing
PLAN-04 sizes Phase 1 at 30 to 75 engineers. Until hiring lands, the small-team variant in PLAN-04 applies: Claude Code plus one open harness, detectors D1/D4/D5/D6/D8 first, one design partner, and the regression gate for that partner before any incident UI. The backlog below is written for the full team but ordered so the small-team path is its prefix.

## 3. Workstreams, deliverables, status

| # | Workstream (PLAN-04) | Phase 1 deliverable | Week-1 item | Status |
|---|---|---|---|---|
| W1 | Replay & Sandbox | Replay manifest v1; fixture capture for coding agents; R2 frozen self-replay; R3 state agreement; sandbox evaluation | **Proof G**: replay engine (`src/harness_engine/replay/`), self-replay of the proofA cassette with the pinned Claude Code 2.1.289 | **R2 pass** (3/3 identical; `docs/phase0/proofs/proof-G-replay.md`) |
| W2 | Capture & Standards | Python and TypeScript SDKs; Tier A instrumentors (LangGraph, OpenAI Agents SDK, ADK, PydanticAI, Claude Agent SDK, OpenHands); Tier B adapters (Claude Code, Codex, Gemini CLI); Tier C ingestion; conformance suite; first OTel proposals | **OpenAI Agents SDK instrumentor** with a scripted model and measured exception rate (`src/harness_engine/adapters/openai_agents/`) | **done**: 2.9% exception rate (2 of 70 native signals); guardrail spans are the v0.2 candidate (`docs/phase0/proofs/proof-B-openai-agents.md`) |
| W3 | Data Plane | Ingestion gateway; versioned normalizer; stream; raw evidence store; payload refs; identity propagation; customer-side payload mode | OTLP receiver hardening (gzip, auth, backpressure) and the shared hook adapter binary | backlog |
| W4 | Flight Recorder & DX | Local UI (timeline, execution tree, subagent tree, context events, permissions, stop reasons); CLI `record`, `run inspect`, `compare` | `qar record` wrapping Claude Code with hooks, OTLP and raw bodies configured automatically | **done**: `scripts/qar.py record|replay`, `harness_engine.recorder`; captures outside the workspace |
| W5 | Execution Graph | Observed edges complete; fidelity per run; reconstructed `derived_from` for tool results into context | carry Proof C builder; add `derived_from` by content addressing | backlog |
| W6 | Reliability Intelligence | D1–D10 with the §13 contract; D11–D19 from the public record (SPEC-03 §4.1); streaming statistical detectors | D11 hook-did-not-fire and D12 policy bypass via delegation, each with a public reproduction fixture | backlog |
| W7 | Benchmark & Corpus | Harness Reliability Benchmark v0.1; fault-injection harness; corpus with data-rights tags | execute `docs/phase0/benchmarks/` plans for store, stream, sandbox | backlog |
| W8 | Security & Privacy | Redaction and secret detection in SDK and collector; tenant identity; audit log v1 | PII stripping moved from adapter to collector boundary with tests | backlog |
| W9 | Design partners | Eight signed (four builders, three fleets, one vendor); production telemetry within four weeks; weekly failure review | **Founder:** 10–20 live conversations with `docs/phase0/discovery/00-counters.md` §3, asking only Q18–Q24 | founder action |
| W10 | Company | Name clearance; entity; OTel SIG membership; first proposal PR | **Founder:** registrar and counsel checks for Kernmantle; join the GenAI SIG; file the `gen_ai.tool.call.decision.source` extension with Proof A evidence | founder action |

## 4. Week-1 engineering log
- **Replay engine.** `cassette.py` loads the Claude Code raw-body side channel into model-call envelopes with three verification keys (exact, normalized under profile `claude_code_v1`, delta). `match.py` implements S1: a positional cursor per conversation, keyed by Anthropic message-thread ids or, for non-threaded transports, by the tool_result ids the request answers; verified by hash; misses recorded as divergences with field diffs and never masked. `server.py` speaks the Messages API streaming protocol and serves recorded responses. `scripts/run_proof_g.py` resets the recorded workspace, runs the pinned harness against the server, and measures coverage, request agreement, tool-result agreement and final-tree agreement over N runs.
- **First replay finding (trial 1).** Pointing the pinned 2.1.289 binary at the replay server with a plain API key produced a different harness *configuration* from the recording: no message-thread betas, a different system-prompt variant, 42 tools loaded instead of 16 with deferred loading. Same binary, different entrypoint and feature flags. The replay manifest must therefore pin entrypoint, provider mode, betas and the tool roster, not only the harness version (SPEC-02 §2 run manifest amended; PLAN-14 A-11).
- **Frozen self-replay (final).** Three runs, 11/11 model calls served and delta-verified, 9/9 tool results reproduced by live execution, final workspace identical to the recording, 3.2 s per replay. Disclosed: configuration drift on every call (the harness resolves prompt variant, betas and tool roster remotely), and one post-completion request caused by subagent-notification timing. Full report in `docs/phase0/proofs/proof-G-replay.md`; SPEC-02 amended (PLAN-14 A-11).

- **OpenAI Agents SDK (Proof B, second harness).** A scripted model drives a real `Runner.run` with function tools, a failing tool, a handoff, an input guardrail, two `needs_approval` interruptions (one approved, one rejected, then resume) and both model and session compaction, all without an API key. The tracing processor and hooks adapters map 59 of 70 native signals, 9 are structural (identity only) and 2 are unmapped: the guardrail span and an app-defined custom span. Gaps the SDK leaves: no tool call id on function spans, no approval event (rejections before resume emit nothing), trace end is not run end, no compaction event, no normalized finish reason.
- **Replay gate (Proof G2).** The proofD and proofE cohorts were re-recorded with the recorder wrapper (18 runs, 121 model calls) and replayed three times each: R2 on 83% of failures and 100% of successes, gate met. The two misses were runs whose agent read the recorder's files inside the workspace; the recorder now writes to a sibling directory. `docs/phase0/proofs/proof-G2-replay-gate.md`.

## 5. Exit criteria (PLAN-04 Phase 1, restated)
- [ ] OSS: 2,000 weekly active local-UI sessions or 500 distinct organizations; median install-to-first-insight under ten minutes.
- [ ] Instrumentation overhead under 3% wall time; under 1% unparseable events on partner traffic.
- [ ] Detectors: at least 5 of 10 at precision over 0.9 on partner production data; partners confirm at least 20 real failures they had not seen.
- [ ] Partners: 6 of 8 still streaming at month 9 and asking for the incident view.
- [x] Replay (carried from SPEC-02 §11): R2 on 80% of recorded failures (83% measured, Proof G2); [ ] R3 on 50% under container isolation.

## 6. Risks watched this phase
M9 (largest fleets build in-house) and M10 (Datadog Agent Console as default fleet monitor) from PLAN-09; T-risks on replay fidelity (SPEC-02 §5) now measured rather than assumed.
