from uuid import UUID

from databases import Database
from databases.backends.common.records import Record

from app.model.request.sample import SampleCreate, SampleUpdate
from app.model.response.sample import Sample

READ_SAMPLES = """
    SELECT *
    FROM sample_table
    ORDER BY created_datetime
    LIMIT :limit OFFSET :offset
    """

READ_SAMPLE_BY_ID = "select * from sample_table where id=:id"

DELETE_SAMPLES = "TRUNCATE TABLE sample_table CASCADE"

DELETE_SAMPLE_BY_ID = "delete from sample_table where id=:id returning id"

INSERT_SAMPLE = """
    INSERT INTO
    sample_table(
        id, username, bool_field, float_field, decimal_field, version, created_datetime, updated_datetime
    ) VALUES(
        gen_random_uuid(), :username, :bool_field, :float_field,
        :decimal_field, 1, timezone('utc', now()), timezone('utc', now())
    )
    RETURNING id
    """

UPDATE_SAMPLE = """
    UPDATE sample_table SET
    username = :username,
    bool_field = :bool_field,
    float_field = :float_field,
    decimal_field = :decimal_field,
    version = :new_version,
    updated_datetime = timezone('utc', now())
    WHERE
    id = :id AND version = :old_version
    RETURNING id
    """


async def read_samples(database: Database, offset: int, limit: int) -> list[Sample]:
    rows: list[Record] = await database.fetch_all(
        query=READ_SAMPLES, values={"offset": offset, "limit": limit}
    )
    return [Sample(**dict(row)) for row in rows]


async def read_sample_by_id(database: Database, sample_id: UUID) -> Sample | None:
    row: Record = await database.fetch_one(
        query=READ_SAMPLE_BY_ID, values={"id": sample_id}
    )
    if row:
        return Sample(**dict(row))
    else:
        return None


async def create_sample(database: Database, sample: SampleCreate) -> UUID:
    inserted_row: Record = await database.fetch_one(
        query=INSERT_SAMPLE, values=vars(sample)
    )
    return inserted_row["id"]


async def update_sample(database: Database, sample: SampleUpdate) -> list[UUID]:
    updated_rows: list[Record] = await database.fetch_all(
        query=UPDATE_SAMPLE, values=vars(sample)
    )
    return [row["id"] for row in updated_rows]


async def delete_by_id(database: Database, sample_id: UUID) -> UUID:
    inserted_row: Record = await database.fetch_one(
        query=DELETE_SAMPLE_BY_ID, values={"id": sample_id}
    )
    return inserted_row["id"]


async def delete_samples(
    database: Database,
) -> None:
    await database.execute(query=DELETE_SAMPLES)
