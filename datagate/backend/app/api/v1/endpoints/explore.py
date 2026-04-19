from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app import models, schemas
from app.api import deps
from app.api.v1.endpoints.services_router import (
    _get_accessible_services_query,
    _filter_schemas_by_integration,
    _filter_tables_by_integration,
    get_service_by_table_or_403,
)
from app.schemas.service_schema import ServiceExplore
from app.services.connection_manager_service import (
    get_schemas as db_get_schemas,
    get_tables as db_get_tables,
    get_sample_data as db_get_sample_data,
    get_table_metadata as db_get_table_metadata,
)

router = APIRouter()


# --- 1. DISCOVERY ---

@router.get("", response_model=List[ServiceExplore])
def get_explore_data(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Lấy toàn bộ thông tin metadata (services, schemas, tables) phục vụ trang Explore."""
    services = _get_accessible_services_query(db, current_user).all()
    result = []
    for service in services:
        discovered_schemas = db_get_schemas(service.connection_url)
        filtered_schemas = _filter_schemas_by_integration(discovered_schemas, service.integrated_tables)

        all_tables = []
        for schema in filtered_schemas:
            tables = db_get_tables(service.connection_url, schema)
            filtered_tables = _filter_tables_by_integration(tables, service.integrated_tables, schema)
            all_tables.extend(filtered_tables)

        result.append({
            "service": service,
            "schemas": filtered_schemas,
            "tables": all_tables,
        })
    return result


# --- 2. ASSET OVERVIEW ---

@router.get("/overview")
def get_asset_overview(
    table: str = Query(...),
    schema: Optional[str] = Query(default=None),
    service_id: Optional[int] = Query(default=None),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Lấy thông tin tổng quan về bảng (Metadata)."""
    full_table_name = f"{schema}.{table}" if schema else table
    service = get_service_by_table_or_403(db, current_user, full_table_name, service_id)

    metadata = db_get_table_metadata(service.connection_url, full_table_name)

    snap = db.query(models.DGObservabilitySnapshot)\
             .filter(models.DGObservabilitySnapshot.table_name == full_table_name)\
             .order_by(models.DGObservabilitySnapshot.snapshot_time.desc())\
             .first()

    return {
        "service_id": service.id,
        "service_name": service.name,
        "service_type": service.service_type,
        "owner": service.owner,
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
    service_id: Optional[int] = Query(default=None),
    sample_limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Lấy dữ liệu mẫu (Sample data)."""
    full_table_name = f"{schema}.{table}" if schema else table
    service = get_service_by_table_or_403(db, current_user, full_table_name, service_id)

    sample_data = db_get_sample_data(service.connection_url, full_table_name, sample_limit)

    return {
        "table_name": full_table_name,
        "schema": schema,
        "table": table,
        "sample_data": sample_data,
    }


# --- 4. COLUMN STATS ---

