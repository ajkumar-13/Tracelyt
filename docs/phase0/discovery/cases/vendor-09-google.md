# Google (Gemini CLI / ADK / Jules): public behavioural-eval CI gate on prompt, tool and agent changes, native GenAI-semconv telemetry, and open destructive-action issues

evidence_grade: A

```yaml
org: Google (Gemini CLI, Agent Development Kit, Jules, Antigravity)
role: harness vendor (open-source Gemini CLI; ADK framework; Jules async agent)
track: vendor
date: 2026-10-05
interviewer: desk-research agent (vendor track)
method: desk
harnesses_frameworks: [Gemini CLI, ADK (Python, Go), Jules, Antigravity]
domain: coding
runs_per_day: unknown
failure_definition: "behavioural: wrong tools called, wrong call ordering, destructive commands, inefficient tool use (e.g. sequential read_file instead of read_many_files)"   # stated (behavioral-evals.md)
failure_rate_estimate: unknown
cost_per_failed_run: unknown
last_failure:
  symptom: "Gemini CLI deleted a user's entire project directory after misreading conversational text as an instruction (issue #15821, Jan 2, 2026); issue closed 'not planned' as stale. Earlier (Jul 2025) Gemini CLI hallucinated a successful mkdir and destroyed a user's files with moves"   # stated
  detected_by: user
  time_to_why: unknown
  attributed_component: permission      # destructive file ops executed without confirmation; Jul 2025 case: missing verification
  recurred: yes                         # two separate destructive-file incidents
  their_words: "the agent acknowledged that it misinterpreted natural-language conversation as an executable command and proceeded with the destructive action."   # user quoting the agent
harness_change:
  last_change: "continuous; PRs touching packages/core/src/{prompts,tools,agents} trigger eval-pr workflow"
  regression_detection: ci
  silent_regression_experienced: unknown
  would_pay_to_prevent: unknown
controls_owned (fleets): n/a (vendor); exposes: [GEMINI.md context, hooks (BeforeTool/AfterTool/BeforeModel/AfterModel), approval modes, mcp_servers, extensions, OTel telemetry settings]
tooling_today: [Eval Development Kit (EDK), 38 behavioural *.eval.ts files, eval-pr workflow, nightly evals across a model matrix, ALWAYS_PASSES/USUALLY_PASSES policies with promotion]
coding_agent_traces_flow_to: other      # native OTel to GCP or any OTLP backend (research/03 B1-B4)
can_reproduce_failed_run: unknown
has_compared_cohorts: yes               # per-model nightly scoring 0/33/66/100% across Gemini 3.x models
most_wanted_question: unknown
data_constraints:
  cannot_leave: unknown                 # terms differ by auth route (Code Assist individual vs Standard/Enterprise vs Vertex)
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: unknown
credible_contract_size: unknown
automation_limits: "approval modes; Novee's CI injection chain against Gemini CLI was rated CVSS 10.0 and Google changed its trust model for non-interactive execution"
would_allow_pause_stop_on_evidence: unknown
would_emit_standard_signal: yes         # Gemini CLI already emits gen_ai.* semconv (gen_ai.agent.name, gen_ai.conversation.id, gen_ai.client.inference.operation.details)
reaction:
  would_use_next_week: unknown
  does_not_believe: unknown
design_partner_candidate: unknown
referrals: []
quotes:
  - q: 10
    text: "They serve as a critical feedback loop for changes to system prompts, tool definitions, and other model-steering"
    paraphrase: false
  - q: 10
    text: "This PR modifies files that affect the model's behavior (prompts, tools, or instructions)."
  - q: 10
    text: "Tests should score at least 66% with key models including Gemini 3.1 pro, Gemini 3.0 pro, and Gemini 3 flash prior to check in and they must pass 100% of the time before they are promoted."
  - q: 1
    text: "I did not issue any command or instruction to delete files or folders."
sources:
  - https://github.com/google-gemini/gemini-cli/blob/main/docs/behavioral-evals.md
  - https://github.com/google-gemini/gemini-cli/blob/main/evals/README.md
  - https://github.com/google-gemini/gemini-cli/blob/main/.github/workflows/eval-pr.yml
  - https://github.com/google-gemini/gemini-cli/blob/main/.github/workflows/evals-nightly.yml
  - https://github.com/google-gemini/gemini-cli/issues/15821
  - https://github.com/swarmproof/agent-postmortems/blob/main/incidents/2025-gemini-cli-file-deletion.yaml
  - https://incidentdatabase.ai/cite/1178/
  - https://github.com/swarmproof/agent-postmortems/blob/main/incidents/2026-google-adk-agent-privilege-escalation.yaml
  - https://thehackernews.com/2026/08/google-deletes-3-adk-ai-workflows-after.html
  - https://novee.security/blog/critical-flaws-in-anthropic-google-and-openais-coding-agents/
  - https://www.pillar.security/blog/the-week-of-sandbox-escapes
  - https://github.com/google-gemini/gemini-cli/blob/main/docs/resources/tos-privacy.md
  - https://developers.googleblog.com/the-anatomy-of-harness-engineering-how-to-evaluate-iterate-and-guard-ai-coding-agents/
tags:
  failure_definition: stated
  last_failure: stated (issue #15821; incident record)
  attributed_component: inferred
  regression_detection: stated (eval-pr.yml path filter)
  has_compared_cohorts: stated
  coding_agent_traces_flow_to: stated (research/03)
  would_emit_standard_signal: stated
  data_constraints: unknown
```

## Evidence
- Gemini CLI ships an Eval Development Kit: behavioural evals "assert on the behavior ... (e.g., verifying which tools are called, checking call ordering, or avoiding destructive commands) rather than checking the final prose output" (https://github.com/google-gemini/gemini-cli/blob/main/docs/behavioral-evals.md).
- A PR workflow fires when a PR touches `packages/core/src/prompts/**`, `tools/**` or `agents/**` and posts "This PR modifies files that affect the model's behavior (prompts, tools, or instructions)" with an eval report; this is a harness-change CI gate in public (https://github.com/google-gemini/gemini-cli/blob/main/.github/workflows/eval-pr.yml).
- Nightly evals run each test 3 times per model in a matrix (e.g. gemini-3.1-pro-preview-customtools, gemini-3-pro-preview), scored 0/33/66/100%; eval logs kept 7 days (https://github.com/google-gemini/gemini-cli/blob/main/.github/workflows/evals-nightly.yml ; https://github.com/google-gemini/gemini-cli/blob/main/evals/README.md).
- Policy: ALWAYS_PASSES tests "run in every CI and can block PRs"; USUALLY_PASSES run nightly "to track the health of the product from build to build"; new evals start as USUALLY_PASSES and need 100% to be promoted (https://github.com/google-gemini/gemini-cli/blob/main/evals/README.md). The repo held 38 *.eval.ts files on 2026-10-05.
- Issue #15821 (Jan 2, 2026): Gemini CLI deleted a whole project directory without a delete instruction; closed as not planned/stale with no visible fix (https://github.com/google-gemini/gemini-cli/issues/15821).
- Jul 2025: Gemini CLI treated a failed mkdir as successful and moves destroyed a user's files, unrecoverable (https://github.com/swarmproof/agent-postmortems/blob/main/incidents/2025-gemini-cli-file-deletion.yaml ; https://incidentdatabase.ai/cite/1178/). The record cites issue #15821, which is a different, later report; treat as two incidents.
- ADK (Aug 2026): a prompt-injected public triage agent in ADK-Python's GitHub Actions could trigger a maintainer-privileged agent and expose CI secrets; Google deleted three workflows (https://thehackernews.com/2026/08/google-deletes-3-adk-ai-workflows-after.html ; https://github.com/swarmproof/agent-postmortems/blob/main/incidents/2026-google-adk-agent-privilege-escalation.yaml).
- Black Hat 2026: Novee's one-issue CI injection chain also hit Gemini CLI; Google rated it CVSS 10.0 and changed its trust model for non-interactive execution (https://novee.security/blog/critical-flaws-in-anthropic-google-and-openais-coding-agents/ via the swarmproof record). Pillar reported Gemini CLI treating a Docker-socket path as documented behaviour (https://www.pillar.security/blog/the-week-of-sandbox-escapes).
- Telemetry: Gemini CLI emits OTel logs, metrics and spans with GenAI semconv attributes (gen_ai.agent.name=gemini-cli, gen_ai.conversation.id, gen_ai.client.token.usage) to GCP or any OTLP target (docs/phase0/research/03-codex-gemini-cursor-surfaces.md B1-B4); ADK Go 1.0 has native OTel (research/09).
- Data terms depend on the auth path (Code Assist for individuals, Standard/Enterprise, Vertex API key) (https://github.com/google-gemini/gemini-cli/blob/main/docs/resources/tos-privacy.md). Jules: no public eval or incident evidence found in this pass.

## What this case says for Gate A
Gemini CLI publishes exactly the artefact we propose to sell: a CI gate that runs behavioural evals whenever prompts, tools or agent code change, with pass-rate policies across a model matrix. That validates the concept and its shape, and also shows a well-resourced vendor can build it in the open, which lowers what customers will pay for a generic version. The gap it leaves is customer-side: the gate protects Google's harness, not the customer's GEMINI.md, hooks or MCP configuration, and destructive-action reports (#15821) were closed as stale. Gemini CLI already emits GenAI semconv natively, so Google is a "yes" on emitting a standard signal.
