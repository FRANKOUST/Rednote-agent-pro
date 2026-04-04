from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol
from uuid import uuid4

from app.core.config import get_settings


@dataclass(slots=True)
class ExternalWorkerHandle:
    status: str
    adapter: str
    job_id: str


class ExternalWorkerAdapter(Protocol):
    name: str

    def enqueue(self, task_name: str, args: tuple, kwargs: dict) -> ExternalWorkerHandle:
        ...


class FilesystemQueueWorkerAdapter:
    name = "filesystem-worker-adapter"

    def __init__(self) -> None:
        self.settings = get_settings()
        self.queue_dir = Path(self.settings.worker_queue_dir)
        self.queue_dir.mkdir(parents=True, exist_ok=True)

    def enqueue(self, task_name: str, args: tuple, kwargs: dict) -> ExternalWorkerHandle:
        job_id = uuid4().hex
        payload = {
            "job_id": job_id,
            "task_name": task_name,
            "args": list(args),
            "kwargs": kwargs,
        }
        (self.queue_dir / f"{job_id}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return ExternalWorkerHandle(status="queued", adapter=self.name, job_id=job_id)


class SubprocessQueueWorkerAdapter:
    name = "subprocess-worker-adapter"

    def __init__(self) -> None:
        self.settings = get_settings()
        self.filesystem = FilesystemQueueWorkerAdapter()

    def enqueue(self, task_name: str, args: tuple, kwargs: dict) -> ExternalWorkerHandle:
        handle = self.filesystem.enqueue(task_name, args, kwargs)
        manifest = Path(self.settings.worker_queue_dir) / f"{handle.job_id}.json"
        try:
            subprocess.Popen(
                [sys.executable, "-m", "app.application.worker_runner", str(manifest)],
                cwd=str(Path.cwd()),
                env=os.environ.copy(),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return ExternalWorkerHandle(status="queued", adapter=self.name, job_id=handle.job_id)
        except Exception:
            return ExternalWorkerHandle(status="queued", adapter=self.filesystem.name, job_id=handle.job_id)


def build_external_worker_adapter() -> ExternalWorkerAdapter:
    settings = get_settings()
    if settings.worker_adapter_kind == "subprocess":
        return SubprocessQueueWorkerAdapter()
    if settings.worker_adapter_kind == "filesystem":
        return FilesystemQueueWorkerAdapter()
    return FilesystemQueueWorkerAdapter()
