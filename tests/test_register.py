import pytest
from httpx import AsyncClient
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

@pytest.mark.asyncio
async def test_register_success():
    async with AsyncClient(app=app, base_url="http://test") as client:
        res = await client.post("/register", json={
            "email": "test@example.com",
            "password": "secure123"
        })
        assert res.status_code == 200
        assert "access_token" in res.json()

@pytest.mark.asyncio
async def test_register_duplicate():
    async with AsyncClient(app=app, base_url="http://test") as client:
        await client.post("/register", json={
            "email": "test2@example.com",
            "password": "secure123"
        })
        res = await client.post("/register", json={
            "email": "test2@example.com",
            "password": "secure123"
        })
        assert res.status_code == 400
