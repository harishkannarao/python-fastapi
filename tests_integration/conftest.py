from typing import Generator

import pytest
from starlette.testclient import TestClient

from app.main import app


@pytest.fixture
def test_client() -> Generator[TestClient, None, None]:
    with TestClient(app) as client:
        yield client
