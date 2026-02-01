from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Query, Response
from pydantic import RootModel
from sqlalchemy import ScalarResult
from sqlmodel import select, delete

from app.db.database_dependencies import AsyncSessionDep, SessionDep
from app.model.entity.sample_entity import SampleEntity
from app.model.request.sample import SampleCreate, SampleUpdate
from app.model.response.sample import Sample
from app.dao.sample_orm_dao import read_samples, read_sample_by_id, create_sample

router = APIRouter(prefix="/samples/orm", tags=["samples", "orm"])


@router.get("")
async def read_samples_handler(
    session: AsyncSessionDep,
    offset: int = 0,
    limit: int = Query(default=100, ge=1, le=100),
) -> tuple[Sample, ...]:
    return await read_samples(session, offset, limit)


@router.get("/{sample_id}")
async def read_sample_by_id_handler(
    session: AsyncSessionDep, sample_id: UUID, response: Response
) -> Sample | None:
    result: Sample | None = await read_sample_by_id(session, sample_id)
    if result is None:
        response.status_code = 404
    return result


@router.put("")
async def create_sample_handler(
    session: AsyncSessionDep, sample: SampleCreate
) -> Sample:
    result: Sample = await create_sample(session, sample)
    return result


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
    session.flush()
    session.refresh(found_sample)
    return Sample(**found_sample.model_dump())


@router.delete("/{sample_id}", status_code=204)
async def delete_sample_by_id(session: AsyncSessionDep, sample_id: UUID) -> None:
    result: SampleEntity | None = (
        await session.exec(select(SampleEntity).where(SampleEntity.id == sample_id))
    ).one_or_none()
    if result is not None:
        await session.delete(result)
        await session.flush()
    return None


@router.delete("", status_code=204)
async def delete_all(session: SessionDep) -> None:
    session.exec(delete(SampleEntity))
    session.flush()
    return None
