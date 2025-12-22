import pytest
from assertpy import assert_that
from fastapi import Response
from fastapi.testclient import TestClient
from importlib import reload
import app.routers.customer as customer


@pytest.fixture
def reload_customer_router() -> None:
    reload(customer)
    return None


def test_customers_insert_read_delete(
    test_client: TestClient,
    reload_customer_router: None,
):
    initial_delete: Response = test_client.delete("/context/customers")
    assert_that(initial_delete.status_code).is_equal_to(204)
