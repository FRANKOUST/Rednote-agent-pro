import os

from fastapi.testclient import TestClient

from app.db.session import reset_db_state


def test_mcp_tool_surface_lists_and_calls_tools() -> None:
    reset_db_state()
    os.environ["XHS_DEFAULT_COLLECTOR_PROVIDER"] = "scrapling_xhs"
    os.environ["XHS_DEFAULT_SYNC_PROVIDER"] = "feishu_cli"
    os.environ["XHS_SCRAPLING_MODE"] = "fixture"
    os.environ["XHS_FEISHU_CLI_DRY_RUN"] = "true"

    from app.main import create_app

    client = TestClient(create_app())

    tools_payload = client.post("/mcp", json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"}).json()
    assert any(tool["name"] == "start_collector_detail" for tool in tools_payload["result"]["tools"])

    result = client.post("/mcp", json={"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "start_pipeline", "arguments": {"keywords": ["护肤"], "min_likes": 50, "auto_publish": False, "dry_run": True}}}).json()["result"]
    assert result["status"] == "completed"

    collector_detail = client.post("/mcp", json={"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "start_collector_detail", "arguments": {"note_ids": ["detail-001"], "dry_run": True}}}).json()["result"]
    assert collector_detail["status"] == "completed"

    provider_status = client.post("/mcp", json={"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "get_provider_status", "arguments": {}}}).json()["result"]
    assert "diagnostics" in provider_status and "health" in provider_status


def test_web_console_root_and_provider_pages_render() -> None:
    from app.main import create_app

    client = TestClient(create_app())
    assert client.get("/").status_code == 200
    provider_page = client.get("/console/providers")
    assert provider_page.status_code == 200
    assert "Provider Status" in provider_page.text
