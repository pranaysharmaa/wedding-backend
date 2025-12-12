from fastapi import Depends, Header, HTTPException, status
from typing import Optional
from .services.auth_service import AuthService

def get_bearer_token(authorization: Optional[str] = Header(None)) -> str:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header missing")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid auth header")
    return parts[1]

def require_admin(token: str = Depends(get_bearer_token)):
    return AuthService.get_current_admin_from_token(token)
