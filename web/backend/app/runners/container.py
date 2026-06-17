"""容器 runner：每任务起一个一次性硬化 Docker 容器跑管道。

事件走容器 stdout 的 JSONL；产物走挂载的工作区。线上用，凭证走 relay（env 注入）。
"""
from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

from ..config import Settings
from ..job_spec import JobSpec
from ..pipeline import Emit


class ContainerRunner:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def _docker_args(self, ws: Path, env: dict) -> list[str]:
        s = self._settings
        args = [
            "docker", "run", "--rm", "-i",
            # 以宿主属主身份跑 —— 工作区是宿主挂载的目录，否则镜像内 uid 10001 无权写。
            # 仍是非 root（后端服务账号本身非 root），镜像内 USER runner 是无 --user 时的兜底。
            "--user", f"{os.getuid()}:{os.getgid()}",
            "--network", s.job_network,
            "--cpus", str(s.job_cpus),
            "--memory", s.job_memory,
            "--pids-limit", str(s.job_pids),
            "--cap-drop", "ALL",
            "--security-opt", "no-new-privileges",
            "--read-only",
            "--tmpfs", "/tmp:size=512m",
            "-e", "HOME=/workspace/.home",
            "-v", f"{ws}:/workspace",
            "-v", f"{s.skill_dir}:/skill:ro",
            "-w", "/workspace",
        ]
        for k, v in env.items():
            args += ["-e", f"{k}={v}"]
        args.append(s.job_image)
        return args

    @staticmethod
    def _parse_event_line(line: str) -> dict | None:
        line = line.strip()
        if not line:
            return None
        try:
            obj = json.loads(line)
        except (ValueError, TypeError):
            return None
        if isinstance(obj, dict) and "type" in obj:
            return obj
        return None

    async def run(self, *, settings: Settings, spec: JobSpec, profiles: list,
                  ws: Path, env: dict, emit: Emit) -> None:
        # 写任务规格供容器入口读取
        (ws / "job-spec.json").write_text(
            json.dumps(spec.to_dict(), ensure_ascii=False), encoding="utf-8")

        args = self._docker_args(ws, env)
        proc = await asyncio.create_subprocess_exec(
            *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

        async def pump_stdout() -> None:
            assert proc.stdout is not None
            async for raw in proc.stdout:
                ev = self._parse_event_line(raw.decode("utf-8", "replace"))
                if ev is not None:
                    emit(ev)

        async def drain_stderr() -> bytes:
            assert proc.stderr is not None
            return await proc.stderr.read()

        # 并发抽干 stdout(事件流) 与 stderr —— 否则 stderr 写满管道(~64KB)会把容器卡在
        # write() 上、stdout 再也不 EOF，白白耗尽整个超时预算。
        try:
            _, stderr_bytes = await asyncio.wait_for(
                asyncio.gather(pump_stdout(), drain_stderr()),
                timeout=settings.job_timeout,
            )
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            raise RuntimeError(f"任务容器超时（>{settings.job_timeout:.0f}s），已终止")

        rc = await proc.wait()
        if rc != 0:
            tail = stderr_bytes.decode("utf-8", "replace").strip()[-500:]
            raise RuntimeError(f"任务容器非零退出（code={rc}）：{tail}")
