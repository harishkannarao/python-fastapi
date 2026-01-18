async def produce_value_async():
    yield "from-prod-async"


def produce_value() -> str:
    return "from-prod"
