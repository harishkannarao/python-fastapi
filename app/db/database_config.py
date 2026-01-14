from databases import Database
from sqlmodel import Session, create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from app.config import settings

DATABASE_URL = (
    f"postgresql://{settings.app_db_user}:{settings.app_db_password}"
    f"@{settings.app_db_host}:{settings.app_db_port}/{settings.app_db_database}"
)
DATABASE_ASYNC_URL = (
    f"postgresql+asyncpg://{settings.app_db_user}:{settings.app_db_password}"
    f"@{settings.app_db_host}:{settings.app_db_port}/{settings.app_db_database}"
)

database = Database(
    DATABASE_ASYNC_URL,
    min_size=settings.app_db_min_con,
    max_size=settings.app_db_max_con,
)

engine = create_engine(
    DATABASE_URL,
    pool_size=settings.app_db_min_con,
    max_overflow=settings.app_db_max_con - settings.app_db_min_con,
    echo=True,
)


def create_session() -> Session:
    return Session(engine)


async_engine = create_async_engine(
    DATABASE_ASYNC_URL,
    pool_size=settings.app_db_min_con,
    max_overflow=settings.app_db_max_con - settings.app_db_min_con,
    echo=True,
    future=True,
)


def create_async_session() -> AsyncSession:
    return AsyncSession(async_engine)
