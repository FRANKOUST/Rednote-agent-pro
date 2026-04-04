from __future__ import annotations

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.config import get_settings
from app.core.middleware import operator_auth_middleware, request_context_middleware
from app.db.session import init_db
from app.interfaces.mcp.routes import router as mcp_router
from app.interfaces.rest.routes import router as rest_router
from app.interfaces.web.routes import router as web_router


def create_app() -> FastAPI:
    settings = get_settings()
    init_db()
    app = FastAPI(title=settings.app_name)
    app.middleware("http")(request_context_middleware)
    app.middleware("http")(operator_auth_middleware)
    app.include_router(rest_router)
    app.include_router(mcp_router)
    app.include_router(web_router)
    app.mount("/static", StaticFiles(directory="static"), name="static")
    return app


app = create_app()
