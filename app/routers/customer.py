from typing import Any

from fastapi import APIRouter, status

from app.db.database_config import database
from app.model.customer import Customer

SELECT_ALL_CUSTOMERS = "SELECT * FROM CUSTOMERS"
INSERT_CUSTOMER = (
    "INSERT INTO CUSTOMERS(FIRST_NAME, LAST_NAME) VALUES (:first_name, :last_name)"
)

router = APIRouter()


def to_customer(row) -> Customer:
    return Customer(first_name=row.first_name, last_name=row.last_name)


@router.get("/customers/", tags=["users"])
async def read_customers() -> list[Customer]:
    rows = await database.fetch_all(query=SELECT_ALL_CUSTOMERS)
    customers: list[Customer] = list(map(to_customer, rows))
    return customers


@router.put("/customers/", status_code=status.HTTP_204_NO_CONTENT, tags=["users"])
async def insert_customers(customers: list[Customer]) -> None:
    rows: list[dict[str, Any]] = list(map(lambda customer: vars(customer), customers))
    await database.execute_many(query=INSERT_CUSTOMER, values=rows)
    return None
