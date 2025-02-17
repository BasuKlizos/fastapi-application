from datetime import datetime, timezone
from typing import Optional, Union

from pydantic import BaseModel, EmailStr


class Userbase(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = "user"
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: Optional[datetime] = None
    deleted: bool = False


class UserCreate(Userbase):
    password: str


class AdminCreate(Userbase):
    password: str
    role: str = "admin"


class GetUserData(BaseModel):
    id: str  # MongoDB ObjectId as string
    username: str
    email: str
    role: str
    created_at: datetime


class UserResponse(BaseModel):
    msg: Optional[str] = None
    data: GetUserData
    # class Config:
    #     exclude_none = True


class LoginRequest(BaseModel):
    email_or_username: Union[EmailStr, str]
    password: str

class LoginResponse(UserResponse):
    access_token : str
