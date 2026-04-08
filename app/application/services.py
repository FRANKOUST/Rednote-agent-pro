from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from typing import Any

from sqlalchemy import func, select

from app.application.dispatcher import build_dispatcher
from app.application.external_worker import build_external_worker_adapter
from app.core.config import get_settings
from app.db.models import (
    AnalysisReport,
    AuditLog,
    CollectorRun,
    ContentDraft,
    ImageAsset,
    PublishJob,
    SourcePost,
    SyncRecord,
    SyncRun,
    TopicSuggestion,
    WorkflowRun,
    WorkflowStageEvent,
)
from app.db.session import session_scope
from app.domain.models import (
    ContentDraftStatus,
    PIPELINE_STAGES,
    PublishJobStatus,
    PublishPackagePayload,
    StageStatus,
    SyncStatus,
    WorkflowRunStatus,
    transition_draft_status,
)
from app.infrastructure.providers.publisher.api_safe_stub import XiaohongshuAPISafeStubProvider
from app.infrastructure.providers.publisher.browser_safe_stub import XiaohongshuBrowserSafeStubProvider
from app.infrastructure.providers.registry import build_provider_registry


def record_id_placeholder(entity_type: str) -> str:
    return f"manual::{entity_type}"


class PipelineService:
    stage_order = PIPELINE_STAGES

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
        normalized = self._normalize_run_payload(payload)
        with session_scope() as session:
            run = WorkflowRun(
                status=WorkflowRunStatus.QUEUED.value,
                current_stage="queued",
                execution_mode=normalized["run_mode"],
                request_payload=normalized,
                result_summary={"stages": []},
            )
            session.add(run)
            session.flush()
            run_id = run.id
            self._log(session, "pipeline.run.created", "workflow_run", run.id, {"run_mode": normalized["run_mode"]})
        if normalized["run_mode"] == "full":
            self.dispatcher.dispatch(self.execute_run, run_id)
        return self.get_run(run_id)

    def execute_run(self, run_id: str) -> dict[str, Any]:
        for stage in self.stage_order:
            self.run_stage(run_id, stage)
        with session_scope() as session:
            run = session.get(WorkflowRun, run_id)
            if run is None:
                raise ValueError(f"Unknown run: {run_id}")
            if run.status != WorkflowRunStatus.FAILED.value:
                run.status = WorkflowRunStatus.COMPLETED.value
            run.current_stage = "sync"
        return self.get_run(run_id)

    def run_stage(self, run_id: str, stage: str, overrides: dict | None = None) -> dict[str, Any]:
        if stage not in self.stage_order:
            raise ValueError(f"Unknown stage: {stage}")
        handler = getattr(self, f"_run_{stage}_stage")
        with session_scope() as session:
            run = session.get(WorkflowRun, run_id)
            if run is None:
                raise ValueError(f"Unknown run: {run_id}")
            run.status = WorkflowRunStatus.RUNNING.value
            run.current_stage = stage
            request_payload = {**dict(run.request_payload), **(overrides or {})}
            stage_row = WorkflowStageEvent(
                run_id=run.id,
                stage=stage,
                status=StageStatus.RUNNING.value,
                provider=self._provider_name_for_stage(stage),
                input_summary=self._summarize_input(stage, request_payload),
                output_summary={},
                error_message=None,
                details={},
                started_at=datetime.utcnow(),
                finished_at=None,
            )
            session.add(stage_row)
            session.flush()
            try:
                output = handler(session, run, request_payload)
                stage_row.status = output.get("stage_status", StageStatus.COMPLETED.value)
                stage_row.provider = output.get("provider", stage_row.provider)
                stage_row.output_summary = output.get("output_summary", {})
                stage_row.details = output.get("details", {})
                stage_row.finished_at = datetime.utcnow()
                run.result_summary = {**(run.result_summary or {}), stage: stage_row.output_summary}
                if stage == self.stage_order[-1] and run.status != WorkflowRunStatus.FAILED.value:
                    run.status = WorkflowRunStatus.COMPLETED.value
                elif stage == "review":
                    run.status = WorkflowRunStatus.ACTION_REQUIRED.value
                self._log(session, f"pipeline.stage.{stage_row.status}", "workflow_run", run.id, {"stage": stage, "output_summary": stage_row.output_summary})
                stage_payload = self._serialize_stage_row(stage_row)
            except Exception as exc:
                stage_row.status = StageStatus.FAILED.value
                stage_row.error_message = str(exc)
                stage_row.finished_at = datetime.utcnow()
                run.status = WorkflowRunStatus.FAILED.value
                run.error_message = str(exc)
                self._log(session, "pipeline.failed", "workflow_run", run.id, {"stage": stage, "error": str(exc)})
                raise
        return {"run_id": run_id, "stage": stage_payload}

    def _run_crawl_stage(self, session, run: WorkflowRun, payload: dict) -> dict[str, Any]:
        collector_run = CollectorRun(
            workflow_run_id=run.id,
            provider=self.collector.name,
            collection_type=payload.get("collection_type", "search"),
            status="running",
            request_payload=payload,
            result_summary={},
            diagnostics={"origin": "pipeline"},
        )
        session.add(collector_run)
        session.flush()
        posts = self.collector.collect(payload)
        persisted_posts, duplicate_posts = self._persist_source_posts(session, run.id, posts, self.collector.name)
        metadata = self._provider_metadata(self.collector)
        collector_run.status = "completed"
        collector_run.result_summary = {
            "fetched_posts": len(posts),
            "persisted_posts": persisted_posts,
            "duplicate_posts": duplicate_posts,
            "candidate_count": metadata.get("candidate_count", len(posts)),
            "detail_hydrated_count": metadata.get("detail_hydrated_count", len(posts)),
        }
        collector_run.diagnostics = metadata
        collector_run.attempt_count = self._attempt_count(metadata)
        collector_run.failure_category = metadata.get("failure_category")
        return {"provider": self.collector.name, "output_summary": collector_run.result_summary, "details": metadata}

    def _run_analyze_stage(self, session, run: WorkflowRun, payload: dict) -> dict[str, Any]:
        posts = self._source_post_rows(session, run.id)
        analysis = self.llm.analyze([self._source_post_payload(row) for row in posts])
        report = AnalysisReport(
            run_id=run.id,
            summary=analysis.summary,
            top_keywords=analysis.high_frequency_keywords,
            top_tags=analysis.hot_tags,
            title_patterns=analysis.title_patterns,
            opening_patterns=analysis.opening_patterns,
            content_structure_templates=analysis.content_structure_templates,
            user_pain_points=analysis.user_pain_points,
            user_delight_points=analysis.user_delight_points,
            user_focus_points=analysis.user_focus_points,
            engagement_triggers=analysis.engagement_triggers,
            applicable_tracks=analysis.applicable_tracks,
            viral_hooks=analysis.viral_hooks,
            risk_alerts=analysis.risk_alerts,
        )
        session.add(report)
        session.flush()
        return {"provider": self.llm.name, "output_summary": {"analysis_report_id": report.id, "hot_tags": report.top_tags[:3], "viral_hooks": report.viral_hooks[:3]}, "details": self._provider_metadata(self.llm)}

    def _run_topic_stage(self, session, run: WorkflowRun, payload: dict) -> dict[str, Any]:
        analysis_row = self._latest_analysis_row(session, run.id)
        analysis = self._analysis_payload(analysis_row)
        topics = self.llm.suggest_topics(analysis)
        topic_ids: list[str] = []
        for topic in topics:
            row = TopicSuggestion(
                report_id=analysis_row.id,
                title=topic.title,
                rationale=topic.reason,
                angle=topic.angle or topic.recommended_format,
                target_audience=topic.target_audience,
                reference_hooks=topic.reference_hooks,
                analysis_evidence=topic.analysis_evidence,
                risk_notes=topic.risk_notes,
                recommended_format=topic.recommended_format,
                priority=topic.priority,
                confidence=int(topic.confidence * 100),
            )
            session.add(row)
            session.flush()
            topic_ids.append(row.id)
        return {"provider": self.llm.name, "output_summary": {"topic_count": len(topic_ids), "topic_ids": topic_ids}, "details": self._provider_metadata(self.llm)}

    def _run_draft_stage(self, session, run: WorkflowRun, payload: dict) -> dict[str, Any]:
        analysis_row = self._latest_analysis_row(session, run.id)
        analysis = self._analysis_payload(analysis_row)
        topic_rows = self._topic_rows(session, run.id)
        draft_ids: list[str] = []
        for topic_row in topic_rows:
            topic = self._topic_payload(topic_row)
            draft_payload = self.llm.generate_draft(topic, analysis)
            row = ContentDraft(
                topic_id=topic_row.id,
                status=transition_draft_status(ContentDraftStatus.CREATED, "generate").value,
                title=draft_payload.headline,
                alternate_titles=draft_payload.alternate_headlines,
                body=draft_payload.body,
                tags=draft_payload.tags,
                cta=draft_payload.cta,
                image_prompt=draft_payload.image_prompt,
                image_suggestions=draft_payload.image_suggestions,
                content_type=draft_payload.content_type,
                target_user=draft_payload.target_user,
                tone_style=draft_payload.tone_style,
                risk_notes=draft_payload.risk_notes,
                review_notes="\n".join(draft_payload.review_notes),
                revision_notes=draft_payload.revision_notes,
            )
            row.status = transition_draft_status(ContentDraftStatus(row.status), "submit_for_review").value
            session.add(row)
            session.flush()
            draft_ids.append(row.id)
        return {"provider": self.llm.name, "output_summary": {"draft_count": len(draft_ids), "draft_ids": draft_ids}, "details": self._provider_metadata(self.llm)}

    def _run_image_stage(self, session, run: WorkflowRun, payload: dict) -> dict[str, Any]:
        analysis_row = self._latest_analysis_row(session, run.id)
        analysis = self._analysis_payload(analysis_row)
        draft_rows = self._draft_rows(session, run.id)
        image_ids: list[str] = []
        for draft_row in draft_rows:
            draft_payload = self._draft_payload(draft_row)
            image_plan = self.llm.plan_image(draft_payload, analysis)
            adjusted_draft = draft_payload.__class__(
                headline=draft_payload.headline,
                alternate_headlines=draft_payload.alternate_headlines,
                body=draft_payload.body,
                tags=draft_payload.tags,
                cta=draft_payload.cta,
                image_suggestions=image_plan.asset_notes or draft_payload.image_suggestions,
                image_prompt=image_plan.prompt,
                content_type=draft_payload.content_type,
                target_user=draft_payload.target_user,
                tone_style=draft_payload.tone_style,
                risk_notes=draft_payload.risk_notes,
                review_notes=draft_payload.review_notes,
                revision_notes=draft_payload.revision_notes,
            )
            asset = self.image.generate(adjusted_draft)
            row = ImageAsset(draft_id=draft_row.id, provider=asset.provider, path=asset.path, prompt=asset.prompt, status="generated")
            session.add(row)
            session.flush()
            image_ids.append(row.id)
        return {"provider": self.image.name, "output_summary": {"image_count": len(image_ids), "image_ids": image_ids}, "details": self._provider_metadata(self.image)}

    def _run_review_stage(self, session, run: WorkflowRun, payload: dict) -> dict[str, Any]:
        draft_rows = self._draft_rows(session, run.id)
        pending_ids: list[str] = []
        for draft in draft_rows:
            if draft.status != ContentDraftStatus.REVIEW_PENDING.value:
                draft.status = ContentDraftStatus.REVIEW_PENDING.value
            pending_ids.append(draft.id)
        return {"provider": "system", "output_summary": {"review_state": "manual_review_required", "pending_draft_ids": pending_ids}, "details": {"safety_gate": self.settings.keep_publish_safety_gate}}

    def _run_publish_stage(self, session, run: WorkflowRun, payload: dict) -> dict[str, Any]:
        draft_rows = self._draft_rows(session, run.id)
        target = next((row for row in draft_rows if row.status in {ContentDraftStatus.APPROVED.value, ContentDraftStatus.PUBLISH_READY.value}), None)
        if target is None and draft_rows:
            target = draft_rows[0]
        if target is None:
            return {"provider": self.publisher.name, "output_summary": {"mode": "skipped", "reason": "no drafts"}, "details": {}}
        prepared = self._prepare_publish_in_session(session, target)
        preview = self._preview_publish_in_session(session, target, prepared)
        if payload.get("auto_publish") and target.status in {ContentDraftStatus.APPROVED.value, ContentDraftStatus.PUBLISH_READY.value} and not self.settings.keep_publish_safety_gate:
            sent = self._send_publish_in_session(session, target, prepared, bool(payload.get("dry_run", True)))
            return {"provider": self.publisher.name, "output_summary": {"mode": "send", "publish_job_id": sent["publish_job"]["id"], "published_url": sent["publish_job"]["published_url"]}, "details": preview}
        return {"provider": self.publisher.name, "output_summary": {"mode": "preview_only", "publish_job_id": prepared["publish_job_id"], "headline": preview["headline"]}, "details": preview}

    def _run_sync_stage(self, session, run: WorkflowRun, payload: dict) -> dict[str, Any]:
        crawled = self._sync_business(session, "sync_crawled", run.id, self._sync_crawled_payload(session, run.id), dry_run=bool(payload.get("dry_run", True)), origin="pipeline")
        generated = self._sync_business(session, "sync_generated", run.id, self._sync_generated_payload(session, run.id), dry_run=bool(payload.get("dry_run", True)), origin="pipeline")
        return {"provider": self.sync.name, "output_summary": {"sync_crawled_record_id": crawled[1].id, "sync_generated_record_id": generated[1].id}, "details": {"sync_crawled": crawled[0], "sync_generated": generated[0]}}

    def get_run(self, run_id: str) -> dict[str, Any]:
        with session_scope() as session:
            run = session.get(WorkflowRun, run_id)
            if run is None:
                raise ValueError(f"Unknown run: {run_id}")
            stages = [self._serialize_stage_row(row) for row in self._stage_rows(session, run_id)]
            draft_ids = self._draft_ids_for_run(session, run_id)
            source_count = session.scalar(select(func.count()).select_from(SourcePost).where(SourcePost.run_id == run.id)) or 0
            report_count = session.scalar(select(func.count()).select_from(AnalysisReport).where(AnalysisReport.run_id == run.id)) or 0
            topic_count = len(self._topic_rows(session, run.id))
            image_count = session.scalar(select(func.count()).select_from(ImageAsset).where(ImageAsset.draft_id.in_(draft_ids))) if draft_ids else 0
            return {
                "id": run.id,
                "status": run.status,
                "current_stage": run.current_stage,
                "execution_mode": run.execution_mode,
                "counts": {"source_posts": source_count, "analysis_reports": report_count, "topic_suggestions": topic_count, "content_drafts": len(draft_ids), "image_assets": image_count or 0},
                "draft_ids": draft_ids,
                "request_payload": run.request_payload,
                "result_summary": run.result_summary,
                "error_message": run.error_message,
                "stages": stages,
                "stage_map": {stage["stage"]: stage for stage in stages},
            }

    def list_runs(self) -> dict[str, list[dict[str, Any]]]:
        with session_scope() as session:
            rows = session.scalars(select(WorkflowRun).order_by(WorkflowRun.created_at.desc())).all()
            return {"items": [{"id": row.id, "status": row.status, "current_stage": row.current_stage, "execution_mode": row.execution_mode, "created_at": row.created_at.isoformat() if row.created_at else None} for row in rows]}

    def get_run_diagnostics(self, run_id: str) -> dict[str, list[dict[str, Any]]]:
        with session_scope() as session:
            rows = self._stage_rows(session, run_id)
            return {"items": [self._serialize_stage_row(row) for row in rows]}

    def list_drafts(self) -> list[dict[str, Any]]:
        with session_scope() as session:
            drafts = session.scalars(select(ContentDraft).order_by(ContentDraft.id)).all()
            return [self._serialize_draft_row(draft) for draft in drafts]

    def list_source_posts(self, run_id: str | None = None) -> dict[str, list[dict[str, Any]]]:
        with session_scope() as session:
            stmt = select(SourcePost).order_by(SourcePost.id)
            if run_id:
                stmt = stmt.where(SourcePost.run_id == run_id)
            rows = session.scalars(stmt).all()
            return {"items": [self._serialize_source_post(row) for row in rows]}

    def get_source_post(self, source_post_id: str) -> dict[str, Any]:
        with session_scope() as session:
            row = session.get(SourcePost, source_post_id)
            if row is None:
                raise ValueError(f"Unknown source post: {source_post_id}")
            return self._serialize_source_post(row)

    def list_analysis_reports(self, run_id: str | None = None) -> dict[str, list[dict[str, Any]]]:
        with session_scope() as session:
            stmt = select(AnalysisReport).order_by(AnalysisReport.id)
            if run_id:
                stmt = stmt.where(AnalysisReport.run_id == run_id)
            rows = session.scalars(stmt).all()
            return {"items": [self._serialize_analysis_row(row) for row in rows]}

    def get_analysis_report(self, report_id: str) -> dict[str, Any]:
        with session_scope() as session:
            row = session.get(AnalysisReport, report_id)
            if row is None:
                raise ValueError(f"Unknown analysis report: {report_id}")
            return self._serialize_analysis_row(row)

    def list_topic_suggestions(self, run_id: str | None = None) -> dict[str, list[dict[str, Any]]]:
        with session_scope() as session:
            stmt = select(TopicSuggestion, AnalysisReport.run_id).join(AnalysisReport, TopicSuggestion.report_id == AnalysisReport.id).order_by(TopicSuggestion.id)
            if run_id:
                stmt = stmt.where(AnalysisReport.run_id == run_id)
            rows = session.execute(stmt).all()
            return {"items": [self._serialize_topic_row(topic, run_id=row_run_id) for topic, row_run_id in rows]}

    def get_topic_suggestion(self, topic_id: str) -> dict[str, Any]:
        with session_scope() as session:
            stmt = select(TopicSuggestion, AnalysisReport.run_id).join(AnalysisReport, TopicSuggestion.report_id == AnalysisReport.id).where(TopicSuggestion.id == topic_id)
            row = session.execute(stmt).first()
            if row is None:
                raise ValueError(f"Unknown topic suggestion: {topic_id}")
            topic, run_id = row
            return self._serialize_topic_row(topic, run_id=run_id)

    def list_image_assets(self, run_id: str | None = None) -> dict[str, list[dict[str, Any]]]:
        with session_scope() as session:
            draft_ids = self._draft_ids_for_run(session, run_id) if run_id else None
            stmt = select(ImageAsset).order_by(ImageAsset.id)
            if draft_ids is not None:
                stmt = stmt.where(ImageAsset.draft_id.in_(draft_ids))
            rows = session.scalars(stmt).all()
            return {"items": [self._serialize_image_row(row, run_id=run_id) for row in rows]}

    def get_image_asset(self, image_id: str) -> dict[str, Any]:
        with session_scope() as session:
            row = session.get(ImageAsset, image_id)
            if row is None:
                raise ValueError(f"Unknown image asset: {image_id}")
            run_id = self._run_id_for_draft(session, row.draft_id)
            return self._serialize_image_row(row, run_id=run_id)

    def approve_draft(self, draft_id: str, review_notes: str = "") -> dict[str, Any]:
        with session_scope() as session:
            draft = session.get(ContentDraft, draft_id)
            if draft is None:
                raise ValueError(f"Unknown draft: {draft_id}")
            draft.status = transition_draft_status(ContentDraftStatus(draft.status), "approve").value
            draft.review_notes = review_notes or draft.review_notes
            self._log(session, "review.approve", "content_draft", draft.id, {"review_notes": review_notes})
            return self._serialize_draft_row(draft)

    def reject_draft(self, draft_id: str, review_notes: str = "") -> dict[str, Any]:
        with session_scope() as session:
            draft = session.get(ContentDraft, draft_id)
            if draft is None:
                raise ValueError(f"Unknown draft: {draft_id}")
            draft.status = transition_draft_status(ContentDraftStatus(draft.status), "reject").value
            draft.review_notes = review_notes or draft.review_notes
            self._log(session, "review.reject", "content_draft", draft.id, {"review_notes": review_notes})
            return self._serialize_draft_row(draft)

    def regenerate_draft(self, draft_id: str, review_notes: str = "") -> dict[str, Any]:
        with session_scope() as session:
            draft = session.get(ContentDraft, draft_id)
            if draft is None:
                raise ValueError(f"Unknown draft: {draft_id}")
            if ContentDraftStatus(draft.status) not in {ContentDraftStatus.REJECTED, ContentDraftStatus.REVISION_REQUESTED}:
                raise ValueError("Only rejected or revision-requested drafts can be regenerated.")
            draft.revision_count += 1
            draft.revision_notes = [*(draft.revision_notes or []), review_notes or "Strengthened opening hook"]
            draft.status = transition_draft_status(ContentDraftStatus(draft.status), "regenerate").value
            self._log(session, "review.revise", "content_draft", draft.id, {"review_notes": review_notes, "revision_count": draft.revision_count})
            return self._serialize_draft_row(draft)

    def prepare_publish(self, draft_id: str) -> dict[str, Any]:
        with session_scope() as session:
            draft = session.get(ContentDraft, draft_id)
            if draft is None:
                raise ValueError(f"Unknown draft: {draft_id}")
            return self._prepare_publish_in_session(session, draft)

    def preview_publish(self, draft_id: str) -> dict[str, Any]:
        with session_scope() as session:
            draft = session.get(ContentDraft, draft_id)
            if draft is None:
                raise ValueError(f"Unknown draft: {draft_id}")
            prepared = self._prepare_publish_in_session(session, draft)
            preview = self._preview_publish_in_session(session, draft, prepared)
            return {"status": "preview_ready", "preview": preview, "publish_job_id": prepared["publish_job_id"]}

    def send_publish(self, draft_id: str, dry_run: bool = True) -> dict[str, Any]:
        with session_scope() as session:
            draft = session.get(ContentDraft, draft_id)
            if draft is None:
                raise ValueError(f"Unknown draft: {draft_id}")
            existing = session.scalars(select(PublishJob).where(PublishJob.draft_id == draft_id, PublishJob.status == PublishJobStatus.PUBLISHED.value)).first()
            if existing is not None:
                raise ValueError("Draft has already been published.")
            prepared = self._prepare_publish_in_session(session, draft)
            preview = self._preview_publish_in_session(session, draft, prepared)
            result = self._send_publish_in_session(session, draft, prepared, dry_run)
            result["preview"] = preview
            return result

    def publish_draft(self, draft_id: str) -> dict[str, Any]:
        result = self.send_publish(draft_id, dry_run=True)
        with session_scope() as session:
            publish_job_id = result["publish_job"]["id"]
            sync_result, sync_record = self._sync_business(session, "sync_generated", publish_job_id, {"entity_type": "publish_job", "draft_id": draft_id, "published_url": result["publish_job"]["published_url"]}, dry_run=True, origin="publish")
            result["sync_record"] = self._serialize_sync_record(sync_record)
            result["sync_diagnostics"] = sync_result.get("diagnostics", {})
        return result

    def sync_crawled(self, run_id: str, dry_run: bool = True) -> dict[str, Any]:
        with session_scope() as session:
            payload = self._sync_crawled_payload(session, run_id)
            result, record = self._sync_business(session, "sync_crawled", run_id, payload, dry_run=dry_run, origin="manual")
            return {"result": result, "record": self._serialize_sync_record(record)}

    def sync_generated(self, run_id: str, dry_run: bool = True) -> dict[str, Any]:
        with session_scope() as session:
            payload = self._sync_generated_payload(session, run_id)
            result, record = self._sync_business(session, "sync_generated", run_id, payload, dry_run=dry_run, origin="manual")
            return {"result": result, "record": self._serialize_sync_record(record)}

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
            posts = self.collector.collect({**payload, "collection_type": collection_type})
            persisted_posts, duplicate_posts = self._persist_source_posts(session, row.id, posts, self.collector.name)
            provider_meta = self._provider_metadata(self.collector)
            row.status = "completed"
            row.result_summary = {"fetched_posts": len(posts), "persisted_posts": persisted_posts, "duplicate_posts": duplicate_posts}
            row.diagnostics = provider_meta
            row.attempt_count = self._attempt_count(provider_meta)
            row.failure_category = provider_meta.get("failure_category")
        return self.get_collector_run(run_id)

    def list_collector_runs(self) -> dict[str, list[dict[str, Any]]]:
        with session_scope() as session:
            rows = session.scalars(select(CollectorRun).order_by(CollectorRun.created_at.desc())).all()
            return {"items": [{"id": row.id, "provider": row.provider, "collection_type": row.collection_type, "status": row.status, "created_at": row.created_at.isoformat() if row.created_at else None} for row in rows]}

    def get_collector_run(self, collector_run_id: str) -> dict[str, Any]:
        with session_scope() as session:
            row = session.get(CollectorRun, collector_run_id)
            if row is None:
                raise ValueError(f"Unknown collector run: {collector_run_id}")
            return {"id": row.id, "provider": row.provider, "collection_type": row.collection_type, "status": row.status, "request_payload": row.request_payload, "result_summary": row.result_summary, "diagnostics": row.diagnostics, "failure_category": row.failure_category, "attempt_count": row.attempt_count}

    def start_sync_run(self, entity_type: str, payload: dict, dry_run: bool) -> dict[str, Any]:
        business_type = payload.get("business_type") or entity_type
        with session_scope() as session:
            result, record = self._sync_business(session, business_type, payload.get("run_id", record_id_placeholder(entity_type)), payload, dry_run=dry_run, origin="manual")
            session.flush(); sync_run = session.scalars(select(SyncRun).order_by(SyncRun.created_at.desc())).first()
            return self._serialize_sync_run(sync_run) if sync_run is not None else {**result, "record": self._serialize_sync_record(record)}

    def list_sync_runs(self) -> dict[str, list[dict[str, Any]]]:
        with session_scope() as session:
            rows = session.scalars(select(SyncRun).order_by(SyncRun.created_at.desc())).all()
            return {"items": [self._serialize_sync_run(row) for row in rows]}

    def get_sync_run(self, sync_run_id: str) -> dict[str, Any]:
        with session_scope() as session:
            row = session.get(SyncRun, sync_run_id)
            if row is None:
                raise ValueError(f"Unknown sync run: {sync_run_id}")
            return self._serialize_sync_run(row)

    def list_audit_logs(self) -> dict[str, list[dict[str, Any]]]:
        with session_scope() as session:
            rows = session.scalars(select(AuditLog).order_by(AuditLog.created_at)).all()
            return {"items": [{"id": row.id, "event_type": row.event_type, "entity_type": row.entity_type, "entity_id": row.entity_id, "details": row.details} for row in rows]}

    def list_sync_records(self) -> dict[str, list[dict[str, Any]]]:
        with session_scope() as session:
            rows = session.scalars(select(SyncRecord).order_by(SyncRecord.created_at.desc())).all()
            return {"items": [self._serialize_sync_record(row) for row in rows]}

    def list_publish_jobs(self) -> dict[str, list[dict[str, Any]]]:
        with session_scope() as session:
            rows = session.scalars(select(PublishJob).order_by(PublishJob.id)).all()
            return {"items": [self._serialize_publish_job(row) for row in rows]}

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
        collector_health = self.collector.health() if hasattr(self.collector, "health") else {"status": "ready", "reason": "collector available"}
        llm_health = self.llm.health() if hasattr(self.llm, "health") else {"status": "ready", "reason": "model provider available"}
        image_health = self.image.health() if hasattr(self.image, "health") else {"status": "ready", "reason": "image provider available"}
        sync_health = self.sync.health() if hasattr(self.sync, "health") else {"status": "ready", "reason": "sync provider available"}
        publish_health = self.publisher.health() if hasattr(self.publisher, "health") else {"status": "ready", "reason": "publisher available"}
        return {"collector": collector_health, "language_model": llm_health, "image": image_health, "publisher": publish_health, "sync": sync_health}

    def check_collector_login(self) -> dict[str, Any]:
        if hasattr(self.collector, "check_login"):
            return self.collector.check_login()
        return {"provider": self.collector.name, **self.collector.health()}

    def check_publish_login(self) -> dict[str, Any]:
        if hasattr(self.publisher, "check_login"):
            return self.publisher.check_login()
        return {"provider": self.publisher.name, **self.publisher.health()}

    def dashboard(self) -> dict[str, Any]:
        runs = self.list_runs()["items"]
        latest_run = self.get_run(runs[0]["id"]) if runs else None
        return {
            "app_name": self.settings.app_name,
            "runs": runs[:10],
            "latest_run": latest_run,
            "collector_runs": self.list_collector_runs()["items"][:10],
            "sync_runs": self.list_sync_runs()["items"][:10],
            "drafts": self.list_drafts(),
            "observability": self.observability_summary(),
            "provider_diagnostics": self.provider_diagnostics(),
            "provider_health": self.provider_health(),
            "publish_jobs": self.list_publish_jobs()["items"][:10],
            "sync_records": self.list_sync_records()["items"][:10],
            "audit_logs": self.list_audit_logs()["items"][:10],
            "collector_login": self.check_collector_login(),
            "publish_login": self.check_publish_login(),
            "stage_order": self.stage_order,
        }

    def _prepare_publish_in_session(self, session, draft: ContentDraft) -> dict[str, Any]:
        package = PublishPackagePayload(
            headline=draft.title,
            body=draft.body,
            tags=draft.tags,
            cta=draft.cta,
            content_type=draft.content_type,
            image_prompt=draft.image_prompt,
            target_user=draft.target_user,
            safety_gate="manual_review",
            notes=draft.risk_notes or [],
        )
        if ContentDraftStatus(draft.status) == ContentDraftStatus.APPROVED:
            draft.status = transition_draft_status(ContentDraftStatus(draft.status), "mark_publish_ready").value
        publish_job = PublishJob(draft_id=draft.id, provider=self.publisher.name, mode="prepare", status=PublishJobStatus.PREPARED.value, prepared_payload=asdict(package), preview_payload={}, details={"safety_gate": self.settings.keep_publish_safety_gate})
        session.add(publish_job)
        session.flush()
        self._log(session, "publish.prepare", "publish_job", publish_job.id, {"draft_id": draft.id})
        return {"status": PublishJobStatus.PREPARED.value, "publish_job_id": publish_job.id, "payload": asdict(package)}

    def _preview_publish_in_session(self, session, draft: ContentDraft, prepared: dict[str, Any]) -> dict[str, Any]:
        preview = {"headline": draft.title, "body": draft.body, "tags": draft.tags, "cta": draft.cta, "content_type": draft.content_type, "image_prompt": draft.image_prompt, "target_user": draft.target_user, "safety_gate": "manual_review"}
        publish_job = session.get(PublishJob, prepared["publish_job_id"])
        if publish_job is not None:
            publish_job.status = PublishJobStatus.PREVIEW_READY.value
            publish_job.preview_payload = preview
        self._log(session, "publish.preview", "publish_job", prepared["publish_job_id"], preview)
        return preview

    def _send_publish_in_session(self, session, draft: ContentDraft, prepared: dict[str, Any], dry_run: bool) -> dict[str, Any]:
        execution_publisher = self._execution_publisher()
        publish_job = session.get(PublishJob, prepared["publish_job_id"])
        if publish_job is None:
            raise ValueError("Prepared publish job missing")
        publish_job.status = PublishJobStatus.PUBLISHING.value
        package = PublishPackagePayload(**prepared["payload"])
        result = execution_publisher.publish(package)
        publish_job.status = PublishJobStatus.PUBLISHED.value
        publish_job.provider = result.provider
        publish_job.mode = result.mode if not dry_run else f"{result.mode}:dry-run"
        publish_job.published_url = result.published_url
        if ContentDraftStatus(draft.status) == ContentDraftStatus.PUBLISH_READY:
            draft.status = transition_draft_status(ContentDraftStatus(draft.status), "publish").value
        self._log(session, "publish.send", "publish_job", publish_job.id, {"published_url": publish_job.published_url, "dry_run": dry_run})
        return {"status": publish_job.status, "publish_job": self._serialize_publish_job(publish_job)}

    def _sync_business(self, session, business_type: str, entity_id: str, payload: dict, dry_run: bool, origin: str):
        request_payload = {**payload, "business_type": business_type, "dry_run": dry_run}
        result = self.sync.sync(business_type, request_payload)
        diagnostics = result.get("diagnostics", {})
        sync_record = SyncRecord(entity_type=payload.get("entity_type", business_type), entity_id=entity_id, business_type=business_type, provider=result.get("provider", self.sync.name), target=result["target"], status=result["status"], dry_run=1 if result.get("dry_run") else 0, payload=result.get("payload", request_payload), diagnostics=diagnostics)
        session.add(sync_record)
        session.flush()
        session.add(SyncRun(provider=result.get("provider", self.sync.name), entity_type=payload.get("entity_type", business_type), business_type=business_type, status=result["status"], dry_run=1 if result.get("dry_run") else 0, request_payload=request_payload, result_summary={"target": result["target"], "sync_record_id": sync_record.id}, diagnostics={**diagnostics, "origin": origin}, failure_category=diagnostics.get("reason"), attempt_count=diagnostics.get("attempts", 1)))
        self._log(session, "sync.completed" if result["status"] == SyncStatus.SYNCED.value else "sync.failed", "sync_record", sync_record.id, {"target": sync_record.target, "provider": sync_record.provider, "business_type": business_type})
        return result, sync_record

    def _persist_source_posts(self, session, owner_id: str, posts: list, provider_name: str) -> tuple[int, int]:
        fingerprints = [self._fingerprint_for_post(post) for post in posts]
        existing: set[str] = set()
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
            session.add(SourcePost(run_id=owner_id, provider=provider_name, keyword=post.keyword, title=post.title, content=post.content, likes=post.likes, favorites=post.favorites, comments=post.comments, author=post.author, url=post.url, published_at=post.published_at, content_type=post.content_type, is_ad=1 if post.is_ad else 0, fingerprint=fingerprint, tags=post.tags, raw_data=post.raw_metrics or {}))
        return persisted, duplicates

    @staticmethod
    def _fingerprint_for_post(post) -> str:
        note_id = (post.raw_metrics or {}).get("note_id") if getattr(post, "raw_metrics", None) else None
        return f"xhs::{note_id or post.url}"

    def _normalize_run_payload(self, payload: dict) -> dict[str, Any]:
        return {"keywords": payload.get("keywords") or [], "topic_words": payload.get("topic_words") or payload.get("keywords") or [], "min_likes": int(payload.get("min_likes", 0)), "min_favorites": int(payload.get("min_favorites", 0)), "min_comments": int(payload.get("min_comments", 0)), "auto_publish": bool(payload.get("auto_publish", False)), "dry_run": bool(payload.get("dry_run", True)), "run_mode": payload.get("run_mode", self.settings.default_run_mode), "collection_type": payload.get("collection_type", "search")}

    def _summarize_input(self, stage: str, payload: dict) -> dict[str, Any]:
        if stage == "crawl":
            return {"keywords": payload.get("keywords", []), "topic_words": payload.get("topic_words", []), "thresholds": {"likes": payload.get("min_likes", 0), "favorites": payload.get("min_favorites", 0), "comments": payload.get("min_comments", 0)}}
        return {"run_mode": payload.get("run_mode"), "dry_run": payload.get("dry_run", True)}

    def _provider_name_for_stage(self, stage: str) -> str:
        return {"crawl": self.collector.name, "analyze": self.llm.name, "topic": self.llm.name, "draft": self.llm.name, "image": self.image.name, "review": "system", "publish": self.publisher.name, "sync": self.sync.name}[stage]

    def _stage_rows(self, session, run_id: str):
        return session.scalars(select(WorkflowStageEvent).where(WorkflowStageEvent.run_id == run_id).order_by(WorkflowStageEvent.created_at)).all()

    def _serialize_stage_row(self, row: WorkflowStageEvent) -> dict[str, Any]:
        return {"id": row.id, "stage": row.stage, "status": row.status, "provider": row.provider, "input_summary": row.input_summary, "output_summary": row.output_summary, "error_message": row.error_message, "started_at": row.started_at.isoformat() if row.started_at else None, "finished_at": row.finished_at.isoformat() if row.finished_at else None, "details": row.details}

    def _source_post_rows(self, session, run_id: str):
        return session.scalars(select(SourcePost).where(SourcePost.run_id == run_id).order_by(SourcePost.id)).all()

    def _source_post_payload(self, row: SourcePost):
        from app.domain.models import SourcePostPayload

        return SourcePostPayload(keyword=row.keyword, title=row.title, content=row.content, likes=row.likes, favorites=row.favorites, comments=row.comments, author=row.author, url=row.url, tags=row.tags, published_at=row.published_at, content_type=row.content_type, is_ad=bool(row.is_ad), raw_metrics=row.raw_data)

    def _analysis_payload(self, row: AnalysisReport):
        from app.domain.models import AnalysisPayload

        return AnalysisPayload(summary=row.summary, high_frequency_keywords=row.top_keywords, hot_tags=row.top_tags, title_patterns=row.title_patterns, opening_patterns=row.opening_patterns, content_structure_templates=row.content_structure_templates, user_pain_points=row.user_pain_points, user_delight_points=row.user_delight_points, user_focus_points=row.user_focus_points, engagement_triggers=row.engagement_triggers, applicable_tracks=row.applicable_tracks, viral_hooks=row.viral_hooks, risk_alerts=row.risk_alerts)

    def _topic_payload(self, row: TopicSuggestion):
        from app.domain.models import TopicPayload

        return TopicPayload(title=row.title, reason=row.rationale, target_audience=row.target_audience, reference_hooks=row.reference_hooks, analysis_evidence=row.analysis_evidence, risk_notes=row.risk_notes, recommended_format=row.recommended_format, priority=row.priority, confidence=(row.confidence or 0) / 100, angle=row.angle)

    def _draft_payload(self, row: ContentDraft):
        from app.domain.models import DraftPayload

        return DraftPayload(headline=row.title, alternate_headlines=row.alternate_titles or [], body=row.body, tags=row.tags, cta=row.cta, image_suggestions=row.image_suggestions or [], image_prompt=row.image_prompt, content_type=row.content_type, target_user=row.target_user, tone_style=row.tone_style, risk_notes=row.risk_notes or [], review_notes=[row.review_notes] if row.review_notes else [], revision_notes=row.revision_notes or [])

    def _latest_analysis_row(self, session, run_id: str) -> AnalysisReport:
        row = session.scalars(select(AnalysisReport).where(AnalysisReport.run_id == run_id).order_by(AnalysisReport.id.desc())).first()
        if row is None:
            raise ValueError("Run has no analysis report yet")
        return row

    def _topic_rows(self, session, run_id: str):
        report_ids = [row[0] for row in session.execute(select(AnalysisReport.id).where(AnalysisReport.run_id == run_id)).all()]
        if not report_ids:
            return []
        return session.scalars(select(TopicSuggestion).where(TopicSuggestion.report_id.in_(report_ids)).order_by(TopicSuggestion.id)).all()

    def _draft_rows(self, session, run_id: str):
        topic_ids = [row.id for row in self._topic_rows(session, run_id)]
        if not topic_ids:
            return []
        return session.scalars(select(ContentDraft).where(ContentDraft.topic_id.in_(topic_ids)).order_by(ContentDraft.id)).all()

    def _draft_ids_for_run(self, session, run_id: str | None) -> list[str]:
        if run_id is None:
            return []
        return [row.id for row in self._draft_rows(session, run_id)]

    def _run_id_for_draft(self, session, draft_id: str) -> str | None:
        draft = session.get(ContentDraft, draft_id)
        if draft is None:
            return None
        topic = session.get(TopicSuggestion, draft.topic_id)
        if topic is None:
            return None
        report = session.get(AnalysisReport, topic.report_id)
        return report.run_id if report else None

    def _serialize_source_post(self, row: SourcePost) -> dict[str, Any]:
        return {"id": row.id, "run_id": row.run_id, "provider": row.provider, "keyword": row.keyword, "title": row.title, "content": row.content, "likes": row.likes, "favorites": row.favorites, "comments": row.comments, "author": row.author, "url": row.url, "published_at": row.published_at, "content_type": row.content_type, "tags": row.tags, "raw_data": row.raw_data}

    def _serialize_analysis_row(self, row: AnalysisReport) -> dict[str, Any]:
        return {"id": row.id, "run_id": row.run_id, "summary": row.summary, "high_frequency_keywords": row.top_keywords, "hot_tags": row.top_tags, "title_patterns": row.title_patterns, "opening_patterns": row.opening_patterns, "content_structure_templates": row.content_structure_templates, "user_pain_points": row.user_pain_points, "user_delight_points": row.user_delight_points, "user_focus_points": row.user_focus_points, "engagement_triggers": row.engagement_triggers, "applicable_tracks": row.applicable_tracks, "viral_hooks": row.viral_hooks, "risk_alerts": row.risk_alerts, "top_keywords": row.top_keywords, "top_tags": row.top_tags}

    def _serialize_topic_row(self, row: TopicSuggestion, run_id: str | None = None) -> dict[str, Any]:
        return {"id": row.id, "report_id": row.report_id, "run_id": run_id, "title": row.title, "reason": row.rationale, "target_audience": row.target_audience, "reference_hooks": row.reference_hooks, "analysis_evidence": row.analysis_evidence, "risk_notes": row.risk_notes, "recommended_format": row.recommended_format, "priority": row.priority, "confidence": (row.confidence or 0) / 100, "angle": row.angle, "rationale": row.rationale}

    def _serialize_draft_row(self, row: ContentDraft) -> dict[str, Any]:
        return {"id": row.id, "title": row.title, "headline": row.title, "alternate_headlines": row.alternate_titles, "status": row.status, "body": row.body, "tags": row.tags, "cta": row.cta, "image_prompt": row.image_prompt, "image_suggestions": row.image_suggestions, "content_type": row.content_type, "target_user": row.target_user, "tone_style": row.tone_style, "risk_notes": row.risk_notes, "review_notes": row.review_notes, "revision_notes": row.revision_notes, "revision_count": row.revision_count}

    def _serialize_image_row(self, row: ImageAsset, run_id: str | None = None) -> dict[str, Any]:
        return {"id": row.id, "draft_id": row.draft_id, "run_id": run_id or None, "provider": row.provider, "path": row.path, "status": row.status}

    def _serialize_publish_job(self, row: PublishJob) -> dict[str, Any]:
        return {"id": row.id, "draft_id": row.draft_id, "provider": row.provider, "mode": row.mode, "status": row.status, "published_url": row.published_url, "preview_payload": row.preview_payload, "prepared_payload": row.prepared_payload}

    def _serialize_sync_record(self, row: SyncRecord) -> dict[str, Any]:
        return {"id": row.id, "entity_type": row.entity_type, "entity_id": row.entity_id, "business_type": row.business_type, "provider": row.provider, "target": row.target, "status": row.status, "dry_run": bool(row.dry_run), "diagnostics": row.diagnostics}

    def _serialize_sync_run(self, row: SyncRun) -> dict[str, Any]:
        return {"id": row.id, "provider": row.provider, "entity_type": row.entity_type, "business_type": row.business_type, "status": row.status, "dry_run": bool(row.dry_run), "request_payload": row.request_payload, "result_summary": row.result_summary, "diagnostics": row.diagnostics}

    def _sync_crawled_payload(self, session, run_id: str) -> dict[str, Any]:
        posts = self._source_post_rows(session, run_id)
        analysis = self._latest_analysis_row(session, run_id)
        return {"entity_type": "workflow_run", "run_id": run_id, "source_post_count": len(posts), "analysis_summary": analysis.summary, "candidate_urls": [post.url for post in posts[:5]]}

    def _sync_generated_payload(self, session, run_id: str) -> dict[str, Any]:
        topics = self._topic_rows(session, run_id)
        drafts = self._draft_rows(session, run_id)
        draft_ids = [draft.id for draft in drafts]
        publish_jobs = session.scalars(select(PublishJob).where(PublishJob.draft_id.in_(draft_ids))).all() if draft_ids else []
        return {"entity_type": "workflow_run", "run_id": run_id, "topic_titles": [topic.title for topic in topics[:5]], "draft_titles": [draft.title for draft in drafts[:5]], "review_statuses": {draft.id: draft.status for draft in drafts}, "published_urls": [job.published_url for job in publish_jobs if job.published_url]}

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
    def _provider_summary(configured: str, provider, extra: dict) -> dict:
        payload = {"configured": configured, "active": provider.name, **extra}
        if hasattr(provider, "diagnostics"):
            payload.update(provider.diagnostics())
        return payload

    @staticmethod
    def _log(session, event_type: str, entity_type: str, entity_id: str, details: dict) -> None:
        session.add(AuditLog(event_type=event_type, entity_type=entity_type, entity_id=entity_id, details=details))

    def _execution_publisher(self):
        if getattr(self.publisher, "name", "").endswith("live-publisher") and not self.settings.allow_live_publish:
            if "browser" in self.publisher.name:
                return XiaohongshuBrowserSafeStubProvider()
            return XiaohongshuAPISafeStubProvider()
        return self.publisher





