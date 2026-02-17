import structlog
import uvicorn
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from contextlib import asynccontextmanager
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import JSONResponse
from fastapi import Request

from app.config import settings
from app.db.database_config import database, engine
from app.db_schema_migrations.yoyo_migration import apply_db_migrations
from app.logging.logging_config import setup_logging
from app.middleware.process_time import ProcessTimeMiddleware
from app.middleware.request_id import RequestIdMiddleware, create_request_context
from app.routers.sample_orm import router as sample_router
from app.routers.sample_jsonb_orm import router as sample_document_router
from app.routers.sample_orm_transaction import router as sample_transaction_router
from app.routers.customer import router as customer_router
from app.routers.dependency import router as dependency_router
from app.routers.external_faq import router as external_faq_router

# Initialize logging at application startup
setup_logging(json_logs=settings.app_json_logs)

context = FastAPI(openapi_url=settings.app_open_api_url)

context.include_router(sample_router)
context.include_router(sample_document_router)
context.include_router(sample_transaction_router)
context.include_router(customer_router)
context.include_router(dependency_router)
context.include_router(external_faq_router)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if settings.app_db_migration_enabled:
        apply_db_migrations()
    if settings.app_db_enabled:
        await database.connect()
    yield
    if engine is not None:
        engine.dispose()
    if settings.app_db_enabled:
        await database.disconnect()


app = FastAPI(openapi_url=settings.app_open_api_url, lifespan=lifespan)

app.mount(settings.app_context, context)

app.add_middleware(
    BaseHTTPMiddleware, dispatch=ProcessTimeMiddleware(header_name="x-process-time")
)
app.add_middleware(
    BaseHTTPMiddleware, dispatch=RequestIdMiddleware(header_name="x-request-id")
)


@app.exception_handler(Exception)
@context.exception_handler(Exception)
async def universal_exception_handler(request: Request, exc: Exception):
    logger = structlog.get_logger()
    logger.error(
        f"Unexpected Internal Server Error!: {repr(exc)}",
        **(create_request_context(request)),
    )
    return JSONResponse(
        status_code=500, content={"error": "Unexpected Internal Server Error!"}
    )


@app.exception_handler(StarletteHTTPException)
@context.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, exc: StarletteHTTPException):
    logger = structlog.get_logger()
    logger.warning(f"An HTTP error!: {repr(exc)}", **(create_request_context(request)))
    return await http_exception_handler(request, exc)


@app.exception_handler(RequestValidationError)
@context.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    logger = structlog.get_logger()
    logger.warning(
        f"The client sent invalid data!: {exc}", **(create_request_context(request))
    )
    return await request_validation_exception_handler(request, exc)


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
