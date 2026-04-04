from __future__ import annotations

from app.core.config import get_settings
from app.domain.models import AnalysisPayload, DraftPayload, SourcePostPayload, TopicPayload
from app.infrastructure.providers.llm.mock import MockLanguageModelProvider


class OpenAISafeLLMStubProvider:
    name = "openai-safe-llm-stub"

    def __init__(self) -> None:
        self.settings = get_settings()
        self.mock = MockLanguageModelProvider()

    def analyze(self, posts: list[SourcePostPayload]) -> AnalysisPayload:
        return self.mock.analyze(posts)

    def suggest_topics(self, analysis: AnalysisPayload) -> list[TopicPayload]:
        return self.mock.suggest_topics(analysis)

    def generate_draft(self, topic: TopicPayload, analysis: AnalysisPayload) -> DraftPayload:
        return self.mock.generate_draft(topic, analysis)
