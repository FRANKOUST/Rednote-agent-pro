from app.db.session import reset_db_state


def test_provider_registry_uses_mock_defaults() -> None:
    reset_db_state()

    from app.infrastructure.providers.registry import build_provider_registry

    registry = build_provider_registry()

    assert registry.collector.name == "mock-collector"
    assert registry.language_model.name == "mock-llm"
    assert registry.image.name == "mock-image"
    assert registry.publisher.name == "mock-publisher"
    assert registry.sync.name == "mock-feishu"


def test_provider_registry_can_select_scrapling_and_feishu_cli() -> None:
    import os

    reset_db_state()
    os.environ["XHS_DEFAULT_COLLECTOR_PROVIDER"] = "scrapling_xhs"
    os.environ["XHS_DEFAULT_SYNC_PROVIDER"] = "feishu_cli"

    from app.infrastructure.providers.registry import build_provider_registry

    registry = build_provider_registry()

    assert registry.collector.name == "scrapling-xhs-collector"
    assert registry.sync.name == "feishu-cli-sync"
