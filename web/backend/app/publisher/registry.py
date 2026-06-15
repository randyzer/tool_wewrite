"""平台注册表 —— 列出平台 + 按平台构造可用的发布适配器。"""
from __future__ import annotations

from typing import Optional

from ..config import Settings
from ..store import Account
from . import douyin, wechat
from .base import PlatformInfo, Publisher
from .mcp_client import HttpMcpTransport, McpTransport
from .xiaohongshu import INFO as XHS_INFO
from .xiaohongshu import XiaohongshuPublisher


def list_platforms(settings: Settings) -> list[PlatformInfo]:
    xhs = PlatformInfo(**{**XHS_INFO.__dict__})
    if not settings.xhs_mcp_url:
        xhs.available = False
        xhs.note = "未配置 XHS_MCP_URL（需先部署 xiaohongshu-mcp）。" + xhs.note
    return [wechat.INFO, xhs, douyin.INFO]


def get_publisher(
    platform: str,
    settings: Settings,
    account: Account,
    *,
    transport: Optional[McpTransport] = None,
) -> Publisher:
    """构造平台适配器。transport 可注入（测试用），否则按配置创建。"""
    if platform == "wechat":
        return wechat.WeChatPublisher(bound=account.wechat_bound, author=account.wechat_author)
    if platform == "xiaohongshu":
        t = transport
        if t is None:
            if not settings.xhs_mcp_url:
                raise ValueError("未配置 XHS_MCP_URL：请先部署 xiaohongshu-mcp 并设置该环境变量。")
            t = HttpMcpTransport(settings.xhs_mcp_url)
        return XiaohongshuPublisher(t)
    if platform == "douyin":
        raise ValueError("抖音渠道尚未开放（暂不产视频）。")
    raise ValueError(f"未知平台：{platform}")
