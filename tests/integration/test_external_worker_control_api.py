import json

from fastapi.testclient import TestClient


def test_external_worker_control_endpoints_can_inspect_requeue_and_cancel(tmp_path) -> None:
    import os

    from app.db.session import reset_db_state

    reset_db_state()
    os.environ["XHS_TASK_MODE"] = "external_worker"
    os.environ["XHS_WORKER_ADAPTER_KIND"] = "filesystem"
    os.environ["XHS_WORKER_QUEUE_DIR"] = str(tmp_path)

    from app.main import create_app

    client = TestClient(create_app())
    response = client.post(
        "/api/pipeline-runs",
        json={"keywords": ["家电"], "min_likes": 5, "min_favorites": 1, "min_comments": 1, "auto_publish": False},
    )
    run_id = response.json()["id"]
    manifest = next(tmp_path.glob("*.json"))
    job_id = manifest.stem

    inspect_response = client.get(f"/api/external-workers/jobs/{job_id}")
    assert inspect_response.status_code == 200
    assert inspect_response.json()["job_id"] == job_id

    cancel_response = client.post(f"/api/external-workers/jobs/{job_id}/cancel")
    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "cancelled"

    payload = json.loads(manifest.read_text(encoding="utf-8"))
    assert payload["status"] == "cancelled"

    requeue_response = client.post(f"/api/external-workers/jobs/{job_id}/requeue")
    assert requeue_response.status_code == 200
    assert requeue_response.json()["status"] == "queued"

    payload = json.loads(manifest.read_text(encoding="utf-8"))
    assert payload["status"] == "queued"
    assert payload["run_id"] == run_id
