import os

import httpx

from app.db.session import reset_db_state
from app.domain.models import DraftPayload, SourcePostPayload


def test_openai_live_llm_falls_back_on_http_error(monkeypatch) -> None:
    reset_db_state()
    os.environ["XHS_OPENAI_API_KEY"] = "test-key"

    from app.infrastructure.providers.llm.openai_live import OpenAILiveLLMProvider

    called = {"value": False}

    def boom(*args, **kwargs):
        called["value"] = True
        raise httpx.HTTPError("boom")

    monkeypatch.setattr(httpx.Client, "post", boom)
    provider = OpenAILiveLLMProvider()
    result = provider.analyze(
        [
            SourcePostPayload(
                keyword="咖啡",
                title="咖啡 爆款",
                content="内容",
                likes=100,
                favorites=20,
                comments=10,
                author="demo",
                url="https://www.xiaohongshu.com/explore/demo",
                tags=["#咖啡"],
            )
        ]
    )

    assert result.summary
    assert called["value"] is True


def test_openai_live_image_falls_back_on_http_error(monkeypatch) -> None:
    reset_db_state()
    os.environ["XHS_OPENAI_API_KEY"] = "test-key"

    from app.infrastructure.providers.image.openai_live import OpenAILiveImageProvider

    called = {"value": False}

    def boom(*args, **kwargs):
        called["value"] = True
        raise httpx.HTTPError("boom")

    monkeypatch.setattr(httpx.Client, "post", boom)
    provider = OpenAILiveImageProvider()
    result = provider.generate(
        DraftPayload(
            title="测试标题",
            body="正文",
            tags=["#测试"],
            cta="评论区见",
            image_prompt="海报",
            content_type="note",
        )
    )

    assert result.path
    assert called["value"] is True
