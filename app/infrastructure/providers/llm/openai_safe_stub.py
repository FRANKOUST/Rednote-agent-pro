from __future__ import annotations

from app.core.config import get_settings
from app.domain.models import AnalysisPayload, DraftPayload, ImagePlanPayload, SourcePostPayload, TopicPayload
from app.infrastructure.providers.llm.mock import MockLanguageModelProvider


class OpenAICompatibleSafeLLMStubProvider:
    name = "openai-compatible-safe-llm"

    def __init__(self) -> None:
        self.settings = get_settings()
        self.mock = MockLanguageModelProvider()

    def analyze(self, posts: list[SourcePostPayload]) -> AnalysisPayload:
        return self.mock.analyze(posts)

    def suggest_topics(self, analysis: AnalysisPayload) -> list[TopicPayload]:
        return self.mock.suggest_topics(analysis)

    def generate_draft(self, topic: TopicPayload, analysis: AnalysisPayload) -> DraftPayload:
        return self.mock.generate_draft(topic, analysis)

    def plan_image(self, draft: DraftPayload, analysis: AnalysisPayload | None = None) -> ImagePlanPayload:
        return self.mock.plan_image(draft, analysis)

    def health(self) -> dict:
        return {"status": "ready", "reason": "safe llm stub available"}

    def diagnostics(self) -> dict:
        return {
            "provider_type": "safe_stub",
            "model_name": self.settings.resolved_model_name,
            "base_url": self.settings.resolved_model_base_url,
            "last_run": self.mock.last_run_metadata,
        }
