# Bootstrap Xiaohongshu Content Platform Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the phase-one foundation for a FastAPI-based Xiaohongshu content platform with shared REST, MCP, and Web UI entrypoints, queue-backed workflow execution, persistence wiring, and provider contracts.

**Architecture:** Use a modular monolith with thin interface layers over shared application services. Persist workflow and job state in PostgreSQL, run long-lived work through Celery, and isolate all external systems behind provider interfaces so later crawler, generation, publish, and Feishu features can be added without rewriting the core.

**Tech Stack:** Python 3.12, FastAPI, Pydantic Settings, SQLAlchemy 2.x, Alembic, Celery, Redis, PostgreSQL, Jinja2, Playwright, pytest

---

## File Structure

- `pyproject.toml`: project metadata and dependencies
- `app/main.py`: FastAPI app factory and startup wiring
- `app/core/config.py`: settings model and environment loading
- `app/interfaces/rest/router.py`: REST router registration
- `app/interfaces/rest/routes/health.py`: health endpoint
- `app/interfaces/web/router.py`: web route registration
- `app/interfaces/mcp/tools.py`: MCP tool surface bootstrap
- `app/application/workflows/service.py`: shared workflow dispatch and status lookup
- `app/domain/models.py`: shared enums and workflow state models
- `app/domain/providers.py`: provider interfaces and normalized result types
- `app/db/base.py`: SQLAlchemy declarative base and metadata conventions
- `app/db/session.py`: engine and session factory
- `app/db/models.py`: persisted job and checkpoint records
- `app/jobs/celery_app.py`: Celery configuration
- `app/jobs/tasks.py`: async workflow task envelope
- `templates/index.html`: minimal operator shell
- `tests/unit/test_state_models.py`: state and contract tests
- `tests/integration/test_health.py`: application startup test
- `tests/integration/test_job_dispatch.py`: queue and service integration test

## Future Change Hand-off

This plan covers only the `bootstrap-xiaohongshu-content-platform` change. Follow-on OpenSpec changes should implement crawler, analysis, draft generation, publish flow, Feishu sync, and richer UI capabilities on top of this foundation.

### Task 1: Bootstrap the backend runtime

**Files:**
- Create: `pyproject.toml`
- Create: `app/main.py`
- Create: `app/core/config.py`
- Create: `app/interfaces/rest/router.py`
- Create: `app/interfaces/rest/routes/health.py`
- Test: `tests/integration/test_health.py`

- [ ] **Step 1: Write the failing startup test**

```python
# tests/integration/test_health.py
from fastapi.testclient import TestClient

from app.main import create_app


def test_health_endpoint_returns_ok() -> None:
    client = TestClient(create_app())

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/integration/test_health.py -q`
Expected: FAIL with `ModuleNotFoundError` or `ImportError` because `app.main` does not exist yet.

- [ ] **Step 3: Write the minimal runtime implementation**

```toml
# pyproject.toml
[project]
name = "xiaohongshu-content-platform"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
  "alembic>=1.14.0",
  "celery[redis]>=5.4.0",
  "fastapi>=0.115.0",
  "jinja2>=3.1.4",
  "playwright>=1.49.0",
  "psycopg[binary]>=3.2.0",
  "pydantic-settings>=2.6.0",
  "sqlalchemy>=2.0.36",
  "uvicorn[standard]>=0.32.0",
]

[project.optional-dependencies]
dev = [
  "httpx>=0.27.2",
  "pytest>=8.3.3",
  "pytest-asyncio>=0.24.0",
]
```

```python
# app/core/config.py
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Xiaohongshu Content Platform"
    environment: str = "development"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="XHS_")


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

```python
# app/interfaces/rest/routes/health.py
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
```

```python
# app/interfaces/rest/router.py
from fastapi import APIRouter

from app.interfaces.rest.routes.health import router as health_router


def build_rest_router() -> APIRouter:
    router = APIRouter(prefix="/api")
    router.include_router(health_router)
    return router
```

```python
# app/main.py
from fastapi import FastAPI

from app.core.config import get_settings
from app.interfaces.rest.router import build_rest_router


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name)
    app.include_router(build_rest_router())
    return app


app = create_app()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/integration/test_health.py -q`
Expected: PASS with `1 passed`.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml app tests/integration/test_health.py
git commit -m "feat: bootstrap fastapi runtime"
```

### Task 2: Add persistence and migration foundations

**Files:**
- Create: `app/db/base.py`
- Create: `app/db/session.py`
- Create: `app/db/models.py`
- Create: `alembic.ini`
- Create: `alembic/env.py`
- Test: `tests/unit/test_state_models.py`

- [ ] **Step 1: Write the failing workflow model test**

```python
# tests/unit/test_state_models.py
from app.domain.models import JobStatus


def test_job_status_terminal_states() -> None:
    assert JobStatus.PUBLISHED.is_terminal is True
    assert JobStatus.FAILED.is_terminal is True
    assert JobStatus.QUEUED.is_terminal is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_state_models.py -q`
Expected: FAIL because `app.domain.models` does not exist yet.

- [ ] **Step 3: Add database and state-model foundation**

```python
# app/db/base.py
from sqlalchemy.orm import DeclarativeBase, declared_attr


class Base(DeclarativeBase):
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
```

```python
# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings


settings = get_settings()
database_url = getattr(settings, "database_url", "postgresql+psycopg://postgres:postgres@localhost:5432/xhs_platform")
engine = create_engine(database_url, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
```

```python
# app/domain/models.py
from enum import StrEnum


class JobStatus(StrEnum):
    QUEUED = "queued"
    PREPARING = "preparing"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"

    @property
    def is_terminal(self) -> bool:
        return self in {self.PUBLISHED, self.FAILED, self.CANCELLED}
```

```python
# app/db/models.py
from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class WorkflowJobRecord(Base):
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    workflow_type: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    checkpoint: Mapped[dict] = mapped_column(JSON, default=dict)
```

```python
# alembic/env.py
from app.db.base import Base
from app.db.models import WorkflowJobRecord  # noqa: F401

target_metadata = Base.metadata
```

- [ ] **Step 4: Run tests to verify the model layer works**

Run: `pytest tests/unit/test_state_models.py -q`
Expected: PASS with `1 passed`.

- [ ] **Step 5: Commit**

```bash
git add app/domain/models.py app/db alembic.ini alembic tests/unit/test_state_models.py
git commit -m "feat: add persistence and state foundations"
```

### Task 3: Introduce queue-backed workflow execution

**Files:**
- Create: `app/jobs/celery_app.py`
- Create: `app/jobs/tasks.py`
- Create: `app/application/workflows/service.py`
- Modify: `app/domain/models.py`
- Test: `tests/integration/test_job_dispatch.py`

- [ ] **Step 1: Write the failing dispatch test**

```python
# tests/integration/test_job_dispatch.py
from app.application.workflows.service import WorkflowService


def test_dispatch_returns_job_reference() -> None:
    service = WorkflowService()

    result = service.dispatch("bootstrap-check", {"source": "test"})

    assert result.workflow_type == "bootstrap-check"
    assert result.status == "queued"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/integration/test_job_dispatch.py -q`
Expected: FAIL because `WorkflowService` does not exist yet.

- [ ] **Step 3: Add minimal queue and workflow service implementation**

```python
# app/jobs/celery_app.py
from celery import Celery


celery_app = Celery(
    "xhs_platform",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
)
```

```python
# app/domain/models.py
from dataclasses import dataclass
from enum import StrEnum


@dataclass(slots=True)
class WorkflowDispatchResult:
    job_id: str
    workflow_type: str
    status: str
```

```python
# app/jobs/tasks.py
from app.jobs.celery_app import celery_app


@celery_app.task(name="workflows.run")
def run_workflow(job_id: str, workflow_type: str, payload: dict) -> dict:
    return {"job_id": job_id, "workflow_type": workflow_type, "payload": payload}
```

```python
# app/application/workflows/service.py
from uuid import uuid4

from app.domain.models import WorkflowDispatchResult
from app.jobs.tasks import run_workflow


class WorkflowService:
    def dispatch(self, workflow_type: str, payload: dict) -> WorkflowDispatchResult:
        job_id = uuid4().hex
        run_workflow.delay(job_id, workflow_type, payload)
        return WorkflowDispatchResult(job_id=job_id, workflow_type=workflow_type, status="queued")
```

- [ ] **Step 4: Run test to verify dispatch works**

Run: `pytest tests/integration/test_job_dispatch.py -q`
Expected: PASS with `1 passed`.

- [ ] **Step 5: Commit**

```bash
git add app/jobs app/application/workflows/service.py app/domain/models.py tests/integration/test_job_dispatch.py
git commit -m "feat: add async workflow dispatch foundation"
```

### Task 4: Define provider contracts and normalized result models

**Files:**
- Modify: `app/domain/models.py`
- Create: `app/domain/providers.py`
- Test: `tests/unit/test_provider_contracts.py`

- [ ] **Step 1: Write the failing provider contract test**

```python
# tests/unit/test_provider_contracts.py
from app.domain.providers import GenerationResult, ProviderError


def test_provider_error_contains_retryability() -> None:
    error = ProviderError(code="timeout", message="timed out", retryable=True)

    assert error.code == "timeout"
    assert error.retryable is True


def test_generation_result_keeps_normalized_fields() -> None:
    result = GenerationResult(title="A", body="B", tags=["#xhs"])

    assert result.title == "A"
    assert result.tags == ["#xhs"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_provider_contracts.py -q`
Expected: FAIL because `app.domain.providers` does not exist yet.

- [ ] **Step 3: Add the provider contracts**

```python
# app/domain/providers.py
from dataclasses import dataclass, field
from typing import Protocol


@dataclass(slots=True)
class ProviderError:
    code: str
    message: str
    retryable: bool
    context: dict = field(default_factory=dict)


@dataclass(slots=True)
class GenerationResult:
    title: str
    body: str
    tags: list[str]
    cta: str = ""
    content_type: str = "note"
    image_prompt: str = ""


class LLMProvider(Protocol):
    def generate_draft(self, payload: dict) -> GenerationResult: ...


class ImageProvider(Protocol):
    def generate_image(self, payload: dict) -> dict: ...


class PublisherProvider(Protocol):
    def publish(self, payload: dict) -> dict: ...


class FeishuProvider(Protocol):
    def sync_record(self, payload: dict) -> dict: ...
```

- [ ] **Step 4: Run unit tests to verify normalized provider types**

Run: `pytest tests/unit/test_provider_contracts.py -q`
Expected: PASS with `2 passed`.

- [ ] **Step 5: Commit**

```bash
git add app/domain/providers.py tests/unit/test_provider_contracts.py
git commit -m "feat: add provider contracts"
```

### Task 5: Wire shared REST, MCP, and Web UI entrypoints

**Files:**
- Modify: `app/main.py`
- Create: `app/interfaces/mcp/tools.py`
- Create: `app/interfaces/web/router.py`
- Create: `templates/index.html`
- Modify: `app/application/workflows/service.py`
- Test: `tests/integration/test_interface_parity.py`

- [ ] **Step 1: Write the failing interface parity test**

```python
# tests/integration/test_interface_parity.py
from fastapi.testclient import TestClient

from app.main import create_app


def test_web_shell_loads() -> None:
    client = TestClient(create_app())

    response = client.get("/")

    assert response.status_code == 200
    assert "Xiaohongshu Content Platform" in response.text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/integration/test_interface_parity.py -q`
Expected: FAIL with `404 != 200` because the web route is not registered yet.

- [ ] **Step 3: Add interface shells over the shared service layer**

```python
# app/interfaces/web/router.py
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"title": "Xiaohongshu Content Platform"},
    )
```

```html
<!-- templates/index.html -->
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>{{ title }}</title>
  </head>
  <body>
    <h1>{{ title }}</h1>
    <p>Platform foundation is running.</p>
  </body>
</html>
```

```python
# app/interfaces/mcp/tools.py
from app.application.workflows.service import WorkflowService


def dispatch_workflow_tool(workflow_type: str, payload: dict) -> dict:
    result = WorkflowService().dispatch(workflow_type, payload)
    return {"job_id": result.job_id, "workflow_type": result.workflow_type, "status": result.status}
```

```python
# app/main.py
from fastapi import FastAPI

from app.interfaces.rest.router import build_rest_router
from app.interfaces.web.router import router as web_router


def create_app() -> FastAPI:
    app = FastAPI(title="Xiaohongshu Content Platform")
    app.include_router(build_rest_router())
    app.include_router(web_router)
    return app
```

- [ ] **Step 4: Run the interface tests**

Run: `pytest tests/integration/test_health.py tests/integration/test_interface_parity.py -q`
Expected: PASS with `2 passed`.

- [ ] **Step 5: Commit**

```bash
git add app/main.py app/interfaces/mcp/tools.py app/interfaces/web/router.py templates/index.html tests/integration/test_interface_parity.py
git commit -m "feat: add shared operator entrypoints"
```

### Task 6: Verify the foundation and document local operations

**Files:**
- Create: `README.md`
- Modify: `docs/superpowers/specs/2026-04-04-xiaohongshu-content-platform-design.md`
- Test: `tests/integration/test_health.py`
- Test: `tests/integration/test_job_dispatch.py`
- Test: `tests/unit/test_state_models.py`
- Test: `tests/unit/test_provider_contracts.py`

- [ ] **Step 1: Write the README and startup instructions**

```md
# Xiaohongshu Content Platform

## Local development

1. Install dependencies from `pyproject.toml`
2. Start PostgreSQL and Redis
3. Run `uvicorn app.main:app --reload`
4. Run `celery -A app.jobs.celery_app.celery_app worker --loglevel=info`

## Verification

- `pytest tests/unit -q`
- `pytest tests/integration -q`
- `openspec validate bootstrap-xiaohongshu-content-platform --strict`
```

- [ ] **Step 2: Run the verification suite**

Run: `pytest tests/unit -q && pytest tests/integration -q`
Expected: PASS with all planned foundation tests succeeding.

- [ ] **Step 3: Validate the OpenSpec change**

Run: `openspec validate bootstrap-xiaohongshu-content-platform`
Expected: PASS with no missing artifact or spec structure errors.

- [ ] **Step 4: Update the design doc with implementation notes**

```md
## Implementation Notes

- Foundation change completed
- Follow-on changes should target crawler, analysis, generation, publish flow, Feishu sync, and richer UI separately
```

- [ ] **Step 5: Commit**

```bash
git add README.md docs/superpowers/specs/2026-04-04-xiaohongshu-content-platform-design.md
git commit -m "docs: add foundation runbook and verification notes"
```
