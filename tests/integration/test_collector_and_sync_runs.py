from fastapi.testclient import TestClient


def test_manual_collector_run_and_sync_run_routes_work() -> None:
    from app.main import create_app

    client = TestClient(create_app())

    collector_response = client.post(
        "/api/collector-runs/search",
        json={"keywords": ["咖啡"], "dry_run": True},
    )
    assert collector_response.status_code == 202
    collector_run = collector_response.json()
    assert collector_run["status"] in {"completed", "queued"}

    collector_runs = client.get("/api/collector-runs")
    assert collector_runs.status_code == 200
    assert len(collector_runs.json()["items"]) >= 1

    collector_detail = client.get(f"/api/collector-runs/{collector_run['id']}")
    assert collector_detail.status_code == 200

    sync_response = client.post(
        "/api/sync-runs",
        json={"entity_type": "source_post_batch", "payload": {"title": "demo"}, "dry_run": True},
    )
    assert sync_response.status_code == 202
    sync_run = sync_response.json()
    assert sync_run["status"] in {"completed", "queued", "synced"}

    sync_runs = client.get("/api/sync-runs")
    assert sync_runs.status_code == 200
    assert len(sync_runs.json()["items"]) >= 1

    sync_detail = client.get(f"/api/sync-runs/{sync_run['id']}")
    assert sync_detail.status_code == 200
