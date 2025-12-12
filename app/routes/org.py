from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse
from ..schemas import OrgCreateRequest, OrgMeta
from ..services.org_service import OrgService
from ..dependencies import require_admin

router = APIRouter()

@router.post("/create", response_model=OrgMeta, status_code=status.HTTP_201_CREATED)
def create_org(payload: OrgCreateRequest):
    """
    Create an organization and its admin (master DB).
    """
    res = OrgService.create_org(payload.organization_name.strip(), payload.email, payload.password)
    body = {"name": res["name"], "collection": res["collection"], "admin_email": res["admin_email"]}
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=body)


@router.get("/get", response_model=OrgMeta)
def get_org(organization_name: str):
    """
    Get organization metadata by name. Returns admin_email as well (fetched from master admins collection).
    Example: /org/get?organization_name=acme_corp
    """
    org = OrgService.get_org_by_name(organization_name.strip())
    if not org:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": "Organization not found"})
    body = {"name": org["name"], "collection": org["collection"], "admin_email": org.get("admin_email")}
    return body


@router.put("/update", status_code=status.HTTP_200_OK)
def update_org(current_name: str, new_name: str, admin=Depends(require_admin)):
    """
    Rename organization (requires admin token).
    Request example query params:
    - current_name=old_org
    - new_name=new_org
    """
    # ensure the caller belongs to the same org
    if admin.get("org") != current_name and admin.get("org") != new_name:
        # admin token must be for same org being changed (either current or new if allowed)
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "Not authorized for this org"})
    res = OrgService.update_org_name(current_name.strip(), new_name.strip())
    return JSONResponse(status_code=status.HTTP_200_OK, content=res)


@router.delete("/delete", status_code=status.HTTP_200_OK)
def delete_org(org_name: str, admin=Depends(require_admin)):
    """
    Delete organization and related data (requires admin token).
    """
    # check admin belongs to same org
    if admin.get("org") != org_name:
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "Not authorized for this org"})
    res = OrgService.delete_org(org_name.strip())
    return JSONResponse(status_code=status.HTTP_200_OK, content=res)
