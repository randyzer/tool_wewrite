"""Pydantic 请求/响应模型。"""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class WeChatBinding(BaseModel):
    """用户绑定自己的公众号凭证（平台无法代出）。"""

    appid: str = Field(..., min_length=1)
    secret: str = Field(..., min_length=1)
    author: str = ""


class StylePrefs(BaseModel):
    """公众号风格 / 写作人格 / 默认排版主题。"""

    account_name: str = ""
    writing_persona: str = "midnight-friend"
    theme: str = "professional-clean"
    audience: str = ""
    tone: str = ""


class AccountState(BaseModel):
    account_name: str = ""
    writing_persona: str = "midnight-friend"
    theme: str = "professional-clean"
    audience: str = ""
    tone: str = ""
    wechat_bound: bool = False
    wechat_author: str = ""


class CreateJobRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="一句话需求，如「写一篇关于 AI Agent 的公众号文章」")
    interactive: bool = False
    theme: Optional[str] = None
    persona: Optional[str] = None
    publish_draft: bool = Field(
        default=False,
        description="完成后是否推送到用户绑定的公众号草稿箱（需已绑定微信）。",
    )


class JobSummary(BaseModel):
    id: str
    status: Literal["queued", "running", "done", "error"]
    prompt: str
    created_at: float
    completion: Optional[str] = None  # DONE / DONE_WITH_CONCERNS / BLOCKED / NEEDS_CONTEXT


class CatalogItem(BaseModel):
    id: str
    label: str
    description: str = ""


# ---- 多平台发布 ----
class PlatformStatus(BaseModel):
    id: str
    label: str
    login_kind: str
    supports_text: bool
    supports_image: bool
    supports_video: bool
    available: bool
    note: str = ""
    logged_in: bool = False
    user_name: str = ""


class LoginChallengeResp(BaseModel):
    kind: str
    qrcode_image: Optional[str] = None
    challenge_id: str = ""
    detail: str = ""


class LoginStatusResp(BaseModel):
    logged_in: bool
    detail: str = ""
    user_name: str = ""


class NoteInput(BaseModel):
    title: str = ""
    content: str = ""
    images: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    video: Optional[str] = None


class PublishRequest(BaseModel):
    job_id: Optional[str] = Field(default=None, description="从某任务成稿发布；与 note 二选一")
    note: Optional[NoteInput] = None


class PublishResponse(BaseModel):
    ok: bool
    platform: str
    url: str = ""
    detail: str = ""


class DistributeRequest(BaseModel):
    """把一份源内容分发改写到多个平台。source_* 三选一。"""

    source_job_id: Optional[str] = Field(default=None, description="从某 generate 任务成稿作源")
    source_text: Optional[str] = Field(default=None, description="直接粘贴的源文本/markdown")
    source_url: Optional[str] = Field(default=None, description="公众号文章 URL，后端抓取作源")
    platforms: list[str] = Field(..., min_length=1, description="目标平台 id 列表")
    persona: Optional[str] = None
    theme: Optional[str] = None


class PlatformVersion(BaseModel):
    platform: str
    label: str = ""
    output_kind: str = "graphic_text"
    title: str = ""
    markdown: str = ""
    images: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    humanness: Optional[float] = None
    max_similarity: Optional[float] = None
    passed: bool = True
    warning: str = ""
    status: str = "done"  # done | failed
