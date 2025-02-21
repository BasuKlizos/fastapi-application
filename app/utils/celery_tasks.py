import asyncio
import threading
import json

from fastapi.encoders import jsonable_encoder
from bson.objectid import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

from app.celery.celery_worker import celery_app
from app.config import settings
from app.utils.redis_dependencies import get_redis_client


def run_async_in_new_thread(coro):
    result_container = []
    exception_container = []

    def runner():
        try:
            result = asyncio.run(coro)
            result_container.append(result)
        except Exception as e:
            exception_container.append(e)

    thread = threading.Thread(target=runner)
    thread.start()
    thread.join()

    if exception_container:
        raise exception_container[0]
    return result_container[0]


@celery_app.task(name="view_trashed_users_task")
def fetch_trashed_users():
    """
    Fetch trashed users from the database
    """
    MONGO_URI = settings.MONGO_URI
    client = AsyncIOMotorClient(MONGO_URI)
    database = client["fastapi_db"]
    users_collection = database["users"]
    trash_collections = database["trash"]

    async def get_data():
        trashed_users = await trash_collections.find().to_list()

        if not trashed_users:
            raise ValueError("Trashed user not found.")

        trashed_response_data = []
        for trashed_user in trashed_users:
            user_data = {
                "id": str(trashed_user["_id"]),
                "original_user_id": trashed_user["original_user_id"],
                "deleted_at": trashed_user["deleted_at"],
                "deleted_by": trashed_user["deleted_by"],
                "reason": trashed_user["reason"],
            }
            trashed_response_data.append(user_data)

        encoded_response = jsonable_encoder(trashed_response_data)
        return encoded_response

    result = run_async_in_new_thread(get_data())
    return result


@celery_app.task(name="restore_trashed_users_task")
def restore_user_task(user_id: str):
    """
    Background Celery task to restore a trashed user.
    """
    MONGO_URI = settings.MONGO_URI
    client = AsyncIOMotorClient(MONGO_URI)
    database = client["fastapi_db"]
    users_collection = database["users"]
    trash_collections = database["trash"]

    async def restore():
        redis = await get_redis_client()

        user = await trash_collections.find_one({"original_user_id": user_id})
        if not user:
            return {"error": "User does not exist."}

        await users_collection.update_one(
            {"_id": ObjectId(user_id)}, {"$set": {"deleted_at": False}}
        )

        await trash_collections.delete_one({"original_user_id": user_id})

        cached_trashed_users = await redis.get("trashed_users")
        if cached_trashed_users:
            trashed_users = json.loads(cached_trashed_users)
            updated_users = [
                user for user in trashed_users if user["original_user_id"] != user_id
            ]
            await redis.setex("trashed_users", 600, json.dumps(updated_users))

        return {"msg": "User restored successfully."}

    return run_async_in_new_thread(restore())
