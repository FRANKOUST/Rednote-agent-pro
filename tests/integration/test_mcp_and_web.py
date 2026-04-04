from fastapi.testclient import TestClient


def test_web_console_root_renders_dashboard() -> None:
    from app.main import create_app

    client = TestClient(create_app())

    response = client.get("/")

    assert response.status_code == 200
    assert "Xiaohongshu Content Platform" in response.text


def test_mcp_tool_surface_lists_and_calls_tools() -> None:
    from app.main import create_app

    client = TestClient(create_app())

    tools_response = client.post("/mcp", json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    assert tools_response.status_code == 200
    tools_payload = tools_response.json()
    assert any(tool["name"] == "start_pipeline" for tool in tools_payload["result"]["tools"])

    call_response = client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "start_pipeline",
                "arguments": {"keywords": ["护肤"], "min_likes": 50, "auto_publish": False},
            },
        },
    )
    assert call_response.status_code == 200
    result = call_response.json()["result"]
    assert result["status"] == "completed"
    assert result["counts"]["content_drafts"] >= 1

    runs_response = client.post(
        "/mcp",
        json={"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "list_runs", "arguments": {}}},
    )
    assert runs_response.status_code == 200
    assert len(runs_response.json()["result"]["items"]) >= 1

    source_posts_response = client.post(
        "/mcp",
        json={"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "list_source_posts", "arguments": {}}},
    )
    assert source_posts_response.status_code == 200
    assert len(source_posts_response.json()["result"]["items"]) >= 1

    source_post_id = source_posts_response.json()["result"]["items"][0]["id"]
    source_post_detail_response = client.post(
        "/mcp",
        json={"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "get_source_post", "arguments": {"id": source_post_id}}},
    )
    assert source_post_detail_response.status_code == 200
    assert source_post_detail_response.json()["result"]["id"] == source_post_id
