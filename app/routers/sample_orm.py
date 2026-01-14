import uuid
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Query, Response
from pydantic import RootModel
from sqlalchemy import ScalarResult
from sqlmodel import select, delete

from app.db.database_config import create_session, create_async_session
from app.model.entity.sample_entity import SampleEntity
from app.model.request.sample import SampleCreate, SampleUpdate
from app.model.response.sample import Sample

router = APIRouter(prefix="/samples/orm", tags=["samples", "orm"])


@router.get("")
async def read_samples(
    offset: int = 0, limit: int = Query(default=100, ge=1, le=100)
) -> list[Sample]:
    async with create_async_session() as session:
        entities = (
            await session.exec(
                select(SampleEntity)
                .order_by(SampleEntity.created_datetime)
                .offset(offset)
                .limit(limit)
            )
        ).all()
        samples = list(map(lambda e: Sample(**e.model_dump()), entities))
        return samples


@router.get("/{sample_id}")
async def read_sample_by_id(sample_id: UUID, response: Response) -> Sample | None:
    async with create_async_session() as session:
        result: SampleEntity | None = (
            await session.exec(select(SampleEntity).where(SampleEntity.id == sample_id))
        ).one_or_none()
        if result is None:
            response.status_code = 404
            return None
        return Sample(**result.model_dump())


@router.put("")
async def create_sample(sample: SampleCreate) -> Sample:
    async with create_async_session() as session:
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
async def update_sample(sample: SampleUpdate, response: Response) -> Sample | None:
    with create_session() as session:
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
async def delete_sample_by_id(sample_id: UUID) -> None:
    async with create_async_session() as session:
        result: SampleEntity | None = (
            await session.exec(select(SampleEntity).where(SampleEntity.id == sample_id))
        ).one_or_none()
        if result is not None:
            await session.delete(result)
            await session.commit()
        return None


@router.delete("", status_code=204)
async def delete_all() -> None:
    with create_session() as session:
        session.exec(delete(SampleEntity))
        session.commit()
        return None
