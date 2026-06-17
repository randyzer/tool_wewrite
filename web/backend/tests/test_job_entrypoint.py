from pathlib import Path

ENTRY = Path(__file__).resolve().parents[1] / "docker" / "job_entrypoint.py"

def _load():
    import importlib.util
    spec = importlib.util.spec_from_file_location("job_entrypoint", ENTRY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def test_setup_skill_links(tmp_path):
    mod = _load()
    skill = tmp_path / "skill"; skill.mkdir()
    for name in ["SKILL.md", "toolkit", "references"]:
        (skill / name).mkdir() if name != "SKILL.md" else (skill / name).write_text("x")
    (skill / ".venv").mkdir()  # 宿主 venv：容器内不可链
    ws = tmp_path / "ws"; ws.mkdir()
    mod.setup_workspace_skill_links(ws, skill)
    assert (ws / "SKILL.md").is_symlink()
    assert (ws / "toolkit").is_symlink()
    assert (ws / ".home").is_dir()
    assert not (ws / ".venv").exists()  # 不链宿主 .venv，用容器内 python

def test_emit_writes_jsonl(capsys):
    mod = _load()
    mod.emit({"type": "log", "text": "hi"})
    out = capsys.readouterr().out.strip()
    import json
    assert json.loads(out) == {"type": "log", "text": "hi"}
