from typing import Any

import pytest
from assertpy import assert_that
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from importlib import reload

from httpx import Response

import app.routers.customer as customer
from app.model.customer import Customer


@pytest.fixture
def reload_customer_router() -> None:
    reload(customer)
    return None


def test_customers_insert_read_delete(
    test_client: TestClient,
    reload_customer_router: None,
):
    initial_delete_response: Response = test_client.delete("/context/customers")
    assert_that(initial_delete_response.status_code).is_equal_to(204)

    customer1 = Customer(first_name="fname1", last_name="lname1")
    customer2 = Customer(first_name="fname2", last_name="lname2")
    input_json = jsonable_encoder([customer1, customer2])

    create_response: Response = test_client.put("/context/customers", json=input_json)
    assert_that(create_response.status_code).is_equal_to(204)

    read_response: Response = test_client.get("/context/customers")

    assert_that(read_response.status_code).is_equal_to(200)
    response_json: list[dict[str, Any]] = read_response.json()

    assert_that(response_json).is_length(2)
    assert_that(response_json).contains(jsonable_encoder(customer1))
    assert_that(response_json).contains(jsonable_encoder(customer2))

    delete_response: Response = test_client.delete("/context/customers")
    assert_that(delete_response.status_code).is_equal_to(204)

    read_response_after_delete: Response = test_client.get("/context/customers")

    assert_that(read_response_after_delete.status_code).is_equal_to(200)
    response_json_after_delete: list[dict[str, Any]] = read_response_after_delete.json()
    assert_that(response_json_after_delete).is_length(0)
