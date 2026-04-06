from __future__ import annotations

from app.infrastructure.providers.feishu.mock import MockSyncProvider


class FeishuSafeStubProvider:
    name = "feishu-safe-stub"

    def __init__(self) -> None:
        self.mock = MockSyncProvider()

    def sync(self, entity_type: str, payload: dict) -> dict:
        result = self.mock.sync(entity_type, payload)
        result.update({"target": "feishu-safe-stub", "provider": self.name})
        return result

    def health(self) -> dict:
        return {"status": "ready", "reason": "safe Feishu stub available"}

    def diagnostics(self) -> dict:
        return {"provider_type": "safe_stub", "delegate": self.mock.name, "last_run": self.mock.last_run_metadata}
