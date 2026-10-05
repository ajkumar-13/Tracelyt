# SPEC-04 — Runtime Control (design only), v0.1

**Version:** 0.1.0 · **Status:** APPROVED v0.1 design (founder approval 2026-10-05); implementation spec at Phase 2 · **Owner:** Runtime Control · **Depends on:** SPEC-03, SPEC-05, PLAN-11 P20, D-017/D-018/D-030

## 1. Position
Runtime control is a capability of the engine, not the category (D-030). It arrives after detector precision, attribution accuracy and rollback reliability are measured per fleet (PLAN-04 Phase 3 to 4). Nothing autonomous ships before measurement.

## 2. Inputs and flow
Inputs: policy (versioned), current execution state (from the event stream), detector findings, incident intelligence, identity, risk level. Flow: runtime event → detectors → policy engine → risk evaluation → low risk: intervention adapter; high risk: human approval → adapter → runtime. Every step audited.

## 3. Intervention catalogue and risk levels
| Level | Interventions | Gate |
|---|---|---|
| 0 Observe | record, annotate | always |
| 1 Advise | warn (hook `additionalContext` or `systemMessage`), require extra verification before completion | detector precision ≥ 0.9 on the fleet |
| 2 Slow | pause, request human, reduce budget, lower effort | plus false-positive rate measured over a defined window |
| 3 Restrict | deny a specific tool call, restrict permission scope, disable a tool or MCP server for the run | plus attribution accuracy and rollback reliability measured |
| 4 Stop or change | stop agent, switch model, roll back harness configuration, quarantine memory entry | per-fleet readiness gate (PLAN-04 Phase 4) and human approval until proven |

## 4. Enforcement points (integrate, do not build a gateway)
Closed harnesses expose synchronous decision points: Claude Code and Codex `PreToolUse` and `PermissionRequest` hooks (allow, deny, ask, defer, rewrite input, add context), Gemini CLI `BeforeTool`/`BeforeModel`, Cursor `beforeShellExecution`/`beforeMCPExecution`. Tier A frameworks expose approval interrupts (PydanticAI deferred tools, LangGraph interrupts, Agents SDK guardrails, Vercel `needsApproval`). Gateways and security products (Portkey/Prisma AIRS, Galileo Agent Control with `deny | steer | observe`, LangSmith Fleet inbox) enforce at the network or runtime layer; we emit evidence-derived policies to them rather than replacing them.

## 5. Policy language (design constraints)
Explicit, versioned, reviewable; never embedded in a prompt. Conditions reference detector findings, event attributes and identity (e.g. `D4.iterations ≥ 6 AND tool.failed ≥ 2 AND no verify.passed → level 2 pause`). Each rule declares its risk level, fail mode (fail-open, fail-closed, degrade-to-human), approver role, and rollback. Policies are versioned harness components and appear in `versions.policy`.

## 6. Control audit
Trigger, policy version, evidence event ids, decision, actor (policy or human), execution result, rollback possibility and outcome, latency. Immutable.

## 7. Readiness gate (per fleet)
Detector precision and false-positive rate on that fleet; attribution accuracy on reviewed incidents; rollback reliability in replay; control-path availability and latency; zero production incidents caused by false-positive interventions over the measurement window before levels 3 and 4 are enabled.

## 8. Open questions
1. Which hook decision controls are stable enough across Claude Code and Codex releases to rely on for level 3.
2. Whether evidence-derived policies are exported to security products as code (OPA-style) or as advisories.
3. Latency budget for synchronous hook-based interventions (hook timeouts default 600 s, 30 s on some events).
