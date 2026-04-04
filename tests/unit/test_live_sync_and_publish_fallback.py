import os

import httpx

from app.db.session import reset_db_state
from app.domain.models import DraftPayload


def test_api_publish_live_provider_falls_back_on_http_error(monkeypatch) -> None:
    reset_db_state()
    os.environ["XHS_XHS_PUBLISH_API_TOKEN"] = "publish-key"
    os.environ["XHS_XHS_PUBLISH_API_BASE"] = "https://publisher.example.com"

    from app.infrastructure.providers.publisher.api_live import XiaohongshuAPILiveProvider

    called = {"value": False}

    def boom(*args, **kwargs):
        called["value"] = True
        raise httpx.HTTPError("boom")

    monkeypatch.setattr(httpx.Client, "post", boom)
    provider = XiaohongshuAPILiveProvider()
    result = provider.publish(
        DraftPayload(
            title="测试发布",
            body="正文",
            tags=["#发布"],
            cta="评论区见",
            image_prompt="封面图",
            content_type="note",
        )
    )

    assert result.published_url
    assert called["value"] is True


def test_feishu_live_provider_falls_back_on_http_error(monkeypatch) -> None:
    reset_db_state()
    os.environ["XHS_FEISHU_APP_ID"] = "app-id"
    os.environ["XHS_FEISHU_APP_SECRET"] = "app-secret"

    from app.infrastructure.providers.feishu.live import FeishuLiveSyncProvider

    called = {"value": False}

    def boom(*args, **kwargs):
        called["value"] = True
        raise httpx.HTTPError("boom")

    monkeypatch.setattr(httpx.Client, "post", boom)
    provider = FeishuLiveSyncProvider()
    result = provider.sync("publish_job", {"title": "demo"})

    assert result["status"] == "synced"
    assert called["value"] is True
