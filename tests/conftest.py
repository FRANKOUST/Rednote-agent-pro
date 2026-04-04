import os
import sys
from pathlib import Path

import pytest

from app.db.session import reset_db_state


@pytest.fixture(autouse=True)
def isolate_test_database(tmp_path: Path) -> None:
    reset_db_state()
    for module_name in list(sys.modules.keys()):
        if module_name == "app.main" or module_name.startswith("app.interfaces") or module_name.startswith("app.application.factory"):
            sys.modules.pop(module_name, None)
    os.environ["XHS_DATABASE_URL"] = f"sqlite:///{tmp_path / 'app.db'}"
    os.environ["XHS_MEDIA_DIR"] = str(tmp_path / "media")
    os.environ["XHS_TASK_MODE"] = "inline"
    os.environ["XHS_ALLOW_AUTO_PUBLISH"] = "false"
    os.environ["XHS_DEFAULT_COLLECTOR_PROVIDER"] = "mock"
    os.environ["XHS_DEFAULT_MODEL_PROVIDER"] = "mock"
    os.environ["XHS_DEFAULT_IMAGE_PROVIDER"] = "mock"
    os.environ["XHS_DEFAULT_PUBLISH_PROVIDER"] = "mock"
    os.environ["XHS_DEFAULT_SYNC_PROVIDER"] = "mock"
    os.environ["XHS_ENABLE_REAL_COLLECTOR"] = "false"
    os.environ["XHS_ENABLE_REAL_MODEL_PROVIDER"] = "false"
    os.environ["XHS_ENABLE_REAL_IMAGE_PROVIDER"] = "false"
    os.environ["XHS_ENABLE_REAL_PUBLISH_PROVIDER"] = "false"
    os.environ["XHS_ENABLE_REAL_SYNC_PROVIDER"] = "false"
    os.environ["XHS_AUTH_ENABLED"] = "false"
    os.environ["XHS_OPERATOR_API_KEY"] = ""
    yield
    reset_db_state()
