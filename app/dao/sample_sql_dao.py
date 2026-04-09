import datetime
import uuid

from app.db.database_config import database
from app.model.request.sample import SampleCreate
from app.model.response.sample import Sample

READ_SAMPLE_BY_ID = (
    "select * from sample_table where id=:sample_id"
)

INSERT_SAMPLE = (
    """INSERT INTO 
    sample_table(id, username, bool_field, float_field, decimal_field, version, created_datetime, updated_datetime) 
    VALUES 
    (:sample_id, :username, :bool_field, :float_field, :decimal_field, 1, timezone('utc', now()), timezone('utc', now()))"""
)

async def read_sample_by_id(sample_id: uuid.UUID) -> Sample | None:
    row = await database.fetch_one(query=READ_SAMPLE_BY_ID, values={"sample_id": sample_id})
    if row:
        return Sample(**dict(row))
    else:
        return None

async def create_sample(sample: SampleCreate) -> Sample | None:
    sample_id: uuid.UUID = uuid.uuid4()
    input_dict = {"sample_id": sample_id, "username": sample.username, "bool_field": sample.bool_field, "float_field": sample.float_field, "decimal_field": sample.decimal_field}
    await database.execute(query=INSERT_SAMPLE, values=input_dict)
    return await read_sample_by_id(sample_id)