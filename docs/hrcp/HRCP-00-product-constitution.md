# Harness Reliability Control Plane

## Product Constitution & Master Source of Truth

**Document ID:** HRCP-00\
**Version:** 0.1\
**Status:** Working Source of Truth\
**Date:** 30 September 2026\
**Owner:** Founding Team\
**Applies To:** Product thesis, scope, strategic decisions, product boundaries, differentiation, open-source strategy, commercial strategy, ICP, long-term vision

---

# 1. Purpose of This Document

This document defines the canonical product vision for the company we are exploring around agent/harness observability, reliability, replay, verification, and runtime control.

It exists to prevent architectural drift.

Any future product requirement, engineering decision, research project, hiring decision, commercial decision, or technical specification should be consistent with this document unless this document is deliberately amended.

This document is not intended to contain every implementation detail. Those belong in the technical specifications referenced later.

The complete source-of-truth system is:

```text
HRCP-00  Product Constitution & Master Strategy
HRCP-01  Technical Architecture & Execution Model
HRCP-02  Build, Validation, Security & Commercialization Plan

Future specifications:

HRCP-03  Harness Telemetry & Execution Graph Specification
HRCP-04  Replay, Simulation & Regression Specification
HRCP-05  Reliability Intelligence & Failure Taxonomy
HRCP-06  Runtime Control, Policy & Intervention Specification
HRCP-07  Security, Privacy & Enterprise Deployment Specification
HRCP-08  SDK, Framework & Integration Specification
HRCP-09  Benchmark & Evaluation Specification
HRCP-10  Open-Source Governance & Ecosystem Specification
```

The first three documents establish the system. The future documents should be derived from them.

---

# 2. Decision Classification

Every important statement should use one of the following classifications.

### DECIDED

A decision we currently intend to build around.

Changing a DECIDED item should require an explicit architectural decision.

### PROPOSED

The current preferred direction, but not yet sufficiently validated to freeze.

### OPEN

An unresolved question requiring experimentation, customer evidence, benchmarking, or further research.

This classification is mandatory.

We must not accidentally turn hypotheses into permanent architecture.

---

# 3. Executive Thesis

**DECIDED**

The company should not be another LLM observability platform.

The commodity layer of AI observability increasingly includes:

- prompt logging;
- model request tracing;
- token tracking;
- latency dashboards;
- cost dashboards;
- ordinary span visualization;
- generic LLM-as-a-judge evaluation;
- prompt experimentation;
- trace storage.

Those capabilities are necessary but insufficient.

The opportunity we are pursuing is:

> **Reliability infrastructure for autonomous agents and their harnesses.**

The core thesis is:

> Agents do not merely need monitoring of model calls. They need infrastructure capable of understanding, reconstructing, diagnosing, replaying, verifying, and eventually controlling the entire execution environment surrounding the model.

The unit of analysis therefore evolves from:

```text
LLM call
   ↓
trace
   ↓
agent trajectory
   ↓
harness execution graph
```

Our platform should ultimately understand the complete execution graph.

---

# 4. Category Definition

**DECIDED**

Working category:

# Harness Reliability Control Plane

Alternative market-facing description:

# Agent Reliability Infrastructure

We should avoid describing ourselves primarily as:

- LLM observability;
- tracing;
- prompt monitoring;
- AI analytics;
- generic evaluation tooling.

These can be product capabilities but should not define the company.

---

# 5. Fundamental Product Question

Traditional AI observability asks:

> What happened during this model or agent run?

Our product should answer:

> What happened?

> Where did the execution first diverge?

> Which harness component was responsible?

> What state, context, policy, tool, model, memory, permission, or environment contributed?

> Why did the existing verification system fail to prevent it?

> Can the failure be reproduced?

> What change would likely prevent it?

> Does that change fix historical failures?

> Does that change introduce new regressions?

> Is the proposed change safe enough to deploy?

> Should the system automatically intervene if the pattern appears again?

---

# 6. The System We Want to Understand

The model is only one component.

A production agent may contain:

```text
Model
│
├── Agent Loop
├── Planner
├── Context Builder
├── Context Compressor
├── Memory
├── Retrieval
├── Skills
├── Tool Registry
├── MCP Servers
├── Permissions
├── Hooks
├── Sandbox
├── State Machine
├── Subagents
├── Delegation
├── Human Approval
├── Verification
├── Artifact Management
├── Budget Controller
├── Stop Logic
└── Runtime Environment
```

The reliability platform must be able to observe the interaction between these components.

---

# 7. Core Product Principle

**DECIDED**

The product is not fundamentally a trace viewer.

The product is an:

# Execution Understanding System

Tracing is the raw substrate.

The higher-value layers are:

```text
Capture
   ↓
Normalize
   ↓
Reconstruct
   ↓
Detect
   ↓
Correlate
   ↓
Diagnose
   ↓
Replay
   ↓
Verify
   ↓
Recommend
   ↓
Control
```

---

# 8. Product Evolution

The industry can be conceptualized as four generations.

```text
GENERATION 1 — LOGGING
"What happened?"

        ↓

GENERATION 2 — OBSERVABILITY
"Where did it happen?"

        ↓

GENERATION 3 — ACTIVE OBSERVABILITY
"Why did it happen?"

        ↓

GENERATION 4 — RELIABILITY CONTROL
"Can we reproduce, prevent, repair or stop it?"
```

**DECIDED**

We should architect for Generation 4 from the beginning.

The MVP will not implement all Generation 4 capabilities, but the underlying data model must not prevent them.

---

# 9. Product Layers

The target platform consists of seven primary layers.

```text
┌─────────────────────────────────────┐
│ 7. RELIABILITY CONTROL PLANE        │
├─────────────────────────────────────┤
│ 6. REGRESSION & VERIFICATION        │
├─────────────────────────────────────┤
│ 5. REPLAY & SIMULATION              │
├─────────────────────────────────────┤
│ 4. RELIABILITY INTELLIGENCE         │
├─────────────────────────────────────┤
│ 3. EXECUTION / CAUSAL GRAPH         │
├─────────────────────────────────────┤
│ 2. HARNESS SEMANTIC MODEL           │
├─────────────────────────────────────┤
│ 1. TELEMETRY / EVENT CAPTURE        │
└─────────────────────────────────────┘
```

---

# 10. Layer 1 — Telemetry / Event Capture

The platform must collect execution data from agent systems.

Possible sources include:

- OpenTelemetry;
- OpenInference;
- direct SDK instrumentation;
- framework adapters;
- model providers;
- MCP;
- tool calls;
- agent frameworks;
- runtime hooks;
- containers;
- sandboxes;
- CI systems;
- source-control systems;
- permission systems;
- human approval interfaces.

**DECIDED**

We should not invent a completely proprietary telemetry transport.

We should build on OpenTelemetry.

**DECIDED**

OpenInference compatibility should be supported.

**DECIDED**

Customers must not be forced to send model traffic through our gateway.

A mandatory proxy creates unnecessary adoption friction and infrastructure risk.

**PROPOSED**

Gateway integration should exist as an optional capture mechanism.

---

# 11. Layer 2 — Harness Semantic Model

Raw spans do not contain sufficient semantic meaning.

For example:

```text
span.name = execute_tool
```

does not tell us whether:

- the planner chose the tool;
- the model hallucinated the tool;
- a permission service approved it;
- a hook transformed its arguments;
- the sandbox rejected it;
- verification later invalidated the result.

Therefore we require a domain-specific semantic layer.

Working name:

# Harness Event Model — HEM

**PROPOSED NAME**

The model should represent events such as:

```text
harness.run
harness.iteration

harness.plan
harness.model

harness.context.build
harness.context.read
harness.context.write
harness.context.compact

harness.memory.read
harness.memory.write

harness.tool.request
harness.tool.execution
harness.tool.result

harness.mcp.request
harness.mcp.response

harness.hook
harness.permission
harness.policy

harness.sandbox

harness.state.read
harness.state.transition

harness.subagent.spawn
harness.subagent.handoff
harness.subagent.return

harness.human.approval

harness.verify
harness.gate

harness.artifact.read
harness.artifact.write
harness.artifact.diff

harness.retry
harness.recovery

harness.budget

harness.stop
```

This list will be expanded in HRCP-03.

---

# 12. Layer 3 — Harness Execution Graph

**DECIDED**

A conventional parent-child trace tree is insufficient.

Agent execution contains relationships that may span large portions of a trajectory.

Example:

```text
MemoryWrite @ Step 12
       │
       │ influences
       ↓
MemoryRead @ Step 184
       │
       ↓
ContextBuild
       │
       ↓
Plan
       │
       ↓
ToolSelection
       │
       ↓
Failure
```

Therefore our internal representation should support a graph.

Working name:

# Harness Execution Graph — HEG

**PROPOSED NAME**

Relationship types should include:

```text
parent_of
caused_by
influenced_by

reads_from
writes_to

derived_from
compacted_from
retrieved_from

requested_by
approved_by
blocked_by

delegated_to
returned_to

verified_by
invalidated_by

depends_on

supersedes

mutates
produces

replayed_from

regression_of
```

The graph must preserve provenance.

---

# 13. Layer 4 — Reliability Intelligence

The intelligence layer transforms raw execution telemetry into useful findings.

It should include:

### Deterministic detectors

Examples:

- infinite loops;
- repeated identical tool calls;
- no-progress loops;
- excessive retries;
- repeated retrieval;
- context explosion;
- budget exhaustion;
- repeated permission failure;
- verification bypass;
- repeated invalid tool arguments;
- artifact rewrite loops.

### Statistical detectors

Examples:

- behavior drift;
- failure-rate shift;
- latency change;
- cost regression;
- unusual tool distribution;
- unusual model usage;
- trajectory-length anomalies.

### Specialized classifiers

Examples:

- context-loss detector;
- tool misuse detector;
- verification weakness classifier;
- loop classifier;
- root-component classifier;
- suspicious permission chain classifier.

### Frontier-model reasoning

Used selectively for:

- difficult investigations;
- summarizing incidents;
- proposing root-cause hypotheses;
- explaining unusual trajectories;
- generating possible fixes.

**DECIDED**

We should use the cheapest adequate intelligence layer.

The hierarchy should normally be:

```text
deterministic rules
        ↓
statistics
        ↓
small specialized models
        ↓
larger specialized models
        ↓
frontier reasoning model
        ↓
human investigation
```

We should not run expensive frontier models over every raw trace.

---

# 14. Incident-Centric Product Model

**DECIDED**

The primary production UI should eventually be incident-first rather than trace-first.

Bad starting point:

```text
8,421,294 traces
```

Better starting point:

```text
INCIDENT HR-491

Started:
14:32 UTC

Affected:
18,419 executions

Primary symptom:
Budget exhaustion

First common divergence:
context.compact

Likely component:
Context management

Correlated change:
compressor v14 → v15

Observed mechanism:
account_region removed
→ planner chooses fallback tool
→ tool failure
→ repeated retry
→ token budget exhausted

Estimated wasted cost:
$X

Potential remediation:
pin account_region during compaction

Replay status:
3,214 historical failures tested

Regression status:
No significant regression detected
```

Individual traces remain accessible underneath the incident.

---

# 15. First-Divergence Analysis

**DECIDED PRODUCT DIRECTION**

One of the important differentiators should be trajectory comparison.

Example:

Successful cohort:

```text
retrieve
   ↓
plan
   ↓
tool-A
   ↓
verify
   ↓
finish
```

Failure cohort:

```text
retrieve
   ↓
plan
   ↓
tool-B     ← first meaningful divergence
   ↓
retry
   ↓
retry
   ↓
budget exhausted
```

The system should compare:

- successful runs;
- failed runs;
- previous versions;
- current versions;
- different models;
- different prompts;
- different harness versions;
- different tool versions;
- different policies;
- different context strategies.

The goal is not merely correlation.

The goal is to produce an evidence-backed root-cause hypothesis.

---

# 16. Important Terminology Rule

**DECIDED**

We should distinguish:

### Observed causal link

A deterministic relationship captured by the system.

Example:

```text
permission decision X directly blocked tool invocation Y
```

### Statistical association

Example:

```text
failure rate is significantly higher after compressor version 8
```

### Causal hypothesis

Example:

```text
compressor version 8 likely caused the increase because it removes region state
```

The product must not present statistical correlation as proven causation.

---

# 17. Layer 5 — Replay

Replay is a foundational capability.

Traditional replay may simply reuse previously recorded model outputs.

That is useful but incomplete.

Our target should be:

# Branch-Aware Replay

Example:

Original trajectory:

```text
A → B → C → D
```

Modified harness:

```text
A → B' → X
```

At `X`, no recorded response exists.

The replay system therefore needs to:

```text
Recorded event available?
        │
   ┌────┴────┐
   │         │
  YES        NO
   │         │
Replay     Controlled live branch
fixture       execution
              │
              ↓
        Capture new branch
```

Replay may involve snapshots of:

- prompts;
- model outputs;
- tool results;
- MCP responses;
- environment variables;
- filesystem state;
- code revision;
- database fixture;
- context;
- memory;
- permissions;
- policies;
- models;
- dependency versions;
- sandbox configuration;
- network responses.

This is expected to be technically difficult.

That difficulty is desirable if the capability creates meaningful reliability value.

---

# 18. Layer 6 — Regression & Verification

A failure should not disappear after debugging.

**DECIDED**

Production failures should be convertible into permanent regression cases.

The loop should become:

```text
Production Failure
       ↓
Incident
       ↓
Diagnosis
       ↓
Replay Case
       ↓
Proposed Fix
       ↓
Historical Regression Suite
       ↓
Validation
       ↓
Deployment
       ↓
Production Monitoring
```

This creates a reliability ratchet.

Every important incident should ideally make future versions harder to break in the same way.

---

# 19. Verification Must Carry Evidence

A verification result should not simply be:

```text
passed = true
```

It should support:

```text
Claim
│
├── Evidence
├── Evaluator
├── Policy
├── Threshold
├── Environment
├── Version
└── Decision
```

Example:

```text
claim:
"implementation complete"

evidence:
- pytest run 132
- 178/178 tests passed
- build passed
- lint passed
- integration suite passed

verification policy:
release-policy-v7

result:
ACCEPT
```

This gives us provenance for autonomous decisions.

---

# 20. Layer 7 — Runtime Reliability Control Plane

The long-term system should eventually move beyond observation.

Possible actions include:

```text
stop runaway agent
pause execution
request human approval

disable tool
disable MCP server

switch model

increase verification requirement

reduce permissions

restore previous policy

rollback harness configuration

quarantine memory entry

force sandbox mode

increase budget

decrease budget

redirect to fallback agent

re-run verification
```

**DECIDED**

Runtime intervention should not be part of the earliest MVP.

**DECIDED**

High-impact interventions require explicit policy and auditability.

**DECIDED**

Human approval should remain available for high-risk interventions.

---

# 21. Context Runtime Observability

This is one of the areas where generic observability remains weak.

The system should treat context operations as runtime events.

Examples:

```text
retain
drop
summarize
compress
retrieve
offload
pin
load memory
load skill
share with subagent
```

Potential findings:

```text
Failure probability rises sharply when compaction occurs
before iteration 12.

Subagent B receives the artifact but not the decision rationale.

42,000 tokens are repeatedly reread because tool output
was never externalized.

A required state field disappears during summarization.
```

Working subcategory:

# Context Runtime Intelligence

This is strategically important because context management is increasingly part of harness behavior.

---

# 22. Memory Provenance

The system should be able to reconstruct:

```text
which memory was read?
who wrote it?
when?
under which agent?
from which source?
which later decisions used it?
was it modified?
was it invalidated?
```

A memory operation should not be treated as an opaque generic tool call.

---

# 23. Agent Identity and Delegation

The system should understand:

```text
Agent A
   ↓ delegates
Agent B
   ↓ requests
Tool
   ↓ uses
Credential
   ↓ modifies
External System
```

Questions should eventually include:

```text
Which agent initiated the action?

Was the action delegated?

Which identity executed it?

Which permission allowed it?

Which credential was exercised?

What changed?

What verification subsequently accepted the change?
```

---

# 24. MCP and Tool Provenance

MCP/tool activity should record:

- server;
- tool;
- tool version;
- request;
- normalized parameters;
- permission decision;
- credential identity where permissible;
- execution environment;
- result;
- mutations;
- downstream consumers;
- verification result.

The product should integrate with MCP ecosystems.

It should not become a generic MCP marketplace or generic MCP gateway.

---

# 25. Artifact Awareness

An autonomous agent frequently changes something tangible.

Examples:

- code;
- document;
- spreadsheet;
- configuration;
- database record;
- ticket;
- CRM object;
- infrastructure resource.

The platform should eventually understand:

```text
before state
   ↓
agent operation
   ↓
after state
   ↓
verification evidence
```

Artifact mutations should therefore be first-class graph entities.

---

# 26. Economics Layer

Traditional observability metrics are insufficient.

We should support:

```text
cost / run
cost / successful run
cost / verified successful run

tokens / successful run

latency / successful run

retry cost
failed-tool cost
loop waste

context reread waste

verification cost

subagent cost

human intervention cost

recovery rate

success / dollar
success / minute
```

**DECIDED**

Success-adjusted economics should become a product differentiator.

---

# 27. Harness Comparison

The system should support experiments such as:

```text
same task
same dataset
same model

Harness A
vs.
Harness B
```

Comparison dimensions:

- task success;
- verified success;
- cost;
- latency;
- retries;
- tool failures;
- trajectory length;
- human intervention;
- context usage;
- verification behavior;
- failure distribution.

The product should compare Pareto frontiers rather than forcing everything into one arbitrary score.

---

# 28. Product Surfaces

Long-term product surfaces may include:

### Incident Center

What is currently failing and why?

### Run Explorer

Detailed inspection of one execution.

### Execution Graph

Causal/provenance-oriented run visualization.

### Fleet Analytics

Aggregate behavior across agents and versions.

### Context Explorer

Context construction, compaction, retrieval, and memory lineage.

### Replay Lab

Reproduce and branch from historical executions.

### Regression Workbench

Test changes against historical failures.

### Harness Compare

Compare runtime configurations and harness versions.

### Economics

Success-adjusted cost and resource efficiency.

### Policy & Control

Define intervention policies and approval requirements.

### Security / Audit

Identity, tool usage, permissions, sensitive actions, provenance.

---

# 29. Initial Wedge

**PROPOSED**

Coding agents are currently the preferred technical wedge.

Reasons:

- long-running trajectories;
- tool-heavy behavior;
- shell/filesystem usage;
- git state;
- clear artifacts;
- frequent verification;
- objective success signals;
- context compaction;
- retries;
- subagents;
- sandboxing;
- permission systems;
- measurable regressions.

Objective verification examples include:

```text
tests pass
build succeeds
benchmark improves
lint succeeds
PR applies cleanly
artifact exists
```

This environment gives us unusually rich reliability signals.

---

# 30. Secondary Markets

Potential future markets:

- enterprise workflow agents;
- AI-native BPO;
- DevOps/SRE agents;
- financial workflow agents;
- research agents;
- browser/computer-use agents;
- customer-support agents performing actions;
- autonomous back-office agents.

We should initially prioritize agents where failure is expensive and trajectories are complex.

---

# 31. Non-Ideal Early Customer

We should not optimize the initial product around:

```text
user question
    ↓
RAG
    ↓
single model answer
```

Simple short-lived chatbots already have mature observability tooling.

Our strongest value appears as agent complexity increases.

---

# 32. Ideal Customer Profile

Good design partners should ideally have systems that meet several of these conditions:

```text
run > 5 minutes

use > 5 tools

maintain persistent state

spawn subagents

mutate real systems

contain verification gates

have meaningful cost per failed run

have human escalation

operate at production volume

have repeated task classes
```

---

# 33. Primary Users

Potential users include:

### Agent Infrastructure Engineer

Needs to understand why agent systems fail.

### AI Platform Engineer

Needs organization-wide visibility and policy.

### Agent Product Engineer

Needs reliable experimentation and regression testing.

### SRE / Production Engineer

Needs incident detection and production debugging.

### Security Engineer

Needs identity, permission, and action provenance.

### Engineering Manager

Needs reliability and economics.

### Enterprise Risk / Audit

Needs evidence for autonomous actions.

---

# 34. Core User Jobs

### Job 1

Find why agent success rate dropped after a release.

### Job 2

Understand why one cohort behaves differently from another.

### Job 3

Determine which component first diverged.

### Job 4

Reproduce a historical failure.

### Job 5

Test a fix against previous incidents.

### Job 6

Detect new failure patterns automatically.

### Job 7

Understand runaway costs.

### Job 8

Determine why the harness allowed an unsafe action.

### Job 9

Understand agent/context/memory/tool provenance.

### Job 10

Stop or contain dangerous runtime behavior.

---

# 35. Open-Source Strategy

**DECIDED DIRECTION**

We should strongly consider an open-core strategy.

The open layer should reduce instrumentation friction and help establish our semantic model as an ecosystem standard.

Candidate open components:

```text
Harness Event Model
OTel semantic conventions

SDK

collector

framework integrations

local recorder

local/basic trace explorer

event validators

development CLI
```

Commercial layer candidates:

```text
large-scale managed storage

incident intelligence

fleet analysis

first-divergence analysis

failure clustering

specialized reliability models

branch-aware replay infrastructure

regression infrastructure

automated investigations

enterprise policy

runtime controls

security analysis

cross-team collaboration

enterprise deployment

retention/governance

advanced economics
```

---

# 36. Why Open Source

The purpose is not charity.

Strategic objectives include:

- easier adoption;
- standard creation;
- framework neutrality;
- community integrations;
- trust;
- self-hosted experimentation;
- ecosystem distribution;
- reduced vendor-lock-in objections;
- telemetry portability.

If the market standardizes around our semantics, that is strategically useful even when the schema itself is open.

---

# 37. What Must Remain Proprietary Enough to Monetize

Our moat cannot be:

```text
we know how to store spans
```

Potential compounding assets are:

### Failure corpus

```text
execution
+
failure
+
first divergence
+
root component
+
intervention
+
outcome
```

### Reliability models

Specialized models for identifying agent/harness failures.

### Replay infrastructure

Especially cross-version branch-aware replay.

### Incident intelligence

Mapping large populations of runs into actionable failures.

### Historical regression intelligence

Knowing which changes fix one class of issue while creating another.

### Cross-system execution graph

Understanding interaction among context, tools, permissions, agents, memory, environment, and verification.

---

# 38. Data Flywheel

Long-term:

```text
Production Runs
      ↓
Failure Detection
      ↓
Incident Clustering
      ↓
Investigation
      ↓
Root-Cause Hypothesis
      ↓
Fix
      ↓
Replay
      ↓
Regression
      ↓
Production Outcome
      ↓
Validated Reliability Data
      ↓
Better Detectors / Models
```

The most valuable dataset is not:

```text
prompt → answer
```

It is closer to:

```text
execution graph
+
harness configuration
+
failure
+
root cause
+
remediation
+
verified result
```

---

# 39. Model Strategy

**DECIDED**

Do not depend on frontier LLM calls for routine observability.

Preferred architecture:

```text
Algorithms
   ↓
Rules
   ↓
Statistics
   ↓
Small classifiers
   ↓
Specialized reasoning models
   ↓
Frontier model
```

Specialized models may eventually include:

```text
loop detector
no-progress classifier

tool-misuse classifier

context-loss classifier

verification-failure classifier

root-component classifier

first-divergence ranker

incident similarity model

permission anomaly model
```

---

# 40. Framework Strategy

**DECIDED**

The product should remain framework-independent.

Integrations should eventually cover major agent ecosystems without requiring customers to rewrite their application around us.

Possible integrations include:

- OpenAI agent tooling;
- Anthropic agent tooling;
- LangGraph;
- PydanticAI;
- CrewAI;
- AutoGen;
- MCP;
- custom internal agent frameworks;
- coding agents;
- generic OTel emitters.

No one framework should control the core data model.

---

# 41. Infrastructure Strategy

**DECIDED**

Build above standards wherever possible.

Use:

```text
OpenTelemetry
+
OpenInference compatibility
+
our harness semantics
```

Do not recreate transport, collectors, propagation, or distributed-tracing fundamentals without a strong reason.

---

# 42. Gateway Strategy

**DECIDED**

Do not begin by building a model gateway as the central product.

Reasons:

- crowded category;
- customer adoption friction;
- critical-path infrastructure responsibility;
- gateway capability is increasingly commoditized;
- it distracts from the reliability layer.

Integrate with existing gateways instead.

Optional gateway functionality may be reconsidered when runtime intervention requires it.

---

# 43. Product Boundary: Memory

We should understand memory operations.

We should not initially build a generic memory platform.

Our responsibility is:

```text
observe memory
trace provenance
measure consequences
diagnose memory-induced failures
```

not:

```text
become the universal memory database
```

---

# 44. Product Boundary: Document Intelligence

The product may observe document and artifact operations.

It should remain separate from the Canonical Document Graph / verifiable enterprise state infrastructure effort.

The two systems may eventually interoperate.

This reliability platform should not become a generic parser or document transformation engine.

---

# 45. Product Boundary: Agent Identity

We need identity awareness and provenance.

We do not initially need to become a full enterprise IAM replacement.

Integrate with existing identity systems.

---

# 46. Product Boundary: MCP

We should deeply understand MCP execution.

We do not need to become a generic MCP marketplace or MCP gateway.

---

# 47. Product Boundary: BPO

AI-native BPO may become a customer/application layer.

We should not initially become the BPO operator.

We build infrastructure that makes such systems reliable.

---

# 48. Product Boundary: Evaluation

Evaluation is required.

We should not become merely another generic evaluation platform.

Evaluations are an input to reliability.

The differentiated workflow is:

```text
failure
→ diagnosis
→ reproduction
→ proposed remediation
→ regression
→ control
```

---

# 49. Product Boundary: Prompt Management

Prompt versioning may be integrated or represented as metadata.

We should not prioritize building a generic prompt CMS.

---

# 50. Competitive Positioning

We must assume excellent existing platforms already provide:

- traces;
- evaluations;
- dashboards;
- prompt management;
- agent/session views;
- failure clustering;
- AI-assisted investigation;
- some replay;
- some automated repair;
- some guardrails.

Therefore differentiation must exist below and beyond those features.

Our target differentiation is:

```text
whole-harness semantics

execution graphs

context/state provenance

verification evidence

first-divergence analysis

component-level failure attribution

branch-aware replay

historical regression

success-adjusted economics

policy-backed runtime intervention
```

---

# 51. Strategic Rule

**DECIDED**

We will not copy a competitor's feature checklist and call that differentiation.

Every major product feature should answer at least one of:

```text
Does this help us understand the harness?

Does this identify failure earlier?

Does this improve attribution?

Does this improve reproducibility?

Does this prevent recurrence?

Does this make autonomy safer?

Does this make agent economics measurable?
```

---

# 52. Incident Intelligence Example

Target output:

```text
INCIDENT HR-521

Affected executions:
14,282

Primary outcome:
budget exhausted

First divergence:
context.compact @ iteration 11

Responsible component:
Context Management

Correlated deployment:
compressor v14 → v15

Evidence:
93% of affected executions lose `account_region`
before planning.

Downstream chain:

context compaction
   ↓
missing account_region
   ↓
incorrect tool chosen
   ↓
tool rejects request
   ↓
retry
   ↓
retry
   ↓
budget exhaustion

Proposed remediation:
pin account_region state during compaction

Replay:
3,412 historical failure trajectories

Outcome:
+11.7 percentage points verified success

Cost impact:
+1.3% median tokens

Regression:
No detected increase in benchmark failures
```

This illustrates the product level we should target.

---

# 53. Customer Value

The product should reduce:

- mean time to understand agent failures;
- mean time to reproduce failures;
- repeat incidents;
- unnecessary model spend;
- runaway trajectories;
- unsafe autonomous actions;
- human trace-reading labor;
- unreliable releases.

The product should increase:

- verified success rate;
- agent reliability;
- reproducibility;
- deployment confidence;
- auditability;
- autonomous task completion;
- engineering velocity.

---

# 54. Success Metrics

Potential company/product metrics:

```text
MTTD — Mean Time to Detect

MTTI — Mean Time to Investigate

MTTRp — Mean Time to Reproduce

MTTFx — Mean Time to Fix

Repeat Incident Rate

Verified Success Rate

Cost per Verified Success

Automated Root-Cause Precision

Replay Reproduction Rate

Regression Catch Rate

False Positive Incident Rate

Human Investigation Minutes Saved

Unsafe Action Prevention Rate
```

Not every metric belongs in customer-facing UI.

---

# 55. Product SLO Philosophy

**PROPOSED**

The platform itself should have stricter reliability expectations than ordinary analytics because customers may eventually use it for runtime intervention.

Separate:

```text
analytics path
```

from:

```text
control path
```

A temporary dashboard outage must not break the customer's agent.

Any runtime control mechanism should fail according to explicit customer-selected policy:

```text
fail-open
fail-closed
degrade-to-human
```

depending on the action's risk.

---

# 56. Privacy Principle

**DECIDED**

Telemetry may contain highly sensitive information.

The system must assume:

- PII;
- credentials;
- proprietary code;
- confidential documents;
- customer records;
- financial data;
- security information

may appear inside traces.

Therefore privacy cannot be added later.

---

# 57. Data Minimization

Customers should eventually be able to configure capture modes such as:

```text
full

metadata-only

redacted

hashed

sampled

customer-side encrypted

customer-retained payload
```

Sensitive payload storage should be separable from structural telemetry where possible.

---

# 58. Training Data Principle

**DECIDED**

Customer telemetry must not silently become shared model-training data.

Any cross-customer learning mechanism requires explicit policy and legal design.

Enterprise customers should have a clear opt-out/default-isolation model.

---

# 59. Deployment Models

Long-term possibilities:

```text
Managed SaaS

Hybrid
collector + sensitive payload customer-side

Private cloud

Self-hosted enterprise
```

**PROPOSED**

Open-source local usage plus managed commercial SaaS is the likely starting combination.

---

# 60. Business Model

Do not price only by span count.

Long-running agents may naturally create enormous trace volumes.

Potential pricing components:

```text
platform subscription

telemetry retention

analyzed runs

active incidents

replay compute

regression compute

enterprise controls

security/governance

support
```

Long-term value metrics may move closer to:

```text
verified autonomous work
```

rather than raw telemetry volume.

Pricing remains **OPEN**.

---

# 61. Go-To-Market Motion

Initial motion should likely be engineering-led.

Potential sequence:

```text
Open-source telemetry specification
       ↓
Developer SDK / Flight Recorder
       ↓
Design Partners
       ↓
Reliability Intelligence
       ↓
Replay / Regression
       ↓
Enterprise Control Plane
```

This creates adoption before demanding a large commercial commitment.

---

# 62. Open-Source Product Wedge

Working concept:

# Harness Flight Recorder

A developer installs instrumentation and receives:

```text
complete run reconstruction

loop iterations

model calls

tool calls

context events

memory events

permissions

verification

state mutations

stop reasons
```

This should deliver obvious value even before the commercial intelligence platform is enabled.

---

# 63. Flight Recorder Philosophy

A flight recorder should answer:

```text
What exactly happened?
```

Reliability Intelligence should answer:

```text
Why does it matter?
```

Replay should answer:

```text
Can we reproduce it?
```

Regression should answer:

```text
Did the fix work safely?
```

Control should answer:

```text
What should happen next time?
```

---

# 64. UI Principle

**DECIDED**

We should not assume a trace waterfall is the optimal interface for long-running agents.

Different interfaces may be required for:

- timeline;
- trajectory;
- state transitions;
- graph dependencies;
- context evolution;
- subagent tree;
- artifact history;
- incident cohort;
- replay branches.

---

# 65. API-First Principle

**DECIDED**

Core reliability functions should be available programmatically.

The product cannot become UI-only.

Agents and CI systems should eventually be able to ask:

```text
get incident

compare runs

replay trajectory

run regression suite

query provenance

evaluate policy

request intervention
```

---

# 66. Evidence-First Principle

Every automated diagnosis should ideally provide evidence.

Avoid:

```text
AI thinks the tool failed.
```

Prefer:

```text
Likely root component:
Tool selection

Evidence:

• 87% of affected failures diverged at tool selection.
• Successful cohort chose `search_customer`.
• Failed cohort chose `search_global`.
• `customer_region` was absent in failed contexts.
• Absence started after compressor version 15.
```

---

# 67. Explainability Principle

If the system recommends:

```text
disable tool X
```

it should show:

- why;
- which evidence;
- affected population;
- expected impact;
- uncertainty;
- previous similar incidents;
- rollback strategy.

---

# 68. Control Safety Principle

Runtime control should be policy-driven.

Example:

```text
IF
tool = delete_database
AND
agent.identity != authorized_admin
THEN
deny
AND
create incident
```

More probabilistic interventions should generally have stronger human-control requirements.

---

# 69. Version Everything

Every run should be capable of referencing relevant versions:

```text
agent version

harness version

prompt version

model

model configuration

tool schema

MCP server

skill version

memory state

context strategy

policy version

verification policy

runtime image

code commit

dataset

environment
```

Without versioning, meaningful regression analysis becomes unreliable.

---

# 70. Immutable Raw Evidence

**DECIDED PRINCIPLE**

Raw captured events should be treated as immutable evidence whenever practical.

Derived interpretations can change.

Example:

```text
RAW EVENT
immutable

↓

NORMALIZED EVENT
versioned

↓

INCIDENT
versioned

↓

ROOT-CAUSE HYPOTHESIS
versioned

↓

FIX RECOMMENDATION
versioned
```

This prevents changing intelligence models from rewriting historical reality.

---

# 71. Derived Views Must Be Rebuildable

If we improve:

- normalization;
- graph construction;
- incident clustering;
- classifiers

we should ideally be able to recompute derived representations from retained evidence.

---

# 72. Reliability Taxonomy

The platform will require a formal failure taxonomy.

Candidate top-level classes:

```text
MODEL

PLANNING

CONTEXT

MEMORY

RETRIEVAL

TOOL

MCP

PERMISSION

POLICY

HOOK

SANDBOX

STATE

DELEGATION

SUBAGENT

VERIFICATION

ARTIFACT

ENVIRONMENT

BUDGET

STOPPING

HUMAN

EXTERNAL DEPENDENCY

UNKNOWN
```

This taxonomy is **PROPOSED** and requires dedicated specification.

---

# 73. Failure vs Symptom

Important distinction:

```text
SYMPTOM:
Budget exhausted

CAUSE:
Context loss caused repeated wrong-tool selection
```

The platform must not confuse downstream outcomes with root components.

---

# 74. Reliability Confidence

Automated findings should carry confidence/evidence levels.

Example:

```text
Observed
High-confidence hypothesis
Medium-confidence hypothesis
Weak correlation
Unknown
```

This is preferable to pretending every AI-generated explanation is correct.

---

# 75. Human Role

Human operators remain important.

The platform should help humans investigate less—not remove humans from all consequential decisions.

Long-term autonomy may increase as evidence quality improves.

---

# 76. Broader Platform Relationship

There is a larger architecture connecting:

```text
Agent Identity
     │
Context / Memory
     │
Harness
     │
MCP / Tools
     │
Observability
     │
Execution Graph
     │
Provenance
     │
Verification
     │
Reliability Control
```

These may eventually participate in a larger agent infrastructure platform.

**DECIDED**

We should not prematurely merge them into one product.

Each layer should have a clear contract.

---

# 77. Main Strategic Moats

Potential moats:

1. Harness execution ontology.
2. High-quality integrations.
3. Historical failure corpus.
4. Specialized reliability models.
5. Branch-aware replay.
6. Execution-graph intelligence.
7. Regression corpus.
8. Enterprise trust.
9. Runtime-policy integration.
10. Developer ecosystem.

---

# 78. Things That Are Not Moats

We must not fool ourselves into treating these as deep moats:

```text
ClickHouse cluster

basic tracing

token dashboard

simple LLM judge

prompt versioning

generic agent timeline

API gateway

generic vector search

basic alerting

pretty trace UI
```

All may be useful.

None alone justifies the company.

---

# 79. Major Competitive Threats

We should continuously watch:

- LangSmith;
- Arize;
- Braintrust;
- HoneyHive;
- Respan;
- Datadog;
- Galileo;
- Laminar;
- Langfuse;
- OpenLIT;
- Phoenix/OpenInference;
- Portkey;
- other emerging agent reliability systems.

Competitor monitoring should focus on architecture rather than feature marketing.

---

# 80. Competitive Research Questions

For every important competitor determine:

```text
What exactly do they ingest?

What is their data model?

How do they model agents/subagents?

Do they model harness components?

Do they model state?

Do they model context transitions?

Do they model verification?

Do they support replay?

How deterministic is replay?

Do they support branching replay?

How do they cluster failures?

Do they perform first-divergence analysis?

How do they attribute root cause?

Can they modify runtime behavior?

What is open-source?

What becomes proprietary?

What scales economically?

What is their customer lock-in?
```

---

# 81. Strategic Risks

### Risk 1 — Existing platforms move downward into harness semantics.

Response:

Move quickly on execution ontology, replay, and component-level reliability.

### Risk 2 — OpenTelemetry standardizes our semantics.

Response:

Welcome standardization. Compete in intelligence and reliability.

### Risk 3 — Frontier models make trace analysis trivial.

Response:

Raw trace scale, privacy, latency, cost, deterministic evidence, and replay still matter.

### Risk 4 — Customers do not want another observability vendor.

Response:

Integrate with existing observability systems and become a reliability layer rather than requiring replacement.

### Risk 5 — Replay proves too difficult.

Response:

Begin with constrained environments such as coding agents.

### Risk 6 — Automatic root-cause analysis is unreliable.

Response:

Evidence-backed hypotheses, confidence, deterministic detectors, replay validation.

### Risk 7 — Data volume makes SaaS uneconomic.

Response:

Sampling, local processing, tiered storage, structural telemetry, specialized models, customer-side payload retention.

---

# 82. Foundational Decisions Register

## D-001

**DECIDED**

We are building agent/harness reliability infrastructure, not generic LLM observability.

## D-002

**DECIDED**

Harness execution—not the individual model request—is the primary conceptual unit.

## D-003

**DECIDED**

OpenTelemetry will be the underlying telemetry foundation wherever possible.

## D-004

**DECIDED**

OpenInference compatibility is desirable.

## D-005

**DECIDED**

Our semantic layer must represent harness-specific runtime behavior.

## D-006

**DECIDED**

Execution should be represented as more than a parent-child trace tree.

## D-007

**DECIDED**

A graph representation is required for provenance and cross-step relationships.

## D-008

**DECIDED**

Incident-centric workflows should eventually become more important than raw trace browsing.

## D-009

**DECIDED**

Deterministic and inexpensive analysis should be preferred before frontier-model reasoning.

## D-010

**DECIDED**

Production incidents should feed regression suites.

## D-011

**DECIDED**

Replay is a core capability.

## D-012

**DECIDED**

Branch-aware replay is a significant differentiation target.

## D-013

**DECIDED**

Verification must carry evidence and provenance.

## D-014

**DECIDED**

Context operations must be observable as first-class events.

## D-015

**DECIDED**

State, memory, permissions, tools, subagents, artifacts and stopping decisions should be represented explicitly.

## D-016

**DECIDED**

Success-adjusted economics are first-class.

## D-017

**DECIDED**

Runtime intervention is a long-term product layer, not MVP scope.

## D-018

**DECIDED**

High-risk intervention must be policy-driven and auditable.

## D-019

**DECIDED**

We should strongly pursue open-source instrumentation and semantic conventions.

## D-020

**DECIDED**

We should not begin by building another generic model gateway.

## D-021

**DECIDED**

We should remain framework-independent.

## D-022

**DECIDED**

Customer telemetry must be isolated and privacy-aware by design.

## D-023

**DECIDED**

Raw evidence should remain distinct from derived AI interpretations.

## D-024

**DECIDED**

The platform should expose APIs and not depend solely on a UI.

## D-025

**DECIDED**

This project remains separate from the Canonical Document Graph/document-state platform, generic memory, IAM, MCP gateway, and BPO layers.

## D-026

**PROPOSED**

Coding agents will be the first technical wedge.

## D-027

**PROPOSED**

Open-source developer product name/concept: Harness Flight Recorder.

## D-028

**PROPOSED**

Semantic specification name: Harness Event Model.

## D-029

**PROPOSED**

Graph representation name: Harness Execution Graph.

## D-030

**PROPOSED**

Commercial category description: Harness Reliability Control Plane.

---

# 83. Open Strategic Questions

These remain unresolved:

1. Exact first design-partner profile.
2. Exact first supported coding-agent ecosystems.
3. Whether the first commercial offering begins with incidents or replay.
4. Exact event-schema granularity.
5. Storage architecture under very high-cardinality workloads.
6. How much trace payload remains customer-side.
7. Exact boundary between statistical correlation and causal attribution.
8. Replay isolation architecture.
9. Pricing model.
10. Open-source license.
11. Hosted vs hybrid priority.
12. Whether specialized reliability models should eventually be published.
13. Whether execution-graph semantics should be submitted upstream to OTel/OpenInference.
14. Exact runtime-control architecture.
15. Company/product name.

These must be resolved through subsequent specifications and experiments rather than assumptions.

---

# 84. One-Sentence Product Definition

> **A reliability control plane that reconstructs the complete execution of autonomous agents, detects where their harnesses fail, reproduces those failures, validates fixes against historical trajectories, and ultimately helps prevent the failures from recurring.**

---

# 85. Long-Term Vision

The end-state should look like:

```text
AUTONOMOUS SYSTEM
       │
       ▼
HARNESS
       │
       ▼
FLIGHT RECORDER
       │
       ▼
EXECUTION GRAPH
       │
       ▼
RELIABILITY INTELLIGENCE
       │
       ├── detect
       ├── cluster
       ├── diagnose
       └── explain
       │
       ▼
REPLAY
       │
       ▼
REGRESSION
       │
       ▼
VERIFIED REMEDIATION
       │
       ▼
CONTROL POLICY
       │
       └───────────────┐
                       │
                       ▼
                 HARNESS IMPROVES
```

The long-term goal is not merely observable agents.

It is:

# Agents whose reliability can be measured, explained, reproduced, tested, and systematically improved.
