from fastapi.testclient import TestClient


def test_web_console_run_detail_and_diagnostics_pages_render() -> None:
    from app.main import create_app

    client = TestClient(create_app())
    run = client.post(
        "/api/pipeline-runs",
        json={"keywords": ["家装"], "min_likes": 10, "min_favorites": 2, "min_comments": 1, "auto_publish": False},
    ).json()

    run_page = client.get(f"/console/runs/{run['id']}")
    assert run_page.status_code == 200
    assert run["id"] in run_page.text

    diagnostics_page = client.get(f"/console/runs/{run['id']}/diagnostics")
    assert diagnostics_page.status_code == 200
    assert "Diagnostics" in diagnostics_page.text
