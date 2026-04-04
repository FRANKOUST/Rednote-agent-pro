from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from app.domain.models import AnalysisPayload, DraftPayload, ImagePayload, PublishPayload, SourcePostPayload, TopicPayload


@dataclass(slots=True)
class ProviderError:
    code: str
    message: str
    retryable: bool
    context: dict = field(default_factory=dict)


class CollectorProvider(Protocol):
    name: str

    def collect(self, payload: dict) -> list[SourcePostPayload]:
        ...


class LanguageModelProvider(Protocol):
    name: str

    def analyze(self, posts: list[SourcePostPayload]) -> AnalysisPayload:
        ...

    def suggest_topics(self, analysis: AnalysisPayload) -> list[TopicPayload]:
        ...

    def generate_draft(self, topic: TopicPayload, analysis: AnalysisPayload) -> DraftPayload:
        ...


class ImageProvider(Protocol):
    name: str

    def generate(self, draft: DraftPayload) -> ImagePayload:
        ...


class PublisherProvider(Protocol):
    name: str

    def publish(self, draft: DraftPayload) -> PublishPayload:
        ...


class SyncProvider(Protocol):
    name: str

    def sync(self, entity_type: str, payload: dict) -> dict:
        ...
