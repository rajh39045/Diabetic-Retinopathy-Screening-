import os

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "retina_xai")

client = AsyncIOMotorClient(MONGODB_URI)

db = client[MONGODB_DATABASE]


async def connect_to_mongodb():
    await client.admin.command("ping")
    print("MongoDB connected successfully")


async def close_mongodb():
    client.close()
    print("MongoDB connection closed")