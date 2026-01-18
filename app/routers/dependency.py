from fastapi import APIRouter
from pydantic.dataclasses import dataclass

from app.service.service_a import get_value

router = APIRouter(prefix="/dependency", tags=["samples", "orm"])


@dataclass(frozen=True)
class Resp:
    value: str


@router.get("/direct")
async def read_direct() -> Resp:
    value: str = get_value()
    return Resp(value=value)
