"""Phase 0 gate criteria (PLAN-04 Phase 0 exit) encoded as tests over the real captured fixtures."""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _results():
    subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "run_proofs.py")], check=True, capture_output=True)
    return json.load(open(os.path.join(ROOT, "docs", "phase0", "proofs", "results.json")))["proofs"]


def test_gate_proof_b_exception_rate_under_10_percent():
    r = _results()["B_exception_rate_proofA"]
    assert r["excluding_hook_domain"] < 0.10, r


def test_gate_proof_c_graph_fidelity_at_least_g3_on_proof_a_run():
    r = _results()["C_graph_proofA"]
    assert r["fidelity"] in ("G3", "G4", "G5"), r


def test_gate_proof_d_detectors_zero_false_positives_on_control_cohort():
    r = _results()
    assert r["D_control_false_positive_runs"].startswith("0/"), r["D_control_false_positive_runs"]
    assert set(r["D_detectors"]["proofD/loop"]["findings"]) >= {"D1", "D3", "D4"}, r["D_detectors"]["proofD/loop"]
    assert r["D_F1_runs_with_D6"] == "5/5"


def test_gate_proof_f_injected_divergence_found_top3_in_at_least_70_percent():
    r = _results()
    hits = total = 0
    for fault, v in r["F_single_run_top3_localization"].items():
        h, t = map(int, v.split("/")); hits += h; total += t
    assert hits / total >= 0.70, r["F_single_run_top3_localization"]
    assert r["EF_F1"]["top1_correct"] and r["EF_F2"]["top1_correct"]
