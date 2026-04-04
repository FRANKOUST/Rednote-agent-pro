from __future__ import annotations

from app.domain.models import SourcePostPayload


class MockCollectorProvider:
    name = "mock-collector"

    def collect(self, payload: dict) -> list[SourcePostPayload]:
        keywords = payload.get("keywords", [])
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
                    url=f"https://www.xiaohongshu.com/explore/{keyword}",
                    tags=[f"#{keyword}", "#干货", "#模板"],
                    raw_metrics={"likes": "320", "favorites": "88", "comments": "19"},
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
                    raw_metrics={"likes": "210", "favorites": "56", "comments": "12"},
                )
            )
        return posts
