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
