import uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from fastapi.encoders import jsonable_encoder

from assertpy import assert_that
from fastapi.testclient import TestClient

from httpx import Response

from app.model.request.sample import SampleCreate
from app.model.response.sample import Sample

SAMPLE_ORM_ENDPOINT = "/context/samples/orm"


def test_sample_orm_crud_operations(test_client: TestClient):
    initial_delete_all_response: Response = test_client.delete(SAMPLE_ORM_ENDPOINT)
    assert_that(initial_delete_all_response.status_code).is_equal_to(204)

    sample_1_create: SampleCreate = SampleCreate(
        username=f"user-1-{uuid.uuid4()}",
        bool_field=True,
        float_field=0.8,
        decimal_field=Decimal("0.5"),
    )
    sample_1_create_response = test_client.put(
        SAMPLE_ORM_ENDPOINT, json=jsonable_encoder(sample_1_create)
    )
    assert_that(sample_1_create_response.status_code).is_equal_to(200)
    sample_1: Sample = Sample(**sample_1_create_response.json())
    assert_that(sample_1.id).is_not_none()
    now = datetime.now(timezone.utc)
    one_minute_ago = now - timedelta(minutes=1)
    one_minute_hence = now + timedelta(minutes=1)
    assert_that(sample_1.created_datetime).is_between(one_minute_ago, one_minute_hence)
    assert_that(sample_1.updated_datetime).is_between(one_minute_ago, one_minute_hence)
    assert_that(sample_1.version).is_equal_to(1)
    assert_that(sample_1.username).is_equal_to(sample_1_create.username)

    # sample_2_create = SampleCreate(
    #     username=f"user-2-{uuid.uuid4()}",
    #     bool_field=None,
    #     float_field=None,
    #     decimal_field=None
    # )
