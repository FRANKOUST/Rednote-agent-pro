from app.domain.model_schemas import (
    AnalysisResultSchema,
    DraftResultSchema,
    ImagePlanSchema,
    PromptTemplateDefinition,
    TopicSuggestionListSchema,
)
from app.infrastructure.providers.llm.prompt_templates import get_prompt_template, list_prompt_templates


def test_analysis_schema_validates_operator_fields() -> None:
    result = AnalysisResultSchema.model_validate(
        {
            "summary": "summary",
            "high_frequency_keywords": ["选题", "开头"],
            "hot_tags": ["#运营"],
            "title_patterns": ["数字清单"],
            "opening_patterns": ["先说结论"],
            "content_structure_templates": ["结论-步骤-CTA"],
            "user_pain_points": ["不知道怎么起标题"],
            "user_delight_points": ["直接拿模板"],
            "user_focus_points": ["收藏价值"],
            "engagement_triggers": ["评论区领取"],
            "applicable_tracks": ["知识IP"],
            "viral_hooks": ["前后对比"],
            "risk_alerts": ["避免夸大承诺"],
        }
    )
    assert result.user_pain_points == ["不知道怎么起标题"]


def test_topic_schema_validates_operator_topic_list() -> None:
    result = TopicSuggestionListSchema.model_validate(
        {
            "topics": [
                {
                    "title": "3个高收藏笔记开头",
                    "reason": "匹配高频开头规律",
                    "target_audience": "新手运营",
                    "reference_hooks": ["先说结论"],
                    "analysis_evidence": ["清单结构高频出现"],
                    "risk_notes": ["避免标题党"],
                    "recommended_format": "清单",
                    "priority": "high",
                    "confidence": 0.86,
                }
            ]
        }
    )
    assert result.topics[0].confidence > 0.8


def test_draft_schema_validates_operator_fields() -> None:
    result = DraftResultSchema.model_validate(
        {
            "headline": "主标题",
            "alternate_headlines": ["备选标题"],
            "body": "正文",
            "tags": ["#运营"],
            "cta": "评论区回复模板",
            "image_suggestions": ["封面做成红白信息卡"],
            "image_prompt": "红白信息卡",
            "content_type": "图文",
            "target_user": "新手运营",
            "tone_style": "直接、利落",
            "risk_notes": ["避免暗示收益"],
            "review_notes": ["需要人工确认案例真实性"],
            "revision_notes": ["加强开头结论"],
        }
    )
    assert result.alternate_headlines[0] == "备选标题"


def test_image_plan_schema_validates() -> None:
    result = ImagePlanSchema.model_validate(
        {
            "visual_goal": "做成高对比封面",
            "frames": ["封面", "内页"],
            "prompt": "小红书封面图，红白配色",
            "asset_notes": ["突出标题"],
        }
    )
    assert result.frames == ["封面", "内页"]


def test_prompt_templates_are_versioned_and_schema_bound() -> None:
    template = get_prompt_template("analyze")
    assert isinstance(template, PromptTemplateDefinition)
    assert template.template_id == "analyze"
    assert template.version.startswith("v")
    assert template.output_schema == AnalysisResultSchema
    assert {item.stage for item in list_prompt_templates()} == {"analyze", "topic", "draft", "image"}
