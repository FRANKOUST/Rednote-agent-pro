from fastapi.testclient import TestClient


def test_entity_rest_endpoints_expose_pipeline_outputs() -> None:
    from app.main import create_app

    client = TestClient(create_app())

    create_response = client.post(
        "/api/pipeline-runs",
        json={"keywords": ["穿搭"], "min_likes": 20, "min_favorites": 5, "min_comments": 2, "auto_publish": False},
    )
    assert create_response.status_code == 202
    run_id = create_response.json()["id"]

    source_posts = client.get("/api/source-posts")
    assert source_posts.status_code == 200
    assert len(source_posts.json()["items"]) >= 1

    reports = client.get("/api/analysis-reports")
    assert reports.status_code == 200
    assert len(reports.json()["items"]) == 1

    topics = client.get("/api/topic-suggestions")
    assert topics.status_code == 200
    assert len(topics.json()["items"]) >= 1

    images = client.get("/api/image-assets")
    assert images.status_code == 200
    assert len(images.json()["items"]) >= 1

    filtered_posts = client.get(f"/api/source-posts?run_id={run_id}")
    assert filtered_posts.status_code == 200
    assert all(item["run_id"] == run_id for item in filtered_posts.json()["items"])

    source_post_id = filtered_posts.json()["items"][0]["id"]
    source_post_detail = client.get(f"/api/source-posts/{source_post_id}")
    assert source_post_detail.status_code == 200
    assert source_post_detail.json()["id"] == source_post_id

    report_id = reports.json()["items"][0]["id"]
    report_detail = client.get(f"/api/analysis-reports/{report_id}")
    assert report_detail.status_code == 200
    assert report_detail.json()["id"] == report_id
