# Desk-research discovery brief (shared by all research agents)

Context: we are a startup building reliability infrastructure for AI agent harnesses
(open telemetry convention + flight recorder, failure detection, incident clustering,
first-divergence analysis, component attribution, replay, CI regression gating of harness
changes: prompts, rules files, hooks, permissions, tools, compaction, model versions).
Phase 0 planned 50 live customer interviews. The founder decided to replace them with
DESK RESEARCH: answer the interview questions from PUBLIC evidence (engineering blogs,
postmortems, conference talks, GitHub issues, papers, surveys, case studies).

Read first (repo /home/user/Tracelyt):
- docs/phase0/discovery/01-interview-guide.md  (the questions)
- docs/phase0/discovery/02-synthesis-template.md (the YAML you fill per case)
- docs/phase0/research/09-interview-targets.md (candidate organizations, with evidence URLs)

## Network reality (tested 2026-10-05)
- WebSearch works and returns rich snippets. Use it heavily, with many specific queries.
- WebFetch WORKS for: github.com (individual issue/discussion/PR/README pages; NOT issue
  search/listing pages, those 403), raw.githubusercontent.com, anthropic.com,
  code.claude.com, datadoghq.com, cloud.google.com.
- WebFetch is BLOCKED (egress policy) for almost everything else: arxiv, medium, blogs,
  youtube, x.com, reddit, HN, infoq, forbes, openai.com, langchain, zenml, etc.
  For those, rely on search snippets: run several differently-worded searches per source so
  the snippets expose the specific facts (numbers, quotes). Do not waste calls retrying
  blocked domains.
- GitHub MCP tools are scoped to the user's own repo; do not use them for other repos.

## Evidence rules (non-negotiable)
1. Never invent a fact, number, name or quote. Every field you fill must cite a URL
   (search-result URL is fine) in `sources:`.
2. Tag each fact: `stated` (the source says it), `inferred` (reasonable reading of the
   source; say from what), or `unknown`. A quote in `quotes:` must be verbatim from a
   snippet or fetched page; if you paraphrase, mark it `paraphrase: true`.
3. Fields that only a live conversation can answer (would_pay_to_prevent,
   replay_inside_env_ok, design_partner_candidate, credible_contract_size) must be
   `unknown` unless the public record says something concrete; then explain.
4. Prefer primary sources (the org's own blog, talk, issue, paper) over press rewrites.
5. One markdown file per case, written with the Write tool (absolute path), named
   docs/phase0/discovery/cases/<track>-<NN>-<org-slug>.md where track is builder|fleet|vendor
   and NN is the number I assigned you. Structure:
   - H1 title: "<Org>: <one-line summary>"
   - `evidence_grade:` A (primary postmortem or talk with specifics) / B (primary but
     thin) / C (secondary press or inference only)
   - the YAML block from 02-synthesis-template.md, every key present (use unknown),
     plus `method: desk`, `sources: [urls]`, and a `tags:` list for each fact:
     `stated` / `inferred`.
   - "## Evidence" section: 5–15 bullet facts, each ending with (URL).
   - "## What this case says for Gate A" : 3–6 sentences, honest.
6. Budget: aim for about 8–15 web calls per case; depth over breadth, but finish all
   cases assigned. If a target has no usable public evidence, replace it with another
   organization in the same track that does (say so in the file) rather than padding.
7. Write files as you go, not at the end. Finish by returning a compact summary table
   (org, grade, attributed_component, silent_regression_experienced, coding_agent_traces_flow_to,
   cannot_leave) so the coordinator can tally counters.
