from __future__ import annotations

import json
import shutil
from pathlib import Path

from app.core.config import get_settings
from app.infrastructure.cli_runner import run_cli_command
from app.infrastructure.providers.feishu.mock import MockSyncProvider


class FeishuCLISyncProvider:
    name = "feishu-cli-sync"

    def __init__(self) -> None:
        self.settings = get_settings()
        self.mock = MockSyncProvider()
        self.last_run_metadata: dict = {}

    def sync(self, entity_type: str, payload: dict) -> dict:
        business_type = payload.get("business_type") or entity_type
        dry_run = bool(payload.get("dry_run", self.settings.feishu_cli_dry_run))
        payload_dir = Path("data/feishu_cli")
        payload_dir.mkdir(parents=True, exist_ok=True)
        payload_document = self.build_payload(business_type, payload, dry_run=dry_run)
        payload_path = payload_dir / f"{business_type}.json"
        payload_path.write_text(json.dumps(payload_document, ensure_ascii=False, indent=2), encoding="utf-8")
        command = self.build_command(business_type, payload_path, dry_run=dry_run)

        if dry_run:
            result = {
                "target": f"feishu-cli-{self.settings.feishu_sync_mode}-dry-run",
                "status": "synced",
                "entity_type": entity_type,
                "business_type": business_type,
                "payload": payload_document,
                "dry_run": True,
                "provider": self.name,
                "diagnostics": {"mode": "dry_run", "command": command},
            }
            self.last_run_metadata = result["diagnostics"]
            return result

        if shutil.which(self.settings.feishu_cli_bin) is None:
            fallback = self.mock.sync(entity_type, payload_document)
            fallback.update(
                {
                    "target": "feishu-cli-fallback",
                    "dry_run": True,
                    "provider": self.name,
                    "business_type": business_type,
                    "payload": payload_document,
                    "diagnostics": {"mode": "fallback", "reason": "cli_not_found", "command": command},
                }
            )
            self.last_run_metadata = fallback["diagnostics"]
            return fallback

        result = run_cli_command(
            command=command,
            cwd=str(Path.cwd()),
            timeout_seconds=self.settings.feishu_cli_timeout_seconds,
            max_retries=self.settings.feishu_cli_max_retries,
        )
        parsed = self.parse_result_stdout(result.stdout)
        if result.returncode != 0:
            fallback = self.mock.sync(entity_type, payload_document)
            fallback.update(
                {
                    "target": "feishu-cli-fallback",
                    "dry_run": True,
                    "provider": self.name,
                    "business_type": business_type,
                    "payload": payload_document,
                    "stderr": result.stderr,
                    "stdout": result.stdout,
                    "diagnostics": {
                        "mode": "fallback",
                        "reason": "cli_failed",
                        "command": command,
                        "timed_out": result.timed_out,
                        "attempts": result.attempts,
                    },
                }
            )
            self.last_run_metadata = fallback["diagnostics"]
            return fallback

        parsed.update(
            {
                "entity_type": entity_type,
                "business_type": business_type,
                "payload": payload_document,
                "provider": self.name,
                "dry_run": False,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "diagnostics": {
                    "mode": "live",
                    "command": command,
                    "attempts": result.attempts,
                    "timed_out": result.timed_out,
                },
            }
        )
        self.last_run_metadata = parsed["diagnostics"]
        return parsed

    def build_payload(self, entity_type: str, payload: dict, dry_run: bool) -> dict:
        business_type = payload.get("business_type") or entity_type
        mapping = self._load_field_mapping().get(business_type, {})
        fields = {}
        for source_key, target_key in mapping.items():
            if source_key in payload:
                fields[target_key] = payload[source_key]
        if not fields:
            fields = {key: value for key, value in payload.items() if key != "dry_run"}
        return {
            "entity_type": entity_type,
            "business_type": business_type,
            "mode": self.settings.feishu_sync_mode,
            "dry_run": dry_run,
            "records": [{"fields": fields}],
        }

    def build_command(self, entity_type: str, payload_path: Path, dry_run: bool = False) -> list[str]:
        command = [self.settings.feishu_cli_bin, "--as", self.settings.feishu_cli_as]
        if self.settings.feishu_sync_mode == "sheet":
            command += ["sheet", "append", "--token", self.settings.feishu_sheet_token, "--range", self.settings.feishu_sheet_range]
        else:
            command += ["base", "upsert", "--base-token", self.settings.feishu_base_token, "--table-id", self.settings.feishu_table_id]
        command += ["--payload-file", str(payload_path), "--entity-type", entity_type]
        if dry_run:
            command.append("--dry-run")
        return command

    @staticmethod
    def parse_result_stdout(stdout: str) -> dict:
        text = (stdout or "").strip()
        if not text:
            return {"target": "feishu-cli", "status": "synced"}
        try:
            return json.loads(text)
        except Exception:
            return {"target": "feishu-cli", "status": "synced", "raw_stdout": text}

    def health(self) -> dict:
        cli_available = shutil.which(self.settings.feishu_cli_bin) is not None
        mapping_exists = Path(self.settings.feishu_field_mapping_path).exists()
        if self.settings.feishu_cli_dry_run:
            status = "ready"
            reason = "dry-run sync path available"
        elif cli_available and mapping_exists:
            status = "ready"
            reason = "lark-cli and field mapping available"
        else:
            status = "degraded"
            reason = "missing lark-cli binary or field mapping"
        return {
            "status": status,
            "reason": reason,
            "cli_available": cli_available,
            "mapping_exists": mapping_exists,
            "mode": self.settings.feishu_sync_mode,
            "dry_run": self.settings.feishu_cli_dry_run,
        }

    def diagnostics(self) -> dict:
        return {
            "provider_type": "feishu_cli",
            "bin": self.settings.feishu_cli_bin,
            "as": self.settings.feishu_cli_as,
            "sync_mode": self.settings.feishu_sync_mode,
            "field_mapping_path": self.settings.feishu_field_mapping_path,
            "last_run": self.last_run_metadata,
        }

    def _load_field_mapping(self) -> dict:
        path = Path(self.settings.feishu_field_mapping_path)
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))
