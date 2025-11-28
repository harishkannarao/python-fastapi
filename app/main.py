import structlog
import uvicorn
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings
from app.logging.logging_config import setup_logging
from app.middleware.process_time import ProcessTimeMiddleware
from app.middleware.request_id import RequestIdMiddleware
from app.routers.sample import router as sample_router

# Initialize logging at application startup
setup_logging(json_logs=settings.app_json_logs)

context = FastAPI(openapi_url=settings.app_open_api_url)

context.include_router(sample_router)

app = FastAPI(openapi_url=settings.app_open_api_url)

app.mount(settings.app_context, context)

app.add_middleware(
    BaseHTTPMiddleware, dispatch=ProcessTimeMiddleware(header_name="x-process-time")
)
app.add_middleware(
    BaseHTTPMiddleware, dispatch=RequestIdMiddleware(header_name="x-request-id")
)


@app.get("/")
async def root():
    logger = structlog.get_logger()
    logger.info("Root request received")
    return {"message": "Hello Bigger Applications!"}


@context.get("/")
async def context_root():
    logger = structlog.get_logger()
    logger.info("Context Root request received")
    return {"message": "Hello Sub Application!"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
