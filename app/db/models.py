from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def generate_id() -> str:
    return uuid4().hex


class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=generate_id)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    current_stage: Mapped[str] = mapped_column(String(64), nullable=False, default="queued")
    execution_mode: Mapped[str] = mapped_column(String(32), nullable=False, default="full")
    request_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    result_summary: Mapped[dict] = mapped_column(JSON, default=dict)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CollectorRun(Base):
    __tablename__ = "collector_runs"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=generate_id)
    workflow_run_id: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    provider: Mapped[str] = mapped_column(String(128), nullable=False)
    collection_type: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    request_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    result_summary: Mapped[dict] = mapped_column(JSON, default=dict)
    diagnostics: Mapped[dict] = mapped_column(JSON, default=dict)
    failure_category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    attempt_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SyncRun(Base):
    __tablename__ = "sync_runs"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=generate_id)
    provider: Mapped[str] = mapped_column(String(128), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    business_type: Mapped[str] = mapped_column(String(64), nullable=False, default="sync_generated")
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    dry_run: Mapped[int] = mapped_column(Integer, default=0)
    request_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    result_summary: Mapped[dict] = mapped_column(JSON, default=dict)
    diagnostics: Mapped[dict] = mapped_column(JSON, default=dict)
    failure_category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    attempt_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SourcePost(Base):
    __tablename__ = "source_posts"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=generate_id)
    run_id: Mapped[str] = mapped_column(String(32), index=True)
    provider: Mapped[str] = mapped_column(String(128), default="")
    keyword: Mapped[str] = mapped_column(String(128), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    likes: Mapped[int] = mapped_column(Integer, default=0)
    favorites: Mapped[int] = mapped_column(Integer, default=0)
    comments: Mapped[int] = mapped_column(Integer, default=0)
    author: Mapped[str] = mapped_column(String(128), nullable=False)
    url: Mapped[str] = mapped_column(String(512), nullable=False)
    published_at: Mapped[str] = mapped_column(String(64), default="")
    content_type: Mapped[str] = mapped_column(String(64), default="image_text")
    is_ad: Mapped[int] = mapped_column(Integer, default=0)
    fingerprint: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    tags: Mapped[list] = mapped_column(JSON, default=list)
    raw_data: Mapped[dict] = mapped_column(JSON, default=dict)


class WorkflowStageEvent(Base):
    __tablename__ = "workflow_stage_events"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=generate_id)
    run_id: Mapped[str] = mapped_column(String(32), index=True)
    stage: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    provider: Mapped[str] = mapped_column(String(128), default="")
    input_summary: Mapped[dict] = mapped_column(JSON, default=dict)
    output_summary: Mapped[dict] = mapped_column(JSON, default=dict)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AnalysisReport(Base):
    __tablename__ = "analysis_reports"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=generate_id)
    run_id: Mapped[str] = mapped_column(String(32), index=True)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    top_keywords: Mapped[list] = mapped_column(JSON, default=list)
    top_tags: Mapped[list] = mapped_column(JSON, default=list)
    title_patterns: Mapped[list] = mapped_column(JSON, default=list)
    opening_patterns: Mapped[list] = mapped_column(JSON, default=list)
    content_structure_templates: Mapped[list] = mapped_column(JSON, default=list)
    user_pain_points: Mapped[list] = mapped_column(JSON, default=list)
    user_delight_points: Mapped[list] = mapped_column(JSON, default=list)
    user_focus_points: Mapped[list] = mapped_column(JSON, default=list)
    engagement_triggers: Mapped[list] = mapped_column(JSON, default=list)
    applicable_tracks: Mapped[list] = mapped_column(JSON, default=list)
    viral_hooks: Mapped[list] = mapped_column(JSON, default=list)
    risk_alerts: Mapped[list] = mapped_column(JSON, default=list)


class TopicSuggestion(Base):
    __tablename__ = "topic_suggestions"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=generate_id)
    report_id: Mapped[str] = mapped_column(String(32), index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    angle: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    target_audience: Mapped[str] = mapped_column(String(255), default="")
    reference_hooks: Mapped[list] = mapped_column(JSON, default=list)
    analysis_evidence: Mapped[list] = mapped_column(JSON, default=list)
    risk_notes: Mapped[list] = mapped_column(JSON, default=list)
    recommended_format: Mapped[str] = mapped_column(String(64), default="note")
    priority: Mapped[str] = mapped_column(String(32), default="medium")
    confidence: Mapped[int] = mapped_column(Integer, default=0)


class ContentDraft(Base):
    __tablename__ = "content_drafts"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=generate_id)
    topic_id: Mapped[str] = mapped_column(String(32), index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    alternate_titles: Mapped[list] = mapped_column(JSON, default=list)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    tags: Mapped[list] = mapped_column(JSON, default=list)
    cta: Mapped[str] = mapped_column(String(255), default="")
    image_prompt: Mapped[str] = mapped_column(Text, default="")
    image_suggestions: Mapped[list] = mapped_column(JSON, default=list)
    content_type: Mapped[str] = mapped_column(String(64), default="note")
    target_user: Mapped[str] = mapped_column(String(255), default="")
    tone_style: Mapped[str] = mapped_column(String(128), default="")
    risk_notes: Mapped[list] = mapped_column(JSON, default=list)
    review_notes: Mapped[str] = mapped_column(Text, default="")
    revision_notes: Mapped[list] = mapped_column(JSON, default=list)
    revision_count: Mapped[int] = mapped_column(Integer, default=0)


class ImageAsset(Base):
    __tablename__ = "image_assets"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=generate_id)
    draft_id: Mapped[str] = mapped_column(String(32), index=True)
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    path: Mapped[str] = mapped_column(String(512), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(32), default="generated")


class PublishJob(Base):
    __tablename__ = "publish_jobs"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=generate_id)
    draft_id: Mapped[str] = mapped_column(String(32), index=True)
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    mode: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    published_url: Mapped[str] = mapped_column(String(512), default="")
    prepared_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    preview_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    details: Mapped[dict] = mapped_column(JSON, default=dict)


class SyncRecord(Base):
    __tablename__ = "sync_records"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=generate_id)
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(32), nullable=False)
    business_type: Mapped[str] = mapped_column(String(64), nullable=False, default="sync_generated")
    provider: Mapped[str] = mapped_column(String(128), default="")
    target: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    dry_run: Mapped[int] = mapped_column(Integer, default=0)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    diagnostics: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=generate_id)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(32), nullable=False)
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
