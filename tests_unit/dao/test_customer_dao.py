from typing import Any
from unittest.mock import AsyncMock

import pytest
from assertpy import assert_that
from fastapi.encoders import jsonable_encoder
from pytest_mock import MockerFixture
from deepdiff import DeepDiff
from app.dao import customer_dao
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


@pytest.fixture
def mock_fetch_all(mocker: MockerFixture) -> AsyncMock:
    mock_fetch_all: AsyncMock = mocker.patch(
        "app.db.database_config.database.fetch_all"
    )
    return mock_fetch_all


@pytest.mark.asyncio
async def test_customers_delete(mock_execute: AsyncMock):
    await customer_dao.delete_all_customers()

    assert len(mock_execute.call_args_list) == 1
    assert mock_execute.call_args.kwargs["query"] == "TRUNCATE TABLE CUSTOMERS"


@pytest.mark.asyncio
async def test_customers_insert(mock_execute_many: AsyncMock):
    customer1 = Customer(first_name="fname1", last_name="lname1")
    customer2 = Customer(first_name="fname2", last_name="lname2")

    await customer_dao.insert_customers([customer1, customer2])

    assert len(mock_execute_many.call_args_list) == 1
    assert_that(mock_execute_many.call_args.kwargs["query"]).is_equal_to(
        "INSERT INTO CUSTOMERS(FIRST_NAME, LAST_NAME) VALUES (:first_name, :last_name)"
    )
    inserted_rows: list[dict[str, Any]] = mock_execute_many.call_args.kwargs["values"]
    expected = jsonable_encoder([customer2, customer1])
    assert_that(DeepDiff(expected, inserted_rows, ignore_order=True)).is_empty()


@pytest.mark.asyncio
async def test_customers_read(mock_fetch_all: AsyncMock):
    customer1 = Customer(first_name="fname1", last_name="lname1")
    customer2 = Customer(first_name="fname2", last_name="lname2")

    mock_fetch_all.return_value = jsonable_encoder([customer1, customer2])

    customers: list[Customer] = await customer_dao.read_customers()

    assert_that(customers).is_length(2)
    assert_that(customers).contains(customer1)
    assert_that(customers).contains(customer2)

    assert len(mock_fetch_all.call_args_list) == 1
    assert_that(mock_fetch_all.call_args.kwargs["query"]).is_equal_to(
        "SELECT * FROM CUSTOMERS"
    )
