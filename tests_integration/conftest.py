import os
import time
from importlib import reload
from typing import Generator, Any, MutableMapping, AsyncGenerator

import pytest
import pytest_asyncio
from pytest import MonkeyPatch
import structlog
from assertpy import assert_that
from fastapi.testclient import TestClient
from sqlmodel import Session
from sqlmodel.ext.asyncio.session import AsyncSession
from tenacity import Retrying, stop_after_delay, wait_fixed
from testcontainers.core.container import DockerContainer
from pytest_httpserver.httpserver import HTTPServer

import app.config as config
import app.dao.customer_dao as customer_dao
import app.db.database_config as database_config
import app.main as main

DB_MODULES_TO_RELOAD = [database_config, customer_dao]


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
        time.sleep(0.5)
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
    mock_external_faq_server: HTTPServer,
    log_db_statements: config.Settings,
    change_postgres_db_host: config.Settings,
    change_postgres_db_port: config.Settings,
) -> Generator[TestClient, None, None]:
    app = reload(main).app
    with TestClient(app) as client:
        yield client
    reload(main)


@pytest.fixture
def mock_external_faq_server(
    monkeypatch: MonkeyPatch,
) -> Generator[HTTPServer, None, None]:
    with HTTPServer() as httpserver:
        test_url: str = f"http://{httpserver.host}:{httpserver.port}"
        monkeypatch.setattr(
            "app.routers.external_faq.settings.app_external_faq_api_base_url", test_url
        )
        yield httpserver


@pytest.fixture
def change_postgres_db_host(
    postgres_docker_container: DockerContainer, monkeypatch: MonkeyPatch
) -> Generator[config.Settings, None, None]:
    name = "APP_DB_HOST"
    original_value = os.getenv(name)
    new_value = postgres_docker_container.get_container_host_ip()
    # set new value, reload module and yield setting
    new_settings = patch_env_var(monkeypatch, name, new_value)
    for mod in DB_MODULES_TO_RELOAD:
        reload(mod)
    yield new_settings
    # reset to original value and reload module
    patch_env_var(monkeypatch, name, original_value)
    for mod in DB_MODULES_TO_RELOAD:
        reload(mod)


@pytest.fixture
def change_postgres_db_port(
    postgres_docker_container: DockerContainer, monkeypatch: MonkeyPatch
) -> Generator[config.Settings, None, None]:
    name = "APP_DB_PORT"
    original_value = os.getenv(name)
    new_value = str(postgres_docker_container.get_exposed_port(5432))
    # set new value, reload module and yield setting
    new_settings = patch_env_var(monkeypatch, name, new_value)
    for mod in DB_MODULES_TO_RELOAD:
        reload(mod)
    yield new_settings
    # reset to original value and reload module
    patch_env_var(monkeypatch, name, original_value)
    for mod in DB_MODULES_TO_RELOAD:
        reload(mod)


@pytest.fixture
def log_db_statements(
    postgres_docker_container: DockerContainer, monkeypatch: MonkeyPatch
) -> Generator[config.Settings, None, None]:
    name = "APP_DB_LOG_SQL"
    original_value = os.getenv(name)
    new_value = "True"
    # set new value, reload module and yield setting
    new_settings = patch_env_var(monkeypatch, name, new_value)
    for mod in DB_MODULES_TO_RELOAD:
        reload(mod)
    yield new_settings
    # reset to original value and reload module
    patch_env_var(monkeypatch, name, original_value)
    for mod in DB_MODULES_TO_RELOAD:
        reload(mod)


@pytest.fixture
def disable_open_api(
    monkeypatch: MonkeyPatch,
) -> Generator[config.Settings, None, None]:
    name = "APP_OPEN_API_URL"
    original_value = os.getenv(name)
    new_value = ""
    # set new value, reload module and yield setting
    yield patch_env_var(monkeypatch, name, new_value)
    # reset to original value and reload module
    patch_env_var(monkeypatch, name, original_value)


@pytest.fixture
def get_session(
    postgres_docker_container: DockerContainer, test_client: TestClient
) -> Generator[Session, Any, None]:
    from sqlmodel import Session, create_engine

    db_ip: str = postgres_docker_container.get_container_host_ip()
    db_port: str = str(postgres_docker_container.get_exposed_port(5432))
    database_url = (
        f"postgresql://superpassword:superpassword@{db_ip}:{db_port}/superpassword"
    )
    engine = create_engine(
        database_url,
        pool_size=10,
        max_overflow=10,
        echo=True,
        future=True,
    )
    with Session(engine) as session:
        yield session
        engine.dispose()


@pytest_asyncio.fixture
async def get_async_session(
    postgres_docker_container: DockerContainer, test_client: TestClient
) -> AsyncGenerator[AsyncSession, Any]:
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlmodel.ext.asyncio.session import AsyncSession

    db_ip: str = postgres_docker_container.get_container_host_ip()
    db_port: str = str(postgres_docker_container.get_exposed_port(5432))
    database_async_url = f"postgresql+asyncpg://superpassword:superpassword@{db_ip}:{db_port}/superpassword"
    async_engine = create_async_engine(
        database_async_url,
        pool_size=10,
        max_overflow=10,
        echo=True,
        future=True,
    )
    async with AsyncSession(async_engine) as session:
        yield session
        await async_engine.dispose()


def patch_env_var(
    monkeypatch: MonkeyPatch, name: str, value: str | None
) -> config.Settings:
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
