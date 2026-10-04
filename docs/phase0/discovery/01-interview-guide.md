# Discovery Interview Guide (Phase 0, W1)

**Goal:** fifty structured conversations in twelve weeks: twenty open-harness builders, twenty closed-harness fleet operators, ten harness vendors. The output is verbatim evidence for Gate A, not opinions about our product. Do not pitch until the last five minutes. Never ask "would you buy AI observability" (PLAN-04; HRCP-02 §50).

## 1. Screening (two minutes, before booking)

Qualify if at least four of these are true (PLAN-01 §7; HRCP-00 §32):
- Agents run in production, not only demos.
- Typical run exceeds five minutes or ten tool calls.
- Agents mutate real systems (code, tickets, records, infrastructure).
- There is persistent state, memory or compaction across the run.
- Subagents or delegation exist.
- A repeated task class exists (tickets, migrations, test generation, support actions).
- Someone is accountable when a run fails badly.
- At least one hundred runs per day, or cost per failed run above $5.

Record: company, role, track (builder, fleet, vendor), frameworks and harnesses, daily run volume, domain.

## 2. Interview structure (forty-five minutes)

Order matters: past behaviour first, then pain, then workflow, then constraints, then (briefly) reaction.

### 2.1 Last failure (ten minutes)
1. "Tell me about the last time an agent run went wrong in production. What happened, step by step?"
2. "How did you find out?" (user report, cost alert, dashboard, CI, nobody)
3. "How long from the failure to knowing *why*? Who did the work? What did they look at?"
4. "Was it the model, or something around the model: prompt, context, tools, permissions, retries, a subagent, verification?" Let them categorize; record their words.
5. "Did it happen again? How many times before it was fixed?"

### 2.2 Fleet and failure rates (five minutes)
6. "How many runs per day? How many fail? How do you define failure: wrong output, no output, over budget, unsafe action, human had to intervene?"
7. "What does a failed run cost you, in money and in someone's time?"
8. "Which failures do you never see because nobody looks?"

### 2.3 The harness and its changes (ten minutes)
9. "Walk me through the system around the model: how is context built and compacted, which tools, which permissions, how retries work, how you decide a task is done." Draw it if possible.
10. "When did you last change any of that: a prompt, a rules file, a tool schema, a permission rule, a model version, a compaction threshold? How did you know it did not make something else worse?"
11. "Have you ever shipped a harness change that silently regressed quality? How long until you noticed?"
12. For fleets of closed harnesses: "Which of those do you actually control: CLAUDE.md or rules files, hooks, permission policy, MCP servers, tool allowlists, model and effort, budgets, CI checks?"

### 2.4 Current tooling (seven minutes)
13. "What do you use today: LangSmith, Langfuse, Braintrust, Datadog, Arize, Weave, Laminar, Raindrop, vendor dashboards, your own? What do you look at daily, what never?"
14. "Do coding-agent traces (Claude Code, Codex, Cursor) flow into your observability stack? Via what?"
15. "Can you reproduce a failed run today? What stops you?"
16. "Can you compare a batch of failed runs against successful ones? Have you tried?"
17. "What question do you most want answered that nothing answers?"

### 2.5 Constraints (five minutes)
18. "Which telemetry cannot leave your environment? Prompts, tool outputs, code, customer data?"
19. "Would you let a third-party replay a failed run in a sandbox inside your environment? Outside?"
20. "Who owns budget for this: observability, AI platform, developer productivity, security? Rough size of a credible contract?"
21. "What actions are too dangerous to automate? Would you let a tool pause or stop an agent on evidence?"

### 2.6 Reaction (five minutes, only now)
22. Describe in two sentences: "We reconstruct every run, group failures into incidents, find where failed runs first diverged from successful ones and which harness component caused it, replay the failure, and gate every harness change in CI against last week's failures." Then: "What part of that would you use next week? What part do you not believe?"
23. "Would you be a design partner: stream production telemetry, host replay, review incidents weekly, in exchange for free access and named engineers?"
24. "Who else should I talk to?"

## 3. Track-specific additions

**Builders:** which framework, what the loop looks like, whether they would add an instrumentor package or emit events natively, whether they have a staging corpus of tasks.
**Fleets:** how many distinct agents (Claude Code, Codex, Cursor, Devin, Copilot), whether GitHub Agent HQ or similar is in use, whether a platform team governs rules files and hooks, cost controls in place, any incident involving destructive commands.
**Vendors:** what they built internally for evaluation and regression, whether they would emit control events natively, what they would never let a third party see, whether their enterprise customers ask for reliability evidence.

## 4. Recording rules

- Record verbatim quotes with permission; tag each quote with the question number and track.
- After each interview complete `02-synthesis-template.md` within one hour.
- Weekly: tally the Gate A counters (see template). Stop and re-plan if the kill triggers in PLAN-09 §6 are met at twenty interviews.
