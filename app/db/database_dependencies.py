from typing import Annotated, Generator, Any, AsyncGenerator

from databases import Database
from fastapi import Depends
from sqlmodel import Session
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.database_config import (
    get_database,
    create_session,
    create_async_session,
)


def get_database_dep() -> Database:
    return get_database()


DatabaseDep = Annotated[Database, Depends(get_database_dep)]


def create_session_dep() -> Generator[Session, Any, None]:
    for session in create_session():
        with session.begin():
            yield session


SessionDep = Annotated[Session, Depends(create_session_dep)]


async def create_async_session_dep() -> AsyncGenerator[AsyncSession, Any]:
    async for async_session in create_async_session():
        async with async_session.begin():
            yield async_session


AsyncSessionDep = Annotated[AsyncSession, Depends(create_async_session_dep)]
