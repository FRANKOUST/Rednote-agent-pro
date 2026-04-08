from __future__ import annotations

from pathlib import Path

from app.core.config import get_settings
from app.domain.models import DraftPayload, PublishPackagePayload, PublishPayload
from app.infrastructure.providers.publisher.browser_safe_stub import XiaohongshuBrowserSafeStubProvider


class XiaohongshuBrowserLiveProvider:
    name = "xhs-browser-live-publisher"

    def __init__(self) -> None:
        self.settings = get_settings()
        self.safe = XiaohongshuBrowserSafeStubProvider()

    def publish(self, draft: DraftPayload | PublishPackagePayload) -> PublishPayload:
        if not Path(self.settings.playwright_storage_state_path).exists():
            return self.safe.publish(draft)
        if not self._playwright_available():
            return self.safe.publish(draft)
        try:
            return self._publish_with_playwright(draft)
        except Exception:
            return self.safe.publish(draft)

    @staticmethod
    def _playwright_available() -> bool:
        try:
            from playwright.sync_api import sync_playwright  # type: ignore # noqa: F401
            return True
        except Exception:
            return False

    def _publish_with_playwright(self, draft: DraftPayload | PublishPackagePayload) -> PublishPayload:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context(storage_state=self.settings.playwright_storage_state_path)
            page = context.new_page()
            page.goto("https://creator.xiaohongshu.com/publish/publish", wait_until="domcontentloaded", timeout=15000)
            page.wait_for_timeout(1200)
            context.close()
            browser.close()
        return self.safe.publish(draft)

    def check_login(self) -> dict:
        exists = Path(self.settings.playwright_storage_state_path).exists()
        return {"provider": self.name, "status": "ready" if exists else "degraded", "mode": "browser", "storage_state_path": self.settings.playwright_storage_state_path, "reason": "publish browser login ready" if exists else "missing browser storage state"}

    def health(self) -> dict:
        return self.check_login()

    def diagnostics(self) -> dict:
        return {"provider_type": "browser_live", "storage_state_path": self.settings.playwright_storage_state_path}
