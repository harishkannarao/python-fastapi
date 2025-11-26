import os
from importlib import reload
from typing import Generator

import pytest
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
    original_value = os.getenv("APP_OPEN_API_URL")
    monkeypatch.setenv("APP_OPEN_API_URL", "")
    yield reload(config).settings
    if original_value is None:
        monkeypatch.delenv("APP_OPEN_API_URL")
    else:
        monkeypatch.setenv("APP_OPEN_API_URL", original_value)
    reload(config)
