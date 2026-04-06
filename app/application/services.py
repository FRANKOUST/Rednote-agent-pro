from __future__ import annotations

from typing import Any

from sqlalchemy import func, select

from app.application.dispatcher import build_dispatcher
from app.application.external_worker import build_external_worker_adapter
from app.core.config import get_settings
from app.db.models import AnalysisReport, AuditLog, CollectorRun, ContentDraft, ImageAsset, PublishJob, SourcePost, SyncRecord, SyncRun, TopicSuggestion, WorkflowRun, WorkflowStageEvent
from app.db.session import session_scope
from app.domain.models import ContentDraftStatus, PublishJobStatus, WorkflowRunStatus, transition_draft_status
from app.infrastructure.providers.publisher.api_safe_stub import XiaohongshuAPISafeStubProvider
from app.infrastructure.providers.publisher.browser_safe_stub import XiaohongshuBrowserSafeStubProvider
from app.infrastructure.providers.registry import build_provider_registry


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
        return self.get_run(run_id)

    def execute_run(self, run_id: str) -> None:
        with session_scope() as session:
            run = session.get(WorkflowRun, run_id)
            if run is None:
                raise ValueError(f"Unknown run: {run_id}")

            collector_run = CollectorRun(
                workflow_run_id=run.id,
                provider=self.collector.name,
                collection_type=run.request_payload.get("collection_type", "search"),
                status="running",
                request_payload=run.request_payload,
                result_summary={},
                diagnostics={"origin": "pipeline"},
            )
            session.add(collector_run)
            session.flush()

            try:
                run.status = WorkflowRunStatus.RUNNING.value
                run.current_stage = "crawl"
                self._stage(session, run.id, "crawl", "started", self.collector.name, {"keywords": run.request_payload.get("keywords", [])})

                collected_posts = self.collector.collect(run.request_payload)
                persisted_posts, duplicate_posts = self._persist_source_posts(session, run.id, collected_posts, self.collector.name)
                collector_meta = self._provider_metadata(self.collector)
                collector_run.status = "completed"
                collector_run.result_summary = {
                    "fetched_posts": len(collected_posts),
                    "persisted_posts": persisted_posts,
                    "duplicate_posts": duplicate_posts,
                }
                collector_run.diagnostics = {**collector_run.diagnostics, **collector_meta}
                collector_run.attempt_count = self._attempt_count(collector_meta)
                collector_run.failure_category = collector_meta.get("failure_category")
                self._stage(
                    session,
                    run.id,
                    "crawl",
                    "completed",
                    self.collector.name,
                    {"fetched_posts": len(collected_posts), "persisted_posts": persisted_posts, "duplicate_posts": duplicate_posts},
                )

                if not collected_posts:
                    raise ValueError("collector returned no posts")

                run.current_stage = "analyze"
                self._stage(session, run.id, "analyze", "started", self.llm.name, {"source_posts": len(collected_posts)})
                analysis = self.llm.analyze(collected_posts)
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
                self._stage(session, run.id, "generate_topics", "started", self.llm.name, {})
                topics = self.llm.suggest_topics(analysis)
                topic_rows: list[TopicSuggestion] = []
                for topic in topics:
                    row = TopicSuggestion(report_id=report.id, title=topic.title, rationale=topic.rationale, angle=topic.angle)
                    session.add(row)
                    topic_rows.append(row)
                session.flush()
                self._stage(session, run.id, "generate_topics", "completed", self.llm.name, {"topic_count": len(topic_rows)})

                run.current_stage = "generate_drafts"
                self._stage(session, run.id, "generate_drafts", "started", self.llm.name, {})
                draft_rows: list[ContentDraft] = []
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

                self._sync_entity(
                    session,
                    entity_type="source_post_batch",
                    entity_id=run.id,
                    payload={"run_id": run.id, "count": len(collected_posts), "keywords": run.request_payload.get("keywords", [])},
                    origin="pipeline",
                )
                self._sync_entity(
                    session,
                    entity_type="content_draft_batch",
                    entity_id=run.id,
                    payload={"run_id": run.id, "count": len(draft_rows), "draft_ids": [draft.id for draft in draft_rows]},
                    origin="pipeline",
                )

                run.current_stage = "review_gate"
                self._stage(session, run.id, "review_gate", "completed", "system", {"drafts_pending_review": len(draft_rows)})
                run.status = WorkflowRunStatus.COMPLETED.value
                run.current_stage = "completed"
                run.result_summary = {
                    "source_posts": persisted_posts,
                    "analysis_reports": 1,
                    "topic_suggestions": len(topic_rows),
                    "content_drafts": len(draft_rows),
                    "image_assets": len(draft_rows),
                    "duplicate_source_posts": duplicate_posts,
                }
                self._log(session, "pipeline.completed_generation", "workflow_run", run.id, {"draft_count": len(draft_rows)})
            except Exception as exc:
                collector_run.status = "failed" if collector_run.status == "running" else collector_run.status
                collector_run.failure_category = self._failure_category(exc)
                run.status = WorkflowRunStatus.FAILED.value
                run.current_stage = "failed"
                run.error_message = str(exc)
                self._stage(session, run.id, "pipeline", "failed", "system", {"error": str(exc)})
                self._log(session, "pipeline.failed", "workflow_run", run.id, {"error": str(exc)})
                raise

    def get_run(self, run_id: str) -> dict[str, Any]:
        with session_scope() as session:
            run = session.get(WorkflowRun, run_id)
            if run is None:
                raise ValueError(f"Unknown run: {run_id}")
            report_ids = [row[0] for row in session.execute(select(AnalysisReport.id).where(AnalysisReport.run_id == run.id)).all()]
            topic_ids = [row[0] for row in session.execute(select(TopicSuggestion.id).where(TopicSuggestion.report_id.in_(report_ids))).all()] if report_ids else []
            draft_ids = [row[0] for row in session.execute(select(ContentDraft.id).where(ContentDraft.topic_id.in_(topic_ids))).all()] if topic_ids else []
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
                "result_summary": run.result_summary,
                "error_message": run.error_message,
            }

    def list_runs(self) -> dict[str, list[dict[str, Any]]]:
        with session_scope() as session:
            rows = session.scalars(select(WorkflowRun).order_by(WorkflowRun.created_at.desc())).all()
            return {"items": [{"id": row.id, "status": row.status, "current_stage": row.current_stage, "created_at": row.created_at.isoformat() if row.created_at else None} for row in rows]}

    def start_collector_run(self, payload: dict, collection_type: str) -> dict[str, Any]:
        with session_scope() as session:
            row = CollectorRun(
                workflow_run_id=None,
                provider=self.collector.name,
                collection_type=collection_type,
                status="running",
                request_payload={**payload, "collection_type": collection_type},
                result_summary={},
                diagnostics={},
            )
            session.add(row)
            session.flush()
            run_id = row.id
        self._execute_collector_run(run_id)
        return self.get_collector_run(run_id)

    def _execute_collector_run(self, collector_run_id: str) -> None:
        with session_scope() as session:
            row = session.get(CollectorRun, collector_run_id)
            if row is None:
                raise ValueError(f"Unknown collector run: {collector_run_id}")
            try:
                request_payload = dict(row.request_payload)
                posts = self.collector.collect(request_payload)
                persisted_posts, duplicate_posts = self._persist_source_posts(session, row.workflow_run_id or row.id, posts, self.collector.name)
                provider_meta = self._provider_metadata(self.collector)
                row.status = "completed"
                row.result_summary = {"fetched_posts": len(posts), "persisted_posts": persisted_posts, "duplicate_posts": duplicate_posts}
                row.diagnostics = provider_meta
                row.attempt_count = self._attempt_count(provider_meta)
                row.failure_category = provider_meta.get("failure_category")
            except Exception as exc:
                row.status = "failed"
                row.failure_category = self._failure_category(exc)
                row.diagnostics = {"error": str(exc), **self._provider_metadata(self.collector)}
                raise

    def list_collector_runs(self) -> dict[str, list[dict[str, Any]]]:
        with session_scope() as session:
            rows = session.scalars(select(CollectorRun).order_by(CollectorRun.created_at.desc())).all()
            return {
                "items": [
                    {
                        "id": row.id,
                        "provider": row.provider,
                        "collection_type": row.collection_type,
                        "status": row.status,
                        "created_at": row.created_at.isoformat() if row.created_at else None,
                    }
                    for row in rows
                ]
            }

    def get_collector_run(self, collector_run_id: str) -> dict[str, Any]:
        with session_scope() as session:
            row = session.get(CollectorRun, collector_run_id)
            if row is None:
                raise ValueError(f"Unknown collector run: {collector_run_id}")
            return {
                "id": row.id,
                "provider": row.provider,
                "collection_type": row.collection_type,
                "status": row.status,
                "request_payload": row.request_payload,
                "result_summary": row.result_summary,
                "diagnostics": row.diagnostics,
                "failure_category": row.failure_category,
                "attempt_count": row.attempt_count,
            }

    def start_sync_run(self, entity_type: str, payload: dict, dry_run: bool) -> dict[str, Any]:
        with session_scope() as session:
            row = SyncRun(
                provider=self.sync.name,
                entity_type=entity_type,
                status="running",
                dry_run=1 if dry_run else 0,
                request_payload=payload,
                result_summary={},
                diagnostics={},
            )
            session.add(row)
            session.flush()
            sync_run_id = row.id
        self._execute_sync_run(sync_run_id)
        return self.get_sync_run(sync_run_id)

    def _execute_sync_run(self, sync_run_id: str) -> None:
        with session_scope() as session:
            row = session.get(SyncRun, sync_run_id)
            if row is None:
                raise ValueError(f"Unknown sync run: {sync_run_id}")
            payload = dict(row.request_payload)
            payload["dry_run"] = bool(row.dry_run)
            result, sync_record = self._sync_entity(session, row.entity_type, row.id, payload, origin="manual")
            row.status = result["status"]
            row.result_summary = {"target": result["target"], "sync_record_id": sync_record.id}
            row.diagnostics = result.get("diagnostics", {})
            row.failure_category = result.get("diagnostics", {}).get("reason")
            row.attempt_count = result.get("diagnostics", {}).get("attempts", 1)

    def list_sync_runs(self) -> dict[str, list[dict[str, Any]]]:
        with session_scope() as session:
            rows = session.scalars(select(SyncRun).order_by(SyncRun.created_at.desc())).all()
            return {
                "items": [
                    {
                        "id": row.id,
                        "provider": row.provider,
                        "entity_type": row.entity_type,
                        "status": row.status,
                        "dry_run": bool(row.dry_run),
                        "created_at": row.created_at.isoformat() if row.created_at else None,
                    }
                    for row in rows
                ]
            }

    def get_sync_run(self, sync_run_id: str) -> dict[str, Any]:
        with session_scope() as session:
            row = session.get(SyncRun, sync_run_id)
            if row is None:
                raise ValueError(f"Unknown sync run: {sync_run_id}")
            return {
                "id": row.id,
                "provider": row.provider,
                "entity_type": row.entity_type,
                "status": row.status,
                "dry_run": bool(row.dry_run),
                "request_payload": row.request_payload,
                "result_summary": row.result_summary,
                "diagnostics": row.diagnostics,
                "failure_category": row.failure_category,
                "attempt_count": row.attempt_count,
            }

    def get_run_diagnostics(self, run_id: str) -> dict[str, list[dict[str, Any]]]:
        with session_scope() as session:
            rows = session.scalars(select(WorkflowStageEvent).where(WorkflowStageEvent.run_id == run_id).order_by(WorkflowStageEvent.created_at)).all()
            return {"items": [{"id": row.id, "stage": row.stage, "status": row.status, "provider": row.provider, "details": row.details} for row in rows]}

    def list_drafts(self) -> list[dict[str, Any]]:
        with session_scope() as session:
            drafts = session.scalars(select(ContentDraft).order_by(ContentDraft.id)).all()
            return [{"id": d.id, "title": d.title, "status": d.status, "review_notes": d.review_notes, "revision_count": d.revision_count} for d in drafts]

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
                        "provider": row.provider,
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
                "provider": row.provider,
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
            return {"items": [{"id": row.id, "run_id": row.run_id, "summary": row.summary, "top_keywords": row.top_keywords, "top_tags": row.top_tags} for row in rows]}

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
            stmt = select(TopicSuggestion.id, TopicSuggestion.report_id, TopicSuggestion.title, TopicSuggestion.rationale, TopicSuggestion.angle, AnalysisReport.run_id).join(AnalysisReport, TopicSuggestion.report_id == AnalysisReport.id).order_by(TopicSuggestion.id)
            if run_id:
                stmt = stmt.where(AnalysisReport.run_id == run_id)
            rows = session.execute(stmt).all()
            return {"items": [{"id": row.id, "report_id": row.report_id, "run_id": row.run_id, "title": row.title, "rationale": row.rationale, "angle": row.angle} for row in rows]}

    def get_topic_suggestion(self, topic_id: str) -> dict[str, Any]:
        with session_scope() as session:
            stmt = select(TopicSuggestion.id, TopicSuggestion.report_id, TopicSuggestion.title, TopicSuggestion.rationale, TopicSuggestion.angle, AnalysisReport.run_id).join(AnalysisReport, TopicSuggestion.report_id == AnalysisReport.id).where(TopicSuggestion.id == topic_id)
            row = session.execute(stmt).first()
            if row is None:
                raise ValueError(f"Unknown topic suggestion: {topic_id}")
            return {"id": row.id, "report_id": row.report_id, "run_id": row.run_id, "title": row.title, "rationale": row.rationale, "angle": row.angle}

    def list_image_assets(self, run_id: str | None = None) -> dict[str, list[dict[str, Any]]]:
        with session_scope() as session:
            stmt = select(ImageAsset.id, ImageAsset.draft_id, ImageAsset.provider, ImageAsset.path, ImageAsset.status, WorkflowRun.id.label("run_id")).join(ContentDraft, ImageAsset.draft_id == ContentDraft.id).join(TopicSuggestion, ContentDraft.topic_id == TopicSuggestion.id).join(AnalysisReport, TopicSuggestion.report_id == AnalysisReport.id).join(WorkflowRun, AnalysisReport.run_id == WorkflowRun.id).order_by(ImageAsset.id)
            if run_id:
                stmt = stmt.where(WorkflowRun.id == run_id)
            rows = session.execute(stmt).all()
            return {"items": [{"id": row.id, "draft_id": row.draft_id, "run_id": row.run_id, "provider": row.provider, "path": row.path, "status": row.status} for row in rows]}

    def get_image_asset(self, image_id: str) -> dict[str, Any]:
        with session_scope() as session:
            stmt = select(ImageAsset.id, ImageAsset.draft_id, ImageAsset.provider, ImageAsset.path, ImageAsset.status, WorkflowRun.id.label("run_id")).join(ContentDraft, ImageAsset.draft_id == ContentDraft.id).join(TopicSuggestion, ContentDraft.topic_id == TopicSuggestion.id).join(AnalysisReport, TopicSuggestion.report_id == AnalysisReport.id).join(WorkflowRun, AnalysisReport.run_id == WorkflowRun.id).where(ImageAsset.id == image_id)
            row = session.execute(stmt).first()
            if row is None:
                raise ValueError(f"Unknown image asset: {image_id}")
            return {"id": row.id, "draft_id": row.draft_id, "run_id": row.run_id, "provider": row.provider, "path": row.path, "status": row.status}

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

    def regenerate_draft(self, draft_id: str, review_notes: str = "") -> dict[str, Any]:
        with session_scope() as session:
            draft = session.get(ContentDraft, draft_id)
            if draft is None:
                raise ValueError(f"Unknown draft: {draft_id}")
            if ContentDraftStatus(draft.status) != ContentDraftStatus.REJECTED:
                raise ValueError("Only rejected drafts can be regenerated.")
            draft.body = draft.body + "\n\n[Revision] Strengthened hook and tightened opening lines."
            draft.review_notes = review_notes
            draft.revision_count += 1
            draft.status = ContentDraftStatus.REVIEW_PENDING.value
            self._log(session, "draft.regenerated", "content_draft", draft.id, {"review_notes": review_notes, "revision_count": draft.revision_count})
            return {"id": draft.id, "status": draft.status, "review_notes": draft.review_notes, "revision_count": draft.revision_count}

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
            result = execution_publisher.publish(type("DraftAdapter", (), {"title": draft.title, "body": draft.body, "tags": draft.tags, "cta": draft.cta, "image_prompt": draft.image_prompt, "content_type": draft.content_type})())
            publish_job.status = PublishJobStatus.PUBLISHED.value
            publish_job.provider = result.provider
            publish_job.mode = result.mode
            publish_job.published_url = result.published_url
            publish_job.details = {"provider": result.provider, "mode": result.mode}
            draft.status = transition_draft_status(ContentDraftStatus.PUBLISH_READY, "publish").value
            self._log(session, "publish.completed", "publish_job", publish_job.id, {"published_url": publish_job.published_url})

            sync_result, sync_record = self._sync_entity(
                session,
                entity_type="publish_job",
                entity_id=publish_job.id,
                payload={"draft_id": draft.id, "published_url": publish_job.published_url, "title": draft.title},
                origin="publish",
            )
            return {
                "status": publish_job.status,
                "publish_job": {"id": publish_job.id, "status": publish_job.status, "published_url": publish_job.published_url, "provider": publish_job.provider},
                "sync_record": {"id": sync_record.id, "status": sync_record.status, "target": sync_record.target, "provider": sync_record.provider},
                "sync_diagnostics": sync_result.get("diagnostics", {}),
            }

    def list_audit_logs(self) -> dict[str, list[dict[str, Any]]]:
        with session_scope() as session:
            rows = session.scalars(select(AuditLog).order_by(AuditLog.created_at)).all()
            return {"items": [{"id": row.id, "event_type": row.event_type, "entity_type": row.entity_type, "entity_id": row.entity_id, "details": row.details} for row in rows]}

    def list_sync_records(self) -> dict[str, list[dict[str, Any]]]:
        with session_scope() as session:
            rows = session.scalars(select(SyncRecord).order_by(SyncRecord.created_at.desc())).all()
            return {
                "items": [
                    {
                        "id": row.id,
                        "entity_type": row.entity_type,
                        "entity_id": row.entity_id,
                        "provider": row.provider,
                        "target": row.target,
                        "status": row.status,
                        "dry_run": bool(row.dry_run),
                        "diagnostics": row.diagnostics,
                    }
                    for row in rows
                ]
            }

    def list_publish_jobs(self) -> dict[str, list[dict[str, Any]]]:
        with session_scope() as session:
            rows = session.scalars(select(PublishJob).order_by(PublishJob.id)).all()
            return {"items": [{"id": row.id, "draft_id": row.draft_id, "provider": row.provider, "mode": row.mode, "status": row.status, "published_url": row.published_url} for row in rows]}

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

    def inspect_external_worker_job(self, job_id: str) -> dict[str, Any]:
        return build_external_worker_adapter().inspect(job_id)

    def cancel_external_worker_job(self, job_id: str) -> dict[str, Any]:
        return build_external_worker_adapter().cancel(job_id)

    def requeue_external_worker_job(self, job_id: str) -> dict[str, Any]:
        return build_external_worker_adapter().requeue(job_id)

    def provider_diagnostics(self) -> dict[str, dict[str, Any]]:
        settings = get_settings()
        return {
            "collector": self._provider_summary(settings.default_collector_provider, self.collector, {"safe_mode": settings.scrapling_mode != "live"}),
            "language_model": self._provider_summary(settings.default_model_provider, self.llm, {"model_name": settings.resolved_model_name}),
            "image": self._provider_summary(settings.default_image_provider, self.image, {"model_name": settings.resolved_image_model_name}),
            "publisher": self._provider_summary(settings.default_publish_provider, self.publisher, {}),
            "sync": self._provider_summary(settings.default_sync_provider, self.sync, {"sync_mode": settings.feishu_sync_mode}),
        }

    def provider_health(self) -> dict[str, dict[str, Any]]:
        settings = get_settings()
        collector_health = self.collector.health() if hasattr(self.collector, "health") else {"status": "ready", "reason": "collector available"}
        llm_health = self.llm.health() if hasattr(self.llm, "health") else {"status": "ready", "reason": "model provider available"}
        image_health = self.image.health() if hasattr(self.image, "health") else {"status": "ready", "reason": "image provider available"}
        sync_health = self.sync.health() if hasattr(self.sync, "health") else {"status": "ready", "reason": "sync provider available"}
        publish_status = "ready"
        publish_reason = "safe publish path available"
        if settings.default_publish_provider == "api" and settings.enable_real_publish_provider and (not settings.xhs_publish_api_token or not settings.xhs_publish_api_base):
            publish_status = "degraded"
            publish_reason = "missing publish api credentials"
        if settings.default_publish_provider == "browser" and settings.enable_real_publish_provider and not settings.playwright_storage_state_path:
            publish_status = "degraded"
            publish_reason = "missing browser storage state"
        return {
            "collector": collector_health,
            "language_model": llm_health,
            "image": image_health,
            "publisher": {"status": publish_status, "reason": publish_reason},
            "sync": sync_health,
        }

    def dashboard(self) -> dict[str, Any]:
        return {
            "app_name": self.settings.app_name,
            "runs": self.list_runs()["items"][:10],
            "collector_runs": self.list_collector_runs()["items"][:10],
            "sync_runs": self.list_sync_runs()["items"][:10],
            "drafts": self.list_drafts(),
            "observability": self.observability_summary(),
            "provider_diagnostics": self.provider_diagnostics(),
            "provider_health": self.provider_health(),
            "publish_jobs": self.list_publish_jobs()["items"][:10],
            "sync_records": self.list_sync_records()["items"][:10],
            "audit_logs": self.list_audit_logs()["items"][:10],
        }

    def _sync_entity(self, session, entity_type: str, entity_id: str, payload: dict, origin: str):
        result = self.sync.sync(entity_type, payload)
        diagnostics = result.get("diagnostics", {})
        sync_record = SyncRecord(
            entity_type=entity_type,
            entity_id=entity_id,
            provider=result.get("provider", self.sync.name),
            target=result["target"],
            status=result["status"],
            dry_run=1 if result.get("dry_run") else 0,
            payload=result.get("payload", payload),
            diagnostics=diagnostics,
        )
        session.add(sync_record)
        session.flush()
        session.add(
            SyncRun(
                provider=result.get("provider", self.sync.name),
                entity_type=entity_type,
                status=result["status"],
                dry_run=1 if result.get("dry_run") else 0,
                request_payload=payload,
                result_summary={"target": result["target"], "sync_record_id": sync_record.id},
                diagnostics={**diagnostics, "origin": origin},
                failure_category=diagnostics.get("reason"),
                attempt_count=diagnostics.get("attempts", 1),
            )
        )
        self._log(session, "sync.completed" if result["status"] == "synced" else "sync.failed", "sync_record", sync_record.id, {"target": sync_record.target, "provider": sync_record.provider})
        return result, sync_record

    def _persist_source_posts(self, session, owner_id: str, posts: list, provider_name: str) -> tuple[int, int]:
        fingerprints = [self._fingerprint_for_post(post) for post in posts]
        existing = set()
        if fingerprints:
            rows = session.scalars(select(SourcePost).where(SourcePost.run_id == owner_id, SourcePost.fingerprint.in_(fingerprints))).all()
            existing = {row.fingerprint for row in rows}
        persisted = 0
        duplicates = 0
        seen = set(existing)
        for post in posts:
            fingerprint = self._fingerprint_for_post(post)
            if fingerprint in seen:
                duplicates += 1
                continue
            seen.add(fingerprint)
            persisted += 1
            session.add(
                SourcePost(
                    run_id=owner_id,
                    provider=provider_name,
                    keyword=post.keyword,
                    title=post.title,
                    content=post.content,
                    likes=post.likes,
                    favorites=post.favorites,
                    comments=post.comments,
                    author=post.author,
                    url=post.url,
                    fingerprint=fingerprint,
                    tags=post.tags,
                    raw_data=post.raw_metrics or {},
                )
            )
        return persisted, duplicates

    @staticmethod
    def _fingerprint_for_post(post) -> str:
        note_id = (post.raw_metrics or {}).get("note_id") if getattr(post, "raw_metrics", None) else None
        return f"xhs::{note_id or post.url}"

    @staticmethod
    def _provider_metadata(provider) -> dict:
        if hasattr(provider, "last_run_metadata"):
            return getattr(provider, "last_run_metadata") or {}
        if hasattr(provider, "diagnostics"):
            return provider.diagnostics() or {}
        return {}

    @staticmethod
    def _attempt_count(metadata: dict) -> int:
        if not metadata:
            return 1
        return int(metadata.get("attempts") or metadata.get("attempt_count") or 1)

    @staticmethod
    def _failure_category(exc: Exception) -> str:
        text = str(exc).lower()
        if "timeout" in text:
            return "timeout"
        if "schema" in text or "parse" in text or "json" in text:
            return "schema_validation"
        if "credential" in text or "api key" in text:
            return "credential"
        return "runtime"

    @staticmethod
    def _provider_summary(configured: str, provider, extra: dict) -> dict:
        payload = {"configured": configured, "active": provider.name, **extra}
        if hasattr(provider, "diagnostics"):
            payload.update(provider.diagnostics())
        return payload

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
