# Desk-Research Discovery: Method and Limits (Phase 0, decided 2026-10-05)

## 1. What changed
PLAN-04 Phase 0 called for fifty live interviews (twenty open-harness builders, twenty closed-harness fleet operators, ten harness vendors) feeding the Gate A counters in `02-synthesis-template.md`. On 5 October 2026 the founder directed that the questions be answered from the public record instead: engineering blogs and postmortems, conference talks, GitHub issues on the harness repositories, research papers, industry surveys and vendor case studies. This document records how that was done, what it can and cannot establish, and how the counters are reported.

## 2. Method
- **Unit of evidence.** One *case* per organization, filed as `cases/<track>-<NN>-<org>.md` using the same YAML as the interview synthesis template, plus `method: desk`, `evidence_grade`, `sources` and a `stated` / `inferred` / `unknown` tag per fact. Fifty cases: builder-01..20, fleet-01..20, vendor-01..10.
- **Aggregate evidence.** `06-quantitative-evidence.md` collects survey and paper figures per interview question (failure rates, time to root cause, attribution, telemetry routing, data residency, budget owners, evaluation adoption). `07-github-issue-corpus.md` and `.csv` classify public issues on Claude Code, Codex, Gemini CLI, Cline, OpenCode, goose, LangGraph, CrewAI, the OpenAI Agents SDK, AutoGen and ADK as stand-ins for the "last failure" questions.
- **Targets.** Cases start from `research/09-interview-targets.md`; a target without usable public evidence on failures, evaluation or harness changes is replaced by one that has it, and the substitution is recorded in the case file.
- **Grades.** A = primary postmortem, talk or paper with specifics; B = primary but thin; C = secondary press or inference only. Counters are reported with and without C-grade cases.
- **Network constraints.** The research ran from a container whose egress policy allowed web search snippets, github.com pages (individual issues, discussions, READMEs; not search listings), anthropic.com, code.claude.com, datadoghq.com and cloud.google.com. Most blogs, arXiv, press and social sites were not fetchable; facts from those come from search snippets of the cited URL and are graded accordingly.
- **Rules.** No invented facts, names, numbers or quotes; quotes are verbatim from a fetched page or snippet or marked as paraphrase; every fact cites a URL.

## 3. What desk research can and cannot establish
| Interview question | Desk research | Note |
|---|---|---|
| Q1–Q5 last failure, detection, time to why, attribution, recurrence | **Yes, partially.** Postmortems, talks and GitHub issues describe real failures with the author's own attribution. | Survivorship: only failures someone chose to write up. |
| Q6–Q8 fleet size, failure rate, invisible failures | **Volumes yes; rates rarely.** Surveys give population-level rates. | "Failures nobody sees" is by definition under-reported. |
| Q9–Q12 harness composition, changes, silent regressions, controls owned | **Yes for vendors and well-documented builders.** Vendor postmortems (quality regressions after harness or routing changes) are the strongest evidence class. | Fleet-level control ownership is usually inferred from product documentation. |
| Q13–Q17 tooling, trace routing, reproduction, cohort comparison, most-wanted question | **Partially.** Tooling is often named; reproduction and cohort comparison are almost never discussed publicly. | |
| Q18–Q21 data constraints, replay hosting, budget owner, automation limits | **Only in aggregate.** Surveys give residency and budget-owner distributions; hosting replay is unanswerable from the public record. | Replay counter reported as a proxy. |
| Q22–Q24 reaction, design partnership, referrals | **No.** | Carried to Phase 1 design-partner recruiting. |

## 4. How the Gate A counters are reported
`00-counters.md` reports each counter three ways: *stated* (the source says it), *stated + inferred*, and *proxy* where the counter cannot be observed. The proxies are declared:
- "Described a harness regression they would pay to prevent" → **described a harness regression with material cost** (money, outage, lost data, engineering time), with willingness to pay marked unknown.
- "Would host replay inside their environment" → **runs agents in self-hosted or customer-controlled sandboxes already, or states that code/prompts cannot leave**; a necessary, not sufficient, condition.
- "Design-partner candidates" → **has a public owner of the agent platform and public, unsolved pain in our scope**; a target list, not a commitment.
The PLAN-09 §6 kill triggers (fewer than 8 of 50 show pain; fewer than 5 of 50 will host replay) are evaluated against the stated counts only; proxies are reported alongside and never used to pass a gate.

## 5. What is carried into Phase 1
The twelve-plus design-partner candidates are recruited in Phase 1 month 1 with the outreach kit in `03-outreach-and-tracking.md`; the first live conversations re-ask Q18–Q24 and replace the proxies. The GitHub issue corpus becomes a seed for the public failure corpus (SPEC-07) and for the detector catalogue (SPEC-03).
