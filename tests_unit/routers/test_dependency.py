from unittest.mock import MagicMock, AsyncMock

import pytest
from assertpy import assert_that
from fastapi.testclient import TestClient
from httpx import Response
from pytest_mock import MockerFixture

from app.routers.dependency import Resp
from tests_unit.test_util import async_gen_helper

DEPENDENCIES_DIRECT_ENDPOINT = "/context/dependency/direct"
DEPENDENCIES_DIRECT_ASYNC_ENDPOINT = "/context/dependency/direct-async"


@pytest.fixture
def mock_get_value(mocker: MockerFixture) -> MagicMock:
    mock: MagicMock = mocker.patch("app.routers.dependency.get_value")
    return mock


@pytest.fixture
def mock_get_async(mocker: MockerFixture) -> AsyncMock:
    mock: AsyncMock = mocker.patch("app.routers.dependency.get_async")
    return mock


def test_read_direct_dependency_with_mock(
    mock_get_value: MagicMock,
    test_client: TestClient,
):
    mock_get_value.return_value = "test"

    response: Response = test_client.get(DEPENDENCIES_DIRECT_ENDPOINT)

    assert_that(response.status_code).is_equal_to(200)
    response_entity = Resp(**response.json())

    assert_that(response_entity.value).is_equal_to("test")


def test_read_direct_dependency(
    test_client: TestClient,
):
    response: Response = test_client.get(DEPENDENCIES_DIRECT_ENDPOINT)

    assert_that(response.status_code).is_equal_to(200)
    response_entity = Resp(**response.json())

    assert_that(response_entity.value).is_equal_to("prod")


def test_read_direct_async_dependency_with_mock(
    mock_get_async: AsyncMock,
    test_client: TestClient,
):
    mock_get_async.return_value = async_gen_helper(["test-async"])
    response: Response = test_client.get(DEPENDENCIES_DIRECT_ASYNC_ENDPOINT)

    assert_that(response.status_code).is_equal_to(200)
    response_entity = Resp(**response.json())

    assert_that(response_entity.value).is_equal_to("test-async")


def test_read_direct_async_dependency(
    test_client: TestClient,
):
    response: Response = test_client.get(DEPENDENCIES_DIRECT_ASYNC_ENDPOINT)

    assert_that(response.status_code).is_equal_to(200)
    response_entity = Resp(**response.json())

    assert_that(response_entity.value).is_equal_to("prod-async")
