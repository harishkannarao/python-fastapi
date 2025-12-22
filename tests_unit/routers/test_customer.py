from unittest.mock import AsyncMock

import pytest
from assertpy import assert_that
from fastapi import Response
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture


@pytest.fixture
def mock_database_execute(mocker: MockerFixture) -> AsyncMock:
    mock_execute: AsyncMock = mocker.patch("app.db.database_config.database.execute")
    return mock_execute


def test_customers_insert_read_delete(
    mock_database_execute: AsyncMock, test_client: TestClient
):
    initial_delete: Response = test_client.delete("/context/customers")
    assert_that(initial_delete.status_code).is_equal_to(204)
