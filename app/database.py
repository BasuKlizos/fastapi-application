from motor.motor_asyncio import AsyncIOMotorClient

from config import settings

MONGO_URI = settings.MONGO_URI
client = AsyncIOMotorClient(MONGO_URI)
database = client["fastapi_db"]
users_collection = database["users"]
trash_collections = database["trashs"]
