# PLAN-07 — Go-to-Market and Pricing

## 1. Motion

Engineering-led, in the HRCP-00 §61 sequence, compressed by parallel streams:

```
Open spec + instrumentors + Flight Recorder (Phase 1)
      ↓ developer adoption, data in our shape
Design partners across both ICP tracks (Phase 1)
      ↓ production failures, first corpus
Managed incidents + release correlation + replay v1 (Phase 2 commercial launch)
      ↓ paying customers
Regression gate + Harness Reliability Score (Phase 3, the product they cannot ship without)
      ↓ land-and-expand, enterprise
Optimization + control + evidence packages (Phase 4)
```

## 2. Ideal customer profile

### Track 1 — Builders (open harness)
- Custom or framework-based harness in production; runs over five minutes; five or more tools; persistent state; subagents; mutates real systems; verification gates; repeated task classes; meaningful cost per failed run (HRCP-00 §32).
- Examples: AI-native companies running coding, support-action, back-office or research agents on LangGraph, Agents SDK, ADK, PydanticAI, Claude Agent SDK, OpenHands; internal platform teams at enterprises with in-house agent frameworks.
- Buyer: Head of AI Engineering, agent infrastructure lead. Users: agent engineers, SRE.
- Why they buy: they own the harness, so component attribution is directly actionable and the regression gate protects their own changes.

### Track 2 — Fleets (closed harness)
- Platform or developer-productivity team running Claude Code, Codex, Cursor, Devin or Copilot coding agents at fleet scale (hundreds to tens of thousands of sessions per day), often several agents at once.
- Buyer: AI platform lead, head of developer productivity, sometimes security. Users: platform engineers, SRE, security.
- Why they buy: they cannot change the vendor harness but they own the configuration around it (rules files, hooks, permission policies, MCP servers, tool allowlists, models, budgets, CI verification), those regress silently, and the vendors' own analytics stop at usage and ROI. Cross-vendor view that no single vendor will build.

### Track 3 — Harness vendors (strategic)
- Cognition, Cursor, Factory, Replit, Sierra, Lovable and the model labs' agent products.
- Why they engage: the problem at the largest scale; partial internal solutions; their postmortems show missing regression gating; emitting our control events natively is the fastest route to standardization. Terms may trade price for data rights and native emission.

### Non-ideal
Short-lived single-model chatbots and RAG Q&A (HRCP-00 §31). Teams satisfied with Datadog's agent view and no harness changes.

## 3. Design partner program (Phase 1 to 2)

- Eight in Phase 1 (four builders, three fleets, one vendor), fifteen by Phase 2.
- Entry requirements per HRCP-02 §48; weekly failure review; forward-deployed engineer embedded for the first four weeks.
- Partner commitments: stream structural telemetry within four weeks; host replay in their environment; review incidents and divergence hypotheses weekly; tag data rights per corpus item.
- Our commitments: free through Phase 2; named engineers; roadmap input; first access to the regression gate.
- Conversion target: at least 60% of Phase 2 partners become paying customers at launch.

## 4. Positioning and messaging

Primary: **"The reliability engine for the system around the model."**
Supporting: "Find which harness component broke your agents, reproduce it, prove the fix on last week's failures, and stop it from coming back."
Avoid: "AI observability", "LLM monitoring", "control plane", "AI-powered" (HRCP-02 §66; PLAN-05 C-9).

Message by audience:
- Agent engineers: "Stop reading traces. Get the first divergence, the responsible component, and a replay you can run."
- Platform leads: "Gate every harness change against everything that ever broke."
- Security: "We find the harness defect behind the unsafe action and hand your firewall the evidence."
- Executives and risk: "Verified success, unsafe-action rate and regression coverage for every agent fleet, with audit trail."

## 5. Competitive positioning in a sales conversation

| They say | We say |
|---|---|
| "We have Datadog / Dynatrace." | Keep it. We export incidents and the Harness Reliability Score into it. Datadog shows the span; we show which compaction policy caused the span and prove the fix. |
| "We use LangSmith; Engine opens PRs." | Engine attributes to prompts and code within LangChain's world. We attribute to harness components across any framework or closed harness, reproduce the failure, and gate the change against history. |
| "Raindrop already clusters our failures." | Clustering is table stakes now; seven vendors do it. Ask them to replay last week's failures against your new retry policy and show you the success and cost delta. |
| "We test with Patronus / Coval / Braintrust before shipping." | Keep it. Those test on synthetic cases. We test on what actually broke in production and tell you which component to change. |
| "Our vendor (Anthropic, OpenAI, Cursor) gives us analytics." | Usage and ROI, not failures. And you run three agents; nobody at any one vendor will build the cross-vendor view. |
| "We have an agent firewall." | Good. It blocks the action. We remove the defect that made the action likely, and we feed the firewall evidence-derived policy. |
| "Another observability vendor? No." | Payloads never leave your environment. Replay runs in your sandbox. We are a loop, not a dashboard. |

## 6. Pricing architecture

Principles (HRCP-00 §60, HRCP-02 §61 to §64): never price by span alone; know our own cost per million runs, per incident, per replay and per regression suite before fixing prices; move the value metric toward verified autonomous work.

**Phase 2 experiments (with design partners):**
- Platform subscription by tier (team, business, enterprise) covering seats, retention and features.
- **Analyzed runs** as the primary usage meter (not spans, not GB), with structural telemetry only; payload storage customer-side is free to us.
- **Replay compute** and **regression compute** metered separately, pass-through plus margin, since they run in the customer's sandbox or ours.
- **Active incidents** as an optional meter to test whether customers value outcomes over volume.
- Enterprise add-ons: hybrid or self-hosted, controls, governance, advisories, support.

**Reference points from the market (2026):** self-serve tiers cluster at $29 to $249 per month; LangSmith $39 per seat plus $2.50 per thousand traces; Arize Pro $50 plus $0.0008 per span; Braintrust $249 plus $3 per GB; Datadog bills LLM spans only and gives agent and tool spans free; enterprise observability ACVs reportedly $50K to $100K. We should land above that band because the regression gate is a release-process product, not a dashboard: target first enterprise ACVs of $100K to $250K in Phase 3, with the Phase 2 launch at $20K to $60K for teams.

**Decision point:** pricing architecture chosen at Gate H from measured cost data and partner willingness to pay. Until then, published prices are experiments.

## 7. Sales motion by phase

- Phase 1 to 2: founders and forward-deployed engineers sell; inbound from OSS and the benchmark; design partners convert.
- Phase 3: enterprise account executives added (6 by month 18) with solutions engineers; land in one agent team, expand to organization-wide telemetry, regression, shared policy, security, control (HRCP-02 §68).
- Phase 4: partner channel through observability vendors and sandbox providers; procurement via the verified-autonomy evidence package.

## 8. Partnerships

- **Observability vendors (Datadog, Grafana, Honeycomb, Dynatrace):** export incidents, scores and divergence findings into their products; never ask for replacement.
- **Sandbox providers (E2B, Modal, Daytona, Firecracker ecosystem):** replay runner integrations; co-marketing.
- **Framework maintainers:** instrumentor upstreaming; joint benchmark publication.
- **Security vendors (Zenity, Noma, Palo Alto):** evidence-derived policies as input to their enforcement.
- **Harness vendors:** native emission; design-partner terms.

## 9. Launch sequence

1. Phase 1 (month 4 to 6): public spec v0.1, instrumentors, Flight Recorder OSS, benchmark v0.1. Launch narrative: "the first execution record for agent harnesses, with fidelity you can see".
2. Phase 2 (month 12 to 14): managed incidents, release correlation, first divergence, replay v1. Narrative: "from eight million traces to three incidents, each with the component that caused it and a replay you can run".
3. Phase 3 (month 18 to 22): regression gate, Harness Reliability Score, recommendations with deltas. Narrative: "every harness change tested against everything that ever broke".
4. Phase 4: optimizer, control, advisories, evidence packages. Narrative: the HRCP-02 §93 demonstration live on a customer fleet.
