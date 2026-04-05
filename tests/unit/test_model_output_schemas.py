from app.domain.model_schemas import AnalysisResultSchema, DraftResultSchema, TopicSuggestionListSchema
from app.infrastructure.providers.llm.prompt_templates import (
    ANALYSIS_PROMPT_VERSION,
    DRAFT_PROMPT_VERSION,
    TOPIC_PROMPT_VERSION,
    build_analysis_prompt,
    build_draft_prompt,
    build_topic_prompt,
)


def test_analysis_schema_validates_expected_shape() -> None:
    result = AnalysisResultSchema.model_validate(
        {
            "summary": "summary",
            "top_keywords": ["a"],
            "top_tags": ["#x"],
            "title_patterns": ["list"],
            "audience_insights": ["insight"],
        }
    )
    assert result.summary == "summary"


def test_topic_schema_validates_topic_list() -> None:
    result = TopicSuggestionListSchema.model_validate(
        {"topics": [{"title": "t", "rationale": "r", "angle": "a"}]}
    )
    assert result.topics[0].title == "t"


def test_draft_schema_validates_expected_shape() -> None:
    result = DraftResultSchema.model_validate(
        {
            "title": "t",
            "body": "body",
            "tags": ["#x"],
            "cta": "cta",
            "image_prompt": "img",
            "content_type": "note",
        }
    )
    assert result.content_type == "note"


def test_prompt_templates_embed_versions() -> None:
    assert build_analysis_prompt([])["version"] == ANALYSIS_PROMPT_VERSION
    assert build_topic_prompt({})["version"] == TOPIC_PROMPT_VERSION
    assert build_draft_prompt({}, {})["version"] == DRAFT_PROMPT_VERSION
