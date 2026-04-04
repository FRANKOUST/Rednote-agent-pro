from __future__ import annotations

import json
import sys
from pathlib import Path

from app.application.factory import get_pipeline_service


def run_manifest(manifest_path: str) -> int:
    path = Path(manifest_path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["status"] = "running"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    task_name = payload.get("task_name")
    args = payload.get("args", [])
    try:
        if task_name == "execute_run":
            get_pipeline_service().execute_run(*args)
        payload["status"] = "completed"
    except Exception as exc:
        payload["status"] = "failed"
        payload["error"] = str(exc)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_manifest(sys.argv[1]))
