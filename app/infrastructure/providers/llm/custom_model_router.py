from __future__ import annotations

from app.domain.models import AnalysisPayload, DraftPayload, ImagePlanPayload, SourcePostPayload, TopicPayload
from app.infrastructure.providers.llm.openai_compatible import OpenAICompatibleLLMProvider
from app.infrastructure.providers.llm.openai_safe_stub import OpenAICompatibleSafeLLMStubProvider


class CustomModelRouterProvider:
    name = "custom-model-router"

    def __init__(self) -> None:
        self.primary = OpenAICompatibleLLMProvider()
        self.safe = OpenAICompatibleSafeLLMStubProvider()
        self.last_run_metadata: dict = {}

    def analyze(self, posts: list[SourcePostPayload]) -> AnalysisPayload:
        result = self.primary.analyze(posts)
        self.last_run_metadata = {"stage": "analyze", "delegate": self.primary.name, "last_run": self.primary.last_run_metadata}
        return result

    def suggest_topics(self, analysis: AnalysisPayload) -> list[TopicPayload]:
        result = self.primary.suggest_topics(analysis)
        self.last_run_metadata = {"stage": "topic", "delegate": self.primary.name, "last_run": self.primary.last_run_metadata}
        return result

    def generate_draft(self, topic: TopicPayload, analysis: AnalysisPayload) -> DraftPayload:
        result = self.primary.generate_draft(topic, analysis)
        self.last_run_metadata = {"stage": "draft", "delegate": self.primary.name, "last_run": self.primary.last_run_metadata}
        return result

    def plan_image(self, draft: DraftPayload, analysis: AnalysisPayload | None = None) -> ImagePlanPayload:
        result = self.primary.plan_image(draft, analysis)
        self.last_run_metadata = {"stage": "image", "delegate": self.primary.name, "last_run": self.primary.last_run_metadata}
        return result

    def health(self) -> dict:
        return self.primary.health()

    def diagnostics(self) -> dict:
        return {"provider_type": "router", "delegate": self.primary.name, "last_run": self.last_run_metadata}
