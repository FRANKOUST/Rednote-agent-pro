from __future__ import annotations

import re

from app.domain.models import DraftPayload, PublishPackagePayload, PublishPayload


def _slugify(value: str) -> str:
    lowered = value.lower().strip()
    lowered = re.sub(r"\s+", "-", lowered)
    lowered = re.sub(r"[^a-z0-9\-]+", "", lowered)
    return lowered or "draft"


class MockPublisherProvider:
    name = "mock-publisher"

    def __init__(self) -> None:
        self.last_run_metadata: dict = {}

    def publish(self, draft: DraftPayload | PublishPackagePayload) -> PublishPayload:
        title = getattr(draft, "headline", None) or getattr(draft, "title", "draft")
        slug = _slugify(title)
        self.last_run_metadata = {"headline": title, "mode": "mock"}
        return PublishPayload(
            published_url=f"https://mock.xiaohongshu.local/published/{slug}",
            provider=self.name,
            mode="mock",
        )

    def check_login(self) -> dict:
        return {"provider": self.name, "status": "ready", "mode": "mock", "reason": "mock publisher does not require login"}

    def health(self) -> dict:
        return {"status": "ready", "reason": "mock publisher available"}

    def diagnostics(self) -> dict:
        return {"provider_type": "mock", "last_run": self.last_run_metadata}
