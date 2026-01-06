from typing import Sequence

from fastapi import APIRouter, Response
from sqlalchemy import ScalarResult
from sqlmodel import select

from app.db.database_config import create_session
from app.model.db.sample_table import SampleTable

router = APIRouter(prefix="/samples/sqlmodel", tags=["samples", "sqlmodel"])


@router.get("")
async def read_all_samples() -> Sequence[SampleTable]:
    with create_session() as session:
        return session.exec(select(SampleTable).offset(0).limit(10)).all()


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
