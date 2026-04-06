from __future__ import annotations

from collections import Counter

from app.domain.models import AnalysisPayload, DraftPayload, SourcePostPayload, TopicPayload


class MockLanguageModelProvider:
    name = "mock-llm"

    def __init__(self) -> None:
        self.last_run_metadata: dict = {}

    def analyze(self, posts: list[SourcePostPayload]) -> AnalysisPayload:
        tokens = Counter()
        tags = Counter()
        for post in posts:
            tokens.update(post.title.replace(" ", ""))
            tags.update(post.tags)
        top_keywords = [item for item, _ in tokens.most_common(5)]
        top_tags = [item for item, _ in tags.most_common(5)]
        self.last_run_metadata = {"stage": "analyze", "source_posts": len(posts)}
        return AnalysisPayload(
            summary="高互动内容集中在清单化表达、避坑建议和结果对比。",
            top_keywords=top_keywords,
            top_tags=top_tags,
            title_patterns=["数字清单", "避坑指南", "前后对比"],
            audience_insights=["用户希望快速获得模板", "用户对真实体验和踩坑成本敏感"],
        )

    def suggest_topics(self, analysis: AnalysisPayload) -> list[TopicPayload]:
        base = analysis.top_tags[0] if analysis.top_tags else "#灵感"
        self.last_run_metadata = {"stage": "suggest_topics", "top_tags": analysis.top_tags[:3]}
        return [
            TopicPayload(
                title="3个可直接套用的小红书爆款选题模板",
                rationale="把高频清单化表达转成可复制内容框架，适合新手起号。",
                angle=f"围绕 {base} 输出结构化模板。",
            ),
            TopicPayload(
                title="为什么你的内容没人收藏：5个最常见结构问题",
                rationale="结合避坑与对比类内容模式，强化收藏动机。",
                angle="从结构缺陷切入，提高互动率。",
            ),
        ]

    def generate_draft(self, topic: TopicPayload, analysis: AnalysisPayload) -> DraftPayload:
        tag = analysis.top_tags[0] if analysis.top_tags else "#小红书运营"
        self.last_run_metadata = {"stage": "generate_draft", "topic": topic.title}
        return DraftPayload(
            title=topic.title,
            body=(
                f"如果你最近也在做 {topic.title} 相关内容，这条可以直接收藏。\n"
                "我把爆款笔记里反复出现的结构拆成了一个简单模板：\n"
                "1. 开头先给结果\n2. 中间用清单写方法\n3. 结尾给行动建议\n"
                "这样更容易被用户收藏和复用。"
            ),
            tags=[tag, "#内容运营", "#模板"],
            cta="你最想先试哪一种写法？评论区告诉我。",
            image_prompt=f"小红书风格信息卡片，主题：{topic.title}，红白配色，清爽排版。",
            content_type="note",
        )

    def health(self) -> dict:
        return {"status": "ready", "reason": "mock llm available"}

    def diagnostics(self) -> dict:
        return {"provider_type": "mock", "last_run": self.last_run_metadata}
