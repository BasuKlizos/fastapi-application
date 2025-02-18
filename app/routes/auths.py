from fastapi import APIRouter, status, HTTPException
from app.models import User
from app.schemas.schemas import (
    UserResponse,
    UserCreate,
    AdminCreate,
    LoginRequest,
    GetUserData,
    LoginResponse,
)
from app.utils.users_validation import UserValidation
from app.utils.hashing import hash_password
from app.database import users_collection
from app.utils.jwt import generate_access_token

auth_routes = APIRouter(prefix="/auth")


@auth_routes.post(
    "/user/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def user_signup(user_create: UserCreate):
    try:
        await UserValidation.is_user_exists(
            username=user_create.username, email=user_create.email
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User exists or validation failed: {str(e)}",
        )

    try:
        hashed_password = hash_password(user_create.password)
        user_create.password = hashed_password
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Password hashing failed: {str(e)}"
        )

    try:
        user_dict = user_create.model_dump()
        new_user = User(**user_dict)
        user_result = await users_collection.insert_one(new_user.to_dict())
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error inserting user: {str(e)}"
        )

    user_response = UserResponse(
        msg="User created successfully",
        data=GetUserData(
            id=UserValidation.object_id_to_str(user_result.inserted_id),
            username=user_dict["username"],
            email=user_dict["email"],
            role=user_dict["role"],
            created_at=user_dict["created_at"],
        ),
        access_token=None,  # Make sure this is explicitly set to None
    )
    user_response_dict = user_response.model_dump()
    return user_response_dict


@auth_routes.post(
    "/admin/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def admin_signup(admin_create: AdminCreate):

    try:
        await UserValidation.is_user_exists(
            username=admin_create.username, email=admin_create.email
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User exists or validation failed: {str(e)}",
        )

    try:
        hashed_password = hash_password(admin_create.password)
        admin_create.password = hashed_password
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Password hashing failed: {str(e)}",
        )

    try:
        admin_dict = admin_create.model_dump()
        new_admin_user = User(**admin_dict)
        admin_result = await users_collection.insert_one(
            new_admin_user.to_dict()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inserting admin: {str(e)}",
        )

    admin_response = UserResponse(
        msg="Admin created successfully",
        data=GetUserData(
            id=UserValidation.object_id_to_str(admin_result.inserted_id),
            username=admin_dict["username"],
            email=admin_dict["email"],
            role=admin_dict["role"],
            created_at=admin_dict["created_at"],
        ),
    )
    admin_response_dict = admin_response.model_dump()

    return admin_response_dict


@auth_routes.post(
    "/login", response_model=LoginResponse, status_code=status.HTTP_200_OK
)
async def login(user_login: LoginRequest):

    try:
        user = await UserValidation.get_user_by_email_or_username(
            user_login.email_or_username
        )
        # print("-------------------------------------------------------------------")
        # print(user)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        await UserValidation.verify_user_password(
            user["password"], user_login.password
        )

        access_token = generate_access_token(user)

        login_user_response = LoginResponse(
            msg="User successfully Logged In",
            data=GetUserData(
                id=UserValidation.object_id_to_str(user["_id"]),
                username=user["username"],
                email=user["email"],
                role=user["role"],
                created_at=user["created_at"],
            ),
            access_token=access_token,
        )
        login_user_response_dict = login_user_response.model_dump()

        return login_user_response_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
