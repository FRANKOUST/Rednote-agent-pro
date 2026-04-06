from __future__ import annotations

import html
import json
import re
from pathlib import Path
from time import perf_counter
from urllib.parse import quote_plus

from app.core.config import get_settings
from app.domain.models import SourcePostPayload
from app.infrastructure.providers.collector.mock import MockCollectorProvider


class ScraplingXhsCollectorProvider:
    name = "scrapling-xhs-collector"

    _script_pattern = re.compile(r'<script[^>]*id=["\']__XHS_DATA__["\'][^>]*>(?P<data>.*?)</script>', re.IGNORECASE | re.DOTALL)
    _search_card_pattern = re.compile(
        r'<(?:section|article|div)[^>]*class=["\'][^"\']*note-item[^"\']*["\'][^>]*'
        r'data-note-id=["\'](?P<note_id>[^"\']+)["\'][^>]*'
        r'data-title=["\'](?P<title>[^"\']+)["\'][^>]*'
        r'data-author=["\'](?P<author>[^"\']+)["\'][^>]*'
        r'data-likes=["\'](?P<likes>[^"\']+)["\'][^>]*'
        r'data-favorites=["\'](?P<favorites>[^"\']+)["\'][^>]*'
        r'data-comments=["\'](?P<comments>[^"\']+)["\'][^>]*'
        r'data-url=["\'](?P<url>[^"\']+)["\'][^>]*'
        r'data-content=["\'](?P<content>[^"\']*)["\'][^>]*'
        r'data-tags=["\'](?P<tags>[^"\']*)["\']',
        re.IGNORECASE | re.DOTALL,
    )
    _detail_pattern = re.compile(
        r'<article[^>]*id=["\']note-detail["\'][^>]*'
        r'data-note-id=["\'](?P<note_id>[^"\']+)["\'][^>]*'
        r'data-title=["\'](?P<title>[^"\']+)["\'][^>]*'
        r'data-author=["\'](?P<author>[^"\']+)["\'][^>]*'
        r'data-likes=["\'](?P<likes>[^"\']+)["\'][^>]*'
        r'data-favorites=["\'](?P<favorites>[^"\']+)["\'][^>]*'
        r'data-comments=["\'](?P<comments>[^"\']+)["\'][^>]*'
        r'data-url=["\'](?P<url>[^"\']+)["\'][^>]*'
        r'data-content=["\'](?P<content>.*?)["\'][^>]*'
        r'data-tags=["\'](?P<tags>[^"\']*)["\']',
        re.IGNORECASE | re.DOTALL,
    )

    def __init__(self) -> None:
        self.settings = get_settings()
        self.fixture_dir = Path(self.settings.scrapling_fixture_dir)
        self.fixture_dir.mkdir(parents=True, exist_ok=True)
        self.mock = MockCollectorProvider()
        self.last_run_metadata: dict = {}

    def collect(self, payload: dict) -> list[SourcePostPayload]:
        collection_type = payload.get("collection_type", "search")
        dry_run = bool(payload.get("dry_run", self.settings.scrapling_mode != "live"))
        started_at = perf_counter()
        request_keywords = payload.get("keywords") or self._read_lines(self.settings.scrapling_keywords_file)
        request_note_ids = payload.get("note_ids") or self._read_lines(self.settings.scrapling_note_ids_file)
        logs = [
            {
                "event": "collector.request.accepted",
                "provider": self.name,
                "collection_type": collection_type,
                "dry_run": dry_run,
                "keywords": request_keywords,
                "note_ids": request_note_ids,
            }
        ]

        if dry_run:
            html_payload = self._load_fixture_html(collection_type)
            posts = self._extract_posts(collection_type, html_payload, request_keywords, request_note_ids)
            self.last_run_metadata = {
                "status": "completed",
                "mode": "fixture",
                "dry_run": True,
                "collection_type": collection_type,
                "attempts": 1,
                "source_posts": len(posts),
                "elapsed_ms": self._elapsed_ms(started_at),
                "logs": logs,
            }
            for post in posts:
                post.raw_metrics = {**(post.raw_metrics or {}), "collector_mode": "fixture", "safe_mode": True}
            return posts

        max_attempts = max(1, self.settings.scrapling_max_retries + 1)
        last_error: Exception | None = None
        for attempt in range(1, max_attempts + 1):
            try:
                document = self._fetch_live_document(collection_type, request_keywords, request_note_ids)
                posts = self._extract_posts(collection_type, document, request_keywords, request_note_ids)
                if not posts:
                    raise ValueError("scrapling returned no structured posts")
                self.last_run_metadata = {
                    "status": "completed",
                    "mode": "live",
                    "dry_run": False,
                    "collection_type": collection_type,
                    "attempts": attempt,
                    "source_posts": len(posts),
                    "elapsed_ms": self._elapsed_ms(started_at),
                    "logs": logs + [{"event": "collector.fetch.completed", "attempt": attempt}],
                }
                for post in posts:
                    post.raw_metrics = {**(post.raw_metrics or {}), "collector_mode": "scrapling-live", "safe_mode": False}
                return posts
            except Exception as exc:
                last_error = exc
                logs.append(
                    {
                        "event": "collector.fetch.failed",
                        "attempt": attempt,
                        "failure_category": self._classify_failure(exc),
                        "error": str(exc),
                    }
                )

        return self._fallback_collect(payload, last_error, started_at, logs)

    def health(self) -> dict:
        runtime_ready = self._scrapling_runtime_available()
        cookies_exist = Path(self.settings.scrapling_cookies_path).exists()
        storage_state_exists = Path(self.settings.scrapling_storage_state_path).exists()
        if self.settings.scrapling_mode != "live":
            return {
                "status": "ready",
                "reason": "fixture/safe scrapling mode active",
                "runtime_available": runtime_ready,
                "cookies_path_exists": cookies_exist,
                "storage_state_exists": storage_state_exists,
            }
        if runtime_ready and (cookies_exist or storage_state_exists):
            return {
                "status": "ready",
                "reason": "scrapling runtime and login material available",
                "runtime_available": runtime_ready,
                "cookies_path_exists": cookies_exist,
                "storage_state_exists": storage_state_exists,
            }
        return {
            "status": "degraded",
            "reason": "scrapling live mode requires runtime plus cookies or storage state",
            "runtime_available": runtime_ready,
            "cookies_path_exists": cookies_exist,
            "storage_state_exists": storage_state_exists,
        }

    def diagnostics(self) -> dict:
        return {
            "provider_type": "scrapling_xhs",
            "mode": self.settings.scrapling_mode,
            "timeout_seconds": self.settings.scrapling_timeout_seconds,
            "max_retries": self.settings.scrapling_max_retries,
            "adaptive_selectors": self.settings.scrapling_adaptive_selectors,
            "headless": self.settings.scrapling_headless,
            "network_idle": self.settings.scrapling_network_idle,
            "fixture_dir": str(self.fixture_dir),
            "last_run": self.last_run_metadata,
        }

    def _fetch_live_document(self, collection_type: str, keywords: list[str], note_ids: list[str]):
        try:
            from scrapling.fetchers import Fetcher, PlayWrightFetcher  # type: ignore
        except Exception as exc:  # pragma: no cover - depends on local runtime
            raise RuntimeError("scrapling runtime not installed") from exc

        if collection_type == "detail":
            target = note_ids[0] if note_ids else "fixture-note"
            url = f"https://www.xiaohongshu.com/explore/{target}"
        else:
            keyword = quote_plus((keywords[0] if keywords else "小红书"))
            url = f"https://www.xiaohongshu.com/search_result?keyword={keyword}"

        if self.settings.scrapling_headless:
            return PlayWrightFetcher.fetch(  # pragma: no cover - depends on local runtime
                url,
                headless=self.settings.scrapling_headless,
                network_idle=self.settings.scrapling_network_idle,
            )

        fetcher = Fetcher(auto_match=self.settings.scrapling_adaptive_selectors)  # pragma: no cover - depends on local runtime
        return fetcher.get(url, stealthy_headers=True)

    def _extract_posts(
        self,
        collection_type: str,
        document,
        keywords: list[str],
        note_ids: list[str],
    ) -> list[SourcePostPayload]:
        html_payload = self._document_to_html(document)
        embedded = self._extract_embedded_state(html_payload)
        if collection_type == "detail":
            items = embedded.get("items") or embedded.get("data") or []
            if items:
                item = items[0]
                note_id = note_ids[0] if note_ids else item.get("note_id", "detail")
                return [self._map_item(item, keywords[0] if keywords else note_id, "detail")]
            match = self._detail_pattern.search(html_payload)
            if match:
                return [self._map_item(match.groupdict(), keywords[0] if keywords else match.group("note_id"), "detail")]
            raise ValueError("detail extractor found no note")

        items = embedded.get("items") or embedded.get("data") or []
        if items:
            keyword = keywords[0] if keywords else "小红书"
            return [self._map_item(item, keyword, "search") for item in items]

        keyword = keywords[0] if keywords else "小红书"
        regex_items = [self._map_item(match.groupdict(), keyword, "search") for match in self._search_card_pattern.finditer(html_payload)]
        if regex_items:
            return regex_items
        raise ValueError("search extractor found no cards")

    def _map_item(self, item: dict, keyword: str, collection_type: str) -> SourcePostPayload:
        note_id = item.get("note_id") or item.get("id") or item.get("noteId") or "unknown"
        tags = item.get("tags") or item.get("tag_list") or []
        if isinstance(tags, str):
            tags = [tag.strip() for tag in tags.split("|") if tag.strip()]
        normalized_tags = [tag if str(tag).startswith("#") else f"#{tag}" for tag in tags]
        return SourcePostPayload(
            keyword=keyword,
            title=html.unescape(item.get("title") or item.get("note_title") or "untitled"),
            content=html.unescape(item.get("content") or item.get("desc") or ""),
            likes=self._to_int(item.get("likes") or item.get("liked_count")),
            favorites=self._to_int(item.get("favorites") or item.get("collected_count")),
            comments=self._to_int(item.get("comments") or item.get("comment_count")),
            author=html.unescape(item.get("author") or item.get("nickname") or "unknown"),
            url=item.get("url") or item.get("note_url") or f"https://www.xiaohongshu.com/explore/{note_id}",
            tags=normalized_tags,
            raw_metrics={
                "note_id": note_id,
                "collection_type": collection_type,
                "keyword": keyword,
                "adaptive_selectors": self.settings.scrapling_adaptive_selectors,
            },
        )

    def _fallback_collect(self, payload: dict, exc: Exception | None, started_at: float, logs: list[dict]) -> list[SourcePostPayload]:
        posts = self.mock.collect(payload)
        failure_category = self._classify_failure(exc) if exc else "runtime"
        for post in posts:
            post.raw_metrics = {
                **(post.raw_metrics or {}),
                "collector_mode": "safe-fallback",
                "safe_mode": True,
                "failure_category": failure_category,
                "fallback_reason": str(exc) if exc else "unknown collector error",
            }
        self.last_run_metadata = {
            "status": "fallback",
            "mode": "safe_fallback",
            "dry_run": bool(payload.get("dry_run")),
            "failure_category": failure_category,
            "reason": str(exc) if exc else "unknown collector error",
            "source_posts": len(posts),
            "elapsed_ms": self._elapsed_ms(started_at),
            "logs": logs,
        }
        return posts

    def _load_fixture_html(self, collection_type: str) -> str:
        fixture_name = "detail_result.html" if collection_type == "detail" else "search_result.html"
        fixture_path = self.fixture_dir / fixture_name
        if not fixture_path.exists():
            raise FileNotFoundError(f"fixture missing: {fixture_path}")
        return fixture_path.read_text(encoding="utf-8")

    def _extract_embedded_state(self, html_payload: str) -> dict:
        match = self._script_pattern.search(html_payload)
        if not match:
            return {}
        try:
            return json.loads(html.unescape(match.group("data")))
        except json.JSONDecodeError:
            return {}

    def _document_to_html(self, document) -> str:
        for attribute in ("html", "html_content", "content", "body", "text"):
            value = getattr(document, attribute, None)
            if isinstance(value, str) and value.strip():
                return value
        return str(document)

    def _scrapling_runtime_available(self) -> bool:
        try:
            from scrapling.fetchers import Fetcher  # type: ignore # noqa: F401
            return True
        except Exception:
            return False

    @staticmethod
    def _read_lines(path: str) -> list[str]:
        file_path = Path(path)
        if not path or not file_path.exists():
            return []
        return [line.strip() for line in file_path.read_text(encoding="utf-8").splitlines() if line.strip()]

    @staticmethod
    def _to_int(value) -> int:
        raw = str(value or "0").strip().lower().replace(",", "")
        if raw.endswith("w"):
            try:
                return int(float(raw[:-1]) * 10000)
            except Exception:
                return 0
        try:
            return int(float(raw))
        except Exception:
            return 0

    @staticmethod
    def _classify_failure(exc: Exception | None) -> str:
        if exc is None:
            return "unknown"
        message = str(exc).lower()
        if "timeout" in message:
            return "timeout"
        if "fixture" in message or "installed" in message or "runtime" in message:
            return "dependency"
        if "extract" in message or "structured" in message or "note" in message or "cards" in message:
            return "parse"
        return "runtime"

    @staticmethod
    def _elapsed_ms(started_at: float) -> int:
        return int((perf_counter() - started_at) * 1000)
