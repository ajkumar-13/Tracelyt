"""Claude Code OTLP/HTTP JSON log batches -> v0.1 events.

Event names and attributes are those observed in CLI 2.1.289 (Proof A). Log records in the HOOK domain
(hook_registered, hook_execution_*) and configuration records (managed_settings_resolved, plugin_loaded) are
outside v0.1 and are preserved as UNKNOWN with native attributes (they become the HOOK domain in v0.2).
"""
from __future__ import annotations
import json, os
from typing import Iterable

from harness_engine.model.events import (CaptureTier, DecisionSource, Event, EventType, Identity, INTERFACES,
                                          PayloadRef, StopReason, Versions, new_event_id)
from .common import CHANNEL_OTEL, HARNESS, coerce_bool, coerce_int, otlp_attrs, sha, ts

# Attributes that identify a person or account. Stripped by the adapter unless keep_pii=True (SPEC-05).
PII_ATTRS = {"user.email", "user.account_id", "user.account_uuid", "user.id", "organization.id", "ccr.session.id"}
V02_HOOK_DOMAIN = {"hook_registered", "hook_execution_start", "hook_execution_complete"}
V02_CONFIG = {"managed_settings_resolved", "plugin_loaded", "skill_activated", "mcp_server_connection"}


def _identity(a: dict) -> Identity:
    qs = a.get("query_source"); agent = a.get("agent.name")
    return Identity(run_id=a.get("session.id", ""), session_id=a.get("session.id"),
                    agent_instance_id=agent if agent else "main", agent_definition=agent or "main", turn_id=a.get("prompt.id"))


def _mk(etype: EventType, a: dict, native: str, attrs: dict, versions: Versions, status=None, correlation=None, payload_refs=None) -> Event:
    comp, counter = INTERFACES[etype]
    key = [a.get("session.id", ""), native, str(a.get("event.sequence")), a.get("event.timestamp", ""), json.dumps(correlation or {}, sort_keys=True)]
    return Event(event_id=new_event_id(*key), type=etype, native_type=f"otel.claude_code.{native}", timestamp=ts(a.get("event.timestamp")),
                 sequence=coerce_int(a.get("event.sequence")), identity=_identity(a), versions=versions, component=comp, counterpart=counter,
                 correlation=correlation or {}, status=status, attrs=attrs, payload_refs=payload_refs or {},
                 capture_tier=CaptureTier.B, source_channel=CHANNEL_OTEL)


def _read_body(path: str | None, path_rewrite: tuple[str, str] | None):
    if not path: return None
    if path_rewrite: path = path.replace(path_rewrite[0], path_rewrite[1])
    try:
        with open(path) as f: return json.load(f)
    except Exception:
        return None


def parse_otlp_logs(batches: Iterable[dict], keep_pii: bool = False, body_path_rewrite: tuple[str, str] | None = None) -> tuple[list[Event], dict]:
    events: list[Event] = []
    stats = {"records": 0, "mapped": 0, "unmapped": 0, "unmapped_names": {}, "pii_attrs_stripped": 0}
    harness_version = None
    for batch in batches:
        for rl in batch.get("resourceLogs", []):
            res = otlp_attrs(rl.get("resource", {}).get("attributes", []))
            harness_version = res.get("service.version", harness_version)
            versions = Versions(harness=f"{HARNESS}@{harness_version}" if harness_version else HARNESS)
            for sl in rl.get("scopeLogs", []):
                for lr in sl.get("logRecords", []):
                    a = otlp_attrs(lr.get("attributes", []))
                    if not keep_pii:
                        for k in list(a):
                            if k in PII_ATTRS: a.pop(k); stats["pii_attrs_stripped"] += 1
                    name = a.get("event.name") or str(lr.get("body", {}).get("stringValue", "")).replace("claude_code.", "")
                    stats["records"] += 1
                    versions_m = versions.model_copy(update={"model": a.get("model")}) if a.get("model") else versions
                    if name == "user_prompt":
                        events.append(_mk(EventType.ITERATION_STARTED, a, name, {"iteration": 0},
                                          versions, correlation={"turn_id": a.get("prompt.id", ""), "message_uuid": a.get("message.uuid", "")},
                                          payload_refs={"prompt": PayloadRef.of(a["prompt"])} if a.get("prompt") else {}))
                    elif name == "api_request_body":
                        body = _read_body(a.get("body_ref"), body_path_rewrite)
                        attrs = {"model": a.get("model", ""), "client_request_id": None, "query_source": a.get("query_source")}
                        refs = {}
                        if body:
                            attrs.update({"num_messages": len(body.get("messages", [])), "num_tools": len(body.get("tools", []) or []),
                                          "tools_hash": sha(body.get("tools", [])), "system_hash": sha(body.get("system", "")),
                                          "max_tokens": body.get("max_tokens"), "thinking_budget_tokens": (body.get("thinking") or {}).get("budget_tokens"),
                                          "previous_message_id": (body.get("thread") or {}).get("previous_message_id")})
                            refs["request_body"] = PayloadRef.of(json.dumps(body, sort_keys=True, default=str), uri=a.get("body_ref"))
                        else:
                            refs["request_body"] = PayloadRef(sha256=sha(a.get("body_ref", "")), size_bytes=coerce_int(a.get("body_length")) or 0, uri=a.get("body_ref"), redaction="full")
                        events.append(_mk(EventType.MODEL_REQUEST, a, name, attrs, versions_m,
                                          correlation={"request_body_id": a.get("request_body_id", ""), "turn_id": a.get("prompt.id", "")}, payload_refs=refs))
                    elif name == "api_request":
                        attrs = {"model": a.get("model", ""), "request_id": a.get("request_id"), "input_tokens": a.get("input_tokens"), "output_tokens": a.get("output_tokens"),
                                 "cache_read_tokens": a.get("cache_read_tokens"), "cache_creation_tokens": a.get("cache_creation_tokens"), "cost_usd": a.get("cost_usd"),
                                 "duration_ms": a.get("duration_ms"), "ttft_ms": a.get("ttft_ms")}
                        events.append(_mk(EventType.MODEL_RESPONSE, a, name, attrs, versions_m,
                                          correlation={"request_id": a.get("request_id", ""), "turn_id": a.get("prompt.id", "")}))
                    elif name == "api_response_body":
                        body = _read_body(a.get("body_ref"), body_path_rewrite)
                        attrs = {"model": a.get("model", ""), "request_id": a.get("request_id"), "message_id": a.get("message.id")}
                        refs = {}
                        if body:
                            attrs["finish_reason"] = body.get("stop_reason")
                            attrs["num_tool_calls"] = sum(1 for b in body.get("content", []) if b.get("type") == "tool_use")
                            refs["response_body"] = PayloadRef.of(json.dumps(body, sort_keys=True, default=str), uri=a.get("body_ref"))
                        events.append(_mk(EventType.MODEL_RESPONSE, a, name, attrs, versions_m,
                                          correlation={"request_id": a.get("request_id", ""), "request_body_id": a.get("request_body_id", ""), "message_uuid": a.get("message.uuid", "")}, payload_refs=refs))
                    elif name == "api_error":
                        events.append(_mk(EventType.MODEL_RESPONSE, a, name, {"model": a.get("model", ""), "error_type": a.get("error") or a.get("error_type"), "retry_attempt": coerce_int(a.get("attempt")), "duration_ms": a.get("duration_ms")},
                                          versions_m, status="error", correlation={"request_id": a.get("request_id", ""), "turn_id": a.get("prompt.id", "")}))
                    elif name == "tool_decision":
                        dec = a.get("decision"); src = a.get("source", "unknown")
                        src_map = {"config": DecisionSource.CONFIG, "hook": DecisionSource.HOOK, "user_permanent": DecisionSource.USER_PERMANENT, "user_temporary": DecisionSource.USER_TEMPORARY,
                                   "user_abort": DecisionSource.USER_ABORT, "user_reject": DecisionSource.USER_REJECT}
                        etype = EventType.TOOL_AUTHORIZED if dec == "accept" else EventType.TOOL_REJECTED
                        events.append(_mk(etype, a, name, {"tool_name": a.get("tool_name", ""), "tool_call_id": a.get("tool_use_id", ""), "decision": "allow" if dec == "accept" else "deny",
                                                           "source": src_map.get(src, DecisionSource.UNKNOWN)}, versions,
                                          status="ok" if dec == "accept" else "denied", correlation={"tool_call_id": a.get("tool_use_id", "")}))
                    elif name == "tool_result":
                        ok = coerce_bool(a.get("success")) is True
                        attrs = {"tool_name": a.get("tool_name", ""), "tool_call_id": a.get("tool_use_id", ""), "success": ok, "duration_ms": coerce_int(a.get("duration_ms")),
                                 "output_size_bytes": coerce_int(a.get("tool_result_size_bytes")), "error_type": a.get("error_type"),
                                 "error_message_hash": sha(a["error"]) if a.get("error") else None}
                        events.append(_mk(EventType.TOOL_COMPLETED if ok else EventType.TOOL_FAILED, a, name, attrs, versions, status="ok" if ok else "error",
                                          correlation={"tool_call_id": a.get("tool_use_id", "")}))
                    elif name == "subagent_completed":
                        events.append(_mk(EventType.AGENT_RETURNED, a, name, {"child_agent_instance_id": "", "child_agent_definition": a.get("agent_type"),
                                                                              "total_tokens": a.get("total_tokens"), "total_tool_uses": a.get("total_tool_uses"), "duration_ms": a.get("duration_ms"),
                                                                              "model_swapped": a.get("model_swapped")}, versions_m,
                                          correlation={"child_agent_definition": a.get("agent_type", ""), "turn_id": a.get("prompt.id", "")}))
                    elif name == "compaction":
                        events.append(_mk(EventType.CONTEXT_COMPACT, a, name, {"trigger": a.get("trigger", "unknown"), "duration_ms": coerce_int(a.get("duration_ms")),
                                                                              # OTel pre_tokens disagrees with the SDK compact_boundary (5421 vs 32800 in Proof A); kept as native_* until the semantics are confirmed.
                                                                              "native_pre_tokens": coerce_int(a.get("pre_tokens")), "native_post_tokens": coerce_int(a.get("post_tokens")), "native_precompute_reuse": a.get("precompute_reuse")},
                                          versions, status="ok" if coerce_bool(a.get("success")) else "error", correlation={"turn_id": a.get("prompt.id", "")}))
                    elif name == "api_retries_exhausted":
                        events.append(_mk(EventType.MODEL_RESPONSE, a, name, {"model": a.get("model", ""), "error_type": "retries_exhausted", "retry_attempt": coerce_int(a.get("attempt"))}, versions_m, status="error"))
                    elif name == "permission_mode_changed":
                        events.append(_mk(EventType.PERMISSION_GRANTED, a, name, {"action": "mode_change", "reason": f"{a.get('from_mode')}->{a.get('to_mode')}", "source": DecisionSource.USER}, versions))
                    elif name in V02_HOOK_DOMAIN or name in V02_CONFIG or name in ("assistant_response",):
                        # assistant_response duplicates api_response_body content; HOOK/config are v0.2 domains.
                        stats["unmapped"] += 1; stats["unmapped_names"][name] = stats["unmapped_names"].get(name, 0) + 1
                        events.append(_mk(EventType.UNKNOWN, a, name, {"native": {k: v for k, v in a.items() if k not in ("prompt", "response")}}, versions))
                        continue
                    else:
                        stats["unmapped"] += 1; stats["unmapped_names"][name] = stats["unmapped_names"].get(name, 0) + 1
                        events.append(_mk(EventType.UNKNOWN, a, name, {"native": a}, versions)); continue
                    stats["mapped"] += 1
    return events, stats
