from typing import Sequence
from uuid import UUID

from fastapi import APIRouter, Query, Response
from sqlalchemy import ScalarResult
from sqlmodel import select

from app.db.database_config import create_session
from app.model.db.sample_table import SampleTable

router = APIRouter(prefix="/samples/sqlmodel", tags=["samples", "sqlmodel"])


@router.get("")
async def read_samples(
    offset: int = 0, limit: int = Query(default=100, ge=1, le=100)
) -> Sequence[SampleTable]:
    with create_session() as session:
        return session.exec(select(SampleTable).offset(offset).limit(limit)).all()


@router.get("/{sample_id}")
async def read_sample_by_id(sample_id: UUID, response: Response) -> SampleTable | None:
    with create_session() as session:
        result: SampleTable | None = session.exec(
            select(SampleTable).where(SampleTable.id == sample_id)
        ).one_or_none()
        if result is None:
            response.status_code = 404
        return result


@router.put("")
async def create_sample(sample: SampleTable) -> SampleTable:
    with create_session() as session:
        session.add(sample)
        session.commit()
        session.refresh(sample)
        return sample


@router.post("")
async def update_sample(sample: SampleTable, response: Response) -> SampleTable | None:
    statement = (
        select(SampleTable)
        .where(SampleTable.id == sample.id)
        .where(SampleTable.version == sample.version)
    )
    with create_session() as session:
        results: ScalarResult[SampleTable] = session.exec(statement)
        found_sample: SampleTable | None = results.first()
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
        result: SampleTable | None = session.exec(
            select(SampleTable).where(SampleTable.id == sample_id)
        ).one_or_none()
        if result is not None:
            session.delete(result)
            session.commit()
        return None