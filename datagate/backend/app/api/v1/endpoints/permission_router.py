from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.db.session import get_db
from app.models import User
from app.rbac.permissions import PermissionCode, ALL_PERMISSIONS

permission_router = APIRouter(tags=["Permissions"])

@permission_router.get("")
def list_permissions(
    _user: User = Depends(require_permission(PermissionCode.USER_VIEW)),
):
    """
    List all available permissions defined in the system.
    """
    return ALL_PERMISSIONS

@permission_router.get("/grouped")
def list_permissions_grouped(
    _user: User = Depends(require_permission(PermissionCode.USER_VIEW)),
):
    """
    List all available permissions grouped by functional area.
    """
    grouped = {}
    for p in ALL_PERMISSIONS:
        group = p.get("group", "Other")
        if group not in grouped:
            grouped[group] = []
        grouped[group].append(p)
    return grouped
