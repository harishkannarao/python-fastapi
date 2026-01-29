import pytest
from assertpy import assert_that
from sqlmodel import Session
from sqlmodel.ext.asyncio.session import AsyncSession


def test_entity_with_session(get_session: Session):
    assert_that(True).is_true()


@pytest.mark.asyncio
async def test_entity_with_async_session(get_async_session: AsyncSession):
    assert_that(True).is_true()
