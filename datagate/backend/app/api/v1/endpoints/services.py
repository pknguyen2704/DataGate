from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models
from app.api import deps
from app.models.service import Service
from app.schemas.service import Service as ServiceSchema
from app.schemas.service import ServiceCreate, ServiceUpdate
from app.services.connection_manager import ConnectionManager
from app.services.observability_scanner import ObservabilityScanner

router = APIRouter()


def _get_accessible_tables(service: Service) -> list[str] | None:
    if not service.integrated_tables:
        return None

    return [table for table in service.integrated_tables if isinstance(table, str) and table.strip()]


def _filter_tables_by_integration(
    discovered_tables: list[str],
    integrated_tables: list[str] | None,
    schema: str | None = None,
) -> list[str]:
    if integrated_tables is None:
        return discovered_tables

    allowed_table_names = set(integrated_tables)
    filtered_tables: list[str] = []

    for table in discovered_tables:
        full_name = f"{schema}.{table}" if schema else table
        if table in allowed_table_names or full_name in allowed_table_names:
            filtered_tables.append(table)

    return filtered_tables


def _filter_schemas_by_integration(discovered_schemas: list[str], integrated_tables: list[str] | None) -> list[str]:
    if integrated_tables is None:
        return discovered_schemas

    allowed_schemas = {
        table.split(".", 1)[0]
        for table in integrated_tables
        if isinstance(table, str) and "." in table
    }
    return [schema_name for schema_name in discovered_schemas if schema_name in allowed_schemas]


def _get_accessible_services_query(db: Session, current_user: models.User):
    query = db.query(Service)
    if current_user.is_superuser:
        return query
    return query.filter(Service.owner_id == current_user.id)


def _get_accessible_asset_map(db: Session, current_user: models.User) -> dict[str, Service]:
    services = _get_accessible_services_query(db, current_user).all()
    asset_map: dict[str, Service] = {}

    for service in services:
        for table_name in service.integrated_tables or []:
            if isinstance(table_name, str) and table_name.strip():
                asset_map[table_name] = service

    return asset_map


def _get_service_or_404(db: Session, service_id: int) -> Service:
    service = db.query(Service).filter(Service.id == service_id).first()
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


def _ensure_service_permission(service: Service, current_user: models.User) -> Service:
    if not current_user.is_superuser and service.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return service


def _get_owned_service(db: Session, service_id: int, current_user: models.User) -> Service:
    service = _get_service_or_404(db, service_id)
    return _ensure_service_permission(service, current_user)


def _get_accessible_asset_service_or_403(db: Session, current_user: models.User, table_name: str) -> Service:
    asset_map = _get_accessible_asset_map(db, current_user)
    service = asset_map.get(table_name)
    if service:
        return service

    for full_name, mapped_service in asset_map.items():
        if full_name.endswith(f".{table_name}"):
            return mapped_service

    raise HTTPException(status_code=403, detail="Not enough permissions to access this data asset")


def get_accessible_asset_service_or_403(db: Session, current_user: models.User, table_name: str) -> Service:
    return _get_accessible_asset_service_or_403(db, current_user, table_name)


def _get_latest_ml_run_for_table(db: Session, table_name: str):
    runs = db.query(models.MLAnomalyRun).order_by(models.MLAnomalyRun.batch_time.desc()).all()
    for run in runs:
        if run.table_name == table_name or (run.table_name and run.table_name.endswith(f".{table_name}")):
            return run
    return None


def _build_service_status(service_in: ServiceCreate) -> str:
    test_result = ConnectionManager.test_connection(service_in)
    return "healthy" if test_result["status"] == "success" else "unhealthy"


def _serialize_owner(service: Service) -> dict | None:
    if service.owner is None:
        return None

    return {
        "id": service.owner.id,
        "full_name": service.owner.full_name,
        "username": service.owner.username,
        "email": service.owner.email,
    }


def _serialize_snapshot(snapshot) -> dict | None:
    if snapshot is None:
        return None

    return {
        "snapshot_time": snapshot.snapshot_time.isoformat() if snapshot.snapshot_time else None,
        "last_updated_time": snapshot.last_updated_time.isoformat() if snapshot.last_updated_time else None,
        "total_records": snapshot.total_records,
        "total_size": snapshot.total_size,
    }


def _serialize_profiling_run(run) -> dict | None:
    if run is None:
        return None

    return {
        "id": run.id,
        "run_time": run.batch_time.isoformat() if run.batch_time else None,
        "num_records": run.num_records,
        "partition_key": run.partition_key,
    }


def _serialize_quality_run(run) -> dict | None:
    if run is None:
        return None

    return {
        "id": run.id,
        "batch_time": run.batch_time.isoformat() if run.batch_time else None,
        "total_checks": run.total_checks,
        "failed_checks": run.failed_checks,
        "status": run.status,
    }


def _serialize_ml_run(run) -> dict | None:
    if run is None:
        return None

    return {
        "id": run.id,
        "batch_time": run.batch_time.isoformat() if run.batch_time else None,
        "anomaly_score": run.anomaly_score,
        "status": run.status,
    }


@router.post("/{service_id}/scan")
def scan_service(
    service_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    _get_owned_service(db, service_id, current_user)
    return ObservabilityScanner.scan_service(db, service_id)


@router.post("/test")
def test_connection(
    service: ServiceCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    result = ConnectionManager.test_connection(service)
    if result["status"] == "success":
        result["schemas"] = ConnectionManager.get_schemas(service.service_type, service.connection_url)
    return result


@router.get("/raw/tables")
def get_raw_tables(
    service_type: str,
    url: str,
    schema: str | None = None,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    return ConnectionManager.get_tables(service_type, url, schema)


@router.post("/", response_model=ServiceSchema)
def create_service(
    service: ServiceCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    db_service = Service(
        name=service.name,
        service_type=service.service_type,
        connection_url=service.connection_url,
        integrated_tables=service.integrated_tables,
        status=_build_service_status(service),
        owner_id=current_user.id,
    )
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service


@router.get("/", response_model=list[ServiceSchema])
def get_services(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    return _get_accessible_services_query(db, current_user).all()


@router.get("/assets")
def get_accessible_assets(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    services = _get_accessible_services_query(db, current_user).all()
    assets = []

    for service in services:
        for table_name in service.integrated_tables or []:
            if not isinstance(table_name, str) or "." not in table_name:
                continue

            schema_name, physical_table_name = table_name.split(".", 1)
            assets.append(
                {
                    "service_id": service.id,
                    "service_name": service.name,
                    "service_type": service.service_type,
                    "table_name": table_name,
                    "schema_name": schema_name,
                    "asset_name": physical_table_name,
                }
            )

    return assets


@router.get("/assets/detail")
def get_asset_detail(
    table_name: str = Query(...),
    service_id: int | None = Query(default=None),
    sample_limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    service = _get_accessible_asset_service_or_403(db, current_user, table_name)

    if service_id is not None and service.id != service_id:
        raise HTTPException(status_code=404, detail="Service not found for this asset")

    schema_tables = ConnectionManager.get_tables(service.service_type, service.connection_url)
    sample_data = ConnectionManager.get_sample_data(service.service_type, service.connection_url, table_name, sample_limit)
    table_metadata = ConnectionManager.get_table_metadata(service.service_type, service.connection_url, table_name)

    latest_snapshot = (
        db.query(models.DQTableSnapshot)
        .filter(models.DQTableSnapshot.table_name == table_name)
        .order_by(models.DQTableSnapshot.snapshot_time.desc())
        .first()
    )
    latest_profiling = (
        db.query(models.ProfilingRun)
        .filter(models.ProfilingRun.table_name == table_name)
        .order_by(models.ProfilingRun.batch_time.desc())
        .first()
    )
    latest_quality_run = (
        db.query(models.QualityCheckRun)
        .filter(models.QualityCheckRun.table_name == table_name)
        .order_by(models.QualityCheckRun.batch_time.desc())
        .first()
    )
    latest_ml_run = _get_latest_ml_run_for_table(db, table_name)
    rules_count = (
        db.query(func.count(models.ActiveRule.id))
        .filter(models.ActiveRule.table_name == table_name)
        .scalar()
        or 0
    )

    row_count = None
    row_count_source = None
    if latest_snapshot and latest_snapshot.total_records is not None:
        row_count = latest_snapshot.total_records
        row_count_source = "dq_table_snapshot"
    elif latest_profiling and latest_profiling.num_records is not None:
        row_count = latest_profiling.num_records
        row_count_source = "profiling_runs"

    schema_name = table_name.split(".", 1)[0] if "." in table_name else ""
    asset_name = table_name.split(".", 1)[1] if "." in table_name else table_name

    return {
        "service_id": service.id,
        "service_name": service.name,
        "service_type": service.service_type,
        "owner": _serialize_owner(service),
        "table_name": table_name,
        "schema_name": schema_name,
        "asset_name": asset_name,
        "integrated_tables_count": len(service.integrated_tables or []),
        "schema_tables_count": len(schema_tables),
        "row_count": row_count,
        "row_count_source": row_count_source,
        "latest_snapshot": _serialize_snapshot(latest_snapshot),
        "latest_profiling": _serialize_profiling_run(latest_profiling),
        "latest_quality_run": _serialize_quality_run(latest_quality_run),
        "latest_ml_run": _serialize_ml_run(latest_ml_run),
        "rules_count": rules_count,
        "table_description": table_metadata.get("table_description"),
        "columns": table_metadata.get("columns", []),
        "sample_data": sample_data,
    }


@router.get("/{service_id}/schemas")
def get_service_schemas(
    service_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    service = _get_owned_service(db, service_id, current_user)
    schemas = ConnectionManager.get_schemas(service.service_type, service.connection_url)
    return _filter_schemas_by_integration(schemas, _get_accessible_tables(service))


@router.get("/{service_id}/tables")
def get_service_tables(
    service_id: int,
    schema: str | None = None,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    service = _get_owned_service(db, service_id, current_user)
    tables = ConnectionManager.get_tables(service.service_type, service.connection_url, schema)
    return _filter_tables_by_integration(tables, _get_accessible_tables(service), schema)


@router.put("/{service_id}", response_model=ServiceSchema)
def update_service(
    service_id: int,
    service_in: ServiceUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    db_service = _get_owned_service(db, service_id, current_user)
    update_data = service_in.model_dump(exclude_unset=True)

    if "connection_url" in update_data:
        test_service = ServiceCreate(
            name=update_data.get("name", db_service.name),
            service_type=update_data.get("service_type", db_service.service_type),
            connection_url=update_data["connection_url"],
            integrated_tables=update_data.get("integrated_tables", db_service.integrated_tables),
        )
        db_service.status = _build_service_status(test_service)

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
    service = _get_owned_service(db, service_id, current_user)
    db.delete(service)
    db.commit()
    return {"status": "success", "message": "Service deleted"}


@router.post("/{service_id}/refresh-tables")
def refresh_service_tables(
    service_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    service = _get_owned_service(db, service_id, current_user)

    try:
        current_tables = ConnectionManager.get_tables(service.service_type, service.connection_url)

        if service.integrated_tables:
            valid_tables = [table for table in service.integrated_tables if table in current_tables]
            service.integrated_tables = valid_tables
            db.add(service)
            db.commit()
            db.refresh(service)
            return {"status": "success", "updated_tables": valid_tables}

        return {"status": "success", "message": "No tables integrated yet"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to refresh tables: {str(exc)}")
