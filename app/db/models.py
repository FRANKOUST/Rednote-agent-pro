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
    request_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    result_summary: Mapped[dict] = mapped_column(JSON, default=dict)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SourcePost(Base):
    __tablename__ = "source_posts"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=generate_id)
    run_id: Mapped[str] = mapped_column(ForeignKey("workflow_runs.id"), index=True)
    keyword: Mapped[str] = mapped_column(String(128), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    likes: Mapped[int] = mapped_column(Integer, default=0)
    favorites: Mapped[int] = mapped_column(Integer, default=0)
    comments: Mapped[int] = mapped_column(Integer, default=0)
    author: Mapped[str] = mapped_column(String(128), nullable=False)
    url: Mapped[str] = mapped_column(String(512), nullable=False)
    fingerprint: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    tags: Mapped[list] = mapped_column(JSON, default=list)
    raw_data: Mapped[dict] = mapped_column(JSON, default=dict)


class WorkflowStageEvent(Base):
    __tablename__ = "workflow_stage_events"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=generate_id)
    run_id: Mapped[str] = mapped_column(ForeignKey("workflow_runs.id"), index=True)
    stage: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    provider: Mapped[str] = mapped_column(String(128), default="")
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AnalysisReport(Base):
    __tablename__ = "analysis_reports"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=generate_id)
    run_id: Mapped[str] = mapped_column(ForeignKey("workflow_runs.id"), index=True)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    top_keywords: Mapped[list] = mapped_column(JSON, default=list)
    top_tags: Mapped[list] = mapped_column(JSON, default=list)
    title_patterns: Mapped[list] = mapped_column(JSON, default=list)
    audience_insights: Mapped[list] = mapped_column(JSON, default=list)


class TopicSuggestion(Base):
    __tablename__ = "topic_suggestions"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=generate_id)
    report_id: Mapped[str] = mapped_column(ForeignKey("analysis_reports.id"), index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    angle: Mapped[str] = mapped_column(String(255), nullable=False)


class ContentDraft(Base):
    __tablename__ = "content_drafts"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=generate_id)
    topic_id: Mapped[str] = mapped_column(ForeignKey("topic_suggestions.id"), index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    tags: Mapped[list] = mapped_column(JSON, default=list)
    cta: Mapped[str] = mapped_column(String(255), default="")
    image_prompt: Mapped[str] = mapped_column(Text, default="")
    content_type: Mapped[str] = mapped_column(String(64), default="note")
    review_notes: Mapped[str] = mapped_column(Text, default="")


class ImageAsset(Base):
    __tablename__ = "image_assets"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=generate_id)
    draft_id: Mapped[str] = mapped_column(ForeignKey("content_drafts.id"), index=True)
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    path: Mapped[str] = mapped_column(String(512), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(32), default="generated")


class PublishJob(Base):
    __tablename__ = "publish_jobs"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=generate_id)
    draft_id: Mapped[str] = mapped_column(ForeignKey("content_drafts.id"), index=True)
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    mode: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    published_url: Mapped[str] = mapped_column(String(512), default="")
    details: Mapped[dict] = mapped_column(JSON, default=dict)


class SyncRecord(Base):
    __tablename__ = "sync_records"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=generate_id)
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(32), nullable=False)
    target: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=generate_id)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(32), nullable=False)
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
