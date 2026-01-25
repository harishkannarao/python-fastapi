import uuid
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Response
from fastapi.encoders import jsonable_encoder
from sqlmodel import select, delete, desc

from app.db.database_dependencies import AsyncSessionDep, SessionDep
from app.model.entity.sample_documents_entity import SampleDocumentEntity
from app.model.request.sample_document import SampleDocumentCreate
from app.model.response.sample_document import SampleDocument

router = APIRouter(prefix="/samples/jsonb/orm", tags=["samples", "orm", "jsonb"])


@router.get("")
async def read_documents(
    session: AsyncSessionDep,
) -> list[SampleDocument]:
    entities = (
        await session.exec(
            select(SampleDocumentEntity).order_by(
                desc(SampleDocumentEntity.created_datetime)
            )
        )
    ).all()
    sample_documents = list(map(lambda e: SampleDocument(**e.model_dump()), entities))
    return sample_documents


@router.get("/{sample_document_id}")
async def read_sample_document_by_id(
    session: AsyncSessionDep, sample_document_id: UUID, response: Response
) -> SampleDocument | None:
    result: SampleDocumentEntity | None = (
        await session.exec(
            select(SampleDocumentEntity).where(
                SampleDocumentEntity.id == sample_document_id
            )
        )
    ).one_or_none()
    if result is None:
        response.status_code = 404
        return None
    return SampleDocument(**result.model_dump())


@router.get("/json_id/{json_id}")
async def read_sample_document_by_json_id(
    session: AsyncSessionDep, json_id: str, response: Response
) -> SampleDocument | None:
    result: SampleDocumentEntity | None = (
        await session.exec(
            select(SampleDocumentEntity).where(
                SampleDocumentEntity.json_data["id"].astext == json_id
            )
        )
    ).one_or_none()
    if result is None:
        response.status_code = 404
        return None
    return SampleDocument(**result.model_dump())


@router.put("")
async def create_sample_document(
    session: AsyncSessionDep, input_document: SampleDocumentCreate
) -> SampleDocument:
    sample_document_entity: SampleDocumentEntity = SampleDocumentEntity(
        id=uuid.uuid4(),
        created_datetime=datetime.now(timezone.utc),
        **jsonable_encoder(input_document),
    )
    session.add(sample_document_entity)
    await session.commit()
    await session.refresh(sample_document_entity)
    return SampleDocument(**sample_document_entity.model_dump())


@router.delete("", status_code=204)
async def delete_all(session: SessionDep) -> None:
    session.exec(delete(SampleDocumentEntity))
    session.commit()
    return None
