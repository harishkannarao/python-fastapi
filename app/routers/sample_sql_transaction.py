from uuid import UUID

import structlog
from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.dao.sample_jsonb_sql_dao import create_sample_document
from app.dao.sample_sql_dao import create_sample
from app.dao.sample_sql_dao import read_sample_by_id
from app.model.request.sample import SampleCreateWithDocuments
from app.model.request.sample_document import SampleDocumentCreate
from app.model.response.sample import Sample

router = APIRouter(prefix="/samples/sql/transaction", tags=["samples", "sql"])


@router.put("/propagated")
async def create_sample_with_documents_handler_with_propagation(
    sample_with_documents: SampleCreateWithDocuments,
) -> Sample | None:
    sample_id: UUID = await create_sample(sample_with_documents.sample)
    for document in sample_with_documents.documents:
        input_document: SampleDocumentCreate = SampleDocumentCreate(
            sample_id=sample_id, **vars(document)
        )
        await create_sample_document(input_document)
    return await read_sample_by_id(sample_id)


@router.put("/isolated", response_model=Sample, responses={207: {"model": Sample}})
async def create_sample_with_documents_handler_with_isolation(
    sample_with_documents: SampleCreateWithDocuments,
) -> JSONResponse:
    sample_id: UUID = await create_sample(sample_with_documents.sample)
    sample: Sample = await read_sample_by_id(sample_id)
    try:
        for document in sample_with_documents.documents:
            input_document: SampleDocumentCreate = SampleDocumentCreate(
                sample_id=sample_id, **vars(document)
            )
            await create_sample_document(input_document)
    except Exception as e:
        logger = structlog.get_logger()
        logger.error(f"Exception!!!: {repr(e)}")
        return JSONResponse(status_code=207, content=jsonable_encoder(sample))

    return JSONResponse(status_code=200, content=jsonable_encoder(sample))
