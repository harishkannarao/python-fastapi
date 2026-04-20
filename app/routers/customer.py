from fastapi import APIRouter, status

from app.dao import customer_dao
from app.db.database_dependencies import DatabaseDep
from app.model.customer import Customer

router = APIRouter(prefix="/customers", tags=["users"])


@router.get("")
async def read_customers(database: DatabaseDep) -> list[Customer]:
    async with database.transaction():
        return await customer_dao.read_customers(database)


@router.put("", status_code=status.HTTP_204_NO_CONTENT, tags=["users"])
async def insert_customers(database: DatabaseDep, customers: list[Customer]) -> None:
    async with database.transaction():
        return await customer_dao.insert_customers(database, customers)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT, tags=["users"])
async def delete_all_customers(database: DatabaseDep) -> None:
    async with database.transaction():
        return await customer_dao.delete_all_customers(database)
