from typing import Sequence

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

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
