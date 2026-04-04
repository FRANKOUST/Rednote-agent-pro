from __future__ import annotations

import re

from app.domain.models import DraftPayload, PublishPayload


def _slugify(value: str) -> str:
    lowered = value.lower().strip()
    lowered = re.sub(r"\s+", "-", lowered)
    lowered = re.sub(r"[^a-z0-9\-]+", "", lowered)
    return lowered or "draft"


class MockPublisherProvider:
    name = "mock-publisher"

    def publish(self, draft: DraftPayload) -> PublishPayload:
        slug = _slugify(draft.title)
        return PublishPayload(
            published_url=f"https://mock.xiaohongshu.local/published/{slug}",
            provider=self.name,
            mode="mock",
        )
