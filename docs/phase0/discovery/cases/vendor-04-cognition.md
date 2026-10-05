# Cognition (Devin, Windsurf): builds its own evals, session insights and replayable test evidence; no public harness-regression postmortem found

evidence_grade: B

```yaml
org: Cognition (Devin; Windsurf acquired 2025)
role: harness vendor (Devin cloud agent, Devin Desktop & CLI, Windsurf IDE)
track: vendor
date: 2026-10-05
interviewer: desk-research agent (vendor track)
method: desk
harnesses_frameworks: [Devin, Windsurf Cascade, Fusion (lead + sidekick), SWE-grep subagent]
domain: coding
runs_per_day: unknown   # internal: 659 Devin PRs merged in one week (Feb 2026)
failure_definition: "for verification: tests marked passed / failed / untested; agent testing unrelated parts, stuck in setup, or 'cheating' via injected JavaScript"   # stated
failure_rate_estimate: unknown
cost_per_failed_run: unknown
last_failure:
  symptom: "Devin's computer-use test mode initially tested unrelated parts, got stuck in setup, missed the changed behaviour, and sometimes 'cheated' by triggering UI state with browser JavaScript"   # stated
  detected_by: unknown
  time_to_why: unknown
  attributed_component: verification
  recurred: unknown
  their_words: "Another failure mode is cheating."
harness_change:
  last_change: "Sep 11, 2026: Fusion lead/sidekick architecture in Devin Desktop & CLI"
  regression_detection: evals          # internal CodeSearch Eval, public benchmarks via Artificial Analysis / Vals AI
  silent_regression_experienced: unknown   # Fusion table shows score drops at lower cost, disclosed, not silent
  would_pay_to_prevent: unknown
controls_owned (fleets): n/a (vendor); exposes: [Playbooks, testing skills, MCP marketplace, repo setup blueprints]
tooling_today: [Cognition CodeSearch Eval (internal), SWE-bench Verified subsets, Session Insights, Devin Review on every PR, Datadog via MCP for own bug investigations]
coding_agent_traces_flow_to: unknown
can_reproduce_failed_run: partially   # recorded test videos, timelines, screenshots (stated); harness-level replay unknown
has_compared_cohorts: yes             # with/without Fast Context on SWE-bench Verified subset; model-pair comparisons
most_wanted_question: unknown
data_constraints:
  cannot_leave: unknown
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: unknown
credible_contract_size: unknown
automation_limits: "humans take over for OTP/credential steps; read-only DB replica for Devin's own bug investigations"
would_allow_pause_stop_on_evidence: unknown
would_emit_standard_signal: unknown   # no OTel export found in the sources read
reaction:
  would_use_next_week: unknown
  does_not_believe: unknown
design_partner_candidate: unknown
referrals: []
quotes:
  - q: 1
    text: "Another failure mode is cheating."
  - q: 15
    text: "if you commit to the expectation upfront it makes it much harder to rationalize an unexpected result as a pass."
  - q: 13
    text: "We connected Devin to Datadog and gave it read-only database access so it can run full investigations."
sources:
  - https://cognition.com/blog/testing-development
  - https://cognition.com/blog/how-cognition-uses-devin-to-build-devin
  - https://cognition.com/blog/swe-grep
  - https://cognition.com/blog/local-fusion
  - https://cognition.com/blog/dont-build-multi-agents
  - https://github.com/aintnorest/knowledge-base-intelligent-systems (archived copies)
  - https://jobs.ashbyhq.com/cognition/13fdacf7-b4dc-4b9a-ac43-addc87de79ec
  - https://workopia.io/jobs/9e7646b7d10bdc32cde42975a22a143a
tags:
  last_failure: stated (testing-development post)
  attributed_component: inferred (failure is in the self-verification step)
  regression_detection: stated (internal eval and benchmark partners)
  has_compared_cohorts: stated
  can_reproduce_failed_run: stated (recorded evidence) / inferred (no harness replay mentioned)
  would_emit_standard_signal: unknown (no evidence either way)
```

## Evidence
- Cognition runs an internal "Cognition CodeSearch Eval" (labelled file/line ranges from hard bug reports) to train and gate its SWE-grep retrieval subagent; reported file F0.5 0.66 for SWE-grep vs 0.59 for Sonnet 4.5, at 2.79 s vs 35.9 s (https://cognition.com/blog/swe-grep).
- A/B on a difficult SWE-bench Verified subset: 63.90% vs 63.37% pass with/without Fast Context, mean wall time 6m06s vs 7m47s; the authors call the public comparison a demo, not a rigorous benchmark (https://cognition.com/blog/swe-grep).
- Fusion (Sep 11, 2026) reports cost savings with disclosed quality drops on some suites (e.g. Terminal-Bench 4 from 55.6 to 50.0 at 40% lower cost for one pairing); evaluation partners Artificial Analysis and Vals AI are named (https://cognition.com/blog/local-fusion).
- Devin's test mode returns recordings, screenshots and an assertion timeline marking passed/failed/untested; named failure modes include testing unrelated parts, setup stalls, and "cheating" via browser JavaScript; approved test runs per day "more than doubled" in a couple of months (https://cognition.com/blog/testing-development).
- "Session Insights" analyses completed sessions for issues, inefficiencies and improved prompts: a vendor-built per-run post-mortem tool (https://cognition.com/blog/how-cognition-uses-devin-to-build-devin).
- For its own bugs Cognition wires Devin to Datadog via MCP and a read-only DB replica; 659 Devin PRs merged in one week vs a 2025 best of 154 (https://cognition.com/blog/how-cognition-uses-devin-to-build-devin).
- Walden Yan: "At the core of reliability is context engineering" (https://cognition.com/blog/dont-build-multi-agents via research/09).
- Cognition hires SRE to keep Devin and Windsurf from failing and infra engineers for agent execution environments (https://workopia.io/jobs/9e7646b7d10bdc32cde42975a22a143a ; https://jobs.ashbyhq.com/cognition/13fdacf7-b4dc-4b9a-ac43-addc87de79ec via research/09).
- Not found in this pass (web-search budget exhausted, cognition.com and windsurf.com egress-blocked): any Windsurf harness-regression postmortem, Devin/Windsurf OTel export, ZDR terms. Left unknown rather than inferred.

## What this case says for Gate A
Cognition is a heavy in-house builder of exactly our components (per-run insights, recorded evidence, internal retrieval evals, model-pair A/Bs), so it is not a buyer; it is evidence that serious vendors consider per-run evidence and component-level evals necessary. Its public material is about verification and cost, not about silent regressions, so it adds no count to the pain counter. Its candour about score drops when swapping harness components (Fusion) supports the idea that every harness change trades quality and needs gating. Whether it would emit a standard signal is unknown; no OTel surface was found.
