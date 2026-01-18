from fastapi import APIRouter
from pydantic.dataclasses import dataclass

from app.service.service_a import (
    get_value,
    get_dep_value,
    get_value_async as get_async,
    get_dep_value_async,
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
async def read_indirect() -> Resp:
    value: str = get_dep_value()
    return Resp(value=value)


@router.get("/direct-async")
async def read_direct_async() -> Resp:
    value: str = await anext(get_async())
    return Resp(value=value)


@router.get("/indirect-async")
async def read_indirect_async() -> Resp:
    value: str = await get_dep_value_async()
    return Resp(value=value)
