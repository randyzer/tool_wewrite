from app.config import Settings
from app.store import Account
from app.workspace import build_workspace, cleanup_workspace

def _account():
    return Account(user_id="u")

def test_container_mode_skips_skill_symlinks(monkeypatch):
    monkeypatch.setenv("WEWRITE_RUNNER", "container")
    ws = build_workspace(Settings(), _account(), theme="professional-clean", persona="midnight-friend")
    try:
        # 容器模式：不建 skill 软链（容器入口建指向 /skill），但写可写文件
        for name in ("SKILL.md", "toolkit", "scripts", "references", "personas", ".venv"):
            assert not (ws / name).exists() and not (ws / name).is_symlink(), f"{name} 不该在容器模式工作区出现"
        assert (ws / "output").is_dir()
        assert (ws / "history.yaml").is_file()
        assert (ws / "style.yaml").is_file()
        assert (ws / "config.yaml").is_file()
    finally:
        cleanup_workspace(ws)

def test_direct_mode_creates_skill_symlinks(monkeypatch):
    monkeypatch.setenv("WEWRITE_RUNNER", "direct")
    ws = build_workspace(Settings(), _account(), theme="professional-clean", persona="midnight-friend")
    try:
        # direct 模式：软链宿主 skill 代码（SKILL.md 一定存在于仓库根）
        assert (ws / "SKILL.md").is_symlink()
        assert (ws / "output").is_dir()
    finally:
        cleanup_workspace(ws)
