"""Recorder and replay-runner plumbing that needs no harness binary: workspace preparation, configuration hashing,
tree hashing, and pre-tree restoration from the archived snapshot."""
import json, os, sys, tarfile, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
from harness_engine.recorder.claude_code import prepare_workspace, config_hash, tree_hashes, HOOK_EVENTS
from harness_engine.replay.runner import reset_to_pre_tree


def test_prepare_workspace_writes_rules_hooks_and_files(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path / "home")); (tmp_path / "home").mkdir()
    ws = str(tmp_path / "ws")
    prepare_workspace(ws, files={"test_target.py": "x = 1\n"}, rules="# rules\n", agents={"reviewer": "---\nname: reviewer\n---\nreview\n"})
    settings = json.load(open(os.path.join(ws, ".claude", "settings.json")))
    assert set(settings["hooks"]) == set(HOOK_EVENTS)
    assert open(os.path.join(ws, "CLAUDE.md")).read() == "# rules\n"
    assert os.path.exists(os.path.join(ws, ".claude", "agents", "reviewer.md"))
    trust = json.load(open(tmp_path / "home" / ".claude.json"))
    assert trust["projects"][os.path.abspath(ws)]["hasTrustDialogAccepted"] is True
    assert sorted(tree_hashes(ws)) == ["CLAUDE.md", "test_target.py"]
    assert "QAR_CAPTURE_DIR" in open(os.path.join(ws, ".claude", "hookdump.sh")).read()


def test_config_hash_changes_with_rules_file_and_hooks(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path / "home")); (tmp_path / "home").mkdir()
    ws = str(tmp_path / "ws"); prepare_workspace(ws, rules="a\n")
    h1 = config_hash(ws)
    open(os.path.join(ws, "CLAUDE.md"), "w").write("b\n"); h2 = config_hash(ws)
    open(os.path.join(ws, "CLAUDE.md"), "w").write("a\n"); h3 = config_hash(ws)
    assert h1 != h2 and h1 == h3


def test_reset_to_pre_tree_restores_archived_snapshot(tmp_path):
    ws = tmp_path / "ws"; cap = ws / "captures"; (ws / ".claude").mkdir(parents=True); cap.mkdir()
    (ws / "target.py").write_text("v1\n"); (ws / "test_target.py").write_text("t\n")
    with tarfile.open(cap / "tree_pre.tar", "w") as tar:
        tar.add(ws / "test_target.py", arcname="test_target.py")
    (ws / "target.py").write_text("v2 written by the agent\n"); (ws / "extra.txt").write_text("junk\n")
    reset_to_pre_tree(str(ws), str(cap))
    assert sorted(tree_hashes(str(ws))) == ["test_target.py"]
    assert (ws / ".claude").is_dir() and (cap / "tree_pre.tar").exists()
