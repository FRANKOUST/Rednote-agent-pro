from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.domain.models import CollectorCandidatePayload, SourcePostPayload


class MockCollectorProvider:
    name = "mock-collector"

    def __init__(self) -> None:
        self.last_run_metadata: dict = {}

    def collect_candidates(self, payload: dict) -> list[CollectorCandidatePayload]:
        keywords = payload.get("keywords") or ["demo"]
        candidates: list[CollectorCandidatePayload] = []
        for keyword in keywords:
            for suffix, author in [("template", "demo_creator"), ("guide", "demo_reviewer")]:
                candidates.append(
                    CollectorCandidatePayload(
                        keyword=keyword,
                        url=f"https://www.xiaohongshu.com/explore/{keyword}-{suffix}",
                        author=author,
                        published_at=(datetime.now(timezone.utc) - timedelta(days=21)).date().isoformat(),
                        content_type="image_text",
                        raw_metrics={"note_id": f"{keyword}-{suffix}", "collection_type": "candidate"},
                    )
                )
        return candidates

    def collect(self, payload: dict) -> list[SourcePostPayload]:
        keywords = payload.get("keywords") or ["demo"]
        min_likes = payload.get("min_likes", 0)
        min_favorites = payload.get("min_favorites", 0)
        min_comments = payload.get("min_comments", 0)
        posts: list[SourcePostPayload] = []
        for keyword in keywords:
            posts.append(
                SourcePostPayload(
                    keyword=keyword,
                    title=f"{keyword} 爆款笔记拆解",
                    content=f"围绕 {keyword} 的高互动小红书内容，强调清单、体验和对比。",
                    likes=max(320, min_likes),
                    favorites=max(88, min_favorites),
                    comments=max(19, min_comments),
                    author="demo_creator",
                    url=f"https://www.xiaohongshu.com/explore/{keyword}-template",
                    tags=[f"#{keyword}", "#干货", "#模板"],
                    published_at=(datetime.now(timezone.utc) - timedelta(days=21)).date().isoformat(),
                    content_type="image_text",
                    raw_metrics={"note_id": f"{keyword}-template", "collector_mode": "mock", "detail_source": "fixture"},
                )
            )
            posts.append(
                SourcePostPayload(
                    keyword=keyword,
                    title=f"{keyword} 新手避坑指南",
                    content=f"说明用户在 {keyword} 决策时最担心的坑点、预算和效果差异。",
                    likes=max(210, min_likes),
                    favorites=max(56, min_favorites),
                    comments=max(12, min_comments),
                    author="demo_reviewer",
                    url=f"https://www.xiaohongshu.com/explore/{keyword}-guide",
                    tags=[f"#{keyword}", "#避坑", "#经验分享"],
                    published_at=(datetime.now(timezone.utc) - timedelta(days=18)).date().isoformat(),
                    content_type="image_text",
                    raw_metrics={"note_id": f"{keyword}-guide", "collector_mode": "mock", "detail_source": "fixture"},
                )
            )

        self.last_run_metadata = {
            "status": "completed",
            "mode": "mock",
            "candidate_count": len(self.collect_candidates(payload)),
            "detail_hydrated_count": len(posts),
            "accepted_count": len(posts),
            "login_state": {"mode": "fixture"},
        }
        return posts

    def check_login(self) -> dict:
        return {"provider": self.name, "status": "ready", "mode": "fixture", "reason": "mock collector does not require login"}

    def health(self) -> dict:
        return {"status": "ready", "reason": "mock collector available"}

    def diagnostics(self) -> dict:
        return {"provider_type": "mock", "last_run": self.last_run_metadata}
