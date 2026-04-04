import os

from app.db.session import reset_db_state


def test_inline_dispatcher_executes_immediately() -> None:
    reset_db_state()
    os.environ["XHS_TASK_MODE"] = "inline"

    from app.application.dispatcher import build_dispatcher

    marker: list[str] = []
    build_dispatcher().dispatch(lambda value: marker.append(value), "done")

    assert marker == ["done"]


def test_background_dispatcher_returns_future() -> None:
    reset_db_state()
    os.environ["XHS_TASK_MODE"] = "background"

    from app.application.dispatcher import build_dispatcher

    marker: list[str] = []
    future = build_dispatcher().dispatch(lambda value: marker.append(value), "done")
    future.result(timeout=2)

    assert marker == ["done"]


def test_worker_stub_dispatcher_returns_queued_handle_without_executing() -> None:
    reset_db_state()
    os.environ["XHS_TASK_MODE"] = "worker_stub"

    from app.application.dispatcher import build_dispatcher

    marker: list[str] = []
    handle = build_dispatcher().dispatch(lambda value: marker.append(value), "done")

    assert marker == []
    assert handle.status == "queued"
