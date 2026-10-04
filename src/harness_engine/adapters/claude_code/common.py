"""Shared helpers for the Claude Code Tier B adapter."""
from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from typing import Any

from harness_engine.model.events import SideEffectClass

HARNESS = "claude-code"
CHANNEL_HOOKS = "claude_code.hooks"
CHANNEL_OTEL = "claude_code.otel_logs"
CHANNEL_STREAM = "claude_code.sdk_stream"

# Builtin tool side-effect classes. Bash is classified by its binary; unknown binaries stay UNKNOWN.
BUILTIN_SIDE_EFFECTS = {
    "Read": SideEffectClass.READ_ONLY, "Glob": SideEffectClass.READ_ONLY, "Grep": SideEffectClass.READ_ONLY,
    "WebFetch": SideEffectClass.READ_ONLY, "WebSearch": SideEffectClass.READ_ONLY,
    "Write": SideEffectClass.REVERSIBLE_WRITE, "Edit": SideEffectClass.REVERSIBLE_WRITE,
    "NotebookEdit": SideEffectClass.REVERSIBLE_WRITE,
    "Task": SideEffectClass.UNKNOWN, "TodoWrite": SideEffectClass.READ_ONLY,
}
READ_ONLY_BINARIES = {"ls", "cat", "head", "tail", "grep", "rg", "find", "wc", "echo", "pwd", "git status", "git log", "git diff", "pytest", "python3 -m pytest"}
IRREVERSIBLE_BINARIES = {"rm", "git push", "terraform", "kubectl delete", "dd", "mkfs", "shred", "drop"}


def sha(obj: Any) -> str:
    if isinstance(obj, (dict, list)):
        obj = json.dumps(obj, sort_keys=True, default=str)
    if isinstance(obj, str):
        obj = obj.encode()
    return hashlib.sha256(obj).hexdigest()


def ts(s: str | None) -> datetime:
    if not s:
        return datetime.now(timezone.utc)
    s = s.replace("Z", "+00:00")
    # trim nanoseconds to microseconds for fromisoformat
    if "." in s:
        head, rest = s.split(".", 1)
        frac = rest.split("+")[0]
        tz = rest[len(frac):]
        s = f"{head}.{frac[:6]}{tz}"
    d = datetime.fromisoformat(s)
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def otlp_attrs(lst: list[dict]) -> dict[str, Any]:
    """Flatten OTLP KeyValue list into a python dict."""
    out: dict[str, Any] = {}
    for kv in lst or []:
        v = kv.get("value", {})
        if "stringValue" in v: out[kv["key"]] = v["stringValue"]
        elif "intValue" in v: out[kv["key"]] = int(v["intValue"])
        elif "doubleValue" in v: out[kv["key"]] = float(v["doubleValue"])
        elif "boolValue" in v: out[kv["key"]] = bool(v["boolValue"])
        elif "arrayValue" in v: out[kv["key"]] = [list(x.values())[0] for x in v["arrayValue"].get("values", [])]
        else: out[kv["key"]] = v
    return out


def bash_side_effect(command: str | None) -> tuple[SideEffectClass, str | None]:
    if not command:
        return SideEffectClass.UNKNOWN, None
    cmd = command.strip()
    binary = cmd.split()[0] if cmd else None
    low = cmd.lower()
    for b in IRREVERSIBLE_BINARIES:
        if low.startswith(b) or f" {b} " in f" {low} " or f"&& {b}" in low or f"| {b}" in low:
            return SideEffectClass.IRREVERSIBLE_WRITE, binary
    for b in READ_ONLY_BINARIES:
        if low.startswith(b):
            return SideEffectClass.READ_ONLY, binary
    return SideEffectClass.UNKNOWN, binary


def coerce_bool(v: Any) -> bool | None:
    if isinstance(v, bool): return v
    if isinstance(v, str): return v.lower() == "true"
    return None


def coerce_int(v: Any) -> int | None:
    try: return int(v)
    except (TypeError, ValueError): return None
