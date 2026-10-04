# Naming workstream report (2026-10-04)

## Method and limits (read first)
- **Registries, checked directly:** PyPI JSON API, the npm registry, the crates.io sparse index, and Homebrew core and cask formula files on raw.githubusercontent.com. These are definitive.
- **GitHub:** repo-name search through the GitHub MCP, plus a fetch of github.com/<name> to see whether a user or org owns the name.
- **Domains:** the egress proxy blocked page content for every live domain, so I could not see what any of them show. I used DNS resolution as the signal instead:
  - **NX** means the name did not resolve. My random control domains (zzqx…qq7.com/.ai/.io) also came back NX, so NX most likely means unregistered. **Check with a registrar before you rely on it.**
  - **R** means the name resolves, so it is registered. Its content is unknown unless web search showed it.
- **Not checked:**
  - Hacker News (hn.algolia.com) and Product Hunt were blocked by the proxy. **HN/PH checks are unverified for all 12 shortlisted names.**
  - The session ran out of web searches (200/200) partway through the trademark pass. Trademark searches for Forensa, Clinamen and Divra did not run.
  - USPTO was not reachable. Trademark notes come from web search only and are not clearance.
- **Main finding:** by October 2026, nautical, climbing and evidence words are heavily used by small agent-tooling open-source projects. Almost every real word has 0–10★ repos, and many are in this exact category. I weighted company, registry and trademark collisions above tiny repos.

## 1. Forty candidates
The note after each name is the triage result. "Registry" means the PyPI/npm/crates state from the first pass.

**Harness / rigging / scaffold**1. **Belay** — climbing/nautical: making a line fast and catching a fall. KILLED: many agent tools use it (github.com/haqaliz/belay "The agent harness… deterministic trace"; github.com/SECBLOK/belay). All three registries taken.
2. **Prusik** — friction hitch that grabs the rope when a load falls. KILLED: github.com/getprusik/prusik, "evidence-based build harness for autonomous coding agents"; PyPI `prusik` v0.220.0.
3. **Kernmantle** — climbing rope: a core ("kern", the model) inside a load-bearing sheath ("mantle", the harness). Shortlisted.
4. **Halyard** — hoists and trims the sail. KILLED: github.com/Kormiloio/Halyard (AI session tracking via Claude Code hooks); halyard.dev.
5. **Bridle** — harness headgear that steers. KILLED: github.com/neiii/bridle ("config manager for agentic harnesses"); bridle-governance.com.
6. **Keelson** — structural backbone above the keel. Shortlisted (crowded).
7. **Fairlead** — fitting that guides a line so it runs true. Shortlisted (crowded).
8. **Backstay** — rigging that holds the mast from behind. Shortlisted.
9. **Bowline** — the reliable knot. KILLED: bowline.ai; github.com/Mindpool-Labs/bowline.
10. **Martingale** — harness strap; also the betting system that leads to ruin. DROPPED.

**Flight recorder / black box**
11. **Foqa** — Flight Operations Quality Assurance: routine analysis of recorded flight data to find precursors before incidents. Shortlisted.
12. **Telltale** — KILLED: agentarchaeology.ai/telltale (detection layer for AI coding agents); Netflix "Telltale".
13. **Debrief** — PyPI and npm taken. 14. **Orangebox** — all registries taken. 15. **Hindsight** — all registries taken; an agent-memory product exists (unverified). 16. **Tacho** — all registries taken.

**Evidence / provenance / forensics**
17. **Probative** — "having the quality of proving". Shortlisted.
18. **Provenant** — KILLED: provenant.ai and several companies.
19. **Corrobo** — KILLED: github.com/vidithsalla/corrobo ("reliability runtime"); PyPI `corrobo` (runtime verification of AI agent actions, Sep 2026).
20. **Forensa** — coined from "forensic". Shortlisted.
21. **Evidra** — KILLED: github.com/vitas/evidra ("Kill-switch for AI agents… evidence-backed"); evidra.cc; Show HN 47231861.
22. **Luminol** — KILLED: github.com/luminol org; LinkedIn anomaly library (unverified).
23. **Custodia** — PyPI and npm taken.

**Replay / rewind / divergence**
24. **Firstfork** — the first divergence point. Shortlisted.
25. **Forkpoint** — KILLED: forkpoint.com (consultancy), GitHub org ForkPoint.
26. **Clinamen** — Lucretius's "swerve", the first deviation. Shortlisted.
27. **Swerve** — KILLED: AI chat app. 28. **Bisect** — DROPPED: Python stdlib module. 29. **Retrace** — Stackify Retrace APM (unverified); registries taken.

**Reliability / engineering**
30. **Loadpath** — the route a load takes through a structure (attribution). Shortlisted.
31. **Plumbline** — KILLED: github.com/ActaClad/plumbline ("reliability & architecture analyzer for LLM and agentic systems"); github.com/askalf/plumbline.
32. **Autoblock** — KILLED: Autoblocks AI, a direct AI-reliability competitor.
33. **Trueline** — KILLED: trueline.ai. 34. **Redline** — registries taken. 35. **Ballast** — registries taken.

**Coined**
36. **Divra** — Shortlisted. 37. **Rigora** — KILLED (rigoralabs.com, rigoraclinical.com). 38. **Harnex** — KILLED (harnex.ai; github.com/junyeong-ai/harnex). 39. **Provena** — KILLED (provena.tech, provena.ai). 40. **Fidra** — KILLED (fidra.ai).

Also killed: Bosun (bosun.ai), Kedge (kedge.dev), Tackline (tacklines.com), Reeve (meetreeve.com), Hawser (gethawser.com).

## 2. Shortlist of 12: collision table
Domain key: R = resolves (registered, content unseen); NX = no DNS (likely free, verify with a registrar). "free" = 404 on that registry. HN/Product Hunt unchecked for all (blocked).

| Name | GitHub user/org | Notable repos | PyPI | npm | crates | Brew | .com | .dev | .ai | .io | Companies / products | Trademark signal | Meaning |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Kernmantle** | available | tweag/kernmantle (Haskell, 65★) | free | free | free | free | R | NX | NX | NX | Steam game "Kernmantle" (2020) | none surfaced | German Kern+Mantel = core+sheath |
| **Probative** | user exists, 0 repos | Vojtaupan/probative (tool-call record checker, 0★, Aug 2026); vedm1/probative | free | free | free | free | R | NX | R | R (Luzern investigations firm) | neighbours Prove AI, Probabl | none surfaced | Latin probare; neutral |
| **Foqa** | user created 2026-09-27, 0 repos | DroidsOnRoids/FoQA (Android QA) | free | free | free | free | R | NX | R | R | FAA AC 120-82; CloudAhoy P-FOQA, GE C-FOQA | two FOQA marks, both cancelled (2018, 2019) | "foca" = seal in Romance languages |
| **Firstfork** | org "First Fork" (1 repo) | throwaway repos | free | free | free | free | R | NX | NX | NX | The First Fork (Pune agency) | none surfaced | git "fork" connotation |
| **Forensa** | available | none | free | free | free | free | R | NX | R | R | neighbours ForensAI, Forensia, ForenseAI | UNVERIFIED | crime/autopsy tone |
| **Loadpath** | available | Modsofthenation/Loadpath (PR impact reviewer, Aug 2026) | free | free | free | free | R | R | NX | R | LoadPath LLC (aerospace, Redwire 2020); loadpath.app | Canada TMA834483 active to 2027 | engineering term |
| **Divra** | user exists | noise | free | free | free | free | R | NX | NX | NX | Swedish band; divra.in, divra.tech; neighbour Devra AI | UNVERIFIED | no meaning |
| **Clinamen** | user exists (Clojure) | Clinamen2 | TAKEN | free | free | free | R | NX | R | R | evarin.fr art project | UNVERIFIED | reads like "clinic" |
| **Backstay** | org exists, 0 repos | incidental | free | **TAKEN in-category** (Claude Code hooks → events, Aug 2026) | free | free | R | R | NX | NX | Backstay Digital/Group/Design | none | nautical |
| **Keelson** | user exists | 91 repos incl. agent harnesses and keelson-ai/keelson (red team) | TAKEN (RISE-Maritime) | TAKEN | TAKEN | free | R | R | R | R | keelson.app and partners | many | nautical |
| **Fairlead** | **org exists, fairlead.dev** (SDKs in 6 languages) | gugia/fairlead ("run evidence" for PydanticAI) | **TAKEN** ("auditable evidence and governance kernel for LLM and agent applications") | **TAKEN** | free | free | R | R | NX | NX | Fairlead Technology Group | Fairlead Strategies | nautical |
| **Prusik** | user exists | **getprusik/prusik** in-category harness | **TAKEN** | free | free | free | R | NX | R | R | Prusik Group | none | surname |

## 3. Top 3
1. **Kernmantle — recommended.** Strongest fit with harness engineering (a load-bearing sheath around a core that exists to catch falls). Cleanest collisions of the twelve: all registries free, GitHub org free, .dev/.ai/.io likely buyable; only a niche Haskell library and a 2020 indie game. Weaknesses: ten letters, three syllables, "kernmantel" misspelling; the short form "Kern" is taken (Kern AI; PyPI and crates `kern`). Lead with kernmantle.dev or .ai and try to buy .com.
2. **Probative.** Clearest evidence word, easy to say, positive in Romance languages, all registries free, .dev free. Risks: adjective, in-category micro-repos from Aug to Sep 2026, probative.io is an investigations firm, .com and .ai registered, fits evidence more than harness.
3. **Foqa.** Short, real aviation meaning that is exactly the product's job, pairs with the internal "Flight Recorder", every registry free so brand equals CLI. Risks: generic acronym in aviation, ambiguous pronunciation, .com/.ai/.io registered, a `foqa` GitHub user appeared on 2026-09-27.

Runner-up: **Firstfork** (all registries free, .dev/.ai/.io free) but describes one feature and the GitHub org is taken.

Before committing: counsel runs USPTO and EUIPO clearance; confirm domains with a registrar.

## 4. Open specification name
1. **Agent Harness Semantic Conventions (`harness-semconv`, namespace `harness.*`) — recommended.** `harness-semconv` and `agent-harness-semconv` free on PyPI, npm, crates, Homebrew; github.com/harness-semconv free; harness-semconv.dev does not resolve. Mirrors OTel wording; the namespace is the external name.
2. **Agent Harness Telemetry (`agent-harness-telemetry`)** — free everywhere; one unrelated GitHub hit.
3. **Harness Event Conventions (`harness-events` / `harness-event-model`)** — free.
4. **Open Harness Conventions — reject.** HKUDS/OpenHarness has 15.9k★; autonomous-ai/openharness 1.1k★; thu-nmrc/OpenHarness; PyPI `openharness` taken; github.com/agent-harness org exists.
5. **OpenTrajectory — reject.** abhid1234/opentrajectory holds npm and PyPI `opentrajectory` (Sep 2026).

Caveat: Harness Inc. (harness.io, CI/CD) holds HARNESS marks (from memory). Descriptive use inside a convention name is lower risk than a brand such as "OpenHarness"; counsel to confirm. A descriptive spec name cannot be held as a trademark, which conflicts with PLAN-06 §6's assumption; PLAN-06 should be amended to hold only the product mark.

## 5. OSS recorder CLI name
1. **`qar`** (quick access recorder, the aviation recorder FOQA programs read) — free on PyPI, npm, crates, Homebrew; github.com/qar is an unrelated individual. Three letters. **Recommended, brand-independent.**
2. **`hrec`** (harness recorder) — free everywhere; only collision is HRec, a recommender research repo. Fallback.
3. **`foqa`** — free everywhere; best if the company is Foqa.
4. **`tracklog`** — free; archived GPX apps on GitHub.
5. **`probative` / `probative-cli`** — free; long to type.

Rejected: `runtape` (PyPI "Record AI agent runs locally", npm "Flight recorder for AI coding agents"), `flightlog` (npm, Jul 2026), `wake`, `spoor`, `logbook`, `tapedeck`, `fdr`, `kern`, `kmt`, `mantle` (taken).

Pairing: Kernmantle plus CLI `qar` (or `hrec`); Foqa plus CLI `foqa`.
