import asyncio
import json
import uuid
from datetime import datetime, UTC

import structlog
from fastapi import APIRouter, Query
from fastapi.encoders import jsonable_encoder
from pydantic.dataclasses import dataclass

from app.model.response.sample import Sample
from app.producer.inbound_producer import publish_to_inbound
from tests_integration.support.model.inbound_message import InboundMessage

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


@router.post("/publish-inbound-messages", status_code=204)
async def publish_inbound_messages_handler(message: InboundMessage) -> None:
    logger = structlog.get_logger()
    await publish_to_inbound(payload_string=json.dumps(jsonable_encoder(message.samples)), headers=message.headers)
    logger.info(f"Published {len(message.samples)} message(s) to inbound queue")
    return


MAX_CONCURRENT_TASKS = 10
GLOBAL_SEMAPHORE = asyncio.Semaphore(MAX_CONCURRENT_TASKS)


@router.get("/publish-bulk-inbound-messages", status_code=204)
async def publish_bulk_inbound_messages_handler(
    count: int = Query(default=1, ge=1, le=10000),
    throttle: bool = False,
) -> None:
    logger = structlog.get_logger()

    async def publish_message(index: int, use_throttle: bool) -> None:
        try:
            if use_throttle:
                await GLOBAL_SEMAPHORE.acquire()
            logger.info(f"Publishing index {index}")
            message: Sample = Sample(
                id=uuid.uuid4(),
                username=f"user-{uuid.uuid4()}",
                bool_field=None,
                float_field=None,
                decimal_field=None,
                created_datetime=datetime.now(UTC),
                updated_datetime=datetime.now(UTC),
                version=1,
            )
            await publish_to_inbound(json.dumps(jsonable_encoder([message])))
            logger.info(f"Published index {index}")
        finally:
            if use_throttle:
                GLOBAL_SEMAPHORE.release()

    # 1. Create a list of coroutines based on the count
    tasks = [publish_message(i, throttle) for i in range(0, count)]

    # 2. Execute them in parallel and wait for all of them to finish
    await asyncio.gather(*tasks)

    logger.info(f"Published {count} message(s) to inbound queue")
    return
