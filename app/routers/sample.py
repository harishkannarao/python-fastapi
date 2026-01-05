from typing import Sequence

from fastapi import APIRouter, Response, Depends
from sqlalchemy import ScalarResult
from sqlmodel import Session, select
from sqlmodel.sql._expression_select_cls import SelectOfScalar

from app.db.database_config import get_session
from app.model.db.sample_table import SampleTable

router = APIRouter(prefix="/samples/sqlmodel", tags=["samples", "sqlmodel"])


@router.get("")
async def read_all_samples(
    session: Session = Depends(get_session),
) -> Sequence[SampleTable]:
    return session.exec(select(SampleTable)).all()


@router.put("")
async def create_sample(
    sample: SampleTable,
    session: Session = Depends(get_session),
) -> SampleTable:
    session.add(sample)
    session.commit()
    session.refresh(sample)
    return sample


@router.post("")
async def update_sample(
    sample: SampleTable,
    response: Response,
    session: Session = Depends(get_session),
) -> SampleTable | None:
    statement: SelectOfScalar[SampleTable] = (
        select(SampleTable)
        .where(SampleTable.id == sample.id)
        .where(SampleTable.version == sample.version)
    )
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
