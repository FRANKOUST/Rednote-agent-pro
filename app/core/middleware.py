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

    if path.startswith("/api") or path.startswith("/mcp"):
        provided = request.headers.get("X-Operator-Key", "")
        if not settings.operator_api_key or provided != settings.operator_api_key:
            return JSONResponse(status_code=401, content={"detail": "Unauthorized operator access"})

    if path == "/" or path.startswith("/console"):
        provided = request.headers.get("X-Operator-Key", "")
        session_cookie = request.cookies.get(settings.operator_session_cookie_name, "")
        if provided == settings.operator_api_key or session_cookie == settings.operator_api_key:
            return await call_next(request)
        return RedirectResponse(url="/login", status_code=303)

    return await call_next(request)
