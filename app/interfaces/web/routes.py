from __future__ import annotations

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.application.factory import get_pipeline_service
from app.core.config import get_settings

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request) -> HTMLResponse:
    context = get_pipeline_service().dashboard()
    context["request"] = request
    return templates.TemplateResponse(request, "index.html", context)


@router.get("/console/providers", response_class=HTMLResponse)
def providers_page(request: Request) -> HTMLResponse:
    service = get_pipeline_service()
    return templates.TemplateResponse(
        request,
        "providers.html",
        {"request": request, "app_name": get_settings().app_name, "diagnostics": service.provider_diagnostics(), "health": service.provider_health()},
    )


@router.get("/console/entities", response_class=HTMLResponse)
def entities_view(request: Request) -> HTMLResponse:
    service = get_pipeline_service()
    context = {
        "request": request,
        "app_name": get_settings().app_name,
        "source_posts": service.list_source_posts()["items"][:20],
        "analysis_reports": service.list_analysis_reports()["items"][:20],
        "topic_suggestions": service.list_topic_suggestions()["items"][:20],
        "image_assets": service.list_image_assets()["items"][:20],
    }
    return templates.TemplateResponse(request, "entities.html", context)


@router.get("/console/source-posts/{source_post_id}", response_class=HTMLResponse)
def source_post_detail(request: Request, source_post_id: str) -> HTMLResponse:
    return templates.TemplateResponse(request, "entity_detail.html", {"request": request, "app_name": get_settings().app_name, "title": "Source Post", "item": get_pipeline_service().get_source_post(source_post_id)})


@router.get("/console/analysis-reports/{report_id}", response_class=HTMLResponse)
def analysis_report_detail(request: Request, report_id: str) -> HTMLResponse:
    return templates.TemplateResponse(request, "entity_detail.html", {"request": request, "app_name": get_settings().app_name, "title": "Analysis Report", "item": get_pipeline_service().get_analysis_report(report_id)})


@router.get("/console/topic-suggestions/{topic_id}", response_class=HTMLResponse)
def topic_detail(request: Request, topic_id: str) -> HTMLResponse:
    return templates.TemplateResponse(request, "entity_detail.html", {"request": request, "app_name": get_settings().app_name, "title": "Topic Suggestion", "item": get_pipeline_service().get_topic_suggestion(topic_id)})


@router.get("/console/image-assets/{image_id}", response_class=HTMLResponse)
def image_asset_detail(request: Request, image_id: str) -> HTMLResponse:
    return templates.TemplateResponse(request, "entity_detail.html", {"request": request, "app_name": get_settings().app_name, "title": "Image Asset", "item": get_pipeline_service().get_image_asset(image_id)})


@router.get("/console/runs/{run_id}", response_class=HTMLResponse)
def run_detail(request: Request, run_id: str) -> HTMLResponse:
    return templates.TemplateResponse(request, "entity_detail.html", {"request": request, "app_name": get_settings().app_name, "title": "Workflow Run", "item": get_pipeline_service().get_run(run_id)})


@router.get("/console/runs/{run_id}/diagnostics", response_class=HTMLResponse)
def run_diagnostics(request: Request, run_id: str) -> HTMLResponse:
    return templates.TemplateResponse(request, "diagnostics.html", {"request": request, "app_name": get_settings().app_name, "title": "Diagnostics", "items": get_pipeline_service().get_run_diagnostics(run_id)["items"]})


@router.get("/console/collector-runs", response_class=HTMLResponse)
def collector_runs_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "run_list.html", {"request": request, "app_name": get_settings().app_name, "title": "Collector Runs", "items": get_pipeline_service().list_collector_runs()["items"]})


@router.get("/console/sync-runs", response_class=HTMLResponse)
def sync_runs_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "run_list.html", {"request": request, "app_name": get_settings().app_name, "title": "Sync Runs", "items": get_pipeline_service().list_sync_runs()["items"]})


@router.get("/console/collector-runs/{collector_run_id}", response_class=HTMLResponse)
def collector_run_detail(request: Request, collector_run_id: str) -> HTMLResponse:
    return templates.TemplateResponse(request, "entity_detail.html", {"request": request, "app_name": get_settings().app_name, "title": "Collector Run", "item": get_pipeline_service().get_collector_run(collector_run_id)})


@router.get("/console/sync-runs/{sync_run_id}", response_class=HTMLResponse)
def sync_run_detail(request: Request, sync_run_id: str) -> HTMLResponse:
    return templates.TemplateResponse(request, "entity_detail.html", {"request": request, "app_name": get_settings().app_name, "title": "Sync Run", "item": get_pipeline_service().get_sync_run(sync_run_id)})


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "login.html", {"request": request, "app_name": get_settings().app_name})


@router.post("/login")
def login(operator_key: str = Form(...)) -> RedirectResponse:
    settings = get_settings()
    if not settings.operator_api_key or operator_key != settings.operator_api_key:
        return RedirectResponse("/login", status_code=303)
    response = RedirectResponse("/", status_code=303)
    response.set_cookie(settings.operator_session_cookie_name, settings.operator_api_key, httponly=True, samesite="lax")
    return response


@router.post("/console/pipeline-runs")
def start_pipeline(keywords: str = Form(...)) -> RedirectResponse:
    keyword_list = [item.strip() for item in keywords.split(",") if item.strip()]
    get_pipeline_service().create_run({"keywords": keyword_list, "min_likes": 0, "min_favorites": 0, "min_comments": 0, "auto_publish": False, "dry_run": True})
    return RedirectResponse("/", status_code=303)


@router.post("/console/collector-runs/search")
def start_search_from_console(keywords: str = Form(...)) -> RedirectResponse:
    keyword_list = [item.strip() for item in keywords.split(",") if item.strip()]
    get_pipeline_service().start_collector_run({"keywords": keyword_list, "dry_run": True}, "search")
    return RedirectResponse("/console/collector-runs", status_code=303)


@router.post("/console/collector-runs/detail")
def start_detail_from_console(note_ids: str = Form(...)) -> RedirectResponse:
    note_id_list = [item.strip() for item in note_ids.split(",") if item.strip()]
    get_pipeline_service().start_collector_run({"note_ids": note_id_list, "dry_run": True}, "detail")
    return RedirectResponse("/console/collector-runs", status_code=303)


@router.post("/console/sync-runs")
def start_sync_from_console(entity_type: str = Form(...), payload_json: str = Form(...)) -> RedirectResponse:
    import json

    payload = json.loads(payload_json)
    get_pipeline_service().start_sync_run(entity_type, payload, True)
    return RedirectResponse("/console/sync-runs", status_code=303)


@router.post("/console/drafts/{draft_id}/approve")
def approve_from_console(draft_id: str) -> RedirectResponse:
    get_pipeline_service().approve_draft(draft_id, "approved from console")
    return RedirectResponse("/", status_code=303)


@router.post("/console/drafts/{draft_id}/publish")
def publish_from_console(draft_id: str) -> RedirectResponse:
    get_pipeline_service().publish_draft(draft_id)
    return RedirectResponse("/", status_code=303)
