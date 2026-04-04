# Implementation Map

## Directory Structure

```text
app/
  application/
    dispatcher.py
    external_worker.py
    services.py
  core/
    config.py
  db/
    base.py
    models.py
    session.py
  domain/
    contracts.py
    models.py
  infrastructure/
    providers/
      collector/mock.py
      llm/mock.py
      image/mock.py
      publisher/mock.py
      feishu/mock.py
      registry.py
  interfaces/
    rest/routes.py
    mcp/routes.py
    web/routes.py
  main.py
tests/
  unit/
  integration/
templates/
docs/
```

## Module Responsibilities

- `app/core/config.py`: settings and environment handling
- `app/domain/models.py`: enums, transitions, payload DTOs
- `app/domain/contracts.py`: provider interfaces
- `app/db/models.py`: persistence schema
- `app/application/dispatcher.py`: task execution abstraction
- `app/application/external_worker.py`: external worker adapter interface and filesystem-backed queue adapter
- `app/application/services.py`: business use cases and pipeline orchestration
- `app/infrastructure/providers/*`: default mock provider implementations
- `app/interfaces/rest/routes.py`: REST endpoints
- `app/interfaces/mcp/routes.py`: MCP-style tools and entity query tools
- `app/interfaces/web/routes.py`: operator console

## Development Order

1. Foundation and config
2. Domain models and state transitions
3. Persistence models
4. Mock providers
5. Pipeline orchestration service
6. REST API
7. MCP tool surface
8. Web Console
9. External worker adapters and live-provider shells
10. Tests and docs

## File-Level Change Focus

- Added all files under `app/`
- Added tests under `tests/`
- Added environment and startup docs
- Added portfolio/demo docs

## Test Strategy

- Unit:
  - draft and publish state transitions
  - provider registry
  - dispatcher modes
- Integration:
  - end-to-end REST flow
  - MCP tool surface
  - Web Console render
  - auth, entity API, and external-worker integration

## Mock Strategy

- `MockCollectorProvider`: returns deterministic source posts
- `MockLanguageModelProvider`: returns deterministic analysis, topics, and drafts
- `MockImageProvider`: writes local SVG assets
- `MockPublisherProvider`: returns mock published URLs
- `MockSyncProvider`: returns mock synced records

## Local Dev Path

1. `pip install -e .[dev]`
2. `copy .env.example .env`
3. `uvicorn app.main:app --reload`
4. 打开 `/` 运行 demo

## Demo Path

1. 启动 pipeline
2. 查看 draft queue
3. 审核 draft
4. 发布 draft
5. 查看 publish jobs、sync records、audit logs
6. 调用 `/mcp` 工具接口
7. 查询实体级 REST / MCP 接口
8. 打开 `/console/entities` 查看实体视图
