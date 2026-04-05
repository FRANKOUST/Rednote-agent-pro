import os

from fastapi.testclient import TestClient

from app.db.session import reset_db_state


def test_viewer_can_read_but_cannot_publish() -> None:
    reset_db_state()
    os.environ["XHS_AUTH_ENABLED"] = "true"
    os.environ["XHS_OPERATOR_API_KEY"] = ""
    os.environ["XHS_VIEWER_API_KEY"] = "viewer-key"
    os.environ["XHS_REVIEWER_API_KEY"] = "reviewer-key"
    os.environ["XHS_ADMIN_API_KEY"] = "admin-key"

    from app.main import create_app

    client = TestClient(create_app())

    assert client.get("/api/drafts", headers={"X-Operator-Key": "viewer-key"}).status_code == 200
    assert client.post(
        "/api/pipeline-runs",
        json={"keywords": ["教育"], "min_likes": 1, "min_favorites": 1, "min_comments": 1, "auto_publish": False},
        headers={"X-Operator-Key": "viewer-key"},
    ).status_code == 403


def test_reviewer_can_approve_but_cannot_publish() -> None:
    reset_db_state()
    os.environ["XHS_AUTH_ENABLED"] = "true"
    os.environ["XHS_OPERATOR_API_KEY"] = "operator-key"
    os.environ["XHS_VIEWER_API_KEY"] = "viewer-key"
    os.environ["XHS_REVIEWER_API_KEY"] = "reviewer-key"
    os.environ["XHS_ADMIN_API_KEY"] = "admin-key"

    from app.main import create_app

    client = TestClient(create_app())
    run = client.post(
        "/api/pipeline-runs",
        json={"keywords": ["教育"], "min_likes": 1, "min_favorites": 1, "min_comments": 1, "auto_publish": False},
        headers={"X-Operator-Key": "operator-key"},
    ).json()
    draft_id = run["draft_ids"][0]

    assert client.post(
        f"/api/drafts/{draft_id}/approve",
        json={"review_notes": "ok"},
        headers={"X-Operator-Key": "reviewer-key"},
    ).status_code == 200
    assert client.post(f"/api/drafts/{draft_id}/publish", headers={"X-Operator-Key": "reviewer-key"}).status_code == 403


def test_admin_can_publish() -> None:
    reset_db_state()
    os.environ["XHS_AUTH_ENABLED"] = "true"
    os.environ["XHS_OPERATOR_API_KEY"] = "operator-key"
    os.environ["XHS_VIEWER_API_KEY"] = "viewer-key"
    os.environ["XHS_REVIEWER_API_KEY"] = "reviewer-key"
    os.environ["XHS_ADMIN_API_KEY"] = "admin-key"

    from app.main import create_app

    client = TestClient(create_app())
    run = client.post(
        "/api/pipeline-runs",
        json={"keywords": ["教育"], "min_likes": 1, "min_favorites": 1, "min_comments": 1, "auto_publish": False},
        headers={"X-Operator-Key": "operator-key"},
    ).json()
    draft_id = run["draft_ids"][0]
    client.post(f"/api/drafts/{draft_id}/approve", json={"review_notes": "ok"}, headers={"X-Operator-Key": "reviewer-key"})

    assert client.post(f"/api/drafts/{draft_id}/publish", headers={"X-Operator-Key": "admin-key"}).status_code == 200
