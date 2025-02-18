from datetime import datetime, timezone
from typing import Optional, Union, List

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
    access_token: str


class TrashBase(BaseModel):
    original_user_id: str
    deleted_at: datetime = datetime.now(timezone.utc)
    deleted_by: str
    reason: Optional[str] = None


class TrashResponse(BaseModel):
    msg: Optional[str] = None
    trash_data: TrashBase


class UserUpdateRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None


class BatchDeleteRequest(BaseModel):
    user_ids: List[str]
    reason: Optional[str] = "No reason provided"


class TrashedUserResponse(BaseModel):
    id: str
    original_user_id: str
    deleted_at: datetime
    deleted_by: str
    reason: Optional[str] = "No reason provided"
