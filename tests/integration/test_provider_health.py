import os

from fastapi.testclient import TestClient

from app.db.session import reset_db_state


def test_provider_health_endpoint_reports_runtime_readiness() -> None:
    reset_db_state()
    os.environ["XHS_DEFAULT_COLLECTOR_PROVIDER"] = "playwright"
    os.environ["XHS_DEFAULT_MODEL_PROVIDER"] = "openai"
    os.environ["XHS_DEFAULT_IMAGE_PROVIDER"] = "openai"
    os.environ["XHS_DEFAULT_PUBLISH_PROVIDER"] = "api"
    os.environ["XHS_DEFAULT_SYNC_PROVIDER"] = "feishu"
    os.environ["XHS_ENABLE_REAL_COLLECTOR"] = "true"
    os.environ["XHS_ENABLE_REAL_MODEL_PROVIDER"] = "true"
    os.environ["XHS_ENABLE_REAL_IMAGE_PROVIDER"] = "true"
    os.environ["XHS_ENABLE_REAL_PUBLISH_PROVIDER"] = "true"
    os.environ["XHS_ENABLE_REAL_SYNC_PROVIDER"] = "true"
    os.environ["XHS_OPENAI_API_KEY"] = ""
    os.environ["XHS_XHS_PUBLISH_API_TOKEN"] = ""
    os.environ["XHS_FEISHU_APP_ID"] = ""
    os.environ["XHS_FEISHU_APP_SECRET"] = ""

    from app.main import create_app

    client = TestClient(create_app())
    response = client.get("/api/providers/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["collector"]["status"] in {"ready", "degraded"}
    assert payload["language_model"]["status"] == "degraded"
    assert payload["publisher"]["status"] == "degraded"
