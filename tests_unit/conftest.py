import os
from importlib import reload
from typing import Generator, MutableMapping, Any
from unittest.mock import AsyncMock, MagicMock

from databases.core import Transaction
from pytest_mock import MockerFixture
from pytest import MonkeyPatch

from app.db.database_config import create_transaction

import pytest
import structlog
from fastapi.testclient import TestClient

import app.config as config
import app.main as main
from tests_unit.test_util import async_gen_helper


@pytest.fixture
def test_client(
    monkeypatch: MonkeyPatch,
    disable_db_migrations: config.Settings,
    disable_db_connection: config.Settings,
    mock_create_transaction: AsyncMock,
) -> Generator[TestClient, None, None]:
    monkeypatch.setattr("app.db.database_config.engine", None)
    monkeypatch.setattr("app.db.database_config.async_engine", None)
    app = reload(main).app
    app.dependency_overrides[create_transaction] = mock_create_transaction
    with TestClient(app) as client:
        yield client
    reload(main)


@pytest.fixture
def mock_create_transaction(mocker: MockerFixture) -> AsyncMock:
    mock_produce_transaction: AsyncMock = mocker.patch(
        "app.db.database_dependencies.create_transaction"
    )
    mock_transaction = MagicMock(spec=Transaction)
    mock_produce_transaction.return_value = async_gen_helper([mock_transaction])
    return mock_transaction


@pytest.fixture
def disable_db_migrations(monkeypatch) -> Generator[config.Settings, None, None]:
    name = "APP_DB_MIGRATION_ENABLED"
    original_value = os.getenv(name)
    new_value = "False"
    # set new value, reload module and yield setting
    yield patch_env_var(monkeypatch, name, new_value)
    # reset to original value and reload module
    patch_env_var(monkeypatch, name, original_value)


@pytest.fixture
def disable_db_connection(monkeypatch) -> Generator[config.Settings, None, None]:
    name = "APP_DB_ENABLED"
    original_value = os.getenv(name)
    new_value = "False"
    # set new value, reload module and yield setting
    yield patch_env_var(monkeypatch, name, new_value)
    # reset to original value and reload module
    patch_env_var(monkeypatch, name, original_value)


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
def captured_logs() -> Generator[list[MutableMapping[str, Any]], None, None]:
    with structlog.testing.capture_logs() as captured_logs:
        yield captured_logs
        for log in captured_logs:
            print(log)
