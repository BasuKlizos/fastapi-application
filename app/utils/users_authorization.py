from bson.objectid import ObjectId

from fastapi import HTTPException

from app.database import users_collection


class UserAuthorization:

    @classmethod
    async def get_users(
        cls, page=1, page_size=10, username=None, email=None, role=None
    ):
        try:
            query = {"deleted": False}

            if username:
                query["username"] = {
                    "$regex": username,
                    "$options": "i",
                }
            if email:
                query["email"] = {"$regex": email, "$options": "i"}
            if role:
                query["role"] = role

            total_users = await users_collection.count_documents(query)

            users_cursor = (
                users_collection.find(query)
                .skip((page - 1) * page_size)
                .limit(page_size)
            )
            users = await users_cursor.to_list(length=page_size)

            for user in users:
                user["_id"] = str(user["_id"])

            return users, total_users
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error fetching users: {str(e)}"
            )

    @classmethod
    async def get_user_by_id(cls, user_id: str):
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID format")

        user = await users_collection.find_one(
            {"$and": [{"_id": ObjectId(user_id)}, {"deleted": False}]}
        )
        # print("*********************************")
        # print(user)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user
