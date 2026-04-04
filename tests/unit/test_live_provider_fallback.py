import os

from app.db.session import reset_db_state


def test_live_provider_flags_without_credentials_fall_back_to_safe_stubs() -> None:
    reset_db_state()
    os.environ["XHS_DEFAULT_MODEL_PROVIDER"] = "openai"
    os.environ["XHS_DEFAULT_IMAGE_PROVIDER"] = "openai"
    os.environ["XHS_DEFAULT_PUBLISH_PROVIDER"] = "api"
    os.environ["XHS_DEFAULT_SYNC_PROVIDER"] = "feishu"
    os.environ["XHS_ENABLE_REAL_MODEL_PROVIDER"] = "true"
    os.environ["XHS_ENABLE_REAL_IMAGE_PROVIDER"] = "true"
    os.environ["XHS_ENABLE_REAL_PUBLISH_PROVIDER"] = "true"
    os.environ["XHS_ENABLE_REAL_SYNC_PROVIDER"] = "true"
    os.environ["XHS_OPENAI_API_KEY"] = ""
    os.environ["XHS_XHS_PUBLISH_API_TOKEN"] = ""
    os.environ["XHS_FEISHU_APP_ID"] = ""
    os.environ["XHS_FEISHU_APP_SECRET"] = ""

    from app.infrastructure.providers.registry import build_provider_registry

    registry = build_provider_registry()

    assert registry.language_model.name == "openai-safe-llm-stub"
    assert registry.image.name == "openai-safe-image-stub"
    assert registry.publisher.name == "xhs-api-safe-stub"
    assert registry.sync.name == "feishu-safe-stub"


def test_live_provider_flags_with_credentials_select_live_adapters() -> None:
    reset_db_state()
    os.environ["XHS_DEFAULT_MODEL_PROVIDER"] = "openai"
    os.environ["XHS_DEFAULT_IMAGE_PROVIDER"] = "openai"
    os.environ["XHS_DEFAULT_PUBLISH_PROVIDER"] = "api"
    os.environ["XHS_DEFAULT_SYNC_PROVIDER"] = "feishu"
    os.environ["XHS_ENABLE_REAL_MODEL_PROVIDER"] = "true"
    os.environ["XHS_ENABLE_REAL_IMAGE_PROVIDER"] = "true"
    os.environ["XHS_ENABLE_REAL_PUBLISH_PROVIDER"] = "true"
    os.environ["XHS_ENABLE_REAL_SYNC_PROVIDER"] = "true"
    os.environ["XHS_OPENAI_API_KEY"] = "test-key"
    os.environ["XHS_XHS_PUBLISH_API_TOKEN"] = "publish-key"
    os.environ["XHS_XHS_PUBLISH_API_BASE"] = "https://publisher.example.com"
    os.environ["XHS_FEISHU_APP_ID"] = "app-id"
    os.environ["XHS_FEISHU_APP_SECRET"] = "app-secret"

    from app.infrastructure.providers.registry import build_provider_registry

    registry = build_provider_registry()

    assert registry.language_model.name == "openai-live-llm"
    assert registry.image.name == "openai-live-image"
    assert registry.publisher.name == "xhs-api-live-publisher"
    assert registry.sync.name == "feishu-live-sync"


def test_browser_publish_provider_can_select_live_adapter_when_enabled(tmp_path) -> None:
    reset_db_state()
    state_path = tmp_path / "state.json"
    state_path.write_text("{}", encoding="utf-8")
    os.environ["XHS_DEFAULT_PUBLISH_PROVIDER"] = "browser"
    os.environ["XHS_ENABLE_REAL_PUBLISH_PROVIDER"] = "true"
    os.environ["XHS_PLAYWRIGHT_STORAGE_STATE_PATH"] = str(state_path)

    from app.infrastructure.providers.registry import build_provider_registry

    registry = build_provider_registry()

    assert registry.publisher.name == "xhs-browser-live-publisher"
