import os

from fastapi.testclient import TestClient

from app.db.session import reset_db_state


def test_provider_diagnostics_surface_safe_modes() -> None:
    reset_db_state()
    os.environ["XHS_DEFAULT_COLLECTOR_PROVIDER"] = "playwright"
    os.environ["XHS_DEFAULT_MODEL_PROVIDER"] = "openai"
    os.environ["XHS_DEFAULT_IMAGE_PROVIDER"] = "openai"
    os.environ["XHS_DEFAULT_PUBLISH_PROVIDER"] = "browser"
    os.environ["XHS_DEFAULT_SYNC_PROVIDER"] = "feishu"
    os.environ["XHS_ENABLE_REAL_COLLECTOR"] = "false"
    os.environ["XHS_ENABLE_REAL_MODEL_PROVIDER"] = "false"
    os.environ["XHS_ENABLE_REAL_IMAGE_PROVIDER"] = "false"
    os.environ["XHS_ENABLE_REAL_PUBLISH_PROVIDER"] = "false"
    os.environ["XHS_ENABLE_REAL_SYNC_PROVIDER"] = "false"

    from app.main import create_app

    client = TestClient(create_app())
    response = client.get("/api/providers/diagnostics")

    assert response.status_code == 200
    payload = response.json()
    assert payload["collector"]["configured"] == "playwright"
    assert payload["collector"]["active"].startswith("safe-playwright")
    assert payload["language_model"]["configured"] == "openai"
    assert payload["publisher"]["configured"] == "browser"
    assert payload["sync"]["configured"] == "feishu"
