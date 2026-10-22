"""Proof G: frozen self-replay of a recorded Claude Code run at R2 (SPEC-02 §5, §11).

Serves the recorded model responses from the raw-body cassette by S1 match, lets the harness execute its
tools live in the recorded workspace path (reset to its pre-run tree), and checks:
  - fixture coverage (every recorded model call served, no unmatched endpoints)
  - request-level agreement (exact / normalized / miss, with first divergence)
  - tool-result agreement (the tool_result content the harness sent back vs the recorded one; this is the
    shell/file state agreement that R3 measures, observed through the model boundary)
  - final workspace agreement (sha256 of the files the run produced)
Usage:
  python3 scripts/run_proof_g.py --cassette <rawbodies dir> --workspace <recorded cwd> --recorded-final <dir>
      --claude <claude binary> --runs 3 --out <out dir> [--policy report|strict]
"""
from __future__ import annotations
import argparse, hashlib, json, os, shutil, subprocess, sys, time, uuid

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
from harness_engine.replay.cassette import Cassette, _norm_block, canonical, sha  # noqa: E402
from harness_engine.replay.server import ReplayServer  # noqa: E402

PRE_STATE_KEEP = {"CLAUDE.md", ".claude", "otlp_receiver.py", "schema"}   # the recorded workspace's pre-run tree


def tree_hash(d: str, ignore=("captures", "__pycache__", ".claude", "otlp_receiver.py", "schema")) -> dict:
    out = {}
    for root, dirs, files in os.walk(d):
        dirs[:] = [x for x in dirs if x not in ignore]
        for f in files:
            if f in ignore: continue
            p = os.path.join(root, f)
            out[os.path.relpath(p, d)] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


def reset_workspace(ws: str, run_out: str):
    for name in os.listdir(ws):
        if name in PRE_STATE_KEEP: continue
        p = os.path.join(ws, name)
        if name == "captures":
            shutil.move(p, os.path.join(run_out, "captures_prev")); continue
        shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    os.makedirs(os.path.join(ws, "captures"), exist_ok=True)


def recorded_tool_results(c: Cassette) -> dict:
    """tool_use_id -> normalized recorded tool_result content, from the recorded requests."""
    out = {}
    for e in c.envelopes:
        for m in e.request.get("messages", []):
            for b in (m.get("content") if isinstance(m.get("content"), list) else []):
                if isinstance(b, dict) and b.get("type") == "tool_result":
                    out[b["tool_use_id"]] = canonical(_norm_block(b))
    return out


def replay_tool_results(cassette_dir: str) -> dict:
    if not os.path.exists(os.path.join(cassette_dir, "index.jsonl")): return {}
    return recorded_tool_results(Cassette.from_raw_bodies(cassette_dir))


def one_run(a, i: int, prompt: str) -> dict:
    run_out = os.path.join(a.out, f"run{i}"); os.makedirs(run_out, exist_ok=True)
    reset_workspace(a.workspace, run_out)
    cassette = Cassette.from_raw_bodies(a.cassette)
    srv = ReplayServer(cassette, run_out, policy=a.policy).start()
    env = dict(os.environ)
    env.update({"ANTHROPIC_BASE_URL": srv.base_url,
                "OTEL_LOG_RAW_API_BODIES": f"file:{a.workspace}/captures/rawbodies",
                "CLAUDE_CODE_ENABLE_TELEMETRY": "1", "OTEL_LOGS_EXPORTER": "none", "OTEL_METRICS_EXPORTER": "none",
                "CLAUDE_CODE_SESSION_ID": str(uuid.uuid4())})
    if a.env_mode == "apikey":                           # plain API-key harness configuration
        env["ANTHROPIC_API_KEY"] = "replay-no-key"
        for k in list(env):
            if k in ("CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST", "CLAUDE_CODE_USE_CCR_V2", "CLAUDE_CODE_REMOTE_SDK_URL"):
                env.pop(k)
    else:                                                 # "inherit": keep the recording's host configuration
        env.pop("ANTHROPIC_API_KEY", None)
    sid = str(uuid.uuid4())
    cmd = [a.claude, "-p", prompt, "--model", a.model, "--output-format", "stream-json", "--verbose", "--max-turns", "25",
           "--permission-mode", "acceptEdits", "--session-id", sid]
    t0 = time.time()
    with open(os.path.join(run_out, "stream.jsonl"), "w") as so, open(os.path.join(run_out, "stderr.log"), "w") as se:
        p = subprocess.run(cmd, cwd=a.workspace, env=env, stdin=subprocess.DEVNULL, stdout=so, stderr=se, timeout=a.timeout)
    wall = time.time() - t0
    srv.stop()
    ms = srv.matcher.summary()
    rec = recorded_tool_results(cassette)
    rep = replay_tool_results(os.path.join(a.workspace, "captures", "rawbodies"))
    tool_agree = {k: (rep.get(k) == v) for k, v in rec.items()}
    final = tree_hash(a.workspace)
    recorded_final = tree_hash(a.recorded_final)
    shutil.copytree(os.path.join(a.workspace, "captures"), os.path.join(run_out, "captures"), dirs_exist_ok=True)
    res = {"run": i, "session_id": sid, "exit_code": p.returncode, "wall_s": round(wall, 1), "match": ms,
           "unmatched_endpoints": srv.unmatched_endpoints,
           "tool_results": {"recorded": len(rec), "replayed_seen": len(rep), "agree": sum(tool_agree.values()),
                            "disagree": [k for k, v in tool_agree.items() if not v]},
           "final_tree": final, "recorded_final_tree": recorded_final, "final_tree_agree": final == recorded_final}
    json.dump(res, open(os.path.join(run_out, "result.json"), "w"), indent=1)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cassette", required=True); ap.add_argument("--workspace", required=True)
    ap.add_argument("--recorded-final", required=True); ap.add_argument("--claude", default="claude")
    ap.add_argument("--model", default="claude-haiku-4-5-20251001"); ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--out", required=True); ap.add_argument("--policy", default="report"); ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--env-mode", default="inherit", choices=["inherit", "apikey"])
    ap.add_argument("--prompt-from-hooks", required=True, help="hooks.jsonl of the recording (first UserPromptSubmit)")
    a = ap.parse_args()
    prompt = next(json.loads(l)["payload"]["prompt"] for l in open(a.prompt_from_hooks) if '"UserPromptSubmit"' in l)
    os.makedirs(a.out, exist_ok=True)
    results = [one_run(a, i, prompt) for i in range(1, a.runs + 1)]
    n = len(Cassette.from_raw_bodies(a.cassette).envelopes)
    summary = {
        "cassette_envelopes": n, "runs": len(results),
        "coverage_all_runs": all(r["match"]["served"] == n and not r["unmatched_endpoints"] for r in results),
        "request_levels": [r["match"]["levels"] for r in results],
        "first_divergence": [r["match"]["first_divergence_seq"] for r in results],
        "tool_result_agreement": [f'{r["tool_results"]["agree"]}/{r["tool_results"]["recorded"]}' for r in results],
        "final_tree_agree": [r["final_tree_agree"] for r in results],
        "identical_across_runs": len({canonical(r["final_tree"]) for r in results}) == 1,
        "exit_codes": [r["exit_code"] for r in results], "wall_s": [r["wall_s"] for r in results],
    }
    served_levels_ok = all(sum(v for k, v in x.items() if k in ("exact", "normalized", "delta")) == n for x in summary["request_levels"])
    summary["config_drift"] = [{"calls": r["match"]["config_drift_calls"], "paths": r["match"]["config_drift_paths"]} for r in results]
    summary["extra_requests"] = [r["match"]["extra_requests"] for r in results]
    r2 = summary["coverage_all_runs"] and served_levels_ok and all(summary["final_tree_agree"]) and summary["identical_across_runs"] and len(results) >= 3
    summary["R2_frozen_self_replay"] = "pass" if r2 else "fail"
    summary["R2_note"] = ("new-input agreement on every served call; harness configuration drift reported separately"
                          if r2 and any(c["calls"] for c in summary["config_drift"]) else "")
    json.dump({"summary": summary, "runs": results}, open(os.path.join(a.out, "proof_g.json"), "w"), indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
