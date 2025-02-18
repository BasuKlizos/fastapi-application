from datetime import datetime, timezone, timedelta

import jwt
import bcrypt
from fastapi import HTTPException, status

SECERT_KEY = "asdsdsjdfjsajjsdasdjjsds324^bjsdb8"
Algorithm = "HS256"


def generate_token(user_data: dict) -> str:
    expiration_time = datetime.now(timezone.utc) + timedelta(minutes=5)
    issue_at = datetime.now(timezone.utc)
    token = jwt.encode(
        {
            "sub": str(user_data["email"]),
            "iat": issue_at,
            "exp": expiration_time,
        },
        SECERT_KEY,
        algorithm=Algorithm,
    )

    return token


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECERT_KEY, algorithms=Algorithm)
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Signature Error"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Token"
        )


def create_hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password.decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        password.encode("utf-8"), hashed_password.encode("utf-8")
    )
