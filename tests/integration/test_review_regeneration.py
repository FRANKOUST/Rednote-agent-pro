from fastapi.testclient import TestClient


def test_rejected_draft_can_be_regenerated_into_review_queue() -> None:
    from app.main import create_app

    client = TestClient(create_app())
    run = client.post(
        "/api/pipeline-runs",
        json={"keywords": ["护肤"], "min_likes": 10, "min_favorites": 2, "min_comments": 1, "auto_publish": False},
    ).json()
    draft_id = run["draft_ids"][0]

    reject = client.post(f"/api/drafts/{draft_id}/reject", json={"review_notes": "needs stronger hook"})
    assert reject.status_code == 200
    assert reject.json()["status"] == "rejected"

    regenerate = client.post(f"/api/drafts/{draft_id}/regenerate", json={"review_notes": "make it punchier"})
    assert regenerate.status_code == 200
    assert regenerate.json()["status"] == "review_pending"
    assert regenerate.json()["revision_count"] == 1
