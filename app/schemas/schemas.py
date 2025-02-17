from datetime import datetime, timezone

from pydantic import BaseModel, EmailStr


class Userbase(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = "user"
    created_at: datetime
    updated_at: datetime 
    deleted: bool = False


class UserCreate(Userbase):
    password: str


class AdminCreate(Userbase):
    password: str
    role: str = "admin"


class UserResponse(Userbase):
    id: str  # MongoDB ObjectId as a string

    class Config:
        orm_mode = True