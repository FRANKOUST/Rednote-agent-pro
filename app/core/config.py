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
    default_sync_provider: str = "feishu_cli"
    default_model_provider: str = "custom_model_router"
    default_image_provider: str = "mock"
    default_collector_provider: str = "scrapling_xhs"
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

    scrapling_mode: str = "fixture"
    scrapling_timeout_seconds: int = 30
    scrapling_headless: bool = True
    scrapling_network_idle: bool = True
    scrapling_adaptive_selectors: bool = True
    scrapling_max_retries: int = 2
    scrapling_concurrency: int = 1
    scrapling_user_agent: str = ""
    scrapling_cookies_path: str = "./data/scrapling/cookies.json"
    scrapling_storage_state_path: str = "./data/scrapling/storage_state.json"
    scrapling_keywords_file: str = "./data/collector/keywords.txt"
    scrapling_note_ids_file: str = "./data/collector/note_ids.txt"
    scrapling_fixture_dir: str = "./fixtures/scrapling"

    feishu_cli_bin: str = "lark-cli"
    feishu_cli_as: str = "user"
    feishu_sync_mode: str = "base"
    feishu_base_token: str = ""
    feishu_table_id: str = ""
    feishu_sheet_token: str = ""
    feishu_sheet_range: str = ""
    feishu_cli_timeout_seconds: int = 60
    feishu_cli_max_retries: int = 2
    feishu_cli_dry_run: bool = True
    feishu_field_mapping_path: str = "./config/feishu_field_mapping.json"

    model_api_key: str = ""
    model_base_url: str = "https://api.openai.com/v1"
    model_name: str = "gpt-4.1-mini"
    model_timeout_seconds: int = 60
    model_max_retries: int = 2
    model_temperature: float = 0.2

    image_model_provider: str = "mock"
    image_model_api_key: str = ""
    image_model_base_url: str = "https://api.openai.com/v1"
    image_model_name: str = "gpt-image-1"
    image_model_timeout_seconds: int = 60
    image_model_max_retries: int = 2

    # Backward-compatible aliases kept only as fallbacks while operators migrate.
    openai_api_key: str = ""
    openai_model_name: str = "gpt-4.1-mini"
    openai_image_model: str = "gpt-image-1"

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

    @property
    def resolved_model_api_key(self) -> str:
        return self.model_api_key or self.openai_api_key

    @property
    def resolved_model_base_url(self) -> str:
        return (self.model_base_url or "https://api.openai.com/v1").rstrip("/")

    @property
    def resolved_model_name(self) -> str:
        return self.model_name or self.openai_model_name

    @property
    def resolved_image_provider(self) -> str:
        return self.image_model_provider or self.default_image_provider

    @property
    def resolved_image_api_key(self) -> str:
        return self.image_model_api_key or self.resolved_model_api_key

    @property
    def resolved_image_base_url(self) -> str:
        return (self.image_model_base_url or self.resolved_model_base_url).rstrip("/")

    @property
    def resolved_image_model_name(self) -> str:
        return self.image_model_name or self.openai_image_model


def _ensure_parent(path: str) -> None:
    if path:
        Path(path).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    Path(settings.media_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.worker_queue_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.worker_dead_letter_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.scrapling_fixture_dir).mkdir(parents=True, exist_ok=True)
    _ensure_parent(settings.playwright_storage_state_path)
    _ensure_parent(settings.scrapling_cookies_path)
    _ensure_parent(settings.scrapling_storage_state_path)
    _ensure_parent(settings.scrapling_keywords_file)
    _ensure_parent(settings.scrapling_note_ids_file)
    _ensure_parent(settings.feishu_field_mapping_path)
    return settings
