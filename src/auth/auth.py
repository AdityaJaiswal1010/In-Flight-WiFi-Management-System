# src/auth/auth.py
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, requests
from src.auth.middleware import get_current_user
from prisma import Prisma
from passlib.hash import bcrypt
from src.auth.jwt_utils import create_access_token, decode_access_token
from src.models.schemas import RegisterRequest, LoginRequest, AdminCredentials, ConvertRequest
from dotenv import load_dotenv
import os
import requests 
from fastapi import Request, HTTPException  

load_dotenv(dotenv_path="./prisma/.env")
LAMBDA_EMAIL_URL = os.getenv("LAMBDA_EMAIL_URL")
def get_auth_router(db: Prisma) -> APIRouter:
    router = APIRouter()

    @router.post("/register")
    async def register(data: RegisterRequest):
        user_exists = await db.user.find_unique(where={"email": data.email})
        if user_exists:
            raise HTTPException(status_code=400, detail="User already exists")

        hashed_pw = bcrypt.hash(data.password)
        user = await db.user.create(
            {
                "email": data.email,
                "password": hashed_pw
            }
        )
        token = create_access_token({"user_id": user.id, "email": user.email})
        return {"access_token": token}

    @router.post("/login")
    async def login(data: LoginRequest):
        user = await db.user.find_unique(where={"email": data.email})
        if not user or not bcrypt.verify(data.password, user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = create_access_token({"user_id": user.id, "email": user.email})
        return {"access_token": token}



    @router.get("/protected")
    async def protected(user_data: dict = Depends(get_current_user)):
        return {"message": "You are logged in", "user": user_data}
    
    @router.get("/users")
    async def get_all_users(data: AdminCredentials):
        if data.password==os.getenv("ADMIN_PASSWORD"):
            db = Prisma()
            await db.connect()
            
            users = await db.user.find_many()
            
            await db.disconnect()
            return users
        else:
            return {"Incorrect credential, Unauthorised"}
        
    
    @router.post("/convert")
    async def convert_points(request: Request, req: ConvertRequest):
        # Step 1: Extract token from Authorization header
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

        token = auth_header.split(" ")[1]

        # Step 2: Decode the token manually
        try:
            payload = decode_access_token(token)
            user_id = payload.get("user_id")
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid token payload")
        except Exception as e:
            raise HTTPException(status_code=401, detail=str(e))

        # Step 3: Fetch user and apply conversion
        user = await db.user.find_unique(where={"id": user_id})
        if not user:
            raise HTTPException(404, detail="User not found")

        if int(req.amount) < 100:
            raise HTTPException(400, detail="Minimum ₹100 required to convert")

        if int(user.bank_balance) < int(req.amount):
            raise HTTPException(400, detail="Not enough bank balance")

        # Step 4: Update user points and balance
        await db.user.update(
            where={"id": user_id},
            data={
                "bank_balance": int(user.bank_balance) - int(req.amount),
                "points": int(user.points) + int(req.amount)
            }
        )

        # Optional: record conversion transaction
        await db.transaction.create({
            "user_id": user_id,
            "points_added": req.amount,
            "amount_deducted": req.amount
        })


        return {"message": f"{req.amount} points added to your account."}

    @router.post("/purchase/{item_id}")
    async def buy_item(item_id: str, request: Request):
        # Extract and decode JWT manually
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid token")
        
        token = auth_header.split(" ")[1]
        payload = decode_access_token(token)
        user_id = payload.get("user_id")

        # Fetch user
        user = await db.user.find_unique(where={"id": user_id})
        if not user:
            raise HTTPException(404, detail="User not found")

        # Fetch item
        item = await db.menuitem.find_unique(where={"id": item_id})
        if not item:
            raise HTTPException(404, detail="Item not found")

        # Check if user has enough points
        if user.points < item.cost_points:
            raise HTTPException(400, detail="Not enough points")

        # Deduct points and record purchase
        await db.user.update(
            where={"id": user_id},
            data={"points": user.points - item.cost_points}
        )

        await db.purchase.create({
            "user_id": user_id,
            "item_id": item_id
        })
        # Send purchase confirmation email via Lambda
        print(user.email)
        email = user.email
        item_name = item.name

        if not email or not item_name:
            print("Missing email or item_name in payload:", event)
            return {
                "statusCode": 400,
                "body": "Missing email or item_name"
            }

        # requests.post(LAMBDA_EMAIL_URL, json={
        #     "email": email,
        #     "item_name": item_name
        # })
        return {"message": f"You purchased {item.name}"}

    @router.get("/purchases")
    async def view_purchases(user_data: dict = Depends(get_current_user)):
        return await db.purchase.find_many(
            where={"user_id": user_data["user_id"]},
            include={"item": True}
        )
    @router.post("/menu/seed")
    async def seed_menu():
        items = [
            {
                "name": "WiFi Basic",
                "type": "WIFI",
                "cost_points": 300,
                "description": "Internet for 1 hour"
            },
            {
                "name": "Veg Sandwich",
                "type": "FOOD",
                "cost_points": 200,
                "description": "Healthy snack"
            }
        ]
        for item in items:
            await db.menuitem.create(data=item)
        return {"message": f"Seeded {len(items)} menu items."}

    @router.get("/menu")
    async def get_menu(type: Optional[str] = Query(None, description="Filter by type (WIFI, FOOD, DRINK, MERCH, UPGRADE)")):
        if type:
            return await db.menuitem.find_many(where={"type": type.upper()})
        return await db.menuitem.find_many()

    @router.get("/me")
    async def get_user_points(request: Request):
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing token")

        token = auth_header.split(" ")[1]
        payload = decode_access_token(token)
        user_id = payload.get("user_id")

        user = await db.user.find_unique(where={"id": user_id})
        if not user:
            raise HTTPException(404, detail="User not found")

        return {
            "email": user.email,
            "points": user.points,
            "bank_balance": user.bank_balance
        }

    return router
                        
