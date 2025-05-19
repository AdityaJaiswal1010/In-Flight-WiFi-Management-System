# app.py
from fastapi import FastAPI
from prisma import Prisma
from src.auth.auth import get_auth_router

app = FastAPI()
db = Prisma()

@app.on_event("startup")
async def on_startup():
    await db.connect()

@app.on_event("shutdown")
async def on_shutdown():
    await db.disconnect()

# Pass the shared Prisma instance to the auth router
app.include_router(get_auth_router(db))
