import uuid
from typing import Callable, Awaitable, Any

import structlog
from fastapi import Request, Response


def create_request_context(request: Request) -> dict[str, Any]:
    return {
        "request_id": request.state.request_id,
        "request_method": request.method,
        "request_path": request.url.path,
    }


class RequestIdMiddleware:
    def __init__(self, header_name: str):
        self.header_name = header_name

    async def __call__(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id: str | None = request.headers.get(self.header_name)
        if request_id is None:
            request_id = str(uuid.uuid4())

        request.state.request_id = request_id

        request_context: dict[str, Any] = create_request_context(request)
        structlog.contextvars.bind_contextvars(**request_context)
        logger = structlog.get_logger()
        logger.info("Request started", **request_context)
        try:
            response = await call_next(request)
            response.headers[self.header_name] = request_id
            request_context["status"] = response.status_code
            structlog.contextvars.bind_contextvars(status=response.status_code)
        finally:
            logger.info("Request finished", **request_context)
            structlog.contextvars.clear_contextvars()
        return response
