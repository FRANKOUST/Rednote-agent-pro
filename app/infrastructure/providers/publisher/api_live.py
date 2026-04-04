from __future__ import annotations

import httpx

from app.core.config import get_settings
from app.domain.models import DraftPayload, PublishPayload
from app.infrastructure.providers.publisher.api_safe_stub import XiaohongshuAPISafeStubProvider


class XiaohongshuAPILiveProvider:
    name = "xhs-api-live-publisher"

    def __init__(self) -> None:
        self.settings = get_settings()
        self.safe = XiaohongshuAPISafeStubProvider()

    def publish(self, draft: DraftPayload) -> PublishPayload:
        try:
            headers = {"Authorization": f"Bearer {self.settings.xhs_publish_api_token}"}
            body = {
                "title": draft.title,
                "body": draft.body,
                "tags": draft.tags,
                "cta": draft.cta,
                "content_type": draft.content_type,
            }
            with httpx.Client(timeout=30.0) as client:
                response = client.post(f"{self.settings.xhs_publish_api_base.rstrip('/')}/posts", headers=headers, json=body)
                response.raise_for_status()
                data = response.json()
            return PublishPayload(
                published_url=data.get("published_url", ""),
                provider=self.name,
                mode="api",
            )
        except Exception:
            return self.safe.publish(draft)
