import os
from pathlib import Path

from app.db.session import reset_db_state


def test_safe_playwright_collector_falls_back_without_real_browser_context() -> None:
    reset_db_state()
    os.environ["XHS_DEFAULT_COLLECTOR_PROVIDER"] = "playwright"
    os.environ["XHS_ENABLE_REAL_COLLECTOR"] = "false"

    from app.infrastructure.providers.registry import build_provider_registry

    collector = build_provider_registry().collector
    posts = collector.collect({"keywords": ["咖啡"], "topic_words": ["咖啡"], "min_likes": 10})

    assert len(posts) >= 1
    assert collector.last_run_metadata["login_state"]["mode"] in {"disabled", "missing_storage_state", "fallback"}


def test_safe_playwright_collector_reports_storage_state_reuse(monkeypatch, tmp_path: Path) -> None:
    reset_db_state()
    state_path = tmp_path / "state.json"
    state_path.write_text("{}", encoding="utf-8")
    os.environ["XHS_DEFAULT_COLLECTOR_PROVIDER"] = "playwright"
    os.environ["XHS_ENABLE_REAL_COLLECTOR"] = "true"
    os.environ["XHS_PLAYWRIGHT_STORAGE_STATE_PATH"] = str(state_path)

    from app.infrastructure.providers.collector.safe_playwright import SafePlaywrightCollectorProvider

    monkeypatch.setattr(SafePlaywrightCollectorProvider, "_playwright_available", lambda self: False)

    collector = SafePlaywrightCollectorProvider()
    collector.collect({"keywords": ["咖啡"], "topic_words": ["咖啡"]})

    assert collector.last_run_metadata["login_state"]["storage_state_path"] == str(state_path)
