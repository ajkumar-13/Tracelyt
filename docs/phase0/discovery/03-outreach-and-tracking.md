# Outreach Messages and Tracking (Phase 0, W1)

Targets: `docs/phase0/research/09-interview-targets.md` (75 organizations, top 20 ranked). Confirm every row marked (U) and current titles before contact.

## Outreach principles
- Ask for 45 minutes about *their* failures. Do not pitch. Do not say "observability".
- Lead with something specific and public about them (their talk, blog, GitHub issue).
- Offer something back: the Phase 0 findings on Claude Code instrumentation (what hooks and OTel expose) are useful to every fleet operator; the failure-taxonomy mapping is useful to every builder.

## Message: builders (open harness)
Subject: how you debug <agent name> when a run goes wrong

Hi <name>, I read <talk/post> on <harness>. I am researching how teams running long-running, tool-heavy agents find out *why* a run failed (context, tools, permissions, retries, subagents, verification) and how they know a harness change did not quietly regress quality. Not selling anything yet; I am trying to understand the workflow and would share back what we have learned instrumenting Claude Code, Codex and LangGraph at the hook and OTel level. Would 45 minutes in the next two weeks work?

## Message: fleets (closed harness)
Subject: Claude Code / Codex / Cursor at scale: what breaks and who finds out

Hi <name>, <company> runs <agent> across <N> engineers per <source>. I am researching how platform teams detect runaway runs, compaction-related failures and silent regressions after rules-file, hook, permission or model changes, and whether vendor analytics plus Datadog answer "why". I can share a field reference of exactly what Claude Code and Codex expose through hooks and OpenTelemetry, which most teams have not seen in one place. 45 minutes?

## Message: harness vendors
Subject: evaluation and regression infrastructure for <product>

Hi <name>, your <job post / blog> describes <datasets, replay, scoring>. We are building an open telemetry convention and a reliability engine for agent harnesses and are deciding what vendors would want to emit natively. I would value 45 minutes on what you built internally, what you would never let a third party see, and whether your enterprise customers ask for reliability evidence. Happy to share our hook and OTel field reference and failure-taxonomy mapping.

## Tracking
`docs/phase0/discovery/00-counters.md` (create at first interview) holds the weekly Gate A counters from the synthesis template. Interviews are filed as `interviews/YYYY-MM-DD-<org>.md`. Kill triggers at 20 interviews: fewer than 4 describe a harness regression they would pay to prevent, or fewer than 2 will host replay in their environment (PLAN-09 §6).
