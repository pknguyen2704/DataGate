"""
Table management endpoints — registration, access, and per-table sub-resources
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime

from app.db.session import get_db
from app.models.auth import User
from app.models.connection import Connection, TableInfo, UserTableAccess
from app.models.quality import (
    TableBatchMetadata, ColumnProfileMetric, QualityRule,
    RuleValidationRun, AnomalyDetectionRun, Alert, JobRun, QualityThreshold
)
from app.core.permissions import PermissionCode
from app.api.deps import get_current_user, require_permission, check_table_access

router = APIRouter()


# ── Schemas ──────────────────────────────────────────────────────────────────

class TableOut(BaseModel):
    id: str
    connection_id: str
    connection_name: Optional[str]
    catalog_name: str
    schema_name: str
    table_name: str
    full_name: str
    layer: str
    description: Optional[str]
    is_active: bool
    monitoring_enabled: bool
    owner_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    # Summary stats (from latest batch)
    latest_batch_date_hour: Optional[str] = None
    latest_record_count: Optional[int] = None
    latest_quality_status: Optional[str] = None
    latest_anomaly_status: Optional[str] = None
    open_alert_count: int = 0


class TableCreate(BaseModel):
    connection_id: str
    catalog_name: str
    schema_name: str
    table_name: str
    layer: str = "bronze"
    description: Optional[str] = None
    monitoring_enabled: bool = True


class TableUpdate(BaseModel):
    layer: Optional[str] = None
    description: Optional[str] = None
    monitoring_enabled: Optional[bool] = None
    is_active: Optional[bool] = None


class AccessGrantRequest(BaseModel):
    user_id: str
    access_level: str = "view"  # view or manage


class PaginatedTables(BaseModel):
    items: list[TableOut]
    total: int
    page: int
    page_size: int


# ── Helpers ──────────────────────────────────────────────────────────────────

async def _enrich_table(db: AsyncSession, table: TableInfo, conn_name: str | None = None) -> TableOut:
    """Attach latest batch, quality, anomaly summary to a table."""
    # Latest batch
    batch_result = await db.execute(
        select(TableBatchMetadata)
        .where(TableBatchMetadata.table_id == table.id)
        .order_by(TableBatchMetadata.committed_at.desc())
        .limit(1)
    )
    latest_batch = batch_result.scalars().first()

    # Latest validation run
    val_result = await db.execute(
        select(RuleValidationRun)
        .where(RuleValidationRun.table_id == table.id)
        .order_by(RuleValidationRun.finished_at.desc())
        .limit(1)
    )
    latest_val = val_result.scalars().first()

    # Latest anomaly run
    anom_result = await db.execute(
        select(AnomalyDetectionRun)
        .where(AnomalyDetectionRun.table_id == table.id)
        .order_by(AnomalyDetectionRun.finished_at.desc())
        .limit(1)
    )
    latest_anom = anom_result.scalars().first()

    # Open alerts count
    alert_count_result = await db.execute(
        select(func.count())
        .where(and_(Alert.table_id == table.id, Alert.status == "open"))
    )
    open_alert_count = alert_count_result.scalar() or 0

    return TableOut(
        id=table.id,
        connection_id=table.connection_id,
        connection_name=conn_name,
        catalog_name=table.catalog_name,
        schema_name=table.schema_name,
        table_name=table.table_name,
        full_name=table.full_name,
        layer=table.layer,
        description=table.description,
        is_active=table.is_active,
        monitoring_enabled=table.monitoring_enabled,
        owner_id=table.owner_user_id,
        created_at=table.created_at,
        updated_at=table.updated_at,
        latest_batch_date_hour=latest_batch.batch_date_hour if latest_batch else None,
        latest_record_count=latest_batch.total_records if latest_batch else None,
        latest_quality_status=latest_val.status if latest_val else None,
        latest_anomaly_status=latest_anom.drift_status if latest_anom else None,
        open_alert_count=open_alert_count,
    )


# ── Table CRUD ───────────────────────────────────────────────────────────────

@router.get("", response_model=PaginatedTables)
async def list_tables(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    layer: Optional[str] = None,
    connection_id: Optional[str] = None,
    quality_status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(PermissionCode.TABLE_VIEW)),
):
    """List tables accessible to current user."""
    from app.core.permissions import PermissionCode as PC

    is_admin = current_user.has_permission(PC.TABLE_GRANT_ACCESS)

    query = select(TableInfo)

    if not is_admin:
        accessible_table_ids = select(UserTableAccess.table_id).where(
            UserTableAccess.user_id == current_user.id
        )
        query = query.where(TableInfo.id.in_(accessible_table_ids))

    if search:
        query = query.where(
            or_(
                TableInfo.table_name.ilike(f"%{search}%"),
                TableInfo.schema_name.ilike(f"%{search}%"),
                TableInfo.catalog_name.ilike(f"%{search}%"),
            )
        )
    if layer:
        query = query.where(TableInfo.layer == layer)
    if connection_id:
        query = query.where(TableInfo.connection_id == connection_id)

    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar()

    query = query.order_by(TableInfo.updated_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    tables = result.scalars().all()

    # Load connections for names
    conn_ids = {t.connection_id for t in tables}
    conn_result = await db.execute(select(Connection).where(Connection.id.in_(conn_ids)))
    conn_map = {c.id: c.name for c in conn_result.scalars().all()}

    items = []
    for t in tables:
        enriched = await _enrich_table(db, t, conn_map.get(t.connection_id))
        items.append(enriched)

    return PaginatedTables(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=TableOut, status_code=status.HTTP_201_CREATED)
async def register_table(
    body: TableCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(PermissionCode.TABLE_CREATE)),
):
    # Verify connection exists
    conn_result = await db.execute(select(Connection).where(Connection.id == body.connection_id))
    conn = conn_result.scalars().first()
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")

    # Check uniqueness
    dup_result = await db.execute(
        select(TableInfo).where(
            and_(
                TableInfo.connection_id == body.connection_id,
                TableInfo.catalog_name == body.catalog_name,
                TableInfo.schema_name == body.schema_name,
                TableInfo.table_name == body.table_name,
            )
        )
    )
    if dup_result.scalars().first():
        raise HTTPException(status_code=400, detail="Table already registered")

    table = TableInfo(
        id=str(uuid.uuid4()),
        connection_id=body.connection_id,
        catalog_name=body.catalog_name,
        schema_name=body.schema_name,
        table_name=body.table_name,
        layer=body.layer,
        description=body.description,
        monitoring_enabled=body.monitoring_enabled,
        owner_user_id=current_user.id,
    )
    db.add(table)
    await db.flush()
    return await _enrich_table(db, table, conn.name)


@router.get("/{table_id}", response_model=TableOut)
async def get_table(
    table_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    table = await check_table_access(table_id, "view", db, current_user)
    conn_result = await db.execute(select(Connection).where(Connection.id == table.connection_id))
    conn = conn_result.scalars().first()
    return await _enrich_table(db, table, conn.name if conn else None)


@router.patch("/{table_id}", response_model=TableOut)
async def update_table(
    table_id: str,
    body: TableUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    table = await check_table_access(table_id, "manage", db, current_user)

    if body.layer is not None:
        table.layer = body.layer
    if body.description is not None:
        table.description = body.description
    if body.monitoring_enabled is not None:
        table.monitoring_enabled = body.monitoring_enabled
    if body.is_active is not None:
        table.is_active = body.is_active

    await db.flush()
    conn_result = await db.execute(select(Connection).where(Connection.id == table.connection_id))
    conn = conn_result.scalars().first()
    return await _enrich_table(db, table, conn.name if conn else None)


# ── Table Access Management ──────────────────────────────────────────────────

@router.post("/{table_id}/access")
async def grant_access(
    table_id: str,
    body: AccessGrantRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(PermissionCode.TABLE_GRANT_ACCESS)),
):
    table_result = await db.execute(select(TableInfo).where(TableInfo.id == table_id))
    if not table_result.scalars().first():
        raise HTTPException(status_code=404, detail="Table not found")

    # Upsert
    existing = await db.execute(
        select(UserTableAccess).where(
            and_(UserTableAccess.user_id == body.user_id, UserTableAccess.table_id == table_id)
        )
    )
    access = existing.scalars().first()
    if access:
        access.access_level = body.access_level
    else:
        access = UserTableAccess(
            id=str(uuid.uuid4()),
            user_id=body.user_id,
            table_id=table_id,
            access_level=body.access_level,
            granted_by=current_user.id,
        )
        db.add(access)
    await db.flush()
    return {"detail": "Access granted"}


@router.delete("/{table_id}/access/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_access(
    table_id: str,
    user_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(PermissionCode.TABLE_REVOKE_ACCESS)),
):
    result = await db.execute(
        select(UserTableAccess).where(
            and_(UserTableAccess.user_id == user_id, UserTableAccess.table_id == table_id)
        )
    )
    access = result.scalars().first()
    if not access:
        raise HTTPException(status_code=404, detail="Access record not found")
    await db.delete(access)


# ── Table Sub-resources ──────────────────────────────────────────────────────

@router.get("/{table_id}/metadata")
async def get_table_metadata(
    table_id: str,
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await check_table_access(table_id, "view", db, current_user)
    result = await db.execute(
        select(TableBatchMetadata)
        .where(TableBatchMetadata.table_id == table_id)
        .order_by(TableBatchMetadata.committed_at.desc())
        .limit(limit)
    )
    batches = result.scalars().all()
    return [
        {
            "id": b.id, "snapshot_id": b.snapshot_id,
            "batch_date_hour": b.batch_date_hour,
            "committed_at": b.committed_at, "operation": b.operation,
            "added_records": b.added_records,
            "added_data_files_size": b.added_data_files_size,
            "total_records": b.total_records,
        }
        for b in batches
    ]


@router.get("/{table_id}/profiling")
async def get_table_profiling(
    table_id: str,
    snapshot_id: Optional[str] = None,
    column_name: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await check_table_access(table_id, "view", db, current_user)

    if not snapshot_id:
        # Get latest
        latest = await db.execute(
            select(TableBatchMetadata.snapshot_id)
            .where(TableBatchMetadata.table_id == table_id)
            .order_by(TableBatchMetadata.committed_at.desc())
            .limit(1)
        )
        snapshot_id = latest.scalar()

    if not snapshot_id:
        return []

    query = select(ColumnProfileMetric).where(
        and_(ColumnProfileMetric.table_id == table_id, ColumnProfileMetric.snapshot_id == snapshot_id)
    )
    if column_name:
        query = query.where(ColumnProfileMetric.column_name == column_name)

    result = await db.execute(query.order_by(ColumnProfileMetric.column_name))
    metrics = result.scalars().all()
    return [
        {
            "column_name": m.column_name, "data_type": m.data_type,
            "metric_name": m.metric_name, "metric_value": m.metric_value,
            "snapshot_id": m.snapshot_id, "batch_date_hour": m.batch_date_hour,
        }
        for m in metrics
    ]


@router.get("/{table_id}/rules")
async def get_table_rules(
    table_id: str,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await check_table_access(table_id, "view", db, current_user)
    query = select(QualityRule).where(QualityRule.table_id == table_id)
    if status:
        query = query.where(QualityRule.status == status)
    result = await db.execute(query.order_by(QualityRule.created_at.desc()))
    rules = result.scalars().all()
    return [
        {
            "id": r.id, "column_name": r.column_name, "rule_name": r.rule_name,
            "rule_type": r.rule_type, "rule_config": r.rule_config,
            "source": r.source, "status": r.status, "severity": r.severity,
            "created_at": r.created_at,
        }
        for r in rules
    ]


@router.get("/{table_id}/quality")
async def get_table_quality(
    table_id: str,
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await check_table_access(table_id, "view", db, current_user)
    result = await db.execute(
        select(RuleValidationRun)
        .where(RuleValidationRun.table_id == table_id)
        .order_by(RuleValidationRun.finished_at.desc())
        .limit(limit)
    )
    runs = result.scalars().all()
    return [
        {
            "id": r.id, "status": r.status, "batch_date_hour": r.batch_date_hour,
            "total_rules": r.total_rules, "passed_rules": r.passed_rules,
            "failed_rules": r.failed_rules, "auc_score": r.auc_score,
            "started_at": r.started_at, "finished_at": r.finished_at,
        }
        for r in runs
    ]


@router.get("/{table_id}/anomaly")
async def get_table_anomaly(
    table_id: str,
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await check_table_access(table_id, "view", db, current_user)
    result = await db.execute(
        select(AnomalyDetectionRun)
        .where(AnomalyDetectionRun.table_id == table_id)
        .order_by(AnomalyDetectionRun.finished_at.desc())
        .limit(limit)
    )
    runs = result.scalars().all()
    return [
        {
            "id": r.id, "auc_score": r.auc_score, "drift_status": r.drift_status,
            "batch_date_hour": r.batch_date_hour, "threshold_used": r.threshold_used,
            "started_at": r.started_at, "finished_at": r.finished_at,
            "top_features": [
                {"column": f.column_name, "shap_value": f.shap_value, "rank": f.importance_rank}
                for f in sorted(r.feature_importances, key=lambda x: x.importance_rank or 99)[:5]
            ],
        }
        for r in runs
    ]


@router.get("/{table_id}/thresholds")
async def get_table_thresholds(
    table_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await check_table_access(table_id, "view", db, current_user)
    result = await db.execute(
        select(QualityThreshold).where(QualityThreshold.table_id == table_id)
    )
    return [
        {
            "id": t.id, "column_name": t.column_name, "metric_name": t.metric_name,
            "threshold_type": t.threshold_type, "lower_bound": t.lower_bound,
            "upper_bound": t.upper_bound, "severity": t.severity, "is_active": t.is_active,
        }
        for t in result.scalars().all()
    ]


@router.get("/{table_id}/alerts")
async def get_table_alerts(
    table_id: str,
    alert_status: Optional[str] = Query(None, alias="status"),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await check_table_access(table_id, "view", db, current_user)
    query = select(Alert).where(Alert.table_id == table_id)
    if alert_status:
        query = query.where(Alert.status == alert_status)
    result = await db.execute(query.order_by(Alert.created_at.desc()).limit(limit))
    return [
        {
            "id": a.id, "alert_type": a.alert_type, "severity": a.severity,
            "title": a.title, "message": a.message, "status": a.status,
            "created_at": a.created_at, "batch_date_hour": a.batch_date_hour,
        }
        for a in result.scalars().all()
    ]


@router.get("/{table_id}/jobs")
async def get_table_jobs(
    table_id: str,
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await check_table_access(table_id, "view", db, current_user)
    result = await db.execute(
        select(JobRun).where(JobRun.table_id == table_id)
        .order_by(JobRun.created_at.desc()).limit(limit)
    )
    return [
        {
            "id": j.id, "job_name": j.job_name, "status": j.status,
            "batch_date_hour": j.batch_date_hour, "started_at": j.started_at,
            "finished_at": j.finished_at, "error_message": j.error_message,
        }
        for j in result.scalars().all()
    ]
