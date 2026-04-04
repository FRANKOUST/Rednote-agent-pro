from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any, Callable

from app.application.external_worker import build_external_worker_adapter
from app.core.config import get_settings

_EXECUTOR = ThreadPoolExecutor(max_workers=4, thread_name_prefix="xhs-worker")


@dataclass(slots=True)
class InlineDispatcher:
    mode: str = "inline"

    def dispatch(self, fn: Callable[..., Any], *args, **kwargs):
        return fn(*args, **kwargs)


@dataclass(slots=True)
class BackgroundDispatcher:
    mode: str = "background"

    def dispatch(self, fn: Callable[..., Any], *args, **kwargs) -> Future:
        return _EXECUTOR.submit(fn, *args, **kwargs)


@dataclass(slots=True)
class QueuedDispatchHandle:
    status: str = "queued"


@dataclass(slots=True)
class WorkerStubDispatcher:
    mode: str = "worker_stub"

    def dispatch(self, fn: Callable[..., Any], *args, **kwargs) -> QueuedDispatchHandle:
        return QueuedDispatchHandle()


@dataclass(slots=True)
class ExternalWorkerDispatcher:
    mode: str = "external_worker"

    def dispatch(self, fn: Callable[..., Any], *args, **kwargs):
        adapter = build_external_worker_adapter()
        return adapter.enqueue(getattr(fn, "__name__", "task"), args, kwargs)


def build_dispatcher():
    settings = get_settings()
    if settings.task_mode == "external_worker":
        return ExternalWorkerDispatcher()
    if settings.task_mode == "worker_stub":
        return WorkerStubDispatcher()
    if settings.task_mode == "background":
        return BackgroundDispatcher()
    return InlineDispatcher()
