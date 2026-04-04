import os

from fastapi.testclient import TestClient

from app.db.session import reset_db_state


def test_web_console_requires_login_when_auth_enabled() -> None:
    reset_db_state()
    os.environ["XHS_AUTH_ENABLED"] = "true"
    os.environ["XHS_OPERATOR_API_KEY"] = "web-secret"

    from app.main import create_app

    client = TestClient(create_app(), follow_redirects=False)

    response = client.get("/")
    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_web_console_login_sets_session_cookie() -> None:
    reset_db_state()
    os.environ["XHS_AUTH_ENABLED"] = "true"
    os.environ["XHS_OPERATOR_API_KEY"] = "web-secret"

    from app.main import create_app

    client = TestClient(create_app(), follow_redirects=False)

    login_response = client.post("/login", data={"operator_key": "web-secret"})
    assert login_response.status_code == 303
    assert "operator_session=" in login_response.headers["set-cookie"]

    session_cookie = login_response.cookies.get("operator_session")
    client.cookies.set("operator_session", session_cookie)
    dashboard_response = client.get("/")
    assert dashboard_response.status_code == 200
    assert "Xiaohongshu Content Platform" in dashboard_response.text
