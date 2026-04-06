import os

from app.db.session import reset_db_state


def test_scrapling_provider_parses_search_fixture() -> None:
    reset_db_state()
    os.environ["XHS_SCRAPLING_FIXTURE_DIR"] = "./fixtures/scrapling"

    from app.infrastructure.providers.collector.scrapling_xhs import ScraplingXhsCollectorProvider

    provider = ScraplingXhsCollectorProvider()
    posts = provider.collect({"keywords": ["咖啡"], "collection_type": "search", "dry_run": True})

    assert len(posts) == 2
    assert posts[0].title
    assert posts[0].raw_metrics["collector_mode"] == "fixture"
    assert provider.last_run_metadata["mode"] == "fixture"


def test_scrapling_provider_parses_detail_fixture() -> None:
    reset_db_state()

    from app.infrastructure.providers.collector.scrapling_xhs import ScraplingXhsCollectorProvider

    provider = ScraplingXhsCollectorProvider()
    posts = provider.collect({"note_ids": ["detail-001"], "collection_type": "detail", "dry_run": True})

    assert len(posts) == 1
    assert posts[0].url.endswith("detail-001")
    assert posts[0].raw_metrics["collection_type"] == "detail"


def test_scrapling_provider_health_reports_fixture_mode_ready() -> None:
    reset_db_state()
    os.environ["XHS_SCRAPLING_MODE"] = "fixture"

    from app.infrastructure.providers.collector.scrapling_xhs import ScraplingXhsCollectorProvider

    health = ScraplingXhsCollectorProvider().health()

    assert health["status"] == "ready"
