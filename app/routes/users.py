from datetime import datetime, timezone
from typing import Optional, Dict, List

from fastapi import APIRouter, Depends, status, HTTPException, Query
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from app.utils.role_required_decorators import role_required
from bson.objectid import ObjectId

from app.database import users_collection, trash_collections
from app.utils.users_authorization import UserAuthorization
from app.utils.role_required_decorators import get_current_user
from app.models import Trash
from app.schemas.schemas import (
    TrashResponse,
    TrashBase,
    UserUpdateRequest,
    BatchDeleteRequest,
    TrashedUserResponse,
)
from app.utils.hashing import hash_password


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
            role=role,
        )
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
            "total_pages": (total_users + page_size - 1)
            // page_size,  # Calculate total pages
            "users": users,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching users: {str(e)}"
        )


@users_route.get("/get-user/{user_id}", status_code=status.HTTP_200_OK)
async def get_user_by_id(user_id: str, token: str = Depends(oauth2_scheme)):
    try:
        user = await UserAuthorization.get_user_by_id(user_id)
        # print("----------------------------------------------------")
        # print(user)

        if not user:
            raise HTTPException(
                status_code=404, detail="User not found or has been deleted"
            )

        response = {
            "id": str(user["_id"]),
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
            "created_at": user["created_at"],
            "updated_at": user["updated_at"],
            "deleted": user["deleted"],
        }

        return response
    except Exception as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching user: {str(e)}"
        )


@users_route.put("/update-user/{user_id}", status_code=status.HTTP_200_OK)
async def user_update_by_id(
    user_id: str,
    user_data: UserUpdateRequest,
    token: str = Depends(oauth2_scheme),
):

    user = await UserAuthorization.get_user_by_id(user_id)
    # print("-------------------------")
    # print(user)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or has been deleted",
        )

    updated_data: Dict = {}

    for field in ["username", "email", "password"]:
        if getattr(user_data, field) is not None:
            updated_data[field] = getattr(user_data, field)

    if user_data.password:
        updated_data["password"] = hash_password(user_data.password)

    updated_data["updated_at"] = datetime.now(timezone.utc)

    result = await users_collection.update_one(
        {"_id": ObjectId(user_id)}, {"$set": updated_data}
    )

    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User update failed",
        )

    return {"message": "User updated successfully"}


@users_route.delete(
    "/delete/{user_id}",
    response_model=TrashResponse,
    status_code=status.HTTP_200_OK,
)
@role_required("admin")
async def delete_user_by_id(
    user_id: str,
    token: str = Depends(oauth2_scheme),
    reason: Optional[str] = None,
):
    try:
        current_user = await get_current_user(token)
        # print("------------------------------")
        # print(current_user)

        user = await UserAuthorization.get_user_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=404, detail="User not found or has been deleted"
            )

        trash_data = Trash(
            original_user_id=user_id,
            deleted_by=current_user["username"],
            reason=reason,
        )

        trash_data_dict = trash_data.to_dict()
        await trash_collections.insert_one(trash_data_dict)

        await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "deleted": True,
                    "updated_at": datetime.now(timezone.utc),
                }
            },
        )

        trash_response = TrashResponse(
            msg="User deleted successfully",
            trash_data=TrashBase(
                original_user_id=trash_data_dict["original_user_id"],
                deleted_at=trash_data_dict["deleted_at"],
                deleted_by=trash_data_dict["deleted_by"],
                reason=trash_data_dict["reason"],
            ),
        )

        trash_response_dict = trash_response.model_dump()
        return trash_response_dict
    except Exception as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching user: {str(e)}"
        )


@users_route.post("/batch-delete", status_code=status.HTTP_200_OK)
@role_required("admin")
async def batch_delete_users(
    request_data: BatchDeleteRequest, token: str = Depends(oauth2_scheme)
):
    user_ids = request_data.user_ids
    reason = request_data.reason

    if not user_ids:
        raise HTTPException(status_code=400, detail="No user IDs provided")

    current_user = await get_current_user(token)

    # Convert user_ids from string to ObjectId
    object_ids = [ObjectId(user_id) for user_id in user_ids]

    users_cursor = users_collection.find(
        {"_id": {"$in": object_ids}, "deleted": False}
    )

    users = await users_cursor.to_list(length=100)
    if not users:
        raise HTTPException(
            status_code=404, detail="No users found for deletion"
        )

    # Soft delete users and move them to trash collection
    for user in users:
        trash_model = TrashBase(
            original_user_id=str(user["_id"]),
            deleted_at=datetime.now(timezone.utc),
            deleted_by=current_user["username"],
            reason=reason,
        )

        await trash_collections.insert_one(trash_model.model_dump())

        await users_collection.update_one(
            {"_id": user["_id"]}, {"$set": {"deleted": True}}
        )

    return {"message": f"Successfully soft-deleted {len(users)} users"}


# I will update this route later
@users_route.get(
    "/view-trash",
    response_model=List[TrashedUserResponse],
    status_code=status.HTTP_200_OK,
)
@role_required("admin")
async def view_trash(token: str = Depends(oauth2_scheme)):
    try:
        trashed_users_cursor = trash_collections.find()
        trashed_users = await trashed_users_cursor.to_list(
            length=100
        )  # Limit to 100 users for performance
        print("---------------------------------------")
        print(trashed_users)

        if not trashed_users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No trashed users found.",
            )

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

        return response_trashed_users

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving trashed users: {str(e)}",
        )


@users_route.post("/restore/{user_id}", status_code=status.HTTP_200_OK)
@role_required("admin")
async def restore_user(user_id: str, token: str = Depends(oauth2_scheme)):

    trash_user = await trash_collections.find_one(
        {"original_user_id": user_id}
    )
    if not trash_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in trash",
        )

    result = await users_collection.update_one(
        {"_id": ObjectId(user_id)}, {"$set": {"deleted": False}}
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or already restored",
        )

    await trash_collections.delete_one({"original_user_id": user_id})

    return JSONResponse(content={"message": "User restored successfully"})


@users_route.delete("/trash/{user_id}", status_code=status.HTTP_200_OK)
@role_required("admin")
async def permanent_delete_user(
    user_id: str, token: str = Depends(oauth2_scheme)
):

    trash_user = await trash_collections.find_one({"_id": ObjectId(user_id)})
    if not trash_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in trash",
        )

    await trash_collections.delete_one({"_id": ObjectId(user_id)})

    return JSONResponse(content={"message": "User permanently deleted"})