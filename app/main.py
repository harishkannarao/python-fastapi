from fastapi import FastAPI
from app.config import settings
from app.routers.sample import router as sample_router

context = FastAPI()

context.include_router(sample_router)

app = FastAPI()

app.mount(settings.app_context, context)


@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}


@context.get("/")
async def context_root():
    return {"message": "Hello Sub Application!"}
