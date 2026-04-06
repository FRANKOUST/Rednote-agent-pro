import os

from fastapi.testclient import TestClient

from app.db.session import reset_db_state


def test_diagnostics_and_health_surfaces_scrapling_model_and_sync_status() -> None:
    reset_db_state()
    os.environ["XHS_DEFAULT_COLLECTOR_PROVIDER"] = "scrapling_xhs"
    os.environ["XHS_DEFAULT_MODEL_PROVIDER"] = "custom_model_router"
    os.environ["XHS_DEFAULT_SYNC_PROVIDER"] = "feishu_cli"
    os.environ["XHS_SCRAPLING_MODE"] = "fixture"
    os.environ["XHS_FEISHU_CLI_DRY_RUN"] = "true"

    from app.main import create_app

    client = TestClient(create_app())

    status_response = client.get("/api/providers/status")
    assert status_response.status_code == 200
    payload = status_response.json()
    assert payload["diagnostics"]["collector"]["configured"] == "scrapling_xhs"
    assert payload["health"]["collector"]["status"] == "ready"
    assert payload["health"]["sync"]["status"] == "ready"

    collector_run = client.post("/api/collector-runs/search", json={"keywords": ["咖啡"], "dry_run": True}).json()
    assert collector_run["result_summary"]["persisted_posts"] >= 1

    sync_run = client.post("/api/sync-runs", json={"entity_type": "publish_job", "payload": {"title": "demo"}, "dry_run": True}).json()
    assert sync_run["status"] == "synced"
    assert sync_run["dry_run"] is True
