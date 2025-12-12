from fastapi import HTTPException, status, Depends
from ..utils.hashing import verify_password
from ..utils.jwt import create_access_token, decode_access_token
from ..database import get_master_db
from ..config import settings
from jose import JWTError

class AuthService:
    ADM_COLL = "admins"
    ORG_COLL = "organizations"

    @classmethod
    def authenticate_admin(cls, email: str, password: str) -> dict:
        db = get_master_db()
        admins = db[cls.ADM_COLL]
        admin = admins.find_one({"email": email})
        if not admin:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        if not verify_password(password, admin["password"]):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        # fetch org name from admin doc
        org_name = admin.get("org")
        # get org collection from organizations master
        org = db[cls.ORG_COLL].find_one({"name": org_name})
        if not org:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Org metadata missing")
        payload = {
            "admin_id": str(admin["_id"]),
            "org": org["name"],
            "collection": org["collection"],
        }
        token = create_access_token(payload)
        return {"access_token": token, "token_type": "bearer"}

    @classmethod
    def get_current_admin_from_token(cls, token: str) -> dict:
        try:
            payload = decode_access_token(token)
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        # basic checks
        if "admin_id" not in payload or "org" not in payload:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
        return payload
