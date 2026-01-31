from uuid import UUID

from sqlmodel import select, asc
from sqlmodel.ext.asyncio.session import AsyncSession

from app.model.entity.sample_entity import SampleEntity
from app.model.response.sample import Sample


async def read_samples(
    session: AsyncSession, offset: int, limit: int
) -> tuple[Sample, ...]:
    entities = (
        await session.exec(
            select(SampleEntity)
            .order_by(asc(SampleEntity.created_datetime))
            .offset(offset)
            .limit(limit)
        )
    ).all()
    samples = tuple(map(lambda e: Sample(**e.model_dump()), entities))
    return samples


async def read_sample_by_id(session: AsyncSession, sample_id: UUID) -> Sample | None:
    result: SampleEntity | None = (
        await session.exec(select(SampleEntity).where(SampleEntity.id == sample_id))
    ).one_or_none()
    if result is None:
        return None
    return Sample(**result.model_dump())
