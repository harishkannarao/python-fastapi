import uuid
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Query, Response
from pydantic import RootModel
from sqlalchemy import ScalarResult
from sqlmodel import select, delete, asc

from app.db.database_dependencies import AsyncSessionDep, SessionDep
from app.model.entity.sample_entity import SampleEntity
from app.model.request.sample import SampleCreate, SampleUpdate
from app.model.response.sample import Sample

router = APIRouter(prefix="/samples/orm", tags=["samples", "orm"])


@router.get("")
async def read_samples(
    session: AsyncSessionDep,
    offset: int = 0,
    limit: int = Query(default=100, ge=1, le=100),
) -> list[Sample]:
    entities = (
        await session.exec(
            select(SampleEntity)
            .order_by(asc(SampleEntity.created_datetime))
            .offset(offset)
            .limit(limit)
        )
    ).all()
    samples = list(map(lambda e: Sample(**e.model_dump()), entities))
    return samples


@router.get("/{sample_id}")
async def read_sample_by_id(
    session: AsyncSessionDep, sample_id: UUID, response: Response
) -> Sample | None:
    result: SampleEntity | None = (
        await session.exec(select(SampleEntity).where(SampleEntity.id == sample_id))
    ).one_or_none()
    if result is None:
        response.status_code = 404
        return None
    return Sample(**result.model_dump())


@router.put("")
async def create_sample(session: AsyncSessionDep, sample: SampleCreate) -> Sample:
    now: datetime = datetime.now(timezone.utc)
    sample_entity: SampleEntity = SampleEntity(
        id=uuid.uuid4(), version=1, created_datetime=now, updated_datetime=now
    )
    sample_entity.sqlmodel_update(RootModel(sample).model_dump())
    session.add(sample_entity)
    await session.commit()
    await session.refresh(sample_entity)
    return Sample(**sample_entity.model_dump())


@router.post("")
async def update_sample(
    session: SessionDep, sample: SampleUpdate, response: Response
) -> Sample | None:
    statement = (
        select(SampleEntity)
        .where(SampleEntity.id == sample.id)
        .where(SampleEntity.version == sample.old_version)
    )
    results: ScalarResult[SampleEntity] = session.exec(statement)
    found_sample: SampleEntity | None = results.one_or_none()
    if found_sample is None:
        response.status_code = 409
        return None
    found_sample.sqlmodel_update(RootModel(sample).model_dump())
    found_sample.updated_datetime = datetime.now(timezone.utc)
    found_sample.version = sample.new_version
    session.add(found_sample)
    session.commit()
    session.refresh(found_sample)
    return Sample(**found_sample.model_dump())


@router.delete("/{sample_id}", status_code=204)
async def delete_sample_by_id(session: AsyncSessionDep, sample_id: UUID) -> None:
    result: SampleEntity | None = (
        await session.exec(select(SampleEntity).where(SampleEntity.id == sample_id))
    ).one_or_none()
    if result is not None:
        await session.delete(result)
        await session.commit()
    return None


@router.delete("", status_code=204)
async def delete_all(session: SessionDep) -> None:
    session.exec(delete(SampleEntity))
    session.commit()
    return None
