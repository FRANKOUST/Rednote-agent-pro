import os

from fastapi.testclient import TestClient

from app.db.session import reset_db_state


def test_api_requires_operator_key_when_auth_enabled() -> None:
    reset_db_state()
    os.environ["XHS_AUTH_ENABLED"] = "true"
    os.environ["XHS_OPERATOR_API_KEY"] = "secret-key"

    from app.main import create_app

    client = TestClient(create_app())

    unauthorized = client.get("/api/drafts")
    assert unauthorized.status_code == 401

    authorized = client.get("/api/drafts", headers={"X-Operator-Key": "secret-key"})
    assert authorized.status_code == 200

    unauthorized_mcp = client.post("/mcp", json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    assert unauthorized_mcp.status_code == 401

    authorized_mcp = client.post(
        "/mcp",
        json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
        headers={"X-Operator-Key": "secret-key"},
    )
    assert authorized_mcp.status_code == 200


def test_request_id_header_and_observability_summary_are_available() -> None:
    reset_db_state()
    os.environ["XHS_AUTH_ENABLED"] = "false"

    from app.main import create_app

    client = TestClient(create_app())

    health = client.get("/api/health")
    assert health.status_code == 200
    assert "X-Request-ID" in health.headers

    summary = client.get("/api/observability/summary")
    assert summary.status_code == 200
    payload = summary.json()
    assert "workflow_runs" in payload
    assert "audit_logs" in payload


def test_worker_stub_mode_returns_queued_run() -> None:
    reset_db_state()
    os.environ["XHS_TASK_MODE"] = "worker_stub"
    os.environ["XHS_AUTH_ENABLED"] = "false"

    from app.main import create_app

    client = TestClient(create_app())

    response = client.post(
        "/api/pipeline-runs",
        json={"keywords": ["家居"], "min_likes": 5, "min_favorites": 1, "min_comments": 1, "auto_publish": False},
    )

    assert response.status_code == 202
    assert response.json()["status"] == "queued"
    assert response.json()["current_stage"] == "queued"


def test_external_worker_mode_returns_queued_run_and_enqueues_manifest(tmp_path) -> None:
    reset_db_state()
    os.environ["XHS_TASK_MODE"] = "external_worker"
    os.environ["XHS_WORKER_ADAPTER_KIND"] = "filesystem"
    os.environ["XHS_WORKER_QUEUE_DIR"] = str(tmp_path)
    os.environ["XHS_AUTH_ENABLED"] = "false"

    from app.main import create_app

    client = TestClient(create_app())

    response = client.post(
        "/api/pipeline-runs",
        json={"keywords": ["收纳"], "min_likes": 5, "min_favorites": 1, "min_comments": 1, "auto_publish": False},
    )

    assert response.status_code == 202
    assert response.json()["status"] == "queued"
    assert len(list(tmp_path.glob("*.json"))) == 1


def test_subprocess_external_worker_can_complete_pipeline(tmp_path) -> None:
    import json
    import time

    reset_db_state()
    os.environ["XHS_TASK_MODE"] = "external_worker"
    os.environ["XHS_WORKER_ADAPTER_KIND"] = "subprocess"
    os.environ["XHS_WORKER_QUEUE_DIR"] = str(tmp_path)
    os.environ["XHS_AUTH_ENABLED"] = "false"

    from app.main import create_app

    client = TestClient(create_app())

    response = client.post(
        "/api/pipeline-runs",
        json={"keywords": ["旅行"], "min_likes": 5, "min_favorites": 1, "min_comments": 1, "auto_publish": False},
    )

    assert response.status_code == 202
    run_id = response.json()["id"]
    manifest = next(tmp_path.glob("*.json"))

    for _ in range(50):
        payload = json.loads(manifest.read_text(encoding="utf-8"))
        run_response = client.get(f"/api/pipeline-runs/{run_id}")
        if payload.get("status") == "completed" and run_response.json()["status"] == "completed":
            break
        time.sleep(0.1)

    assert payload["status"] == "completed"
    assert run_response.json()["status"] == "completed"
