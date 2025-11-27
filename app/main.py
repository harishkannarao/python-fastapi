import uvicorn
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings
from app.middleware.process_time import ProcessTimeMiddleware
from app.routers.sample import router as sample_router

context = FastAPI(openapi_url=settings.app_open_api_url)

context.include_router(sample_router)

app = FastAPI(openapi_url=settings.app_open_api_url)

app.mount(settings.app_context, context)

app.add_middleware(
    BaseHTTPMiddleware, dispatch=ProcessTimeMiddleware(header_name="x-process-time")
)


@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}


@context.get("/")
async def context_root():
    return {"message": "Hello Sub Application!"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
