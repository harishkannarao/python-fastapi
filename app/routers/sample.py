import uuid
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Query, Response
from sqlalchemy import ScalarResult
from sqlmodel import select

from app.db.database_config import create_session
from app.model.entity.sample_entity import SampleEntity
from app.model.request.sample import SampleCreate
from app.model.response.sample import Sample

router = APIRouter(prefix="/samples/sqlmodel", tags=["samples", "sqlmodel"])


@router.get("")
async def read_samples(
    offset: int = 0, limit: int = Query(default=100, ge=1, le=100)
) -> list[Sample]:
    with create_session() as session:
        entities = session.exec(select(SampleEntity).offset(offset).limit(limit)).all()
        samples = list(map(lambda e: Sample(**e.model_dump()), entities))
        return samples


@router.get("/{sample_id}")
async def read_sample_by_id(sample_id: UUID, response: Response) -> Sample | None:
    with create_session() as session:
        result: SampleEntity | None = session.exec(
            select(SampleEntity).where(SampleEntity.id == sample_id)
        ).one_or_none()
        if result is None:
            response.status_code = 404
        return Sample(**result.model_dump())


@router.put("")
async def create_sample(sample: SampleCreate) -> Sample:
    with create_session() as session:
        now: datetime = datetime.now(timezone.utc)
        sample_entity: SampleEntity = SampleEntity(
            id=uuid.uuid4(),
            version=1,
            created_datetime=now,
            updated_datetime=now,
            **vars(sample),
        )
        session.add(sample_entity)
        session.commit()
        session.refresh(sample_entity)
        return Sample(**sample_entity.model_dump())


@router.post("")
async def update_sample(
    sample: SampleEntity, response: Response
) -> SampleEntity | None:
    statement = (
        select(SampleEntity)
        .where(SampleEntity.id == sample.id)
        .where(SampleEntity.version == sample.version)
    )
    with create_session() as session:
        results: ScalarResult[SampleEntity] = session.exec(statement)
        found_sample: SampleEntity | None = results.first()
        if found_sample is None:
            response.status_code = 409
            return None
        found_sample.sqlmodel_update(sample.model_dump(exclude_unset=True))
        session.add(found_sample)
        session.commit()
        session.refresh(found_sample)
        return found_sample


@router.delete("/{sample_id}", status_code=204)
async def delete_sample_by_id(sample_id: UUID) -> None:
    with create_session() as session:
        result: SampleEntity | None = session.exec(
            select(SampleEntity).where(SampleEntity.id == sample_id)
        ).one_or_none()
        if result is not None:
            session.delete(result)
            session.commit()
        return None
