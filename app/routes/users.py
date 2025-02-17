from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from app.utils.role_required_decorators import role_required

from app.database import users_collection 


users_route = APIRouter(prefix="/user")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@users_route.get("/get-users")
@role_required("admin")  # Only accessible by "admin" role
async def get_all_users(token: str = Depends(oauth2_scheme)):
    users = await users_collection.find().to_list(length=100)
    return users