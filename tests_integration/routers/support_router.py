import structlog
from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from pydantic.dataclasses import dataclass

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
