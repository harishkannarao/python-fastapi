import os
from importlib import reload
from typing import Generator, Any, MutableMapping

import pytest
import structlog
from assertpy import assert_that
from fastapi.testclient import TestClient
from tenacity import Retrying, stop_after_delay, wait_fixed
from testcontainers.core.container import DockerContainer

import app.config as config
import app.db_schema_migrations.yoyo_migration as yoyo_migration
import app.main as main


@pytest.fixture(scope="session")
def postgres_docker_container() -> Generator[DockerContainer, None, None]:
    env_vars: dict[str, str] = {
        "POSTGRES_USER": "myuser",
        "POSTGRES_PASSWORD": "superpassword",
    }
    with DockerContainer(
        image="public.ecr.aws/docker/library/postgres:18-alpine",
        env=env_vars,
        ports=[5432],
    ) as container:
        # wait for the postgres server to start
        for attempt in Retrying(
            stop=stop_after_delay(10), wait=wait_fixed(0.5), reraise=True
        ):
            with attempt:
                stdout, stderr = container.get_logs()
                all_logs = stdout.decode("utf-8") + stderr.decode("utf-8")
                assert_that(all_logs).contains("server started")
        yield container


@pytest.fixture
def test_client(
    change_posgtres_db_host: config.Settings,
    change_posgtres_db_port: config.Settings,
) -> Generator[TestClient, None, None]:
    app = reload(main).app
    with TestClient(app) as client:
        yield client


@pytest.fixture
def change_posgtres_db_host(
    postgres_docker_container: DockerContainer, monkeypatch
) -> Generator[config.Settings, None, None]:
    name = "APP_DB_HOST"
    original_value = os.getenv(name)
    new_value = postgres_docker_container.get_container_host_ip()
    # set new value, reload module and yield setting
    new_settings = patch_env_var(monkeypatch, name, new_value)
    reload(yoyo_migration)
    yield new_settings
    # reset to original value and reload module
    patch_env_var(monkeypatch, name, original_value)


@pytest.fixture
def change_posgtres_db_port(
    postgres_docker_container: DockerContainer, monkeypatch
) -> Generator[config.Settings, None, None]:
    name = "APP_DB_PORT"
    original_value = os.getenv(name)
    new_value = str(postgres_docker_container.get_exposed_port(5432))
    # set new value, reload module and yield setting
    new_settings = patch_env_var(monkeypatch, name, new_value)
    reload(yoyo_migration)
    yield new_settings
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
