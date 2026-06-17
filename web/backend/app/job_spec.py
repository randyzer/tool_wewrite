"""跨进程任务规格 —— runner 与容器入口共用。仅依赖 dataclasses/json，勿引重依赖。"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict


@dataclass
class JobSpec:
    kind: str                       # generate | distribute
    prompt: str
    theme: str = ""
    persona: str = ""
    interactive: bool = False       # generate 用
    publish: bool = False           # generate 用（已结合 wechat_bound 判定）
    source_markdown: str = ""       # distribute 用
    target_platforms: list[str] = field(default_factory=list)  # distribute 用

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "JobSpec":
        return cls(
            kind=d["kind"],
            prompt=d["prompt"],
            theme=d.get("theme", ""),
            persona=d.get("persona", ""),
            interactive=bool(d.get("interactive", False)),
            publish=bool(d.get("publish", False)),
            source_markdown=d.get("source_markdown", ""),
            target_platforms=list(d.get("target_platforms", [])),
        )
