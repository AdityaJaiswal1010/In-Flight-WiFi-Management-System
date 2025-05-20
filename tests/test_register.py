import pytest
from starlette.testclient import TestClient
from app import app
from prisma import Prisma

client = TestClient(app)
db = Prisma()

@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown():
    import asyncio
    asyncio.run(db.connect())
    yield
    asyncio.run(db.disconnect())

def test_register_success():
    response = client.post("/register", json={
        "email": "test@example.com",
        "password": "secure123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_register_duplicate():
    client.post("/register", json={
        "email": "test2@example.com",
        "password": "secure123"
    })
    response = client.post("/register", json={
        "email": "test2@example.com",
        "password": "secure123"
    })
    assert response.status_code == 400
