from __future__ import annotations

import json


class MockSyncProvider:
    name = "mock-feishu"

    def __init__(self) -> None:
        self.last_run_metadata: dict = {}

    def sync(self, entity_type: str, payload: dict) -> dict:
        result = {
            "target": "mock-feishu-bitable",
            "status": "synced",
            "entity_type": entity_type,
            "payload": payload,
            "dry_run": True,
            "provider": self.name,
            "diagnostics": {"mode": "mock"},
        }
        self.last_run_metadata = {"entity_type": entity_type, "payload_preview": json.dumps(payload, ensure_ascii=False)[:200]}
        return result

    def health(self) -> dict:
        return {"status": "ready", "reason": "mock sync provider available"}

    def diagnostics(self) -> dict:
        return {"provider_type": "mock", "last_run": self.last_run_metadata}
