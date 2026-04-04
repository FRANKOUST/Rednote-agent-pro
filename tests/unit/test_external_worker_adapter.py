import json
import os
from pathlib import Path
import subprocess

from app.db.session import reset_db_state


def test_external_worker_dispatcher_writes_job_manifest(tmp_path: Path) -> None:
    reset_db_state()
    os.environ["XHS_TASK_MODE"] = "external_worker"
    os.environ["XHS_WORKER_ADAPTER_KIND"] = "filesystem"
    os.environ["XHS_WORKER_QUEUE_DIR"] = str(tmp_path)

    from app.application.dispatcher import build_dispatcher

    handle = build_dispatcher().dispatch(lambda value: value, "done")

    assert handle.status == "queued"
    manifests = list(tmp_path.glob("*.json"))
    assert len(manifests) == 1
    payload = json.loads(manifests[0].read_text(encoding="utf-8"))
    assert payload["task_name"] == "<lambda>"
    assert payload["args"] == ["done"]


def test_unknown_worker_adapter_falls_back_to_stub_mode() -> None:
    reset_db_state()
    os.environ["XHS_TASK_MODE"] = "external_worker"
    os.environ["XHS_WORKER_ADAPTER_KIND"] = "unknown"

    from app.application.dispatcher import build_dispatcher

    handle = build_dispatcher().dispatch(lambda value: value, "done")

    assert handle.status == "queued"


def test_subprocess_worker_adapter_spawns_process(monkeypatch, tmp_path: Path) -> None:
    reset_db_state()
    os.environ["XHS_TASK_MODE"] = "external_worker"
    os.environ["XHS_WORKER_ADAPTER_KIND"] = "subprocess"
    os.environ["XHS_WORKER_QUEUE_DIR"] = str(tmp_path)
    called = {"value": False}

    class DummyProc:
        pass

    def fake_popen(*args, **kwargs):
        called["value"] = True
        return DummyProc()

    monkeypatch.setattr(subprocess, "Popen", fake_popen)

    from app.application.dispatcher import build_dispatcher

    handle = build_dispatcher().dispatch(lambda value: value, "done")

    assert handle.status == "queued"
    assert handle.adapter == "subprocess-worker-adapter"
    assert called["value"] is True
