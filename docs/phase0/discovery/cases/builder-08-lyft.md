# Lyft: LangGraph customer-care agents handling 270,000+ AI interactions a day; an LLM-as-user simulator passed at 90% offline while production was poor because simulated users were "too polite"; fixed with a fine-tuned simulator, adversarial personas, binary rubrics and a Git-backed CI linting pipeline for prompts

evidence_grade: A

Access note (pass 2, 2026-10-05): the primary talk (Nick Ung and Akshay Sharma, Interrupt 2026, "Build Evals That Actually Matter") is on YouTube (blocked) but its content is captured in LangChain's own post "Customer Experience (CX) Agents in Production: Lessons from Lyft, Vodafone, and LATAM Airlines", LangChain's Lyft platform post, a ZenML summary, 8th Light's and 99P Labs' conference notes, and a verbatim tweet. Anthropic's Lyft page was fetched directly in pass 1. All pass-1 "carried" facts are now verified. Grade A: primary talk and vendor-co-authored post with a concrete failure, its root cause and the fix.

```yaml
org: Lyft
role: Safety & Customer Care data science / AI platform (public: Nick Ung, head of data science for safety and customer care; Akshay Sharma)
track: builder
date: 2026-10-05
interviewer: desk
method: desk
harnesses_frameworks: [LangGraph router-based multi-agent (rider/driver requests routed to specialised subagents with safety checks, state management, handoffs), LangSmith (tracing, dashboards, LLM-as-judge), self-serve agent platform where ops/VoC/PMs define agents via prompts and configuration, fine-tuned LLM-as-user simulator, Claude (model used for the care assistant per Anthropic)]
domain: support
runs_per_day: "270,000+ AI-handled customer interactions per day (recap of talk); 79M trips/month; 55% containment, 35% full resolution"
failure_definition: "Task-specific binary rubrics validated as classifiers against human-labelled data; containment and resolution in production; hallucination rate tracked"
failure_rate_estimate: "Offline simulator pass rate >90% before fix; production 'poor' (no number); after platform work: +16% AI resolution rate, -20% hallucination rate"
cost_per_failed_run: unknown
last_failure:
  symptom: "Agent validated against an LLM-as-user simulator at ~90% offline success; shipped; production performance was poor. Simulated users were 'too polite, too patient, too detailed'; real riders 'answered in one or two words', write in fragments, omit context, repeat themselves, or arrive wanting a refund or to bypass the agent"
  detected_by: production_users
  time_to_why: unknown
  attributed_component: verification
  recurred: no
  their_words: "People don't sit down and nicely explain their issues."
harness_change:
  last_change: "Rebuilt the eval harness: simulated user fine-tuned on real customer verbatims; personas 'Bypasser', 'Refund Seeker', 'AI Skeptic'; binary task-specific rubrics validated as classifiers; confidence intervals on every score; structured prompt-writing framework with a Git-backed CI linting pipeline for prompts"
  regression_detection: ci
  silent_regression_experienced: yes
  would_pay_to_prevent: unknown
controls_owned (fleets): []
tooling_today: [LangGraph, LangSmith (every invocation traced in dev, staging and production including reasoning, retrieved content and tool calls), LLM-as-judge, fine-tuned user simulator, Git + CI prompt linting]
coding_agent_traces_flow_to: unknown (support-agent traces go to LangSmith; nothing on coding agents)
can_reproduce_failed_run: partially
has_compared_cohorts: yes
most_wanted_question: "inferred: which offline eval scores actually predict production outcomes ('if your LLM-as-a-judge is just floating out there and no one is really using that score as a meaningful gate' it is not useful)"
data_constraints:
  cannot_leave: [customer_data]
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: ai_platform
credible_contract_size: unknown
automation_limits: "Safety concerns, complex disputes and cases needing empathy are routed to human agents with AI-generated summaries; safety checks and handoffs are built into the LangGraph flow"
would_allow_pause_stop_on_evidence: unknown
reaction:
  would_use_next_week: unknown
  does_not_believe: unknown
design_partner_candidate: unknown
referrals: [Nick Ung, Akshay Sharma]
quotes:
  - q: 1
    text: "People don't sit down and nicely explain their issues."
  - q: 1
    text: "Lyft's first LLM-generated customers were too articulate, patient, and cooperative, producing offline pass rates above 90% that did not reflect production behavior."
    paraphrase: true
  - q: 11
    text: "if your LM-as-a-judge is just floating out there and no one is really using that score as a meaningful gate"
  - q: 10
    text: "the team's biggest lesson was that prompt quality, not infrastructure, was the real bottleneck, leading them to create a structured prompt writing framework and a Git-backed CI linting pipeline"
    paraphrase: true
  - q: 13
    text: "Every invocation is traced in LangSmith across development, staging, and production, including the agent's reasoning, the educational content it retrieved, and the tools it called."
  - q: 4
    text: "accuracy of the response and the ability of the AI models to have the tone and persona that represented our brand"
sources:
  - https://www.langchain.com/blog/customer-experience-cx-agents-in-production-lessons-from-lyft-vodafone-and-latam-airlines
  - https://www.langchain.com/blog/lyft-built-a-self-serve-ai-agent-platform-for-customer-support-with-langgraph-and-langsmith
  - https://www.youtube.com/watch?v=3z2uT5aDx_Y
  - https://8thlight.com/insights/production-is-the-new-prototype-notes-from-langchain-interrupt-2026
  - https://www.zenml.io/llmops-database/building-production-grade-evaluation-systems-for-customer-support-ai-agents
  - https://x.com/zostaff/status/2087176597895864478
  - https://finance.biggo.com/news/9964d2cf12e70e8e
  - https://medium.com/99p-labs/agents-at-scale-field-notes-from-langchains-2026-interrupt-conference-3abbbfab52d0
  - https://claude.com/customers/lyft
tags:
  harnesses_frameworks: stated (LangChain Lyft platform post; Anthropic page for Claude)
  runs_per_day: stated in conference recaps of the talk (270,000+/day, 79M trips, 55%/35%); the tweet says "270,000 support conversations a month", a discrepancy between secondary sources, both recorded
  failure_definition: stated (ZenML summary of the talk: binary rubrics validated against human labels)
  failure_rate_estimate: stated (>90% offline, "poor" in production; +16% resolution and -20% hallucination from the LangChain platform post)
  last_failure.symptom: stated (LangChain CX post; 8th Light notes)
  last_failure.detected_by: inferred (discovered after shipping, from production performance)
  last_failure.attributed_component: inferred (the agent was not changed first; the evaluation harness was wrong, so the failure sits in verification)
  last_failure.recurred: inferred (described as a one-time lesson followed by a rebuilt harness)
  harness_change.last_change: stated (LangChain CX post; ZenML; LangChain platform post for CI linting)
  regression_detection: stated (Git-backed CI linting pipeline for prompts; LangSmith LLM-as-judge; rebuilt offline evals)
  silent_regression_experienced: inferred (an eval harness that passed at 90% while production was poor is a silent quality gap; it was not a change-induced regression in the strict sense, so treat as borderline yes)
  tooling_today: stated
  can_reproduce_failed_run: inferred (full traces in LangSmith plus a simulator; no statement about replaying a specific failed conversation)
  has_compared_cohorts: stated (offline vs production comparison; multi-model comparison on Anthropic page)
  cannot_leave: inferred (rider/driver support data; not stated)
  budget_owner: inferred
  automation_limits: stated (Anthropic page; LangChain platform post)
```

## Evidence
- Lyft built a lightweight simulator with an LLM playing the user, "watched offline success rates hit 90%", shipped, and "production performance was poor"; the simulated users "were too polite, too patient, too detailed" while real riders "answered in one or two words" (https://8thlight.com/insights/production-is-the-new-prototype-notes-from-langchain-interrupt-2026).
- LangChain's own write-up: the first LLM-generated customers "were too articulate, patient, and cooperative, producing offline pass rates above 90% that did not reflect production behavior"; real users "write in fragments, omit context, repeat themselves, or arrive with a specific goal such as securing a refund or bypassing the agent" (https://www.langchain.com/blog/customer-experience-cx-agents-in-production-lessons-from-lyft-vodafone-and-latam-airlines).
- Fix: fine-tune the simulated user on real customer verbatims and add personas ("Bypasser", "Refund Seeker", "AI Skeptic"); "the evaluation got harder. The production-offline gap got smaller" (https://8thlight.com/insights/production-is-the-new-prototype-notes-from-langchain-interrupt-2026 ; https://www.langchain.com/blog/customer-experience-cx-agents-in-production-lessons-from-lyft-vodafone-and-latam-airlines).
- Rebuilt harness: fine-tuned user simulators, "binary task-specific rubrics validated as classifiers against human-labeled data, and confidence intervals on every reported score", producing an eval harness that "surfaces specific failure modes" (https://www.zenml.io/llmops-database/building-production-grade-evaluation-systems-for-customer-support-ai-agents).
- Nick Ung on gating: "if your LM-as-a-judge is just floating out there and no one is really using that score as a meaningful gate" it is not useful; most eval pipelines "produce generic, non-actionable scores that do not gate real decisions" (https://finance.biggo.com/news/9964d2cf12e70e8e).
- Scale: 79 million trips a month, "270,000-plus AI-handled customer interactions per day", 55% containment, 35% full resolution (https://medium.com/99p-labs/agents-at-scale-field-notes-from-langchains-2026-interrupt-conference-3abbbfab52d0). A tweet from the talk says "270,000 support conversations a month" (https://x.com/zostaff/status/2087176597895864478).
- Platform: LangGraph routes rider and driver requests across specialised subagents "with safety checks, state management, and handoffs built into the flow"; ops teams, VoC leads and PMs define agents through prompts and configuration (https://www.langchain.com/blog/lyft-built-a-self-serve-ai-agent-platform-for-customer-support-with-langgraph-and-langsmith).
- "The team's biggest lesson was that prompt quality, not infrastructure, was the real bottleneck", leading to "a structured prompt writing framework and a Git-backed CI linting pipeline"; results: 16% higher AI resolution rate and 20% lower hallucination rate (https://www.langchain.com/blog/lyft-built-a-self-serve-ai-agent-platform-for-customer-support-with-langgraph-and-langsmith).
- "Every invocation is traced in LangSmith across development, staging, and production, including the agent's reasoning, the educational content it retrieved, and the tools it called" (https://www.langchain.com/blog/customer-experience-cx-agents-in-production-lessons-from-lyft-vodafone-and-latam-airlines).
- Anthropic page: resolution time cut by 87%; models compared on "accuracy of the response and the ability of the AI models to have the tone and persona that represented our brand"; safety and empathy cases routed to humans (https://claude.com/customers/lyft).

## What this case says for Gate A
Lyft is the cleanest public example of an offline gate that passed while production failed, and the team's own diagnosis is that the evaluation harness, not the model, was wrong. Their response is exactly the direction we argue for: evals grounded in real production verbatims, rubrics validated against human labels, and prompts under Git with a CI linting gate. That makes Lyft both a validation of "gate on production-derived failures, not synthetic suites" and a sign that sophisticated teams build this themselves on LangSmith. It is a support agent, not a coding agent, and the traces live in LangSmith, so an incumbent is in place. Counts: silent_regression yes (borderline, see tag), attribution = verification, traces to LangSmith for support agents and unknown for coding agents, cannot_leave customer_data (inferred).
