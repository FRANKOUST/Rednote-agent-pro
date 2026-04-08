import os

from app.db.session import reset_db_state


def test_scrapling_provider_runs_two_phase_collection_and_filters_ads() -> None:
    reset_db_state()
    os.environ["XHS_SCRAPLING_FIXTURE_DIR"] = "./fixtures/scrapling"

    from app.infrastructure.providers.collector.scrapling_xhs import ScraplingXhsCollectorProvider

    provider = ScraplingXhsCollectorProvider()
    posts = provider.collect(
        {
            "keywords": ["咖啡"],
            "topic_words": ["咖啡"],
            "min_likes": 100,
            "min_favorites": 20,
            "min_comments": 5,
            "collection_type": "search",
            "dry_run": True,
        }
    )

    assert len(posts) >= 1
    assert all(post.content for post in posts)
    assert all(post.content_type == "image_text" for post in posts)
    assert provider.last_run_metadata["candidate_count"] >= provider.last_run_metadata["accepted_count"]
    assert provider.last_run_metadata["detail_hydrated_count"] >= provider.last_run_metadata["accepted_count"]
    assert provider.last_run_metadata["login_state"]["mode"] in {"storage_state", "cookie_fallback", "fixture"}


def test_scrapling_provider_parses_detail_fixture_with_reliable_metrics() -> None:
    reset_db_state()

    from app.infrastructure.providers.collector.scrapling_xhs import ScraplingXhsCollectorProvider

    provider = ScraplingXhsCollectorProvider()
    posts = provider.collect({"note_ids": ["detail-001"], "collection_type": "detail", "dry_run": True})

    assert len(posts) == 1
    assert posts[0].url.endswith("detail-001")
    assert posts[0].published_at
    assert posts[0].raw_metrics["detail_source"] in {"meta", "fixture", "detail_dom"}


def test_scrapling_provider_health_reports_login_material_status() -> None:
    reset_db_state()
    os.environ["XHS_SCRAPLING_MODE"] = "fixture"

    from app.infrastructure.providers.collector.scrapling_xhs import ScraplingXhsCollectorProvider

    health = ScraplingXhsCollectorProvider().health()

    assert health["status"] == "ready"
    assert "login" in health["reason"] or "fixture" in health["reason"]
