import uuid
from uuid import UUID

from databases.backends.common.records import Record

from app.db.database_config import database
from app.model.request.sample import SampleCreate, SampleUpdate
from app.model.response.sample import Sample

READ_SAMPLE_BY_ID = "select * from sample_table where id=:sample_id"

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


async def read_sample_by_id(sample_id: uuid.UUID) -> Sample | None:
    row = await database.fetch_one(
        query=READ_SAMPLE_BY_ID, values={"sample_id": sample_id}
    )
    if row:
        return Sample(**dict(row))
    else:
        return None


async def create_sample(sample: SampleCreate) -> uuid.UUID:
    input_dict = vars(sample)
    inserted_row: Record = await database.fetch_one(
        query=INSERT_SAMPLE, values=input_dict
    )
    return inserted_row["id"]


async def update_sample(sample: SampleUpdate) -> list[UUID]:
    updated_rows: list[Record] = await database.fetch_all(
        query=UPDATE_SAMPLE, values=vars(sample)
    )
    return [row["id"] for row in updated_rows]
