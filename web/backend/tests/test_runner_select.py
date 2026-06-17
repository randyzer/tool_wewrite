from app.config import Settings
from app.runners.base import get_runner
from app.runners.direct import DirectRunner


def test_get_runner_direct(monkeypatch):
    monkeypatch.setenv("WEWRITE_RUNNER", "direct")
    assert isinstance(get_runner(Settings()), DirectRunner)


def test_get_runner_container(monkeypatch):
    monkeypatch.setenv("WEWRITE_RUNNER", "container")
    from app.runners.container import ContainerRunner
    assert isinstance(get_runner(Settings()), ContainerRunner)
