from __future__ import annotations

import base64
from pathlib import Path
from uuid import uuid4

import httpx

from app.core.config import get_settings
from app.domain.models import DraftPayload, ImagePayload
from app.infrastructure.providers.image.openai_safe_stub import OpenAISafeImageStubProvider


class OpenAILiveImageProvider:
    name = "openai-live-image"

    def __init__(self) -> None:
        self.settings = get_settings()
        self.safe = OpenAISafeImageStubProvider()

    def generate(self, draft: DraftPayload) -> ImagePayload:
        try:
            headers = {"Authorization": f"Bearer {self.settings.openai_api_key}"}
            body = {
                "model": self.settings.openai_image_model,
                "prompt": draft.image_prompt,
                "size": "1024x1024",
            }
            with httpx.Client(timeout=60.0) as client:
                response = client.post("https://api.openai.com/v1/images/generations", headers=headers, json=body)
                response.raise_for_status()
                payload = response.json()["data"][0]
            if "b64_json" in payload:
                filename = f"{uuid4().hex}.png"
                path = Path(self.settings.media_dir) / filename
                path.write_bytes(base64.b64decode(payload["b64_json"]))
                return ImagePayload(path=str(path), prompt=draft.image_prompt, provider=self.name)
        except Exception:
            return self.safe.generate(draft)
        return self.safe.generate(draft)
