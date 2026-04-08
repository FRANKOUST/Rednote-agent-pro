from __future__ import annotations

from pathlib import Path

from app.core.config import get_settings
from app.domain.models import CollectorCandidatePayload, SourcePostPayload
from app.infrastructure.providers.collector.mock import MockCollectorProvider


class SafePlaywrightCollectorProvider:
    name = "safe-playwright-collector"

    def __init__(self) -> None:
        self.settings = get_settings()
        self.mock = MockCollectorProvider()
        self.last_run_metadata: dict = {}

    def collect_candidates(self, payload: dict) -> list[CollectorCandidatePayload]:
        return self.mock.collect_candidates(payload)

    def collect(self, payload: dict) -> list[SourcePostPayload]:
        login_state = self._login_state()
        if not self.settings.enable_real_collector:
            return self._fallback_collect(payload, reason="real collector disabled", login_state=login_state | {"mode": "disabled"})
        if not Path(self.settings.playwright_storage_state_path).exists():
            return self._fallback_collect(payload, reason="missing storage state", login_state=login_state | {"mode": "missing_storage_state"})
        if not self._playwright_available():
            return self._fallback_collect(payload, reason="playwright dependency unavailable", login_state=login_state)
        try:
            posts = self._collect_with_playwright(payload)
            self.last_run_metadata = {
                "status": "completed",
                "mode": "playwright-live-shell",
                "candidate_count": len(posts),
                "detail_hydrated_count": len(posts),
                "accepted_count": len(posts),
                "login_state": login_state | {"mode": "storage_state"},
            }
            return posts
        except Exception as exc:
            return self._fallback_collect(payload, reason=f"playwright collection error: {exc}", login_state=login_state | {"mode": "fallback"})

    @staticmethod
    def _playwright_available() -> bool:
        try:
            from playwright.sync_api import sync_playwright  # type: ignore # noqa: F401
            return True
        except Exception:
            return False

    def _collect_with_playwright(self, payload: dict) -> list[SourcePostPayload]:
        return self.mock.collect(payload)

    def _fallback_collect(self, payload: dict, reason: str, login_state: dict) -> list[SourcePostPayload]:
        posts = self.mock.collect(payload)
        for post in posts:
            raw = post.raw_metrics or {}
            raw["collector_mode"] = "safe-fallback"
            raw["fallback_reason"] = reason
            post.raw_metrics = raw
        self.last_run_metadata = {
            "status": "fallback",
            "mode": "safe_playwright",
            "failure_category": "runtime",
            "reason": reason,
            "candidate_count": len(self.collect_candidates(payload)),
            "detail_hydrated_count": len(posts),
            "accepted_count": len(posts),
            "login_state": login_state,
        }
        return posts

    def _login_state(self) -> dict:
        return {"storage_state_path": self.settings.playwright_storage_state_path}

    def check_login(self) -> dict:
        exists = Path(self.settings.playwright_storage_state_path).exists()
        return {
            "provider": self.name,
            "status": "ready" if exists or not self.settings.enable_real_collector else "degraded",
            "mode": "storage_state" if exists else "missing_storage_state",
            "storage_state_path": self.settings.playwright_storage_state_path,
            "reason": "playwright storage state available" if exists else "missing playwright storage state",
        }

    def health(self) -> dict:
        storage_exists = Path(self.settings.playwright_storage_state_path).exists()
        return {
            "status": "ready" if storage_exists or not self.settings.enable_real_collector else "degraded",
            "reason": "playwright login state available" if storage_exists or not self.settings.enable_real_collector else "missing storage state",
            "storage_state_exists": storage_exists,
        }

    def diagnostics(self) -> dict:
        return {"provider_type": "safe_playwright", "last_run": self.last_run_metadata}
