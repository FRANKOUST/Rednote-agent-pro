import os

from fastapi.testclient import TestClient

from app.db.session import reset_db_state


def test_mcp_tool_surface_lists_high_level_operator_actions() -> None:
    reset_db_state()
    os.environ["XHS_DEFAULT_COLLECTOR_PROVIDER"] = "scrapling_xhs"
    os.environ["XHS_DEFAULT_SYNC_PROVIDER"] = "feishu_cli"
    os.environ["XHS_SCRAPLING_MODE"] = "fixture"
    os.environ["XHS_FEISHU_CLI_DRY_RUN"] = "true"

    from app.main import create_app

    client = TestClient(create_app())

    tools_payload = client.post("/mcp", json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"}).json()
    tool_names = {tool["name"] for tool in tools_payload["result"]["tools"]}
    assert {
        "run_content_pipeline",
        "run_pipeline_stage",
        "crawl_and_analyze",
        "generate_topics_from_run",
        "generate_draft_from_topic",
        "prepare_publish",
        "preview_publish",
        "send_publish",
        "sync_crawled_data",
        "sync_generated_data",
        "check_collector_login",
        "check_publish_login",
        "check_provider_health",
    }.issubset(tool_names)


def test_mcp_tools_execute_high_level_pipeline_actions() -> None:
    from app.main import create_app

    client = TestClient(create_app())

    run_result = client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "run_content_pipeline",
                "arguments": {"keywords": ["护肤"], "topic_words": ["护肤"], "run_mode": "full", "dry_run": True},
            },
        },
    ).json()["result"]
    assert run_result["counts"]["content_drafts"] >= 1

    provider_status = client.post(
        "/mcp",
        json={"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "check_provider_health", "arguments": {}}},
    ).json()["result"]
    assert "collector" in provider_status

    collector_login = client.post(
        "/mcp",
        json={"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "check_collector_login", "arguments": {}}},
    ).json()["result"]
    assert collector_login["provider"]


def test_web_content_workbench_renders_dashboard_and_run_detail() -> None:
    from app.main import create_app

    client = TestClient(create_app())
    dashboard = client.get("/")
    assert dashboard.status_code == 200
    assert "内容助手工作台" in dashboard.text
    assert "一键跑完整链路" in dashboard.text

    run = client.post(
        "/api/content-pipeline/runs",
        json={"keywords": ["家装"], "topic_words": ["家装"], "run_mode": "full", "dry_run": True},
    ).json()

    run_page = client.get(f"/console/runs/{run['id']}")
    assert run_page.status_code == 200
    assert "Pipeline Run" in run_page.text
    assert "crawl" in run_page.text

    diagnostics_page = client.get(f"/console/runs/{run['id']}/diagnostics")
    assert diagnostics_page.status_code == 200
    assert "Stage Diagnostics" in diagnostics_page.text
