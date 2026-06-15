"""微信公众号发布适配器。

公众号有官方草稿箱 API（appid/secret），是已有且最成熟的渠道 —— 主管道 Step 7 已
直接通过 toolkit 推送草稿箱。这里提供一个统一接口下的适配器，用于「成稿后单独按平台
发布」的显式动作，并反映绑定状态。
"""
from __future__ import annotations

from .base import (
    LoginKind,
    LoginStatus,
    NotePayload,
    PlatformInfo,
    PublishResult,
    Publisher,
)

INFO = PlatformInfo(
    id="wechat",
    label="微信公众号",
    login_kind=LoginKind.API_KEY,
    supports_text=True,
    supports_image=True,
    supports_video=False,
    available=True,
    note="官方草稿箱 API。在「设置」绑定 appid/secret 后，主管道可直接推送草稿箱。",
)


class WeChatPublisher(Publisher):
    info = INFO

    def __init__(self, *, bound: bool, author: str = "") -> None:
        self._bound = bound
        self._author = author

    def login_status(self) -> LoginStatus:
        return LoginStatus(
            logged_in=self._bound,
            user_name=self._author,
            detail="已绑定 appid/secret" if self._bound else "未绑定",
        )

    def publish(self, note: NotePayload) -> PublishResult:
        # 公众号推送由主管道（toolkit publisher，凭 env 注入的 appid/secret）完成。
        # 此适配器返回引导信息，避免与管道重复实现一套发布逻辑。
        if not self._bound:
            return PublishResult(ok=False, platform=self.info.id, detail="未绑定公众号，请先在设置绑定。")
        return PublishResult(
            ok=True, platform=self.info.id,
            detail="公众号草稿箱推送由生成管道完成（创建任务时勾选「推送草稿箱」）。",
        )
