"""抖音发布适配器（登记为暂不可用）。

抖音基本只支持视频，WeWrite 暂不产视频；官方视频发布 API 需企业应用审核 + 每用户
OAuth，门槛高。先登记平台信息，待补齐视频能力或接入浏览器自动化（如 social-auto-upload
的 douyin uploader）后再实现。
"""
from __future__ import annotations

from .base import LoginKind, PlatformInfo

INFO = PlatformInfo(
    id="douyin",
    label="抖音",
    login_kind=LoginKind.QRCODE,
    supports_text=False,
    supports_image=True,
    supports_video=True,
    available=False,
    note="抖音以视频为主，WeWrite 暂不产视频；接入浏览器自动化上传后开放。",
)
