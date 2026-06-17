from __future__ import annotations
from ..config import Settings


class ContainerRunner:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
