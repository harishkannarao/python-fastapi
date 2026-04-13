import json
from typing import Any
from uuid import UUID

from databases.backends.common.records import Record
from fastapi.encoders import jsonable_encoder

from app.db.database_config import database
from app.model.request.sample_document import SampleDocumentCreate
from app.model.response.sample_document import SampleDocument, DocumentMetadata

READ_SAMPLE_DOCUMENT_BY_ID = "select * from sample_documents where id=:id"

INSERT_SAMPLE_DOCUMENT = """
    INSERT INTO
    sample_documents(
        id, sample_id, json_data, secondary_json_dict, created_datetime
    ) VALUES(
        gen_random_uuid(), :sample_id, :json_data, :secondary_json_dict, timezone('utc', now())
    )
    RETURNING id
    """


async def read_sample_document_by_id(sample_document_id: UUID) -> SampleDocument | None:
    row: Record = await database.fetch_one(
        query=READ_SAMPLE_DOCUMENT_BY_ID, values={"id": sample_document_id}
    )
    if row:
        return map_from_db_row(row)
    else:
        return None


async def create_sample_document(input_document: SampleDocumentCreate) -> UUID:
    inserted_row: Record = await database.fetch_one(
        query=INSERT_SAMPLE_DOCUMENT, values=map_to_db_row(input_document)
    )
    return inserted_row["id"]


def map_from_db_row(input_document: Record) -> SampleDocument:
    db_dict = jsonable_encoder(input_document)
    db_dict["json_data"] = DocumentMetadata(**json.loads(db_dict["json_data"]))
    db_dict["secondary_json_dict"] = json.loads(db_dict["secondary_json_dict"])
    return SampleDocument(**db_dict)


def map_to_db_row(input_document: SampleDocumentCreate) -> dict[str, Any]:
    input_dict = jsonable_encoder(input_document)
    input_dict["json_data"] = json.dumps(input_dict["json_data"])
    input_dict["secondary_json_dict"] = json.dumps(input_dict["secondary_json_dict"])
    return input_dict
