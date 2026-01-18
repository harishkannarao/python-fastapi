from app.service.service_b import produce_value_async as produce_async, produce_value


async def get_value_async():
    yield "prod-async"


def get_value() -> str:
    return "prod"


async def get_dep_value_async():
    return await anext(produce_async())


def get_dep_value() -> str:
    return produce_value()
