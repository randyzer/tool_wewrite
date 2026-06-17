import shutil
import subprocess
import asyncio
import json
import uuid
from pathlib import Path
import pytest


def _docker_up() -> bool:
    if shutil.which("docker") is None:
        return False
    try:
        return subprocess.run(["docker", "info"], capture_output=True, timeout=5).returncode == 0
    except Exception:  # noqa: BLE001 - daemon hung/unreachable → treat as unavailable
        return False


pytestmark = pytest.mark.skipif(not _docker_up(), reason="docker daemon not available")

FAKE_DOCKERFILE = """
FROM python:3.11-slim
COPY entry.py /entry.py
ENTRYPOINT ["python", "/entry.py"]
"""
FAKE_ENTRY = '''
import json, sys, pathlib
print(json.dumps({"type":"assistant_text","text":"[1/8] fake"}), flush=True)
print(json.dumps({"type":"result_meta","completion":"DONE","num_turns":1}), flush=True)
out = pathlib.Path("/workspace/output"); out.mkdir(exist_ok=True)
(out/"article.md").write_text("# 假成稿\\n\\n内容。", encoding="utf-8")
'''

def test_container_runner_streams_and_collects(tmp_path, monkeypatch):
    # 唯一 tag + 收尾删除，避免并行 CI 撞 tag / 镜像层堆积
    tag = f"wewrite-job-fake-{uuid.uuid4().hex[:8]}"
    ctx = tmp_path / "ctx"; ctx.mkdir()
    (ctx / "Dockerfile").write_text(FAKE_DOCKERFILE)
    (ctx / "entry.py").write_text(FAKE_ENTRY)
    assert subprocess.run(["docker", "build", "-t", tag, str(ctx)],
                          capture_output=True).returncode == 0
    try:
        monkeypatch.setenv("WEWRITE_JOB_IMAGE", tag)
        monkeypatch.setenv("WEWRITE_JOB_NETWORK", "bridge")
        from app.config import Settings
        from app.runners.container import ContainerRunner
        from app.job_spec import JobSpec

        ws = tmp_path / "ws"; ws.mkdir()
        events = []
        spec = JobSpec(kind="generate", prompt="x")
        r = ContainerRunner(Settings())
        asyncio.run(r.run(settings=Settings(), spec=spec, profiles=[], ws=ws, env={}, emit=events.append))

        assert any(e["type"] == "assistant_text" for e in events)
        assert any(e["type"] == "result_meta" and e["completion"] == "DONE" for e in events)
        assert (ws / "output" / "article.md").read_text(encoding="utf-8").startswith("# 假成稿")
    finally:
        subprocess.run(["docker", "rmi", "-f", tag], capture_output=True)
