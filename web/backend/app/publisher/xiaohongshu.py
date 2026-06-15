"""小红书发布适配器 —— 对接 xiaohongshu-mcp 暴露的 MCP 工具。

参考: https://github.com/xpzouying/xiaohongshu-mcp
该服务暴露的相关工具: check_login_status / get_login_qrcode / delete_cookies /
publish_content（图文）/ publish_with_video。

NOTE(多租户): 参考实现是单账号、cookie 存在服务端的。要做到按用户隔离，生产应
为每个用户/会话起独立 MCP 实例（或换支持 cookie 导入的服务），把用户 cookie 从下面的
加密 CookieVault 注入。本适配器面向「一个已登录的 MCP 实例」工作，登录态变化经回调
持久化到 CookieVault。
"""
from __future__ import annotations

from .base import (
    LoginChallenge,
    LoginKind,
    LoginStatus,
    NotePayload,
    PlatformInfo,
    PublishResult,
    Publisher,
)
from .mcp_client import McpError, McpTransport

INFO = PlatformInfo(
    id="xiaohongshu",
    label="小红书",
    login_kind=LoginKind.QRCODE,
    supports_text=True,
    supports_image=True,
    supports_video=True,
    available=True,
    note="经 xiaohongshu-mcp 浏览器自动化发布图文笔记；需扫码登录，cookie 会过期。",
)


class XiaohongshuPublisher(Publisher):
    info = INFO

    def __init__(self, transport: McpTransport) -> None:
        self.t = transport

    def login_status(self) -> LoginStatus:
        res = self.t.call_tool("check_login_status", {})
        data = res.get("data") or {}
        logged = bool(data.get("logged_in") or data.get("isLoggedIn") or data.get("status") == "logged_in")
        name = str(data.get("user_name") or data.get("nickname") or "")
        return LoginStatus(logged_in=logged, detail=res.get("text", ""), user_name=name)

    def start_login(self) -> LoginChallenge:
        res = self.t.call_tool("get_login_qrcode", {})
        data = res.get("data") or {}
        img = data.get("qrcode") or data.get("image") or data.get("img") or ""
        if img and not str(img).startswith(("data:", "http")):
            img = f"data:image/png;base64,{img}"
        return LoginChallenge(
            kind=LoginKind.QRCODE,
            qrcode_image=img or None,
            challenge_id=str(data.get("session_id") or ""),
            detail=res.get("text", "请用小红书 App 扫码登录"),
        )

    def publish(self, note: NotePayload) -> PublishResult:
        if note.video:
            tool, args = "publish_with_video", {
                "title": note.title,
                "content": note.content,
                "video": note.video,
                "tags": note.tags,
            }
        else:
            if not note.images:
                return PublishResult(
                    ok=False, platform=self.info.id,
                    detail="小红书图文笔记至少需要 1 张图片（封面）。",
                )
            tool, args = "publish_content", {
                "title": note.title[:20],  # 小红书标题上限约 20 字
                "content": note.content,
                "images": note.images,
                "tags": note.tags,
            }
        try:
            res = self.t.call_tool(tool, args)
        except McpError as exc:
            return PublishResult(ok=False, platform=self.info.id, detail=str(exc))
        if res.get("is_error"):
            return PublishResult(ok=False, platform=self.info.id, detail=res.get("text", "发布失败"))
        data = res.get("data") or {}
        return PublishResult(
            ok=True, platform=self.info.id,
            url=str(data.get("url") or data.get("note_url") or ""),
            detail=res.get("text", "已发布"),
        )

    def logout(self) -> None:
        self.t.call_tool("delete_cookies", {})
