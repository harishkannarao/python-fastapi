from uuid import UUID

import structlog
from fastapi import APIRouter, Response, HTTPException
from sqlalchemy.exc import IntegrityError

from app.dao.sample_jsonb_orm_dao import (
    read_documents,
    read_sample_document_by_id,
    read_sample_document_by_json_id,
    create_sample_document,
    delete_all,
)
from app.db.database_dependencies import AsyncSessionDep, SessionDep
from app.model.request.sample_document import SampleDocumentCreate
from app.model.response.sample_document import SampleDocument

router = APIRouter(prefix="/samples/jsonb/orm", tags=["samples", "orm", "jsonb"])


@router.get("")
async def read_documents_handler(
    session: AsyncSessionDep,
) -> list[SampleDocument]:
    return await read_documents(session)


@router.get("/{sample_document_id}")
async def read_sample_document_by_id_handler(
    session: AsyncSessionDep, sample_document_id: UUID, response: Response
) -> SampleDocument | None:
    result: SampleDocument | None = await read_sample_document_by_id(
        session, sample_document_id
    )
    if result is None:
        response.status_code = 404
    return result


@router.get("/json_id/{json_id}")
async def read_sample_document_by_json_id_handler(
    session: AsyncSessionDep, json_id: str, response: Response
) -> SampleDocument | None:
    result: SampleDocument | None = await read_sample_document_by_json_id(
        session, json_id
    )
    if result is None:
        response.status_code = 404
    return result


@router.put("")
async def create_sample_document_handler(
    session: AsyncSessionDep, input_document: SampleDocumentCreate
) -> SampleDocument:
    try:
        return await create_sample_document(session, input_document)
    except IntegrityError as ie:
        logger = structlog.get_logger()
        logger.error(f"IntegrityError!: {repr(ie)}")
        raise HTTPException(
            status_code=409,
            detail={"key": "$.json_id.id", "value": str(input_document.json_data.id)},
        )


@router.delete("", status_code=204)
async def delete_all_handler(session: SessionDep) -> None:
    return await delete_all(session)
