from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.application.factory import get_pipeline_service
from app.schemas import DraftReviewRequest, PipelineRunRequest

router = APIRouter(prefix="/api")


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/pipeline-runs", status_code=202)
def create_pipeline_run(request: PipelineRunRequest) -> dict:
    return get_pipeline_service().create_run(request.model_dump())


@router.get("/pipeline-runs")
def list_pipeline_runs() -> dict:
    return get_pipeline_service().list_runs()


@router.get("/pipeline-runs/{run_id}")
def get_pipeline_run(run_id: str) -> dict:
    try:
        return get_pipeline_service().get_run(run_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/pipeline-runs/{run_id}/diagnostics")
def get_pipeline_run_diagnostics(run_id: str) -> dict:
    return get_pipeline_service().get_run_diagnostics(run_id)


@router.get("/drafts")
def list_drafts() -> dict:
    return {"items": get_pipeline_service().list_drafts()}


@router.get("/source-posts")
def list_source_posts(run_id: str | None = Query(default=None)) -> dict:
    return get_pipeline_service().list_source_posts(run_id)


@router.get("/source-posts/{source_post_id}")
def get_source_post(source_post_id: str) -> dict:
    try:
        return get_pipeline_service().get_source_post(source_post_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/analysis-reports")
def list_analysis_reports(run_id: str | None = Query(default=None)) -> dict:
    return get_pipeline_service().list_analysis_reports(run_id)


@router.get("/analysis-reports/{report_id}")
def get_analysis_report(report_id: str) -> dict:
    try:
        return get_pipeline_service().get_analysis_report(report_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/topic-suggestions")
def list_topic_suggestions(run_id: str | None = Query(default=None)) -> dict:
    return get_pipeline_service().list_topic_suggestions(run_id)


@router.get("/topic-suggestions/{topic_id}")
def get_topic_suggestion(topic_id: str) -> dict:
    try:
        return get_pipeline_service().get_topic_suggestion(topic_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/image-assets")
def list_image_assets(run_id: str | None = Query(default=None)) -> dict:
    return get_pipeline_service().list_image_assets(run_id)


@router.get("/image-assets/{image_id}")
def get_image_asset(image_id: str) -> dict:
    try:
        return get_pipeline_service().get_image_asset(image_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/drafts/{draft_id}/approve")
def approve_draft(draft_id: str, request: DraftReviewRequest) -> dict:
    try:
        return get_pipeline_service().approve_draft(draft_id, request.review_notes)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/drafts/{draft_id}/reject")
def reject_draft(draft_id: str, request: DraftReviewRequest) -> dict:
    try:
        return get_pipeline_service().reject_draft(draft_id, request.review_notes)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/drafts/{draft_id}/regenerate")
def regenerate_draft(draft_id: str, request: DraftReviewRequest) -> dict:
    try:
        return get_pipeline_service().regenerate_draft(draft_id, request.review_notes)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/drafts/{draft_id}/publish")
def publish_draft(draft_id: str) -> dict:
    try:
        return get_pipeline_service().publish_draft(draft_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/audit-logs")
def audit_logs() -> dict:
    return get_pipeline_service().list_audit_logs()


@router.get("/sync-records")
def sync_records() -> dict:
    return get_pipeline_service().list_sync_records()


@router.get("/publish-jobs")
def publish_jobs() -> dict:
    return get_pipeline_service().list_publish_jobs()


@router.get("/observability/summary")
def observability_summary() -> dict:
    return get_pipeline_service().observability_summary()


@router.get("/providers/diagnostics")
def provider_diagnostics() -> dict:
    return get_pipeline_service().provider_diagnostics()


@router.get("/providers/health")
def provider_health() -> dict:
    return get_pipeline_service().provider_health()


@router.get("/external-workers/jobs/{job_id}")
def inspect_external_worker_job(job_id: str) -> dict:
    return get_pipeline_service().inspect_external_worker_job(job_id)


@router.post("/external-workers/jobs/{job_id}/cancel")
def cancel_external_worker_job(job_id: str) -> dict:
    return get_pipeline_service().cancel_external_worker_job(job_id)


@router.post("/external-workers/jobs/{job_id}/requeue")
def requeue_external_worker_job(job_id: str) -> dict:
    return get_pipeline_service().requeue_external_worker_job(job_id)
