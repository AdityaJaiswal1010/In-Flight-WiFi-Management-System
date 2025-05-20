import pytest
from httpx import AsyncClient
from app import app

@pytest.mark.asyncio
async def test_full_user_journey():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        
        # 1. LOGIN
        login_response = await ac.post("/login", json={
            "email": "aditya@gmail.com",
            "password": "Aditya"
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. GET MENU TO FETCH PRICE
        menu_response = await ac.get("/menu", headers=headers)
        assert menu_response.status_code == 200
        menu_items = menu_response.json()
        
        # Find the item you want to purchase
        item_id = "5063247f-a17d-48b1-a67c-aad241a27df6"
        item = next((i for i in menu_items if i["id"] == item_id), None)
        assert item is not None, "Menu item not found"
        cost_points = item["cost_points"]

        # 3. CONVERT POINTS
        convert_response = await ac.post("/convert", json={
            "account_id": item_id,
            "points": cost_points
        }, headers=headers)
        assert convert_response.status_code == 200

        # 4. PURCHASE
        purchase_response = await ac.post("/purchases", json={
            "account_id": item_id,
            "item": item["name"],
            "price": item["cost_points"]
        }, headers=headers)
        assert purchase_response.status_code in [200, 201]
        purchase_data = purchase_response.json()
        assert purchase_data["item"] == item["name"]
        assert purchase_data["price"] == item["cost_points"]
