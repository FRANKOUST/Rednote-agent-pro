from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class AnalysisResultSchema(BaseModel):
    summary: str = Field(min_length=1)
    high_frequency_keywords: list[str] = Field(default_factory=list)
    hot_tags: list[str] = Field(default_factory=list)
    title_patterns: list[str] = Field(default_factory=list)
    opening_patterns: list[str] = Field(default_factory=list)
    content_structure_templates: list[str] = Field(default_factory=list)
    user_pain_points: list[str] = Field(default_factory=list)
    user_delight_points: list[str] = Field(default_factory=list)
    user_focus_points: list[str] = Field(default_factory=list)
    engagement_triggers: list[str] = Field(default_factory=list)
    applicable_tracks: list[str] = Field(default_factory=list)
    viral_hooks: list[str] = Field(default_factory=list)
    risk_alerts: list[str] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def support_legacy_shape(cls, data: Any):
        if isinstance(data, dict):
            data = dict(data)
            data.setdefault("high_frequency_keywords", data.get("top_keywords", []))
            data.setdefault("hot_tags", data.get("top_tags", []))
            data.setdefault("opening_patterns", data.get("title_patterns", []))
            data.setdefault("content_structure_templates", ["结论-步骤-CTA"] if data.get("title_patterns") else [])
            data.setdefault("user_pain_points", data.get("audience_insights", []))
            data.setdefault("user_delight_points", data.get("audience_insights", []))
            data.setdefault("user_focus_points", data.get("audience_insights", []))
            data.setdefault("engagement_triggers", ["评论区交流"] if data.get("audience_insights") else [])
            data.setdefault("applicable_tracks", ["通用内容运营"])
            data.setdefault("viral_hooks", data.get("title_patterns", []))
            data.setdefault("risk_alerts", ["避免夸大承诺"])
        return data


class TopicSuggestionItemSchema(BaseModel):
    title: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    target_audience: str = Field(min_length=1)
    reference_hooks: list[str] = Field(default_factory=list)
    analysis_evidence: list[str] = Field(default_factory=list)
    risk_notes: list[str] = Field(default_factory=list)
    recommended_format: str = Field(min_length=1)
    priority: str = Field(default="medium", pattern="^(high|medium|low)$")
    confidence: float = Field(default=0.7, ge=0, le=1)

    @model_validator(mode="before")
    @classmethod
    def support_legacy_shape(cls, data: Any):
        if isinstance(data, dict):
            data = dict(data)
            data.setdefault("reason", data.get("rationale", ""))
            data.setdefault("target_audience", "通用创作者")
            data.setdefault("reference_hooks", [data.get("angle", "")] if data.get("angle") else [])
            data.setdefault("analysis_evidence", [data.get("rationale", "")] if data.get("rationale") else [])
            data.setdefault("recommended_format", data.get("angle", "清单") or "清单")
        return data


class TopicSuggestionListSchema(BaseModel):
    topics: list[TopicSuggestionItemSchema] = Field(min_length=1)


class DraftResultSchema(BaseModel):
    headline: str = Field(min_length=1)
    alternate_headlines: list[str] = Field(default_factory=list)
    body: str = Field(min_length=1)
    tags: list[str] = Field(default_factory=list)
    cta: str = Field(min_length=1)
    image_suggestions: list[str] = Field(default_factory=list)
    image_prompt: str = Field(min_length=1)
    content_type: str = Field(min_length=1)
    target_user: str = Field(default="通用用户")
    tone_style: str = Field(default="直接")
    risk_notes: list[str] = Field(default_factory=list)
    review_notes: list[str] = Field(default_factory=list)
    revision_notes: list[str] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def support_legacy_shape(cls, data: Any):
        if isinstance(data, dict):
            data = dict(data)
            data.setdefault("headline", data.get("title", ""))
            data.setdefault("alternate_headlines", [data.get("title", "")] if data.get("title") else [])
            data.setdefault("image_suggestions", ["封面突出主标题"] if data.get("image_prompt") else [])
        return data


class ImagePlanSchema(BaseModel):
    visual_goal: str = Field(min_length=1)
    frames: list[str] = Field(min_length=1)
    prompt: str = Field(min_length=1)
    asset_notes: list[str] = Field(default_factory=list)


class PromptTemplateDefinition(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    template_id: str
    version: str
    stage: str
    input_fields: list[str]
    output_schema: type[BaseModel]
    purpose: str
    system_prompt: str
    user_instruction: str
    metadata: dict[str, Any] = Field(default_factory=dict)
