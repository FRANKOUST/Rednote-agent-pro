from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Xiaohongshu Content Platform"
    environment: str = "development"
    database_url: str = "sqlite:///./data/app.db"
    media_dir: str = "./data/media"
    task_mode: str = "inline"
    allow_auto_publish: bool = False
    default_publish_provider: str = "mock"
    default_sync_provider: str = "mock"
    default_model_provider: str = "mock"
    default_image_provider: str = "mock"
    default_collector_provider: str = "mock"
    enable_real_collector: bool = False
    enable_real_model_provider: bool = False
    enable_real_image_provider: bool = False
    enable_real_publish_provider: bool = False
    enable_real_sync_provider: bool = False
    allow_live_publish: bool = False
    playwright_safe_mode: bool = True
    playwright_storage_state_path: str = "./data/playwright/state.json"
    collector_max_pages: int = 3
    collector_action_delay_ms: int = 750
    openai_api_key: str = ""
    openai_model_name: str = "gpt-4.1-mini"
    openai_image_model: str = "gpt-image-1"
    feishu_app_id: str = ""
    feishu_app_secret: str = ""
    xhs_publish_api_base: str = ""
    xhs_publish_api_token: str = ""
    auth_enabled: bool = False
    operator_api_key: str = ""
    viewer_api_key: str = ""
    reviewer_api_key: str = ""
    admin_api_key: str = ""
    operator_session_cookie_name: str = "operator_session"
    request_id_header_name: str = "X-Request-ID"
    log_level: str = "INFO"
    worker_adapter_kind: str = "subprocess"
    worker_queue_dir: str = "./data/worker-queue"
    worker_dead_letter_dir: str = "./data/worker-dead-letter"
    worker_max_attempts: int = 3
    team_slug: str = Field(default="internal-team")

    model_config = SettingsConfigDict(env_prefix="XHS_", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    Path(settings.media_dir).mkdir(parents=True, exist_ok=True)
    return settings
