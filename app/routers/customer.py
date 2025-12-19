from fastapi import APIRouter

from app.db.database_config import database
from app.model.customer import Customer

router = APIRouter()


def to_customer(row) -> Customer:
    return Customer(first_name=row.first_name, last_name=row.last_name)


@router.get("/customers/", tags=["users"])
async def read_customers() -> list[Customer]:
    rows = await database.fetch_all(query="select * from customers")
    customers: list[Customer] = list(map(lambda row: to_customer(row), rows))
    return customers
