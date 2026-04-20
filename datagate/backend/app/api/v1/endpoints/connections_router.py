from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app import models
from app.api import deps
from app.models.connection.connection import Connection
from app.models.connection.table import Table
from app.schemas.connection import ConnectionOut as ConnectionSchema
from app.schemas.connection import ConnectionCreate, ConnectionUpdate
from app.models.observability.config import ObservabilityConfig
from app.services.connection_manager_service import (
    test_connection as db_test_connection,
    get_schemas as db_get_schemas,
    get_tables as db_get_tables,
)

router = APIRouter()

# --- 1. HELPERS & RBAC (TABLE LEVEL) ---

def get_system_connection(db: Session) -> Connection:
    # Lấy kết nối duy nhất của hệ thống (mặc định ID=1)
    conn = db.query(Connection).first()
    if not conn:
        raise HTTPException(status_code=404, detail="Hệ thống chưa cấu hình kết nối Trino")
    return conn

def check_table_access(user: models.User, full_table_name: str):
    """Kiểm tra quyền truy cập của user tới một bảng cụ thể."""
    if user.is_superuser:
        return True
    
    permitted = user.accessible_tables or []
    # Kiểm tra cả tên đầy đủ schema.table hoặc chỉ table nếu không có dấu chấm
    if full_table_name in permitted:
        return True
    
    # Hỗ trợ kiểm tra linh hoạt
    if "." in full_table_name:
        table_only = full_table_name.split(".")[-1]
        if table_only in permitted:
            return True
            
    raise HTTPException(status_code=403, detail=f"Bạn không có quyền truy cập bảng {full_table_name}")

def _filter_tables_by_rbac(user: models.User, tables: List[str], schema: Optional[str] = None) -> List[str]:
    """Lọc danh sách bảng dựa trên quyền của User."""
    if user.is_superuser:
        return tables
    
    permitted = set(user.accessible_tables or [])
    filtered = []
    for t in tables:
        full_name = f"{schema}.{t}" if schema else t
        if t in permitted or full_name in permitted:
            filtered.append(t)
    return filtered

def _filter_schemas_by_rbac(user: models.User, schemas: List[str], integrated_tables: List[str]) -> List[str]:
    """Lọc danh sách schema dựa trên các bảng user được phép."""
    if user.is_superuser:
        return schemas
        
    permitted = set(user.accessible_tables or [])
    allowed_schemas = set()
    for t in permitted:
        if "." in t:
            allowed_schemas.add(t.split(".")[0])
            
    return [s for s in schemas if s in allowed_schemas]

# --- 2. CONNECTION ENDPOINTS ---

@router.get("", response_model=List[ConnectionSchema])
def get_connections(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    # Trả về kết nối duy nhất (dưới dạng list để FE không vỡ giao diện)
    conn = db.query(Connection).first()
    return [conn] if conn else []

@router.post("", response_model=ConnectionSchema)
def create_or_update_connection(
    conn_in: ConnectionCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Chỉ Admin mới có quyền cấu hình kết nối hệ thống")
        
    db_conn = db.query(Connection).first()
    
    if db_conn:
        for field, value in conn_in.model_dump().items():
            setattr(db_conn, field, value)
    else:
        db_conn = Connection(**conn_in.model_dump())
    
    db.add(db_conn)
    db.commit()
    db.refresh(db_conn)
    return db_conn

@router.put("/{connection_id}", response_model=ConnectionSchema)
def update_connection(
    connection_id: int,
    conn_in: ConnectionUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Chỉ Admin mới có quyền sửa kết nối")
        
    db_conn = db.query(Connection).filter(Connection.id == connection_id).first()
    if not db_conn:
        raise HTTPException(status_code=404, detail="Không tìm thấy kết nối")

    # Neu co update integrated_tables, dong bo vao bang integrated_tables
    if "integrated_tables" in update_data:
        tables = update_data["integrated_tables"] or []
        
        # Lay tat ca config hien tai cua connection nay
        existing_integrated = db.query(IntegratedTable).filter(IntegratedTable.connection_id == db_conn.id).all()
        existing_map = {f"{c.schema_name}.{c.table_name}": c for c in existing_integrated}
        
        # 1. Danh dau nhung bang khong con trong list la is_active = False
        for full_name, item in existing_map.items():
            if full_name not in tables:
                item.is_active = False
                db.add(item)
        
        # 2. Them hoac kich hoat cac bang moi
        for t_full in tables:
            schema, name = t_full.split('.') if '.' in t_full else ('public', t_full)
            if t_full in existing_map:
                existing_map[t_full].is_active = True
                db.add(existing_map[t_full])
            else:
                new_item = IntegratedTable(
                    connection_id=db_conn.id,
                    catalog="iceberg",
                    schema_name=schema,
                    table_name=name,
                    is_active=True
                )
                db.add(new_item)
                
        # 3. Dong bo sang ca observability_config de DAG co the chay luon
        # (Legacy support cho DAG dang query bảng nay)
        for t_full in tables:
            schema, name = t_full.split('.') if '.' in t_full else ('public', t_full)
            obs_cfg = db.query(ObservabilityConfig).filter(
                ObservabilityConfig.schema_name == schema, 
                ObservabilityConfig.table_name == name
            ).first()
            if not obs_cfg:
                db.add(ObservabilityConfig(schema_name=schema, table_name=name, is_active=True))
            else:
                obs_cfg.is_active = True
                db.add(obs_cfg)
    
    # Loai bo field nay khoi model_dump vi gio no khong con ton tai trong model Connection (JSON)
    # Nhung FE van gui len de legacy.
    filtered_update = {k: v for k, v in update_data.items() if k != "integrated_tables"}

    for field, value in filtered_update.items():
        setattr(db_conn, field, value)

    db.add(db_conn)
    db.commit()
    db.refresh(db_conn)
    
    # Append integrated_tables manually for the response schema if needed
    # (Since we removed it from Connection model but ConnectionOut schema might expect it)
    res_obj = db_conn
    all_integrated = db.query(IntegratedTable).filter(IntegratedTable.connection_id == db_conn.id, IntegratedTable.is_active == True).all()
    res_obj.integrated_tables = [f"{i.schema_name}.{i.table_name}" for i in all_integrated]
    
    return res_obj

@router.post("/test")
def test_connection(
    conn: ConnectionCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    result = db_test_connection(conn.connection_url)
    if result["status"] == "success":
        result["schemas"] = db_get_schemas(conn.connection_url)
    return result

@router.get("/raw/tables")
def get_raw_tables(
    url: str,
    schema: Optional[str] = None,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    return db_get_tables(url, schema)
