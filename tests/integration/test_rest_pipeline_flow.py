import os

from fastapi.testclient import TestClient

from app.db.session import reset_db_state


def test_rest_content_pipeline_full_run_exposes_eight_stage_workbench_flow() -> None:
    reset_db_state()
    os.environ["XHS_DEFAULT_COLLECTOR_PROVIDER"] = "scrapling_xhs"
    os.environ["XHS_DEFAULT_MODEL_PROVIDER"] = "custom_model_router"
    os.environ["XHS_DEFAULT_SYNC_PROVIDER"] = "feishu_cli"
    os.environ["XHS_SCRAPLING_MODE"] = "fixture"
    os.environ["XHS_FEISHU_CLI_DRY_RUN"] = "true"

    from app.main import create_app

    client = TestClient(create_app())

    create_response = client.post(
        "/api/content-pipeline/runs",
        json={
            "keywords": ["咖啡"],
            "topic_words": ["咖啡", "手冲"],
            "min_likes": 100,
            "min_favorites": 20,
            "min_comments": 5,
            "run_mode": "full",
            "dry_run": True,
        },
    )
    assert create_response.status_code == 202
    payload = create_response.json()
    assert payload["status"] in {"completed", "action_required"}
    assert [stage["stage"] for stage in payload["stages"]] == [
        "crawl",
        "analyze",
        "topic",
        "draft",
        "image",
        "review",
        "publish",
        "sync",
    ]
    assert payload["counts"]["source_posts"] >= 1
    assert payload["counts"]["content_drafts"] >= 1
    assert payload["stage_map"]["publish"]["output_summary"]["mode"] in {"preview_only", "send"}

    run_id = payload["id"]
    diagnostics_payload = client.get(f"/api/content-pipeline/runs/{run_id}/diagnostics").json()
    assert diagnostics_payload["items"][0]["input_summary"]
    assert diagnostics_payload["items"][0]["started_at"]


def test_rest_content_pipeline_supports_stepwise_execution_publish_and_sync_actions() -> None:
    from app.main import create_app

    client = TestClient(create_app())

    create_response = client.post(
        "/api/content-pipeline/runs",
        json={"keywords": ["护肤"], "topic_words": ["护肤"], "run_mode": "step", "dry_run": True},
    )
    assert create_response.status_code == 202
    run_id = create_response.json()["id"]

    for stage in ["crawl", "analyze", "topic", "draft", "image", "review"]:
        stage_response = client.post(f"/api/content-pipeline/runs/{run_id}/stages/{stage}")
        assert stage_response.status_code == 200
        assert stage_response.json()["stage"]["stage"] == stage

    run_payload = client.get(f"/api/content-pipeline/runs/{run_id}").json()
    draft_id = run_payload["draft_ids"][0]

    approve_response = client.post(
        f"/api/content-drafts/{draft_id}/review/approve",
        json={"review_notes": "可以进入发布准备"},
    )
    assert approve_response.status_code == 200
    assert approve_response.json()["status"] == "approved"

    prepare_response = client.post(f"/api/content-drafts/{draft_id}/publish/prepare")
    assert prepare_response.status_code == 200
    assert prepare_response.json()["status"] == "prepared"

    preview_response = client.post(f"/api/content-drafts/{draft_id}/publish/preview")
    assert preview_response.status_code == 200
    assert preview_response.json()["status"] == "preview_ready"
    assert preview_response.json()["preview"]["headline"]

    send_response = client.post(f"/api/content-drafts/{draft_id}/publish/send", json={"dry_run": True})
    assert send_response.status_code == 200
    assert send_response.json()["publish_job"]["status"] == "published"

    sync_crawled = client.post(f"/api/content-pipeline/runs/{run_id}/sync/crawled", json={"dry_run": True})
    assert sync_crawled.status_code == 200
    assert sync_crawled.json()["record"]["business_type"] == "sync_crawled"

    sync_generated = client.post(f"/api/content-pipeline/runs/{run_id}/sync/generated", json={"dry_run": True})
    assert sync_generated.status_code == 200
    assert sync_generated.json()["record"]["business_type"] == "sync_generated"
