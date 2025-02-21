import asyncio
import threading

from fastapi.encoders import jsonable_encoder
from bson.objectid import ObjectId
from asgiref.sync import async_to_sync
from motor.motor_asyncio import AsyncIOMotorClient

from app.celery.celery_worker import celery_app
from app.database import trash_collections, users_collection
from app.config import settings


class CeleryTasks:
    
    MONGO_URI = settings.MONGO_URI
    client = AsyncIOMotorClient(MONGO_URI)
    database = client["fastapi_db"]
    users_collection = database["users"]
    trash_collections = database["trash"]

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

    @celery_app.task
    def fetch_trashed_users():
        """
        Fetch trashed users from the database
        """ 
        # MONGO_URI = settings.MONGO_URI
        # client = AsyncIOMotorClient(MONGO_URI)
        # database = client["fastapi_db"]
        # users_collection = database["users"]
        # trash_collections = database["trash"]


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


# @celery_app.task
# def 