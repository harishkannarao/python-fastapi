import pytest
from databases import Database

from app.dao import customer_dao


@pytest.mark.asyncio
async def test_customers_delete(get_database: Database):
    await customer_dao.delete_all_customers(get_database)
