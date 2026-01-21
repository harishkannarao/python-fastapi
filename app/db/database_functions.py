from typing import Annotated, Generator, Any, AsyncGenerator

from databases.core import Transaction
from fastapi import Depends
from sqlmodel import Session
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.database_config import (
    create_transaction,
    create_session,
    create_async_session,
)


async def create_transaction_dep():
    async for transaction in create_transaction():
        yield transaction


TransactionDep = Annotated[Transaction, Depends(create_transaction_dep)]


def create_session_dep() -> Generator[Session, Any, None]:
    for session in create_session():
        yield session


SessionDep = Annotated[Session, Depends(create_session_dep)]


async def create_async_session_dep() -> AsyncGenerator[AsyncSession, Any]:
    async for async_session in create_async_session():
        yield async_session


AsyncSessionDep = Annotated[AsyncSession, Depends(create_async_session_dep)]
