from fastapi import APIRouter, status

from app.dao import customer_dao
from app.db.database_config import database
from app.model.customer import Customer

router = APIRouter(prefix="/customers", tags=["users"])


@router.get("")
async def read_customers() -> list[Customer]:
    async with database.transaction():
        return await customer_dao.read_customers()


@router.put("", status_code=status.HTTP_204_NO_CONTENT, tags=["users"])
async def insert_customers(customers: list[Customer]) -> None:
    async with database.transaction():
        return await customer_dao.insert_customers(customers)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT, tags=["users"])
async def delete_all_customers() -> None:
    async with database.transaction():
        return await customer_dao.delete_all_customers()
