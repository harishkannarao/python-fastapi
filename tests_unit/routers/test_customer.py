from typing import Any
from unittest.mock import AsyncMock

import pytest
from assertpy import assert_that
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from httpx import Response
from pytest_mock import MockerFixture

from app.model.customer import Customer

CUSTOMERS_ENDPOINT = "/context/customers"


@pytest.fixture
def mock_read_customers(mocker: MockerFixture) -> AsyncMock:
    mock_execute: AsyncMock = mocker.patch("app.dao.customer_dao.read_customers")
    return mock_execute


@pytest.fixture
def mock_insert_customers(mocker: MockerFixture) -> AsyncMock:
    mock_execute: AsyncMock = mocker.patch("app.dao.customer_dao.insert_customers")
    return mock_execute


@pytest.fixture
def mock_delete_all_customers(mocker: MockerFixture) -> AsyncMock:
    mock_execute: AsyncMock = mocker.patch("app.dao.customer_dao.delete_all_customers")
    return mock_execute


def test_customers_delete(
    mock_create_transaction: AsyncMock,
    mock_delete_all_customers: AsyncMock,
    test_client: TestClient,
):
    mock_delete_all_customers.return_value = None

    response: Response = test_client.delete(CUSTOMERS_ENDPOINT)
    assert_that(response.status_code).is_equal_to(204)

    assert len(mock_delete_all_customers.call_args_list) == 1
    assert mock_delete_all_customers.call_args == ()


def test_customers_insert(
    mock_create_transaction: AsyncMock,
    mock_insert_customers: AsyncMock,
    test_client: TestClient,
):
    customer1 = Customer(first_name="fname1", last_name="lname1")
    customer2 = Customer(first_name="fname2", last_name="lname2")
    input_json = jsonable_encoder([customer1, customer2])

    mock_insert_customers.return_value = None

    response: Response = test_client.put(CUSTOMERS_ENDPOINT, json=input_json)
    assert_that(response.status_code).is_equal_to(204)

    assert len(mock_insert_customers.call_args_list) == 1
    assert len(mock_insert_customers.call_args.args) == 1

    inserted_rows: list[Customer] = mock_insert_customers.call_args.args[0]
    assert_that(inserted_rows).is_length(2)
    assert_that(inserted_rows).contains(customer1)
    assert_that(inserted_rows).contains(customer2)


def test_customers_read(
    mock_create_transaction: AsyncMock,
    mock_read_customers: AsyncMock,
    test_client: TestClient,
):
    customer1 = Customer(first_name="fname1", last_name="lname1")
    customer2 = Customer(first_name="fname2", last_name="lname2")

    mock_read_customers.return_value = [customer1, customer2]

    response: Response = test_client.get(CUSTOMERS_ENDPOINT)

    assert_that(response.status_code).is_equal_to(200)
    response_json: list[dict[str, Any]] = response.json()

    assert_that(response_json).is_length(2)
    assert_that(response_json).contains(jsonable_encoder(customer1))
    assert_that(response_json).contains(jsonable_encoder(customer2))

    assert len(mock_read_customers.call_args_list) == 1
    assert mock_read_customers.call_args.args == ()
