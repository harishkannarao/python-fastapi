import uuid
from typing import Callable, Awaitable

from fastapi import Request, Response


class RequestIdMiddleware:
    def __init__(self, header_name: str):
        self.header_name = header_name

    async def __call__(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id: str | None = request.headers.get(self.header_name)
        if request_id is None:
            request_id = str(uuid.uuid4())
        response = await call_next(request)
        response.headers[self.header_name] = request_id
        return response
