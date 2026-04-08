from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class StringEnum(str, Enum):
    pass


class WorkflowRunStatus(StringEnum):
    QUEUED = "queued"
    RUNNING = "running"
    ACTION_REQUIRED = "action_required"
    COMPLETED = "completed"
    FAILED = "failed"


class ContentDraftStatus(StringEnum):
    CREATED = "created"
    GENERATED = "generated"
    REVIEW_PENDING = "review_pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVISION_REQUESTED = "revision_requested"
    PUBLISH_READY = "publish_ready"
    PUBLISHED = "published"


class PublishJobStatus(StringEnum):
    QUEUED = "queued"
    PREPARED = "prepared"
    PREVIEW_READY = "preview_ready"
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


class StageStatus(StringEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"


PIPELINE_STAGES = ["crawl", "analyze", "topic", "draft", "image", "review", "publish", "sync"]


def transition_draft_status(current: ContentDraftStatus, action: str) -> ContentDraftStatus:
    transitions = {
        (ContentDraftStatus.CREATED, "generate"): ContentDraftStatus.GENERATED,
        (ContentDraftStatus.GENERATED, "submit_for_review"): ContentDraftStatus.REVIEW_PENDING,
        (ContentDraftStatus.REVIEW_PENDING, "approve"): ContentDraftStatus.APPROVED,
        (ContentDraftStatus.REVIEW_PENDING, "reject"): ContentDraftStatus.REJECTED,
        (ContentDraftStatus.REVIEW_PENDING, "revise"): ContentDraftStatus.REVISION_REQUESTED,
        (ContentDraftStatus.REJECTED, "regenerate"): ContentDraftStatus.REVIEW_PENDING,
        (ContentDraftStatus.REVISION_REQUESTED, "regenerate"): ContentDraftStatus.REVIEW_PENDING,
        (ContentDraftStatus.APPROVED, "mark_publish_ready"): ContentDraftStatus.PUBLISH_READY,
        (ContentDraftStatus.PUBLISH_READY, "publish"): ContentDraftStatus.PUBLISHED,
    }
    try:
        return transitions[(current, action)]
    except KeyError as exc:
        raise ValueError(f"Invalid draft transition: {current} -> {action}") from exc


@dataclass(slots=True)
class CollectorCandidatePayload:
    keyword: str
    url: str
    author: str
    published_at: str = ""
    content_type: str = "image_text"
    is_video: bool = False
    raw_metrics: dict | None = None


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
    published_at: str = ""
    content_type: str = "image_text"
    is_ad: bool = False
    is_video: bool = False
    raw_metrics: dict | None = None


@dataclass(slots=True)
class AnalysisPayload:
    summary: str
    high_frequency_keywords: list[str]
    hot_tags: list[str]
    title_patterns: list[str]
    opening_patterns: list[str]
    content_structure_templates: list[str]
    user_pain_points: list[str]
    user_delight_points: list[str]
    user_focus_points: list[str]
    engagement_triggers: list[str]
    applicable_tracks: list[str]
    viral_hooks: list[str]
    risk_alerts: list[str]

    @property
    def top_keywords(self) -> list[str]:
        return self.high_frequency_keywords

    @property
    def top_tags(self) -> list[str]:
        return self.hot_tags

    @property
    def audience_insights(self) -> list[str]:
        return self.user_focus_points


@dataclass(slots=True)
class TopicPayload:
    title: str
    reason: str
    target_audience: str
    reference_hooks: list[str]
    analysis_evidence: list[str]
    risk_notes: list[str]
    recommended_format: str
    priority: str
    confidence: float
    angle: str = ""

    @property
    def rationale(self) -> str:
        return self.reason


@dataclass(slots=True)
class DraftPayload:
    headline: str = ""
    title: str = ""
    alternate_headlines: list[str] | None = None
    body: str = ""
    tags: list[str] | None = None
    cta: str = ""
    image_suggestions: list[str] | None = None
    image_prompt: str = ""
    content_type: str = ""
    target_user: str = ""
    tone_style: str = ""
    risk_notes: list[str] | None = None
    review_notes: list[str] | None = None
    revision_notes: list[str] | None = None

    def __post_init__(self) -> None:
        if not self.headline:
            self.headline = self.title
        if not self.title:
            self.title = self.headline
        self.alternate_headlines = list(self.alternate_headlines or [])
        self.tags = list(self.tags or [])
        self.image_suggestions = list(self.image_suggestions or [])
        self.risk_notes = list(self.risk_notes or [])
        self.review_notes = list(self.review_notes or [])
        self.revision_notes = list(self.revision_notes or [])


@dataclass(slots=True)
class ImagePlanPayload:
    visual_goal: str
    frames: list[str]
    prompt: str
    asset_notes: list[str]


@dataclass(slots=True)
class ImagePayload:
    path: str
    prompt: str
    provider: str


@dataclass(slots=True)
class PublishPackagePayload:
    headline: str
    body: str
    tags: list[str]
    cta: str
    content_type: str
    image_prompt: str
    target_user: str
    safety_gate: str
    notes: list[str] = field(default_factory=list)

    @property
    def title(self) -> str:
        return self.headline


@dataclass(slots=True)
class PublishPayload:
    published_url: str
    provider: str
    mode: str

