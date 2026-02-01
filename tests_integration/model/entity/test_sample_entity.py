import datetime
import uuid
from datetime import timezone
from decimal import Decimal
from typing import Generator

import pytest
from assertpy import assert_that
from sqlmodel import Session
from sqlmodel import select, delete
from sqlmodel.ext.asyncio.session import AsyncSession

from app.model.entity.sample_entity import SampleEntity


@pytest.fixture
def delete_all(get_session: Session) -> Generator[None, None, None]:
    get_session.exec(delete(SampleEntity))
    get_session.flush()
    yield
    get_session.exec(delete(SampleEntity))
    get_session.flush()


def test_entity_with_session(delete_all: None, get_session: Session):
    entity = SampleEntity(
        id=uuid.uuid4(),
        username=f"user-{uuid.uuid4()}",
        bool_field=True,
        float_field=0.978,
        decimal_field=Decimal("0.578"),
        created_datetime=datetime.datetime.now(timezone.utc),
        updated_datetime=datetime.datetime.now(timezone.utc),
        version=1,
    )
    get_session.add(entity)
    get_session.flush()
    result = get_session.exec(
        select(SampleEntity).where(SampleEntity.id == entity.id)
    ).one_or_none()
    assert_that(result).is_equal_to(entity)


@pytest.mark.asyncio
async def test_entity_with_async_session(
    delete_all: None, get_async_session: AsyncSession
):
    entity = SampleEntity(
        id=uuid.uuid4(),
        username=f"user-{uuid.uuid4()}",
        bool_field=True,
        float_field=0.888,
        decimal_field=Decimal("0.9978"),
        created_datetime=datetime.datetime.now(timezone.utc),
        updated_datetime=datetime.datetime.now(timezone.utc),
        version=1,
    )
    get_async_session.add(entity)
    await get_async_session.flush()
    result = (
        await get_async_session.exec(
            select(SampleEntity).where(SampleEntity.id == entity.id)
        )
    ).one_or_none()
    assert_that(result).is_equal_to(entity)
