from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.application.factory import get_pipeline_service
from app.schemas import CollectorRunRequest, DraftReviewRequest, PipelineRunRequest, PublishSendRequest, StageRunRequest, SyncActionRequest, SyncRunRequest

router = APIRouter(prefix="/api")


def _not_found(exc: ValueError):
    raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/content-pipeline/runs", status_code=202)
def create_content_pipeline_run(request: PipelineRunRequest) -> dict:
    return get_pipeline_service().create_run(request.model_dump())


@router.get("/content-pipeline/runs")
def list_content_pipeline_runs() -> dict:
    return get_pipeline_service().list_runs()


@router.get("/content-pipeline/runs/{run_id}")
def get_content_pipeline_run(run_id: str) -> dict:
    try:
        return get_pipeline_service().get_run(run_id)
    except ValueError as exc:
        _not_found(exc)


@router.post("/content-pipeline/runs/{run_id}/stages/{stage}")
def run_content_pipeline_stage(run_id: str, stage: str, request: StageRunRequest | None = None) -> dict:
    try:
        return get_pipeline_service().run_stage(run_id, stage, (request.model_dump() if request else {}).get("overrides", {}))
    except ValueError as exc:
        _not_found(exc)


@router.get("/content-pipeline/runs/{run_id}/diagnostics")
def get_content_pipeline_run_diagnostics(run_id: str) -> dict:
    return get_pipeline_service().get_run_diagnostics(run_id)


@router.post("/content-pipeline/runs/{run_id}/sync/crawled")
def sync_crawled(run_id: str, request: SyncActionRequest) -> dict:
    return get_pipeline_service().sync_crawled(run_id, request.dry_run)


@router.post("/content-pipeline/runs/{run_id}/sync/generated")
def sync_generated(run_id: str, request: SyncActionRequest) -> dict:
    return get_pipeline_service().sync_generated(run_id, request.dry_run)


@router.post("/content-drafts/{draft_id}/review/approve")
def approve_draft(draft_id: str, request: DraftReviewRequest) -> dict:
    try:
        return get_pipeline_service().approve_draft(draft_id, request.review_notes)
    except ValueError as exc:
        _not_found(exc)


@router.post("/content-drafts/{draft_id}/review/reject")
def reject_draft(draft_id: str, request: DraftReviewRequest) -> dict:
    try:
        return get_pipeline_service().reject_draft(draft_id, request.review_notes)
    except ValueError as exc:
        _not_found(exc)


@router.post("/content-drafts/{draft_id}/review/revise")
def revise_draft(draft_id: str, request: DraftReviewRequest) -> dict:
    try:
        return get_pipeline_service().regenerate_draft(draft_id, request.review_notes)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/content-drafts/{draft_id}/publish/prepare")
def prepare_publish(draft_id: str) -> dict:
    try:
        return get_pipeline_service().prepare_publish(draft_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/content-drafts/{draft_id}/publish/preview")
def preview_publish(draft_id: str) -> dict:
    try:
        return get_pipeline_service().preview_publish(draft_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/content-drafts/{draft_id}/publish/send")
def send_publish(draft_id: str, request: PublishSendRequest) -> dict:
    try:
        return get_pipeline_service().send_publish(draft_id, request.dry_run)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/providers/checks/collector-login")
def check_collector_login() -> dict:
    return get_pipeline_service().check_collector_login()


@router.get("/providers/checks/publish-login")
def check_publish_login() -> dict:
    return get_pipeline_service().check_publish_login()


# legacy aliases
@router.post("/pipeline-runs", status_code=202)
def create_pipeline_run(request: PipelineRunRequest) -> dict:
    return create_content_pipeline_run(request)


@router.get("/pipeline-runs")
def list_pipeline_runs() -> dict:
    return list_content_pipeline_runs()


@router.get("/pipeline-runs/{run_id}")
def get_pipeline_run(run_id: str) -> dict:
    return get_content_pipeline_run(run_id)


@router.get("/pipeline-runs/{run_id}/diagnostics")
def get_pipeline_run_diagnostics(run_id: str) -> dict:
    return get_content_pipeline_run_diagnostics(run_id)


@router.post("/collector-runs/search", status_code=202)
def start_search_collector_run(request: CollectorRunRequest) -> dict:
    return get_pipeline_service().start_collector_run(request.model_dump(), "search")


@router.post("/collector-runs/detail", status_code=202)
def start_detail_collector_run(request: CollectorRunRequest) -> dict:
    return get_pipeline_service().start_collector_run(request.model_dump(), "detail")


@router.get("/collector-runs")
def list_collector_runs() -> dict:
    return get_pipeline_service().list_collector_runs()


@router.get("/collector-runs/{collector_run_id}")
def get_collector_run(collector_run_id: str) -> dict:
    try:
        return get_pipeline_service().get_collector_run(collector_run_id)
    except ValueError as exc:
        _not_found(exc)


@router.post("/sync-runs", status_code=202)
def start_sync_run(request: SyncRunRequest) -> dict:
    return get_pipeline_service().start_sync_run(request.entity_type, request.payload, request.dry_run)


@router.get("/sync-runs")
def list_sync_runs() -> dict:
    return get_pipeline_service().list_sync_runs()


@router.get("/sync-runs/{sync_run_id}")
def get_sync_run(sync_run_id: str) -> dict:
    try:
        return get_pipeline_service().get_sync_run(sync_run_id)
    except ValueError as exc:
        _not_found(exc)


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
        _not_found(exc)


@router.get("/analysis-reports")
def list_analysis_reports(run_id: str | None = Query(default=None)) -> dict:
    return get_pipeline_service().list_analysis_reports(run_id)


@router.get("/analysis-reports/{report_id}")
def get_analysis_report(report_id: str) -> dict:
    try:
        return get_pipeline_service().get_analysis_report(report_id)
    except ValueError as exc:
        _not_found(exc)


@router.get("/topic-suggestions")
def list_topic_suggestions(run_id: str | None = Query(default=None)) -> dict:
    return get_pipeline_service().list_topic_suggestions(run_id)


@router.get("/topic-suggestions/{topic_id}")
def get_topic_suggestion(topic_id: str) -> dict:
    try:
        return get_pipeline_service().get_topic_suggestion(topic_id)
    except ValueError as exc:
        _not_found(exc)


@router.get("/image-assets")
def list_image_assets(run_id: str | None = Query(default=None)) -> dict:
    return get_pipeline_service().list_image_assets(run_id)


@router.get("/image-assets/{image_id}")
def get_image_asset(image_id: str) -> dict:
    try:
        return get_pipeline_service().get_image_asset(image_id)
    except ValueError as exc:
        _not_found(exc)


@router.post("/drafts/{draft_id}/approve")
def approve_draft_legacy(draft_id: str, request: DraftReviewRequest) -> dict:
    return approve_draft(draft_id, request)


@router.post("/drafts/{draft_id}/reject")
def reject_draft_legacy(draft_id: str, request: DraftReviewRequest) -> dict:
    return reject_draft(draft_id, request)


@router.post("/drafts/{draft_id}/regenerate")
def regenerate_draft_legacy(draft_id: str, request: DraftReviewRequest) -> dict:
    return revise_draft(draft_id, request)


@router.post("/drafts/{draft_id}/publish")
def publish_draft_legacy(draft_id: str) -> dict:
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


@router.get("/providers/status")
def provider_status() -> dict:
    service = get_pipeline_service()
    return {"diagnostics": service.provider_diagnostics(), "health": service.provider_health()}


@router.get("/external-workers/jobs/{job_id}")
def inspect_external_worker_job(job_id: str) -> dict:
    return get_pipeline_service().inspect_external_worker_job(job_id)


@router.post("/external-workers/jobs/{job_id}/cancel")
def cancel_external_worker_job(job_id: str) -> dict:
    return get_pipeline_service().cancel_external_worker_job(job_id)


@router.post("/external-workers/jobs/{job_id}/requeue")
def requeue_external_worker_job(job_id: str) -> dict:
    return get_pipeline_service().requeue_external_worker_job(job_id)

