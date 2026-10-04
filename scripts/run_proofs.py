"""Run Proofs B-F on the captured fixtures and write docs/phase0/proofs/results.md plus results.json."""
from __future__ import annotations
import json, os, sys, collections
from harness_engine.normalize.claude_code import normalize_dir
from harness_engine.graph.builder import build_graph
from harness_engine.detectors.deterministic import run_all
from harness_engine.divergence.first_divergence import compare_cohorts
from harness_engine.model.events import EventType

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIX = os.path.join(ROOT, "tests", "fixtures", "claude_code")
RW = ("/work/proofE", os.path.join(FIX, "proofE"))


def load_cohorts():
    runs = {}
    for line in open(os.path.join(FIX, "proofE", "cohorts.tsv")):
        c, i, sid = line.strip().split("\t")
        d = os.path.join(FIX, "proofE", "runs", f"{c}-{i}")
        # OTLP batches are shared across runs; filter by session id
        tmp = os.path.join(FIX, "proofE")
        ev_hooks, st = normalize_dir(d, session_id=sid, path_rewrite=RW)
        # add otel logs for this session from the shared directory
        ev_otel, st2 = normalize_dir(tmp, session_id=sid, path_rewrite=RW)
        from harness_engine.normalize.merge import merge
        merged, _ = merge(ev_hooks + [e for e in ev_otel if e.source_channel.startswith("claude_code.otel")])
        from harness_engine.normalize.claude_code import _post
        runs[f"{c}-{i}"] = (c, sid, _post(merged), st)
    return runs


def main():
    out = {"proofs": {}}
    # Proof A/B on the full proof-A run
    evA, stA = normalize_dir(FIX, session_id="2514bbc3-9419-453a-a491-d07ac2cabfbf")
    gA = build_graph(evA)
    out["proofs"]["B_exception_rate_proofA"] = {"all_records": round(stA["v01_exception_rate"], 4), "excluding_hook_domain": round(stA["v01_exception_rate_excluding_hook_domain"], 4),
                                                "unmapped_names": {**stA["hooks"]["unmapped_names"], **stA["otel_logs"]["unmapped_names"]}}
    out["proofs"]["C_graph_proofA"] = {"nodes": len(gA.nodes), "edges": len(gA.edges), "fidelity": gA.fidelity, "reasons": gA.fidelity_reasons,
                                       "edges_by_rel_and_source": dict(collections.Counter(f"{e.rel}/{e.source.value}" for e in gA.edges))}
    # Proof D on proofD + cohorts
    dres = {}
    for line in open(os.path.join(FIX, "proofD", "sessions.txt")):
        name, sid = line.strip().split("=")
        ev, st = normalize_dir(os.path.join(FIX, "proofD"), session_id=sid)
        f = run_all(ev); g = build_graph(ev)
        dres[f"proofD/{name}"] = {"findings": sorted({x.detector_id for x in f}), "detail": [x.summary for x in f], "fidelity": g.fidelity, "exception_rate_excl_hook": round(st["v01_exception_rate_excluding_hook_domain"], 4)}
    runs = load_cohorts()
    cohort_findings = collections.defaultdict(list)
    for name, (c, sid, ev, st) in runs.items():
        f = run_all(ev); g = build_graph(ev)
        dres[f"proofE/{name}"] = {"cohort": c, "findings": sorted({x.detector_id for x in f}), "detail": [x.summary for x in f], "fidelity": g.fidelity, "n_events": len(ev)}
        cohort_findings[c].append({x.detector_id for x in f})
    out["proofs"]["D_detectors"] = dres
    # precision on control cohort S: any finding is a false positive
    fp_runs = sum(1 for s in cohort_findings["S"] if s); out["proofs"]["D_control_false_positive_runs"] = f"{fp_runs}/{len(cohort_findings['S'])}"
    out["proofs"]["D_F1_runs_with_D6"] = f"{sum(1 for s in cohort_findings['F1'] if 'D6' in s)}/{len(cohort_findings['F1'])}"
    out["proofs"]["D_F1_runs_with_D7"] = f"{sum(1 for s in cohort_findings['F1'] if 'D7' in s)}/{len(cohort_findings['F1'])}"
    # Proof E/F: divergence S vs F1 and S vs F2
    S = [ev for (c, sid, ev, st) in runs.values() if c == "S"]
    for fault, expected in (("F1", "permission"), ("F2", "context_builder")):
        Fr = [ev for (c, sid, ev, st) in runs.values() if c == fault]
        rep = compare_cohorts(Fr, S)
        out["proofs"][f"EF_{fault}"] = {"expected_root_component": expected, "primary_component": rep.primary_component.value if rep.primary_component else None,
                                        "mechanism_component": rep.mechanism_component.value if rep.mechanism_component else None, "confidence": rep.primary_confidence,
                                        "candidates": rep.candidates[:3], "upstream_differences": rep.upstream_differences, "explanation": rep.explanation,
                                        "top1_correct": (rep.primary_component.value == expected) if rep.primary_component else False,
                                        "top3_correct": expected in [c["component"] for c in rep.candidates[:3]] + [u["component"] for u in rep.upstream_differences]}
    # Leave-one-out per failed run: can a single failed run be localized against the success cohort?
    loo = {}
    for fault, expected in (("F1", "permission"), ("F2", "context_builder")):
        hits = 0; n = 0
        for name, (c, sid, ev, st) in runs.items():
            if c != fault: continue
            rep = compare_cohorts([ev], S); n += 1
            comps = ([rep.primary_component.value] if rep.primary_component else []) + [x["component"] for x in rep.candidates[:3]]
            hits += expected in comps
        loo[fault] = f"{hits}/{n}"
    out["proofs"]["F_single_run_top3_localization"] = loo
    os.makedirs(os.path.join(ROOT, "docs", "phase0", "proofs"), exist_ok=True)
    json.dump(out, open(os.path.join(ROOT, "docs", "phase0", "proofs", "results.json"), "w"), indent=1, default=str)
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
