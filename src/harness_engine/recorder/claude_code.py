"""Recorder wrapper for Claude Code (Tier B, SPEC-06): one call records a run with every channel the replay and
graph need, into a single capture directory, with a manifest that pins what SPEC-02 §2 says a replay must pin.

Channels: hooks (stdin JSON dumped per event), OTLP logs and metrics (in-process receiver), the raw-body side
channel (`OTEL_LOG_RAW_API_BODIES=file:`), the Agent SDK stream (`--output-format stream-json`), stderr, plus
pre- and post-run workspace trees for state agreement checks.
"""
from __future__ import annotations
import gzip, hashlib, json, os, shutil, subprocess, tarfile, threading, time, uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Optional

HOOK_EVENTS = ["SessionStart", "InstructionsLoaded", "UserPromptSubmit", "PreToolUse", "PermissionRequest", "PermissionDenied",
               "PostToolUse", "PostToolUseFailure", "SubagentStart", "SubagentStop", "Stop", "PreCompact", "PostCompact", "SessionEnd"]
HOOKDUMP = '''#!/usr/bin/env bash
# Append the raw stdin JSON for every hook event, tagged with the event name from argv[1].
# Captures go to $QAR_CAPTURE_DIR (inherited by hook subprocesses; OTEL_* variables are not), outside the
# workspace so the agent's own tools never see the recorder's files. Fallback: ./captures inside the workspace.
d="$(cat)"
out="${QAR_CAPTURE_DIR:-$CLAUDE_PROJECT_DIR/captures}"; mkdir -p "$out"
printf '{"_hook":"%s","_ts":"%s","_pid":%s,"payload":%s}\\n' "$1" "$(date -u +%Y-%m-%dT%H:%M:%S.%NZ)" "$$" "$d" >> "$out/hooks.jsonl"
exit 0
'''
IGNORE_TREE = ("captures", "captures_recorded", "__pycache__", ".claude", ".pytest_cache")


def tree_hashes(d: str, ignore=IGNORE_TREE) -> dict:
    out = {}
    for root, dirs, files in os.walk(d):
        dirs[:] = [x for x in dirs if x not in ignore]
        for f in files:
            if f in ignore: continue
            p = os.path.join(root, f)
            out[os.path.relpath(p, d)] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


class OTLPReceiver:
    """Minimal OTLP/HTTP JSON receiver: writes each batch to <out>/<signal>-NNNN.json."""
    def __init__(self, out: str, host: str = "127.0.0.1", port: int = 0):
        os.makedirs(out, exist_ok=True)
        self.out, self.n = out, {}
        rec = self

        class H(BaseHTTPRequestHandler):
            def log_message(self, *a): pass

            def do_POST(self):
                ln = int(self.headers.get("Content-Length", 0)); body = self.rfile.read(ln)
                if self.headers.get("Content-Encoding") == "gzip": body = gzip.decompress(body)
                sig = self.path.strip("/").split("/")[-1]; rec.n[sig] = rec.n.get(sig, 0) + 1
                ext = "json" if "json" in self.headers.get("Content-Type", "") else "bin"
                open(f"{rec.out}/{sig}-{rec.n[sig]:04d}.{ext}", "wb").write(body)
                self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers(); self.wfile.write(b"{}")

        self.httpd = ThreadingHTTPServer((host, port), H)
        self.port = self.httpd.server_address[1]
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)

    def start(self): self.thread.start(); return self

    def stop(self): self.httpd.shutdown(); self.httpd.server_close()


def ensure_trust(workspace: str):
    """Headless runs ignore project settings in an untrusted directory; mark it trusted in ~/.claude.json."""
    p = os.path.expanduser("~/.claude.json")
    d = json.load(open(p)) if os.path.exists(p) else {}
    d.setdefault("projects", {}).setdefault(os.path.abspath(workspace), {})["hasTrustDialogAccepted"] = True
    json.dump(d, open(p, "w"), indent=1)


def prepare_workspace(workspace: str, files: dict[str, str] | None = None, rules: str | None = None,
                      hook_events: list[str] = HOOK_EVENTS, agents: dict[str, str] | None = None, clean: bool = True):
    """Create the pre-run tree: project files, rules file, hook configuration, agent definitions."""
    if clean and os.path.isdir(workspace): shutil.rmtree(workspace)
    os.makedirs(os.path.join(workspace, ".claude"), exist_ok=True)
    for rel, content in (files or {}).items():
        p = os.path.join(workspace, rel); os.makedirs(os.path.dirname(p), exist_ok=True); open(p, "w").write(content)
    if rules is not None: open(os.path.join(workspace, "CLAUDE.md"), "w").write(rules)
    hd = os.path.join(workspace, ".claude", "hookdump.sh"); open(hd, "w").write(HOOKDUMP); os.chmod(hd, 0o755)
    hooks = {e: [{"hooks": [{"type": "command", "command": f'"$CLAUDE_PROJECT_DIR"/.claude/hookdump.sh {e}', "timeout": 10}]}] for e in hook_events}
    json.dump({"hooks": hooks}, open(os.path.join(workspace, ".claude", "settings.json"), "w"), indent=1)
    for name, body in (agents or {}).items():
        ad = os.path.join(workspace, ".claude", "agents"); os.makedirs(ad, exist_ok=True); open(os.path.join(ad, f"{name}.md"), "w").write(body)
    ensure_trust(workspace)


def config_hash(workspace: str) -> str:
    """Hash of the harness configuration the customer controls: rules file, settings, hooks, agents."""
    h = hashlib.sha256()
    for rel in sorted(["CLAUDE.md"] + [os.path.join(".claude", f) for f in sorted(os.listdir(os.path.join(workspace, ".claude")))]):
        p = os.path.join(workspace, rel)
        if os.path.isfile(p): h.update(rel.encode()); h.update(open(p, "rb").read())
        elif os.path.isdir(p):
            for f in sorted(os.listdir(p)): h.update(f.encode()); h.update(open(os.path.join(p, f), "rb").read())
    return h.hexdigest()


def record(workspace: str, prompt: str, model: str, claude_bin: str = "claude", allowed_tools: str | None = None,
           permission_mode: str = "acceptEdits", max_turns: int = 25, timeout: int = 600, session_id: str | None = None,
           extra_env: dict | None = None, label: str = "", capture_dir: str | None = None) -> dict:
    """Run one headless Claude Code session with every capture channel on. Returns and writes the manifest.
    Captures default to `<workspace>.captures`, a sibling directory: nothing of the recorder's is visible to the agent."""
    ws = os.path.abspath(workspace); cap = os.path.abspath(capture_dir or ws.rstrip("/") + ".captures"); os.makedirs(cap, exist_ok=True)
    pre = tree_hashes(ws); json.dump(pre, open(os.path.join(cap, "tree_pre.json"), "w"), indent=1)
    # The pre-run tree is archived, not copied as files: a loose copy inside the workspace is visible to the agent's
    # own tools (pytest collected the duplicate test module in the first smoke recording).
    with tarfile.open(os.path.join(cap, "tree_pre.tar"), "w") as tar:
        for rel in pre: tar.add(os.path.join(ws, rel), arcname=rel)
    rx = OTLPReceiver(os.path.join(cap, "otlp")).start()
    sid = session_id or str(uuid.uuid4())
    env = dict(os.environ); env.pop("ANTHROPIC_API_KEY", None)
    env.update({"CLAUDE_CODE_ENABLE_TELEMETRY": "1", "OTEL_LOGS_EXPORTER": "otlp", "OTEL_METRICS_EXPORTER": "otlp",
                "OTEL_EXPORTER_OTLP_PROTOCOL": "http/json", "OTEL_EXPORTER_OTLP_ENDPOINT": f"http://127.0.0.1:{rx.port}",
                "OTEL_LOG_TOOL_DETAILS": "1", "OTEL_LOG_USER_PROMPTS": "1", "OTEL_LOGS_EXPORT_INTERVAL": "1000",
                "OTEL_METRIC_EXPORT_INTERVAL": "2000", "OTEL_LOG_RAW_API_BODIES": f"file:{cap}/rawbodies", "QAR_CAPTURE_DIR": cap})
    env.update(extra_env or {})
    cmd = [claude_bin, "-p", prompt, "--model", model, "--session-id", sid, "--output-format", "stream-json", "--verbose",
           "--max-turns", str(max_turns), "--permission-mode", permission_mode]
    if allowed_tools: cmd += ["--allowedTools", allowed_tools]
    t0 = time.time(); timed_out = False
    with open(os.path.join(cap, "stream.jsonl"), "w") as so, open(os.path.join(cap, "stderr.log"), "w") as se:
        try:
            p = subprocess.run(cmd, cwd=ws, env=env, stdin=subprocess.DEVNULL, stdout=so, stderr=se, timeout=timeout); rc = p.returncode
        except subprocess.TimeoutExpired:
            rc, timed_out = -1, True
    time.sleep(3); rx.stop()                                   # let the last OTLP batches flush
    post = tree_hashes(ws); json.dump(post, open(os.path.join(cap, "tree_post.json"), "w"), indent=1)
    version = subprocess.run([claude_bin, "--version"], capture_output=True, text=True).stdout.strip().split()[0]
    init = next((json.loads(l) for l in open(os.path.join(cap, "stream.jsonl")) if '"subtype":"init"' in l), {})
    result = next((json.loads(l) for l in reversed(open(os.path.join(cap, "stream.jsonl")).readlines()) if '"type":"result"' in l), {})
    betas, entry = None, None
    idx = os.path.join(cap, "rawbodies", "index.jsonl")
    if os.path.exists(idx):
        first = json.loads(open(idx).readline())
        req = json.load(open(os.path.join(cap, "rawbodies", first["request_file"])))
        betas = req.get("betas"); sysb = req.get("system")
        if isinstance(sysb, list) and sysb and "cc_entrypoint=" in sysb[0].get("text", ""):
            entry = sysb[0]["text"].split("cc_entrypoint=")[1].split(";")[0]
    manifest = {"label": label, "session_id": sid, "workspace": ws, "capture_dir": cap, "prompt": prompt, "model": model, "harness": f"claude-code@{version}",
                "entrypoint": entry or init.get("startup_timing", {}).get("entrypoint"), "api_key_source": init.get("apiKeySource"),
                "permission_mode": permission_mode, "allowed_tools": allowed_tools, "max_turns": max_turns, "api_betas": betas,
                "harness_config_hash": config_hash(ws), "started_at": t0, "wall_s": round(time.time() - t0, 1), "exit_code": rc,
                "timed_out": timed_out, "terminal_reason": result.get("terminal_reason"), "num_turns": result.get("num_turns"),
                "is_error": result.get("is_error"), "cost_usd": result.get("total_cost_usd"),
                "model_calls": sum(1 for _ in open(idx)) if os.path.exists(idx) else 0,
                "tree_pre": pre, "tree_post": post, "channels": ["hooks", "otlp_logs", "otlp_metrics", "raw_bodies", "stream", "stderr"]}
    json.dump(manifest, open(os.path.join(cap, "manifest.json"), "w"), indent=1)
    return manifest
