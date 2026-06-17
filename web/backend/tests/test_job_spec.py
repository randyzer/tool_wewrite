from app.job_spec import JobSpec

def test_roundtrip_generate():
    s = JobSpec(kind="generate", prompt="写一篇 X", theme="sspai",
                persona="cold-analyst", interactive=False, publish=True)
    d = s.to_dict()
    assert d["kind"] == "generate" and d["publish"] is True
    assert JobSpec.from_dict(d) == s

def test_roundtrip_distribute():
    s = JobSpec(kind="distribute", prompt="分发", theme="t", persona="p",
                source_markdown="# 源", target_platforms=["xiaohongshu", "douyin"])
    assert JobSpec.from_dict(s.to_dict()) == s

def test_from_dict_tolerates_missing_optional():
    s = JobSpec.from_dict({"kind": "generate", "prompt": "hi"})
    assert s.theme == "" and s.target_platforms == [] and s.publish is False
