from fastapi.testclient import TestClient


def test_web_console_run_detail_and_diagnostics_pages_render() -> None:
    from app.main import create_app

    client = TestClient(create_app())
    run = client.post(
        "/api/pipeline-runs",
        json={"keywords": ["家装"], "min_likes": 10, "min_favorites": 2, "min_comments": 1, "auto_publish": False},
    ).json()

    run_page = client.get(f"/console/runs/{run['id']}")
    assert run_page.status_code == 200
    assert run["id"] in run_page.text

    diagnostics_page = client.get(f"/console/runs/{run['id']}/diagnostics")
    assert diagnostics_page.status_code == 200
    assert "Diagnostics" in diagnostics_page.text


def test_web_console_collector_and_sync_run_pages_render() -> None:
    from app.main import create_app

    client = TestClient(create_app())
    client.post("/api/collector-runs/search", json={"keywords": ["咖啡"], "dry_run": True})
    client.post("/api/sync-runs", json={"entity_type": "source_post_batch", "payload": {"title": "demo"}, "dry_run": True})

    collector_page = client.get("/console/collector-runs")
    assert collector_page.status_code == 200
    assert "Collector Runs" in collector_page.text

    sync_page = client.get("/console/sync-runs")
    assert sync_page.status_code == 200
    assert "Sync Runs" in sync_page.text

    collector_run_id = client.get("/api/collector-runs").json()["items"][0]["id"]
    sync_run_id = client.get("/api/sync-runs").json()["items"][0]["id"]
    assert client.get(f"/console/collector-runs/{collector_run_id}").status_code == 200
    assert client.get(f"/console/sync-runs/{sync_run_id}").status_code == 200
