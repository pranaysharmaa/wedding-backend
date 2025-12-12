from typing import Annotated
from pydantic import BaseModel, StringConstraints, EmailStr, Field

# Pydantic v2 replacement for constr()
OrgName = Annotated[
    str,
    StringConstraints(
        min_length=1,
        max_length=64,
        pattern=r"^[A-Za-z0-9 _\-\.\&]+$"
    )
]

class OrgCreateRequest(BaseModel):
    organization_name: OrgName
    email: EmailStr
    password: str = Field(min_length=6)


class OrgMeta(BaseModel):
    name: str
    collection: str
    admin_email: EmailStr | None = None


class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
