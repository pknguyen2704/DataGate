from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app import models, schemas
from app.api import deps
from app.api.v1.endpoints.connections_router import (
    get_system_connection,
    _filter_schemas_by_rbac,
    _filter_tables_by_rbac,
    check_table_access,
)
from app.models.connection.connection import Connection
from app.schemas.connection import ConnectionExplore
from app.services.connection_manager_service import (
    get_schemas as db_get_schemas,
    get_tables as db_get_tables,
    get_sample_data as db_get_sample_data,
    get_table_metadata as db_get_table_metadata,
)

router = APIRouter()

# --- 1. DISCOVERY ---

@router.get("", response_model=List[ConnectionExplore])
def get_explore_data(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Lấy dữ liệu hạ tầng dựa trên quyền truy cập bảng của User."""
    # Kiểm tra xem hệ thống đã có kết nối nào chưa
    conn = db.query(Connection).first()
    if not conn:
        return []
    
    # 1. Lấy schema gốc từ DB
    try:
        discovered_schemas = db_get_schemas(conn.connection_url)
    except Exception:
        discovered_schemas = []
    
    # 2. Lọc schema dựa trên các bảng user được phép (nếu không phải superuser)
    system_integrated = set(conn.integrated_tables or [])
    filtered_schemas = _filter_schemas_by_rbac(current_user, discovered_schemas, list(system_integrated))

    all_tables = []
    for schema in filtered_schemas:
        try:
            tables = db_get_tables(conn.connection_url, schema)
            # Chỉ lấy những bảng đã được hệ thống integrate VÀ user có quyền
            integrated_in_schema = [t for t in tables if f"{schema}.{t}" in system_integrated or t in system_integrated]
            user_permitted_tables = _filter_tables_by_rbac(current_user, integrated_in_schema, schema)
            all_tables.extend([f"{schema}.{t}" for t in user_permitted_tables])
        except Exception:
            continue

    return [{
        "connection": conn,
        "schemas": filtered_schemas,
        "tables": all_tables,
    }]

# --- 2. ASSET OVERVIEW ---

@router.get("/overview")
def get_asset_overview(
    table: str = Query(...),
    schema: Optional[str] = Query(default=None),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Lấy thông tin tổng quan về bảng (Metadata). Kiểm tra RBAC tới bảng."""
    full_table_name = f"{schema}.{table}" if schema else table
    check_table_access(current_user, full_table_name)
    
    conn = get_system_connection(db)
    metadata = db_get_table_metadata(conn.connection_url, full_table_name)

    snap = db.query(models.ObservabilitySnapshot)\
             .filter(
                 models.ObservabilitySnapshot.table_name == table,
                 models.ObservabilitySnapshot.schema_name == (schema or "public")
             )\
             .order_by(models.ObservabilitySnapshot.snapshot_time.desc())\
             .first()

    return {
        "connection_name": conn.name,
        "table_name": full_table_name,
        "schema_name": schema or "",
        "asset_name": table,
        "row_count": snap.total_records if snap else 0,
        "total_size": snap.total_size if snap else 0,
        "last_updated": snap.last_updated_time if snap else None,
        "table_description": metadata.get("table_description"),
        "columns": metadata.get("columns", []),
    }

# --- 3. ASSET SAMPLE ---

@router.get("/sample")
def get_asset_sample(
    table: str = Query(...),
    schema: Optional[str] = Query(default=None),
    sample_limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Lấy dữ liệu mẫu. Kiểm tra RBAC tới bảng."""
    full_table_name = f"{schema}.{table}" if schema else table
    check_table_access(current_user, full_table_name)
    
    conn = get_system_connection(db)
    sample_data = db_get_sample_data(conn.connection_url, full_table_name, sample_limit)

    return {
        "table_name": full_table_name,
        "schema": schema,
        "table": table,
        "sample_data": sample_data,
    }
