import os

from app.db.session import reset_db_state


def test_registry_can_select_safe_playwright_collector() -> None:
    reset_db_state()
    os.environ["XHS_DEFAULT_COLLECTOR_PROVIDER"] = "playwright"
    os.environ["XHS_PLAYWRIGHT_SAFE_MODE"] = "true"

    from app.infrastructure.providers.registry import build_provider_registry

    registry = build_provider_registry()

    assert registry.collector.name == "safe-playwright-collector"


def test_safe_playwright_collector_falls_back_without_real_browser_context() -> None:
    reset_db_state()
    os.environ["XHS_DEFAULT_COLLECTOR_PROVIDER"] = "playwright"
    os.environ["XHS_PLAYWRIGHT_SAFE_MODE"] = "true"
    os.environ["XHS_ENABLE_REAL_COLLECTOR"] = "false"

    from app.infrastructure.providers.registry import build_provider_registry

    collector = build_provider_registry().collector
    posts = collector.collect({"keywords": ["咖啡"], "min_likes": 10})

    assert len(posts) >= 1
    assert all(post.url.startswith("https://www.xiaohongshu.com/") for post in posts)


def test_safe_playwright_collector_falls_back_when_real_collection_errors(monkeypatch, tmp_path) -> None:
    reset_db_state()
    state_path = tmp_path / "state.json"
    state_path.write_text("{}", encoding="utf-8")
    os.environ["XHS_DEFAULT_COLLECTOR_PROVIDER"] = "playwright"
    os.environ["XHS_PLAYWRIGHT_SAFE_MODE"] = "true"
    os.environ["XHS_ENABLE_REAL_COLLECTOR"] = "true"
    os.environ["XHS_PLAYWRIGHT_STORAGE_STATE_PATH"] = str(state_path)

    from app.infrastructure.providers.collector.safe_playwright import SafePlaywrightCollectorProvider

    monkeypatch.setattr(SafePlaywrightCollectorProvider, "_playwright_available", lambda self: True)
    monkeypatch.setattr(SafePlaywrightCollectorProvider, "_collect_with_playwright", lambda self, payload: (_ for _ in ()).throw(RuntimeError("fail")))

    posts = SafePlaywrightCollectorProvider().collect({"keywords": ["咖啡"]})

    assert len(posts) >= 1
