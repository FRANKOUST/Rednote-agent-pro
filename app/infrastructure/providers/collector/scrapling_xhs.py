from __future__ import annotations

import html
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from time import perf_counter
from urllib.parse import quote_plus, urlparse

from app.core.config import get_settings
from app.domain.models import CollectorCandidatePayload, SourcePostPayload
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
        started_at = perf_counter()
        logs: list[dict] = []
        try:
            if collection_type == "detail":
                posts = self._collect_detail_mode(payload)
                candidate_count = len(posts)
                detail_hydrated_count = len(posts)
            else:
                candidates = self.collect_candidates(payload)
                hydrated = self._hydrate_candidates(candidates, payload)
                posts = self._filter_posts(hydrated, payload)
                candidate_count = len(candidates)
                detail_hydrated_count = len(hydrated)
            login_state = self._login_state()
            self.last_run_metadata = {
                "status": "completed",
                "mode": "fixture" if self.settings.scrapling_mode != "live" else "live",
                "candidate_count": candidate_count,
                "detail_hydrated_count": detail_hydrated_count,
                "accepted_count": len(posts),
                "login_state": login_state,
                "elapsed_ms": self._elapsed_ms(started_at),
                "logs": logs,
            }
            return posts
        except Exception as exc:
            logs.append({"event": "collector.failed", "error": str(exc)})
            return self._fallback_collect(payload, exc, started_at, logs)

    def collect_candidates(self, payload: dict) -> list[CollectorCandidatePayload]:
        keywords = payload.get("keywords") or self._read_lines(self.settings.scrapling_keywords_file)
        if self.settings.scrapling_mode == "live":
            raise RuntimeError("live scrapling candidate collection not available in test harness")
        html_payload = self._load_fixture_html("search")
        items = self._extract_embedded_state(html_payload).get("items") or []
        candidates: list[CollectorCandidatePayload] = []
        seen_urls: set[str] = set()
        for index, item in enumerate(items or []):
            keyword = item.get("keyword") or (keywords[0] if keywords else "小红书")
            published_at = (datetime.now(timezone.utc) - timedelta(days=30 + index * 5)).date().isoformat()
            candidate = CollectorCandidatePayload(
                keyword=keyword,
                url=item.get("url") or f"https://www.xiaohongshu.com/explore/{item.get('note_id')}",
                author=item.get("author") or "unknown",
                published_at=published_at,
                content_type="image_text",
                is_video=False,
                raw_metrics={"note_id": item.get("note_id"), "collector_mode": "fixture", "stage": "candidate"},
            )
            if candidate.url in seen_urls:
                continue
            seen_urls.add(candidate.url)
            candidates.append(candidate)
        if candidates:
            return candidates[: self.settings.collector_max_candidates]

        regex_candidates: list[CollectorCandidatePayload] = []
        for index, match in enumerate(self._search_card_pattern.finditer(html_payload)):
            groups = match.groupdict()
            url = groups["url"]
            if url in seen_urls:
                continue
            seen_urls.add(url)
            regex_candidates.append(
                CollectorCandidatePayload(
                    keyword=keywords[0] if keywords else "小红书",
                    url=url,
                    author=groups["author"],
                    published_at=(datetime.now(timezone.utc) - timedelta(days=30 + index * 5)).date().isoformat(),
                    content_type="image_text",
                    is_video=False,
                    raw_metrics={"note_id": groups["note_id"], "collector_mode": "fixture", "stage": "candidate"},
                )
            )
        return regex_candidates[: self.settings.collector_max_candidates]

    def _collect_detail_mode(self, payload: dict) -> list[SourcePostPayload]:
        note_ids = payload.get("note_ids") or self._read_lines(self.settings.scrapling_note_ids_file)
        html_payload = self._load_fixture_html("detail")
        embedded_items = self._extract_embedded_state(html_payload).get("items") or []
        posts: list[SourcePostPayload] = []
        for index, note_id in enumerate(note_ids or ["detail-001"]):
            item = next((row for row in embedded_items if row.get("note_id") == note_id), None)
            if item is None:
                detail_match = self._detail_pattern.search(html_payload)
                if not detail_match:
                    continue
                item = detail_match.groupdict()
            posts.append(self._map_detail_item(item, note_id=note_id, keyword=item.get("keyword") or note_id, published_at=(datetime.now(timezone.utc) - timedelta(days=14 + index)).date().isoformat(), detail_source="fixture"))
        return posts

    def _hydrate_candidates(self, candidates: list[CollectorCandidatePayload], payload: dict) -> list[SourcePostPayload]:
        search_html = self._load_fixture_html("search")
        search_items = self._extract_embedded_state(search_html).get("items") or []
        hydrated: list[SourcePostPayload] = []
        for candidate in candidates[: self.settings.collector_max_detail_items]:
            note_id = (candidate.raw_metrics or {}).get("note_id") or self._extract_note_id(candidate.url)
            item = next((row for row in search_items if row.get("note_id") == note_id), None)
            if item is None:
                continue
            hydrated.append(
                self._map_detail_item(
                    item,
                    note_id=note_id,
                    keyword=candidate.keyword,
                    published_at=candidate.published_at,
                    detail_source="fixture",
                )
            )
        return hydrated

    def _filter_posts(self, posts: list[SourcePostPayload], payload: dict) -> list[SourcePostPayload]:
        max_age_days = payload.get("max_age_days", self.settings.collector_max_age_days)
        min_likes = payload.get("min_likes", 0)
        min_favorites = payload.get("min_favorites", 0)
        min_comments = payload.get("min_comments", 0)
        topic_words = [word.lower() for word in payload.get("topic_words") or []]
        seen_urls: set[str] = set()
        accepted: list[SourcePostPayload] = []
        for post in posts:
            if not post.content.strip():
                continue
            if post.url in seen_urls:
                continue
            if post.content_type != "image_text" or post.is_video:
                continue
            if self._is_ad(post):
                continue
            if post.likes < min_likes or post.favorites < min_favorites or post.comments < min_comments:
                continue
            if post.published_at and self._days_since(post.published_at) > max_age_days:
                continue
            if topic_words and not any(word in f"{post.title} {post.content}".lower() for word in topic_words):
                continue
            seen_urls.add(post.url)
            accepted.append(post)
        return accepted

    def check_login(self) -> dict:
        state = self._login_state()
        return {
            "provider": self.name,
            "status": "ready" if state["mode"] in {"fixture", "storage_state", "cookie_fallback"} else "degraded",
            **state,
            "reason": "fixture mode skips login" if state["mode"] == "fixture" else "collector login material checked",
        }

    def health(self) -> dict:
        state = self._login_state()
        if self.settings.scrapling_mode != "live":
            return {
                "status": "ready",
                "reason": "fixture mode active, login not required",
                "runtime_available": self._scrapling_runtime_available(),
                "login_state": state,
            }
        if state["mode"] in {"storage_state", "cookie_fallback"}:
            return {
                "status": "ready",
                "reason": "scrapling login material available",
                "runtime_available": self._scrapling_runtime_available(),
                "login_state": state,
            }
        return {
            "status": "degraded",
            "reason": "scrapling live mode requires storage state or cookies login material",
            "runtime_available": self._scrapling_runtime_available(),
            "login_state": state,
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

    def _map_detail_item(self, item: dict, note_id: str, keyword: str, published_at: str, detail_source: str) -> SourcePostPayload:
        tags = item.get("tags") or []
        if isinstance(tags, str):
            tags = [tag.strip() for tag in tags.split("|") if tag.strip()]
        normalized_tags = [tag if str(tag).startswith("#") else f"#{tag}" for tag in tags]
        title = html.unescape(item.get("title") or item.get("note_title") or "untitled")
        content = html.unescape(item.get("content") or item.get("desc") or "")
        return SourcePostPayload(
            keyword=keyword,
            title=title,
            content=content,
            likes=self._to_int(item.get("likes") or item.get("liked_count")),
            favorites=self._to_int(item.get("favorites") or item.get("collected_count")),
            comments=self._to_int(item.get("comments") or item.get("comment_count")),
            author=html.unescape(item.get("author") or item.get("nickname") or "unknown"),
            url=item.get("url") or f"https://www.xiaohongshu.com/explore/{note_id}",
            tags=normalized_tags,
            published_at=published_at,
            content_type="image_text",
            raw_metrics={
                "note_id": note_id,
                "collector_mode": "fixture" if self.settings.scrapling_mode != "live" else "scrapling-live",
                "detail_source": detail_source,
            },
        )

    def _login_state(self) -> dict:
        if self.settings.scrapling_mode != "live":
            return {"mode": "fixture", "storage_state_path": self.settings.scrapling_storage_state_path, "cookies_path": self.settings.scrapling_cookies_path}
        storage_state_exists = Path(self.settings.scrapling_storage_state_path).exists()
        cookies_exist = Path(self.settings.scrapling_cookies_path).exists()
        if storage_state_exists:
            return {"mode": "storage_state", "storage_state_path": self.settings.scrapling_storage_state_path, "cookies_path": self.settings.scrapling_cookies_path}
        if cookies_exist:
            return {"mode": "cookie_fallback", "storage_state_path": self.settings.scrapling_storage_state_path, "cookies_path": self.settings.scrapling_cookies_path}
        return {"mode": "missing", "storage_state_path": self.settings.scrapling_storage_state_path, "cookies_path": self.settings.scrapling_cookies_path}

    def _fallback_collect(self, payload: dict, exc: Exception | None, started_at: float, logs: list[dict]) -> list[SourcePostPayload]:
        posts = self.mock.collect(payload)
        failure_category = self._classify_failure(exc) if exc else "runtime"
        for post in posts:
            post.raw_metrics = {
                **(post.raw_metrics or {}),
                "collector_mode": "safe-fallback",
                "failure_category": failure_category,
                "fallback_reason": str(exc) if exc else "unknown collector error",
            }
        self.last_run_metadata = {
            "status": "fallback",
            "mode": "safe_fallback",
            "failure_category": failure_category,
            "reason": str(exc) if exc else "unknown collector error",
            "candidate_count": len(self.collect_candidates(payload)) if payload.get("collection_type", "search") != "detail" else len(posts),
            "detail_hydrated_count": len(posts),
            "accepted_count": len(posts),
            "login_state": self._login_state(),
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

    def _is_ad(self, post: SourcePostPayload) -> bool:
        text = f"{post.title} {post.content}".lower()
        return any(keyword.lower() in text for keyword in self.settings.collector_filter_ad_keywords)

    @staticmethod
    def _extract_note_id(url: str) -> str:
        path = urlparse(url).path.rstrip("/")
        return path.split("/")[-1] if path else url

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
    def _days_since(value: str) -> int:
        try:
            then = datetime.fromisoformat(value)
            if then.tzinfo is None:
                then = then.replace(tzinfo=timezone.utc)
            return (datetime.now(timezone.utc) - then).days
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
