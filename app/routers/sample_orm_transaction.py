import structlog
from fastapi import APIRouter

from app.dao.sample_jsonb_orm_dao import create_sample_document
from app.dao.sample_orm_dao import create_sample
from app.db.database_dependencies import AsyncSessionDep
from app.model.request.sample import SampleCreateWithDocuments
from app.model.request.sample_document import SampleDocumentCreate
from app.model.response.sample import Sample
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

router = APIRouter(prefix="/samples/orm/transaction", tags=["samples", "orm"])


@router.put("/propagated")
async def create_sample_with_documents_handler_with_propagation(
    session: AsyncSessionDep, sample_with_documents: SampleCreateWithDocuments
) -> Sample:
    result: Sample = await create_sample(session, sample_with_documents.sample)
    for document in sample_with_documents.documents:
        input_document: SampleDocumentCreate = SampleDocumentCreate(
            sample_id=result.id, **vars(document)
        )
        await create_sample_document(session, input_document)
    return result


@router.put("/isolated", response_model=Sample, responses={207: {"model": Sample}})
async def create_sample_with_documents_handler_with_isolation(
    session: AsyncSessionDep, sample_with_documents: SampleCreateWithDocuments
) -> JSONResponse:
    result: Sample = await create_sample(session, sample_with_documents.sample)
    await session.flush()

    try:
        for document in sample_with_documents.documents:
            async with session.begin_nested():
                input_document: SampleDocumentCreate = SampleDocumentCreate(
                    sample_id=result.id, **vars(document)
                )
                await create_sample_document(session, input_document)
                await session.flush()
    except Exception as e:
        logger = structlog.get_logger()
        logger.error(f"Exception!!!: {repr(e)}")
        return JSONResponse(status_code=207, content=jsonable_encoder(result))

    return JSONResponse(status_code=200, content=jsonable_encoder(result))
