from __future__ import annotations


class MockSyncProvider:
    name = "mock-feishu"

    def sync(self, entity_type: str, payload: dict) -> dict:
        return {"target": "mock-feishu-bitable", "status": "synced", "entity_type": entity_type, "payload": payload}
