from fastapi import APIRouter, Depends, status, HTTPException, Query
from fastapi.security import OAuth2PasswordBearer
from app.utils.role_required_decorators import role_required

from app.database import users_collection
from app.utils.users_authorization import UserAuthorization


users_route = APIRouter(prefix="/user")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


@users_route.get("/get-users", status_code=status.HTTP_200_OK)
@role_required("admin")  # Only accessible by "admin" role
async def get_all_users(
    token: str = Depends(oauth2_scheme),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    username: str = Query(None),
    email: str = Query(None),
    role: str = Query(None),
):
    try:
        users, total_users = await UserAuthorization.get_users(
            page=page,
            page_size=page_size,
            username=username,
            email=email,
            role=role)
        # response = []

        # for user in users:
        #     response.append(
        #         {
        #             "id": str(user["_id"]),
        #             "username": user["username"],
        #             "email": user["email"],
        #             "role": user["role"],
        #             "created_at": user["created_at"],
        #             "updated_at": user["updated_at"],
        #             "deleted": user["deleted"],
        #         }
        #     )

        # return response

        return {
            "page": page,
            "page_size": page_size,
            "total_users": total_users,
            "total_pages": (total_users + page_size - 1) // page_size,  # Calculate total pages
            "users": users
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching users: {str(e)}")
