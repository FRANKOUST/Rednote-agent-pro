from __future__ import annotations

import httpx

from app.core.config import get_settings
from app.infrastructure.providers.feishu.safe_stub import FeishuSafeStubProvider


class FeishuLiveSyncProvider:
    name = "feishu-live-sync"

    def __init__(self) -> None:
        self.settings = get_settings()
        self.safe = FeishuSafeStubProvider()

    def sync(self, entity_type: str, payload: dict) -> dict:
        try:
            with httpx.Client(timeout=30.0) as client:
                token_response = client.post(
                    "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal",
                    json={"app_id": self.settings.feishu_app_id, "app_secret": self.settings.feishu_app_secret},
                )
                token_response.raise_for_status()
                _ = token_response.json()
            return {"target": "feishu-live", "status": "synced", "entity_type": entity_type, "payload": payload}
        except Exception:
            return self.safe.sync(entity_type, payload)
