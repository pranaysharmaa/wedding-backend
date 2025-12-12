from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from ..schemas import AdminLoginRequest, TokenResponse
from ..services.auth_service import AuthService

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
def admin_login(payload: AdminLoginRequest):
    """
    Admin login. Returns JWT access token on success.
    """
    res = AuthService.authenticate_admin(payload.email, payload.password)
    return JSONResponse(status_code=status.HTTP_200_OK, content=res)
