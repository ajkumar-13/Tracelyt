"""Tally Gate A counters from desk-research case files.

Usage: python3 scripts/tally_discovery.py [docs/phase0/discovery/cases]
Parses the first ```yaml block of each case file (keys per 02-synthesis-template.md,
plus method, evidence_grade, tags) and prints a markdown counter table.
Deliberately tolerant: values are read as strings; nested keys are flattened with dots.
"""
from __future__ import annotations
import re, sys, pathlib, collections

ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "docs/phase0/discovery/cases")

def parse_yaml_block(text: str) -> dict:
    m = re.search(r"```yaml\n(.*?)```", text, re.S)
    if not m:
        return {}
    out, stack = {}, []
    for raw in m.group(1).splitlines():
        if not raw.strip() or raw.lstrip().startswith("#") or raw.lstrip().startswith("- "):
            continue
        indent = len(raw) - len(raw.lstrip())
        if ":" not in raw:
            continue
        key, _, val = raw.strip().partition(":")
        val = val.split("#")[0].strip().strip('"')
        while stack and stack[-1][0] >= indent:
            stack.pop()
        path = ".".join([s[1] for s in stack] + [key.strip()])
        if val == "":
            stack.append((indent, key.strip()))
        else:
            out[path] = val
    return out

def norm(v: str | None) -> str:
    v = (v or "unknown").lower()
    for k in ("yes", "no", "partial", "conditional", "maybe", "unknown"):
        if v.startswith(k):
            return k
    return v

cases = []
for f in sorted(ROOT.glob("*.md")):
    d = parse_yaml_block(f.read_text())
    grade = re.search(r"evidence_grade:\s*([ABC])", f.read_text())
    d["_file"] = f.name
    d["_grade"] = grade.group(1) if grade else d.get("evidence_grade", "?")[:1]
    d["_track"] = f.name.split("-")[0]
    cases.append(d)

def count(pred, subset=None):
    cs = cases if subset is None else [c for c in cases if c["_grade"] in subset]
    return sum(1 for c in cs if pred(c))

rows = [
    ("Cases filed", lambda c: True),
    ("Silent regression experienced (yes)", lambda c: norm(c.get("harness_change.silent_regression_experienced")) == "yes"),
    ("Would pay to prevent (yes, stated)", lambda c: norm(c.get("harness_change.would_pay_to_prevent")) == "yes"),
    ("Replay inside env OK (yes or conditional, stated)", lambda c: norm(c.get("data_constraints.replay_inside_env_ok")) in ("yes", "conditional")),
    ("Design-partner candidate (yes)", lambda c: norm(c.get("design_partner_candidate")) == "yes"),
    ("Design-partner candidate (yes or maybe)", lambda c: norm(c.get("design_partner_candidate")) in ("yes", "maybe")),
    ("Last failure attributed to non-model component", lambda c: c.get("last_failure.attributed_component", "unknown").lower() not in ("model", "unknown")),
    ("Last failure attributed to model", lambda c: c.get("last_failure.attributed_component", "").lower().startswith("model")),
    ("Coding-agent traces flow to an observability stack", lambda c: norm(c.get("coding_agent_traces_flow_to")) not in ("none", "unknown")),
    ("Can reproduce a failed run (yes)", lambda c: norm(c.get("can_reproduce_failed_run")) == "yes"),
    ("Has compared cohorts (yes)", lambda c: norm(c.get("has_compared_cohorts")) == "yes"),
    ("Would allow pause/stop on evidence (yes or conditional)", lambda c: norm(c.get("would_allow_pause_stop_on_evidence")) in ("yes", "conditional")),
]
print(f"| Counter | All ({len(cases)}) | A+B only ({count(lambda c: True, 'AB')}) | builder | fleet | vendor |")
print("|---|---|---|---|---|---|")
for name, pred in rows:
    by = {t: sum(1 for c in cases if c['_track'] == t and pred(c)) for t in ("builder", "fleet", "vendor")}
    print(f"| {name} | {count(pred)} | {count(pred, 'AB')} | {by['builder']} | {by['fleet']} | {by['vendor']} |")

print("\n**Attributed component distribution**")
dist = collections.Counter(c.get("last_failure.attributed_component", "unknown").lower() for c in cases)
print(", ".join(f"{k}: {v}" for k, v in dist.most_common()))
print("\n**Budget owner distribution**")
dist = collections.Counter(c.get("budget_owner", "unknown").lower() for c in cases)
print(", ".join(f"{k}: {v}" for k, v in dist.most_common()))
print("\n**Evidence grades**")
print(", ".join(f"{k}: {v}" for k, v in sorted(collections.Counter(c['_grade'] for c in cases).items())))
print("\n**Regression detection today**")
dist = collections.Counter(c.get("harness_change.regression_detection", "unknown").lower() for c in cases)
print(", ".join(f"{k}: {v}" for k, v in dist.most_common()))
