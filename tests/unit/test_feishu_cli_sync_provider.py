import os
from pathlib import Path

from app.db.session import reset_db_state


def test_feishu_cli_sync_provider_builds_crawled_command_and_payload(tmp_path: Path) -> None:
    reset_db_state()
    os.environ["XHS_FEISHU_CLI_BIN"] = "lark-cli"
    os.environ["XHS_FEISHU_SYNC_MODE"] = "base"
    os.environ["XHS_FEISHU_BASE_TOKEN"] = "base-token"
    os.environ["XHS_FEISHU_TABLE_ID"] = "tbl123"

    from app.infrastructure.providers.feishu.cli import FeishuCLISyncProvider

    provider = FeishuCLISyncProvider()
    payload = provider.build_payload("sync_crawled", {"title": "demo", "run_id": "run-1"}, dry_run=True)
    command = provider.build_command("sync_crawled", tmp_path / "payload.json", dry_run=True)

    assert payload["business_type"] == "sync_crawled"
    assert command[:4] == ["lark-cli", "--as", "user", "base"]
    assert "--dry-run" in command


def test_feishu_cli_sync_provider_returns_structured_dry_run_payload_for_generated_sync() -> None:
    reset_db_state()
    os.environ["XHS_FEISHU_CLI_DRY_RUN"] = "true"

    from app.infrastructure.providers.feishu.cli import FeishuCLISyncProvider

    result = FeishuCLISyncProvider().sync("sync_generated", {"title": "demo"})

    assert result["status"] == "synced"
    assert result["dry_run"] is True
    assert result["payload"]["business_type"] == "sync_generated"
    assert result["diagnostics"]["mode"] == "dry_run"


def test_feishu_cli_sync_provider_parses_stdout_json() -> None:
    reset_db_state()

    from app.infrastructure.providers.feishu.cli import FeishuCLISyncProvider

    result = FeishuCLISyncProvider().parse_result_stdout('{"target":"feishu-cli","status":"synced"}')

    assert result["target"] == "feishu-cli"
    assert result["status"] == "synced"
