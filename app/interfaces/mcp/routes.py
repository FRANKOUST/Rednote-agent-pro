from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.application.factory import get_pipeline_service
from app.schemas import MCPRequest

router = APIRouter()


def _tools() -> list[dict]:
    return [
        {"name": "run_content_pipeline", "description": "Run the content pipeline through the shared business layer.", "inputSchema": {"type": "object", "properties": {"keywords": {"type": "array", "items": {"type": "string"}}, "topic_words": {"type": "array", "items": {"type": "string"}}, "run_mode": {"type": "string"}, "dry_run": {"type": "boolean"}}, "required": ["keywords"]}},
        {"name": "run_pipeline_stage", "description": "Run one explicit pipeline stage for an existing run.", "inputSchema": {"type": "object", "properties": {"run_id": {"type": "string"}, "stage": {"type": "string"}}, "required": ["run_id", "stage"]}},
        {"name": "crawl_and_analyze", "description": "Run crawl then analyze for a staged run.", "inputSchema": {"type": "object", "properties": {"keywords": {"type": "array", "items": {"type": "string"}}}, "required": ["keywords"]}},
        {"name": "generate_topics_from_run", "description": "Generate topics for a run that already has analysis.", "inputSchema": {"type": "object", "properties": {"run_id": {"type": "string"}}, "required": ["run_id"]}},
        {"name": "generate_draft_from_topic", "description": "Generate drafts for a run that already has topics.", "inputSchema": {"type": "object", "properties": {"run_id": {"type": "string"}}, "required": ["run_id"]}},
        {"name": "prepare_publish", "description": "Prepare a draft for publish preview/send.", "inputSchema": {"type": "object", "properties": {"draft_id": {"type": "string"}}, "required": ["draft_id"]}},
        {"name": "preview_publish", "description": "Preview a prepared draft publish package.", "inputSchema": {"type": "object", "properties": {"draft_id": {"type": "string"}}, "required": ["draft_id"]}},
        {"name": "send_publish", "description": "Send a publish package via the configured provider.", "inputSchema": {"type": "object", "properties": {"draft_id": {"type": "string"}, "dry_run": {"type": "boolean"}}, "required": ["draft_id"]}},
        {"name": "sync_crawled_data", "description": "Sync crawled data for a run.", "inputSchema": {"type": "object", "properties": {"run_id": {"type": "string"}, "dry_run": {"type": "boolean"}}, "required": ["run_id"]}},
        {"name": "sync_generated_data", "description": "Sync generated data for a run.", "inputSchema": {"type": "object", "properties": {"run_id": {"type": "string"}, "dry_run": {"type": "boolean"}}, "required": ["run_id"]}},
        {"name": "check_collector_login", "description": "Check collector login readiness.", "inputSchema": {"type": "object", "properties": {}}},
        {"name": "check_publish_login", "description": "Check publish login readiness.", "inputSchema": {"type": "object", "properties": {}}},
        {"name": "check_provider_health", "description": "Return provider health summary.", "inputSchema": {"type": "object", "properties": {}}},
        {"name": "list_runs", "description": "List pipeline runs.", "inputSchema": {"type": "object", "properties": {}}},
        {"name": "list_drafts", "description": "List drafts.", "inputSchema": {"type": "object", "properties": {}}},
        {"name": "get_provider_status", "description": "Legacy provider diagnostics + health tool.", "inputSchema": {"type": "object", "properties": {}}},
    ]


@router.post("/mcp")
def handle_mcp(request: MCPRequest) -> dict:
    if request.method == "initialize":
        return {"jsonrpc": "2.0", "id": request.id, "result": {"serverInfo": {"name": "xhs-platform-mcp", "version": "0.3.0"}}}
    if request.method == "tools/list":
        return {"jsonrpc": "2.0", "id": request.id, "result": {"tools": _tools()}}
    if request.method == "tools/call":
        params = request.params or {}
        name = params.get("name")
        arguments = params.get("arguments", {})
        service = get_pipeline_service()
        if name == "run_content_pipeline":
            return {"jsonrpc": "2.0", "id": request.id, "result": service.create_run(arguments)}
        if name == "run_pipeline_stage":
            return {"jsonrpc": "2.0", "id": request.id, "result": service.run_stage(arguments["run_id"], arguments["stage"])}
        if name == "crawl_and_analyze":
            run = service.create_run({**arguments, "run_mode": "step", "dry_run": arguments.get("dry_run", True)})
            service.run_stage(run["id"], "crawl")
            return {"jsonrpc": "2.0", "id": request.id, "result": service.run_stage(run["id"], "analyze")}
        if name == "generate_topics_from_run":
            return {"jsonrpc": "2.0", "id": request.id, "result": service.run_stage(arguments["run_id"], "topic")}
        if name == "generate_draft_from_topic":
            return {"jsonrpc": "2.0", "id": request.id, "result": service.run_stage(arguments["run_id"], "draft")}
        if name == "prepare_publish":
            return {"jsonrpc": "2.0", "id": request.id, "result": service.prepare_publish(arguments["draft_id"])}
        if name == "preview_publish":
            return {"jsonrpc": "2.0", "id": request.id, "result": service.preview_publish(arguments["draft_id"])}
        if name == "send_publish":
            return {"jsonrpc": "2.0", "id": request.id, "result": service.send_publish(arguments["draft_id"], arguments.get("dry_run", True))}
        if name == "sync_crawled_data":
            return {"jsonrpc": "2.0", "id": request.id, "result": service.sync_crawled(arguments["run_id"], arguments.get("dry_run", True))}
        if name == "sync_generated_data":
            return {"jsonrpc": "2.0", "id": request.id, "result": service.sync_generated(arguments["run_id"], arguments.get("dry_run", True))}
        if name == "check_collector_login":
            return {"jsonrpc": "2.0", "id": request.id, "result": service.check_collector_login()}
        if name == "check_publish_login":
            return {"jsonrpc": "2.0", "id": request.id, "result": service.check_publish_login()}
        if name == "check_provider_health":
            return {"jsonrpc": "2.0", "id": request.id, "result": service.provider_health()}
        if name == "list_runs":
            return {"jsonrpc": "2.0", "id": request.id, "result": service.list_runs()}
        if name == "list_drafts":
            return {"jsonrpc": "2.0", "id": request.id, "result": {"items": service.list_drafts()}}
        if name == "get_provider_status":
            return {"jsonrpc": "2.0", "id": request.id, "result": {"diagnostics": service.provider_diagnostics(), "health": service.provider_health()}}
        raise HTTPException(status_code=404, detail=f"Unknown tool: {name}")
    raise HTTPException(status_code=400, detail=f"Unsupported MCP method: {request.method}")
