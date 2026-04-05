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

    def inspect(self, job_id: str) -> dict:
        ...

    def cancel(self, job_id: str) -> dict:
        ...

    def requeue(self, job_id: str) -> dict:
        ...


class FilesystemQueueWorkerAdapter:
    name = "filesystem-worker-adapter"

    def __init__(self) -> None:
        self.settings = get_settings()
        self.queue_dir = Path(self.settings.worker_queue_dir)
        self.dead_letter_dir = Path(self.settings.worker_dead_letter_dir)
        self.queue_dir.mkdir(parents=True, exist_ok=True)
        self.dead_letter_dir.mkdir(parents=True, exist_ok=True)

    def enqueue(self, task_name: str, args: tuple, kwargs: dict) -> ExternalWorkerHandle:
        job_id = uuid4().hex
        payload = {
            "job_id": job_id,
            "task_name": task_name,
            "args": list(args),
            "kwargs": kwargs,
            "run_id": args[0] if args else None,
            "status": "queued",
            "attempts": 0,
            "max_attempts": self.settings.worker_max_attempts,
            "dead_lettered": False,
        }
        (self.queue_dir / f"{job_id}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return ExternalWorkerHandle(status="queued", adapter=self.name, job_id=job_id)

    def inspect(self, job_id: str) -> dict:
        path = self._resolve_path(job_id)
        return json.loads(path.read_text(encoding="utf-8"))

    def cancel(self, job_id: str) -> dict:
        path = self._resolve_path(job_id)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["status"] = "cancelled"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return payload

    def requeue(self, job_id: str) -> dict:
        path = self._resolve_path(job_id)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["status"] = "queued"
        if path.parent == self.dead_letter_dir:
            path = self.queue_dir / path.name
            payload["dead_lettered"] = False
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return payload

    def dead_letter(self, job_id: str, payload: dict) -> dict:
        path = self.dead_letter_dir / f"{job_id}.json"
        payload["dead_lettered"] = True
        payload["status"] = "dead_letter"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        queue_path = self.queue_dir / f"{job_id}.json"
        if queue_path.exists():
            queue_path.unlink()
        return payload

    def _resolve_path(self, job_id: str) -> Path:
        queue = self.queue_dir / f"{job_id}.json"
        if queue.exists():
            return queue
        dead = self.dead_letter_dir / f"{job_id}.json"
        if dead.exists():
            return dead
        return queue


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

    def inspect(self, job_id: str) -> dict:
        return self.filesystem.inspect(job_id)

    def cancel(self, job_id: str) -> dict:
        return self.filesystem.cancel(job_id)

    def requeue(self, job_id: str) -> dict:
        return self.filesystem.requeue(job_id)


class FallbackWorkerAdapter:
    name = "fallback-worker-adapter"

    def __init__(self) -> None:
        self.filesystem = FilesystemQueueWorkerAdapter()

    def enqueue(self, task_name: str, args: tuple, kwargs: dict) -> ExternalWorkerHandle:
        return self.filesystem.enqueue(task_name, args, kwargs)

    def inspect(self, job_id: str) -> dict:
        return self.filesystem.inspect(job_id)

    def cancel(self, job_id: str) -> dict:
        return self.filesystem.cancel(job_id)

    def requeue(self, job_id: str) -> dict:
        return self.filesystem.requeue(job_id)


def build_external_worker_adapter() -> ExternalWorkerAdapter:
    settings = get_settings()
    if settings.worker_adapter_kind == "subprocess":
        return SubprocessQueueWorkerAdapter()
    if settings.worker_adapter_kind == "filesystem":
        return FilesystemQueueWorkerAdapter()
    return FallbackWorkerAdapter()
