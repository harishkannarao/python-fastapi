from typing import Any
from unittest.mock import AsyncMock

import pytest
from assertpy import assert_that
from fastapi import Response
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture

from app.model.customer import Customer


@pytest.fixture
def mock_execute(mocker: MockerFixture) -> AsyncMock:
    mock_execute: AsyncMock = mocker.patch("app.db.database_config.database.execute")
    return mock_execute


@pytest.fixture
def mock_execute_many(mocker: MockerFixture) -> AsyncMock:
    mock_execute_many: AsyncMock = mocker.patch(
        "app.db.database_config.database.execute_many"
    )
    return mock_execute_many


def test_customers_delete(mock_execute: AsyncMock, test_client: TestClient):
    initial_delete: Response = test_client.delete("/context/customers")
    assert_that(initial_delete.status_code).is_equal_to(204)

    assert len(mock_execute.call_args_list) == 1
    assert mock_execute.call_args.kwargs["query"] == "TRUNCATE TABLE CUSTOMERS"


def test_customers_insert(mock_execute_many: AsyncMock, test_client: TestClient):
    customer1 = Customer(first_name="fname1", last_name="lname1")
    customer2 = Customer(first_name="fname2", last_name="lname2")
    input_json = jsonable_encoder([customer1, customer2])
    response: Response = test_client.put("/context/customers", json=input_json)
    assert_that(response.status_code).is_equal_to(204)

    assert len(mock_execute_many.call_args_list) == 1
    assert_that(mock_execute_many.call_args.kwargs["query"]).is_equal_to(
        "INSERT INTO CUSTOMERS(FIRST_NAME, LAST_NAME) VALUES (:first_name, :last_name)"
    )
    inserted_rows: list[dict[str, Any]] = mock_execute_many.call_args.kwargs["values"]
    assert_that(inserted_rows).is_length(2)
    assert_that(inserted_rows).contains(jsonable_encoder(customer1))
    assert_that(inserted_rows).contains(jsonable_encoder(customer2))
