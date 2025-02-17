from bson.objectid import ObjectId

from fastapi import HTTPException
from passlib.context import CryptContext

from app.database import users_collection


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserValidation:

    @classmethod
    async def is_user_exists(cls, username: str = None, email: str = None):
        if username:
            user_by_username = await users_collection.find_one({"username": username})
            if user_by_username:
                raise HTTPException(status_code=400, detail="Username already exists")
        if email:
            user_by_email = await users_collection.find_one({"email": email})
            if user_by_email:
                raise HTTPException(status_code=400, detail="Email already exists")

    @classmethod
    async def get_user_by_email_or_username(cls, email_or_username: str):
        user = await users_collection.find_one(
            {"$or": [{"email": email_or_username}, {"username": email_or_username}]}
        )

        if not user:
            raise HTTPException(status_code=404, detail="User Not found")
        return user

    @classmethod
    async def get_user_by_id(cls, user_id: str):
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if user:
            return user
        raise HTTPException(status_code=404, detail="User not found")

    @classmethod
    async def verify_user_password(cls, hashed_password: str, password: str):

        if not pwd_context.verify(password, hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

    @classmethod
    def object_id_to_str(cls, obj):
        return str(obj) if obj else None
