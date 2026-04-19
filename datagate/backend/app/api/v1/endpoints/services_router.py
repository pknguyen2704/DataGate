from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from app import models
from app.api import deps
from app.models.service_model import Service
from app.schemas.service_schema import ServiceOut as ServiceSchema
from app.schemas.service_schema import ServiceCreate, ServiceUpdate, ServiceExplore
from app.services.connection_manager_service import (
    test_connection as db_test_connection,
    get_schemas as db_get_schemas,
    get_tables as db_get_tables,
)

router = APIRouter()

# =============================================================================
# 1. HELPERS & PERMISSIONS (CÁC HÀM HỖ TRỢ & PHÂN QUYỀN)
# =============================================================================

def _get_accessible_services_query(db: Session, current_user: models.User):
    """
    Tạo truy vấn để lấy danh sách các Service mà người dùng hiện tại có quyền truy cập.
    Admin (superuser) sẽ thấy tất cả, người dùng thường chỉ thấy service của họ.
    """
    query = db.query(Service).filter(Service.is_active == True)
    if current_user.is_superuser:
        return query
    return query.filter(Service.owner_id == current_user.id)

def _get_owned_service(db: Session, service_id: int, current_user: models.User) -> Service:
    """
    Lấy thông tin Service theo ID và kiểm tra quyền sở hữu.
    Nếu không tìm thấy hoặc không có quyền, sẽ ném ra lỗi HTTP tương ứng.
    """
    service = db.query(Service).filter(
        Service.id == service_id,
        Service.is_active == True
    ).first()
    if not service:
        raise HTTPException(status_code=404, detail="Không tìm thấy dịch vụ kết nối")
    
    if not current_user.is_superuser and service.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Bạn không có quyền truy cập dịch vụ này")
    
    return service

def get_service_by_table_or_403(db: Session, current_user: models.User, table_name: str, service_id: Optional[int] = None) -> Service:
    """
    Tìm Service quản lý một bảng cụ thể và kiểm tra quyền truy cập của người dùng.
    Dùng để bảo vệ các API liên quan đến chi tiết bảng (Assets).
    Nếu service_id được cung cấp, sẽ kiểm tra trực tiếp service đó.
    """
    if service_id:
        service = _get_owned_service(db, service_id, current_user)
        for it in service.integrated_tables or []:
            if it == table_name or it.endswith(f".{table_name}"):
                return service
        raise HTTPException(status_code=404, detail="Bảng dữ liệu không thuộc dịch vụ này")

    services = _get_accessible_services_query(db, current_user).all()
    for s in services:
        for it in s.integrated_tables or []:
            if it == table_name or it.endswith(f".{table_name}"):
                return s
    raise HTTPException(status_code=403, detail="Bạn không có quyền truy cập bảng dữ liệu này")

def _filter_tables_by_integration(discovered_tables: List[str], integrated_tables: Optional[List[str]], schema: Optional[str] = None) -> List[str]:
    """Lọc danh sách bảng thực tế từ DB chỉ giữ lại những bảng đã được đăng ký (integrated)."""
    if not integrated_tables:
        return discovered_tables
    
    allowed = set(integrated_tables)
    filtered = []
    for table in discovered_tables:
        full_name = f"{schema}.{table}" if schema else table
        if table in allowed or full_name in allowed:
            filtered.append(table)
    return filtered

def _filter_schemas_by_integration(discovered_schemas: List[str], integrated_tables: Optional[List[str]]) -> List[str]:
    """Lọc danh sách schema dựa trên các bảng đã đăng ký."""
    if not integrated_tables:
        return discovered_schemas
    
    allowed_schemas = {t.split(".", 1)[0] for t in integrated_tables if "." in t}
    return [s for s in discovered_schemas if s in allowed_schemas]


# =============================================================================
# 2. SERVICE ENDPOINTS (QUẢN LÝ KẾT NỐI)
# =============================================================================

@router.get("", response_model=List[ServiceSchema])
def get_services(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Lấy danh sách tất cả các Service mà user có quyền truy cập."""
    return _get_accessible_services_query(db, current_user).all()

@router.post("", response_model=ServiceSchema)
def create_service(
    service_in: ServiceCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Tạo mới hoặc tái kích hoạt một kết nối Service."""
    # Kiểm tra sự tồn tại của tên (bao gồm cả bản ghi đã xoá mềm)
    existing_any = db.query(Service).filter(Service.name == service_in.name).first()
    
    if existing_any:
        if existing_any.is_active:
            raise HTTPException(
                status_code=400,
                detail=f"Dịch vụ với tên '{service_in.name}' đã tồn tại và đang hoạt động."
            )
        else:
            # Nếu đã bị xoá mềm, chúng ta sẽ cập nhật và tái kích hoạt bản ghi này
            test_res = db_test_connection(service_in.connection_url)
            is_active = (test_res["status"] == "success")
            
            update_data = service_in.model_dump()
            for field, value in update_data.items():
                setattr(existing_any, field, value)
            
            existing_any.is_active = is_active
            existing_any.owner_id = current_user.id
            db.add(existing_any)
            db.commit()
            db.refresh(existing_any)
            return existing_any

    # Trường hợp chưa tồn tại bất kỳ bản ghi nào trùng tên
    test_res = db_test_connection(service_in.connection_url)
    is_active = (test_res["status"] == "success")

    db_service = Service(
        **service_in.model_dump(),
        is_active=is_active,
        owner_id=current_user.id,
    )
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service

@router.put("/{service_id}", response_model=ServiceSchema)
def update_service(
    service_id: int,
    service_in: ServiceUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Cập nhật thông tin Service hiện có."""
    db_service = _get_owned_service(db, service_id, current_user)
    update_data = service_in.model_dump(exclude_unset=True)

    # Kiểm tra trùng tên khi cập nhật
    if "name" in update_data and update_data["name"] != db_service.name:
        existing_service = db.query(Service).filter(
            Service.name == update_data["name"],
            Service.id != service_id,
            Service.is_active == True
        ).first()
        if existing_service:
            raise HTTPException(
                status_code=400,
                detail=f"Dịch vụ với tên '{update_data['name']}' đã tồn tại."
            )

    if "connection_url" in update_data:
        test_res = db_test_connection(update_data["connection_url"])
        db_service.is_active = (test_res["status"] == "success")

    for field, value in update_data.items():
        setattr(db_service, field, value)

    db.add(db_service)
    db.commit()

    db.refresh(db_service)
    return db_service

@router.delete("/{service_id}")
def delete_service(
    service_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Xóa mềm một Service bằng cách tắt trạng thái hoạt động."""
    service = _get_owned_service(db, service_id, current_user)
    service.is_active = False
    db.add(service)
    db.commit()
    return {"status": "success", "message": "Đã xóa dịch vụ thành công"}


# =============================================================================
# 3. DISCOVERY (KHÁM PHÁ DỮ LIỆU BAN ĐẦU)
# =============================================================================

@router.post("/test")
def test_connection(
    service: ServiceCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Kiểm tra thử kết nối DB (dùng khi user đang nhập form tạo mới)."""
    result = db_test_connection(service.connection_url)
    if result["status"] == "success":
        result["schemas"] = db_get_schemas(service.connection_url)
    return result

@router.get("/raw/tables")
def get_raw_tables(
    url: str,
    schema: Optional[str] = None,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Lấy danh sách bảng trực tiếp từ database nguồn cho bước Discovery."""
    return db_get_tables(url, schema)

@router.get("/{service_id}/schemas")
def get_service_schemas(
    service_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Lấy danh sách các schema (database) của một Service."""
    service = _get_owned_service(db, service_id, current_user)
    schemas = db_get_schemas(service.connection_url)
    return _filter_schemas_by_integration(schemas, service.integrated_tables)

@router.get("/{service_id}/tables")
def get_service_tables(
    service_id: int,
    schema: Optional[str] = None,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Lấy danh sách các bảng của một Service, có thể lọc theo schema."""
    service = _get_owned_service(db, service_id, current_user)
    tables = db_get_tables(service.connection_url, schema)
    return _filter_tables_by_integration(tables, service.integrated_tables, schema)


