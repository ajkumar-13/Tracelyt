# PLAN-10 — Metrics and Benchmark

## 1. Company metrics (reported monthly at the gate review)

**Adoption**
- Distinct organizations with the local recorder; weekly active local-UI sessions.
- Emitters of our control events (frameworks, harnesses, vendors), split by native vs our packages.
- Design partners streaming; paying customers; customers running the regression gate on every change.

**Value delivered**
- Real failures surfaced per partner that they had not seen (partner-confirmed).
- Incidents rated real and actionable (partner-rated).
- Regressions prevented before production (documented).
- Measured verified-success improvement attributable to a recommendation.
- Customer release workflows changed because of the platform (HRCP-02 §51).

**Commercial**
- ARR, net revenue retention, ACV distribution, time from partner to paid, gross margin after replay and regression compute.

**Economics (ours)**
- Cost per million analyzed runs; per active incident; per replay; per regression suite (HRCP-02 §61). Published internally before any price is fixed.

## 2. Product and reliability metrics (HRCP-00 §54, made operational)

| Metric | Definition | Target by Phase 3 |
|---|---|---|
| MTTD | Time from first failing run in an incident class to incident creation | Under 15 minutes streaming; under 1 hour batch |
| MTTI | Time from incident creation to a reviewed root-component hypothesis | Under 1 hour automated; partner review within a day |
| MTTRp | Time from hypothesis to a successful replay reproducing the failure class | Under 4 hours where Level 3 fidelity is available |
| MTTFx | Time from reproduction to a regression-validated fix proposal | Under 1 day for recommendations with deltas |
| Repeat incident rate | Incidents whose class recurs after a validated fix | Under 5% |
| Automated root-cause precision | Partner agreement with the top hypothesis | At least 60% at Phase 2, 75% at Phase 3 |
| First-divergence accuracy | Top-3 on controlled benchmark; exact root step on LongRCA-Mini | 70% / 35% at Phase 2; 85% / 45% at Phase 3 |
| Replay reproduction rate | Replays at Level 3 that reproduce the failure class | 75% at Phase 2; 85% at Phase 3 |
| Regression catch rate | Injected harness regressions caught by the gate | 90% on benchmark |
| False-positive incident rate | Incidents partners rate not real | Under 20% at Phase 2; under 10% at Phase 3 |
| Detector precision and recall | Per detector, per HRCP-02 §13 contract | Precision at least 0.9 to ship |
| Unsafe-action prevention rate | Phase 4: policy-prevented actions later confirmed unsafe | Measured before high-impact interventions are enabled |
| Instrumentation overhead | Wall time and memory added by capture | Under 3% wall time |
| Unparseable events | Normalizer failures | Under 1% |

## 3. Fidelity levels (published with the standard)

**Graph fidelity per run**
- G1: tree only (parent-child spans).
- G2: observed edges complete (requests, decisions, delegation, artifacts).
- G3: G2 plus reconstructed context and memory lineage via content addressing.
- G4: G3 plus verification evidence chain and version graph.
- G5: G4 plus inferred edges with confidence from attribution.

**Replay fidelity per run** (HRCP-01 §57, confirmed)
- R1: event-only reconstruction.
- R2: recorded dependency fixtures (model, tool, MCP, network).
- R3: R2 plus filesystem and runtime snapshot.
- R4: near-deterministic sandbox replay.
- R5: full environment replica.

Each run, incident and regression report shows its fidelity level. Marketing never claims a level the fleet is not achieving.

## 4. Harness Reliability Benchmark (HRB)

Owned by Benchmark & Corpus; independent of the teams it grades; public from Phase 1.

**Scope (HRCP-02 §53):** detection, localization, first divergence, root-component attribution, reproduction, fix validation, regression detection.

**Case structure (HRCP-02 §54):** task, environment, baseline harness, mutated harness, injected fault, expected symptom, true first divergence, true responsible component, expected evidence, success criteria.

**Fault library (HRCP-02 §20, §52):** remove context field; change tool schema; modify prompt; change permission; change retry threshold; modify memory; change model; modify verification; change budget; change stop condition; subagent context loss; memory poisoning; compaction policy change; MCP server version change.

**Domains:** coding agents (SWE-bench-style tasks in containers) and API-workflow agents (mocked services) in v0.1; browser, research and computer-use agents later.

**External baselines:** LongRCA-Mini (200 trajectories, public labels) and LongRCA full (1,140); MAST-Data; TRAIL; AgentErrorBench. We report our methods on them alongside our own benchmark so results are comparable to the literature.

**Metrics (HRCP-02 §56):** detection precision and recall; localization distance to ground-truth step; root-component accuracy; incident clustering quality; replay reproduction rate; regression detection accuracy; analysis cost per run and per incident; time to useful diagnosis.

**Rules:** never evaluate diagnosis only by asking another LLM whether it sounds good (HRCP-02 §57); synthetic faults are necessary and insufficient, real production failures with data rights are required before any robustness claim (HRCP-02 §58); the benchmark team publishes quarterly.

## 5. Corpus

Per HRCP-02 §59 and §60: raw execution, normalized events, execution graph, failure symptom, first divergence, root component, root-cause evidence, fix, replay result, regression result, and the production outcome of the fix. Every item carries data rights: internal benchmark, open-source permitted, customer-isolated, training prohibited, training allowed. Corpus growth and the share with outcome labels are reported monthly; they are the leading indicator of whether the moat is forming.

## 6. Standard adoption metrics

See PLAN-06 §8.

## 7. Gate review format

Monthly. Each stream presents: gate criteria, current measurements, evidence source (benchmark, partner data, interviews), and the decision requested (continue, scale, hold, re-plan). The benchmark team presents independently on detector, divergence, replay and model claims. Decisions are recorded as ADRs or decision changes.
