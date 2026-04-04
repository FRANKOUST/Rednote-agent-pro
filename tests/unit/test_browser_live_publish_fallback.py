import os

from app.db.session import reset_db_state
from app.domain.models import DraftPayload


def test_browser_live_publish_provider_falls_back_on_playwright_error(monkeypatch, tmp_path) -> None:
    reset_db_state()
    state_path = tmp_path / "state.json"
    state_path.write_text("{}", encoding="utf-8")
    os.environ["XHS_PLAYWRIGHT_STORAGE_STATE_PATH"] = str(state_path)

    from app.infrastructure.providers.publisher.browser_live import XiaohongshuBrowserLiveProvider

    monkeypatch.setattr(XiaohongshuBrowserLiveProvider, "_playwright_available", lambda self: True)
    monkeypatch.setattr(XiaohongshuBrowserLiveProvider, "_publish_with_playwright", lambda self, draft: (_ for _ in ()).throw(RuntimeError("fail")))

    result = XiaohongshuBrowserLiveProvider().publish(
        DraftPayload(
            title="浏览器发布",
            body="正文",
            tags=["#发布"],
            cta="评论",
            image_prompt="图",
            content_type="note",
        )
    )

    assert result.published_url
