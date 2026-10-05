# Amp (ex-Sourcegraph): server-side shareable threads that admins can see, "mini evaluations" after every system-prompt change, a documented model-update regression, no-ask tool permissions by default, and an enterprise control plane (MCP allowlist, per-user spend limits, minimal data retention)

evidence_grade: B (pass 2: Amp's own manual, news posts, notes, security reference and podcast, all reached through search snippets because ampcode.com is egress-blocked; specific on practice and controls, no incident postmortem, so not A)

```yaml
org: Amp Inc. (spun out of Sourcegraph, December 2025)
role: harness vendor (Amp CLI, editor extensions, server-side threads, SDK, runners)
track: vendor
date: 2026-10-05
interviewer: desk (no interview)
method: desk
harnesses_frameworks: [Amp (main agent plus subagents: oracle (read-only reviewer on o3, later GPT-5.4), read_thread subagent, search/summarization utility models; "smart" and formerly "free" modes; skills; MCP servers; tool-level permissions)]
domain: coding
runs_per_day: unknown
failure_definition: unknown (internally: regression on "existing behavior you'd like to preserve", measured by evals used "as unit tests and regression tests")
failure_rate_estimate: unknown (oracle eval: response quality 60.8% → 68.2% when moving the oracle to GPT-5.4)
cost_per_failed_run: unknown
last_failure:
  symptom: "A new model update regressed the human developer experience in a SvelteKit/VS Code setting, forcing a choice between preserving human DX and agent DX (podcast episode 10); separately, public discoverable thread sharing was withdrawn because agents read so many files into context that reviewing threads for sensitive snippets became too hard (stated as proactive, not incident-driven)"
  detected_by: dashboard   # inferred: internal dogfooding and evals; the vendor is its own user
  time_to_why: unknown
  attributed_component: model
  recurred: unknown
  their_words: "whenever they find that the agent or model is not responding to something right in the system prompt, they update it and then run a mini evaluation"
harness_change:
  last_change: "Continuous: read_thread rewritten as a subagent (2 Jul 2026); oracle moved to GPT-5.4; permissions defaulted to no-ask ('what was once the --dangerously-allow-all flag is now the default behavior for users who have not configured permissions'); public threads removed; Amp Free paused"
  regression_detection: evals   # stated: evals as regression tests; mini evaluation after each system-prompt change; qualitative week-long model evaluations
  silent_regression_experienced: yes   # stated: a model update regressed behavior they cared about (ep. 10); detection was by use, not by a gate
  would_pay_to_prevent: unknown
controls_owned (fleets): n/a (vendor); exposes to customers [tool-level permissions (allow / reject / ask / delegate to a program), managed user settings, MCP registry allowlist, thread visibility (private / workspace / group / unlisted), workspace entitlements (per-user and team spending limits), minimal or zero data retention, secret redaction]
tooling_today: [internal evals used as regression tests, "mini evaluation" after system-prompt edits, week-long qualitative model evaluations with team notes, dogfooding via shared threads, status page]
coding_agent_traces_flow_to: other   # stated: threads (full agent transcripts) are stored server-side on ampcode.com in a multi-tenant GCP project, shared with the workspace by default, visible to workspace admins
can_reproduce_failed_run: partially   # inferred: full thread transcripts are persisted and referenceable (read_thread), but no replay tooling is described
has_compared_cohorts: yes   # stated: oracle quality measured 60.8% vs 68.2% across models; model-vs-model evaluation weeks
most_wanted_question: unknown
data_constraints:
  cannot_leave: unknown   # Amp stores "partial code data, but not the entire codebase" on its servers; e2b sees code when sandboxes ("orbs") are used
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: unknown
credible_contract_size: unknown
automation_limits: "Amp rejects edit-by-edit approval ('would impede the agentic feedback loop') and manual model switching; default is no permission prompts; customers can define allow/reject/ask/delegate rules per tool and argument; admins can allowlist MCP servers and cap spend"
would_allow_pause_stop_on_evidence: conditional   # inferred: permission rules can 'delegate the decision to another program', which is a hook for evidence-based stops
would_emit_standard_signal: unknown   # binary bundles @opentelemetry/api and reads OTEL_EXPORTER_OTLP_ENDPOINT (pass 1), but no customer-facing OTel export is documented in anything reachable
reaction:
  would_use_next_week: unknown
  does_not_believe: unknown
design_partner_candidate: unknown
referrals: []
quotes:
  - q: 11
    text: "whenever they find that the agent or model is not responding to something right in the system prompt, they update it and then run a mini evaluation"
    paraphrase: true
  - q: 10
    text: "everyone wants to treat evals as some magical oracle for what 'good' is because it seems scientific, but this is actually scientism"
    paraphrase: true
  - q: 21
    text: "Amp will no longer ask for permission before running tools, and what was once the --dangerously-allow-all flag is now the default behavior for users who have not configured permissions."
    paraphrase: true
  - q: 18
    text: "Change thread visibility (private, unlisted, workspace, group). Use --visibility to change who can access the thread."
sources:
  - https://sourcegraph.com/blog/why-sourcegraph-and-amp-are-becoming-independent-companies
  - https://ampcode.com/news/model-evaluation
  - https://ampcode.com/news/oracle
  - https://ampcode.com/news/gpt-5.4-the-new-oracle
  - https://ampcode.com/podcast/episode-10
  - https://ampcode.com/notes/fif
  - https://ampcode.com/notes/permissions
  - https://ampcode.com/news/tool-level-permissions
  - https://ampcode.com/docs/threads
  - https://ampcode.com/news/end-of-public-threads
  - https://ampcode.com/news/read-threads
  - https://ampcode.com/security
  - https://ampcode.com/news/secret-redaction
  - https://ampcode.com/news/workspace-entitlements
  - https://ampcode.com/manual/appendix
  - https://ampcode.com/news/amp-free
  - https://ampcode.com/news/free-agent
  - https://statusgator.com/services/amp-code
  - https://registry.npmjs.org/@ampcode/cli
tags:
  harnesses_frameworks: stated (news posts, manual)
  failure_definition: stated (podcast/evals framing, snippet rendering)
  failure_rate_estimate: stated (oracle eval figures)
  last_failure.symptom: stated (episode 10 summary; end-of-public-threads post); detected_by inferred
  attributed_component: stated (a model update)
  harness_change.last_change: stated
  regression_detection: stated
  silent_regression_experienced: inferred from the episode-10 account (regression noticed in use)
  controls exposed: stated (manual appendix, permissions note, threads docs, entitlements post)
  coding_agent_traces_flow_to: stated (security reference: threads stored in multi-tenant GCP; threads docs: workspace default and admin visibility)
  can_reproduce_failed_run: inferred
  has_compared_cohorts: stated
  cannot_leave: stated partial-code storage; customer constraint unknown
  automation_limits: stated
  would_allow_pause_stop_on_evidence: inferred
  quotes: marked paraphrase where they are the search tool's rendering of ampcode.com text; the --visibility quote is verbatim from the CLI binary (pass 1)
```

## Evidence

- Spinout: Sourcegraph and Amp became separate companies in December 2025; Quinn Slack is Amp's CEO with Beyang Liu among the founders; Amp said it was profitable without giving figures (https://sourcegraph.com/blog/why-sourcegraph-and-amp-are-becoming-independent-companies).
- Model evaluation practice: a "week in the life" of evaluating new models, with running notes from named team members; candidate roles are frontier main-agent model, spiky subagent model, or fast utility model; the team warns that treating evals as "some magical oracle for what 'good' is" is "scientism" because product experience cannot be fully captured in evals (https://ampcode.com/news/model-evaluation).
- Evals are nonetheless used "as unit tests and regression tests, to ensure a new model doesn't regress some existing behavior you'd like to preserve"; after any system-prompt edit the team runs "a mini evaluation" because untested prompt changes "can accumulate" (podcast rendering) (https://ampcode.com/podcast/episode-10; https://ampcode.com/podcast/episode-8).
- A documented regression: in episode 10 the hosts describe a model update that "regressed the human developer experience using SvelteKit in VS Code", forcing a trade-off between human and agent developer experience; they also note the model, more than the system prompt, determines how aggressive the agent is and which tools it uses (https://ampcode.com/podcast/episode-10).
- Oracle: a read-only subagent for review and debugging, first on o3, then GPT-5.4, with "internal evals showing response quality improved from 60.8% to 68.2%" (https://ampcode.com/news/oracle; https://ampcode.com/news/gpt-5.4-the-new-oracle).
- Threads are first-class server-side objects: shareable as private, workspace, group (Enterprise) or unlisted; "If you are in a workspace, threads are shared with workspace members by default, and admins control that default and external sharing"; private threads are still visible to workspace admins; an activity feed lists every visible thread; read_thread lets the agent pull context from past threads and was rewritten as a subagent on 2 Jul 2026 that checks "whether later work revised or reverted what it found" (https://ampcode.com/docs/threads; https://ampcode.com/news/read-threads).
- Public, internet-discoverable thread sharing was removed because, as models read more files into context, "it's becoming too difficult to review threads to ensure they don't contain sensitive file snippets"; stated as proactive, "not prompted by any incident" (https://ampcode.com/news/end-of-public-threads).
- Permissions: rules match tool and arguments and can allow, reject, ask, or "delegate the decision to another program"; built-in defaults apply otherwise; the former --dangerously-allow-all behaviour became the default for users without configured permissions; Amp argues restricting tools makes agents "look for alternatives, like running Bash commands instead" (https://ampcode.com/notes/permissions; https://ampcode.com/news/tool-level-permissions).
- "Frequently Ignored Feedback": no manual model switching (a difficulty dial picks models, prompts, tools and reasoning effort per mode and is updated as models improve); no edit-by-edit approval; threads default to shared because it "reduces the expectation that every thread must be 'perfect'" (https://ampcode.com/notes/fif).
- Enterprise controls: admin controls, minimal data retention, thread visibility controls, per-user cost controls (Workspace Entitlements: default and team-wide spending limits for Enterprise Premium), MCP registry allowlist, managed user settings (https://ampcode.com/manual/appendix; https://ampcode.com/news/workspace-entitlements).
- Data handling: SOC 2 Type II, annual pentest; threads, user data and telemetry stored in a multi-tenant GCP project "including partial code data, but not the entire codebase"; e2b sees code when sandboxes are used; zero data retention for enterprise text inputs, later "zero and minimal data retention policy to all Amp users and workspaces"; a Secret Redaction feature exists; Amp does not train on customer data (https://ampcode.com/security; https://ampcode.com/news/secret-redaction).
- Amp Free (Oct 2025) was ad-supported and initially required opting into training-data sharing, then dropped that requirement, then was paused; ads were targeted on the codebase but "never influence Amp's responses" (https://ampcode.com/news/amp-free; https://ampcode.com/news/free-agent).
- Status history (third-party monitor): thread-creation failures (1 Sep 2026), 500 errors from ampcode.com (26 Aug), app unreachable (25 Aug), elevated errors on OpenAI-backed models (20 Aug). No postmortem was found for any of them (https://statusgator.com/services/amp-code).
- Still unverified: a customer-facing OpenTelemetry export (the CLI binary bundles OTel strings, pass 1) and any eval or incident data shared with enterprise customers.

## What this case says for Gate A

Amp is a vendor that already holds the data Tracelyt wants: every run is a persisted, shareable thread visible to workspace admins, and the agent itself reads past threads for context. Its own regression practice is honest and thin: evals as unit tests, a "mini evaluation" after prompt edits, week-long qualitative model trials, and at least one acknowledged model-update regression found in use. That is a vendor-side "silent regression experienced: yes", attributed to the model. For fleets, the salient facts are that Amp defaults to no permission prompts, lets admins allowlist MCP servers and cap spend, and keeps partial code on its servers; a customer who needs a control plane across Claude Code, Cursor and Amp would have to pull Amp's thread data out, and nothing reachable documents an export. Whether Amp would emit a standard control signal or let a third party see threads is unknown; a live conversation (Slack, Ball) is still needed.
