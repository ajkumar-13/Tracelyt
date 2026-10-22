"""Replay one recorded run (recorder manifest + cassette) in its recorded workspace and measure agreement.

Generalizes scripts/run_proof_g.py: the pre-run tree and the harness flags come from the recorder manifest, so any
run recorded by harness_engine.recorder can be replayed with one call.
"""
from __future__ import annotations
import json, os, shutil, subprocess, tarfile, time, uuid

from .cassette import Cassette, _norm_block, canonical
from .server import ReplayServer
from ..recorder.claude_code import tree_hashes


def _tool_results(c: Cassette) -> dict:
    out = {}
    for e in c.envelopes:
        for m in e.request.get("messages", []):
            for b in (m.get("content") if isinstance(m.get("content"), list) else []):
                if isinstance(b, dict) and b.get("type") == "tool_result":
                    out[b["tool_use_id"]] = canonical(_norm_block(b))
    return out


def reset_to_pre_tree(ws: str, cap: str):
    """Restore the workspace to the recorded pre-run tree; keep .claude; move live captures aside."""
    for name in os.listdir(ws):
        if name in (".claude", "captures"): continue
        p = os.path.join(ws, name); shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    with tarfile.open(os.path.join(cap, "tree_pre.tar")) as tar:
        tar.extractall(ws)


def replay_run(capture_dir: str, claude_bin: str, out_dir: str, policy: str = "report", timeout: int = 600, runs: int = 1) -> dict:
    cap = os.path.abspath(capture_dir)
    man = json.load(open(os.path.join(cap, "manifest.json")))
    ws = man["workspace"]
    cassette_dir = os.path.join(cap, "rawbodies")
    results = []
    for i in range(1, runs + 1):
        run_out = os.path.join(out_dir, f"run{i}"); os.makedirs(run_out, exist_ok=True)
        live_cap = os.path.join(ws, "captures")
        if os.path.isdir(live_cap) and os.path.abspath(live_cap) != cap:
            shutil.rmtree(live_cap)
        if os.path.abspath(live_cap) == cap:                 # recording lives in the workspace: move it out first
            moved = os.path.join(out_dir, "recorded_captures")
            if not os.path.isdir(moved): shutil.move(cap, moved)
            cap = moved; cassette_dir = os.path.join(cap, "rawbodies")
        os.makedirs(live_cap, exist_ok=True)
        reset_to_pre_tree(ws, cap)
        cassette = Cassette.from_raw_bodies(cassette_dir)
        srv = ReplayServer(cassette, run_out, policy=policy).start()
        env = dict(os.environ); env.pop("ANTHROPIC_API_KEY", None)
        env.update({"ANTHROPIC_BASE_URL": srv.base_url, "OTEL_LOG_RAW_API_BODIES": f"file:{live_cap}/rawbodies",
                    "CLAUDE_CODE_ENABLE_TELEMETRY": "1", "OTEL_LOGS_EXPORTER": "none", "OTEL_METRICS_EXPORTER": "none"})
        sid = str(uuid.uuid4())
        cmd = [claude_bin, "-p", man["prompt"], "--model", man["model"], "--session-id", sid, "--output-format", "stream-json", "--verbose",
               "--max-turns", str(man.get("max_turns", 25)), "--permission-mode", man.get("permission_mode", "acceptEdits")]
        if man.get("allowed_tools"): cmd += ["--allowedTools", man["allowed_tools"]]
        t0 = time.time()
        with open(os.path.join(run_out, "stream.jsonl"), "w") as so, open(os.path.join(run_out, "stderr.log"), "w") as se:
            try:
                p = subprocess.run(cmd, cwd=ws, env=env, stdin=subprocess.DEVNULL, stdout=so, stderr=se, timeout=timeout); rc = p.returncode
            except subprocess.TimeoutExpired:
                rc = -1
        wall = time.time() - t0; srv.stop()
        ms = srv.matcher.summary()
        rec = _tool_results(cassette)
        rep_idx = os.path.join(live_cap, "rawbodies", "index.jsonl")
        rep = _tool_results(Cassette.from_raw_bodies(os.path.join(live_cap, "rawbodies"))) if os.path.exists(rep_idx) else {}
        agree = {k: rep.get(k) == v for k, v in rec.items()}
        final = tree_hashes(ws)
        result = next((json.loads(l) for l in reversed(open(os.path.join(run_out, "stream.jsonl")).readlines()) if '"type":"result"' in l), {})
        shutil.copytree(live_cap, os.path.join(run_out, "captures"), dirs_exist_ok=True)
        n = len(cassette.envelopes)
        served_ok = sum(v for k, v in ms["levels"].items() if k in ("exact", "normalized", "delta")) == n
        r = {"run": i, "exit_code": rc, "wall_s": round(wall, 1), "terminal_reason": result.get("terminal_reason"),
             "match": ms, "unmatched_endpoints": srv.unmatched_endpoints,
             "tool_results": {"recorded": len(rec), "agree": sum(agree.values()), "disagree": [k for k, v in agree.items() if not v]},
             "final_tree_agree": final == man["tree_post"], "final_tree": final,
             "r2": bool(ms["served"] == n and served_ok and final == man["tree_post"])}
        json.dump(r, open(os.path.join(run_out, "result.json"), "w"), indent=1)
        results.append(r)
    summary = {"label": man.get("label"), "session_id": man["session_id"], "model_calls": len(Cassette.from_raw_bodies(cassette_dir).envelopes),
               "recorded_terminal_reason": man.get("terminal_reason"), "runs": len(results),
               "r2_each": [r["r2"] for r in results], "r2": all(r["r2"] for r in results) and len({canonical(r["final_tree"]) for r in results}) == 1,
               "tool_result_agreement": [f'{r["tool_results"]["agree"]}/{r["tool_results"]["recorded"]}' for r in results],
               "levels": [r["match"]["levels"] for r in results], "extra_requests": [r["match"]["extra_requests"] for r in results],
               "first_divergence": [r["match"]["first_divergence_seq"] for r in results], "wall_s": [r["wall_s"] for r in results],
               "recorded_wall_s": man.get("wall_s"), "capture_dir": cap}
    json.dump({"summary": summary, "runs": results}, open(os.path.join(out_dir, "replay.json"), "w"), indent=1)
    return summary
