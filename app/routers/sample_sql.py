from uuid import UUID

from fastapi import APIRouter, Query, Response, HTTPException

import structlog

from app.dao.sample_sql_dao import (
    read_samples,
    read_sample_by_id,
    create_sample,
    update_sample,
    delete_by_id,
    delete_samples,
)
from app.db.database_dependencies import DatabaseDep
from app.model.request.sample import SampleCreate, SampleUpdate
from app.model.response.sample import Sample

router = APIRouter(prefix="/samples/sql", tags=["samples", "orm"])


@router.get("")
async def read_samples_handler(
    database: DatabaseDep,
    offset: int = 0,
    limit: int = Query(default=100, ge=1, le=100),
) -> tuple[Sample, ...]:
    return await read_samples(database, offset, limit)


@router.get("/{sample_id}")
async def read_sample_by_id_handler(
    database: DatabaseDep, sample_id: UUID, response: Response
) -> Sample | None:
    result: Sample | None = await read_sample_by_id(database, sample_id)
    if result is None:
        response.status_code = 404
    return result


@router.put("")
async def create_sample_handler(database: DatabaseDep, sample: SampleCreate) -> Sample:
    sample_id: UUID = await create_sample(database, sample)
    result: Sample | None = await read_sample_by_id(database, sample_id)
    if result is None:
        logger = structlog.get_logger()
        logger.error(f"Couldn't lookup sample by id after creation: {sample_id}")
        raise HTTPException(
            status_code=500,
            detail={"message": "Unexpected error"},
        )
    return result


@router.post("")
async def update_sample_handler(
    database: DatabaseDep, sample: SampleUpdate, response: Response
) -> Sample | None:
    result: list[UUID] = await update_sample(database, sample)
    if len(result) == 0:
        response.status_code = 409
        return None
    elif len(result) > 1:
        logger = structlog.get_logger()
        logger.error(f"Unexpectedly updated multiple rows by id: {sample.id}")
        raise HTTPException(
            status_code=500,
            detail={"message": "Unexpected error"},
        )
    else:
        return await read_sample_by_id(database, result[0])


@router.delete("/{sample_id}", status_code=204)
async def delete_sample_by_id_handler(database: DatabaseDep, sample_id: UUID) -> None:
    await delete_by_id(database, sample_id)
    return None


@router.delete("", status_code=204)
async def delete_all_handler(database: DatabaseDep) -> None:
    await delete_samples(database)
    return None
