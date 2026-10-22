"""qar: record and replay agent runs (Phase 1 CLI stub; name per D-043).

  qar record  --workspace DIR --prompt TEXT [--model M] [--allowed-tools T] [--rules FILE] [--claude BIN] [--label L]
  qar replay  --capture DIR [--claude BIN] [--runs N] [--out DIR] [--policy report|strict]
"""
from __future__ import annotations
import argparse, json, os, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
from harness_engine.recorder.claude_code import prepare_workspace, record  # noqa: E402
from harness_engine.replay.runner import replay_run  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser(prog="qar"); sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("record"); r.add_argument("--workspace", required=True); r.add_argument("--prompt", required=True)
    r.add_argument("--model", default="claude-haiku-4-5-20251001"); r.add_argument("--allowed-tools"); r.add_argument("--rules")
    r.add_argument("--claude", default="claude"); r.add_argument("--label", default=""); r.add_argument("--max-turns", type=int, default=25)
    r.add_argument("--permission-mode", default="acceptEdits"); r.add_argument("--no-prepare", action="store_true")
    p = sub.add_parser("replay"); p.add_argument("--capture", required=True); p.add_argument("--claude", default="claude")
    p.add_argument("--runs", type=int, default=1); p.add_argument("--out", required=True); p.add_argument("--policy", default="report")
    a = ap.parse_args(argv)
    if a.cmd == "record":
        if not a.no_prepare:
            prepare_workspace(a.workspace, rules=open(a.rules).read() if a.rules else None, clean=False)
        m = record(a.workspace, a.prompt, a.model, claude_bin=a.claude, allowed_tools=a.allowed_tools, max_turns=a.max_turns,
                   permission_mode=a.permission_mode, label=a.label)
        print(json.dumps({k: m[k] for k in ("label", "session_id", "harness", "entrypoint", "model_calls", "terminal_reason", "exit_code", "wall_s")}))
    else:
        s = replay_run(a.capture, a.claude, a.out, policy=a.policy, runs=a.runs)
        print(json.dumps(s, indent=1))


if __name__ == "__main__":
    main()
