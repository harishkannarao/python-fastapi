import os
from importlib import reload
from typing import Generator, Any, MutableMapping
from testcontainers.postgres import PostgresContainer

import pytest
import structlog
from fastapi.testclient import TestClient

import app.config as config
import app.main as main


@pytest.fixture(scope="session")
def postgres_container() -> Generator[PostgresContainer, None, None]:
    with PostgresContainer(image="postgres:18-alpine") as postgres:
        yield postgres


@pytest.fixture
def test_client(
    disable_db_migrations: config.Settings,
    postgres_container: PostgresContainer,
) -> Generator[TestClient, None, None]:
    print(postgres_container.get_container_host_ip())
    print(postgres_container.get_exposed_port(5432))
    print(postgres_container.username)
    print(postgres_container.password)
    print(postgres_container.dbname)
    app = reload(main).app
    with TestClient(app) as client:
        yield client


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
