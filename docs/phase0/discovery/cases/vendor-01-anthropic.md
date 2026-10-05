# Anthropic (Claude Code / Agent SDK): two public postmortems show harness changes, not weights, silently degrading quality for weeks

evidence_grade: A

```yaml
org: Anthropic
role: harness vendor (Claude Code CLI, Claude Agent SDK, Claude Code on the web / Managed Agents)
track: vendor
date: 2026-10-05
interviewer: desk-research agent (vendor track)
method: desk
harnesses_frameworks: [Claude Code, Claude Agent SDK]
domain: coding
runs_per_day: unknown
failure_definition: "quality degradation reported by users: shorter answers, forgetfulness, repetition, odd tool choices, faster usage-limit burn"   # stated (April 2026 postmortem)
failure_rate_estimate: "Aug-Sep 2025: ~30% of Claude Code users had at least one misrouted request; Apr 2026 verbosity prompt: 3% drop in code-generation quality on broader evals"   # stated
cost_per_failed_run: unknown
last_failure:
  symptom: "Six weeks (Mar 4 - Apr 20, 2026) of degraded Claude Code quality from three overlapping changes: default reasoning effort high->medium, a thinking-pruning cache bug that dropped prior reasoning every turn, and a system-prompt line capping text between tool calls at 25 words"   # stated
  detected_by: user
  time_to_why: "weeks overall; caching bug alone took 'over a week to discover and confirm the root cause'"   # stated
  attributed_component: context            # caching/thinking-pruning bug (context), plus prompt and model_effort; vendor states the model weights were not the cause
  recurred: yes                              # second public quality postmortem in ~8 months (Sep 2025 was infrastructure, Apr 2026 harness)
  their_words: "After multiple weeks of internal testing and no regressions in the set of evaluations we ran, we felt confident about the change."
harness_change:
  last_change: "2026-04-16 system-prompt verbosity instruction (reverted 2026-04-20)"
  regression_detection: evals               # evals existed but missed it; detection was production_users
  silent_regression_experienced: yes
  would_pay_to_prevent: unknown             # vendor builds in-house; no public statement about buying
controls_owned (fleets): n/a (vendor) ; exposes to customers: [rules_files (CLAUDE.md), hooks, permissions, mcp_servers, tool_allowlists, model_effort, managed settings, OTel export]
tooling_today: [internal per-model eval suites, ablations, dogfooding, gradual rollout, soak periods (promised), /feedback transcripts, session quality surveys]
coding_agent_traces_flow_to: other          # vendor emits OTLP metrics/logs/spans (beta) to any customer backend; internal destination unknown
can_reproduce_failed_run: partially        # postmortem: unrelated experiments made reproduction hard
has_compared_cohorts: unknown
most_wanted_question: unknown
data_constraints:
  cannot_leave: [prompts, code]              # inferred: from customer side, ZDR offering and redaction defaults; vendor side unknown
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: unknown
credible_contract_size: unknown
automation_limits: "permission modes, managed settings, hooks; trust dialog before project hooks/MCP after CVE-2025-59536"
would_allow_pause_stop_on_evidence: unknown
would_emit_standard_signal: yes             # already emits OTLP with partial gen_ai.* attributes on beta spans
reaction:
  would_use_next_week: unknown
  does_not_believe: unknown
design_partner_candidate: unknown
referrals: []
quotes:
  - q: 11
    text: "After multiple weeks of internal testing and no regressions in the set of evaluations we ran, we felt confident about the change."
  - q: 10
    text: "We will run a broad suite of per-model evals for every system prompt change to Claude Code."
  - q: 15
    text: "Two unrelated experiments made it challenging for us to reproduce the issue at first"
  - q: 10
    text: "we'll ensure that a larger share of internal staff use the exact public build of Claude Code."
  - q: 2
    text: "Expanding our continuous monitoring of evaluation transcripts for unexpected behavior"
sources:
  - https://www.anthropic.com/engineering/april-23-postmortem
  - https://www.anthropic.com/engineering/a-postmortem-of-three-recent-issues
  - https://simonwillison.net/2025/Sep/17/anthropic-postmortem/
  - https://www.infoq.com/news/2026/05/anthropic-claude-code-postmortem/
  - https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
  - https://research.checkpoint.com/2026/rce-and-api-token-exfiltration-through-claude-code-project-files-cve-2025-59536/
  - https://advisories.gitlab.com/pkg/npm/@anthropic-ai/claude-code/CVE-2026-21852/
  - https://code.claude.com/docs/en/data-usage
  - https://www.anthropic.com/news/investigating-incidents-cybersecurity-evals
  - https://nvd.nist.gov/vuln/detail/CVE-2025-55284
  - https://nvd.nist.gov/vuln/detail/CVE-2026-54316
  - https://code.claude.com/docs/en/monitoring-usage
tags:
  failure_definition: stated
  failure_rate_estimate: stated
  last_failure.symptom: stated
  last_failure.detected_by: stated ("users began reporting that Claude Code felt less intelligent")
  last_failure.time_to_why: stated
  last_failure.attributed_component: inferred (three components: model effort config, context/caching, prompt; we pick context for the longest-hidden bug)
  last_failure.recurred: inferred (two postmortems)
  harness_change.regression_detection: stated (evals ran and missed it)
  silent_regression_experienced: stated
  coding_agent_traces_flow_to: stated (OTLP export documented) / inferred (internal)
  can_reproduce_failed_run: stated
  data_constraints.cannot_leave: inferred
  would_emit_standard_signal: stated (gen_ai.system, gen_ai.request.model, gen_ai.tool.call.id on spans; see research/02 sec 2.6)
```

## Evidence
- April 23, 2026 postmortem "An update on recent Claude Code quality reports": three separate changes (default effort high to medium on Mar 4; clear-thinking cache bug Mar 26 - Apr 10; verbosity prompt Apr 16 - 20) compounded into weeks of degraded quality; usage limits were reset for subscribers (https://www.anthropic.com/engineering/april-23-postmortem ; https://www.infoq.com/news/2026/05/anthropic-claude-code-postmortem/).
- Detection was by users: "Soon after rolling out, users began reporting that Claude Code felt less intelligent." (https://www.anthropic.com/engineering/april-23-postmortem).
- The verbosity prompt passed internal evals: "After multiple weeks of internal testing and no regressions in the set of evaluations we ran, we felt confident about the change." Broader ablations later showed a 3% drop in code quality (https://www.anthropic.com/engineering/april-23-postmortem ; https://shattered.io/anthropic-claude-code-quality-drop-explained-2026/).
- The cache bug was masked during testing by an internal-only server-side experiment and a thinking-display change, and "it took us over a week to discover and confirm the root cause" (https://www.anthropic.com/engineering/april-23-postmortem).
- Promised changes: per-model eval suite for every system-prompt change, continued line-level ablations, more staff on the exact public build, gradual rollouts, soak periods for intelligence-affecting changes (https://www.anthropic.com/engineering/april-23-postmortem).
- Sep 2025 postmortem (infrastructure, not harness): context-window routing error hit ~30% of Claude Code users; promised "more sensitive evaluations", continuous quality checks on true production systems, and faster debugging tooling for community feedback (https://www.anthropic.com/engineering/a-postmortem-of-three-recent-issues ; https://simonwillison.net/2025/Sep/17/anthropic-postmortem/).
- Anthropic's Jan 2026 evals guide says Claude Code evals started from employee and user feedback, then narrow evals (concision, file edits), then behaviour evals (over-engineering); capability evals "graduate" into regression suites (https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents ; https://gist.github.com/pebeto/76c1e61120cb27445d53a00459db5fc8).
- CVE-2025-59536 (CVSS 8.7): hooks and MCP servers defined in a repo's .claude/settings.json ran before the trust dialog; CVE-2026-21852: ANTHROPIC_BASE_URL in project settings exfiltrated API keys pre-trust (https://research.checkpoint.com/2026/rce-and-api-token-exfiltration-through-claude-code-project-files-cve-2025-59536/ ; https://advisories.gitlab.com/pkg/npm/@anthropic-ai/claude-code/CVE-2026-21852/).
- Eval-harness incidents (disclosed Jul 30, 2026): reviewing 141,006 evaluation runs where Claude could reach the internet, Anthropic found three incidents in which models in misconfigured third-party cyber-eval environments hit real organisations (one published malicious code to PyPI that ran on 15 real systems); review began Jul 23 only after OpenAI's own disclosure. Promised: "Expanding our continuous monitoring of evaluation transcripts for unexpected behavior", better investigation tooling, vendor assurance (https://www.anthropic.com/news/investigating-incidents-cybersecurity-evals).
- Other permission-boundary CVEs: CVE-2025-55284 (allowlisted ping/dig/nslookup used to exfiltrate secrets over DNS, fixed v1.0.4) and CVE-2026-54316 (CI-wired Claude Code exfiltrating secrets via pre-approved Hugging Face access, fixed v2.1.163) (https://nvd.nist.gov/vuln/detail/CVE-2025-55284 ; https://nvd.nist.gov/vuln/detail/CVE-2026-54316 ; https://github.com/swarmproof/agent-postmortems/tree/main/incidents).
- Data: commercial standard retention 30 days; ZDR for Claude Code "enabled on a per-organization basis by your account team"; transcripts kept locally in plaintext 30 days; telemetry to Anthropic off by default on Bedrock/Vertex/Foundry (https://code.claude.com/docs/en/data-usage).
- Feedback path for regressions: opt-in "Can Anthropic look at your session transcript" upload after quality survey (retained up to 6 months); /feedback transcripts retained 5 years; survey ratings can be routed to the customer's own OTel collector (https://code.claude.com/docs/en/data-usage).
- Native OTel: OTLP metrics/logs plus beta spans carrying gen_ai.system, gen_ai.request.model, gen_ai.tool.call.id (https://code.claude.com/docs/en/monitoring-usage ; see docs/phase0/research/02-claude-code-surfaces.md sec 2.6).

## What this case says for Gate A
This is the strongest public proof that harness-component changes (effort default, context pruning, one system-prompt line) cause silent regressions that the vendor's own evals miss and users detect first. It validates the "CI regression gate of harness changes" and "component attribution" thesis, but it also shows that the vendor answered by building it in-house (ablations, soak, gradual rollout), so Anthropic is a channel/standard partner, not a buyer. The customer-side gap is real: a customer saw the degradation weeks before Anthropic named a cause and had no instrument to attribute it to effort vs. context vs. prompt. Anthropic already emits OTLP with some gen_ai attributes, so a convention that maps to its existing fields is plausible; native adoption of a startup's schema is unlikely without OTel SIG backing.
