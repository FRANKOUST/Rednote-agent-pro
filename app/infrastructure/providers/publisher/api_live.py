from __future__ import annotations

import httpx

from app.core.config import get_settings
from app.domain.models import DraftPayload, PublishPackagePayload, PublishPayload
from app.infrastructure.providers.publisher.api_safe_stub import XiaohongshuAPISafeStubProvider


class XiaohongshuAPILiveProvider:
    name = "xhs-api-live-publisher"

    def __init__(self) -> None:
        self.settings = get_settings()
        self.safe = XiaohongshuAPISafeStubProvider()

    def publish(self, draft: DraftPayload | PublishPackagePayload) -> PublishPayload:
        title = getattr(draft, "headline", None) or getattr(draft, "title", "")
        body = getattr(draft, "body", "")
        tags = getattr(draft, "tags", [])
        cta = getattr(draft, "cta", "")
        content_type = getattr(draft, "content_type", "图文")
        try:
            headers = {"Authorization": f"Bearer {self.settings.xhs_publish_api_token}"}
            body_payload = {"title": title, "body": body, "tags": tags, "cta": cta, "content_type": content_type}
            with httpx.Client(timeout=30.0) as client:
                response = client.post(f"{self.settings.xhs_publish_api_base.rstrip('/')}/posts", headers=headers, json=body_payload)
                response.raise_for_status()
                data = response.json()
            return PublishPayload(published_url=data.get("published_url", ""), provider=self.name, mode="api")
        except Exception:
            return self.safe.publish(draft)

    def check_login(self) -> dict:
        configured = bool(self.settings.xhs_publish_api_token and self.settings.xhs_publish_api_base)
        return {"provider": self.name, "status": "ready" if configured else "degraded", "mode": "api", "reason": "publish api credentials configured" if configured else "missing publish api credentials"}

    def health(self) -> dict:
        return self.check_login()

    def diagnostics(self) -> dict:
        return {"provider_type": "api_live", "base": self.settings.xhs_publish_api_base}
