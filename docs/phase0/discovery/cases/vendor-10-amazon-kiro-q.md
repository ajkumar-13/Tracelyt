# Amazon (Kiro / Q Developer): a poisoned system prompt shipped to users through CI, and an approval gate defeated by one misclassified command

evidence_grade: B

Selection note: chosen over Augment Code and Cline/OpenCode/goose because it has two confirmed, primary-sourced harness incidents (a GitHub security advisory and an AWS bulletin). Augment and Cline had no reachable primary material in this pass (augmentcode.com and cline.bot are egress-blocked and the web-search budget was exhausted).

```yaml
org: Amazon Web Services (Kiro IDE/CLI, Amazon Q Developer)
role: harness vendor (Q Developer IDE extensions and CLI, Kiro spec-driven IDE with agent hooks)
track: vendor
date: 2026-10-05
interviewer: desk-research agent (vendor track)
method: desk
harnesses_frameworks: [Amazon Q Developer, Kiro]
domain: coding
runs_per_day: unknown
failure_definition: unknown
failure_rate_estimate: unknown
cost_per_failed_run: unknown
last_failure:
  symptom: "Jul 2025: a malicious prompt instructing the agent to wipe local files and AWS resources was committed into the open-source Q Developer VS Code extension via an over-scoped GitHub token in CodeBuild and shipped automatically in v1.84.0; it failed only because of a syntax error"   # stated
  detected_by: user          # external security researchers after release
  time_to_why: unknown
  attributed_component: prompt  # system prompt poisoned through the release pipeline
  recurred: yes              # second harness failure a month later: find -exec misclassified as read-only (approval bypass)
  their_words: "This prevented the malicious code from making changes to any services or customer environments."
harness_change:
  last_change: "v1.85.0 (removed malicious code); find reclassified from read-only to mutating"
  regression_detection: unknown
  silent_regression_experienced: yes   # a harness change (system prompt) reached users unnoticed via CI; inferred
  would_pay_to_prevent: unknown
controls_owned (fleets): n/a (vendor); exposes: [Kiro hooks, specs, steering, Powers, enterprise governance controls]
tooling_today: unknown
coding_agent_traces_flow_to: unknown
can_reproduce_failed_run: unknown
has_compared_cohorts: unknown
most_wanted_question: unknown
data_constraints:
  cannot_leave: unknown
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: unknown
credible_contract_size: unknown
automation_limits: "per-command read-only vs mutating classification decides whether approval is required"
would_allow_pause_stop_on_evidence: unknown
would_emit_standard_signal: unknown
reaction:
  would_use_next_week: unknown
  does_not_believe: unknown
design_partner_candidate: unknown
referrals: []
quotes:
  - q: 4
    text: "Amazon Q Developer for Visual Studio Code Extension had an inappropriately scoped GitHub token in their CodeBuild configuration. With that access token, the threat actor was able to commit malicious code into the extension's open-source repository that was automatically included in a release."
  - q: 1
    text: "This prevented the malicious code from making changes to any services or customer environments."
sources:
  - https://github.com/aws/aws-toolkit-vscode/security/advisories/GHSA-7g7f-ff96-5gcw
  - https://www.reversinglabs.com/blog/aws-amazonq-ai-incident
  - https://www.csoonline.com/article/4027963/hacker-inserts-destructive-code-in-amazon-q-as-update-goes-live.html
  - https://github.com/swarmproof/agent-postmortems/blob/main/incidents/2025-amazon-q-wiper-supply-chain.yaml
  - https://embracethered.com/blog/posts/2025/amazon-q-developer-remote-code-execution/
  - https://www.theregister.com/security/2025/08/20/aws-patches-q-developer-after-prompt-injection-rce-demo/827867
  - https://aws.amazon.com/security/security-bulletins/AWS-2025-019
  - https://github.com/swarmproof/agent-postmortems/blob/main/incidents/2025-amazon-q-find-exec-rce.yaml
  - https://github.com/kirodotdev/Kiro
  - https://www.techtarget.com/searchsoftwarequality/news/366639129/AWS-Kiro-user-error-reflects-common-AI-coding-review-gap
tags:
  last_failure.symptom: stated (GHSA; incident record)
  attributed_component: inferred (malicious instruction lived in the agent's prompt)
  recurred: stated (two incidents)
  silent_regression_experienced: inferred (a harness change shipped without detection; security, not quality)
  Kiro outage: unverified (all sources blocked)
```

## Evidence
- GHSA-7g7f-ff96-5gcw (Jul 26, 2025): an "inappropriately scoped GitHub token in their CodeBuild configuration" let an attacker commit code that "was automatically included in a release" (v1.84.0); it failed with a syntax error; fixed in 1.85.0 (https://github.com/aws/aws-toolkit-vscode/security/advisories/GHSA-7g7f-ff96-5gcw).
- The injected content was an agent-directing prompt to delete local files and wipe AWS resources, shipped to an install base of nearly one million (https://www.reversinglabs.com/blog/aws-amazonq-ai-incident ; https://www.csoonline.com/article/4027963/hacker-inserts-destructive-code-in-amazon-q-as-update-goes-live.html ; summarised in https://github.com/swarmproof/agent-postmortems/blob/main/incidents/2025-amazon-q-wiper-supply-chain.yaml).
- Contributing factors in the incident record: "System prompts were not treated as security-critical artifacts in review" and releases were not signed or verified in a way that would flag the injected instruction (same record).
- Aug 2025: Q Developer classified `find` as read-only, so a hidden prompt injection could run `find -exec` without confirmation (PoC launched a Sliver C2 agent); AWS reclassified `find` as mutating in v1.85; no CVE assigned (https://embracethered.com/blog/posts/2025/amazon-q-developer-remote-code-execution/ ; https://www.theregister.com/security/2025/08/20/aws-patches-q-developer-after-prompt-injection-rce-demo/827867 ; https://aws.amazon.com/security/security-bulletins/AWS-2025-019).
- Kiro's public repo is an issue tracker; product docs describe agent hooks, specs, Powers and organisation-wide governance controls (https://github.com/kirodotdev/Kiro).
- Unverified (all sources egress-blocked): Kiro reportedly deleted and recreated an environment, causing a 13-hour AWS Cost Explorer outage in Dec 2025 (FT, Feb 2026), after which Amazon added mandatory peer review (https://www.techtarget.com/searchsoftwarequality/news/366639129/AWS-Kiro-user-error-reflects-common-AI-coding-review-gap via research/09).
- Not found: Kiro/Q eval practices, OTel export, ZDR terms.

## What this case says for Gate A
The Q wiper incident is the starkest example of a "harness change" (a system-prompt edit) reaching every user through CI with no behavioural gate: only a syntax error stopped it. It argues that prompts and tool classifications are release artefacts that need the same diffing and behavioural gating as code, which is our CI-gate thesis, though here the frame is supply-chain security rather than quality. The find -exec bypass shows approval gates failing through one misclassification, which is a component-attribution example (permission classifier). Nothing public shows what Amazon built internally for harness evaluation or whether it would emit a standard signal.
