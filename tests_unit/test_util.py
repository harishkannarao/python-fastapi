from typing import Any


async def async_gen_helper(items: list[Any]):
    for item in items:
        yield item


def gen_helper(items: list[Any]):
    for item in items:
        yield item
