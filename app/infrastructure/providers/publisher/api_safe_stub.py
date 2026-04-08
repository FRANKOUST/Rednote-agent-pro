from __future__ import annotations

from app.core.config import get_settings
from app.domain.models import DraftPayload, PublishPackagePayload, PublishPayload
from app.infrastructure.providers.publisher.mock import MockPublisherProvider


class XiaohongshuAPISafeStubProvider:
    name = "xhs-api-safe-stub"

    def __init__(self) -> None:
        self.settings = get_settings()
        self.mock = MockPublisherProvider()

    def publish(self, draft: DraftPayload | PublishPackagePayload) -> PublishPayload:
        result = self.mock.publish(draft)
        return PublishPayload(published_url=result.published_url, provider=self.name, mode="safe_stub")

    def check_login(self) -> dict:
        return {"provider": self.name, "status": "ready", "mode": "safe_stub", "reason": "safe stub bypasses live publish login"}

    def health(self) -> dict:
        return {"status": "ready", "reason": "safe publish stub available"}

    def diagnostics(self) -> dict:
        return {"provider_type": "safe_stub"}
