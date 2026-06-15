"""多平台发布适配层。

设计：每个平台一个 Publisher 适配器，统一接口。
  - 微信公众号：官方草稿箱 API（appid/secret）—— 已有，最成熟。
  - 小红书：无个人发布 API，走浏览器自动化。本原型对接 xiaohongshu-mcp
    （https://github.com/xpzouying/xiaohongshu-mcp）暴露的 MCP 工具。
  - 抖音：基本只支持视频，WeWrite 暂不产视频 —— 先登记为不可用。

登录态（cookie）按用户加密存储；不可联网验证的真实 MCP 调用被隔离在
McpTransport 之后，便于测试用 FakeTransport 替换。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class LoginKind(str, Enum):
    API_KEY = "api_key"  # 填 appid/secret 等（微信）
    QRCODE = "qrcode"  # 扫码（小红书/抖音）
    NONE = "none"


@dataclass
class PlatformInfo:
    id: str
    label: str
    login_kind: LoginKind
    supports_text: bool
    supports_image: bool
    supports_video: bool
    available: bool  # 平台适配器是否已就绪可用
    note: str = ""


@dataclass
class LoginStatus:
    logged_in: bool
    detail: str = ""
    user_name: str = ""


@dataclass
class LoginChallenge:
    """发起登录后返回给前端的挑战（如二维码）。"""

    kind: LoginKind
    qrcode_image: Optional[str] = None  # data:image/png;base64,... 或 URL
    challenge_id: str = ""
    detail: str = ""


@dataclass
class NotePayload:
    """一篇待发布内容（已适配为目标平台所需的形态）。"""

    title: str
    content: str
    images: list[str] = field(default_factory=list)  # 本地路径或 URL
    tags: list[str] = field(default_factory=list)
    video: Optional[str] = None


@dataclass
class PublishResult:
    ok: bool
    platform: str
    url: str = ""
    detail: str = ""


class Publisher:
    """平台发布适配器基类。"""

    info: PlatformInfo

    def login_status(self) -> LoginStatus:  # pragma: no cover - 抽象
        raise NotImplementedError

    def start_login(self) -> LoginChallenge:  # pragma: no cover - 抽象
        raise NotImplementedError

    def publish(self, note: NotePayload) -> PublishResult:  # pragma: no cover - 抽象
        raise NotImplementedError

    def logout(self) -> None:  # pragma: no cover - 抽象
        raise NotImplementedError
