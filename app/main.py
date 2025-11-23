from fastapi import FastAPI
from app.config import settings
from app.routers.sample import router as sample_router

sub_app = FastAPI()

sub_app.include_router(sample_router)

app = FastAPI()

app.mount(settings.app_context, sub_app)


@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}


@sub_app.get("/")
async def sub_root():
    return {"message": "Hello Sub Application!"}
