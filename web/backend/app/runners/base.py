"""Runner 抽象：决定任务在哪执行（进程内 / 容器）。"""
from __future__ import annotations

from pathlib import Path
from typing import Protocol

from ..config import Settings
from ..job_spec import JobSpec
from ..pipeline import Emit


class Runner(Protocol):
    async def run(self, *, settings: Settings, spec: JobSpec, profiles: list,
                  ws: Path, env: dict, emit: Emit) -> None:
        """跑完一条管道：在 ws/ 内产出文件，过程经 emit 发事件。不负责收集产物。"""
        ...


def get_runner(settings: Settings) -> "Runner":
    if settings.runner == "container":
        from .container import ContainerRunner
        return ContainerRunner(settings)
    from .direct import DirectRunner
    return DirectRunner()
