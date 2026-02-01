from uuid import UUID

from fastapi import APIRouter, Query, Response

from app.db.database_dependencies import AsyncSessionDep, SessionDep
from app.model.request.sample import SampleCreate, SampleUpdate
from app.model.response.sample import Sample
from app.dao.sample_orm_dao import (
    read_samples,
    read_sample_by_id,
    create_sample,
    update_sample,
    delete_sample_by_id,
    delete_all,
)

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
async def update_sample_handler(
    session: SessionDep, sample: SampleUpdate, response: Response
) -> Sample | None:
    result: Sample | None = update_sample(session, sample)
    if result is None:
        response.status_code = 409
    return result


@router.delete("/{sample_id}", status_code=204)
async def delete_sample_by_id_handler(
    session: AsyncSessionDep, sample_id: UUID
) -> None:
    return await delete_sample_by_id(session, sample_id)


@router.delete("", status_code=204)
async def delete_all_handler(session: SessionDep) -> None:
    return delete_all(session)
