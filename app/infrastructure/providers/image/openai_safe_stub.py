from __future__ import annotations

from app.core.config import get_settings
from app.domain.models import DraftPayload, ImagePayload
from app.infrastructure.providers.image.mock import MockImageProvider


class OpenAISafeImageStubProvider:
    name = "openai-safe-image-stub"

    def __init__(self) -> None:
        self.settings = get_settings()
        self.mock = MockImageProvider()

    def generate(self, draft: DraftPayload) -> ImagePayload:
        return self.mock.generate(draft)
