from __future__ import annotations

from app.infrastructure.providers.feishu.cli import FeishuCLISyncProvider


class FeishuLiveSyncProvider(FeishuCLISyncProvider):
    name = "feishu-live-sync"
