import pytest
from pydantic import ValidationError
from app.store import Job
from app.models import DistributeRequest, PlatformVersion

def test_job_distribute_defaults():
    j = Job(id="x", user_id="u", prompt="")
    assert j.kind == "generate"
    assert j.source_markdown == ""
    assert j.target_platforms == []
    assert j.platform_versions == []

def test_distribute_request_requires_platforms():
    with pytest.raises(ValidationError):
        DistributeRequest(source_text="hi", platforms=[])

def test_distribute_request_ok():
    r = DistributeRequest(source_text="hi", platforms=["xiaohongshu"])
    assert r.platforms == ["xiaohongshu"]
    assert r.source_job_id is None

def test_platform_version_defaults():
    v = PlatformVersion(platform="xiaohongshu", label="小红书")
    assert v.passed is True
    assert v.status == "done"
    assert v.images == []
