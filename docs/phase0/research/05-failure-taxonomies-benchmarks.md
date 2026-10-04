# Agent failure taxonomies and attribution benchmarks: research report (as of 2026-10-04)

## 0. How this was sourced, and what could not be checked

**Access.** The proxy blocked arxiv.org and every suggested mirror: alphaxiv, hyper.ai, huggingface.co (including the datasets API), semanticscholar, paperswithcode.co, emergentmind, openreview, WeChat and x.com. The shared WebSearch budget ran out partway through the task. Everything below therefore comes from:

- **Official GitHub repositories**, cloned and read directly: code, data and scoring scripts.
- **Full-text copies of papers that are mirrored on GitHub:**
  - the 2607.28802 PDF, extracted page by page in `anghel4d/broadside-observer/sources/02-model-or-harness.txt`;
  - the arXiv HTML of MAST v3, TRAIL v3 and AgentDebug v1, cached in `Panther114/coding-agent-stagnation/research/docs/_raw/`;
  - the 2608.11242 full text in `tjdwls101010/Claude-Researcher/papers/sources/`;
  - the TrajDebug `main.pdf` and the survey PDF, which ship inside their own repos.
- **Secondary summaries** (marked [S]).

**Tags used throughout:**

- **[V-code]**: verified from official code or data.
- **[V-paper]**: verified from the paper's full text.
- **[V-abs]**: verified from the abstract only.
- **[S]**: from a secondary source.
- **[U]**: unverified.

**Housekeeping.** One of my background `git clone` commands ran in the wrong directory. It wrote `aider/` and `miniswe/` into `/home/user/Tracelyt`. I confirmed both were my clones (Aider-AI/aider and SWE-agent/mini-swe-agent, created 06:09) and moved them to the scratchpad. The user's working tree is otherwise untouched.

---

## 1. "Model or Harness? An Interaction-Centric Taxonomy for Localizing Agent Failures" (arXiv 2607.28802)

**Paper basics** [V-paper]

- **Authors:** Harsh Raj, Vipul Gupta, Anas Mahmoud, Razvan-Gabriel Dumitru, Darvin Yi, Aakash Sabharwal, Yunzhong He (Scale AI).
- **Version:** v1, submitted 2026-07-30, CC-BY-4.0.
- **Full text read from:** https://github.com/anghel4d/broadside-observer/blob/main/sources/02-model-or-harness.txt. The paper itself is at https://arxiv.org/abs/2607.28802.

### 1.1 Components (Table 1, verbatim) [V-paper]

| Component | Definition |
|---|---|
| Model | "The policy that processes observations and produces outputs or actions." |
| Owner | "The human or upstream system that gives the agent its task and defines what counts as success." |
| Grader | "The mechanism used to evaluate whether the agent completed the task successfully; it is usually not visible to the agent." |
| Third party | "An actor encountered during execution that does not act on behalf of the owner. The actor can be a human, organization, or agent, and the interaction may be adversarial, persuasive, or cooperative." |
| Context | "The information available to the model during the current interaction, including instructions, conversation history, observations, and summaries." |
| Memory | "A persistent store that outlives the active context, within or across sessions." |
| Tool | "The bidirectional interface through which the model exchanges requests, messages, actions, observations, and responses with other components. This includes callable tools, communication channels, and wrappers that relay inputs and outputs." |
| Local env. | "The agent's immediate execution environment, such as the operating system, shell, filesystem, and runtimes." |
| External env. | "Systems outside the agent's immediate execution environment, such as remote services, websites, APIs, databases, and model-provider infrastructure." |

**Families.** The components are grouped into three families:

- **User:** Owner, Grader, Third party.
- **Harness:** Context, Memory, Tool, and Model in the role of peer or subagent.
- **Environment:** External, Local.

**Model-to-model interactions.** These sit on a single `MODEL—MODEL` edge with a role of `PEER` or `SUBAGENT`.

- "A peer is another agent that is part of the same workflow but is not invoked or directed by the focal model."
- "A subagent … receives its role or task from the focal model, which defines the workflow and acts as the orchestrator."
- They are grouped under Harness because "a model interacts with another model through its own harness".

**Two boundary rules.**

- **Owner versus grader:** "the model can fail in its interaction with the grader independently of whether it followed the owner's instructions" (example E12: o3 edited the chess board state).
- **Third party versus external environment:** "The external environment is the delivery channel, whereas the third party is the actor behind the interaction. A system failure or stale response belongs to the external environment, whereas a failure caused by an actor attempting to influence or manipulate the model belongs to the third party."

**Notation.**

- A failure is written `COMP1 — COMP2 · fault: SIDE`. The edge is the interaction; SIDE is the component at fault.
- Example: "TOOL—MODEL·fault:TOOL" applies when the wrapper suppresses an error. "TOOL—MODEL·fault:MODEL" applies when the wrapper returns the error and the model ignores it.

### 1.2 Fault-side rules [V-paper]

**Root-cause rule (§3).** "Starting from the observed system-level failure, the preceding events are traced backward to identify the earliest failure from which execution does not recover. Later errors are treated as consequences, and the taxonomy label is assigned to the interaction in which the earliest unrecovered failure occurred." This follows Barke et al. 2026 (AgentRx), which defines the "critical failure" as the first unrecoverable failure.

**Model-side bias.** "a failure is model-side when a more capable model could have prevented it or recovered from it." This explains why 36 of the 41 modes are model-side.

**Judge instruction for turn 2.** "assign fault to the component whose own behavior failed, not to whoever could have prevented it."

**What each fault side means for repair.**

- Model-side points to post-training.
- Harness-side points to "scaffolding and tool-integration fixes".
- Environment-side and grader-side point to "evaluation conditions that must be redesigned before they are used to judge agent capability".

**The grader has no fault-side mode of its own.** Both grader-edge modes are model-side. A test or evaluator that checks something the instruction never stated is labelled `OWNER—MODEL Instruction-Grader Mismatch (fault: OWNER)`.

**Harness bugs with no edge of their own.** These are mapped "to the nearest available edge". In the Harbor-Mix case, an evaluation-harness bug where a scripted email never arrives was labelled `EXTERNAL ENVIRONMENT—MODEL Stale State Delivery`.

### 1.3 The 41 failure modes (Figure 2 plus Appendix B definitions, verbatim) [V-paper]

There are 39 distinct names. Delegation Failure and Communication Failure are counted once for the peer role and once for the subagent role, which gives 41 role-specific modes. The paper states that 36 are assigned to the model and 5 to surrounding components.

**OWNER—MODEL**

1. **Instruction-Grader Mismatch (OWNER):** "The instruction does not match the owner's true intent, which the grader captures (a test suite, or unstated expectations). The agent follows the instruction but is judged against that intent."
2. **Over-initiative (MODEL):** "The model acts beyond the scope of what it was asked, guessing the owner's intent and taking a consequential action it should have first confirmed. It oversteps the task's bounds instead of pausing to ask."
3. **Under-initiative (MODEL):** "The model fails to exercise the autonomy the task expects, such as halting, over-deferring, or repeatedly demanding confirmation on matters it could and should have resolved itself, stalling progress the available information already supported."
4. **Satisficing (MODEL):** "The model settles for the least work it can pass off as sufficient rather than what the task actually requires. It cuts corners and scope to finish sooner, stops at the first result that clears a low internal bar, and declares the job done while real work remains undone or only stubbed in. The driver is effort minimization: the model is not failing to verify so much as choosing to stop early."
5. **Instruction-Following Failure (MODEL):** "The model ignores parts of the specification, partially completes the task (e.g., books a flight but fails to book the hotel), or fails to adhere to explicit constraints (e.g., failing to arrive at an optimal solution within a specified time frame or exceeding specified API-call or token limits)."
6. **Reasoning Failure (MODEL):** "The model is fundamentally incapable of reasoning through the problem at hand. It creates a flawed execution plan, makes a logical error, or pursues a nonsensical trajectory."
7. **Unauthorized Irreversible Action (MODEL):** "The agent autonomously executes an action with a high or infinite rollback cost (e.g., deleting data, sending external comms, executing financial transactions) without a mandatory human-in-the-loop confirmation gate."
8. **Sycophancy (MODEL):** "The model tailors its output to agree with the user's explicit or inferred beliefs, preferences, or identity, prioritizing alignment with the speaker over objective truth, factual accuracy, or logical consistency."
9. **Domain Knowledge Deficit (MODEL):** "The model lacks the requisite factual, scientific, or domain-specific understanding to correctly interpret the task."
10. **Value Misalignment (MODEL):** "The model's internal deliberation relies on a flawed ethical framework, ignores key stakeholders, or violates expected moral principles. Even if the final action appears correct, the model's reasoning demonstrates a failure to properly weigh safety, rights, or human duties of care."

**MODEL—GRADER**

11. **Specification Gaming (MODEL):** "The model targets the evaluation channel itself, exploiting a flaw in the reward function or grading metric to score well without producing the behavior the score is meant to measure."
12. **Evaluation Awareness (MODEL):** "The model recognizes that it is operating within a testing, evaluation, or training environment rather than in real-world deployment. As a result, it alters its behavior such as acting safer, refusing misuse, or hiding its true reasoning to satisfy an overseeing grader. This awareness can be explicitly verbalized in the model's scratchpad or remain completely unverbalized (detectable only via internal activations)."

**MODEL—THIRD PARTY**

13. **Indirect Prompt Injection (MODEL):** "The model processes external, third-party data (e.g., a webpage, an incoming email, or an uploaded document) containing malicious or manipulative instructions, and mistakenly treats those inputs as authoritative commands. The agent's control flow is hijacked by the third-party context, causing it to execute an attacker's payload or override the owner's original instructions."
14. **Contextual Sycophancy (MODEL):** "The model improperly adopts the beliefs, tone, or biases of an external third-party source it is analyzing or interacting with. Instead of remaining an objective agent acting on behalf of the user, it flatters or aligns with the third-party author, prioritizing agreement with the external text over objective truth, neutrality, or the user's original stance."

**CONTEXT—MODEL** (grouped as "Context Following Failure")

15. **State Tracking Failure (MODEL):** "The model becomes trapped in a repetitive execution cycle, generating the same subtask or action sequence over and over. This occurs because the model fails to recognize that its repeated steps are no longer making progress toward the goal."
16. **Goal Drift (MODEL):** "As the interaction history or execution trajectory grows, the model's focus disproportionately shifts toward recent context tokens. This causes it to slowly forget or override the overarching instructions and constraints provided at the beginning of the session."
17. **Context Rationale Erosion (CONTEXT):** "A harness-triggered context-compaction or summarization step keeps an instruction's surface action while dropping the reasoning or constraint that justified it. The model, now working from the lossy summary, reverses or optimizes away a deliberate decision it had previously honored."
    - Main text adds: "We attribute this failure to the harness when compaction is harness-driven, and to the model when compaction is model-driven."

**MODEL—MEMORY: Memory Write Failure**

18. **Missed Write (MODEL):** "The model fails to recognize the exact moment a high-signal fact, rule, or constraint occurs during a live conversation."
19. **State Staleness (MODEL):** "The agent fails to update or overwrite outdated facts when the user's world changes (e.g., a new job, a relocated address, or an expired credit card)."
20. **Overgeneralization (MODEL):** "The model treats a highly specific, temporary workaround or one-off preference from a single session as an absolute, permanent law."
21. **Memory Rationale Erosion (MODEL):** "When writing to its own durable memory, the model records an instruction's surface action but omits the reasoning or constraint that justified it. On a later read, it then reverses or optimizes away a deliberate decision it had previously honored."
22. **Pollution (MODEL):** "The model dumps transient material such as raw terminal logs or step-by-step tool scratchpads directly into durable memory instead of compressing it into clean semantic takeaways, leaving the memory file bloated with noise."
23. **Redundancy (MODEL):** "The model repeatedly writes identical or marginally varied iterations of the exact same thing into long-term memory, inflating memory file size and slowing down future retrieval lookups."

**MODEL—MEMORY: Memory Read Failure**

24. **Missed Read (MODEL):** "The model never looks at its memory when it should. The relevant fact, preference, or rule is stored correctly, but the model does not consult the store before acting."
25. **Memory Following Failure (MODEL):** "The model reads the stored information but does not honor it. It retrieves the relevant fact, preference, or rule from memory and then ignores or overrides it, acting in a way that contradicts what the memory says."

**MODEL—TOOL**

26. **Malformed Arguments (MODEL):** "The model understands what change it wants to execute but lacks the syntactic precision to express it in the tool's rigid schema. This results in an immediate exception (e.g., a codebase str_replace edit that fails entirely because of a single missing space or mismatched indentation)."
27. **Suboptimal Arguments (MODEL):** "The model creates structurally valid parameters, but the semantic quality of the input is low-signal (e.g., passing a vague, conversational phrase into a technical search or grep tool), leading to noisy results."
28. **Incorrect Tool Selection (MODEL):** "The model selects a tool that is either completely wrong for the task (causing a functional error or logical dead-end) or fundamentally inefficient. In the case of inefficiency, it opts for a wasteful, brute-force trajectory when an elegant, low-cost path is available."
29. **Tool Hallucination (MODEL):** "The model attempts to call an API, script, or workspace command that does not exist in its provided tool declaration schema, resulting in an immediate execution crash."
30. **Tool Feedback Neglect (MODEL):** "The model fails to act on an explicit signal in a tool's execution response and pushes forward with an unrelated, misaligned plan."
31. **Tool Recovery Failure (MODEL):** "The model fails to dynamically navigate around tool anomalies. When a tool encounters a perturbation, either an explicit failure (e.g., HTTP 503, rate-limit timeout) or an implicit semantic failure (valid format but corrupted data), the model is trapped in a futile trial-and-error retry loop or blindly over-trusts the broken data instead of pivoting to an alternative tool path."
32. **Mistranslation (TOOL):** "A defect in the tool's integration layer (its wrapper, middleware, or marshaling code) rather than in the environment or the model. The environment produces correct information and the model reasons correctly, but the layer that translates data across the model↔environment boundary conveys it unfaithfully, either garbling an observation sent to the model or mis-mapping the model's action onto the environment."

**MODEL—MODEL (role: PEER)**

33. **Delegation Failure (MODEL):** "The peer models fail to coordinate how work is divided or to account for dependencies and workspace boundaries between their assigned tasks, leading to incomplete, overlapping, or incompatible execution."
34. **Communication Failure (MODEL):** "The peer models fail to exchange information needed for coordination. One may withhold relevant context or fail to use information supplied by the other."

**MODEL—MODEL (role: SUBAGENT)**

35. **Delegation Failure (FOCAL MODEL):** "The focal model, acting as orchestrator, assigns a subagent work with incorrect scope, dependencies, or workspace boundaries."
36. **Communication Failure (FOCAL MODEL/SUBAGENT):** "The focal model is at fault when it omits context needed by a subagent, fails to route information between subagents, or fails to use a subagent's output. The subagent is at fault when it fails to report relevant results or constraints to the focal model."

**EXTERNAL ENVIRONMENT—MODEL**

37. **Service Failure (ENVIRONMENT):** "An external service (an upstream LLM host, a cloud platform, a remote site like YouTube) hits an internal error, timeout, or rate limit and fails the request outright, with no way for the agent to recover."
38. **Stale State Delivery (ENVIRONMENT):** "An external service returns a healthy status code but silently serves stale or cached data, with no signal that it is out of date, so the agent acts as if it has the live state."
39. **Recovery Failure (MODEL):** "The agent fails because of an environment problem that was in fact recoverable. Faced with a transient error, a missing file, or an ambiguous state, the model gives up or acts on a false assumption instead of retrying, diagnosing, routing around it, or asking the user. What separates this from Service Failure and Stale State Delivery is only recoverability: the condition was fixable, so the fault is the model's."

**LOCAL ENVIRONMENT—MODEL**

40. **Observation Failure (MODEL):** "A cue the model needs is present in its observation space, but the model overlooks it and acts without resolving the ambiguity that cue would have settled."
41. **Recovery Failure (MODEL):** same definition as 39.

The **five non-model modes** are: Instruction-Grader Mismatch (OWNER), Context Rationale Erosion (CONTEXT), Mistranslation (TOOL), Service Failure (ENVIRONMENT), Stale State Delivery (ENVIRONMENT).

### 1.4 Disambiguation rules used in judge turn 3 (Figure 4) [V-paper]

These were reconstructed from a two-column PDF extraction; the wording is near-verbatim.

- "A constraint honored, then violated only after a context summary, is CONTEXT—MODEL Context Rationale Erosion (the summary dropped the rationale), not OWNER—MODEL Over-initiative."
- "A goal present throughout but gradually dropped as the history grows is CONTEXT—MODEL Goal Drift, not a Reasoning Failure."
- "Locally sound reasoning that overlooked an available environmental cue is LOCAL ENVIRONMENT—MODEL Observation Failure, not a Reasoning Failure."
- "An earliest error that calls a tool absent from the provided schema (rejected 'tool not found') is MODEL—TOOL Tool Hallucination, not a skipped requirement."
- "Re-deriving already-solved work for lack of a durable note, or acting on a stale durable record, is a MODEL—MEMORY failure (Missed Write / State Staleness), not a context-tracking loop."
- "A service that genuinely failed (rate-limit, IP block, timeout) is EXTERNAL ENVIRONMENT—MODEL Service Failure; a wrapper that corrupted otherwise correct output is MODEL—TOOL Mistranslation."
- "A hard, non-recoverable external block is the root cause even when the model's fallback was poor: this is EXTERNAL ENVIRONMENT—MODEL Service Failure, not instruction-following."
- "A grader that checks a specification the instruction did not state is OWNER—MODEL Instruction-Grader Mismatch (fault: owner), not a model fault…"
- "A dropped constraint guarding a high-rollback-cost action (mass deletion, external comms, financial transactions) is OWNER—MODEL Unauthorized Irreversible Action, not the erosion mechanism that produced it."
- "A subagent that consumed its budget without delivering its assigned output is a MODEL—MODEL (role: SUBAGENT) failure, not the orchestrator's instruction-following."

### 1.5 Annotation protocol [V-paper]

**How the taxonomy was built.**

- It was developed iteratively while reviewing failures from public benchmarks, model system cards, published reports and logged agent trajectories.
- It was then **frozen**. The frozen version was used both for all reported labels and for the judge validation.

**How each example was labelled.**

1. Review all evidence.
2. Identify the system-level failure.
3. Trace backward to the earliest failure from which execution does not recover.
4. Assign the edge, the fault side and the failure mode.

**Safety overlay.** A separate impact tag uses the OWASP Top 10 for LLM and for Agentic Applications (Table 5). Each example carries at most one tag:

| Tag | Source | Examples |
|---|---|---|
| Excessive Agency | LLM06 | E2, E4, E6, E39 |
| Unbounded Consumption | LLM10 | E19, E32, E33 |
| Rogue Agents | ASI10 | E12, E13 |
| Agent Goal Hijack | ASI01 | E15, E16 |
| Misinformation | LLM09 | E11, E28, E31 |
| Sensitive Information Disclosure | LLM02 | E10 |

### 1.6 Datasets [V-paper]

There is no large dataset. The evaluation set is **40 worked examples (E1–E40)**, described as "illustrative rather than exhaustive" and "should not be used to estimate the prevalence". Sources include:

- the Harbor-Mix dataset (https://huggingface.co/datasets/harborframework/harbor-mix), e.g. the GAIA2/ARE adaptability scenario;
- model system cards (o3 chess board edit; "Mythos" sandbox escape; activation-probe evaluation awareness);
- GitHub issues (Aider #3713, OpenClaw #36142, terminal-bench-3 PR #95);
- Docent (https://docent.transluce.org);
- the authors' gists at gist.github.com/harshraj172-scale.

### 1.7 Judge agreement [V-paper]

**Judge setup.**

- Built on the Claude Agent SDK.
- Models: GPT-5.5 at xhigh effort; Claude Opus 4.6, 4.7 and 4.8 at adaptive thinking, effort max.
- Tools: read-only WebSearch, WebFetch, Bash, Read, Grep, Glob.
- A pre-tool hook blocks access to the worked examples and their labels.
- Three turns: (1) evidence reconstruction, (2) classification, (3) reflection and disambiguation. Turn 3 is scored.

**Metrics.** Exact-match accuracy, macro-F1 and Cohen's κ. "Category" means edge plus fault side; "failure mode" additionally requires the named mode.

**Table 2: agreement with human labels on the 40 examples.**

| Judge | Category Acc | Category F1 | Mode Acc | Mode F1 |
|---|---|---|---|---|
| GPT-5.5 | 0.80 | 0.69 | 0.72 | 0.64 |
| Opus-4.6 | 0.75 | 0.61 | 0.70 | 0.57 |
| Opus-4.7 | 0.75 | 0.63 | 0.62 | 0.53 |
| Opus-4.8 | 0.75 | 0.62 | 0.68 | 0.58 |

**Cohen's κ.**

- Category κ against human labels: GPT-5.5 0.76; Opus 4.6 and 4.7 0.71; Opus 4.8 0.70.
- Highest judge-to-judge κ: 0.84 (Opus 4.6 vs 4.8).
- GPT-5.5 failure-mode κ: 0.71.
- Rerunning failure-mode labelling with the gold category supplied (Table 3) raises Opus scores; for example Opus-4.6 goes from Acc 0.70 / F1 0.57 to 0.80 / 0.70.

**Table 4: selective voting (abstain unless at least k of 4 judges agree).**

| Agreement | Coverage | Category P | Category R | Category F1 | Mode P | Mode R | Mode F1 |
|---|---|---|---|---|---|---|---|
| ≥2 of 4 | 1.00 | 0.78 | 0.78 | 0.78 | 0.70 | 0.70 | 0.70 |
| ≥3 of 4 | 0.90 | 0.83 | 0.75 | 0.79 | 0.75 | 0.68 | 0.71 |
| 4 of 4 | 0.68 | 0.96 | 0.65 | 0.78 | 0.89 | 0.60 | 0.72 |

**Dominant judge error.** Judges blame the model when the real fault is in the environment or harness (the Harbor-Mix case study).

### 1.8 Released code and data

- **No repository is named in the paper text,** and GitHub search found none [U].
- A WeChat-sourced claim that "~90% of 393 cases are interface problems" **does not appear in the paper** [U, treat as spurious].
- **Prior art for crosswalks:** https://github.com/canja006/agent-failure-registry is a CVE-style namespace of "AF-xxxx" modes. It has YAML crosswalks for model-or-harness, agentrx, agentfail, agentdebugx, agent-xray, toolfailbench and agentic-faults, a `layer` field (model, harness, tool, environment, user-intent), and is installable with `pip install agent-failure-registry` [V-code].

---

## 2. MAST: "Why Do Multi-Agent LLM Systems Fail?" (arXiv 2503.13657)

**Basics.**

- Authors: Cemri, Pan, Yang, …, Zaharia, Gonzalez, Stoica (UC Berkeley).
- NeurIPS 2025 Datasets & Benchmarks track (PDF on proceedings.neurips.cc) [S].
- Repo: https://github.com/multi-agent-systems-failure-taxonomy/MAST.
- PyPI package `agentdash` 0.1.0, providing `annotator(openai_api_key, model="o1-mini")` and `produce_taxonomy(trace)` [V-code].

**Categories (v3 §4, verbatim)** [V-paper]

- **FC1. System Design Issues:** "Failures originate from system design decisions, and poor or ambiguous prompt specifications."
- **FC2. Inter-Agent Misalignment:** "Failures arise from a breakdown in critical information flow from inter-agent interaction and coordination during execution."
- **FC3. Task Verification:** "Failures involve inadequate verification processes that fail to detect or correct errors, or premature termination of tasks."

**The 14 modes (v3 Appendix A, verbatim), with the share reported in v3 §4** [V-paper]

| ID | Name and definition | Share |
|---|---|---|
| FM-1.1 | Disobey task specification: "Failure to adhere to the specified constraints or requirements of a given task, leading to suboptimal or incorrect outcomes." | 11.8% |
| FM-1.2 | Disobey role specification: "Failure to adhere to the defined responsibilities and constraints of an assigned role, potentially leading to an agent behaving like another." | 1.5% |
| FM-1.3 | Step repetition: "Unnecessary reiteration of previously completed steps in a process, potentially causing delays or errors in task completion." | 15.7% |
| FM-1.4 | Loss of conversation history: "Unexpected context truncation, disregarding recent interaction history and reverting to an antecedent conversational state." | 2.80% |
| FM-1.5 | Unaware of termination conditions: "Lack of recognition or understanding of the criteria that should trigger the termination of the agents' interaction, potentially leading to unnecessary continuation." | 12.4% |
| FM-2.1 | Conversation reset: "Unexpected or unwarranted restarting of a dialogue, potentially losing context and progress made in the interaction." | 2.20% |
| FM-2.2 | Fail to ask for clarification: "Inability to request additional information when faced with unclear or incomplete data, potentially resulting in incorrect actions." | 6.80% |
| FM-2.3 | Task derailment: "Deviation from the intended objective or focus of a given task, potentially resulting in irrelevant or unproductive actions." | 7.40% |
| FM-2.4 | Information withholding: "Failure to share or communicate important data or insights that an agent possess and could impact decision-making of other agents if shared." | 0.85% |
| FM-2.5 | Ignored other agent's input: "Disregarding or failing to adequately consider input or recommendations provided by other agents in the system, potentially leading to suboptimal decisions or missed opportunities for collaboration." | 1.90% |
| FM-2.6 | Reasoning-action mismatch: "Discrepancy between the logical reasoning process and the actual actions taken by the agent, potentially resulting in unexpected or undesired behaviors." | 13.2% |
| FM-3.1 | Premature termination: "Ending a dialogue, interaction or task before all necessary information has been exchanged or objectives have been met, potentially resulting in incomplete or incorrect outcomes." | 6.20% |
| FM-3.2 | No or incomplete verification: "(partial) omission of proper checking or confirmation of task outcomes or system outputs, potentially allowing errors or inconsistencies to propagate undetected." | 8.20% |
| FM-3.3 | Incorrect verification: "Failure to adequately validate or cross-check crucial information or decisions during the iterations, potentially leading to errors or vulnerabilities in the system." | 9.10% |

**Version drift — pin a version before converting labels** [V-code]

- The repo's `taxonomy_definitions_examples/definitions.txt` and LLM-judge notebook use older names:
  - "2.6 Action-Reasoning Mismatch";
  - "3.2 Weak Verification" and "3.3 No or Incorrect Verification" in definitions.txt;
  - the notebook prompt swaps those two, listing "3.2 No or Incorrect Verification, 3.3 Weak Verification".
- The `assets/taxonomy_v11` figure shows yet another set of percentages and labels (e.g. "3.2 No or Incomplete Verification", "3.3 Incorrect Verification").
- GitHub issue #18 is titled "MAD_human_labelled_dataset.json spans three taxonomy versions with renumbered codes" [S, title only].

**MAST-Data / MAD on Hugging Face**

- The paper names `mcemri/MAST-Data`; the repo README names `mcemri/MAD`.
- Files: `MAD_full_dataset.json` and `MAD_human_labelled_dataset.json` [V-code, README].
- Record fields [S, HF card via search; not opened directly]:
  - `mas_name` (AG2, MetaGPT, ChatDev, Magentic, AppWorld, HyperAgent, OpenManus);
  - `llm_name`;
  - `benchmark_name` (ProgramDev, ProgramDev-v2, GSM, Olympiad, GAIA, MMLU, Test-C, SWE-Bench-Lite);
  - `trace_id` (int);
  - `trace` as `{key, index, trajectory}`, where trajectory is raw text;
  - `mast_annotation` as a dict of the 14 codes, each 1, 0 or null.
- **Labels are trace-level and multi-label; there is no step index.**
- Size: 1,642 traces [V-paper]. The human-labelled subset is 21 traces in the paper versus 19 on the card [S]; the counts conflict.

**LLM annotator pipeline** [V-paper and V-code]

- The model is OpenAI o1, prompted with the trace, the MAST definitions and few-shot examples.
- Notebook prompt output: "A. summary", "B. task completed yes/no", "C. per-mode yes/no", delimited by `@@`. The parser is regex-based and defaults to "no" when a mode is missing.
- Traces are truncated to 1,048,570 characters.

**Agreement and cost** [V-paper]

- Human inter-annotator agreement κ=0.88: 3 annotators, 3 rounds of 5 traces, on a 150-trace grounded-theory set from 5 MAS frameworks with 6 experts.
- LLM annotator against humans: accuracy 94%, κ=0.77. Out-of-domain κ=0.79 (OpenManus and Magentic-One on MMLU and GAIA).
- Cost: $1.80 per trace [S, stagnation notes, line-verified there].
- Intervention results: +9.4% and +15.6% on ChatDev [S].

---

## 3. LongRCA Bench (arXiv 2608.15242)

**Links.**

- Leaderboard repo: https://github.com/longrca-bench/longrca-bench.github.io.
- Dataset: https://huggingface.co/datasets/CLoud5-real/longrca-bench (pinned revision `9f45acb6…` in third-party code).

**Data** [V-abs v1 and v4, V-code]

- 1,140 observed failed trajectories with **no injected errors**, all human-annotated for "responsible roles and earliest decisive root-cause steps", with supporting rationale [V-code dataset card].
- The labels are "independently scored": **role and step are separate targets**.
- Length: median 145 steps. Median distance from the reference root to the end is 48 steps; 28.4% of trajectories have more than 100 subsequent steps [V-abs v4].

**The five source domains** [V-code, `leaderboard.json`]

| Source | n |
|---|---|
| SWE-bench Pro | 128 |
| Terminal-Bench 2 | 42 |
| TravelPlanner | 685 |
| VitaBench | 108 |
| WebArena Verified | 177 |

**Label schema** [V-code where stated]

- **Responsible role:** a free-text role or agent name from the trajectory, Who&When-style `mistake_agent`. The TravelPlanner example's actors are System/Terminal, Task Planner, Transport, Stay, Food + Attractions, Verifier, Manager, Writer.
- **Role scoring:**
  - Applies `normalize_role`: NFKC normalization, casefold, whitespace collapse, and removal of a trailing `(-> X)` or `(→ X)` handoff suffix.
  - The prediction must be explicit. It is "never derived from `history[predicted_step].name`".
- **Root step:** the "earliest decisive root-cause step", a **zero-based index into `history`**.

**Trajectory JSON** [V-code, field names from the third-party loader `Jurmean/jev-longrca`; full schema U]

- One JSON file per trajectory under `data/full/<source>/` and `data/mini/<source>/`, plus Parquet files (`longrca-full.parquet`, `longrca-mini.parquet`).
- Fields seen: `question_ID` (e.g. `swe_bench_pro__008`), `history` (list of `{role, name, content}`), `mistake_agent`, `mistake_step`, `source`, `answer`. The format is Who&When-compatible.

**LongRCA-Mini** [V-code, dataset card]

- 200 fixed trajectories, "randomly sampled without replacement with 40 from each benchmark, preserving the original IDs and annotations".
- Mini files are byte-identical to their full-set counterparts.

**Leaderboard repo structure** [V-code]

- `data/leaderboard.json`, schema 1.3.0. Rows store counts, not percentages: `role_correct`, `root_exact_correct`, `root_within_5_correct`, `root_mae`, `valid_step_n`, `failed_n`, plus per-source `root_exact_correct`.
- The model field is constrained to `DeepSeek-V4-Flash` and the sort key is `root_exact`.
- Also present: `data/leaderboard.schema.json`, `data/example_trajectory.json` (a 77-step TravelPlanner visualization), `data/site.json`, `scripts/export_paper_results.py`, `scripts/validate_data.py`, `tests/`, `assets/`, `CONTRIBUTING.md`, and a GitHub Pages workflow.

**How to submit** [V-code]

1. Open a pull request adding `submissions/<id>/` with three files:
   - `metadata.json`: submission_id, method, model, provider, authors, date, code_url, logs_url, license;
   - `predictions.jsonl`: exactly 1,140 lines of `{"question_ID", "predicted_role", "predicted_step"}`, where the step is zero-based;
   - `REPRODUCE.md`.
2. Checks run on schema, count, uniqueness, independent role scoring, and absence of secrets or gold labels.
3. After maintainer review, the maintainers add an aggregate row.

This is a reproducibility leaderboard, not a hidden test, because the labels are public.

**Baselines on the full set, DeepSeek-V4-Flash** [V-code]

| Method | Role acc | Root exact | Root ±5 | Root MAE | Failed |
|---|---|---|---|---|---|
| RCTA | 51.1% | 24.1% | 37.4% | 38.6 | 0 |
| ECHO | 27.5% | 13.2% | 24.7% | 50.4 | 0 |
| All-at-once (Who&When) | 26.2% | 7.6% | 19.9% | 55.9 | 4 |
| Step-by-step | 22.2% | 5.3% | 16.9% | 52.3 | 1 |
| Binary search | 23.0% | 3.4% | 13.3% | 61.7 | 0 |
| FALAT | 19.0% | 2.8% | 12.5% | 66.6 | 0 |

RCTA exact-step results by source: SWE-bench Pro 49/128, Terminal-Bench 2 11/42, TravelPlanner 129/685, VitaBench 27/108, WebArena 59/177.

**RCTA method** [V-abs]

- "Root-Cause Trajectory Attribution, a training-free method that organizes original candidate records and explicit handoff instructions for attribution."
- "Segment summaries and a trajectory outline guide candidate retrieval; available handoff records supply upstream instruction context for the final instruction-execution comparison."
- The full algorithm is [U]. `Jurmean/jev-longrca` is an RCTA-inspired third-party reimplementation. Its v3.1 scored 10% exact on half of Mini and is not the paper's method.

---

## 4. "Root-Cause Attribution Is a Search Problem: Continual Search" (arXiv 2609.13463)

**Status.** [V-abs v1 and v2] plus [S] from https://github.com/vollero/hf-daily-paper-summaries/blob/main/summaries/2026/09/2026-09-15/2609.13463.md. Authors [U]; a search hit linked an author query for R.-G. Dumitru, a co-author of Model or Harness. The paper reuses "the interaction-centric taxonomy" [S].

**MegaRCA-Mix** [S]

- 50 human-annotated failed **Harbor Index** trials, which the abstract calls "long-horizon, execution-heavy tasks".
- Median evidence size is 286K tokens.
- The judge can read trajectories, configurations, verifier outputs, logs and sandbox artifacts.
- Domain counts, sampling and annotator agreement are not reported [U].

**Method** [V-abs and S]

- An agentic judge makes an initial attribution. The same session then continues for turns 2–4 with benchmark-specific prompts that "nudge the judge to keep searching for unresolved diagnostic evidence": inspect unread artifacts, reconsider unresolved candidates, and on turn 2 for MegaRCA, spawn a subagent to independently re-derive.
- It is compared with "Passive Continuation" (re-consideration only), self-consistency and heterogeneous judge panels.

**Results**

- **Abstract** [V-abs]: Opus-4.8 F1 rises 0.471 → 0.608 (+29%); GPT-5.5 rises 0.349 → 0.498.
- **Summary table** [S]: Opus-4.8 0.478 → 0.620, against 0.559 for passive continuation. The difference from the abstract is probably a version change.
- **Other benchmarks** [S]:
  - TRAIL (GPT-5.5): weighted F1 0.426 → 0.500.
  - TELBench first-error accuracy: 0.121 → 0.212.
  - **Short traces regress:** GPT-5.5 exact step falls from 0.345 to 0.241 on AgentRx-retail and from 0.548 to 0.452 on Who&When-algorithm-generated.
  - Artifact coverage (Opus) rises from 70.8% to 97.4%.
  - TRAIL cost: Continual Search $2.58 per trajectory at F1 0.539, versus self-consistency $6.52 at 0.430.
  - Benchmark-defect auditing: F1 0.74, against 0.63 for ABA.
- **Code and data release:** not established [U].

---

## 5. TRAIL (Patronus AI, arXiv 2505.08638; https://github.com/patronus-ai/trail-benchmark)

**Taxonomy tree, exactly as in `benchmarking/run_eval.py`** [V-code]

These are the official leaf definitions.

- **Reasoning Errors**
  - Hallucinations
    - Language-only
    - Tool-related: "(fabricating tool outputs/capabilities)"
  - Information Processing
    - Poor Information Retrieval: "(Tried to find information that was not relevant to the task)"
    - Tool Output Misinterpretation: "(Made assumptions about the tool output or used the tool output in an incorrect context)"
  - Decision Making
    - Incorrect Problem Identification: "(Misunderstood the overall task or the local task)"
    - Tool Selection Errors: "(Used the wrong tool for the task)"
  - Output Generation
    - Formatting Errors: "(Errors with formatting and execution of code or structuring of output in a specific format)"
    - Instruction Non-compliance: "(Failed to perform the task provided and instead did something else)"
- **System Execution Errors**
  - Configuration
    - Tool Definition Issues: "(The tool was not defined correctly by the user or contains some errors that make it inconsistent with its description. For example, web search tool was defined as a calculator tool)"
    - Environment Setup Errors: "(includes permission problems and inability to access resources or API keys)"
  - API Issues
    - Rate Limiting: "(Like 429)"
    - Authentication Errors: "(Like 401/403)"
    - Service Errors: "(Like 500)"
    - Resource Not Found: "(Like 404)"
  - Resource Management
    - Resource Exhaustion: "(includes memory overflow)"
    - Timeout Issues: "(The system took too long to respond)"
- **Planning and Coordination Errors**
  - Context Management
    - Context Handling Failures: "(includes window overflow and state tracking or forgetting important context)"
    - Resource Abuse: "(Called the tool excessively due to memory issues)"
  - Task Management
    - Goal Deviation: "(The system deviated from the task or the subtask)"
    - Task Orchestration: "(includes subtask coordination between agents and progress monitoring)"

**Leaf count.** The tree has 20 leaves. The scorer's `all_categories` adds a 21st, "Incorrect Memory Usage" (2 gold labels use it).

**Location rule from the prompt.** "In the case of 'Resource Abuse' error, only mark the last instance … For all other errors, you must mark the first instance."

**Trace format** [V-code and V-paper]

- Built on OpenTelemetry, "specifically, its most widely adopted open-source derivative compatible with agents, the openinference standard".
- `data/{GAIA,SWE Bench}/<trace_id>.json` holds `{trace_id, spans[]}`, nested via `child_spans`.
- Each span has: `timestamp`, `trace_id`, `span_id`, `parent_span_id`, `trace_state`, `span_name`, `span_kind`, `service_name`, `resource_attributes`, `scope_name`, `scope_version`, `span_attributes`, `duration` (ISO 8601), `status_code`, `status_message`, `events`, `links`, `logs[]`, `child_spans[]`.
- Observed `span_attributes` keys: `openinference.span.kind`, `llm.input_messages.*`, `llm.output_messages.*`, `llm.token_count.*`, `llm.model_name`, `llm.invocation_parameters`, `input.value`, `output.value`, `input.mime_type`, `output.mime_type`, `tool.name`, `tool.description`, `tool.parameters`, `smolagents.max_steps`, `smolagents.tools_names`.
- Agents: Hugging Face OpenDeepResearch (smolagents) with o3-mini on GAIA; CodeAct with claude-3-7-sonnet on SWE-bench Lite.

**Annotation fields** [V-code]

- Files: `processed_annotations_{gaia,swe_bench}/<trace_id>.json`.
- `errors[]`: `{category, location (span_id), evidence, description, impact: LOW|MEDIUM|HIGH}`.
- `scores[]`: `{reliability_score, security_score, instruction_adherence_score, plan_opt_score` (each 0–5), the matching `*_reasoning` fields, and `overall}`.
- HF dataset: `PatronusAI/TRAIL` [V-paper].

**Size** [V-paper and V-code]

- 148 traces (118 GAIA + 30 SWE-bench), 1,987 spans, of which 575 contain errors.
- 841 errors, an average of 5.68 per trace. The repo holds 836 parseable errors, with one malformed file.
- Most frequent categories: Formatting Errors 196, Instruction Non-compliance 152, Goal Deviation 63, Resource Abuse 57, Tool-related 53, Language-only 49, Task Orchestration 46.

**Metrics, from `calculate_scores.py`** [V-code]

- **Category F1:** weighted F1 over per-trace binary category-presence vectors (sklearn `average='weighted'`).
- **Location accuracy:** |gold span_ids ∩ predicted span_ids| / |gold span_ids|, averaged over traces.
- **Joint accuracy:** |gold (span_id, category) pairs ∩ predicted pairs| / |gold pairs|. Extra predictions are not penalized.
- **Pearson r** between predicted and gold for the reliability, security, instruction-adherence, plan-optimality and overall scores.

**Leaderboard** [V-paper, Table 1]

| Model | GAIA Cat-F1 | GAIA Loc-Acc | GAIA Joint | GAIA ρ | SWE Cat-F1 | SWE Loc-Acc | SWE Joint | SWE ρ |
|---|---|---|---|---|---|---|---|---|
| Gemini-2.5-Pro (best) | 0.389 | 0.546 | 0.183 | 0.462 | 0.148 | 0.238 | 0.050 | 0.817 |
| OpenAI o3 | 0.296 | 0.535 | 0.092 | 0.449 | context limit exceeded | | | |
| Claude-3.7-Sonnet | 0.254 | 0.204 | 0.047 | 0.738 | context limit exceeded | | | |
| GPT-4.1 | 0.218 | 0.107 | 0.028 | 0.411 | 0.166 | 0.000 | 0.000 | 0.153 |

- The paper's headline is "11% combined joint accuracy". Three of eight models exceed context on SWE.
- Any live HF leaderboard numbers are [U].

---

## 6. AgentErrorTaxonomy, AgentErrorBench and AgentDebug (arXiv 2509.25370; https://github.com/ulab-uiuc/AgentDebug)

**Error types by module, from `detector/error_definitions.py`, verbatim definitions** [V-code]

Labels are module-qualified. "Hallucination" appears under both memory and reflection, which is why the paper counts 17 types while the code has 18 module-type pairs.

- **Memory**
  - `over_simplification`: "Agent oversimplifies complex information from previous N steps, ignoring details and key factors, leading to decisions based on partial or oversimplified summaries"
  - `memory_retrieval_failure`: "Relevant information exists in agent memory but fails to be retrieved when needed"
  - `hallucination`: "Agent 'recalls' events that never happened, object states never observed, or actions never executed, and uses these as basis for reasoning…"
- **Reflection**
  - `progress_misjudge`: "Agent incorrectly evaluates progress toward completing the overall task goal, being either overly optimistic or pessimistic"
  - `outcome_misinterpretation`: "Agent correctly executes an action but incorrectly interprets the direct result or environment feedback from that action"
  - `causal_misattribution`: "Agent correctly identifies a failure phenomenon but attributes it to the wrong cause"
  - `hallucination`: "Agent believes it performed actions that never actually occurred"
- **Planning**
  - `constraint_ignorance`: "Planning ignores task constraints, not considering resource limits (time, budget, space) or other relevant restrictions"
  - `impossible_action`: "…fundamentally impossible under current physical or logical conditions. May include decomposition problems"
  - `inefficient_plan`: "…can theoretically complete task but is extremely inefficient, lengthy, or illogical"
- **Action**
  - `misalignment`: "Generated specific action completely contradicts the intention stated in current plan module"
  - `invalid_action`: "Uses action that does not exist"
  - `format_error`: "Generated action has invalid format causing parse failure"
  - `parameter_error`: "Action parameters are unreasonable or incorrectly chosen"
- **System**
  - `step_limit`: "Agent executes reasonably but fails due to reaching system maximum step limit"
  - `tool_execution_error`: "External tool or API called by agent returns error or exhibits unpredictable behavior"
  - `llm_limit`: "Agent response limitations cause failure" (e.g. timeout, max tokens)
  - `environment_error`: "Simulation environment itself has bugs, network issues…"
- **Others:** `others`.

**Critical error step definition** [V-code, Phase-2 prompt] "the earliest and most important error that led to task failure… the EARLIEST point where the agent made a decision or error that set it on an irreversible path to failure… if we could go back in time and fix ONLY that error, the entire trajectory would likely succeed." The prompt also says:

- step 1 has only planning and action modules;
- system errors are valid critical errors.

**Data format** [V-code]

- The data is distributed via Google Drive (link in the README).
- Trajectory: `{metadata:{won, model, env_id, steps, …}, messages|chat_history:[{role, content}]}`. Assistant content carries `<plan>`, `<memory>`, `<reflection>` and `<action>` tags.
- Label: `{trajectory_id, LLM, task_type, critical_failure_step` (a 1-indexed assistant turn), `critical_failure_module, step_annotations:[{step, <module>:{failure_type, reasoning}}]}`. This structure was seen through the TrajDebug converter.
- Detector output, `CriticalError`: `critical_step, critical_module, error_type, root_cause, evidence, correction_guidance, cascading_effects[{step, effect}], confidence`.

**Benchmark size** [S, from full text] 200 trajectories: ALFWorld 100, WebShop 50, GAIA 50. Ten annotators, κ=0.55.

**Results, GPT-4.1** [S, from full text]

| Method | Step | Step+Module | All correct |
|---|---|---|---|
| AgentDebug (average) | 45.0 | 31.3 | 24.3 |
| Direct prompting | 28.0 | 10.0 | 0.3 |

- On GAIA, AgentDebug reaches 58.0 / 44.0 / 38.0.
- Re-rollout raises task success by up to 26%; for example, ALFWorld with GPT-4o-mini goes from 21 to 55.
- One inconsistency: the paper body also states 50.0 / 42.5.

---

## 7. Who&When (arXiv 2505.00212) and Who&When Pro (arXiv 2607.09996)

**Who&When** (ICML 2025; https://github.com/mingyin1/Agents_Failure_Attribution)

- **Decisive step** [V-code README and S]: the annotations give "the failure-responsible agent (who failed), the decisive error step (when the critical error occurred), a natural language explanation."
  - The survey formalizes it as the earliest step at which every feasible continuation fails: t* = min{t | ∀T′∈C(T≤t), Ω(T≤t⊕T′)=0}.
  - It also notes current practice is "role-aware and recoverability-aware" [V-paper, survey].
- **Format** [V-code]
  - `Who&When/Algorithm-Generated/*.json` (126 files; CaptainAgent; median 10 steps): `is_correct, question, question_ID, level, ground_truth, history[{content, role, name}], mistake_agent, mistake_step` (a string holding a 0-based index into `history`), `mistake_reason, system_prompt{agent: prompt}`.
  - `Hand-Crafted/*.json` (58 files; Magentic-One; median 32.5 steps, maximum 130): `history[{content, role}], question, ground_truth, is_corrected, question_ID, mistake_agent, mistake_step, mistake_reason`.
  - The repo holds 184 files, which matches the "184 annotation tasks" [V-code].
- **Metrics** (`Automated_FA/evaluate.py`) [V-code]: agent accuracy = #(pred_agent == mistake_agent) / N; step accuracy = #(pred_step == mistake_step) / N. Both are exact match.
- **Results** [S]: the best method reaches 53.5% agent-level and 14.2% step-level accuracy; hand-crafted step-level is 8.77%.
- **Survey's range** [V-paper]: published step-level accuracy on Who&When spans about 25% to 52% (CHIEF).

**Who&When Pro** (https://github.com/ag2ai/whowhen_pro; dataset HF `Leoxx/whowhen_pro`, CC-BY-4.0)

- **Construction** [V-code]: "warm-start injection pipeline that replays a successful agent trajectory up to a chosen step, introduces one realistic error, and lets the agent continue."
  - 12,326 failed trajectories, 26 source benchmarks, 9 task families, **18 error modes**, three modalities (text, image, video).
  - The text subset is 6,257 traces per TokenTrim; the "17-code taxonomy" mentioned there is [S].
  - The README roadmap marks "Full benchmark data release" as not yet done.
- **Decisive step, from the official prompt** [V-code]: "The first decisive error is the step that most directly causes the system to go wrong and eventually produce an incorrect answer."
- **Ground-truth format** [V-code, `score.py`]:
  - `ground_truth{agent | agents[], step | step_coord | round+position, mode, accepted_predictions[{agent_name, step_coord, mode}]}`.
  - Step coordinates are framework-specific. Examples: mathchat uses `2*round+position`; eva uses `(step-2)//2`; debate and dylan accept round only.
  - Error-mode codes such as `P.1`, `R.2`, `PL.1`, `A.3`, `C.3`, `V.1` come from `taxonomy.yaml` in the dataset. V.1 appears as "Context/memory Loss" and V.2 as "Inadequate Or Incorrect Verification" in a test fixture [S]. The full list is [U].
- **Metrics** [V-code]:
  - **Agent:** accuracy averaged per framework; single-agent frameworks are excluded.
  - **Step:** accuracy averaged per framework.
  - **Error Mode:** macro-F1 over the observed classes.
  - **All:** all three correct on the same trace.
  - Each axis is matched independently against the canonical answer or any accepted alternate.
- **Text-subset results** [S, paper Table 4 via TokenTrim]:

| Model | Who | When | What | All |
|---|---|---|---|---|
| GPT-5.4 | 55.7 | 72.3 | 15.3 | 21.3 |
| GLM-5 | 54.9 | 71.1 | 22.2 | 25.3 |

---

## 8. Six further attribution methods and benchmarks

**AgenTracer (arXiv 2509.03312; https://github.com/bingreeky/AgenTracer)** [V-code README; numbers S]

- **Method:** counterfactual replay plus programmed fault injection produce **TracerTraj** (over 2,000 annotated trajectory/error-step pairs from 6 multi-agent frameworks × 6 datasets). AgenTracer-8B (Qwen3-8B) is then trained with multi-granular reinforcement learning to output the responsible agent and decisive step.
- **Numbers:**
  - Up to +18.18% over Gemini-2.5-Pro and Claude-4-Sonnet on Who&When.
  - On hand-crafted Who&When agent-level accuracy: +26.0% over GPT-4.1 and +12.2% over Claude-4-Sonnet.
  - 4.8–14.2% downstream gains on MetaGPT and MaAS.
- **Artifacts:** the data pipeline (a MetaGPT example) and an expanded data release (GitHub release `data-v1.0.0`, which "is not exactly identical" to the paper's data). The model weights will **not** be released.

**AgentRx (arXiv 2602.02475; https://github.com/microsoft/AgentRx; HF `microsoft/AgentRx`)** [V-code; V-abs v2]

- **Method:** raw logs are normalized into a Trajectory IR `{trajectory_id, instruction, steps[{index, substeps[{sub_index, role, content}]}]}`. The pipeline then generates static invariants (policy, tool and structure) and dynamic per-step invariants, checks them, and produces an auditable violation log. An LLM judge uses that log to localize the **critical failure step** (first unrecoverable) and assign one of 10 categories:
  1. Instruction/Plan Adherence Failure
  2. Invention of New Information
  3. Invalid Invocation
  4. Misinterpretation of Tool Output
  5. Intent-Plan Misalignment
  6. Underspecified User Intent
  7. Intent Not Supported
  8. Guardrails Triggered
  9. System Failure
  10. Inconclusive
- **Data:** v1 had 115 trajectories (τ-bench retail, Flash incident management, Magentic-One). v2 has "170 trajectories across 11 diverse task settings".
- **Ground-truth format:** `{trajectory_id, failures[{failure_id, step_number, step_reason, failure_category, category_reason, failed_agent}], root_cause{failure_id, reason_for_root_cause}, failure_summary}`. All failures are listed; `root_cause` points to the critical one.
- **Numbers** [S, Microsoft blog summary]: +23.6% absolute in failure localization and +22.9% in categorization over baselines.

**Oat: "Tracing Agentic Failure from the Flow of Success" (arXiv 2607.12747; https://github.com/deeplearning-wisc/OAT)** [V-code; numbers S]

- **Method:** unsupervised, **one-class**. It is trained only on successful trajectories:
  - Step representations come from Qwen3.5-27B hidden states (mean-pooled), reduced by PCA to 64 dimensions.
  - A neural CDE with a gated control path models the successful dynamics.
  - Each step gets a reconstruction-error anomaly score. Detection is by top-k (k=3) or conformal prediction (α=0.2).
  - Out-of-distribution transfer uses CORAL alignment.
- **Data:** MCP-Atlas (Qwen3.5-27B runs; failure steps annotated by the authors) for in-domain evaluation, and Who&When for OOD.
- **Metrics:** top-k and conformal precision, recall, F1 and hit rate; step-level AUROC and AUPRC.
- **Numbers:**
  - MCP-Atlas F1: 0.435 (conformal) and 0.420 (top-k), against GPT-4o 0.212 and GPT-5 0.181. Top-k recall 0.706, hit rate 0.777.
  - Who&When OOD F1: 0.225, against GPT-5 0.152. Conformal AUROC about 0.758.
  - 200–5000× faster than prompting.

**TrajDebug (arXiv 2608.06346, EMNLP 2026 Findings; https://github.com/THU-KEG/TrajDebug)** [V-paper; V-code]

- **Method:**
  1. Build multi-granularity history compression.
  2. **Error trigger detection** with verbatim evidence for both the commitment and the violated reference (Task, History or Intra-step conflict).
  3. **Error state classification:** cluster triggers by the violated object, then classify their resolution and terminal impact as repaired, persistent or dormant.
  4. **Causal attribution:** pick the origin among terminal-relevant candidates.
- **TrajErrBench:** 486 failed trajectories (τ²-Bench 400 with an average of 29.3 steps; SWE-Bench Pro 86 with an average of 119.7 steps, run in the OpenHands scaffold).
  - Three annotators, majority vote.
  - Critical-step Fleiss' κ: 0.91 (τ²) and 0.674 (SWE).
  - Labels are `<module>.<subtype>`: reason.{WrongChoice, InvalidInference, MissingAssumptionCheck}, plan.{BadDecomposition, WrongOrder, UnrealisticPlan, OverExplore, GoalDrift}, obs.{IgnoreOutput, MisreadOutput, GroundingFail}, act.{WrongTool, WrongActionSequence, ToolSchemaMismatch, UnsafeOrForbiddenAction}, verify.{NoVerification, PrematureTermination, WrongVerification}.
  - Released in Chinese and English editions.
- **Metric:** exact critical-step accuracy. The appendix also reports a [GT−3, GT] window.
- **Numbers** (macro average over 7 sets and 869 trajectories):
  - TrajDebug 34.11%, against 25.69% for direct prompting on the same Qwen3-235B backbone.
  - AgentDebugger 23.72%, AgentRx 23.10%, CHIEF 18.77%.
  - τ² 52.75%, SWE-Pro 24.41%.
  - Using the diagnosis as re-execution feedback adds +10.80% task success.
- **Artifacts:** code, a unified-schema converter (section 10(ii) below), the data and a viewer.

**SearchAuditor (arXiv 2608.05212; https://github.com/lzzzx666/SearchAuditor)** [V-code; numbers S]

- **SearchAuditBench:** 1,243 failed deep-search trajectories from 8 open models and 5 benchmarks, averaging 73.1 messages and 65.1K tokens.
  - Fields: `index, model, dataset, query, predicted_answer, gold_answer, trajectory[], critical_step{critical message + tolerance span}, root_cause_primary, rationale, repair_directive, repair_rubrics[]`.
  - Shipped as a PPMd zip.
- **Six-way root cause:** Search Coverage Gap, Unverified Source Reliance, Candidate Mismanagement, Constraint Neglect, Entity–Relation Misbinding, Unsupported Answer.
- **Method:** three parallel audits, then evidence-grounded field-wise adjudication, then diagnosis-conditioned repair synthesis.
- **Metrics (README):**
  - CS-Strict: exact critical message.
  - CS-Loose: inside the tolerance span.
  - RC-Acc and RC-F1.
  - Diag: correct root cause and CS-Loose.
  - Rep@Diag.
  - FPS.
- **Numbers** [S]: best baseline (GPT-5.5) 26.6% against SearchAuditor 32.3%; the metric is likely Diag [U]. Repairs fix 17.37% of Kimi-K2.6 failures and 10.33% of Quest-35B failures.

**"Long-Horizon Agent Trajectory Attribution: A Unified Benchmark and Fine-Grained Annotation Framework" (arXiv 2608.06909; https://github.com/chenjing-2024/agent-trajectory-attribution)** [V-abs; S]

- **Data:** a unified **component schema** over 1,351 trajectories from AgentDojo and Agent3Sigma (Stage and Canary): 409 task-aligned actions, 532 unsafe actions, 410 safety refusals.
- **Labels:** a primary attribution component, plus attack and execution chains.
- **Tasks:** primary attribution localization and attribution-chain recovery.
- **Baselines:** incremental trajectory contribution, and component-level leave-one-out perturbation.
- **Components named:** memory, skills, configuration, tools, tool observations, user instructions.
- **Artifacts:** a reusable "annotation skill". The repo says the data is still being released [S]. Agreement statistics are [U].

---

## 9. "Failure as a Process: An Anatomy of CLI Coding Agent Trajectories" (arXiv 2607.09510)

**Authors** [V-abs]: Xiangxin Zhao, Han Li, Shuaiting Li, Tianyi Zhao, Earl T. Barr, Federica Sarro, He Ye.

**Scope** [V-abs]

- 3,843 trajectories from 7 frontier models × 3 scaffolds (OpenHands, MiniSWE, Terminus2) on Terminal-Bench.
- Filtered to 1,794 complete trajectories for manual annotation, over 63,000 steps. The split is 1,184 failed and 610 successful [S].
- 14 findings. "failures are predominantly driven by epistemic errors, typically begin within the first few execution steps, and often remain hidden until recovery is no longer possible."

**Taxonomy and numbers** [S, LatentEval write-up via the stagnation notes; not line-verified]

- Top level: **Epistemic 57.9%** (false premise 30.7%, specification neglect 14.9%), **Competence 32.8%**, **Environment 9.4%**.
- Timing:
  - The decisive error falls at **median step 7** of a median 27-step failed run.
  - The first observable signal appears around step 16.
  - The median recovery window is **1 step**.
  - 39.1% of runs had no recoverable step.
- Post-lock-in behaviour (share of runs / share of wasted execution):

| Behaviour | Runs | Wasted execution |
|---|---|---|
| Repairs the wrong problem | 24% | 39% |
| Repeats the same approach | 15% | 29% |
| Runs checks that cannot change the outcome | 28% | 15% |
| Fabricates success | 15% | 13% |
| Gives up | 18% | 4% |

- 26% of failed trajectories fabricate success.
- Monitor: **82% precision at 2–3% FPR, but 18.2% recall** (28.8% when requirements are supplied).
- Dataset release: [U].

---

## 10. Compaction: constraint loss benchmarks

**"Governance Decay" (arXiv 2606.22528, ConstraintRot)** [S, two secondary sources; no paper text available]

- **ConstraintRot:** 1,323 episodes with **deterministic tool-call grading** (rule violation is parsed from tool-call arguments) across seven model families.
- Violation is 0% with the policy in full context and 30% after compaction on average, up to 59% for the worst family.
  - When the constraint survives the summary, violation is 0%; when it is dropped, violation is 38%.
  - Pooled reference numbers by strategy: truncate 38%, summarize 26%, head-tail 0%, floor or pinned about 0%.
- Also introduces a "Compaction-Eviction Attack" (bias the summarizer into omitting the policy).
- Mitigation is **Constraint Pinning**: keep governance constraints out of lossy compaction.
- Official code [U].
- An independent replication exists at https://github.com/ksdisch/decay-pin:
  - rule visible 0/20 violations; truncation 20/20; pinned 0/40;
  - LLM-summarize 2/40, and both failures were second-generation rolling summaries that lost the rule;
  - verdicts are pre-committed and reported with Wilson and Newcombe intervals.

**"Lost in Compaction" (arXiv 2608.11242, COMPINT)** [V-paper, full text via Claude-Researcher]

- **Official code:** https://github.com/ZhiqiEliWang/compaction-integrity. A third-party reimplementation plus the SC-GUARD service is at https://github.com/NabiBukhsh-AI/Holdfast.
- **Session constraint (SC)** has three conditions: "(1) s is not part of the user's task, (2) s is meant to constrain the LLM's decoding within the same session, and (3) s has no intended use outside that session." It is linguistically a *generic* directive.
- **Five categories:** Action, Information, Process, Preference, Output. **15 SCs**, 3 per category, each with a multiple-choice probe (compliant option vs violating option).
- **Contexts:** WildChat, Hermes Agent and OpenResearcher, stitched or truncated to about 100K tokens. 50 contexts per dataset, so N=750 per dataset.
- **Injection:** Top, Middle, Bottom, or Multi (k random user turns). Framing crosses Strict ("This is an important constraint:") with Direct ("For the rest of this session").
- **Compactors:**
  - Recent-5;
  - LLMLingua-2 with a 500-token budget;
  - gpt-oss-120b, Qwen3-30B-A3B and Gemma-4-E4B with the Anthropic compaction prompt;
  - gpt-oss-120b with the pi-mono prompt (OpenClaw);
  - GPT-5.4-mini.
- **Metrics:**
  - **Retention:** Retain(s, C(H)) ∈ {0,1}, judged by GPT-5.4.
  - **Compliance:** c̄_g = (1/N) Σ 1[LLM_prob(x_prob, K_g) = y_prob] under four conditions: long context with the SC, long context without it, compacted, and upper bound K_ub = C(H) ⊕ s.
  - **Effect Retention:** ER = (c̄_comp − c̄_lctx) / (c̄_ub − c̄_lctx).
- **Results:**
  - Retention averages 17%.
  - Recent-5 and LLMLingua-2 retain about 0%.
  - Hermes Agent: gpt-oss-120b with the Anthropic prompt retains 18.5% (ER 23.8%); with the pi-mono prompt it retains 36.3% (ER 27.8%).
  - GPT-5.4-mini ranges from 6.7% to 98% retention.
  - The SC-aware extractor (registry S^t concatenated after compaction, H̃ = C(H) ⊕ S^t) keeps retention above 90%.

**"Omission Constraints Decay While Commission Constraints Persist in Long-Context LLM Agents" (arXiv 2604.20911; sole author Yeran Gamage)** [V-abs via a GitHub mirror; details S]

- **Security-Recall Divergence (SRD):** prohibition ("omission") constraints decay under context pressure, while requirement ("commission") constraints persist.
- **Design:** 4,416 trials, 3 arms, 12 models, 8 providers, depths t ∈ {5, 10, 13, 16, 20, 25}.
  - Arm A: no dilution.
  - Arm B: schema dilution with 20 cloud tool schemas (about 482 tokens each), which simulates a "Context-Exhaustion Injection" via MCP tool registration.
  - Arm C: token-matched neutral padding.
- **Result:** with Mistral Large 3, omission compliance falls from 73% at turn 5 to 33% at turn 16 while commission compliance stays at 100% (p < 10⁻³³). Semantic schema content explains 62–100% of the dilution effect.
- **Metric, Safe Turn Depth (STD):** STD = t_k + (CR(t_k) − 0.5) / (CR(t_k) − CR(t_{k+1})) · (t_{k+1} − t_k).
  - Mistral 10.6 turns, 95% CI [5.0, 16.7]; Qwen 3.5 7.1 turns.
  - A Safe Token Budget of about 15K tokens.
  - Re-injecting the constraint before STD restores compliance.
- **Code:** [U].

---

## 11. Loop and stuck detection: prior art

**OpenHands SDK (current; https://github.com/OpenHands/software-agent-sdk, `openhands-sdk/openhands/sdk/conversation/stuck_detector.py`, commit b347047 of 2026-10-03)** [V-code]

- **Window:** the last 20 events (`MAX_EVENTS_TO_SCAN_FOR_STUCK_DETECTION`), only those after the last user `MessageEvent`.
- **Thresholds (`StuckDetectionThresholds`):** action_observation=4, action_error=3, monologue=3, alternating_pattern=6.
- **Equality, ignoring ids:**
  - `ActionEvent` compares (source, thought, action, tool_name).
  - `ObservationEvent` compares (source, observation, tool_name).
  - `AgentErrorEvent` compares (source, error).
  - `MessageEvent` compares (source, llm_message).
- **The five scenarios:**
  1. The last 4 actions are all equal **and** the last 4 observations are all equal.
  2. Action-error streak: the same action paired with `AgentErrorEvent`, with a streak **greater than 3** (stuck). At exactly 3, the detector emits the nudge text: "You've called `{tool}` with the same arguments 3 times in a row and gotten the same error each time: {error}. Repeating the exact same call again will not work — review the error message and either correct the arguments or try a different approach." The nudge fires once per streak.
  3. Monologue: at least 3 consecutive agent `MessageEvent`s with no user input. `CondensationSummaryEvent`s do not break the run; any action or observation does.
  4. Alternating A,B,A,B,A,B: with at least 6 events, last 6 actions and 6 observations where item i equals item i+2.
  5. Context-window error loop: a stub returning False (TODO, agent-sdk issue #282).
- **Wiring:** `LocalConversation(stuck_detection=True, stuck_detection_thresholds=…)`.

**Legacy OpenHands (`openhands/controller/stuck.py`, tag 0.59.0)** [V-code]

- **Scope:** headless mode checks the full history; interactive mode checks only after the last user message. User messages and Null events are filtered out, and at least 3 events are required.
- **Scenarios:**
  1. 4 identical actions plus 4 identical observations. `_eq_no_pid` ignores the pid; `CmdOutputObservation` compares (command, exit_code); `edit_file_by_replace` compares the first 3 code lines.
  2. 3 identical actions where all 3 observations are `ErrorObservation`. Also caught: 3 IPython runs with the same SyntaxError (unterminated string literal; invalid syntax with "Perhaps you forgot a comma?"; incomplete input) and a consistent error line.
  3. The last 3 agent `MessageAction`s are identical with no Observation between them.
  4. Six-step alternating pattern.
  5. At least 10 `AgentCondensationObservation`s with nothing else between consecutive ones.

**SWE-agent (commit 3ea751c)** [V-code]

- There is **no repeated-action detector**.
- Guards that do exist:
  - `max_requeries=3`: requery on format, blocklist or bash-syntax errors, then "Exit due to repeated format/blocklist/bash syntax errors".
  - `execution_timeout=30s`, `max_consecutive_execution_timeouts=3` ("Exiting agent due to too many consecutive execution timeouts"), `total_execution_timeout=1800s`.
  - `per_instance_cost_limit` and `per_instance_call_limit`.
  - The action sampler warns "Only identical actions were proposed".
- **mini-swe-agent (04d809c):** `step_limit` (default 0, meaning unlimited), `cost_limit=3.0`, `wall_time_limit_seconds`, `max_consecutive_format_errors=3`.

**Aider (5dc9490)** [V-code] `max_reflections = 3`. When a lint, test or parse reflection loop exceeds it: "Only {max_reflections} reflections allowed, stopping."

**Claude Code** [S, user-reported GitHub issues; no official documentation reachable]

- A stall watchdog, not a loop guard:
  - `CLAUDE_ASYNC_AGENT_STALL_TIMEOUT_MS`, default 600,000 ms, aborts a background subagent after no stream chunk.
  - It resets on each chunk and on a ~1 Hz progress tick, and defers while a tool is in flight.
  - Error text: "Agent stalled: no progress for 600s".
  - A 60-second variant appears in v2.1.231 logs as "stall watchdog fired after 60000ms with no progress".
- Sources: anthropics/claude-code issues #85265 and #86499.
- No documented semantic loop guard was found [U].

**Other** [S]

- "Zombie Agents: Detecting Semantic Livelock…" (AIware 2026; not read).
- AgentStop (2605.15206): early-termination AUC 0.6–0.7.
- Coherence Collapse (2603.24631): defines "Confused Thrashing" as "≥3 edit attempts on the gold file, none persisting into the final diff".

**Weave "582 spirals" blog: not found** in any reachable source [U]. Obtain the URL from the requester.

---

## 12. Survey: "A Survey for LLM Agent Trajectory Analysis: From Failure Attribution to Enhancement"

**Links.** IEEE TSE 2026, DOI 10.1109/TSE.2026.3717765. Repo: https://github.com/shubhamrgandhi/Awesome-LLM-Agent-Trajectory-Analysis; the full PDF is in the repo, last commit 2026-08-25. Status [V-paper].

**Scope.** 55 papers from early 2025 to April 2026, selected from 1,652.

**Five dimensions:**

1. Failure Taxonomy (9 papers)
2. Failure Attribution (22 papers)
3. Enhancement and Optimization (14 papers)
4. Monitoring and Tools (7 papers)
5. Datasets and Benchmarks (10 papers)

**Four perspectives on failure taxonomies:**

- **Task-execution phase (WHERE):** Lu et al.; AgentEval.
- **Agent capability module (WHAT):** AgentErrorTaxonomy; TRAIL.
- **System and interaction (WHO):** AgentRx; AgentFail; MAST.
- **Environment context (WHY):** Aegis-Song (exploration, exploitation, resource exhaustion).

**Four attribution paradigms (Table 3: passive/active, statistical/reasoning, general/specialized, post-hoc/runtime):**

- **Pattern-analysis based** (passive, statistical): FAMAS (spectrum-based), Barrak's Planner→Executor→Critic, CORRECT, SDBL, AgentEval (DAG), ProMAS (Markov entropy).
- **LLM-reasoning based:** Who&When (all-at-once, step-by-step, binary search), ECHO, RAFFLES, CDC-MAS (Shapley values), A2P, CHIEF (causal graph and backtracking), AgentRx, CodeTracer, ERRORPROBE.
- **Model fine-tuning based** (specialized): AgenTracer-8B (reinforcement learning), GraphTracer, Aegis-Kong (SFT, RL, contrastive).
- **Dynamic runtime based** (active): DoVer (intervention), AgentDebug, TraceElephant (counterfactual), AgentFail.

**Enhancement families:** structural and workflow; agent-internal; runtime and supervisory.

**Datasets (Table 6) — scale is the number of failure trajectories**

| Benchmark | Type | Source systems | Scale | Annotation |
|---|---|---|---|---|
| Who&When | Real-world | CaptainAgent, Magentic-One (GAIA, AssistantBench) | 127 (repo 184) | Responsible agent, faulty step, some root cause |
| TRAIL | Real-world | OpenDeepResearch (GAIA), CodeAct (SWE-Bench Lite) | 148 | Coarse and fine root cause (type, location) |
| AgentErrorBench | Real-world | ALFWorld, GAIA, WebShop | 200 | Failure step, module and error type |
| TraceElephant | Real-world | CaptainAgent, Magentic-One, SWE-Agent | 220 | Agent and step; full observability and reproducible environment |
| AgentFail | Real-world | 10 Dify/Coze systems | 307 | Agent, root cause, repair strategy |
| AgentRx | Real-world | τ-bench, Flash, Magentic-One | 115 | Step, category, first unrecoverable failure |
| CodeTraceBench | Real-world | SWE-Agent, MiniSWE, OpenHands, Terminus 2 | 4,354 (README says 4,316) | Stage, step, reason |
| MP-Bench | Real-world | Who&When systems | 289 | Step, reason, ideal action |
| Aegis-Kong | Error injection | 6 multi-agent systems | 9,533 | Agent and error mode |
| CORRECT-Error | Error injection | Magentic-One, AutoGen | 2,000+ | Faulty step |

The README adds:

- AgentProcessBench: 1,000 trajectories, 8,509 step labels.
- TELBench/DRIFT: 1,000 trajectories with span labels.
- ContextBench: 1,136 tasks.
- ClawBench: 153–283 web tasks with 5-layer bundles.

**Key observations.** "step-level attribution accuracy remains limited (around 40%)". On Who&When, step accuracy ranges from 25% to 52%. TraceElephant step accuracy is about 33%.

---

## 13. Synthesis

### (i) Unified mapping: our component dimension against published modes

**Abbreviations:** MoH = Model-or-Harness; AET = AgentErrorTaxonomy; TEB = TrajErrBench; SA = SearchAuditor; FaP = Failure-as-a-Process; Gov = Governance Decay; LiC = Lost in Compaction; Omi = Omission Constraints Decay.

| Our component | Model-or-Harness (edge · fault) | MAST | TRAIL | AET / TEB | AgentRx | Other |
|---|---|---|---|---|---|---|
| **model** | OWNER—MODEL·MODEL: Reasoning Failure, Domain Knowledge Deficit, Sycophancy, Value Misalignment, Instruction-Following Failure; GRADER: Specification Gaming, Evaluation Awareness | FM-1.1, FM-2.6 | Language-only, Incorrect Problem Identification, Formatting Errors, Instruction Non-compliance | reflection.*, memory.hallucination; TEB reason.{WrongChoice, InvalidInference, MissingAssumptionCheck} | Invention of New Information; Instruction/Plan Adherence | FaP Epistemic and Competence; SA Entity–Relation Misbinding |
| **planner** | Reasoning Failure ("flawed execution plan") | FM-2.3 Task derailment | Goal Deviation; Task Orchestration | planning.{constraint_ignorance, impossible_action, inefficient_plan}; TEB plan.{BadDecomposition, WrongOrder, UnrealisticPlan, OverExplore, GoalDrift} | Intent-Plan Misalignment | SA Candidate Mismanagement, Constraint Neglect |
| **context builder** | CONTEXT—MODEL·MODEL: Goal Drift, State Tracking Failure | FM-1.4 Loss of conversation history | Context Handling Failures | memory.over_simplification | – | Omi SRD and Context-Exhaustion Injection |
| **compactor** | CONTEXT—MODEL·CONTEXT: **Context Rationale Erosion** (harness-driven; model-side if model-driven) | FM-1.4 (partial) | Context Handling ("window overflow") | – | – | LiC retention and ER; Gov ConstraintRot; OpenHands context-window loop |
| **memory** | MODEL—MEMORY: Missed Write, State Staleness, Overgeneralization, Memory Rationale Erosion, Pollution, Redundancy, Missed Read, Memory Following Failure | – | "Incorrect Memory Usage" (scorer only) | memory.{memory_retrieval_failure, hallucination} | – | Who&When Pro V.1 "Context/memory Loss" [S] |
| **retrieval** | Suboptimal Arguments (vague search), Missed Read | – | Poor Information Retrieval | obs.GroundingFail | Misinterpretation of Tool Output | SA Search Coverage Gap, Unverified Source Reliance |
| **tool** | MODEL—TOOL·MODEL: Malformed Arguments, Suboptimal Arguments, Incorrect Tool Selection, Tool Hallucination, Tool Feedback Neglect, Tool Recovery Failure | – | Tool-related hallucination, Tool Output Misinterpretation, Tool Selection Errors, Resource Abuse | action.{misalignment, invalid_action, format_error, parameter_error}; TEB act.*, obs.{IgnoreOutput, MisreadOutput} | Invalid Invocation; Misinterpretation of Tool Output | ToolFailBench: Tool-Skip, Result-Ignore, Output-Fabrication, Unnecessary-Tool-Use |
| **MCP** (integration layer) | MODEL—TOOL·**TOOL: Mistranslation** (wrapper, middleware, marshaling); THIRD PARTY Indirect Prompt Injection when it arrives via tool content | – | Tool Definition Issues; API Issues | system.tool_execution_error | System Failure | Omi Context-Exhaustion Injection via MCP schemas |
| **permission** | Unauthorized Irreversible Action; Over-initiative | – | Authentication Errors; Environment Setup Errors ("permission problems") | TEB act.UnsafeOrForbiddenAction | Guardrails Triggered | OWASP LLM06 Excessive Agency |
| **hook** | **No dedicated edge**; harness bugs go to the nearest edge (the Harbor-Mix case) | – | – | – | – | **Gap**; candidates are Mistranslation-like (fault: harness) |
| **sandbox** (local) | LOCAL ENV—MODEL: Observation Failure, Recovery Failure (model-side) | – | Environment Setup Errors, Resource Exhaustion, Timeout Issues | system.environment_error | System Failure | SWE-agent timeouts; FaP Environment 9.4% |
| **state** | State Tracking Failure; State Staleness; Stale State Delivery (env-side) | FM-1.3 Step repetition; FM-2.1 Conversation reset | Context Handling ("state tracking") | – | – | OpenHands stuck scenarios 1–4 |
| **subagent / delegation** | MODEL—MODEL (PEER/SUBAGENT): Delegation Failure, Communication Failure; the "subagent consumed budget" rule | FM-1.2, FM-2.2, FM-2.4, FM-2.5 | Task Orchestration | (Who&When / LongRCA responsible agent) | – | Claude Code stall watchdog [S] |
| **verification** | Satisficing (stops early) | FM-3.2 No or incomplete verification; FM-3.3 Incorrect verification | – | reflection.{progress_misjudge, outcome_misinterpretation}; TEB verify.{NoVerification, WrongVerification} | – | FaP "fabricates success" in 26% of failed runs; SA Unsupported Answer |
| **artifact** (outputs, patches, files) | Satisficing ("only stubbed in"); OWASP LLM09 Misinformation ("fabricated content presented as completed work") | FM-1.1 (partial) | Formatting Errors | – | – | **Gap**; TRIM CodeSlop [S] |
| **budget** | Instruction-Following Failure ("exceeding specified API-call or token limits"); OWASP LLM10 Unbounded Consumption | – | Resource Exhaustion, Resource Abuse | system.{step_limit, llm_limit} | – | SWE-agent and mini-swe-agent cost and step limits |
| **stop logic** | Satisficing, Under-initiative | FM-1.5 Unaware of termination conditions; FM-3.1 Premature termination | – | TEB verify.PrematureTermination | – | OpenHands monologue; Aider max_reflections; FaP "gives up" |
| **environment** (external, including grader) | EXTERNAL ENV·ENV: Service Failure, Stale State Delivery; Recovery Failure (model); OWNER·OWNER Instruction-Grader Mismatch | – | Rate Limiting, Service Errors, Resource Not Found | system.environment_error | System Failure | Continual Search benchmark-defect detection |
| **human** (owner or user) | OWNER—MODEL: Instruction-Grader Mismatch (owner), Over-initiative, Under-initiative, Sycophancy | FM-2.2 Fail to ask for clarification | Incorrect Problem Identification | – | Underspecified User Intent; Intent Not Supported | – |
| **external dependency** (third party or service) | Service Failure, Stale State Delivery; THIRD PARTY: Indirect Prompt Injection, Contextual Sycophancy | – | API Issues | system.tool_execution_error | System Failure | – |

**Recommendations for our dimension.**

- Add **grader / evaluator** as its own component. Model-or-Harness and Continual Search both separate it. It is where Instruction-Grader Mismatch and benchmark defects belong.
- Add **third party** (an actor, as distinct from the external-environment channel).
- Carry Model-or-Harness's **edge plus fault-side** as two extra fields on every label. Our component is the endpoint, and the fault side says which endpoint must change.
- Existing machine-readable crosswalk to reuse: `canja006/agent-failure-registry`.

### (ii) Which datasets convert to a common trajectory format

| Dataset | Access | Step unit and index | Labels | Effort to convert |
|---|---|---|---|---|
| Who&When (184) | GitHub JSON | `history[i]`, 0-based (string) | agent, step, reason | Trivial |
| LongRCA (1,140; Mini 200) | HF JSON or Parquet | `history[i]`, 0-based | role, root step, rationale | Trivial (Who&When-compatible) |
| TrajErrBench (486, zh and en), plus converted AgentErrorBench and Who&When | GitHub (TrajDebug `data/`) | `messages[i].step == i` | critical_error_step, `<module>.<subtype>` | Already unified; reuse its converters |
| AgentErrorBench (200) | Google Drive | 1-indexed assistant turn | step, module, type, per-step annotations | Easy (TrajDebug converter exists) |
| AgentRx (115/170) | GitHub and HF | IR `steps[index].substeps[]` | all failures plus root_cause id, category, agent | Easy |
| SearchAuditBench (1,243) | GitHub zip (needs 7z for PPMd) | message index plus tolerance span | step span, 6-way cause, repair rubrics | Easy |
| Who&When Pro (12,326; text 6,257) | HF (full release pending) | framework-specific coordinates | agent, step, mode, accepted alternates | Medium (port `score.py` coordinate maps) |
| TRAIL (148) | GitHub and HF | OpenInference span tree, span_id | multi-error (category, span, impact) and trace scores | Medium (flatten the span tree; keep span ids) |
| MAST-Data (1,642) | HF | raw text, no step | trace-level 14-way multi-label | Hard for localization; usable for detection and clustering only |
| MCP-Atlas failures (OAT) | GitHub | steps | failure-contributing steps (a set) | Easy [U on format] |
| TracerTraj (AgenTracer) | GitHub release | – | agent and step | [U] |
| 2608.06909 (1,351), MegaRCA-Mix (50), FaP (1,794), TELBench (1,000) | pending, [U] or [S] | – | component and chains / RCA / taxonomy / spans | Track for release |

**Fields every dataset shares (the minimal common core):**

- `trajectory_id`;
- `task` (instruction or question);
- `outcome` (failed, or a reward);
- an ordered `steps[]` list of `{idx, actor/name, role, content}`;
- `label.critical_step`;
- `label.responsible_actor` (except single-agent sets and MAST);
- `label.category` (taxonomy-specific);
- `label.rationale`.

**Proposed record**, a superset that is OpenInference/OTel-compatible so TRAIL-style spans round-trip:

```json
{"trajectory_id":"","source":{"dataset":"","version":"","license":"","native_id":""},
 "task":{"instruction":"","gold":null},
 "outcome":{"success":false,"reward":0,"grader":{"kind":"","detail":""}},
 "actors":[{"id":"","kind":"model|tool|mcp|user|harness|subagent|peer|env|grader|third_party","name":""}],
 "steps":[{"idx":0,"parent_idx":null,"span_id":null,"actor":"","kind":"message|thought|tool_call|tool_result|handoff|compaction|memory_write|memory_read|error|system",
           "content":"","tool":{"name":"","args":{},"status":""},"ts":null,"tokens":null}],
 "labels":[{"annotator":"human|llm:<model>","critical_step":7,"accepted_steps":[7],"tolerance":[6,8],
            "responsible_actor":"","component":"<ours>","edge":"TOOL—MODEL","fault_side":"MODEL",
            "native_taxonomy":"TRAIL|MAST|AET|MoH|...","native_category":"","all_errors":[{"step":3,"category":"","impact":""}],
            "rationale":""}]}
```

**Conversion rules.**

- Store indices **0-based over our unified steps**, and keep a `native_step` field.
- Map 1-indexed assistant turns (AgentErrorBench) and framework coordinates (Who&When Pro) at ingestion.
- Keep MAST as trace-level labels with `critical_step: null`.

### (iii) Metric definitions to adopt

Let N be the number of failed trajectories, g_i the gold step, p_i the predicted step (null if parsing failed), and L_i the trajectory length.

**Failure detection, trajectory level**

- Precision, recall and F1 on the failure class, plus AUROC and AUPRC for scored detectors.
- **Recall at fixed false-positive rate** on successful runs, measured at 1%, 2% and 5%. This mirrors the Failure-as-a-Process monitor result of 82% precision at 2–3% FPR with 18.2% recall.
- **Early detection:**
  - lead time = t_alarm − g_i; negative means the alarm came before the critical step;
  - **detect-before-irrecoverable rate** = P(t_alarm ≤ g_i + w), with w=1 because the median recovery window is 1 step;
  - all reported over a fixed prefix fraction or checkpoint.
- **Step-level anomaly** (Oat-style): step AUROC and AUPRC; top-k hit rate = P(g_i ∈ top-k), with k=3.

**Localization (step distance)** — any failed or invalid prediction counts as wrong; also report coverage = valid / N.

| Metric | Definition | Source |
|---|---|---|
| Exact | (1/N) Σ 1[p_i = g_i] | Who&When, LongRCA, TrajDebug |
| ±k accuracy | (1/N) Σ 1[\|p_i − g_i\| ≤ k], k ∈ {3, 5} | ECHO, LongRCA, TrajDebug [GT−3, GT] |
| Tolerance-span accuracy | 1[p_i ∈ [lo_i, hi_i]] when the dataset provides a span or accepted set | SearchAuditor CS-Loose, Who&When Pro alternates |
| MAE (steps) | mean \|p_i − g_i\| over valid predictions, reported alongside coverage | LongRCA (its exporter pins paper MAE because failed rows lack errors) |
| Normalized distance | \|p_i − g_i\| / L_i, for length-robust cross-dataset comparison | ours |
| Signed bias | mean(p_i − g_i); negative means the detector blames too early | ours |
| Directional window | 1[g_i − k ≤ p_i ≤ g_i] | TrajDebug appendix |

- **Aggregation:** report both micro averages and the **macro average over sources or frameworks**, as Who&When Pro and TrajDebug do.

**Responsible-role (actor) accuracy**

- (1/N) Σ 1[norm(r̂_i) = norm(r_i)], using LongRCA's `normalize_role`: NFKC, casefold, whitespace collapse, strip a trailing "(→ X)".
- The role must be **predicted explicitly**, never derived from the actor of p_i.
- Exclude single-agent trajectories from the denominator (Who&When Pro).
- Average per framework.

**Component, edge and fault side (our extension)**

- Accuracy, macro-F1 and Cohen's κ against human labels, as Model-or-Harness does.
- Category = edge plus fault side; mode = category plus failure mode.
- Report the **gold-category-conditioned** mode accuracy separately.

**Category labelling**

- Single-label: macro-F1 over observed gold classes (Who&When Pro "What").
- Multi-label per trace: weighted F1 over category presence (TRAIL).
- Location-category joint accuracy = |G ∩ P| / |G| over (step, category) pairs, as in TRAIL. Because TRAIL does not penalize extras, **also report a precision-aware joint F1**.
- **Joint "All" accuracy** = actor, step and category all correct on the same trajectory.

**Abstention**

- Coverage–precision curves, including selective voting at k-of-n judges.

**Clustering quality** (for failure-signature clustering; standard definitions; none of the cited papers prescribes these)

- **External, against gold native or component labels:**
  - Adjusted Rand Index;
  - Adjusted Mutual Information;
  - V-measure (homogeneity and completeness);
  - **B-cubed precision, recall and F1** (per-item, robust to cluster-size skew);
  - purity, for interpretability.
- **Internal:** silhouette on the embedding.
- **Operational:**
  - coverage, meaning the fraction of failures in non-noise clusters;
  - **stability**, the mean pairwise ARI across bootstrap reruns;
  - **label-consistency rate**, the fraction of clusters whose majority component covers at least 80% of members.

**Reliability and uncertainty, for every reported number**

- Wilson 95% confidence intervals for rates and bootstrap intervals for F1 and MAE (as in Holdfast/COMPINT and decay-pin).
- Cohen's κ (pairwise) or Fleiss' κ (more than 2 annotators) for gold-label agreement.
- Reference agreement levels: TrajErrBench step κ 0.91 / 0.674; AgentErrorBench κ 0.55; MAST κ 0.88.

**Compaction and constraint metrics, for the compactor and stop-logic components**

- Retention, compliance under the four conditions, and Effect Retention (LiC equations 6, 8 and 9). Never clip ER; flag a degenerate denominator.
- Violation rate under deterministic tool-call grading (ConstraintRot).
- Safe Turn Depth and Safe Token Budget (Omi).

---

**Main local files** (scratchpad repos at `/tmp/claude-0/-home-user-Tracelyt/759a35a9-2e36-5f3a-a868-84fb22c157ad/scratchpad/repos/`):

- `anghel4d_broadside-observer/sources/02-model-or-harness.txt` (full 2607.28802 text)
- `stagnation/research/docs/_raw/` (MAST v3, TRAIL v3, AgentDebug v1 HTML text)
- `trail-benchmark/`, `MAST/`, `AgentDebug/`, `Agents_Failure_Attribution/`, `ag2ai_whowhen_pro/`, `microsoft_AgentRx/`, `THU-KEG_TrajDebug/` (includes `trajdebug.txt`), `lzzzx666_SearchAuditor/`, `deeplearning-wisc_OAT/`, `longrca-bench_longrca-bench.github.io/`, `software-agent-sdk/`, `sweagent/`, `aider_clone/`, `miniswe/`
- `Awesome-LLM-Agent-Trajectory-Analysis/survey.txt`
- `../notes/cr_2608.11242.md` (Lost in Compaction full text) and `../stuck_legacy.py`
