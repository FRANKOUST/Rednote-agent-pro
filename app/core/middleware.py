from __future__ import annotations

import logging
from time import perf_counter
from uuid import uuid4

from fastapi import Request
from fastapi.responses import JSONResponse, RedirectResponse

from app.core.config import get_settings

logger = logging.getLogger("xhs_platform.requests")


async def request_context_middleware(request: Request, call_next):
    settings = get_settings()
    request_id = uuid4().hex
    started = perf_counter()
    response = await call_next(request)
    duration_ms = round((perf_counter() - started) * 1000, 2)
    response.headers[settings.request_id_header_name] = request_id
    logger.info(
        "request_complete",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        },
    )
    return response


async def operator_auth_middleware(request: Request, call_next):
    settings = get_settings()
    if not settings.auth_enabled:
        return await call_next(request)

    path = request.url.path
    if path == "/api/health" or path.startswith("/static") or path == "/login":
        return await call_next(request)

    def resolve_role(key: str) -> str | None:
        if key and settings.admin_api_key and key == settings.admin_api_key:
            return "admin"
        if key and settings.reviewer_api_key and key == settings.reviewer_api_key:
            return "reviewer"
        if key and settings.operator_api_key and key == settings.operator_api_key:
            return "operator"
        if key and settings.viewer_api_key and key == settings.viewer_api_key:
            return "viewer"
        if key and settings.operator_api_key and key == settings.operator_api_key:
            return "operator"
        return None

    def is_read_only(method: str) -> bool:
        return method.upper() == "GET"

    def allowed(role: str, method: str, req_path: str) -> bool:
        if role == "admin":
            return True
        if role == "viewer":
            return is_read_only(method)
        if role == "reviewer":
            if is_read_only(method):
                return True
            return "/approve" in req_path or "/reject" in req_path
        if role == "operator":
            if is_read_only(method):
                return True
            return "/publish" not in req_path
        return False

    if path.startswith("/api") or path.startswith("/mcp"):
        provided = request.headers.get("X-Operator-Key", "")
        role = resolve_role(provided)
        if role is None:
            return JSONResponse(status_code=401, content={"detail": "Unauthorized operator access"})
        request.state.operator_role = role
        if not allowed(role, request.method, path):
            return JSONResponse(status_code=403, content={"detail": "Forbidden for operator role"})

    if path == "/" or path.startswith("/console"):
        provided = request.headers.get("X-Operator-Key", "")
        session_cookie = request.cookies.get(settings.operator_session_cookie_name, "")
        role = resolve_role(provided) or resolve_role(session_cookie)
        if role is not None:
            request.state.operator_role = role
            return await call_next(request)
        return RedirectResponse(url="/login", status_code=303)

    return await call_next(request)
