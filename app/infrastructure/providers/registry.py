from __future__ import annotations

from dataclasses import dataclass

from app.core.config import get_settings
from app.infrastructure.providers.collector.mock import MockCollectorProvider
from app.infrastructure.providers.collector.safe_playwright import SafePlaywrightCollectorProvider
from app.infrastructure.providers.collector.scrapling_xhs import ScraplingXhsCollectorProvider
from app.infrastructure.providers.feishu.cli import FeishuCLISyncProvider
from app.infrastructure.providers.feishu.mock import MockSyncProvider
from app.infrastructure.providers.feishu.safe_stub import FeishuSafeStubProvider
from app.infrastructure.providers.image.mock import MockImageProvider
from app.infrastructure.providers.image.openai_compatible import OpenAICompatibleImageProvider
from app.infrastructure.providers.image.openai_safe_stub import OpenAICompatibleSafeImageStubProvider
from app.infrastructure.providers.llm.custom_model_router import CustomModelRouterProvider
from app.infrastructure.providers.llm.mock import MockLanguageModelProvider
from app.infrastructure.providers.llm.openai_compatible import OpenAICompatibleLLMProvider
from app.infrastructure.providers.llm.openai_safe_stub import OpenAICompatibleSafeLLMStubProvider
from app.infrastructure.providers.publisher.api_live import XiaohongshuAPILiveProvider
from app.infrastructure.providers.publisher.api_safe_stub import XiaohongshuAPISafeStubProvider
from app.infrastructure.providers.publisher.browser_live import XiaohongshuBrowserLiveProvider
from app.infrastructure.providers.publisher.browser_safe_stub import XiaohongshuBrowserSafeStubProvider
from app.infrastructure.providers.publisher.mock import MockPublisherProvider


@dataclass(slots=True)
class ProviderRegistry:
    collector: object
    language_model: object
    image: object
    publisher: object
    sync: object


_COLLECTORS = {
    "mock": MockCollectorProvider,
    "playwright": SafePlaywrightCollectorProvider,
    "scrapling_xhs": ScraplingXhsCollectorProvider,
    "mediacrawler_xhs": ScraplingXhsCollectorProvider,
}

_LANGUAGE_MODELS = {
    "mock": MockLanguageModelProvider,
    "openai": OpenAICompatibleLLMProvider,
    "openai_compatible": OpenAICompatibleLLMProvider,
    "custom_model_router": CustomModelRouterProvider,
    "openai_safe_stub": OpenAICompatibleSafeLLMStubProvider,
}

_IMAGE_MODELS = {
    "mock": MockImageProvider,
    "openai": OpenAICompatibleImageProvider,
    "openai_compatible": OpenAICompatibleImageProvider,
    "openai_safe_stub": OpenAICompatibleSafeImageStubProvider,
}

_SYNC_PROVIDERS = {
    "mock": MockSyncProvider,
    "feishu": FeishuCLISyncProvider,
    "feishu_cli": FeishuCLISyncProvider,
    "feishu_safe_stub": FeishuSafeStubProvider,
}


def _select_publish_provider(settings):
    if settings.default_publish_provider == "api":
        if settings.enable_real_publish_provider and settings.xhs_publish_api_token and settings.xhs_publish_api_base:
            return XiaohongshuAPILiveProvider
        return XiaohongshuAPISafeStubProvider
    if settings.default_publish_provider == "browser":
        if settings.enable_real_publish_provider and settings.playwright_storage_state_path:
            return XiaohongshuBrowserLiveProvider
        return XiaohongshuBrowserSafeStubProvider
    return MockPublisherProvider


def build_provider_registry() -> ProviderRegistry:
    settings = get_settings()
    collector_cls = _COLLECTORS.get(settings.default_collector_provider, ScraplingXhsCollectorProvider)
    llm_cls = _LANGUAGE_MODELS.get(settings.default_model_provider, CustomModelRouterProvider)
    image_cls = _IMAGE_MODELS.get(settings.default_image_provider, MockImageProvider)
    sync_cls = _SYNC_PROVIDERS.get(settings.default_sync_provider, FeishuCLISyncProvider)

    return ProviderRegistry(
        collector=collector_cls(),
        language_model=llm_cls(),
        image=image_cls(),
        publisher=_select_publish_provider(settings)(),
        sync=sync_cls(),
    )
