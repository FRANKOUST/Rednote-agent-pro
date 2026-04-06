import os

from app.db.session import reset_db_state


def test_provider_registry_selects_scrapling_feishu_cli_and_custom_router() -> None:
    reset_db_state()
    os.environ["XHS_DEFAULT_COLLECTOR_PROVIDER"] = "scrapling_xhs"
    os.environ["XHS_DEFAULT_SYNC_PROVIDER"] = "feishu_cli"
    os.environ["XHS_DEFAULT_MODEL_PROVIDER"] = "custom_model_router"
    os.environ["XHS_DEFAULT_IMAGE_PROVIDER"] = "openai_compatible"

    from app.infrastructure.providers.registry import build_provider_registry

    registry = build_provider_registry()

    assert registry.collector.name == "scrapling-xhs-collector"
    assert registry.sync.name == "feishu-cli-sync"
    assert registry.language_model.name == "custom-model-router"
    assert registry.image.name == "openai-compatible-image"


def test_model_provider_resolves_openai_compatible_alias() -> None:
    reset_db_state()
    os.environ["XHS_DEFAULT_MODEL_PROVIDER"] = "openai_compatible"

    from app.infrastructure.providers.registry import build_provider_registry

    registry = build_provider_registry()

    assert registry.language_model.name == "openai-compatible-llm"
