# J.P. Morgan Private Bank: "Ask D.A.V.I.D.", a LangGraph supervisor with retrieval, structured-data and analytics sub-agents plus an LLM-judge reflection node and human-in-the-loop; "evaluation-driven development" started before ground truth existed, because "billions of dollars" are at stake

evidence_grade: B

Access note (2026-10-05): the primary source is the Interrupt 2025 talk "Multi-Agent Frontiers: Building Ask D.A.V.I.D." by David Odomirok and Zheng Xue (YouTube, egress-blocked), captured through LangChain's own tweets, a conference note page, a ZenML LLMOps-database summary and two secondary write-ups. No J.P. Morgan-authored blog post was found. Grade B: primary talk with architecture and evaluation practice, but no concrete failed-run story, no volumes, and accuracy figures only as generalities.

```yaml
org: J.P. Morgan Chase (Private Bank, investment research)
role: Investment research AI engineering (public: David Odomirok; Zheng Xue; a developer referred to as "Jane" in a secondary summary)
track: builder
date: 2026-10-05
interviewer: desk
method: desk
harnesses_frameworks: [LangGraph supervisor architecture, sub-agents (structured data: NL to queries/API calls; unstructured RAG over emails, meeting notes, recordings; analytics on proprietary models), LLM-as-judge reflection node with retry, short-term and long-term memory, MongoDB document search, human-in-the-loop final check; started as "a simple ReAct agent"]
domain: research
runs_per_day: unknown ("thousands of financial products" covered)
failure_definition: "inferred: an answer that fails the reflection judge or the human last-mile accuracy check; metrics named are accuracy, conciseness and trajectory"
failure_rate_estimate: unknown ("accuracy limitations requiring human oversight" acknowledged)
cost_per_failed_run: unknown
last_failure:
  symptom: "No incident published. Stated: 'achieving 100% accuracy with AI alone is challenging', so a reflection judge retries and a human patches 'the last mile accuracy gap'"
  detected_by: unknown
  time_to_why: unknown
  attributed_component: unknown
  recurred: unknown
  their_words: ""
harness_change:
  last_change: "Evolved from a simple ReAct agent to a supervisor with specialised sub-agents, a judge reflection node, memory and role-based personalisation ('start simple and refactor often')"
  regression_detection: evals
  silent_regression_experienced: unknown
  would_pay_to_prevent: unknown
controls_owned (fleets): []
tooling_today: [LangGraph, LLM-as-judge (in-loop reflection and offline evals), human review, MongoDB]
coding_agent_traces_flow_to: unknown
can_reproduce_failed_run: unknown
has_compared_cohorts: unknown
most_wanted_question: unknown
data_constraints:
  cannot_leave: [customer_data, prompts, tool_outputs]
  replay_inside_env_ok: unknown
  replay_outside_env_ok: unknown
budget_owner: ai_platform
credible_contract_size: unknown
automation_limits: "Human-in-the-loop is 'KEY for reliability (billions of dollars at stake)'; the judge runs 'before any answer leaves the system'"
would_allow_pause_stop_on_evidence: unknown
reaction:
  would_use_next_week: unknown
  does_not_believe: unknown
design_partner_candidate: unknown
referrals: [David Odomirok, Zheng Xue]
quotes:
  - q: 9
    text: "Supervisor architecture in LangGraph, human in the loop is KEY for reliability (billions of dollars at stake), short term and long term memory"
  - q: 10
    text: "compared to traditional AI projects, GenAI projects have shorter development phases but longer evaluation phases"
    paraphrase: true
  - q: 10
    text: "starting evaluation early, even without ground truth, and using LLM-as-a-judge combined with human review"
    paraphrase: true
  - q: 10
    text: "continuous evaluation of sub-agents and the main flow using appropriate metrics like accuracy, conciseness, and trajectory"
    paraphrase: true
  - q: 9
    text: "We started with a simple ReAct agent."
sources:
  - https://x.com/LangChain/status/1922717861698732514
  - https://x.com/LangChainAI/status/1928135137658818711
  - https://cameronrohn.com/docs/discover/LangChain-Interrupt-2025/presentations/2.4-Multi-Agent-Frontiers-Building-Ask-D.A.V.I.D./
  - https://www.zenml.io/llmops-database/multi-agent-investment-research-assistant-with-rag-and-human-in-the-loop
  - https://x.com/pvergadia/status/2051466913952485824
  - https://theaievolutionchronicle.substack.com/p/how-jpmorgans-ask-david-ai-agent
  - https://aibuilder.services/how-jp-morgan-built-an-ai-agent-for-investment-research-with-langgraph/
tags:
  harnesses_frameworks: stated (LangChain tweets; conference notes; ZenML summary)
  runs_per_day: unknown ("thousands of financial products" from LangChain tweet)
  failure_definition: inferred (from reflection judge and named metrics)
  failure_rate_estimate: stated as a limitation only (ZenML summary)
  last_failure.symptom: stated as a general limitation, not an incident
  harness_change.last_change: stated (conference notes: start simple, refactor often; secondary: "simple ReAct agent")
  regression_detection: stated (evaluation-driven development with LLM judge and human review; continuous evaluation of sub-agents)
  tooling_today: stated (LangGraph, LLM judge, MongoDB from LangChain tweet)
  cannot_leave: inferred (private-bank client data, proprietary models and internal emails/meeting notes; no explicit statement)
  budget_owner: inferred
  automation_limits: stated (LangChain tweet; secondary summaries)
  quotes: verbatim from LangChain tweet and secondary summaries; paraphrases marked
```

## Evidence
- LangChain (May 2025): "Zheng Xue and David Odomirok showing how @jpmorgan built D.A.V.I.D. to automate investment research! - Goal: Enable realtime decision making - Supervisor architecture in LangGraph, human in the loop is KEY for reliability (billions of dollars at stake), short term and long term memory" (https://x.com/LangChain/status/1922717861698732514).
- The system automates "investment research for thousands of financial products" (https://x.com/LangChainAI/status/1928135137658818711).
- Architecture: a supervisor routes to a structured-data agent (NL to queries/API calls), an unstructured RAG agent and an analytics agent; a reflection node with an LLM judge checks accuracy and retries; answers are personalised to role (advisor vs analyst) (https://cameronrohn.com/docs/discover/LangChain-Interrupt-2025/presentations/2.4-Multi-Agent-Frontiers-Building-Ask-D.A.V.I.D./).
- "LLM-as-judge reflection runs before any answer leaves the system, and human-in-the-loop patches the last mile accuracy gap AI can't solve alone" (https://x.com/pvergadia/status/2051466913952485824).
- Evaluation practice: "GenAI projects have shorter development phases but longer evaluation phases"; start evaluation early "even without ground truth"; continuously evaluate sub-agents and the main flow on accuracy, conciseness and trajectory (https://cameronrohn.com/docs/discover/LangChain-Interrupt-2025/presentations/2.4-Multi-Agent-Frontiers-Building-Ask-D.A.V.I.D./ ; https://www.zenml.io/llmops-database/multi-agent-investment-research-assistant-with-rag-and-human-in-the-loop).
- The team "acknowledge[s] accuracy limitations requiring human oversight, especially for high-stakes financial decisions involving billions in assets" (https://www.zenml.io/llmops-database/multi-agent-investment-research-assistant-with-rag-and-human-in-the-loop).
- Data sources: "decades of structured data, vast unstructured data (emails, meeting notes, recordings), and proprietary models"; MongoDB used for document search (https://x.com/LangChainAI/status/1928135137658818711 ; https://cameronrohn.com/docs/discover/LangChain-Interrupt-2025/presentations/2.4-Multi-Agent-Frontiers-Building-Ask-D.A.V.I.D./).
- Secondary: development "began with simple agents" ("We started with a simple ReAct agent"); claimed research-time reduction "by up to 95%" (https://theaievolutionchronicle.substack.com/p/how-jpmorgans-ask-david-ai-agent ; https://aibuilder.services/how-jp-morgan-built-an-ai-agent-for-investment-research-with-langgraph/).

## What this case says for Gate A
J.P. Morgan is a regulated, high-stakes builder that already does what we would call trajectory evaluation of sub-agents and has an in-loop judge, so component-level attribution is a concept they practise, not one we would need to sell. The stakes ("billions of dollars") and the data (client holdings, internal emails and meeting notes, proprietary models) make in-environment replay the only credible deployment model, and a bank of this size would not stream traces to a startup. The record contains no failure, no regression, no trace tooling and no volumes, so it contributes constraints and architecture, not pain. Also note this is a 2025 talk; the system has likely moved on. Counts: silent_regression unknown, attribution unknown, traces unknown, cannot_leave customer_data + prompts + tool_outputs (inferred).
