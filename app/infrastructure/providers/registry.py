from __future__ import annotations

from dataclasses import dataclass

from app.core.config import get_settings
from app.infrastructure.providers.collector.mock import MockCollectorProvider
from app.infrastructure.providers.collector.safe_playwright import SafePlaywrightCollectorProvider
from app.infrastructure.providers.feishu.live import FeishuLiveSyncProvider
from app.infrastructure.providers.feishu.mock import MockSyncProvider
from app.infrastructure.providers.feishu.safe_stub import FeishuSafeStubProvider
from app.infrastructure.providers.image.openai_live import OpenAILiveImageProvider
from app.infrastructure.providers.image.mock import MockImageProvider
from app.infrastructure.providers.image.openai_safe_stub import OpenAISafeImageStubProvider
from app.infrastructure.providers.llm.openai_live import OpenAILiveLLMProvider
from app.infrastructure.providers.llm.mock import MockLanguageModelProvider
from app.infrastructure.providers.llm.openai_safe_stub import OpenAISafeLLMStubProvider
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


def _select_language_model_provider(settings):
    if settings.default_model_provider == "openai":
        if settings.enable_real_model_provider and settings.openai_api_key:
            return OpenAILiveLLMProvider
        return OpenAISafeLLMStubProvider
    return MockLanguageModelProvider


def _select_image_provider(settings):
    if settings.default_image_provider == "openai":
        if settings.enable_real_image_provider and settings.openai_api_key:
            return OpenAILiveImageProvider
        return OpenAISafeImageStubProvider
    return MockImageProvider


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


def _select_sync_provider(settings):
    if settings.default_sync_provider == "feishu":
        if settings.enable_real_sync_provider and settings.feishu_app_id and settings.feishu_app_secret:
            return FeishuLiveSyncProvider
        return FeishuSafeStubProvider
    return MockSyncProvider


def build_provider_registry() -> ProviderRegistry:
    settings = get_settings()

    collectors = {"mock": MockCollectorProvider, "playwright": SafePlaywrightCollectorProvider}

    return ProviderRegistry(
        collector=collectors[settings.default_collector_provider](),
        language_model=_select_language_model_provider(settings)(),
        image=_select_image_provider(settings)(),
        publisher=_select_publish_provider(settings)(),
        sync=_select_sync_provider(settings)(),
    )
