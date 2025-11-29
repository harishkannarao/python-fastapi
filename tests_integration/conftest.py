import os
from importlib import reload
from typing import Generator

import pytest
import structlog
from fastapi.testclient import TestClient

import app.config as config
import app.main as main


@pytest.fixture
def test_client() -> Generator[TestClient, None, None]:
    app = reload(main).app
    with TestClient(app) as client:
        yield client


@pytest.fixture
def disable_open_api(monkeypatch) -> Generator[config.Settings, None, None]:
    name = "APP_OPEN_API_URL"
    original_value = os.getenv(name)
    new_value = ""
    # set new value, reload module and yield setting
    yield patch_env_var(monkeypatch, name, new_value)
    # reset to original value and reload module
    patch_env_var(monkeypatch, name, original_value)


def patch_env_var(monkeypatch, name: str, value: str | None) -> config.Settings:
    if value is None:
        monkeypatch.delenv(name)
    else:
        monkeypatch.setenv(name, value)
    return reload(config).settings


@pytest.fixture
def captured_logs():
    with structlog.testing.capture_logs() as captured_logs:
        yield captured_logs
        for log in captured_logs:
            print(log)
