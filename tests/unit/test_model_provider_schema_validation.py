from app.domain.model_schemas import AnalysisResultSchema, DraftResultSchema, TopicSuggestionListSchema


def test_model_output_schemas_validate_expected_shapes() -> None:
    assert AnalysisResultSchema.model_validate({"summary": "summary", "top_keywords": ["a"], "top_tags": ["#x"], "title_patterns": ["list"], "audience_insights": ["insight"]}).summary == "summary"
    assert TopicSuggestionListSchema.model_validate({"topics": [{"title": "t", "rationale": "r", "angle": "a"}]}).topics[0].title == "t"
    assert DraftResultSchema.model_validate({"title": "t", "body": "body", "tags": ["#x"], "cta": "cta", "image_prompt": "img", "content_type": "note"}).content_type == "note"


def test_openai_compatible_provider_falls_back_when_schema_is_invalid(monkeypatch) -> None:
    from app.infrastructure.providers.llm.openai_compatible import OpenAICompatibleLLMProvider

    provider = OpenAICompatibleLLMProvider()
    monkeypatch.setattr(provider, "_chat_json", lambda stage, payload: {"oops": "bad-shape"})

    result = provider.analyze([])

    assert result.summary
    assert provider.last_run_metadata["mode"] == "fallback"
