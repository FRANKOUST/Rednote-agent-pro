from __future__ import annotations

from collections import Counter

from app.domain.models import AnalysisPayload, DraftPayload, ImagePlanPayload, SourcePostPayload, TopicPayload


class MockLanguageModelProvider:
    name = "mock-llm"

    def __init__(self) -> None:
        self.last_run_metadata: dict = {}

    def analyze(self, posts: list[SourcePostPayload]) -> AnalysisPayload:
        title_tokens = Counter()
        tags = Counter()
        for post in posts:
            title_tokens.update([token for token in post.title.replace("#", " ").replace("，", " ").split() if token])
            tags.update(post.tags)
        top_keywords = [item for item, _ in title_tokens.most_common(5)] or ["模板", "清单"]
        top_tags = [item for item, _ in tags.most_common(5)] or ["#小红书运营", "#内容策略"]
        self.last_run_metadata = {"stage": "analyze", "source_posts": len(posts)}
        return AnalysisPayload(
            summary="高互动内容集中在结论先行、清单拆解、避坑提醒和可复制模板。",
            high_frequency_keywords=top_keywords,
            hot_tags=top_tags,
            title_patterns=["数字清单", "避坑指南", "结果前置"],
            opening_patterns=["先说结论", "直接给模板", "先晒结果再拆方法"],
            content_structure_templates=["结论-拆解-行动建议", "痛点-方案-案例-CTA"],
            user_pain_points=["不知道标题怎么写", "内容没有收藏点"],
            user_delight_points=["能直接套用模板", "读完马上能执行"],
            user_focus_points=["收藏价值", "真实体验", "执行成本"],
            engagement_triggers=["评论区领取模板", "留下你的问题"],
            applicable_tracks=["知识IP", "产品种草", "技能教学"],
            viral_hooks=["前后对比", "三步拆解", "避坑清单"],
            risk_alerts=["避免夸大承诺", "避免暗示保收益"],
        )

    def suggest_topics(self, analysis: AnalysisPayload) -> list[TopicPayload]:
        tag = analysis.hot_tags[0] if analysis.hot_tags else "#内容运营"
        self.last_run_metadata = {"stage": "topic", "top_tags": analysis.hot_tags[:3]}
        return [
            TopicPayload(
                title="3个高收藏小红书开头公式",
                reason="对应高频开头句式和结论前置规律，适合快速复制。",
                target_audience="新手运营",
                reference_hooks=analysis.opening_patterns[:2],
                analysis_evidence=analysis.content_structure_templates[:2],
                risk_notes=analysis.risk_alerts[:1],
                recommended_format="清单",
                priority="high",
                confidence=0.88,
                angle=f"围绕 {tag} 做模板拆解",
            ),
            TopicPayload(
                title="为什么你的笔记没人收藏：5个结构问题",
                reason="直接响应用户痛点和互动引导规律，适合作为避坑内容。",
                target_audience="想提升转化的创作者",
                reference_hooks=analysis.viral_hooks[:2],
                analysis_evidence=analysis.user_pain_points[:2],
                risk_notes=analysis.risk_alerts[:1],
                recommended_format="避坑",
                priority="medium",
                confidence=0.81,
                angle="用结构诊断切入收藏率问题",
            ),
        ]

    def generate_draft(self, topic: TopicPayload, analysis: AnalysisPayload) -> DraftPayload:
        self.last_run_metadata = {"stage": "draft", "topic": topic.title}
        return DraftPayload(
            headline=topic.title,
            alternate_headlines=[f"先别发笔记，先看这份{topic.title}", f"{topic.title}：新手也能直接照抄"],
            body=(
                f"如果你最近也在做《{topic.title}》相关内容，这条建议先收藏。\n"
                "我把高互动笔记里反复出现的结构拆成了一个更好执行的版本：\n"
                "1. 开头先给结论和结果\n2. 中间按清单拆动作\n3. 结尾用互动问题把评论拉起来\n"
                "你只要按这个顺序写，内容的收藏率通常会比平铺直叙更高。"
            ),
            tags=[analysis.hot_tags[0] if analysis.hot_tags else "#小红书运营", "#内容运营", "#模板"],
            cta="你更想先拿标题模板还是正文结构？评论区告诉我。",
            image_suggestions=["封面用红白信息卡突出主标题", "第二张图放步骤清单"],
            image_prompt=f"小红书风格封面，主题：{topic.title}，红白高对比信息卡，清爽排版。",
            content_type="图文",
            target_user=topic.target_audience,
            tone_style="直接、利落、可执行",
            risk_notes=topic.risk_notes,
            review_notes=["发布前确认案例和数据表达不过度承诺"],
            revision_notes=["二次修改时优先加强开头结论和 CTA"],
        )

    def plan_image(self, draft: DraftPayload, analysis: AnalysisPayload | None = None) -> ImagePlanPayload:
        self.last_run_metadata = {"stage": "image", "headline": draft.headline}
        return ImagePlanPayload(
            visual_goal="把主结论做成一眼可收藏的信息卡",
            frames=["封面", "步骤页"],
            prompt=draft.image_prompt,
            asset_notes=draft.image_suggestions,
        )

    def health(self) -> dict:
        return {"status": "ready", "reason": "mock llm available"}

    def diagnostics(self) -> dict:
        return {"provider_type": "mock", "last_run": self.last_run_metadata}
