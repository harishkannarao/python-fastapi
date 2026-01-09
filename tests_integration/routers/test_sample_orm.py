from assertpy import assert_that
from fastapi.testclient import TestClient

from httpx import Response

SAMPLE_ORM_ENDPOINT = "/context/samples/orm"


def test_sample_orm_crud_operations(test_client: TestClient):
    initial_delete_all_response: Response = test_client.delete(SAMPLE_ORM_ENDPOINT)
    assert_that(initial_delete_all_response.status_code).is_equal_to(204)
