# Company Decisions Package (Phase 0, W8)

**Status (5 October 2026): all recommendations below were accepted by the founder as written.** Items marked "before committing" remain mechanical checks (registrar, counsel) that do not change the decision unless they fail. The decision register in PLAN-11 records D-027, D-043, D-045 (provisional) and D-046 accordingly.

## 1. Name (D-043, DECIDED 2026-10-05, conditional on clearance)

**Recommendation: Kernmantle** (company and product), with specification **Agent Harness Semantic Conventions** (`harness-semconv`, namespace `harness.*`) and recorder CLI **`qar`**.

Evidence (research 08, 40 candidates screened, 12 collision-checked on PyPI, npm, crates.io, Homebrew, GitHub, DNS, trademark search):
- Kernmantle: all package registries free; GitHub org free; `.dev`, `.ai`, `.io` did not resolve (likely buyable; `.com` registered by an unknown owner); only collisions are a niche Haskell library (65★) and a 2020 indie game; no trademark surfaced. Meaning: a climbing rope with a load-bearing sheath (the harness) around a core (the model), built to catch falls. Weaknesses: ten letters, misspelling risk ("kernmantel"), short form "Kern" is taken.
- Alternatives: **Probative** (evidence word; registries free; adjective; in-category micro-repos exist), **Foqa** (aviation Flight Operations Quality Assurance, exactly the job; registries free; `.com/.ai/.io` registered; a `foqa` GitHub user appeared 2026-09-27). Runner-up **Firstfork**.
- Killed because of in-category collisions: Belay, Prusik, Halyard, Bridle, Bowline, Telltale, Corrobo, Evidra, Plumbline, Autoblock (Autoblocks AI competitor), Trueline, Harnex, Provena, Fidra, Backstay (npm package translating Claude Code hooks to events), Fairlead (org with SDKs, "auditable evidence kernel"), Keelson.
- "Tracelyt" is withdrawn: Evidently AI's `tracely` OTel library, tracely.io, Tracely app.
- Spec name caveat: a descriptive name cannot be trademarked; PLAN-06 §6 amended so the company holds only the product mark. Counsel to check Harness Inc.'s HARNESS marks before public use of "harness-semconv".

**Before committing:** registrar check of kernmantle.dev/.ai/.io; USPTO and EUIPO clearance by counsel; purchase attempt on kernmantle.com.

## 2. Open-source license (D-036)
**Decided: Apache 2.0** for all open code; CC-BY-4.0 for spec text and public corpus (SPEC-08 §2, ADR-012). Rationale: adoption is the open layer's job; Elastic License 2.0 (Phoenix) is widely misread; the commercial layer is a separate codebase.

## 3. OpenTelemetry GenAI SIG engagement (PLAN-06 Track 1, plan approved 2026-10-05)
Facts (research 01 §A.6, A.7): every `gen_ai.*` item is Development status; the conventions moved to `open-telemetry/semantic-conventions-genai`; attributes are proposed by YAML PR with weaver tooling; the GenAI SIG meets Mondays 09:00 PT in CNCF Slack `#otel-genai-instrumentation`; the maintainer (lmolkova) paused PR #445 pending prototypes in `opentelemetry-python-genai` (LangGraph, then CrewAI and ADK).
Plan: two engineers at half time from month 1. Join the SIG; contribute prototypes to `opentelemetry-python-genai` because that is what unblocks maintainer review. Proposals in order (SPEC-08 §6): extend PR #535 (`gen_ai.tool.call.decision.source`, `.reason`); context provenance per issue #181 with our observed fields; `gen_ai.context.compaction` event; `gen_ai.agent.stop.reason`; `gen_ai.verification`; agent instance identity aligned with PR #445 and issue #37; participate in issue #320 hook stages with observed HOOK-domain fields. Each proposal ships with a Claude Code capture from `tests/fixtures/claude_code/` as evidence that the field exists in the wild.

## 4. Laminar relationship (D-046, DECIDED 2026-10-05: compete)
Facts (research 07 §4; archive 02): YC S24, $3M seed (Mar 2026, Atlantic.vc), Apache-2.0, Rust app server, ClickHouse; Signals (LLM-defined detectors with online hierarchical clustering); debugger with cache-based LLM replay keyed on input hash, tools not stubbed; agent identity inferred from system-prompt hashes; browser session replay; coding-agent debug loop via an `lmnr-skills` skill. Overlap with us: recorder, detection, clustering, partial replay, coding-agent focus. Gaps: no tool or environment replay, no branching, no regression gate, no harness semantics, no open standard, no closed-harness hook adapters, no fidelity disclosure.
Options:
- **Compete.** Default. Their wedge is ours minus the hard parts; with a 100-engineer plan we out-build them on replay, standard and Tier B adapters within two quarters.
- **Partner.** Low value: they are an observability backend, not an emitter; partnership would mean exporting into them.
- **Acqui-merge.** Attractive if the founders want it: two strong engineers who built a ClickHouse signals pipeline and a replay cache, Apache-2.0 code we could absorb, YC network. Cost at seed stage is small relative to the plan. Risk: their cache-replay design (hash excludes system prompt, latches live) is the opposite of our S1 verified-cursor design and would be discarded.
**Recommendation:** compete by default; open a conversation in Phase 1 once the recorder is public, with acqui-merge as the only partnership form worth pursuing.

## 5. Other decisions surfaced in Phase 0
- **Tier B first harness:** Claude Code (deepest surface, verified in Proof A), then Codex (12 hooks with generated JSON schemas), then Gemini CLI.
- **Second Tier A harness for Proof B:** OpenAI Agents SDK (trace processor insertion, `CompactionItem`, handoff spans, `interruptions`) or LangGraph (callbacks plus checkpoints). Recommendation: Agents SDK first; its processor API is the cleanest insertion point and it exposes compaction and approvals natively.
- **Compaction semantics question for Anthropic:** OTel `compaction.pre_tokens` vs SDK `compact_boundary.pre_tokens` differ (5421 vs 32800); ask through the developer relations channel with the Proof A evidence.
- **PII default:** strip `user.*`, `organization.id`, `ccr.session.id` at the adapter (SPEC-05 T3). Decided.

## 6. Specifications
SPEC-01 to SPEC-08 v0.1.0 were approved for stream build-out on 5 October 2026. Their status lines move from PROPOSED to APPROVED (v0.1, Phase 1 baseline); changes go through the SPEC decision logs and PLAN-14 amendments.

## 7. Discovery program
The founder replaced the 50 live interviews with a desk-research program drawing on public postmortems, talks, GitHub issues, surveys and papers. Method, limits and results: `docs/phase0/discovery/04-desk-research-method.md`, `05-synthesis.md`, `00-counters.md`, `cases/`.
