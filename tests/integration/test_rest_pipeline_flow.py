import os

from fastapi.testclient import TestClient

from app.db.session import reset_db_state


def test_rest_pipeline_review_publish_and_sync_flow() -> None:
    reset_db_state()
    os.environ["XHS_DEFAULT_COLLECTOR_PROVIDER"] = "scrapling_xhs"
    os.environ["XHS_DEFAULT_MODEL_PROVIDER"] = "custom_model_router"
    os.environ["XHS_DEFAULT_SYNC_PROVIDER"] = "feishu_cli"
    os.environ["XHS_SCRAPLING_MODE"] = "fixture"
    os.environ["XHS_FEISHU_CLI_DRY_RUN"] = "true"

    from app.main import create_app

    client = TestClient(create_app())

    create_response = client.post("/api/pipeline-runs", json={"keywords": ["咖啡"], "min_likes": 100, "min_favorites": 20, "min_comments": 5, "auto_publish": False, "dry_run": True})
    assert create_response.status_code == 202
    run_id = create_response.json()["id"]

    run_payload = client.get(f"/api/pipeline-runs/{run_id}").json()
    assert run_payload["status"] == "completed"
    assert run_payload["counts"]["source_posts"] >= 1
    assert run_payload["counts"]["content_drafts"] >= 1

    sync_records = client.get("/api/sync-records").json()["items"]
    generation_entities = {item["entity_type"] for item in sync_records}
    assert {"source_post_batch", "content_draft_batch"}.issubset(generation_entities)

    diagnostics_payload = client.get(f"/api/pipeline-runs/{run_id}/diagnostics").json()
    assert any(item["stage"] == "crawl" for item in diagnostics_payload["items"])

    draft_id = run_payload["draft_ids"][0]
    assert client.post(f"/api/drafts/{draft_id}/approve", json={"review_notes": "approved for publish"}).status_code == 200
    publish_payload = client.post(f"/api/drafts/{draft_id}/publish").json()
    assert publish_payload["status"] == "published"
    assert publish_payload["sync_record"]["status"] == "synced"
    assert publish_payload["sync_record"]["provider"] == "feishu-cli-sync"
