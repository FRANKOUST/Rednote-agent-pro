from __future__ import annotations

from typing import Any

from sqlalchemy import func, select

from app.application.dispatcher import build_dispatcher
from app.core.config import get_settings
from app.db.models import AnalysisReport, AuditLog, ContentDraft, ImageAsset, PublishJob, SourcePost, SyncRecord, TopicSuggestion, WorkflowRun, WorkflowStageEvent
from app.db.session import session_scope
from app.domain.models import ContentDraftStatus, PublishJobStatus, WorkflowRunStatus, transition_draft_status
from app.infrastructure.providers.registry import build_provider_registry
from pathlib import Path

from app.infrastructure.providers.publisher.api_safe_stub import XiaohongshuAPISafeStubProvider
from app.infrastructure.providers.publisher.browser_safe_stub import XiaohongshuBrowserSafeStubProvider


class PipelineService:
    def __init__(self) -> None:
        self.settings = get_settings()
        registry = build_provider_registry()
        self.dispatcher = build_dispatcher()
        self.collector = registry.collector
        self.llm = registry.language_model
        self.image = registry.image
        self.publisher = registry.publisher
        self.sync = registry.sync

    def create_run(self, payload: dict) -> dict[str, Any]:
        with session_scope() as session:
            run = WorkflowRun(status=WorkflowRunStatus.QUEUED.value, current_stage="queued", request_payload=payload)
            session.add(run)
            session.flush()
            run_id = run.id
        self.dispatcher.dispatch(self.execute_run, run_id)
        if getattr(self.dispatcher, "mode", "inline") == "inline":
            return self.get_run(run_id)
        if getattr(self.dispatcher, "mode", "") == "worker_stub":
            return self.get_run(run_id)
        return self.get_run(run_id)

    def execute_run(self, run_id: str) -> None:
        with session_scope() as session:
            run = session.get(WorkflowRun, run_id)
            if run is None:
                raise ValueError(f"Unknown run: {run_id}")
            run.status = WorkflowRunStatus.RUNNING.value
            run.current_stage = "crawl"
            self._stage(session, run.id, "crawl", "started", self.collector.name, {"keywords": run.request_payload.get("keywords", [])})

            posts = self.collector.collect(run.request_payload)
            self._stage(session, run.id, "crawl", "completed", self.collector.name, {"source_posts": len(posts)})
            for post in posts:
                session.add(
                    SourcePost(
                        run_id=run.id,
                        keyword=post.keyword,
                        title=post.title,
                        content=post.content,
                        likes=post.likes,
                        favorites=post.favorites,
                        comments=post.comments,
                        author=post.author,
                        url=post.url,
                        fingerprint=f"xiaohongshu::{post.url}",
                        tags=post.tags,
                        raw_data=post.raw_metrics or {},
                    )
                )

            run.current_stage = "analyze"
            self._stage(session, run.id, "analyze", "started", self.llm.name, {"source_posts": len(posts)})
            analysis = self.llm.analyze(posts)
            self._stage(session, run.id, "analyze", "completed", self.llm.name, {"top_tags": analysis.top_tags[:3]})
            report = AnalysisReport(
                run_id=run.id,
                summary=analysis.summary,
                top_keywords=analysis.top_keywords,
                top_tags=analysis.top_tags,
                title_patterns=analysis.title_patterns,
                audience_insights=analysis.audience_insights,
            )
            session.add(report)
            session.flush()

            run.current_stage = "generate_topics"
            topic_rows: list[TopicSuggestion] = []
            self._stage(session, run.id, "generate_topics", "started", self.llm.name, {})
            topics = self.llm.suggest_topics(analysis)
            for topic in topics:
                row = TopicSuggestion(report_id=report.id, title=topic.title, rationale=topic.rationale, angle=topic.angle)
                session.add(row)
                topic_rows.append(row)
            session.flush()
            self._stage(session, run.id, "generate_topics", "completed", self.llm.name, {"topic_count": len(topic_rows)})

            run.current_stage = "generate_drafts"
            draft_rows: list[ContentDraft] = []
            self._stage(session, run.id, "generate_drafts", "started", self.llm.name, {})
            for topic_row, topic_payload in zip(topic_rows, topics):
                draft_payload = self.llm.generate_draft(topic_payload, analysis)
                draft_row = ContentDraft(
                    topic_id=topic_row.id,
                    status=ContentDraftStatus.CREATED.value,
                    title=draft_payload.title,
                    body=draft_payload.body,
                    tags=draft_payload.tags,
                    cta=draft_payload.cta,
                    image_prompt=draft_payload.image_prompt,
                    content_type=draft_payload.content_type,
                )
                draft_row.status = transition_draft_status(ContentDraftStatus.CREATED, "generate").value
                draft_row.status = transition_draft_status(ContentDraftStatus(draft_row.status), "submit_for_review").value
                session.add(draft_row)
                session.flush()
                draft_rows.append(draft_row)

                image = self.image.generate(draft_payload)
                session.add(ImageAsset(draft_id=draft_row.id, provider=image.provider, path=image.path, prompt=image.prompt, status="generated"))
            self._stage(session, run.id, "generate_drafts", "completed", self.llm.name, {"draft_count": len(draft_rows)})
            self._stage(session, run.id, "generate_images", "completed", self.image.name, {"image_count": len(draft_rows)})

            source_sync = self.sync.sync(
                "source_post_batch",
                {
                    "run_id": run.id,
                    "count": len(posts),
                    "keywords": run.request_payload.get("keywords", []),
                },
            )
            session.add(
                SyncRecord(
                    entity_type="source_post_batch",
                    entity_id=run.id,
                    target=source_sync["target"],
                    status=source_sync["status"],
                    payload=source_sync["payload"],
                )
            )

            draft_sync = self.sync.sync(
                "content_draft_batch",
                {
                    "run_id": run.id,
                    "count": len(draft_rows),
                    "draft_ids": [draft.id for draft in draft_rows],
                },
            )
            session.add(
                SyncRecord(
                    entity_type="content_draft_batch",
                    entity_id=run.id,
                    target=draft_sync["target"],
                    status=draft_sync["status"],
                    payload=draft_sync["payload"],
                )
            )

            run.current_stage = "review_gate"
            self._stage(session, run.id, "review_gate", "completed", "system", {"drafts_pending_review": len(draft_rows)})
            run.status = WorkflowRunStatus.COMPLETED.value
            run.current_stage = "completed"
            run.result_summary = {
                "source_posts": len(posts),
                "analysis_reports": 1,
                "topic_suggestions": len(topic_rows),
                "content_drafts": len(draft_rows),
                "image_assets": len(draft_rows),
            }
            self._log(session, "pipeline.completed_generation", "workflow_run", run.id, {"draft_count": len(draft_rows)})

    def get_run(self, run_id: str) -> dict[str, Any]:
        with session_scope() as session:
            run = session.get(WorkflowRun, run_id)
            if run is None:
                raise ValueError(f"Unknown run: {run_id}")
            report_ids = [
                row[0]
                for row in session.execute(select(AnalysisReport.id).where(AnalysisReport.run_id == run.id)).all()
            ]
            topic_ids = []
            if report_ids:
                topic_ids = [row[0] for row in session.execute(select(TopicSuggestion.id).where(TopicSuggestion.report_id.in_(report_ids))).all()]
            draft_ids = []
            if topic_ids:
                draft_ids = [row[0] for row in session.execute(select(ContentDraft.id).where(ContentDraft.topic_id.in_(topic_ids))).all()]

            source_count = session.scalar(select(func.count()).select_from(SourcePost).where(SourcePost.run_id == run.id)) or 0
            return {
                "id": run.id,
                "status": run.status,
                "current_stage": run.current_stage,
                "counts": {
                    "source_posts": source_count,
                    "analysis_reports": len(report_ids),
                    "topic_suggestions": len(topic_ids),
                    "content_drafts": len(draft_ids),
                },
                "draft_ids": draft_ids,
                "request_payload": run.request_payload,
            }

    def list_runs(self) -> dict[str, list[dict[str, Any]]]:
        with session_scope() as session:
            rows = session.scalars(select(WorkflowRun).order_by(WorkflowRun.created_at.desc())).all()
            return {
                "items": [
                    {
                        "id": row.id,
                        "status": row.status,
                        "current_stage": row.current_stage,
                        "created_at": row.created_at.isoformat() if row.created_at else None,
                    }
                    for row in rows
                ]
            }

    def get_run_diagnostics(self, run_id: str) -> dict[str, list[dict[str, Any]]]:
        with session_scope() as session:
            rows = session.scalars(
                select(WorkflowStageEvent).where(WorkflowStageEvent.run_id == run_id).order_by(WorkflowStageEvent.created_at)
            ).all()
            return {
                "items": [
                    {
                        "id": row.id,
                        "stage": row.stage,
                        "status": row.status,
                        "provider": row.provider,
                        "details": row.details,
                    }
                    for row in rows
                ]
            }

    def list_drafts(self) -> list[dict[str, Any]]:
        with session_scope() as session:
            drafts = session.scalars(select(ContentDraft).order_by(ContentDraft.id)).all()
            return [{"id": d.id, "title": d.title, "status": d.status, "review_notes": d.review_notes} for d in drafts]

    def list_source_posts(self, run_id: str | None = None) -> dict[str, list[dict[str, Any]]]:
        with session_scope() as session:
            stmt = select(SourcePost).order_by(SourcePost.id)
            if run_id:
                stmt = stmt.where(SourcePost.run_id == run_id)
            rows = session.scalars(stmt).all()
            return {
                "items": [
                    {
                        "id": row.id,
                        "run_id": row.run_id,
                        "keyword": row.keyword,
                        "title": row.title,
                        "likes": row.likes,
                        "favorites": row.favorites,
                        "comments": row.comments,
                        "url": row.url,
                        "tags": row.tags,
                    }
                    for row in rows
                ]
            }

    def get_source_post(self, source_post_id: str) -> dict[str, Any]:
        with session_scope() as session:
            row = session.get(SourcePost, source_post_id)
            if row is None:
                raise ValueError(f"Unknown source post: {source_post_id}")
            return {
                "id": row.id,
                "run_id": row.run_id,
                "keyword": row.keyword,
                "title": row.title,
                "content": row.content,
                "likes": row.likes,
                "favorites": row.favorites,
                "comments": row.comments,
                "author": row.author,
                "url": row.url,
                "tags": row.tags,
                "raw_data": row.raw_data,
            }

    def list_analysis_reports(self, run_id: str | None = None) -> dict[str, list[dict[str, Any]]]:
        with session_scope() as session:
            stmt = select(AnalysisReport).order_by(AnalysisReport.id)
            if run_id:
                stmt = stmt.where(AnalysisReport.run_id == run_id)
            rows = session.scalars(stmt).all()
            return {
                "items": [
                    {
                        "id": row.id,
                        "run_id": row.run_id,
                        "summary": row.summary,
                        "top_keywords": row.top_keywords,
                        "top_tags": row.top_tags,
                    }
                    for row in rows
                ]
            }

    def get_analysis_report(self, report_id: str) -> dict[str, Any]:
        with session_scope() as session:
            row = session.get(AnalysisReport, report_id)
            if row is None:
                raise ValueError(f"Unknown analysis report: {report_id}")
            return {
                "id": row.id,
                "run_id": row.run_id,
                "summary": row.summary,
                "top_keywords": row.top_keywords,
                "top_tags": row.top_tags,
                "title_patterns": row.title_patterns,
                "audience_insights": row.audience_insights,
            }

    def list_topic_suggestions(self, run_id: str | None = None) -> dict[str, list[dict[str, Any]]]:
        with session_scope() as session:
            stmt = (
                select(TopicSuggestion.id, TopicSuggestion.report_id, TopicSuggestion.title, TopicSuggestion.rationale, TopicSuggestion.angle, AnalysisReport.run_id)
                .join(AnalysisReport, TopicSuggestion.report_id == AnalysisReport.id)
                .order_by(TopicSuggestion.id)
            )
            if run_id:
                stmt = stmt.where(AnalysisReport.run_id == run_id)
            rows = session.execute(stmt).all()
            return {
                "items": [
                    {
                        "id": row.id,
                        "report_id": row.report_id,
                        "run_id": row.run_id,
                        "title": row.title,
                        "rationale": row.rationale,
                        "angle": row.angle,
                    }
                    for row in rows
                ]
            }

    def get_topic_suggestion(self, topic_id: str) -> dict[str, Any]:
        with session_scope() as session:
            stmt = (
                select(TopicSuggestion.id, TopicSuggestion.report_id, TopicSuggestion.title, TopicSuggestion.rationale, TopicSuggestion.angle, AnalysisReport.run_id)
                .join(AnalysisReport, TopicSuggestion.report_id == AnalysisReport.id)
                .where(TopicSuggestion.id == topic_id)
            )
            row = session.execute(stmt).first()
            if row is None:
                raise ValueError(f"Unknown topic suggestion: {topic_id}")
            return {
                "id": row.id,
                "report_id": row.report_id,
                "run_id": row.run_id,
                "title": row.title,
                "rationale": row.rationale,
                "angle": row.angle,
            }

    def list_image_assets(self, run_id: str | None = None) -> dict[str, list[dict[str, Any]]]:
        with session_scope() as session:
            stmt = (
                select(ImageAsset.id, ImageAsset.draft_id, ImageAsset.provider, ImageAsset.path, ImageAsset.status, WorkflowRun.id.label("run_id"))
                .join(ContentDraft, ImageAsset.draft_id == ContentDraft.id)
                .join(TopicSuggestion, ContentDraft.topic_id == TopicSuggestion.id)
                .join(AnalysisReport, TopicSuggestion.report_id == AnalysisReport.id)
                .join(WorkflowRun, AnalysisReport.run_id == WorkflowRun.id)
                .order_by(ImageAsset.id)
            )
            if run_id:
                stmt = stmt.where(WorkflowRun.id == run_id)
            rows = session.execute(stmt).all()
            return {
                "items": [
                    {
                        "id": row.id,
                        "draft_id": row.draft_id,
                        "run_id": row.run_id,
                        "provider": row.provider,
                        "path": row.path,
                        "status": row.status,
                    }
                    for row in rows
                ]
            }

    def get_image_asset(self, image_id: str) -> dict[str, Any]:
        with session_scope() as session:
            stmt = (
                select(ImageAsset.id, ImageAsset.draft_id, ImageAsset.provider, ImageAsset.path, ImageAsset.status, WorkflowRun.id.label("run_id"))
                .join(ContentDraft, ImageAsset.draft_id == ContentDraft.id)
                .join(TopicSuggestion, ContentDraft.topic_id == TopicSuggestion.id)
                .join(AnalysisReport, TopicSuggestion.report_id == AnalysisReport.id)
                .join(WorkflowRun, AnalysisReport.run_id == WorkflowRun.id)
                .where(ImageAsset.id == image_id)
            )
            row = session.execute(stmt).first()
            if row is None:
                raise ValueError(f"Unknown image asset: {image_id}")
            return {
                "id": row.id,
                "draft_id": row.draft_id,
                "run_id": row.run_id,
                "provider": row.provider,
                "path": row.path,
                "status": row.status,
            }

    def approve_draft(self, draft_id: str, review_notes: str = "") -> dict[str, Any]:
        with session_scope() as session:
            draft = session.get(ContentDraft, draft_id)
            if draft is None:
                raise ValueError(f"Unknown draft: {draft_id}")
            draft.status = transition_draft_status(ContentDraftStatus(draft.status), "approve").value
            draft.review_notes = review_notes
            self._log(session, "draft.approved", "content_draft", draft.id, {"review_notes": review_notes})
            return {"id": draft.id, "status": draft.status, "review_notes": draft.review_notes}

    def reject_draft(self, draft_id: str, review_notes: str = "") -> dict[str, Any]:
        with session_scope() as session:
            draft = session.get(ContentDraft, draft_id)
            if draft is None:
                raise ValueError(f"Unknown draft: {draft_id}")
            draft.status = transition_draft_status(ContentDraftStatus(draft.status), "reject").value
            draft.review_notes = review_notes
            self._log(session, "draft.rejected", "content_draft", draft.id, {"review_notes": review_notes})
            return {"id": draft.id, "status": draft.status, "review_notes": draft.review_notes}

    def publish_draft(self, draft_id: str) -> dict[str, Any]:
        with session_scope() as session:
            draft = session.get(ContentDraft, draft_id)
            if draft is None:
                raise ValueError(f"Unknown draft: {draft_id}")

            current = ContentDraftStatus(draft.status)
            if current == ContentDraftStatus.APPROVED:
                draft.status = transition_draft_status(current, "mark_publish_ready").value
            elif current != ContentDraftStatus.PUBLISH_READY:
                raise ValueError("Draft must be approved before publishing.")

            execution_publisher = self._execution_publisher()
            publish_job = PublishJob(draft_id=draft.id, provider=execution_publisher.name, mode="mock", status=PublishJobStatus.QUEUED.value, details={})
            session.add(publish_job)
            session.flush()
            publish_job.status = PublishJobStatus.PREPARING.value
            publish_job.status = PublishJobStatus.PUBLISHING.value
            result = execution_publisher.publish(
                type(
                    "DraftAdapter",
                    (),
                    {
                        "title": draft.title,
                        "body": draft.body,
                        "tags": draft.tags,
                        "cta": draft.cta,
                        "image_prompt": draft.image_prompt,
                        "content_type": draft.content_type,
                    },
                )()
            )
            publish_job.status = PublishJobStatus.PUBLISHED.value
            publish_job.provider = result.provider
            publish_job.mode = result.mode
            publish_job.published_url = result.published_url
            publish_job.details = {"provider": result.provider, "mode": result.mode}
            draft.status = transition_draft_status(ContentDraftStatus.PUBLISH_READY, "publish").value
            self._log(session, "publish.completed", "publish_job", publish_job.id, {"published_url": publish_job.published_url})

            sync_result = self.sync.sync("publish_job", {"draft_id": draft.id, "published_url": publish_job.published_url, "title": draft.title})
            sync_record = SyncRecord(
                entity_type="publish_job",
                entity_id=publish_job.id,
                target=sync_result["target"],
                status=sync_result["status"],
                payload=sync_result["payload"],
            )
            session.add(sync_record)
            session.flush()
            self._log(session, "sync.completed", "sync_record", sync_record.id, {"target": sync_record.target})

            return {
                "status": publish_job.status,
                "publish_job": {
                    "id": publish_job.id,
                    "status": publish_job.status,
                    "published_url": publish_job.published_url,
                    "provider": publish_job.provider,
                },
                "sync_record": {"id": sync_record.id, "status": sync_record.status, "target": sync_record.target},
            }

    def list_audit_logs(self) -> dict[str, list[dict[str, Any]]]:
        with session_scope() as session:
            rows = session.scalars(select(AuditLog).order_by(AuditLog.created_at)).all()
            return {"items": [{"id": row.id, "event_type": row.event_type, "entity_type": row.entity_type, "entity_id": row.entity_id, "details": row.details} for row in rows]}

    def list_sync_records(self) -> dict[str, list[dict[str, Any]]]:
        with session_scope() as session:
            rows = session.scalars(select(SyncRecord).order_by(SyncRecord.id)).all()
            return {"items": [{"id": row.id, "entity_type": row.entity_type, "entity_id": row.entity_id, "target": row.target, "status": row.status} for row in rows]}

    def list_publish_jobs(self) -> dict[str, list[dict[str, Any]]]:
        with session_scope() as session:
            rows = session.scalars(select(PublishJob).order_by(PublishJob.id)).all()
            return {
                "items": [
                    {
                        "id": row.id,
                        "draft_id": row.draft_id,
                        "provider": row.provider,
                        "mode": row.mode,
                        "status": row.status,
                        "published_url": row.published_url,
                    }
                    for row in rows
                ]
            }

    def observability_summary(self) -> dict[str, int]:
        with session_scope() as session:
            return {
                "workflow_runs": session.scalar(select(func.count()).select_from(WorkflowRun)) or 0,
                "source_posts": session.scalar(select(func.count()).select_from(SourcePost)) or 0,
                "analysis_reports": session.scalar(select(func.count()).select_from(AnalysisReport)) or 0,
                "topic_suggestions": session.scalar(select(func.count()).select_from(TopicSuggestion)) or 0,
                "content_drafts": session.scalar(select(func.count()).select_from(ContentDraft)) or 0,
                "publish_jobs": session.scalar(select(func.count()).select_from(PublishJob)) or 0,
                "sync_records": session.scalar(select(func.count()).select_from(SyncRecord)) or 0,
                "audit_logs": session.scalar(select(func.count()).select_from(AuditLog)) or 0,
            }

    def provider_diagnostics(self) -> dict[str, dict[str, Any]]:
        settings = get_settings()
        return {
            "collector": {
                "configured": settings.default_collector_provider,
                "active": self.collector.name,
                "real_enabled": settings.enable_real_collector,
                "safe_mode": settings.playwright_safe_mode,
            },
            "language_model": {
                "configured": settings.default_model_provider,
                "active": self.llm.name,
                "real_enabled": settings.enable_real_model_provider,
                "model_name": settings.openai_model_name,
            },
            "image": {
                "configured": settings.default_image_provider,
                "active": self.image.name,
                "real_enabled": settings.enable_real_image_provider,
                "model_name": settings.openai_image_model,
            },
            "publisher": {
                "configured": settings.default_publish_provider,
                "active": self.publisher.name,
                "real_enabled": settings.enable_real_publish_provider,
            },
            "sync": {
                "configured": settings.default_sync_provider,
                "active": self.sync.name,
                "real_enabled": settings.enable_real_sync_provider,
            },
        }

    def provider_health(self) -> dict[str, dict[str, Any]]:
        settings = get_settings()
        collector_status = "ready"
        collector_reason = "mock or safe collector available"
        if settings.default_collector_provider == "playwright" and settings.enable_real_collector:
            if not Path(settings.playwright_storage_state_path).exists():
                collector_status = "degraded"
                collector_reason = "missing playwright storage state"
        model_status = "ready" if (settings.default_model_provider != "openai" or settings.openai_api_key) else "degraded"
        image_status = "ready" if (settings.default_image_provider != "openai" or settings.openai_api_key) else "degraded"
        publish_status = "ready"
        publish_reason = "safe publish path available"
        if settings.default_publish_provider == "api" and settings.enable_real_publish_provider:
            if not settings.xhs_publish_api_token or not settings.xhs_publish_api_base:
                publish_status = "degraded"
                publish_reason = "missing publish API credentials"
        sync_status = "ready"
        sync_reason = "safe sync path available"
        if settings.default_sync_provider == "feishu" and settings.enable_real_sync_provider:
            if not settings.feishu_app_id or not settings.feishu_app_secret:
                sync_status = "degraded"
                sync_reason = "missing Feishu credentials"
        return {
            "collector": {"status": collector_status, "reason": collector_reason},
            "language_model": {"status": model_status, "reason": "missing OpenAI API key" if model_status == "degraded" else "ready"},
            "image": {"status": image_status, "reason": "missing OpenAI API key" if image_status == "degraded" else "ready"},
            "publisher": {"status": publish_status, "reason": publish_reason},
            "sync": {"status": sync_status, "reason": sync_reason},
        }

    def dashboard(self) -> dict[str, Any]:
        return {
            "app_name": "Xiaohongshu Content Platform",
            "runs": self.list_runs()["items"][:10],
            "drafts": self.list_drafts(),
            "provider_diagnostics": self.provider_diagnostics(),
            "provider_health": self.provider_health(),
            "publish_jobs": self.list_publish_jobs()["items"][-10:],
            "sync_records": self.list_sync_records()["items"][-10:],
            "audit_logs": self.list_audit_logs()["items"][-10:],
        }

    @staticmethod
    def _log(session, event_type: str, entity_type: str, entity_id: str, details: dict) -> None:
        session.add(AuditLog(event_type=event_type, entity_type=entity_type, entity_id=entity_id, details=details))

    @staticmethod
    def _stage(session, run_id: str, stage: str, status: str, provider: str, details: dict) -> None:
        session.add(WorkflowStageEvent(run_id=run_id, stage=stage, status=status, provider=provider, details=details))

    def _execution_publisher(self):
        if getattr(self.publisher, "name", "").endswith("live-publisher") and not self.settings.allow_live_publish:
            if "browser" in self.publisher.name:
                return XiaohongshuBrowserSafeStubProvider()
            return XiaohongshuAPISafeStubProvider()
        return self.publisher
