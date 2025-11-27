import time
from typing import Callable, Awaitable

from fastapi import Request, Response


class ProcessTimeMiddleware:
    def __init__(self, header_name: str):
        self.header_name = header_name

    async def __call__(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        response.headers[self.header_name] = str(process_time)
        return response
