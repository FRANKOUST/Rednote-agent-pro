from __future__ import annotations

from app.domain.model_schemas import AnalysisResultSchema, DraftResultSchema, ImagePlanSchema, PromptTemplateDefinition, TopicSuggestionListSchema


_TEMPLATE_REGISTRY = {
    "analyze": PromptTemplateDefinition(
        template_id="analyze",
        version="v2.0",
        stage="analyze",
        input_fields=["posts", "request_context"],
        output_schema=AnalysisResultSchema,
        purpose="将采集结果总结成运营视角分析报告，供选题和起稿复用。",
        system_prompt="你是小红书内容策略分析师，只能输出满足 schema 的 JSON。",
        user_instruction="阅读输入帖子，提炼高频关键词、爆点结构、用户痛点/爽点/关注点、互动诱因、适用赛道和风险提醒。",
        metadata={"category": "analysis"},
    ),
    "topic": PromptTemplateDefinition(
        template_id="topic",
        version="v2.0",
        stage="topic",
        input_fields=["analysis", "request_context"],
        output_schema=TopicSuggestionListSchema,
        purpose="基于分析报告生成可执行的运营选题池。",
        system_prompt="你是小红书选题策划，只能输出满足 schema 的 JSON。",
        user_instruction="生成多个带优先级、目标人群、风险提示和分析依据的选题建议。",
        metadata={"category": "topic"},
    ),
    "draft": PromptTemplateDefinition(
        template_id="draft",
        version="v2.0",
        stage="draft",
        input_fields=["topic", "analysis", "request_context"],
        output_schema=DraftResultSchema,
        purpose="基于分析和选题生成可审核的内容草稿。",
        system_prompt="你是小红书内容主编，只能输出满足 schema 的 JSON。",
        user_instruction="输出主标题、备选标题、正文、标签、CTA、图片建议、风险备注和修订备注。",
        metadata={"category": "draft"},
    ),
    "image": PromptTemplateDefinition(
        template_id="image",
        version="v2.0",
        stage="image",
        input_fields=["draft", "analysis", "request_context"],
        output_schema=ImagePlanSchema,
        purpose="在生成图片前先产出图像规划，便于审核和替换 provider。",
        system_prompt="你是内容配图策划，只能输出满足 schema 的 JSON。",
        user_instruction="输出视觉目标、分镜/画面块、统一 prompt 与资产提示。",
        metadata={"category": "image_plan"},
    ),
}


def list_prompt_templates() -> list[PromptTemplateDefinition]:
    return list(_TEMPLATE_REGISTRY.values())


def get_prompt_template(stage: str) -> PromptTemplateDefinition:
    try:
        return _TEMPLATE_REGISTRY[stage]
    except KeyError as exc:
        raise ValueError(f"Unknown prompt stage: {stage}") from exc


def build_prompt_request(stage: str, **payload) -> dict:
    template = get_prompt_template(stage)
    return {
        "template_id": template.template_id,
        "version": template.version,
        "stage": template.stage,
        "purpose": template.purpose,
        "input_fields": template.input_fields,
        "output_schema": template.output_schema.__name__,
        "payload": payload,
    }
