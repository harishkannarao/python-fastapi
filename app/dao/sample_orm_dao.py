import uuid
from datetime import datetime, timezone
from uuid import UUID

from pydantic import RootModel
from sqlalchemy import ScalarResult
from sqlmodel import select, delete, asc, Session
from sqlmodel.ext.asyncio.session import AsyncSession

from app.model.entity.sample_entity import SampleEntity
from app.model.request.sample import SampleCreate, SampleUpdate
from app.model.response.sample import Sample


async def read_samples(
    session: AsyncSession, offset: int, limit: int
) -> tuple[Sample, ...]:
    entities = (
        await session.exec(
            select(SampleEntity)
            .order_by(asc(SampleEntity.created_datetime))
            .offset(offset)
            .limit(limit)
        )
    ).all()
    samples = tuple(map(lambda e: Sample(**e.model_dump()), entities))
    return samples


async def read_sample_by_id(session: AsyncSession, sample_id: UUID) -> Sample | None:
    result: SampleEntity | None = (
        await session.exec(select(SampleEntity).where(SampleEntity.id == sample_id))
    ).one_or_none()
    if result is None:
        return None
    return Sample(**result.model_dump())


async def create_sample(session: AsyncSession, sample: SampleCreate) -> Sample:
    now: datetime = datetime.now(timezone.utc)
    sample_entity: SampleEntity = SampleEntity(
        id=uuid.uuid4(), version=1, created_datetime=now, updated_datetime=now
    )
    sample_entity.sqlmodel_update(RootModel(sample).model_dump())
    session.add(sample_entity)
    await session.flush()
    await session.refresh(sample_entity)
    return Sample(**sample_entity.model_dump())


def update_sample(session: Session, sample: SampleUpdate) -> Sample | None:
    statement = (
        select(SampleEntity)
        .where(SampleEntity.id == sample.id)
        .where(SampleEntity.version == sample.old_version)
    )
    results: ScalarResult[SampleEntity] = session.exec(statement)
    found_sample: SampleEntity | None = results.one_or_none()
    if found_sample is None:
        return None
    found_sample.sqlmodel_update(RootModel(sample).model_dump())
    found_sample.updated_datetime = datetime.now(timezone.utc)
    found_sample.version = sample.new_version
    session.add(found_sample)
    session.flush()
    session.refresh(found_sample)
    return Sample(**found_sample.model_dump())


async def delete_sample_by_id(session: AsyncSession, sample_id: UUID) -> None:
    result: SampleEntity | None = (
        await session.exec(select(SampleEntity).where(SampleEntity.id == sample_id))
    ).one_or_none()
    if result is not None:
        await session.delete(result)
        await session.flush()
    return None


def delete_all(session: Session) -> None:
    session.exec(delete(SampleEntity))
    session.flush()
    return None
