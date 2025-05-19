from fastapi import FastAPI
from prisma import Prisma
from src.auth.auth import get_auth_router

db = Prisma()
app = FastAPI()

@app.on_event("startup")
async def connect_db():
    await db.connect()

@app.on_event("shutdown")
async def disconnect_db():
    await db.disconnect()

app.include_router(get_auth_router(db))
