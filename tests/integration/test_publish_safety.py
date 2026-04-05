from fastapi.testclient import TestClient


def test_duplicate_publish_is_blocked() -> None:
    from app.main import create_app

    client = TestClient(create_app())
    run = client.post(
        "/api/pipeline-runs",
        json={"keywords": ["效率"], "min_likes": 10, "min_favorites": 2, "min_comments": 1, "auto_publish": False},
    ).json()
    draft_id = run["draft_ids"][0]

    client.post(f"/api/drafts/{draft_id}/approve", json={"review_notes": "ok"})
    first_publish = client.post(f"/api/drafts/{draft_id}/publish")
    assert first_publish.status_code == 200

    second_publish = client.post(f"/api/drafts/{draft_id}/publish")
    assert second_publish.status_code == 400
