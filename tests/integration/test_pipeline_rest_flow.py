from fastapi.testclient import TestClient


def test_rest_pipeline_review_publish_and_sync_flow() -> None:
    from app.main import create_app

    client = TestClient(create_app())

    create_response = client.post(
        "/api/pipeline-runs",
        json={
            "keywords": ["咖啡"],
            "min_likes": 100,
            "min_favorites": 20,
            "min_comments": 5,
            "auto_publish": False,
        },
    )

    assert create_response.status_code == 202
    run_id = create_response.json()["id"]

    run_response = client.get(f"/api/pipeline-runs/{run_id}")
    assert run_response.status_code == 200
    run_payload = run_response.json()
    assert run_payload["status"] == "completed"
    assert run_payload["counts"]["source_posts"] >= 1
    assert run_payload["counts"]["analysis_reports"] == 1
    assert run_payload["counts"]["topic_suggestions"] >= 1
    assert run_payload["counts"]["content_drafts"] >= 1

    sync_records_after_generation = client.get("/api/sync-records")
    assert sync_records_after_generation.status_code == 200
    generation_entities = {item["entity_type"] for item in sync_records_after_generation.json()["items"]}
    assert "source_post_batch" in generation_entities
    assert "content_draft_batch" in generation_entities

    list_runs_response = client.get("/api/pipeline-runs")
    assert list_runs_response.status_code == 200
    assert len(list_runs_response.json()["items"]) >= 1

    diagnostics_response = client.get(f"/api/pipeline-runs/{run_id}/diagnostics")
    assert diagnostics_response.status_code == 200
    diagnostics_payload = diagnostics_response.json()
    assert any(item["stage"] == "crawl" for item in diagnostics_payload["items"])
    assert any(item["provider"] for item in diagnostics_payload["items"])

    draft_id = run_payload["draft_ids"][0]

    approve_response = client.post(f"/api/drafts/{draft_id}/approve", json={"review_notes": "approved for publish"})
    assert approve_response.status_code == 200
    assert approve_response.json()["status"] == "approved"

    publish_response = client.post(f"/api/drafts/{draft_id}/publish")
    assert publish_response.status_code == 200
    publish_payload = publish_response.json()
    assert publish_payload["status"] == "published"
    assert publish_payload["sync_record"]["status"] == "synced"

    publish_jobs_response = client.get("/api/publish-jobs")
    assert publish_jobs_response.status_code == 200
    assert len(publish_jobs_response.json()["items"]) >= 1

    audit_response = client.get("/api/audit-logs")
    assert audit_response.status_code == 200
    assert any(entry["event_type"] == "draft.approved" for entry in audit_response.json()["items"])
    assert any(entry["event_type"] == "publish.completed" for entry in audit_response.json()["items"])


def test_pipeline_runs_with_safe_playwright_collector_fallback() -> None:
    import os

    from app.db.session import reset_db_state

    reset_db_state()
    os.environ["XHS_DEFAULT_COLLECTOR_PROVIDER"] = "playwright"
    os.environ["XHS_PLAYWRIGHT_SAFE_MODE"] = "true"
    os.environ["XHS_ENABLE_REAL_COLLECTOR"] = "false"

    from app.main import create_app

    client = TestClient(create_app())

    response = client.post(
        "/api/pipeline-runs",
        json={"keywords": ["美妆"], "min_likes": 20, "min_favorites": 10, "min_comments": 3, "auto_publish": False},
    )

    assert response.status_code == 202
    assert response.json()["status"] == "completed"
    assert response.json()["counts"]["source_posts"] >= 1


def test_pipeline_runs_with_safe_real_provider_stubs() -> None:
    import os

    from app.db.session import reset_db_state

    reset_db_state()
    os.environ["XHS_DEFAULT_MODEL_PROVIDER"] = "openai"
    os.environ["XHS_DEFAULT_IMAGE_PROVIDER"] = "openai"
    os.environ["XHS_DEFAULT_PUBLISH_PROVIDER"] = "api"
    os.environ["XHS_DEFAULT_SYNC_PROVIDER"] = "feishu"
    os.environ["XHS_ENABLE_REAL_MODEL_PROVIDER"] = "false"
    os.environ["XHS_ENABLE_REAL_IMAGE_PROVIDER"] = "false"
    os.environ["XHS_ENABLE_REAL_PUBLISH_PROVIDER"] = "false"
    os.environ["XHS_ENABLE_REAL_SYNC_PROVIDER"] = "false"

    from app.main import create_app

    client = TestClient(create_app())

    create_response = client.post(
        "/api/pipeline-runs",
        json={"keywords": ["健身"], "min_likes": 30, "min_favorites": 10, "min_comments": 2, "auto_publish": False},
    )
    assert create_response.status_code == 202
    draft_id = create_response.json()["draft_ids"][0]

    approve_response = client.post(f"/api/drafts/{draft_id}/approve", json={"review_notes": "safe stub approval"})
    assert approve_response.status_code == 200

    publish_response = client.post(f"/api/drafts/{draft_id}/publish")
    assert publish_response.status_code == 200
    assert publish_response.json()["status"] == "published"


def test_live_publish_provider_is_gated_to_safe_stub_by_default() -> None:
    import os

    from app.db.session import reset_db_state

    reset_db_state()
    os.environ["XHS_DEFAULT_PUBLISH_PROVIDER"] = "api"
    os.environ["XHS_ENABLE_REAL_PUBLISH_PROVIDER"] = "true"
    os.environ["XHS_XHS_PUBLISH_API_TOKEN"] = "publish-key"
    os.environ["XHS_XHS_PUBLISH_API_BASE"] = "https://publisher.example.com"
    os.environ["XHS_ALLOW_LIVE_PUBLISH"] = "false"

    from app.main import create_app

    client = TestClient(create_app())

    create_response = client.post(
        "/api/pipeline-runs",
        json={"keywords": ["出行"], "min_likes": 30, "min_favorites": 10, "min_comments": 2, "auto_publish": False},
    )
    draft_id = create_response.json()["draft_ids"][0]

    client.post(f"/api/drafts/{draft_id}/approve", json={"review_notes": "approved"})
    publish_response = client.post(f"/api/drafts/{draft_id}/publish")

    assert publish_response.status_code == 200
    assert publish_response.json()["publish_job"]["provider"] == "xhs-api-safe-stub"
