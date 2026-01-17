from fastapi import APIRouter, status

from app.dao import customer_dao
from app.db.database_config import TransactionDep
from app.model.customer import Customer

router = APIRouter(prefix="/customers", tags=["users"])


@router.get("")
async def read_customers(transaction: TransactionDep) -> list[Customer]:
    return await customer_dao.read_customers()


@router.put("", status_code=status.HTTP_204_NO_CONTENT, tags=["users"])
async def insert_customers(
    transaction: TransactionDep, customers: list[Customer]
) -> None:
    return await customer_dao.insert_customers(customers)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT, tags=["users"])
async def delete_all_customers(transaction: TransactionDep) -> None:
    return await customer_dao.delete_all_customers()
