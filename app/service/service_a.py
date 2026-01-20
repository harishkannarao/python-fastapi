from typing import Annotated

from fastapi import Depends

from app.service.service_b import produce_value_async as produce_async, produce_value


async def get_value_async():
    yield "prod-async"


def get_value() -> str:
    return "prod"


async def get_dep_value_async():
    async for value in produce_async():
        yield value

GetDepValueAsync = Annotated[str, Depends(get_dep_value_async)]

def get_dep_value() -> str:
    return produce_value()

GetDepValue = Annotated[str, Depends(get_dep_value)]
