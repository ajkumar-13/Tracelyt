"""Harness event model v0.1 (SPEC-01 draft).

First principles:
* A harness is components joined by interfaces; every event names the component on each side
  so attribution is possible by construction.
* Observed facts carry runtime identifiers. Reconstructed and inferred facts live on graph edges,
  never inside events.
* Content never travels inside an event. It is referenced by content hash (PayloadRef).
* Nine domains, ~20 events in v0.1 (PLAN-11 D-034). Unknown events are kept via EventType.UNKNOWN
  with the native name preserved in `native_type`.
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, field_validator

SCHEMA_VERSION = "0.1.0"


class Component(str, Enum):
    """Harness components. Also the component dimension of the failure taxonomy (PLAN-11 D-035)."""
    MODEL = "model"
    PLANNER = "planner"
    LOOP = "loop"
    CONTEXT_BUILDER = "context_builder"
    COMPACTOR = "compactor"
    MEMORY = "memory"
    RETRIEVAL = "retrieval"
    TOOL = "tool"
    MCP = "mcp"
    PERMISSION = "permission"
    HOOK = "hook"
    SANDBOX = "sandbox"
    STATE = "state"
    DELEGATION = "delegation"
    VERIFICATION = "verification"
    ARTIFACT = "artifact"
    BUDGET = "budget"
    STOP = "stop"
    ENVIRONMENT = "environment"
    HUMAN = "human"
    EXTERNAL = "external_dependency"
    UNKNOWN = "unknown"


class EventType(str, Enum):
    # RUN
    RUN_STARTED = "run.started"
    RUN_RESUMED = "run.resumed"
    RUN_COMPLETED = "run.completed"
    RUN_FAILED = "run.failed"
    RUN_ABORTED = "run.aborted"
    # LOOP
    ITERATION_STARTED = "iteration.started"
    ITERATION_COMPLETED = "iteration.completed"
    # MODEL
    MODEL_REQUEST = "model.request"
    MODEL_RESPONSE = "model.response"
    # TOOL / MCP
    TOOL_REQUESTED = "tool.requested"
    TOOL_AUTHORIZED = "tool.authorized"
    TOOL_REJECTED = "tool.rejected"
    TOOL_STARTED = "tool.started"
    TOOL_COMPLETED = "tool.completed"
    TOOL_FAILED = "tool.failed"
    # CONTEXT
    CONTEXT_BUILD = "context.build"
    CONTEXT_COMPACT = "context.compact"
    CONTEXT_PROVENANCE_LOADED = "context.provenance.loaded"
    # PERMISSION
    PERMISSION_REQUESTED = "permission.requested"
    PERMISSION_GRANTED = "permission.granted"
    PERMISSION_DENIED = "permission.denied"
    # AGENT (delegation)
    AGENT_SPAWNED = "agent.spawned"
    AGENT_RETURNED = "agent.returned"
    AGENT_CANCELLED = "agent.cancelled"
    # VERIFICATION
    VERIFY_REQUESTED = "verify.requested"
    VERIFY_EVIDENCE = "verify.evidence"
    VERIFY_PASSED = "verify.passed"
    VERIFY_FAILED = "verify.failed"
    VERIFY_ABSTAINED = "verify.abstained"
    # STOP
    STOP = "stop"
    # Extensibility
    UNKNOWN = "unknown"


class StopReason(str, Enum):
    SUCCESS = "success"
    VERIFIED_SUCCESS = "verified_success"
    AGENT_DECLARED_COMPLETE = "agent_declared_complete"
    BUDGET_EXHAUSTED = "budget_exhausted"
    TIMEOUT = "timeout"
    NO_PROGRESS = "no_progress"
    POLICY_STOP = "policy_stop"
    HUMAN_STOP = "human_stop"
    FATAL_ERROR = "fatal_error"
    EXTERNAL_DEPENDENCY = "external_dependency"
    MAX_TURNS = "max_turns"
    UNKNOWN = "unknown"


class DecisionSource(str, Enum):
    CONFIG = "config"
    HOOK = "hook"
    USER = "user"
    USER_PERMANENT = "user_permanent"
    USER_TEMPORARY = "user_temporary"
    USER_ABORT = "user_abort"
    USER_REJECT = "user_reject"
    CLASSIFIER = "classifier"
    POLICY = "policy"
    HEADLESS_DEFAULT = "headless_default"
    UNKNOWN = "unknown"


class SideEffectClass(str, Enum):
    READ_ONLY = "read_only"
    REVERSIBLE_WRITE = "reversible_write"
    IRREVERSIBLE_WRITE = "irreversible_write"
    FINANCIAL = "financial"
    SECURITY_SENSITIVE = "security_sensitive"
    EXTERNAL_COMMUNICATION = "external_communication"
    UNKNOWN = "unknown"


class CaptureTier(str, Enum):
    A = "A"  # native instrumentation
    B = "B"  # hook / OTel adapter on a closed harness
    C = "C"  # API / log adapter


class PayloadRef(BaseModel):
    """Content-addressed reference. Content stays customer-side; events carry only this."""
    sha256: str = Field(..., min_length=64, max_length=64)
    size_bytes: int = Field(..., ge=0)
    media_type: str = "application/json"
    uri: Optional[str] = None            # customer object store or local path; never required
    redaction: Literal["none", "partial", "full", "hashed"] = "none"

    @classmethod
    def of(cls, content: bytes | str, media_type: str = "application/json", uri: str | None = None) -> "PayloadRef":
        b = content.encode() if isinstance(content, str) else content
        return cls(sha256=hashlib.sha256(b).hexdigest(), size_bytes=len(b), media_type=media_type, uri=uri)


class Identity(BaseModel):
    """Execution identity. Never conflate these (PLAN-12 §7)."""
    organization_id: Optional[str] = None
    project_id: Optional[str] = None
    run_id: str                                   # the semantic execution; for CLIs the session
    session_id: Optional[str] = None              # long-lived container of runs, if distinct
    agent_definition: Optional[str] = None        # e.g. "reviewer", "main"
    agent_instance_id: Optional[str] = None       # runtime instance; subagents get their own
    parent_agent_instance_id: Optional[str] = None
    iteration: Optional[int] = None               # loop index within the agent instance
    turn_id: Optional[str] = None                 # human prompt scope (Claude Code prompt_id)
    trace_id: Optional[str] = None
    span_id: Optional[str] = None


class Versions(BaseModel):
    harness: Optional[str] = None                 # e.g. "claude-code@2.1.289"
    harness_config_hash: Optional[str] = None     # hash of rules files + settings + hooks + MCP config
    model: Optional[str] = None
    prompt: Optional[str] = None
    policy: Optional[str] = None
    tools: Optional[str] = None                   # hash of tool definitions presented to the model
    code_commit: Optional[str] = None
    runtime_image: Optional[str] = None


class Event(BaseModel):
    """Envelope. `attrs` is validated against the per-type model in ATTR_MODELS when present."""
    event_id: str
    type: EventType
    native_type: Optional[str] = None             # the emitter's own name, always preserved
    timestamp: datetime
    sequence: Optional[int] = None                # emitter-monotonic order when available
    identity: Identity
    versions: Versions = Field(default_factory=Versions)
    component: Component                          # the component that produced/owns this event
    counterpart: Optional[Component] = None       # the component on the other side of the interface
    parent_event_id: Optional[str] = None
    correlation: dict[str, str] = Field(default_factory=dict)   # tool_call_id, request_id, message_uuid...
    status: Optional[Literal["ok", "error", "denied", "cancelled", "unknown"]] = None
    attrs: dict[str, Any] = Field(default_factory=dict)
    payload_refs: dict[str, PayloadRef] = Field(default_factory=dict)  # named refs: input, output, summary...
    capture_tier: CaptureTier
    source_channel: str                           # "claude_code.hooks", "claude_code.otel_logs", "langgraph.callbacks"...
    schema_version: str = SCHEMA_VERSION

    @field_validator("timestamp")
    @classmethod
    def _tz(cls, v: datetime) -> datetime:
        return v if v.tzinfo else v.replace(tzinfo=timezone.utc)

    def validated_attrs(self) -> BaseModel | None:
        m = ATTR_MODELS.get(self.type)
        return m.model_validate(self.attrs) if m else None


# ---- Per-event attribute models (the normative field lists for SPEC-01 v0.1) -----------------

class RunStartedAttrs(BaseModel):
    task: Optional[str] = None                    # redacted/hashed by policy; often a PayloadRef instead
    entrypoint: Optional[str] = None              # cli, sdk, ci, api
    permission_mode: Optional[str] = None
    cwd_hash: Optional[str] = None
    source: Optional[str] = None                  # startup | resume | clear | compact | fork

class RunEndedAttrs(BaseModel):
    stop_reason: StopReason = StopReason.UNKNOWN
    total_turns: Optional[int] = None
    duration_ms: Optional[int] = None
    total_cost_usd: Optional[float] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    cache_read_tokens: Optional[int] = None
    cache_creation_tokens: Optional[int] = None
    num_permission_denials: Optional[int] = None
    terminal_reason: Optional[str] = None         # emitter's own reason string, preserved

class IterationAttrs(BaseModel):
    iteration: int
    state_hash_before: Optional[str] = None
    state_hash_after: Optional[str] = None
    budget_remaining_tokens: Optional[int] = None
    budget_remaining_usd: Optional[float] = None
    progress_signal: Optional[Literal["progress", "no_change", "unknown"]] = None

class ModelRequestAttrs(BaseModel):
    provider: Optional[str] = None
    model: str
    request_id: Optional[str] = None
    client_request_id: Optional[str] = None
    max_tokens: Optional[int] = None
    thinking_budget_tokens: Optional[int] = None
    num_messages: Optional[int] = None
    num_tools: Optional[int] = None
    tools_hash: Optional[str] = None
    system_hash: Optional[str] = None
    previous_message_id: Optional[str] = None     # chain between consecutive calls
    context_tokens_estimate: Optional[int] = None
    query_source: Optional[str] = None            # main | subagent | auxiliary | sdk

class ModelResponseAttrs(BaseModel):
    model: str
    request_id: Optional[str] = None
    message_id: Optional[str] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    cache_read_tokens: Optional[int] = None
    cache_creation_tokens: Optional[int] = None
    thinking_tokens: Optional[int] = None
    cost_usd: Optional[float] = None
    duration_ms: Optional[int] = None
    ttft_ms: Optional[int] = None
    finish_reason: Optional[str] = None           # end_turn | tool_use | max_tokens | refusal | ...
    num_tool_calls: Optional[int] = None
    retry_attempt: Optional[int] = None
    error_type: Optional[str] = None

class ToolRequestedAttrs(BaseModel):
    tool_name: str
    tool_call_id: str
    tool_source: Optional[str] = None             # builtin | mcp | plugin
    mcp_server: Optional[str] = None
    mcp_tool: Optional[str] = None
    side_effect_class: SideEffectClass = SideEffectClass.UNKNOWN
    input_hash: Optional[str] = None
    input_size_bytes: Optional[int] = None
    # For coding harnesses, a structural summary that never carries content:
    file_path_hash: Optional[str] = None
    command_binary: Optional[str] = None          # e.g. "python3" (never the full command unless opted in)

class ToolDecisionAttrs(BaseModel):
    tool_name: str
    tool_call_id: str
    decision: Literal["allow", "deny", "ask", "defer"]
    source: DecisionSource = DecisionSource.UNKNOWN
    rule: Optional[str] = None
    reason: Optional[str] = None

class ToolResultAttrs(BaseModel):
    tool_name: str
    tool_call_id: str
    success: bool
    duration_ms: Optional[int] = None
    output_hash: Optional[str] = None
    output_size_bytes: Optional[int] = None
    error_type: Optional[str] = None
    error_message_hash: Optional[str] = None
    exit_code: Optional[int] = None
    # artifact effects, structural only
    files_created: Optional[int] = None
    files_modified: Optional[int] = None
    lines_added: Optional[int] = None
    lines_removed: Optional[int] = None

class ContextCompactAttrs(BaseModel):
    trigger: Literal["auto", "manual", "policy", "unknown"] = "unknown"
    tokens_before: Optional[int] = None
    tokens_after: Optional[int] = None
    tokens_dropped: Optional[int] = None
    duration_ms: Optional[int] = None
    policy_version: Optional[str] = None
    preserved_head_id: Optional[str] = None
    preserved_anchor_id: Optional[str] = None
    preserved_tail_id: Optional[str] = None
    num_preserved_messages: Optional[int] = None
    custom_instructions_present: Optional[bool] = None
    # Declared-state survival (reconstructed later; recorded here when the harness reports it)
    declared_keys_total: Optional[int] = None
    declared_keys_surviving: Optional[int] = None

class ContextProvenanceLoadedAttrs(BaseModel):
    source_kind: str                              # project_instructions | user_instructions | rule | skill | memory | tool_result
    source_id_hash: str                           # hash of full path or identifier (run-specific)
    source_name_hash: Optional[str] = None        # hash of the basename; comparable across runs
    load_reason: Optional[str] = None             # session_start | resume | tool | explicit
    content_hash: Optional[str] = None
    tokens: Optional[int] = None

class PermissionAttrs(BaseModel):
    actor: Optional[str] = None                   # agent instance
    resource: Optional[str] = None                # tool name or resource class
    action: Optional[str] = None
    tool_call_id: Optional[str] = None
    decision: Optional[Literal["granted", "denied", "pending"]] = None
    source: DecisionSource = DecisionSource.UNKNOWN
    policy_version: Optional[str] = None
    reason: Optional[str] = None
    classifier_verdict: Optional[str] = None
    num_suggested_rules: Optional[int] = None

class AgentSpawnedAttrs(BaseModel):
    child_agent_instance_id: str
    child_agent_definition: Optional[str] = None
    via_tool_call_id: Optional[str] = None
    is_async: Optional[bool] = None
    model: Optional[str] = None
    task_hash: Optional[str] = None
    shared_context_hashes: list[str] = Field(default_factory=list)
    budget_tokens: Optional[int] = None

class AgentReturnedAttrs(BaseModel):
    child_agent_instance_id: str
    total_tokens: Optional[int] = None
    total_tool_uses: Optional[int] = None
    duration_ms: Optional[int] = None
    model_swapped: Optional[bool] = None
    result_hash: Optional[str] = None
    status: Optional[Literal["ok", "error", "cancelled"]] = None

class VerifyAttrs(BaseModel):
    claim: Optional[str] = None                   # e.g. "task_complete", "tests_pass"
    claim_hash: Optional[str] = None
    evaluator: Optional[str] = None               # pytest | build | lint | human | llm_judge | harness_adapter
    policy: Optional[str] = None
    threshold: Optional[str] = None
    outcome: Optional[Literal["passed", "failed", "abstained", "pending"]] = None
    evidence_hashes: list[str] = Field(default_factory=list)
    exit_code: Optional[int] = None
    tests_total: Optional[int] = None
    tests_failed: Optional[int] = None

class StopAttrs(BaseModel):
    reason: StopReason
    declared_by: Optional[Literal["agent", "harness", "human", "policy", "budget", "error"]] = None
    verification_present: Optional[bool] = None   # was any verify.* event observed before the stop
    native_reason: Optional[str] = None


ATTR_MODELS: dict[EventType, type[BaseModel]] = {
    EventType.RUN_STARTED: RunStartedAttrs,
    EventType.RUN_RESUMED: RunStartedAttrs,
    EventType.RUN_COMPLETED: RunEndedAttrs,
    EventType.RUN_FAILED: RunEndedAttrs,
    EventType.RUN_ABORTED: RunEndedAttrs,
    EventType.ITERATION_STARTED: IterationAttrs,
    EventType.ITERATION_COMPLETED: IterationAttrs,
    EventType.MODEL_REQUEST: ModelRequestAttrs,
    EventType.MODEL_RESPONSE: ModelResponseAttrs,
    EventType.TOOL_REQUESTED: ToolRequestedAttrs,
    EventType.TOOL_AUTHORIZED: ToolDecisionAttrs,
    EventType.TOOL_REJECTED: ToolDecisionAttrs,
    EventType.TOOL_STARTED: ToolRequestedAttrs,
    EventType.TOOL_COMPLETED: ToolResultAttrs,
    EventType.TOOL_FAILED: ToolResultAttrs,
    EventType.CONTEXT_COMPACT: ContextCompactAttrs,
    EventType.CONTEXT_PROVENANCE_LOADED: ContextProvenanceLoadedAttrs,
    EventType.PERMISSION_REQUESTED: PermissionAttrs,
    EventType.PERMISSION_GRANTED: PermissionAttrs,
    EventType.PERMISSION_DENIED: PermissionAttrs,
    EventType.AGENT_SPAWNED: AgentSpawnedAttrs,
    EventType.AGENT_RETURNED: AgentReturnedAttrs,
    EventType.AGENT_CANCELLED: AgentReturnedAttrs,
    EventType.VERIFY_REQUESTED: VerifyAttrs,
    EventType.VERIFY_EVIDENCE: VerifyAttrs,
    EventType.VERIFY_PASSED: VerifyAttrs,
    EventType.VERIFY_FAILED: VerifyAttrs,
    EventType.VERIFY_ABSTAINED: VerifyAttrs,
    EventType.STOP: StopAttrs,
}

# Interface each event sits on: (owning component, counterpart). Attribution by construction.
INTERFACES: dict[EventType, tuple[Component, Optional[Component]]] = {
    EventType.RUN_STARTED: (Component.LOOP, Component.HUMAN),
    EventType.RUN_RESUMED: (Component.LOOP, Component.HUMAN),
    EventType.RUN_COMPLETED: (Component.LOOP, Component.STOP),
    EventType.RUN_FAILED: (Component.LOOP, Component.STOP),
    EventType.RUN_ABORTED: (Component.LOOP, Component.STOP),
    EventType.ITERATION_STARTED: (Component.LOOP, None),
    EventType.ITERATION_COMPLETED: (Component.LOOP, None),
    EventType.MODEL_REQUEST: (Component.CONTEXT_BUILDER, Component.MODEL),
    EventType.MODEL_RESPONSE: (Component.MODEL, Component.LOOP),
    EventType.TOOL_REQUESTED: (Component.MODEL, Component.TOOL),
    EventType.TOOL_AUTHORIZED: (Component.PERMISSION, Component.TOOL),
    EventType.TOOL_REJECTED: (Component.PERMISSION, Component.TOOL),
    EventType.TOOL_STARTED: (Component.TOOL, Component.SANDBOX),
    EventType.TOOL_COMPLETED: (Component.TOOL, Component.CONTEXT_BUILDER),
    EventType.TOOL_FAILED: (Component.TOOL, Component.CONTEXT_BUILDER),
    EventType.CONTEXT_BUILD: (Component.CONTEXT_BUILDER, Component.MODEL),
    EventType.CONTEXT_COMPACT: (Component.COMPACTOR, Component.CONTEXT_BUILDER),
    EventType.CONTEXT_PROVENANCE_LOADED: (Component.CONTEXT_BUILDER, Component.ENVIRONMENT),
    EventType.PERMISSION_REQUESTED: (Component.PERMISSION, Component.HUMAN),
    EventType.PERMISSION_GRANTED: (Component.PERMISSION, Component.TOOL),
    EventType.PERMISSION_DENIED: (Component.PERMISSION, Component.TOOL),
    EventType.AGENT_SPAWNED: (Component.DELEGATION, Component.LOOP),
    EventType.AGENT_RETURNED: (Component.DELEGATION, Component.CONTEXT_BUILDER),
    EventType.AGENT_CANCELLED: (Component.DELEGATION, Component.LOOP),
    EventType.VERIFY_REQUESTED: (Component.VERIFICATION, Component.ARTIFACT),
    EventType.VERIFY_EVIDENCE: (Component.VERIFICATION, Component.ARTIFACT),
    EventType.VERIFY_PASSED: (Component.VERIFICATION, Component.STOP),
    EventType.VERIFY_FAILED: (Component.VERIFICATION, Component.LOOP),
    EventType.VERIFY_ABSTAINED: (Component.VERIFICATION, Component.STOP),
    EventType.STOP: (Component.STOP, Component.HUMAN),
    EventType.UNKNOWN: (Component.UNKNOWN, None),
}

# Naming forms (PLAN-05 C-3 / ADR-002). Proposal form for OTel and the registry form we govern.
NAMING: dict[EventType, dict[str, str]] = {
    t: {"harness": f"harness.{t.value}", "gen_ai_proposal": f"gen_ai.{t.value}"} for t in EventType
}


def new_event_id(*parts: str) -> str:
    """Deterministic event id from stable parts, so re-normalization is idempotent (PLAN-11 P18)."""
    return hashlib.sha256("|".join(parts).encode()).hexdigest()[:32]
