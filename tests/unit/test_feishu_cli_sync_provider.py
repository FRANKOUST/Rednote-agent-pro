import os
from pathlib import Path

from app.db.session import reset_db_state


def test_feishu_cli_sync_provider_builds_base_command(tmp_path: Path) -> None:
    reset_db_state()
    os.environ["XHS_FEISHU_CLI_BIN"] = "lark-cli"
    os.environ["XHS_FEISHU_SYNC_MODE"] = "base"
    os.environ["XHS_FEISHU_BASE_TOKEN"] = "base-token"
    os.environ["XHS_FEISHU_TABLE_ID"] = "tbl123"

    from app.infrastructure.providers.feishu.cli import FeishuCLISyncProvider

    provider = FeishuCLISyncProvider()
    command = provider.build_command("publish_job", tmp_path / "payload.json", dry_run=True)

    assert command[:4] == ["lark-cli", "--as", "user", "base"]
    assert "--table-id" in command
    assert "--dry-run" in command


def test_feishu_cli_sync_provider_returns_structured_dry_run_payload() -> None:
    reset_db_state()
    os.environ["XHS_FEISHU_CLI_DRY_RUN"] = "true"

    from app.infrastructure.providers.feishu.cli import FeishuCLISyncProvider

    result = FeishuCLISyncProvider().sync("publish_job", {"title": "demo"})

    assert result["status"] == "synced"
    assert result["dry_run"] is True
    assert result["diagnostics"]["mode"] == "dry_run"


def test_feishu_cli_sync_provider_parses_stdout_json() -> None:
    reset_db_state()

    from app.infrastructure.providers.feishu.cli import FeishuCLISyncProvider

    result = FeishuCLISyncProvider().parse_result_stdout('{"target":"feishu-cli","status":"synced"}')

    assert result["target"] == "feishu-cli"
    assert result["status"] == "synced"
