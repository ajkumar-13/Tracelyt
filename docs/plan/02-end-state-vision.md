# PLAN-02 — End-State Vision: The Harness Engine

This document answers the question: if the hypotheses in HRCP-00 hold, the execution graph is real, first divergence is computable, and replay works, what does the company become, and why does that break from everything in the market?

## 1. The claim

Every agent harness today is designed by intuition and tuned by anecdote. Compaction policies, context budgets, retry limits, tool schemas, permission rules, verification gates, delegation patterns and stop conditions are chosen by an engineer reading a few traces. There is no empirical model of how those choices map to outcomes, because nobody records the harness as a first-class object, nobody links it to trajectories and verified outcomes at fleet scale, and nobody can re-run history against an alternative.

If we build the engine described in HRCP-00 and prove the three hypotheses, we will hold the first such model. The company then stops being a tool that shows engineers what their agents did and becomes the system that **makes harnesses measurably better every week, with proof**. The analogy is not Datadog. It is closer to what compilers and query optimizers did for code and databases: a layer that takes a specification of intent and a corpus of evidence and produces a better execution strategy than a human would hand-write.

## 2. The six capabilities that emerge, in order of arrival

### 2.1 Harness regression CI (Phase 2 to 3)
Every change to a harness, whether a prompt, a compaction policy, a tool schema, a permission rule, a retry limit, a model version or a CLAUDE.md file, is gated by replaying the historical failure corpus and a success control set, and reporting verified success delta, cost delta, latency delta, new failures and fixed failures. This is the SWE-bench-from-your-own-incidents that Cursor built internally and nobody sells.

### 2.2 Harness Reliability Score (Phase 3)
A component-level scorecard for a harness, computed from the execution graph across a fleet:
- Context: fraction of declared or pinned state surviving compaction; reread waste; context growth vs progress.
- Tools: schema failure rate; thrash index; side-effect classification coverage.
- Recovery: retry storms without progress checks; recovery rate after first error.
- Verification: bypass rate (completion claimed without required evidence); evidence strength.
- Delegation: context handed to subagents vs context used; silent subagent stalls.
- Budget and stop: budget spirals; stop-reason distribution.
Think Lighthouse for harnesses. Published as a standard methodology so it can be cited, benchmarked and improved by others.

### 2.3 Recommendations with proven deltas (Phase 3)
Not "consider pinning state". Instead: "Pinning `account_region`, `tenant_id` and `approval_status` through compaction eliminates 92% of incident HR-491's class across 3,412 historical trajectories, with +1.3% median tokens and no regression on the 1,800-run control set. Patch attached. Confidence: high. Evidence: attached." Each recommendation is a replay experiment, not an opinion. This is the output customers will quote in meetings and to their management.

### 2.4 Harness optimization (Phase 4)
Once replay is a reliable simulator for a task class, the harness configuration space becomes searchable: compaction policy and thresholds, context budget allocation, retry and backoff, verification requirements per action class, delegation depth and context sharing, model and effort per step, tool exposure per phase, stop conditions. The engine proposes configurations, replays them against the corpus, and returns a Pareto frontier of verified success against cost and latency (HRCP-01 §63). deepset's finding that harness-only changes move agents 20+ leaderboard positions says the optimization surface is large. Autotuning for harnesses.

### 2.5 Evidence-derived runtime control (Phase 4)
Runtime policies written from measured failure classes rather than from scratch: "at iteration 6 with no state-hash change and two schema failures, pause and require human review" because that pattern preceded 94% of budget exhaustions in this fleet. Interventions carry the incident, the evidence and the rollback plan (HRCP-00 §67). Low-risk interventions first, autonomous high-impact interventions only after detector precision is measured (HRCP-02 §33).

### 2.6 Ecosystem reliability intelligence (Phase 4, opt-in only)
With explicit data rights (HRCP-02 §60), cross-customer patterns become an index of the agent ecosystem's components: "MCP server X v3.1 produces invalid results under concurrent calls", "model Y regresses tool selection when context exceeds N tokens", "framework Z's default compactor drops session constraints". Published as Harness Reliability Advisories, modelled on CVE and on Consumer Reports. No one is positioned to produce this because no one holds cross-vendor, outcome-labelled, component-attributed data.

## 3. What this breaks

| Category | What they sell | What the Harness Engine sells instead |
|---|---|---|
| Observability | See what happened | A loop that changes what happens next, with proof |
| LLM engineering platforms | Cluster failures, open PRs against prompts and code | Attribute to harness components, reproduce, gate the change, measure the outcome |
| Eval and simulation | Confidence before shipping, on synthetic worlds | Confidence from history, on what actually failed in production |
| Agent security | Block the unsafe action | Remove the defect that made it likely; hand the firewall evidence |
| Model labs | A better model | A better system around any model, across labs |
| Harness vendors' internal tooling | Built once, for one harness, by the richest teams | Built for every harness, available to everyone, improving from everyone's evidence |

The strongest version of the claim: **autonomy is gated by evidence, and we become the evidence layer.** Gartner's 40% decommission prediction is a statement that enterprises cannot currently prove their agents are safe to run. A fleet whose harness profile shows 99.2% verified success, zero unsafe actions in a million runs, every incident reproduced and regression-tested, and every intervention audited, is a fleet an enterprise can expand. That is the product that unlocks the next tranche of agent deployment, and it is why the long-term value metric moves toward verified autonomous work (HRCP-00 §60).

## 4. What "making the harness perfect" honestly means

Perfect is not achievable and we should never say it. Three honest statements replace it:

1. **Asymptotic improvement with evidence.** Every material incident becomes a permanent regression case (HRCP-00 §18). Each release is tested against everything that ever broke. The harness ratchets; it does not jump to perfection.
2. **Measured, not assumed.** The Harness Reliability Score makes harness quality a number that can be compared across versions, teams, frameworks and vendors. Today it is not measured at all.
3. **Bounded autonomy, expanding.** Interventions begin as warnings and pauses, and expand as detector precision and attribution accuracy are demonstrated. Humans remain in consequential decisions (HRCP-00 §75).

Also honest: the inferred layer (caused_by, likely_caused_by) will remain probabilistic. The product is designed so that the observed and reconstructed layers deliver value on their own, and the inferred layer adds ranked hypotheses with confidence. If first divergence tops out at, say, 60% top-3 accuracy on real data, the regression CI and the scorecard still work. If it reaches 85%, the optimizer works. The business does not depend on the hardest hypothesis.

## 5. The flywheel, restated with the research

```
Open instrumentors and adapters put the event model in every agent's path
        ↓
Fleets stream structural telemetry; payloads stay customer-side
        ↓
Detectors and incidents label failures at scale
        ↓
First divergence and attribution localize them to harness components
        ↓
Replay reproduces them; fixtures accumulate
        ↓
Regression CI proves fixes; production confirms them
        ↓
Outcome-labelled failure corpus grows (with data rights)
        ↓
Attribution models and the scorecard improve
        ↓
Recommendations and optimization produce better harnesses
        ↓
Better harnesses run more autonomous work
        ↓
More runs, more evidence
```

The only link in that chain nobody else can close is "production confirms them": the label that says whether a fix worked. Observability has traces; eval has test results; only the loop has outcomes.

## 6. Threats to the end state and how the design absorbs them

- **Model vendors absorb the harness** (Claude Managed Agents, OpenAI Frontier). Then the vendors are customers: their own postmortems (Anthropic, Sept 2025: weeks-long undetected degradation hitting ~30% of users) show they lack regression gating too, and enterprises still need cross-vendor evidence. Design the engine so a vendor can run it on their own harness.
- **Frontier models make trace analysis trivial.** Root-cause attribution accuracy collapses as traces grow (Continual Search paper); evidence is sparse and distant from symptoms. Scale, privacy, latency, cost and deterministic evidence still require the engine. Frontier models become a component in our hierarchy (HRCP-00 §13), not a replacement.
- **OTel standardizes our control events.** Welcome it. We are the ones proposing them. The engine competes above the schema.
- **Replay remains low-fidelity for most domains.** Then the regression CI runs at Level 2 to 3 (fixtures without full environment) and the scorecard runs on observed and reconstructed edges only. Both still beat the status quo of no gating and no measurement.
- **Someone funded builds the same loop.** Raindrop, Judgment Labs and Laminar could. Speed on replay and the standard, plus the design-partner corpus, is the only defense. This is why the plan parallelizes with a large team rather than sequencing.
