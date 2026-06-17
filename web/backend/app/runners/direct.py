"""进程内 runner：本地开发用宿主登录态 claude，免额度。"""
from __future__ import annotations

import os
from pathlib import Path

from claude_agent_sdk import query

from .. import pipeline
from ..config import Settings
from ..job_spec import JobSpec
from ..pipeline import Emit


class DirectRunner:
    async def run(self, *, settings: Settings, spec: JobSpec, profiles: list,
                  ws: Path, env: dict, emit: Emit) -> None:
        # 进程内：CLI 需要完整 os.environ（PATH/node 等）+ 注入的密钥
        full_env = {**os.environ, **env}
        options, prompt = pipeline.make_options_and_prompt(settings, spec, profiles, full_env, ws)
        await pipeline.consume_stream(query(prompt=prompt, options=options), emit)
