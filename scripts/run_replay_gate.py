"""Replay gate (SPEC-02 §11): replay every recorded cohort run N times and report the R2 share by cohort and by
expected outcome (failure runs are the gate's denominator: R2 on >= 80% of recorded failures).
Usage: python3 scripts/run_replay_gate.py --root <cohorts root> --claude BIN [--runs 3] [--out DIR]
"""
from __future__ import annotations
import argparse, json, os, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
from harness_engine.replay.runner import replay_run  # noqa: E402


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--root", required=True); ap.add_argument("--claude", default="claude")
    ap.add_argument("--runs", type=int, default=3); ap.add_argument("--out"); ap.add_argument("--only", default="")
    a = ap.parse_args(); out = a.out or os.path.join(a.root, "replay"); os.makedirs(out, exist_ok=True)
    rows = [json.loads(l) for l in open(os.path.join(a.root, "cohorts.jsonl"))]
    only = set(x for x in a.only.split(",") if x)
    results = []
    for r in rows:
        if only and r["label"] not in only: continue
        ws = os.path.join(a.root, "runs", r["label"])
        cap = next(c for c in (ws + ".recorded", ws + ".captures", os.path.join(ws, "captures")) if os.path.isdir(c))
        s = replay_run(cap, a.claude, os.path.join(out, r["label"]), runs=a.runs)
        s.update({"cohort": r["cohort"], "expect": r["expect"], "recorded_wall_s": r["wall_s"]})
        results.append(s); print(json.dumps({k: s[k] for k in ("label", "cohort", "expect", "model_calls", "r2", "tool_result_agreement", "extra_requests", "first_divergence", "wall_s")}), flush=True)
    by = {}
    for s in results:
        for key in (s["cohort"], "expect:" + s["expect"], "all"):
            d = by.setdefault(key, {"runs": 0, "r2": 0}); d["runs"] += 1; d["r2"] += int(s["r2"])
    summary = {k: {**v, "share": round(v["r2"] / v["runs"], 3)} for k, v in by.items()}
    gate = {"R2_on_failures": summary.get("expect:failure", {}).get("share"), "R2_on_successes": summary.get("expect:success", {}).get("share"),
            "gate_failures_ge_0.8": (summary.get("expect:failure", {}).get("share") or 0) >= 0.8}
    json.dump({"summary": summary, "gate": gate, "runs": results}, open(os.path.join(out, "replay_gate.json"), "w"), indent=1)
    print(json.dumps({"summary": summary, "gate": gate}, indent=1))


if __name__ == "__main__":
    main()
