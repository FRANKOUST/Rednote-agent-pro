from __future__ import annotations

from app.core.config import get_settings
from app.infrastructure.providers.feishu.mock import MockSyncProvider


class FeishuSafeStubProvider:
    name = "feishu-safe-stub"

    def __init__(self) -> None:
        self.settings = get_settings()
        self.mock = MockSyncProvider()

    def sync(self, entity_type: str, payload: dict) -> dict:
        return self.mock.sync(entity_type, payload)
