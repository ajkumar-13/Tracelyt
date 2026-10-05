# Goldman Sachs: "hundreds of Devins" scaling toward thousands beside ~12,000 developers, with the CIO on record that the firm is "still assessing what additional controls it needs" for agentic AI

evidence_grade: C (re-searched in pass 2; now rests on the CIO's own on-record statements to CNBC, Fortune and Forbes, reached through search snippets, plus a Goldman Sachs podcast page whose transcript could not be read. Not B because every fact arrives via press and nothing describes the engineering harness, an incident, telemetry or cost control for the coding agents.)

**Pass-2 note.** The pass-1 file relied on a secondary research corpus. This version replaces it with the underlying interviews (CNBC 11 Jul 2025, Fortune 19 Mar 2025, CNBC 6 Feb 2026, Forbes 6 Aug 2026), all reached through snippets because the domains are egress-blocked. A Goldman-hosted primary (the "AI Exchanges" podcast with Marco Argenti, recorded 6 Mar 2025) exists but its transcript was not retrievable. Claims that only a low-quality secondary source makes are marked as such.

```yaml
org: Goldman Sachs
role: unknown (public voices: Marco Argenti, CIO; John Waldron, President)
track: fleet
date: 2026-10-05
interviewer: desk (no interview)
method: desk
harnesses_frameworks: [Devin (Cognition), GitHub Copilot, Gemini Code Assist, GS AI Assistant (internal, on the GS AI Platform), Claude-based operations agents co-developed with embedded Anthropic engineers]
domain: coding   # plus workflow: trade accounting, reconciliation, client onboarding agents
runs_per_day: "unknown; 'hundreds of Devins' initially, 'might go into the thousands, depending on the use cases'; ~12,000 human developers; GS AI Assistant averages >1M prompts per month (secondary)"
failure_definition: unknown
failure_rate_estimate: unknown
cost_per_failed_run: unknown
last_failure:
  symptom: unknown
  detected_by: unknown
  time_to_why: unknown
  attributed_component: unknown
  recurred: unknown
  their_words: ""
harness_change:
  last_change: unknown (Devin pilot announced Jul 2025; Claude operations agents announced Feb 2026 after six months of co-development)
  regression_detection: unknown
  silent_regression_experienced: unknown
  would_pay_to_prevent: unknown
controls_owned (fleets): [permissions]   # stated at platform level: role-based access, entitlements, audit logs, prompt filtering, human-in-the-loop; nothing specific to Devin
tooling_today: [GS AI Platform (hosts models; data-protection, entitlement and data-access controls), GS AI Assistant, Devin, Copilot, Gemini Code Assist]
coding_agent_traces_flow_to: unknown
can_reproduce_failed_run: unknown
has_compared_cohorts: unknown   # Argenti's "three to four times" is a forward-looking estimate, not a measured comparison
most_wanted_question: unknown
data_constraints:
  cannot_leave: unknown   # regulated bank; platform-level data-protection controls stated, but no statement about agent telemetry
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: unknown   # CIO-sponsored; whether engineering platform or a separate AI group holds the Devin budget is not public
credible_contract_size: unknown
automation_limits: "Devin starts on 'low-level' repetitive work (legacy code updates, migrations to newer languages, refactoring, debugging); humans turn problems into prompts and supervise and verify the output. For the Claude operations agents a secondary source reports human approval before ledger posting."
would_allow_pause_stop_on_evidence: unknown
reaction:
  would_use_next_week: unknown
  does_not_believe: unknown
design_partner_candidate: unknown
referrals: []
quotes:
  - q: 6
    text: "Initially, we will have hundreds of Devins [and] that might go into the thousands, depending on the use cases."
  - q: 9
    text: "It's really about people and AIs working side-by-side"
  - q: 12
    text: "Goldman says it is still assessing what additional controls it needs to effectively and safely use agentic AI."
    paraphrase: true
sources:
  - https://www.cnbc.com/2025/07/11/goldman-sachs-autonomous-coder-pilot-marks-major-ai-milestone.html
  - https://fortune.com/2025/03/19/goldman-sachs-cio-ai
  - https://www.cnbc.com/2026/02/06/anthropic-goldman-sachs-ai-model-accounting.html
  - https://www.forbes.com/sites/bernardmarr/2026/08/06/how-goldman-sachs-is-using-agentic-ai-for-software-engineering-at-scale/
  - https://www.goldmansachs.com/insights/goldman-sachs-exchanges/ai-exchanges-cio-marco-argenti-on-the-future-of-ai-in-the-workplace
  - https://techcrunch.com/2025/07/11/goldman-sachs-is-testing-viral-ai-agent-devin-as-a-new-employee/
  - https://www.secureworld.io/industry-news/goldman-sachs-autonomous-coder
  - https://www.americanbanker.com/news/goldman-sachs-marco-argenti-is-3-on-the-most-innovative-people-in-finance
  - https://www.aicerts.ai/news/goldman-sachs-advances-ai-banking-agents/
  - https://www.forbes.com/sites/zennonkapron/2026/04/22/the-governance-gap-that-could-break-financial-markets/
tags:
  harnesses_frameworks: stated (CNBC Jul 2025 for Devin and Copilot; Fortune Mar 2025 for Copilot and Gemini Code Assist; CNBC Feb 2026 for Claude agents)
  runs_per_day: stated (Argenti quote via CNBC snippet; 12,000 developers via CNBC; 1M prompts/month via American Banker, secondary)
  controls_owned: stated at platform level (Fortune snippet: "Encryption, prompt filtering, role-based access, audit logs, human-in-the-loop"); inferred that none is Devin-specific
  automation_limits: stated (CNBC/TechCrunch snippets); the ledger-posting approval claim is from aicerts.ai only (low confidence)
  has_compared_cohorts: inferred (the 3-4x figure is described as an expectation)
  quotes: q6 and q9 verbatim from CNBC/TechCrunch snippets; q12 is the search tool's rendering of Fortune, marked paraphrase
  everything else: unknown
```

## Evidence

- CNBC, 11 Jul 2025: Goldman is testing Cognition's Devin, "expected to soon join the ranks of the firm's 12,000 human developers". Argenti: "Initially, we will have hundreds of Devins [and] that might go into the thousands, depending on the use cases." He estimated Devin "could boost developer output by three to four times" compared with prior AI tools, starting with "repetitive programming tasks including legacy code management, refactoring, and debugging" (https://www.cnbc.com/2025/07/11/goldman-sachs-autonomous-coder-pilot-marks-major-ai-milestone.html; https://www.secureworld.io/industry-news/goldman-sachs-autonomous-coder).
- The same interview framed a "hybrid workforce": engineers "describe problems coherently and turn them into prompts, then supervise the work of AI agents"; Devin is "like a new employee" (https://techcrunch.com/2025/07/11/goldman-sachs-is-testing-viral-ai-agent-devin-as-a-new-employee/).
- Fortune, 19 Mar 2025: engineers (about one in four of 46,000 employees) were the first group given generative-AI tools, "including GitHub Copilot and Gemini Code Assist"; the GS AI Platform carries "risk and compliance controls" for data protection, entitlements and data access; security measures listed as encryption, prompt filtering, role-based access, audit logs and human-in-the-loop; Goldman "is still assessing what additional controls it needs to effectively and safely use agentic AI" (snippet rendering) (https://fortune.com/2025/03/19/goldman-sachs-cio-ai).
- Goldman's president John Waldron cited about 20% productivity gains among developer teams using AI in late May 2025 (https://www.secureworld.io/industry-news/goldman-sachs-autonomous-coder).
- CNBC, 6 Feb 2026: Goldman spent six months with embedded Anthropic engineers co-developing Claude-based agents for transaction reconciliation, trade accounting and client vetting/onboarding; Argenti called them "digital co-workers" (https://www.cnbc.com/2026/02/06/anthropic-goldman-sachs-ai-model-accounting.html).
- A low-quality secondary source adds that Goldman "maintains human approval stages before ledger posting, and every agent action logs to immutable storage with metadata". Not confirmed by CNBC's snippets; treat as unverified (https://www.aicerts.ai/news/goldman-sachs-advances-ai-banking-agents/).
- Forbes (Bernard Marr), 6 Aug 2026: Devin agents "scope projects, write, test, and debug code" alongside 12,000 engineers to modernize legacy IT. The "30 minutes to 1.5 minutes per vulnerability fix" figure in that piece is attributed to another Cognition customer, not Goldman (https://www.forbes.com/sites/bernardmarr/2026/08/06/how-goldman-sachs-is-using-agentic-ai-for-software-engineering-at-scale/).
- Regulatory context: the Federal Reserve's SR 26-2 is reported to exclude agentic AI from the model-risk framework examiners apply to banks (https://www.forbes.com/sites/zennonkapron/2026/04/22/the-governance-gap-that-could-break-financial-markets/).
- A Goldman-hosted podcast with Argenti (recorded 6 Mar 2025) offers a downloadable transcript; it could not be fetched here (https://www.goldmansachs.com/insights/goldman-sachs-exchanges/ai-exchanges-cio-marco-argenti-on-the-future-of-ai-in-the-workplace).
- Nothing public describes a Devin incident, a cost overrun, telemetry export, rules-file ownership or who approves agent permissions.

## What this case says for Gate A

Goldman is the largest disclosed closed-harness coding-agent fleet in regulated finance: hundreds of Devin instances with a stated path to thousands, run by a firm whose CIO has said on record that the controls for agentic AI are still being worked out. That is the condition in which a flight recorder and attribution tooling would matter, but it is a condition, not evidence of pain. No failure, regression, replay or telemetry fact is public, so this row still moves no counter. The platform-level controls Goldman names (entitlements, audit logs, prompt filtering) suggest that any product would have to sit inside its environment; that is inference. The Argenti podcast transcript and any Cognition-published Goldman material are the next sources to mine; the live-interview target is the engineering platform group that operates the Devin fleet.
