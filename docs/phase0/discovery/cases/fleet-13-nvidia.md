# NVIDIA: 30,000+ engineers on Cursor, about 40,000 with Codex, an internal coding-agents team, and its own agent sandbox and audit runtime (OpenShell)

evidence_grade: B (some primary sources: NVIDIA AI Red Team blog, NVIDIA job postings, NVIDIA's OpenShell docs and repo, CEO statements. Usage figures come from vendor case studies. No internal incident or postmortem.)

```yaml
org: NVIDIA
role: unknown (internal "coding agents team"; job postings for Sr Staff SWE – AI Agent Platform and SWE – Agent Simulation & Evaluation)
track: fleet
date: 2026-10-05
interviewer: desk
method: desk
harnesses_frameworks: [Cursor, Codex, Claude Code (NVIDIA ships agent skills to its plugin marketplace), NVIDIA OpenShell (sandbox runtime that runs Claude Code / Codex / OpenCode / OpenClaw)]
domain: coding
runs_per_day: unknown (30,000+ daily Cursor users; ~40,000 employees with Codex access)
failure_definition: unknown
failure_rate_estimate: unknown (Cursor's case study claims defect rates stayed flat while committed code tripled)
cost_per_failed_run: unknown
last_failure:
  symptom: no internal incident is public. NVIDIA's AI Red Team showed a malicious Go dependency writing an AGENTS.md that made Codex insert a 5-minute sleep and hide it from the PR summary (a research demo)
  detected_by: unknown
  time_to_why: unknown
  attributed_component: unknown   # the red-team finding is context/rules-file injection, but it is not an operational failure
  recurred: unknown
  their_words: ""
harness_change:
  last_change: unknown
  regression_detection: unknown (hiring for "Agent Simulation and Evaluation" suggests evals; inferred)
  silent_regression_experienced: unknown
  would_pay_to_prevent: unclear
controls_owned: [hooks, permissions, tool_allowlists, budgets]   # inferred: the platform job lists harnesses, lifecycle hooks, skills, OTel; OpenShell enforces filesystem/network/process policy; the CEO frames token budgets per engineer
tooling_today: [Cursor, Codex, OpenShell (policy sandbox with allow/deny audit log), OTel (named in a platform job posting)]
coding_agent_traces_flow_to: other   # inferred: OTel named as a platform skill and OpenShell keeps its own audit logs; destination stack unknown
can_reproduce_failed_run: unknown
has_compared_cohorts: unknown
most_wanted_question: ""
data_constraints:
  cannot_leave: [unknown]   # "privacy constraints" cited for building internal apps instead of buying; agent-telemetry policy not public
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: ai_platform   # inferred from the coding-agents team and AI Agent Platform org
credible_contract_size: unknown
automation_limits: ""
would_allow_pause_stop_on_evidence: unknown (OpenShell already enforces deny-by-policy at runtime, so NVIDIA accepts automated blocking in principle; inferred)
reaction:
  would_use_next_week: ""
  does_not_believe: ""
design_partner_candidate: unknown
referrals: []
quotes:
  - q: 7
    text: "We're trying to."
    context: "Huang, asked whether NVIDIA is spending about $2B a year on tokens for engineering (via search snippet)"
sources:
  - https://cursor.com/blog/nvidia
  - https://www.techradar.com/pro/cursor-claims-more-than-30-000-nvidia-engineers-commit-3x-more-code-and-make-coding-a-lot-more-fun-than-it-used-to-be-but-is-it-too-good-to-be-true
  - https://openai.com/index/nvidia/
  - https://www.cnbc.com/2026/03/20/nvidia-ai-agents-tokens-human-workers-engineer-jobs-unemployment-jensen-huang.html
  - https://www.tomshardware.com/tech-industry/artificial-intelligence/jensen-huang-says-nvidia-engineers-should-use-ai-tokens-worth-half-their-annual-salary-every-year-to-be-fully-productive-compares-not-using-ai-to-using-paper-and-pencil-for-designing-chips
  - https://developer.nvidia.com/blog/mitigating-indirect-agents-md-injection-attacks-in-agentic-environments/
  - https://github.com/NVIDIA/openshell
  - https://docs.nvidia.com/openshell/latest/about/overview.html
  - https://jobs.nvidia.com/careers/job/893394980306
  - https://jobs.nvidia.com/careers/job/893396993536
  - https://dataconomy.com/2025/10/15/jensen-huang-says-every-nvidia-engineer-now-codes-with-cursor/
tags:
  harnesses_frameworks: stated
  runs_per_day: stated (user counts only)
  controls_owned: inferred
  coding_agent_traces_flow_to: inferred
  budget_owner: inferred
  last_failure.symptom: stated (red-team research, not an incident)
  quotes: stated (search snippet; context paraphrased)
```

## Evidence
- More than 30,000 NVIDIA developers use Cursor daily. Cursor claims committed code more than tripled while defect rates stayed flat. The press calls the 3x figure an unverified vendor claim (https://cursor.com/blog/nvidia ; https://www.techradar.com/pro/cursor-claims-more-than-30-000-nvidia-engineers-commit-3x-more-code-and-make-coding-a-lot-more-fun-than-it-used-to-be-but-is-it-too-good-to-be-true).
- About 40,000 NVIDIA employees have Codex access. An internal "coding agents team" helps engineers adopt the tools and "feeds usage patterns back into how the tools are configured and deployed". That is a central team owning harness configuration (https://openai.com/index/nvidia/).
- Jensen Huang said every NVIDIA software engineer uses Cursor (https://dataconomy.com/2025/10/15/jensen-huang-says-every-nvidia-engineer-now-codes-with-cursor/).
- Huang suggested engineers should consume tokens worth about half their salary, and on roughly $2B a year of engineering token spend said "We're trying to." Cost is treated as an investment, not a control problem (https://www.tomshardware.com/tech-industry/artificial-intelligence/jensen-huang-says-nvidia-engineers-should-use-ai-tokens-worth-half-their-annual-salary-every-year-to-be-fully-productive-compares-not-using-ai-to-using-paper-and-pencil-for-designing-chips ; https://www.cnbc.com/2026/03/20/nvidia-ai-agents-tokens-human-workers-engineer-jobs-unemployment-jensen-huang.html).
- NVIDIA's AI Red Team showed a compromised Go library detecting Codex (via CODEX_PROXY_CERT) and writing an AGENTS.md that made the agent add a 5-minute sleep and hide it from PR summaries. OpenAI judged it no worse than a compromised dependency (https://developer.nvidia.com/blog/mitigating-indirect-agents-md-injection-attacks-in-agentic-environments/).
- NVIDIA ships OpenShell, an open-source runtime that runs Claude Code, Codex, OpenCode and OpenClaw unmodified inside kernel-level sandboxes. Each sandbox has its own YAML policy, and every allow/deny decision is logged with destination, binary and reason (https://github.com/NVIDIA/openshell ; https://docs.nvidia.com/openshell/latest/about/overview.html).
- The "Sr Staff SWE – AI Agent Platform" posting asks for experience with "harnesses, lifecycle hooks, skills configurability, observability (OTEL), and memory services" (https://jobs.nvidia.com/careers/job/893394980306).
- A separate posting exists for "Senior Software Engineer, Agent Simulation and Evaluation" (https://jobs.nvidia.com/careers/job/893396993536).

## What this case says for Gate A
NVIDIA has the largest disclosed closed-harness fleet in this set, and a central team explicitly tunes how those tools are configured. That is the buyer persona. It is also building the adjacent layers itself: OpenShell already provides a policy-enforced sandbox with a full allow/deny audit trail, and its job postings cover OTel, hooks and agent simulation/evaluation. NVIDIA therefore looks more like a platform competitor, or the substrate our recorder would plug into, than a buyer. The only failure evidence is red-team research on AGENTS.md injection, which fits our "context/rules-file" attribution class but is not a reported production regression. Public data gives no basis for any Gate A counter. Cost discipline is explicitly not a pain point.
