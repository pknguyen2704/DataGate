from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.db.session import get_db
from app.models import User
from app.rbac.permissions import PermissionCode
from app.schemas.lab_schema import NotebookEmbedUrlOut
from app.services.lab_service import LabService

lab_router = APIRouter(prefix="/lab", tags=["Lab"])


def get_lab_service(db: Session = Depends(get_db)) -> LabService:
    return LabService(db)


@lab_router.get("/notebook", response_model=NotebookEmbedUrlOut)
def notebook(
    service: LabService = Depends(get_lab_service),
    _user: User = Depends(require_permission(PermissionCode.LAB_VIEW)),
):
    return {"url": service.get_notebook_url()}
