from __future__ import annotations

from app.domain.models import DraftPayload, ImagePayload


class MockImageProvider:
    name = "mock-image"

    def __init__(self) -> None:
        self.last_run_metadata: dict = {}

    def generate(self, draft: DraftPayload) -> ImagePayload:
        filename = draft.title.replace("/", "-")[:32] or "mock-image"
        self.last_run_metadata = {"title": draft.title, "mode": "mock"}
        return ImagePayload(path=f"./data/media/{filename}.png", prompt=draft.image_prompt, provider=self.name)

    def health(self) -> dict:
        return {"status": "ready", "reason": "mock image provider available"}

    def diagnostics(self) -> dict:
        return {"provider_type": "mock", "last_run": self.last_run_metadata}
