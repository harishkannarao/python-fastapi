from fastapi import APIRouter

from app.dao.sample_jsonb_orm_dao import create_sample_document
from app.dao.sample_orm_dao import create_sample
from app.db.database_dependencies import AsyncSessionDep
from app.model.request.sample import SampleCreateWithDocuments
from app.model.request.sample_document import SampleDocumentCreate
from app.model.response.sample import Sample

router = APIRouter(prefix="/samples/orm/transaction", tags=["samples", "orm"])

@router.put("/propagated")
async def create_sample_with_documents_handler(
    session: AsyncSessionDep, sample_with_documents: SampleCreateWithDocuments
) -> Sample:
    result: Sample = await create_sample(session, sample_with_documents.sample)
    for document in sample_with_documents.documents:
        input_document: SampleDocumentCreate = SampleDocumentCreate(sample_id=result.id, **vars(document))
        await create_sample_document(session, input_document)
    return result