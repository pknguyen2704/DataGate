from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.db.session import get_db
from app.models import User
from app.rbac.permissions import PermissionCode, ALL_PERMISSIONS

permission_router = APIRouter(tags=["Permissions"])

from app.services.role_service import RoleService

@permission_router.get("")
def list_permissions(
    service: RoleService = Depends(lambda db: RoleService(db)),
    _user: User = Depends(require_permission(PermissionCode.USER_MANAGE)),
    db: Session = Depends(get_db)
):
    """
    List all available permissions defined in the system.
    """
    return RoleService(db).list_permissions()

@permission_router.get("/grouped")
def list_permissions_grouped(
    _user: User = Depends(require_permission(PermissionCode.USER_MANAGE)),
    db: Session = Depends(get_db)
):
    """
    List all available permissions grouped by functional area.
    """
    service = RoleService(db)
    perms = service.list_permissions()
    
    grouped = {}
    for p in perms:
        group = p.permission_group or "Other"
        if group not in grouped:
            grouped[group] = []
        grouped[group].append({
            "id": str(p.id),
            "code": p.code,
            "name": p.name,
            "group": group
        })
    return grouped
