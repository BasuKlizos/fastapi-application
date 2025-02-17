import os
from datetime import datetime, timezone, timedelta

from jose import JWTError, jwt

from config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

def generate_access_token(user_data:dict):
    to_encoded_user_data = user_data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    issue_at = datetime.utcnow()
    to_encoded_user_data.update({
        "iat":issue_at,
        "exp":expire
    })
    return jwt.encode(to_encoded_user_data, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token:str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
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
        raise ValueError("Token is invalid or expired.")
    except Exception as e:
        raise ValueError(f"An error occurred while decoding the token: {e}")
