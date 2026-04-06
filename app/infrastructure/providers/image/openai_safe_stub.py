from __future__ import annotations

from app.core.config import get_settings
from app.domain.models import DraftPayload, ImagePayload
from app.infrastructure.providers.image.mock import MockImageProvider


class OpenAICompatibleSafeImageStubProvider:
    name = "openai-compatible-safe-image"

    def __init__(self) -> None:
        self.settings = get_settings()
        self.mock = MockImageProvider()

    def generate(self, draft: DraftPayload) -> ImagePayload:
        return self.mock.generate(draft)

    def health(self) -> dict:
        return {"status": "ready", "reason": "safe image stub available"}

    def diagnostics(self) -> dict:
        return {
            "provider_type": "safe_stub",
            "model_name": self.settings.resolved_image_model_name,
            "base_url": self.settings.resolved_image_base_url,
            "last_run": self.mock.last_run_metadata,
        }
