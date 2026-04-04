import os

from app.db.session import reset_db_state


def test_registry_can_wire_safe_real_provider_stubs() -> None:
    reset_db_state()
    os.environ["XHS_DEFAULT_MODEL_PROVIDER"] = "openai"
    os.environ["XHS_DEFAULT_IMAGE_PROVIDER"] = "openai"
    os.environ["XHS_DEFAULT_PUBLISH_PROVIDER"] = "api"
    os.environ["XHS_DEFAULT_SYNC_PROVIDER"] = "feishu"
    os.environ["XHS_ENABLE_REAL_MODEL_PROVIDER"] = "false"
    os.environ["XHS_ENABLE_REAL_IMAGE_PROVIDER"] = "false"
    os.environ["XHS_ENABLE_REAL_PUBLISH_PROVIDER"] = "false"
    os.environ["XHS_ENABLE_REAL_SYNC_PROVIDER"] = "false"

    from app.infrastructure.providers.registry import build_provider_registry

    registry = build_provider_registry()

    assert registry.language_model.name == "openai-safe-llm-stub"
    assert registry.image.name == "openai-safe-image-stub"
    assert registry.publisher.name == "xhs-api-safe-stub"
    assert registry.sync.name == "feishu-safe-stub"
