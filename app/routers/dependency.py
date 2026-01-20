from fastapi import APIRouter
from pydantic.dataclasses import dataclass

from app.service.service_a import (
    get_value,
    get_value_async as get_async,
    GetDepValue, GetDepValueAsync,
)

router = APIRouter(prefix="/dependency", tags=["samples", "orm"])


@dataclass(frozen=True)
class Resp:
    value: str


@router.get("/direct")
async def read_direct() -> Resp:
    value: str = get_value()
    return Resp(value=value)


@router.get("/indirect")
async def read_indirect(value: GetDepValue) -> Resp:
    return Resp(value=value)


@router.get("/direct-async")
async def read_direct_async() -> Resp:
    value: str = await anext(get_async())
    return Resp(value=value)


@router.get("/indirect-async")
async def read_indirect_async(value: GetDepValueAsync) -> Resp:
    return Resp(value=value)
