import os
from datetime import datetime, timezone, timedelta

from jose import JWTError, jwt
from fastapi import HTTPException

from app.config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM


def generate_access_token(user_data: dict):
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    payload = {
        "sub":str(user_data["_id"]),
        "username": user_data["username"],
        "role": user_data["role"],
        "iat": datetime.now(timezone.utc),
        "exp": expire
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        print(f"JWTError encountered: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error encountered: {e}")
        return None


def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token is invalid or expired.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while decoding the token: {e}")
