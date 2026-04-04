from __future__ import annotations

from app.core.config import get_settings
from app.domain.models import DraftPayload, PublishPayload
from app.infrastructure.providers.publisher.mock import MockPublisherProvider


class XiaohongshuBrowserSafeStubProvider:
    name = "xhs-browser-safe-stub"

    def __init__(self) -> None:
        self.settings = get_settings()
        self.mock = MockPublisherProvider()

    def publish(self, draft: DraftPayload) -> PublishPayload:
        result = self.mock.publish(draft)
        return PublishPayload(published_url=result.published_url, provider=self.name, mode="safe_stub")
