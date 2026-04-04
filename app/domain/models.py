from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class StringEnum(str, Enum):
    pass


class WorkflowRunStatus(StringEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ContentDraftStatus(StringEnum):
    CREATED = "created"
    GENERATED = "generated"
    REVIEW_PENDING = "review_pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    PUBLISH_READY = "publish_ready"
    PUBLISHED = "published"


class PublishJobStatus(StringEnum):
    QUEUED = "queued"
    PREPARING = "preparing"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"

    @property
    def is_terminal(self) -> bool:
        return self in {self.PUBLISHED, self.FAILED, self.CANCELLED}


class SyncStatus(StringEnum):
    PENDING = "pending"
    SYNCED = "synced"
    FAILED = "failed"


def transition_draft_status(current: ContentDraftStatus, action: str) -> ContentDraftStatus:
    transitions = {
        (ContentDraftStatus.CREATED, "generate"): ContentDraftStatus.GENERATED,
        (ContentDraftStatus.GENERATED, "submit_for_review"): ContentDraftStatus.REVIEW_PENDING,
        (ContentDraftStatus.REVIEW_PENDING, "approve"): ContentDraftStatus.APPROVED,
        (ContentDraftStatus.REVIEW_PENDING, "reject"): ContentDraftStatus.REJECTED,
        (ContentDraftStatus.APPROVED, "mark_publish_ready"): ContentDraftStatus.PUBLISH_READY,
        (ContentDraftStatus.PUBLISH_READY, "publish"): ContentDraftStatus.PUBLISHED,
    }
    try:
        return transitions[(current, action)]
    except KeyError as exc:
        raise ValueError(f"Invalid draft transition: {current} -> {action}") from exc


@dataclass(slots=True)
class SourcePostPayload:
    keyword: str
    title: str
    content: str
    likes: int
    favorites: int
    comments: int
    author: str
    url: str
    tags: list[str]
    is_ad: bool = False
    is_video: bool = False
    raw_metrics: dict | None = None


@dataclass(slots=True)
class AnalysisPayload:
    summary: str
    top_keywords: list[str]
    top_tags: list[str]
    title_patterns: list[str]
    audience_insights: list[str]


@dataclass(slots=True)
class TopicPayload:
    title: str
    rationale: str
    angle: str


@dataclass(slots=True)
class DraftPayload:
    title: str
    body: str
    tags: list[str]
    cta: str
    image_prompt: str
    content_type: str


@dataclass(slots=True)
class ImagePayload:
    path: str
    prompt: str
    provider: str


@dataclass(slots=True)
class PublishPayload:
    published_url: str
    provider: str
    mode: str
