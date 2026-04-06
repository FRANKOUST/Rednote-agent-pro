from __future__ import annotations

from pathlib import Path

from app.core.config import get_settings
from app.domain.models import SourcePostPayload
from app.infrastructure.providers.collector.mock import MockCollectorProvider


class SafePlaywrightCollectorProvider:
    name = "safe-playwright-collector"

    def __init__(self) -> None:
        self.settings = get_settings()
        self.mock = MockCollectorProvider()
        self.last_run_metadata: dict = {}

    def collect(self, payload: dict) -> list[SourcePostPayload]:
        if not self.settings.enable_real_collector:
            return self._fallback_collect(payload, reason="real collector disabled")

        if not Path(self.settings.playwright_storage_state_path).exists():
            return self._fallback_collect(payload, reason="missing storage state")

        if not self._playwright_available():
            return self._fallback_collect(payload, reason="playwright dependency unavailable")

        try:
            posts = self._collect_with_playwright(payload)
            self.last_run_metadata = {
                "status": "completed",
                "mode": "playwright-live-shell",
                "source_posts": len(posts),
            }
            return posts
        except Exception as exc:
            return self._fallback_collect(payload, reason=f"playwright collection error: {exc}")

    @staticmethod
    def _playwright_available() -> bool:
        try:
            from playwright.sync_api import sync_playwright  # type: ignore # noqa: F401
            return True
        except Exception:
            return False

    def _collect_with_playwright(self, payload: dict) -> list[SourcePostPayload]:
        from playwright.sync_api import sync_playwright

        keywords = payload.get("keywords", [])
        collected: list[SourcePostPayload] = []
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context(storage_state=self.settings.playwright_storage_state_path)
            page = context.new_page()
            for keyword in keywords:
                search_url = f"https://www.xiaohongshu.com/search_result?keyword={keyword}"
                page.goto(search_url, wait_until="domcontentloaded", timeout=15000)
                page.wait_for_timeout(self.settings.collector_action_delay_ms)
                cards = page.locator("section.note-item, div.note-item").all()[:10]
                for index, card in enumerate(cards):
                    title = ""
                    try:
                        title = (card.locator("a.title span").first.inner_text(timeout=1500) or "").strip()
                    except Exception:
                        continue
                    if not title:
                        continue
                    url = f"https://www.xiaohongshu.com/explore/{keyword}-{index}"
                    content = title
                    try:
                        content = (card.locator("div.desc, p.desc").first.inner_text(timeout=1000) or title).strip()
                    except Exception:
                        pass
                    collected.append(
                        SourcePostPayload(
                            keyword=keyword,
                            title=title,
                            content=content,
                            likes=max(payload.get("min_likes", 0), 1),
                            favorites=max(payload.get("min_favorites", 0), 1),
                            comments=max(payload.get("min_comments", 0), 1),
                            author="playwright_collector",
                            url=url,
                            tags=[f"#{keyword}", "#playwright"],
                            raw_metrics={"collector_mode": "playwright-live-shell"},
                        )
                    )
                    if len(collected) >= payload.get("max_results", 10):
                        break
                if len(collected) >= payload.get("max_results", 10):
                    break
            context.close()
            browser.close()
        if not collected:
            return self._fallback_collect(payload, reason="no results collected")
        return collected

    def _fallback_collect(self, payload: dict, reason: str) -> list[SourcePostPayload]:
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
            "source_posts": len(posts),
        }
        return posts

    def health(self) -> dict:
        storage_exists = Path(self.settings.playwright_storage_state_path).exists()
        return {
            "status": "ready" if storage_exists or not self.settings.enable_real_collector else "degraded",
            "reason": "playwright safe collector available" if storage_exists or not self.settings.enable_real_collector else "missing storage state",
            "storage_state_exists": storage_exists,
        }

    def diagnostics(self) -> dict:
        return {"provider_type": "safe_playwright", "last_run": self.last_run_metadata}
