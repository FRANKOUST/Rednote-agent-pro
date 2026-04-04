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
    context = {
        "request": request,
        "app_name": get_settings().app_name,
        "title": "Source Post",
        "item": get_pipeline_service().get_source_post(source_post_id),
    }
    return templates.TemplateResponse(request, "entity_detail.html", context)


@router.get("/console/analysis-reports/{report_id}", response_class=HTMLResponse)
def analysis_report_detail(request: Request, report_id: str) -> HTMLResponse:
    context = {
        "request": request,
        "app_name": get_settings().app_name,
        "title": "Analysis Report",
        "item": get_pipeline_service().get_analysis_report(report_id),
    }
    return templates.TemplateResponse(request, "entity_detail.html", context)


@router.get("/console/topic-suggestions/{topic_id}", response_class=HTMLResponse)
def topic_detail(request: Request, topic_id: str) -> HTMLResponse:
    context = {
        "request": request,
        "app_name": get_settings().app_name,
        "title": "Topic Suggestion",
        "item": get_pipeline_service().get_topic_suggestion(topic_id),
    }
    return templates.TemplateResponse(request, "entity_detail.html", context)


@router.get("/console/image-assets/{image_id}", response_class=HTMLResponse)
def image_asset_detail(request: Request, image_id: str) -> HTMLResponse:
    context = {
        "request": request,
        "app_name": get_settings().app_name,
        "title": "Image Asset",
        "item": get_pipeline_service().get_image_asset(image_id),
    }
    return templates.TemplateResponse(request, "entity_detail.html", context)


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
    get_pipeline_service().create_run({"keywords": keyword_list, "min_likes": 0, "min_favorites": 0, "min_comments": 0, "auto_publish": False})
    return RedirectResponse("/", status_code=303)


@router.post("/console/drafts/{draft_id}/approve")
def approve_from_console(draft_id: str) -> RedirectResponse:
    get_pipeline_service().approve_draft(draft_id, "approved from console")
    return RedirectResponse("/", status_code=303)


@router.post("/console/drafts/{draft_id}/publish")
def publish_from_console(draft_id: str) -> RedirectResponse:
    get_pipeline_service().publish_draft(draft_id)
    return RedirectResponse("/", status_code=303)
