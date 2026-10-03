# PLAN-08 — Investor Pitch

Figures are from `docs/research/` and marked where single-sourced or estimated. Update before use.

## 1. One-liners

- "The reliability engine for the system around the model."
- "Agents fail because of the harness, not the model. We find the component, reproduce the failure, prove the fix on history, and stop it from coming back."
- "Harness engineering, with evidence."

## 2. Narrative (three minutes)

Enterprises are deploying autonomous agents and they are failing in production in ways nobody can explain or prevent. Not the model: the harness. The context compactor silently drops the constraint the agent was given. The retry policy has no progress check and burns 1.6 billion tokens overnight. The subagent never gets the decision rationale. Verification is declared without evidence. A production database gets deleted. Gartner now says 40% of enterprises will shut down autonomous agents by 2027 because of exactly these incidents.

Every team already has observability. Eighty-nine percent have it; seventy-one percent of production teams trace every step. It does not help. They can see what happened and still cannot say which component caused it, cannot reproduce it, cannot test a fix against history, and cannot stop it recurring. Seven vendors now cluster failing traces into "issues". Two open PRs against prompts. Observability consolidated into Datadog, Dynatrace, Cisco and ClickHouse this year. Visibility is a feature now.

We are building the layer above it: an engine that reconstructs every agent run as an execution graph of the whole harness, finds where failed trajectories first diverge from successful ones, attributes the failure to a component with evidence, replays it deterministically, proves the fix against last week's failures without new regressions, and gates every harness change in CI. On an open event model that we are driving into OpenTelemetry, for both the harnesses people build and the ones they buy.

The richest teams already built this for themselves. Cursor built checkpoint and fork pipelines and review agents whose mistakes become evaluation cases. Nobody sells it. Nobody has the data it produces: harness configuration, trajectory, failure, root component, fix, and whether the fix worked in production, across vendors. That corpus is the moat. Over time it makes harnesses measurably better every week, with proof, and becomes the evidence that lets enterprises expand autonomy instead of decommissioning it.

## 3. Deck outline (14 slides)

1. **Title and one-liner.**
2. **The failure is the harness.** The 20-component harness diagram (HRCP-00 §6). Research: "Model or Harness?", Jarmak, deepset 20+ positions, Governance Decay 0% to 30%.
3. **Incidents, with dollar signs.** Claude Code 1.67B tokens; compaction double-billing closed "not planned"; $6,000 overnight; Replit production DB; Anthropic's weeks-long undetected degradation hitting ~30% of users; Gartner's 40% decommission prediction.
4. **Observability is saturated and consolidating.** 89% / 71.5%; quality #1 barrier; Arize $915M to Dynatrace, Galileo to Cisco, Langfuse to ClickHouse, Portkey to Palo Alto, Promptfoo to OpenAI; seven vendors cluster failures. "Visibility became a feature."
5. **Fleets are here.** Cursor >50M actions per day; Codex P99 >60 agent-hours per day; Devin 67% merge rate; >1M Copilot agent PRs in four months; Claude Code >$2.5B run-rate, one prompt per session.
6. **The product: the loop.** Capture → graph → detect → incident → first divergence → attribute → replay → regression gate → recommend → control. One screenshot: the incident from HRCP-00 §52.
7. **What nobody ships.** The table from PLAN-01 §4: replay, regression gate, first divergence, component attribution, cross-harness control events, Harness Reliability Score, success-adjusted economics, each with the nearest competitor and their distance.
8. **Open standard as distribution.** The hole in OTel `gen_ai.*`; our proposals; six frameworks plus three CLIs; conformance; "customers arrive with data in our shape".
9. **Both open and closed harnesses.** Tier A, B, C; fidelity disclosure; the Claude Code, Codex and Gemini CLI hook convergence.
10. **The moat is the loop and its corpus.** PLAN-01 §5. The outcome label nobody else collects.
11. **End state.** PLAN-02: regression CI → score → recommendations with deltas → optimization → evidence-derived control → ecosystem advisories → verified autonomy.
12. **Go-to-market and traction plan.** Two ICP tracks plus vendors; design partners; Phase 2 launch; Phase 3 regression gate; targets per gate.
13. **Team and plan.** 100+ engineers in streams; gates fund phases; 36-month roadmap.
14. **The ask.** Round size, use of funds, milestones to next round.

## 4. Market sizing (bottom-up, with sources)

- **Spend context:** enterprise AI spend ~$37B in 2025 (Menlo). Observability and eval startups raised ~$1.1B Jan 2024 to Apr 2026 [single-source]. Agent security is a separate ~$3.6B funding category [single-source].
- **Coding-agent fleets (Track 2):** Claude Code >$2.5B run-rate; Devin ~$492M run-rate (May 2026); Codex >4M weekly users; Copilot 4.7M paid seats. If platform teams spend 3% to 5% of agent spend on reliability tooling (comparable to observability's share of infrastructure spend), coding agents alone imply a $150M to $300M near-term serviceable market, growing with agent spend.
- **Builders (Track 1):** 57% of surveyed teams have agents in production, but only 16% of enterprise deployments are "true agents" (Menlo); the builder population is smaller today and grows as agentic share rises. Enterprise observability ACVs of $50K to $100K are the floor; the regression gate as release infrastructure supports $100K to $250K.
- **Comparables:** Braintrust $800M valuation on evals; Arize $915M exit; Entire $300M valuation on provenance alone; Raindrop ~$50M raised on detection alone. The loop is a superset of each.
- Label every number as an estimate in the deck; the research files carry the sources.

## 5. Why now, in one slide

Harness failures became research consensus in 2026; fleets reached tens of millions of actions per day; observability consolidated into platforms and commoditized clustering; OTel has a hole exactly where control events belong; the closed-harness hook contracts converged; and Gartner put a date on the consequence.

## 6. Competitive FAQ

**Why won't LangSmith Engine do this?** Engine clusters issues and opens PRs against prompts and code inside LangChain's ecosystem. It does not model harness components, does not replay, does not gate harness changes against history, and its distribution is LangGraph. Half our customers run Claude Code or Codex.

**Why won't Datadog do this?** Datadog ingests spans and bills only LLM spans. It has no harness model, no replay, no regression. Its history is to acquire the layer above (Metaplane, Adaptive ML) and it invests in Arize and Patronus. We export into Datadog and are a natural partner or acquirer target, which is a fine outcome but not the plan.

**Why won't Raindrop?** Raindrop detects and clusters production failures and announced pre-ship simulation. They are a strong detection company. They have no event model for harness components, no replay, no open standard, and no coding-agent focus. We should expect them to try; speed on replay and the corpus is the defense.

**Why won't Anthropic or OpenAI?** Their analytics stop at usage and ROI. Their own postmortems show they lack regression gating. Enterprises run three vendors' agents and need a cross-vendor view none of them will build. They are customers and standard adopters, not competitors.

**Why won't Cursor or Cognition sell their internal tooling?** They built it for one harness and sell agents, not infrastructure. They are design partners and the fastest route to native emission.

**Isn't first divergence a research problem?** Yes. The best published method reaches 24% exact root step on real trajectories. Our product delivers value on observed and reconstructed graph layers, the regression gate and the score without it; first divergence adds ranked hypotheses with confidence and improves with the corpus. The business does not depend on the hardest hypothesis.

**Isn't replay impossible with non-deterministic models?** Deterministic replay of recorded fixtures until divergence, then controlled live branching, with fidelity disclosed per run. Level 2 to 3 covers the regression gate; Level 4 is a Phase 3 target for coding. Nobody ships even Level 2 for production runs today.

**Why open source the schema if the corpus is the moat?** Because the schema is distribution and the corpus requires the loop. OpenInference proves a vendor-authored vocabulary can reach 40+ instrumentors; Arize still sold for $915M.

**What kills you?** Customers satisfied with clustered traces; replay economically useless; first divergence providing no value; vendors absorbing the harness and the evidence; buyers putting the budget under security. PLAN-09 has the kill criteria and what we would do.

## 7. The ask and use of funds

Round sized to the 36-month plan in PLAN-03: $80M to $110M, structured as a large seed or Series A with a milestone-based second close at Gate D/E/F (month 15). Use of funds: roughly 70% engineering and research, 15% go-to-market and forward-deployed engineering, 10% infrastructure and compute (sandboxes, replay, benchmark), 5% compliance, legal and data rights.

Milestones to the second close: Gate B and C passed (OSS adoption, detectors validated, eight partners streaming); Phase 2 commercial launch; five paying customers including two at six figures; first-divergence and replay metrics published against the benchmark.

## 8. Risks we will volunteer

Consolidation and incumbent response; standard rejection; replay fidelity ceiling; attribution accuracy ceiling; platform vendors absorbing the harness; security owning the budget; data-rights constraints on the corpus. Each with the mitigation in PLAN-09. Investors who have seen the 2026 exits will ask; answering first is credibility.
