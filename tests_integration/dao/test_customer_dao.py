import pytest
import pytest_asyncio
from databases import Database
from pytest import MonkeyPatch

from app.dao import customer_dao


@pytest_asyncio.fixture
def setup_dao_database(get_database: Database, monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr("app.dao.customer_dao.database", get_database)


@pytest.mark.asyncio
async def test_customers_delete(setup_dao_database: None):
    await customer_dao.delete_all_customers()
