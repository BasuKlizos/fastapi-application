import logging

import pytest
from httpx import AsyncClient
from fastapi import status
from app.database import users_collection

logging.basicConfig(level=logging.INFO)

@pytest.mark.asyncio
async def test_user_signup(async_client: AsyncClient):
    payload = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword"
    }
    response = await async_client.post("/auth/user/signup", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["msg"] == "User created successfully"
    assert data["data"]["username"] == "testuser"
    assert data["data"]["email"] == "testuser@example.com"

    await users_collection.delete_one({"email":"testuser@example.com"})
    logging.info(f"Test user successfully deleted from database")


@pytest.mark.asyncio
async def test_admin_signup(async_client: AsyncClient):
    payload = {
        "username": "testadmin",
        "email": "testadmin@example.com",
        "password": "adminpassword"
    }
    response = await async_client.post("/auth/admin/signup", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["msg"] == "Admin created successfully"
    assert data["data"]["username"] == "testadmin"
    assert data["data"]["email"] == "testadmin@example.com"

    await users_collection.delete_one({"email":"testadmin@example.com"})


# @pytest.mark.asyncio
# async def test_signup(async_client: AsyncClient):
#     test_data = {
#         "username":"testuser",
#         "email":"testuser@gmail.com",
#         "password":"testpassword"
#     }

#     response = await async_client.post("/auth/user/signup", json=test_data)
#     assert response.status_code == status.HTTP_201_CREATED
#     test_data_json = response.json()
#     assert test_data_json["msg"] == "User created successfully"

#     payload = {
#         "email_or_username":"testuser",
#         "password":"testuser@example.com"
#     }
#     resp = await async_client.post("/auth/login", json=payload)

#     assert resp.status_code == status.HTTP_200_OK
    
#     data = resp.json()
#     assert data["msg"] == "User successfully Logged In"
