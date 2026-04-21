import json
from typing import Any
from uuid import UUID

from databases import Database
from databases.backends.common.records import Record
from fastapi.encoders import jsonable_encoder

from app.model.request.sample_document import SampleDocumentCreate
from app.model.response.sample_document import SampleDocument, DocumentMetadata

READ_SAMPLES_DOCUMENTS = """
    SELECT *
    FROM sample_documents
    ORDER BY created_datetime
    """

READ_SAMPLE_DOCUMENT_BY_ID = "select * from sample_documents where id=:id"

READ_SAMPLE_DOCUMENT_BY_JSON_ID = """
    SELECT *
    FROM sample_documents
    WHERE (cast(json_data->>'id' as text)) = :json_id
    """

INSERT_SAMPLE_DOCUMENT = """
    INSERT INTO
    sample_documents(
        id, sample_id, json_data, secondary_json_dict, created_datetime
    ) VALUES(
        gen_random_uuid(), :sample_id, :json_data, :secondary_json_dict, timezone('utc', now())
    )
    RETURNING id
    """

DELETE_SAMPLES_DOCUMENTS = "TRUNCATE TABLE sample_documents"


async def read_sample_documents(database: Database) -> list[SampleDocument]:
    rows: list[Record] = await database.fetch_all(query=READ_SAMPLES_DOCUMENTS)
    return [map_from_db_row(row) for row in rows]


async def read_sample_document_by_id(
    database: Database, sample_document_id: UUID
) -> SampleDocument | None:
    row: Record = await database.fetch_one(
        query=READ_SAMPLE_DOCUMENT_BY_ID, values={"id": sample_document_id}
    )
    if row:
        return map_from_db_row(row)
    else:
        return None


async def read_sample_document_by_json_id(
    database: Database, json_id: UUID
) -> SampleDocument | None:
    row: Record = await database.fetch_one(
        query=READ_SAMPLE_DOCUMENT_BY_JSON_ID, values={"json_id": str(json_id)}
    )
    if row:
        return map_from_db_row(row)
    else:
        return None


async def create_sample_document(
    database: Database, input_document: SampleDocumentCreate
) -> UUID:
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


async def delete_sample_documents(database: Database) -> None:
    await database.execute(query=DELETE_SAMPLES_DOCUMENTS)
