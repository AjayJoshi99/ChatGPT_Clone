from passlib.context import CryptContext
from jose import jwt , JWTError
from datetime import datetime , timedelta, timezone
from fastapi import HTTPException, status

from core.settings import settings


password_context = CryptContext(schemes=[settings.HASHING_ALGO])


def get_hashed_password(password: str) -> str:
    hashed = password_context.hash(password)
    return hashed


def verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)


def create_access_token(payload : dict, expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.now(timezone.utc) + expires_delta
    else:
        expires_delta = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload.update({"exp": expires_delta})
    payload.update({"type": "access"})
    encoded_jwt = jwt.encode(payload, settings.SECRET_KEY_ACCESS_TOKEN, settings.TOKEN_ENCODE_ALGORITHM)
    return encoded_jwt


def create_refresh_token(payload : dict, expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.now(timezone.utc) + expires_delta
    else:
        expires_delta = datetime.now(timezone.utc) + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

    payload.update({"exp": expires_delta})
    payload.update({"type": "refresh"})
    encoded_jwt = jwt.encode(payload, settings.SECRET_KEY_REFRESH_TOKEN, settings.TOKEN_ENCODE_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY_ACCESS_TOKEN, algorithms=[settings.TOKEN_ENCODE_ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

def decode_refresh_token(token : str) -> dict :
    user = jwt.decode(token, settings.SECRET_KEY_REFRESH_TOKEN, settings.TOKEN_ENCODE_ALGORITHM)
    return user