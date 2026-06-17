"""容器内任务入口：读 /workspace/job-spec.json → 跑共享管道 → 事件 JSONL 到 stdout、产物到 /workspace/output。

镜像把 app 包烤在 /app（PYTHONPATH=/app），skill 代码 ro 挂载到 /skill（WEWRITE_SKILL_DIR=/skill）。
工作区 /workspace 由宿主挂载（rw），本入口在容器内补 skill 软链（指向 /skill，宿主侧不可建那些链）。
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

# 容器内 PYTHONPATH=/app；本文件被 ENTRYPOINT 直接执行
from app import pipeline
from app.config import get_settings
from app.job_spec import JobSpec
from app.platforms import get_profile

_SKILL_LINKS = ["SKILL.md", "VERSION", "toolkit", "scripts", "references", "personas"]


def emit(event: dict) -> None:
    sys.stdout.write(json.dumps(event, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def setup_workspace_skill_links(ws: Path, skill: Path) -> None:
    """在容器内把 skill 只读代码软链进工作区。不链 .venv（用容器内 python）。"""
    for name in _SKILL_LINKS:
        src = skill / name
        if not src.exists():
            continue
        link = ws / name
        if link.is_symlink():
            link.unlink()  # 清掉宿主路径的（容器内悬空）软链，重指 /skill
        if not link.exists():  # 没有真实文件/目录占位才建
            link.symlink_to(src)
    (ws / ".home").mkdir(exist_ok=True)


async def _main() -> int:
    ws = Path("/workspace")
    settings = get_settings()  # WEWRITE_SKILL_DIR=/skill → settings.skill_dir=/skill
    setup_workspace_skill_links(ws, settings.skill_dir)

    spec = JobSpec.from_dict(json.loads((ws / "job-spec.json").read_text(encoding="utf-8")))
    profiles = [p for p in (get_profile(pid) for pid in spec.target_platforms) if p]

    from claude_agent_sdk import query
    env = dict(os.environ)  # 容器内 env（relay 凭证、image keys 等经 docker -e 注入）
    options, prompt = pipeline.make_options_and_prompt(settings, spec, profiles, env, ws)
    try:
        await pipeline.consume_stream(query(prompt=prompt, options=options), emit)
        return 0
    except Exception as exc:  # noqa: BLE001 - 失败也要让宿主拿到非零码 + stderr
        sys.stderr.write(f"{type(exc).__name__}: {exc}\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(_main()))
