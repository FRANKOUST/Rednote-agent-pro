from __future__ import annotations

import base64
from pathlib import Path
from uuid import uuid4

import httpx

from app.core.config import get_settings
from app.domain.models import DraftPayload, ImagePayload
from app.infrastructure.providers.image.openai_safe_stub import OpenAICompatibleSafeImageStubProvider


class OpenAICompatibleImageProvider:
    name = "openai-compatible-image"

    def __init__(self) -> None:
        self.settings = get_settings()
        self.safe = OpenAICompatibleSafeImageStubProvider()
        self.last_run_metadata: dict = {}

    def generate(self, draft: DraftPayload) -> ImagePayload:
        try:
            if not self.settings.enable_real_image_provider:
                raise RuntimeError("real image provider disabled")
            if not self.settings.resolved_image_api_key:
                raise RuntimeError("missing image api key")
            headers = {"Authorization": f"Bearer {self.settings.resolved_image_api_key}"}
            body = {
                "model": self.settings.resolved_image_model_name,
                "prompt": draft.image_prompt,
                "size": "1024x1024",
            }
            with httpx.Client(timeout=self.settings.image_model_timeout_seconds) as client:
                response = client.post(f"{self.settings.resolved_image_base_url}/images/generations", headers=headers, json=body)
                response.raise_for_status()
                payload = response.json()["data"][0]
            if "b64_json" in payload:
                filename = f"{uuid4().hex}.png"
                path = Path(self.settings.media_dir) / filename
                path.write_bytes(base64.b64decode(payload["b64_json"]))
                self.last_run_metadata = {"mode": "live", "path": str(path), "model": self.settings.resolved_image_model_name}
                return ImagePayload(path=str(path), prompt=draft.image_prompt, provider=self.name)
        except Exception as exc:
            self.last_run_metadata = {"mode": "fallback", "error": str(exc)}
            return self.safe.generate(draft)
        return self.safe.generate(draft)

    def health(self) -> dict:
        if not self.settings.enable_real_image_provider:
            return {"status": "ready", "reason": "safe image mode active"}
        if self.settings.resolved_image_api_key:
            return {"status": "ready", "reason": "image api key configured"}
        return {"status": "degraded", "reason": "missing image api key"}

    def diagnostics(self) -> dict:
        return {
            "provider_type": "openai_compatible",
            "base_url": self.settings.resolved_image_base_url,
            "model_name": self.settings.resolved_image_model_name,
            "last_run": self.last_run_metadata,
        }
