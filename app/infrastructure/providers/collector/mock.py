from __future__ import annotations

from app.domain.models import SourcePostPayload


class MockCollectorProvider:
    name = "mock-collector"

    def __init__(self) -> None:
        self.last_run_metadata: dict = {}

    def collect(self, payload: dict) -> list[SourcePostPayload]:
        keywords = payload.get("keywords") or ["demo"]
        note_ids = payload.get("note_ids") or []
        min_likes = payload.get("min_likes", 0)
        min_favorites = payload.get("min_favorites", 0)
        min_comments = payload.get("min_comments", 0)
        collection_type = payload.get("collection_type", "search")
        posts: list[SourcePostPayload] = []

        if collection_type == "detail" and note_ids:
            for note_id in note_ids:
                posts.append(
                    SourcePostPayload(
                        keyword=payload.get("keywords", ["detail"])[0] if payload.get("keywords") else "detail",
                        title=f"{note_id} 详情样例",
                        content=f"这是 {note_id} 的详情采集样例内容。",
                        likes=max(520, min_likes),
                        favorites=max(133, min_favorites),
                        comments=max(24, min_comments),
                        author="detail_demo_creator",
                        url=f"https://www.xiaohongshu.com/explore/{note_id}",
                        tags=["#详情", "#样例", "#小规模验证"],
                        raw_metrics={"note_id": note_id, "collector_mode": "mock", "collection_type": "detail"},
                    )
                )
        else:
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
                        url=f"https://www.xiaohongshu.com/explore/{keyword}",
                        tags=[f"#{keyword}", "#干货", "#模板"],
                        raw_metrics={"likes": "320", "favorites": "88", "comments": "19", "collector_mode": "mock", "collection_type": "search"},
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
                        raw_metrics={"likes": "210", "favorites": "56", "comments": "12", "collector_mode": "mock", "collection_type": "search"},
                    )
                )

        self.last_run_metadata = {
            "status": "completed",
            "mode": "mock",
            "collection_type": collection_type,
            "source_posts": len(posts),
        }
        return posts

    def health(self) -> dict:
        return {"status": "ready", "reason": "mock collector available"}

    def diagnostics(self) -> dict:
        return {"provider_type": "mock", "last_run": self.last_run_metadata}
