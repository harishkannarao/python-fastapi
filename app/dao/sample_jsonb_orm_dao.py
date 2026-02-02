import uuid
from datetime import datetime, timezone
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlmodel import select, delete, desc, Session
from sqlmodel.ext.asyncio.session import AsyncSession

from app.model.entity.sample_documents_entity import SampleDocumentEntity
from app.model.request.sample_document import SampleDocumentCreate
from app.model.response.sample_document import SampleDocument


async def read_documents(
    session: AsyncSession,
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


async def read_sample_document_by_id(
    session: AsyncSession, sample_document_id: UUID
) -> SampleDocument | None:
    result: SampleDocumentEntity | None = (
        await session.exec(
            select(SampleDocumentEntity).where(
                SampleDocumentEntity.id == sample_document_id
            )
        )
    ).one_or_none()
    if result is None:
        return None
    return SampleDocument(**result.model_dump())


async def read_sample_document_by_json_id(
    session: AsyncSession, json_id: str
) -> SampleDocument | None:
    result: SampleDocumentEntity | None = (
        await session.exec(
            select(SampleDocumentEntity).where(
                SampleDocumentEntity.json_data["id"].astext == json_id
            )
        )
    ).one_or_none()
    if result is None:
        return None
    return SampleDocument(**result.model_dump())


async def create_sample_document(
    session: AsyncSession, input_document: SampleDocumentCreate
) -> SampleDocument:
    sample_document_entity: SampleDocumentEntity = SampleDocumentEntity(
        id=uuid.uuid4(),
        created_datetime=datetime.now(timezone.utc),
        **jsonable_encoder(input_document),
    )
    session.add(sample_document_entity)
    await session.flush()
    await session.refresh(sample_document_entity)
    return SampleDocument(**sample_document_entity.model_dump())


async def delete_all(session: Session) -> None:
    session.exec(delete(SampleDocumentEntity))
    session.flush()
    return None
