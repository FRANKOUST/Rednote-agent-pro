from fastapi.testclient import TestClient


def test_web_console_entity_view_renders_pipeline_outputs() -> None:
    from app.main import create_app

    client = TestClient(create_app())
    client.post(
        "/api/pipeline-runs",
        json={"keywords": ["美食"], "min_likes": 10, "min_favorites": 2, "min_comments": 1, "auto_publish": False},
    )

    response = client.get("/console/entities")

    assert response.status_code == 200
    assert "Source Posts" in response.text
    assert "Analysis Reports" in response.text
    assert "Image Assets" in response.text


def test_web_console_entity_detail_page_renders_source_post() -> None:
    from app.main import create_app

    client = TestClient(create_app())
    client.post(
        "/api/pipeline-runs",
        json={"keywords": ["读书"], "min_likes": 10, "min_favorites": 2, "min_comments": 1, "auto_publish": False},
    )
    source_post = client.get("/api/source-posts").json()["items"][0]

    response = client.get(f"/console/source-posts/{source_post['id']}")

    assert response.status_code == 200
    assert source_post["title"] in response.text


def test_web_console_entity_detail_page_renders_analysis_report() -> None:
    from app.main import create_app

    client = TestClient(create_app())
    client.post(
        "/api/pipeline-runs",
        json={"keywords": ["电影"], "min_likes": 10, "min_favorites": 2, "min_comments": 1, "auto_publish": False},
    )
    report = client.get("/api/analysis-reports").json()["items"][0]

    response = client.get(f"/console/analysis-reports/{report['id']}")

    assert response.status_code == 200
    assert report["id"] in response.text
