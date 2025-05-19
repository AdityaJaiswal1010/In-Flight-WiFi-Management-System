import pytest
from starlette.testclient import TestClient
from app import app
from prisma import Prisma

client = TestClient(app)

def test_register_success():
    res = client.post("/register", json={
        "email": "test@example.com",
        "password": "secure123"
    })
    assert res.status_code == 200
    assert "access_token" in res.json()

def test_register_duplicate():
    client.post("/register", json={
        "email": "test2@example.com",
        "password": "secure123"
    })
    res = client.post("/register", json={
        "email": "test2@example.com",
        "password": "secure123"
    })
    assert res.status_code == 400
