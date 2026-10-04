"""Claude Code hook stream -> v0.1 events.

Input: JSONL lines of the form {"_hook": <event name>, "_ts": <iso>, "payload": {...}} as produced by a
hook command that dumps its stdin. Field names are those observed in CLI 2.1.289 (Proof A) and the
hooks reference (docs/phase0/research/02-claude-code-surfaces.md).
"""
from __future__ import annotations
import json, os
from typing import Iterable

from harness_engine.model.events import (CaptureTier, Component, DecisionSource, Event, EventType, Identity,
                                          INTERFACES, PayloadRef, StopReason, Versions, new_event_id)
from .common import (BUILTIN_SIDE_EFFECTS, CHANNEL_HOOKS, HARNESS, bash_side_effect, coerce_int, sha, ts)

UNMAPPED_HOOKS = {"Notification", "MessageDisplay", "Setup", "ConfigChange", "CwdChanged", "DirectoryAdded",
                  "FileChanged", "WorktreeCreate", "WorktreeRemove", "TeammateIdle", "TaskCreated", "TaskCompleted",
                  "UserPromptExpansion", "PostToolBatch", "PreModelSwitch", "PostModelSwitch",
                  "Elicitation", "ElicitationResult", "StopFailure"}


def _identity(p: dict) -> Identity:
    return Identity(run_id=p["session_id"], session_id=p["session_id"],
                    agent_instance_id=p.get("agent_id") or "main",
                    agent_definition=p.get("agent_type") or ("main" if not p.get("agent_id") else None),
                    turn_id=p.get("prompt_id"))


def _mk(etype: EventType, p: dict, when: str, native: str, attrs: dict, status=None, correlation=None,
        payload_refs=None, versions: Versions | None = None, counterpart_override: Component | None = None) -> Event:
    comp, counter = INTERFACES[etype]
    key_parts = [p["session_id"], native, when, json.dumps(correlation or {}, sort_keys=True)]
    return Event(event_id=new_event_id(*key_parts), type=etype, native_type=f"hook.{native}", timestamp=ts(when),
                 identity=_identity(p), versions=versions or Versions(harness=HARNESS), component=comp,
                 counterpart=counterpart_override or counter, correlation=correlation or {}, status=status,
                 attrs=attrs, payload_refs=payload_refs or {}, capture_tier=CaptureTier.B, source_channel=CHANNEL_HOOKS)


def parse_hooks(lines: Iterable[str], harness_version: str | None = None, path_rewrite: tuple[str, str] | None = None) -> tuple[list[Event], dict]:
    events: list[Event] = []
    stats = {"records": 0, "mapped": 0, "unmapped": 0, "unmapped_names": {}}
    versions = Versions(harness=f"{HARNESS}@{harness_version}" if harness_version else HARNESS)
    pending_compact: dict[str, dict] = {}
    for line in lines:
        line = line.strip()
        if not line: continue
        rec = json.loads(line); name = rec["_hook"]; when = rec["_ts"]; p = rec["payload"]
        stats["records"] += 1
        if name == "SessionStart":
            events.append(_mk(EventType.RUN_STARTED if p.get("source") != "resume" else EventType.RUN_RESUMED, p, when, name,
                              {"source": p.get("source"), "entrypoint": "cli", "permission_mode": p.get("permission_mode"),
                               "cwd_hash": sha(p.get("cwd", ""))}, versions=versions))
        elif name == "InstructionsLoaded":
            content_hash = None; tokens = None
            fp = p.get("file_path", "")
            if path_rewrite and fp: fp = fp.replace(path_rewrite[0], path_rewrite[1])
            try:
                with open(fp) as fh:
                    content = fh.read(); content_hash = sha(content); tokens = max(1, len(content) // 4)
            except OSError:
                pass
            events.append(_mk(EventType.CONTEXT_PROVENANCE_LOADED, p, when, name,
                              {"source_kind": {"Project": "project_instructions", "User": "user_instructions", "Local": "local_instructions"}.get(p.get("memory_type"), str(p.get("memory_type")).lower()),
                               "source_id_hash": sha(p.get("file_path", "")), "source_name_hash": sha(os.path.basename(p.get("file_path", ""))), "load_reason": p.get("load_reason"), "content_hash": content_hash, "tokens": tokens},
                              correlation={"file_path_hash": sha(p.get("file_path", "")), **({"content_hash": content_hash} if content_hash else {})}, versions=versions))
        elif name == "UserPromptSubmit":
            prompt = p.get("prompt", "")
            events.append(_mk(EventType.ITERATION_STARTED, p, when, name, {"iteration": 0},
                              correlation={"turn_id": p.get("prompt_id", "")},
                              payload_refs={"prompt": PayloadRef.of(prompt)} if prompt else {}, versions=versions))
        elif name == "PreToolUse":
            tool = p.get("tool_name", ""); inp = p.get("tool_input", {}) or {}
            se = BUILTIN_SIDE_EFFECTS.get(tool); binary = None
            if tool == "Bash":
                se, binary = bash_side_effect(inp.get("command"))
            attrs = {"tool_name": tool, "tool_call_id": p.get("tool_use_id", ""), "tool_source": "mcp" if tool.startswith("mcp__") else "builtin",
                     "side_effect_class": (se or BUILTIN_SIDE_EFFECTS.get(tool, "unknown")), "input_hash": sha(inp), "input_size_bytes": len(json.dumps(inp, default=str)),
                     "command_binary": binary}
            if tool.startswith("mcp__"):
                parts = tool.split("__"); attrs["mcp_server"] = parts[1] if len(parts) > 1 else None; attrs["mcp_tool"] = parts[2] if len(parts) > 2 else None
            if isinstance(inp, dict) and inp.get("file_path"): attrs["file_path_hash"] = sha(inp["file_path"])
            events.append(_mk(EventType.TOOL_REQUESTED, p, when, name, attrs, correlation={"tool_call_id": p.get("tool_use_id", "")},
                              payload_refs={"input": PayloadRef.of(json.dumps(inp, sort_keys=True, default=str))}, versions=versions))
        elif name == "PermissionRequest":
            events.append(_mk(EventType.PERMISSION_REQUESTED, p, when, name,
                              {"actor": p.get("agent_id") or "main", "resource": p.get("tool_name"), "action": "invoke", "decision": "pending",
                               "source": DecisionSource.UNKNOWN, "num_suggested_rules": len(p.get("permission_suggestions") or [])},
                              correlation={"tool_call_id": p.get("tool_use_id", "")}, versions=versions))
        elif name == "PermissionDenied":
            events.append(_mk(EventType.PERMISSION_DENIED, p, when, name,
                              {"actor": p.get("agent_id") or "main", "resource": p.get("tool_name"), "action": "invoke", "decision": "denied",
                               "source": DecisionSource.CLASSIFIER if p.get("classifier_verdict") else DecisionSource.UNKNOWN,
                               "reason": p.get("denial_reason"), "classifier_verdict": p.get("classifier_verdict")},
                              status="denied", correlation={"tool_call_id": p.get("tool_use_id", "")}, versions=versions))
        elif name in ("PostToolUse", "PostToolUseFailure"):
            tool = p.get("tool_name", ""); resp = p.get("tool_response"); err = p.get("tool_error") or p.get("error")
            ok = name == "PostToolUse"
            attrs = {"tool_name": tool, "tool_call_id": p.get("tool_use_id", ""), "success": ok, "duration_ms": coerce_int(p.get("duration_ms")),
                     "output_hash": sha(resp) if resp is not None else None, "output_size_bytes": len(json.dumps(resp, default=str)) if resp is not None else None}
            if not ok:
                attrs["error_type"] = "ToolError"; attrs["error_message_hash"] = sha(str(err)) if err else None
            if isinstance(resp, dict):
                if resp.get("type") == "create": attrs["files_created"] = 1
                if resp.get("type") == "update": attrs["files_modified"] = 1
                if "exit_code" in resp: attrs["exit_code"] = coerce_int(resp.get("exit_code"))
            refs = {}
            if resp is not None: refs["output"] = PayloadRef.of(json.dumps(resp, sort_keys=True, default=str))
            if err: refs["error"] = PayloadRef.of(str(err))
            events.append(_mk(EventType.TOOL_COMPLETED if ok else EventType.TOOL_FAILED, p, when, name, attrs, status="ok" if ok else "error",
                              correlation={"tool_call_id": p.get("tool_use_id", "")}, payload_refs=refs, versions=versions))
        elif name == "SubagentStart":
            parent = dict(p); parent.pop("agent_id", None); parent.pop("agent_type", None)
            events.append(_mk(EventType.AGENT_SPAWNED, parent, when, name,
                              {"child_agent_instance_id": p.get("agent_id"), "child_agent_definition": p.get("agent_type"),
                               "task_hash": sha(p.get("agent_input", "")) if p.get("agent_input") else None},
                              correlation={"child_agent_instance_id": p.get("agent_id", "")}, versions=versions))
        elif name == "SubagentStop":
            parent = dict(p); parent.pop("agent_id", None); parent.pop("agent_type", None)
            last = p.get("last_assistant_message") or ""
            events.append(_mk(EventType.AGENT_RETURNED, parent, when, name,
                              {"child_agent_instance_id": p.get("agent_id"), "child_agent_definition": p.get("agent_type"), "status": "ok", "result_hash": sha(last) if last else None},
                              correlation={"child_agent_instance_id": p.get("agent_id", "")},
                              payload_refs={"result": PayloadRef.of(last)} if last else {}, versions=versions))
        elif name == "PreCompact":
            pending_compact[p["session_id"]] = {"when": when, "trigger": p.get("trigger"), "custom": bool(p.get("custom_instructions"))}
        elif name == "PostCompact":
            pre = pending_compact.pop(p["session_id"], {})
            summary = p.get("compact_summary") or ""
            attrs = {"trigger": p.get("trigger") or pre.get("trigger") or "unknown", "custom_instructions_present": pre.get("custom", None)}
            if pre.get("when"):
                attrs["duration_ms"] = int((ts(when) - ts(pre["when"])).total_seconds() * 1000)
            events.append(_mk(EventType.CONTEXT_COMPACT, p, when, name, attrs,
                              correlation={"turn_id": p.get("prompt_id", "")},
                              payload_refs={"summary": PayloadRef.of(summary)} if summary else {}, versions=versions))
        elif name == "Stop":
            last = p.get("last_assistant_message") or ""
            events.append(_mk(EventType.STOP, p, when, name,
                              {"reason": StopReason.AGENT_DECLARED_COMPLETE, "declared_by": "agent", "native_reason": "Stop"},
                              payload_refs={"final_message": PayloadRef.of(last)} if last else {}, versions=versions))
        elif name == "SessionEnd":
            reason = p.get("reason", "other")
            etype = EventType.RUN_COMPLETED if reason in ("other", "prompt_input_exit", "clear", "logout", "resume") else EventType.RUN_FAILED
            events.append(_mk(etype, p, when, name, {"stop_reason": StopReason.UNKNOWN, "terminal_reason": reason}, versions=versions))
        else:
            stats["unmapped"] += 1; stats["unmapped_names"][name] = stats["unmapped_names"].get(name, 0) + 1
            events.append(_mk(EventType.UNKNOWN, p, when, name, {"native": {k: v for k, v in p.items() if k not in ("transcript_path", "cwd", "scratchpad_dir")}}, versions=versions))
            continue
        stats["mapped"] += 1
    return events, stats
