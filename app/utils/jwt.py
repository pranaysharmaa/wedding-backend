from datetime import datetime, timedelta
from jose import jwt, JWTError
from ..config import settings

ALGO = "HS256"


def create_access_token(data: dict, expires_hours: int | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=(expires_hours or settings.TOKEN_EXPIRE_HOURS))
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGO)
    return token


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGO])
        return payload
    except JWTError as e:
        raise e
