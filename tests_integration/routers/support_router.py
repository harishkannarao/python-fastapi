import asyncio
import datetime
import uuid

import structlog
from fastapi import APIRouter, Query
from fastapi.encoders import jsonable_encoder
from pydantic.dataclasses import dataclass

from app.model.response.sample import Sample
from app.producer.inbound_producer import publish_to_inbound

router = APIRouter(prefix="/test-support")


@dataclass(frozen=True)
class Resp:
    value: str


@router.get("/get")
async def get_handler() -> Resp:
    logger = structlog.get_logger()
    resp = Resp(value="test-value")
    logger.info("Support Request Success!!", **jsonable_encoder(resp))
    return resp


@router.get("/publish-inbound-messages", status_code=204)
async def publish_inbound_messages_handler(
    count: int = Query(default=1, ge=1, le=10000),
) -> None:
    logger = structlog.get_logger()

    async def publish_message(index: int) -> None:
        logger.info(f"Publishing index {index}")
        message: Sample = Sample(
            id=uuid.uuid4(),
            username=f"user-{uuid.uuid4()}",
            bool_field=None,
            float_field=None,
            decimal_field=None,
            created_datetime=datetime.datetime.now(datetime.UTC),
            updated_datetime=datetime.datetime.now(datetime.UTC),
            version=1,
        )
        await publish_to_inbound([message])
        logger.info(f"Published index {index}")

    # 1. Create a list of coroutines based on the count
    tasks = [publish_message(i) for i in range(0, count)]

    # 2. Execute them in parallel and wait for all of them to finish
    await asyncio.gather(*tasks)

    logger.info(f"Published {count} message(s) to inbound queue")
    return
