import json
import asyncio

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from bson.objectid import ObjectId

from app.celery.celery_worker import celery_app
from app.database import trash_collections, users_collection
# from app.redis.redis import redis_client
from app.main import app 


class CeleryTasks:
    @staticmethod
    @celery_app.task
    def fetch_trashed_users():
        """Sync Celery task that runs the async function."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(CeleryTasks.fetch_trashed_users_async())

    @staticmethod
    async def fetch_trashed_users_async():
        """Background task to fetch trashed users and cache them in Redis."""
        trashed_users_cursor = trash_collections.find()
        trashed_users = await trashed_users_cursor.to_list(
            length=100
        )  # Limit to 100 users for performance
        # print("---------------------------------------")
        # print(trashed_users)

        if not trashed_users:
            return {"message": "No trashed users found."}

        response_trashed_users = []
        for trashed_user in trashed_users:
            user_data = {
                "id": str(trashed_user["_id"]),
                "original_user_id": trashed_user["original_user_id"],
                "deleted_at": trashed_user["deleted_at"],
                "deleted_by": trashed_user["deleted_by"],
                "reason": trashed_user["reason"],
            }
            response_trashed_users.append(user_data)

        redis_client = app.state.redis_client

        # Cache data in Redis for 30 minutes (1800 seconds)
        await redis_client.setex(
            "redis_trashed_users", 1800, json.dumps(response_trashed_users)
        )

        return response_trashed_users

    @staticmethod
    @celery_app.task
    def restore_user_from_trash_task(user_id: str):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(CeleryTasks.restore_user_from_trash_task_async(user_id))

    @staticmethod
    async def restore_user_from_trash_task_async(user_id: str):
        """Background task to restore a user from the trash and update Redis cache."""
        trash_user = await trash_collections.find_one({"original_user_id": user_id})
        if not trash_user:
            return {"msg": "User not found in trash"}

        result = await users_collection.update_one(
            {"_id": ObjectId(user_id)}, {"$set": {"deleted": False}}
        )

        if result.matched_count == 0:
            return {"msg": "User not found or already restored"}

        await trash_collections.delete_one({"original_user_id": user_id})

        redis_client = app.state.redis_client

        cached_trash_data = redis_client.get("redis_trashed_users")
        if cached_trash_data:
            trashed_users = json.loads(cached_trash_data)
            updated_users = [
                user for user in trashed_users if user["original_user_id"] != user_id
            ]
            redis_client.setex("redis_trashed_users", 1800, json.dumps(updated_users))

        return JSONResponse(content={"message": "User restored successfully"})
