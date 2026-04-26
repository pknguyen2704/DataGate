"""
Rules, Alerts, Jobs, Dashboard endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from pydantic import BaseModel
from typing import Optional, Any
import uuid
from datetime import datetime

from app.db.session import get_db
from app.models.auth import User
from app.models.connection import TableInfo
from app.models.quality import (
    QualityRule, Alert, JobRun,
    RuleValidationRun, AnomalyDetectionRun,
    QualityThreshold, TableBatchMetadata, ColumnProfileMetric
)
from app.core.permissions import PermissionCode
from app.api.deps import get_current_user, require_permission

# ── Rules Router ─────────────────────────────────────────────────────────────
rules_router = APIRouter()


class RuleCreate(BaseModel):
    table_id: str
    column_name: Optional[str] = None
    rule_name: str
    rule_type: str
    rule_config: dict[str, Any] = {}
    severity: str = "medium"
    status: str = "enabled"


class RuleUpdate(BaseModel):
    rule_name: Optional[str] = None
    rule_config: Optional[dict[str, Any]] = None
    severity: Optional[str] = None


class RuleStatusUpdate(BaseModel):
    status: str  # enabled, disabled, rejected


@rules_router.get("")
async def list_rules(
    table_id: Optional[str] = None,
    rule_status: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(PermissionCode.RULE_VIEW)),
):
    query = select(QualityRule)
    if table_id:
        query = query.where(QualityRule.table_id == table_id)
    if rule_status:
        query = query.where(QualityRule.status == rule_status)
    result = await db.execute(query.order_by(QualityRule.created_at.desc()))
    return [
        {
            "id": r.id, "table_id": r.table_id, "column_name": r.column_name,
            "rule_name": r.rule_name, "rule_type": r.rule_type, "rule_config": r.rule_config,
            "source": r.source, "status": r.status, "severity": r.severity,
            "created_at": r.created_at, "updated_at": r.updated_at,
        }
        for r in result.scalars().all()
    ]


@rules_router.post("", status_code=status.HTTP_201_CREATED)
async def create_rule(
    body: RuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(PermissionCode.RULE_CREATE)),
):
    rule = QualityRule(
        id=str(uuid.uuid4()),
        table_id=body.table_id,
        column_name=body.column_name,
        rule_name=body.rule_name,
        rule_type=body.rule_type,
        rule_config=body.rule_config,
        source="manual",
        status=body.status,
        severity=body.severity,
        created_by=current_user.id,
    )
    db.add(rule)
    await db.flush()
    return {"id": rule.id, "rule_name": rule.rule_name, "status": rule.status}


@rules_router.patch("/{rule_id}")
async def update_rule(
    rule_id: str,
    body: RuleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(PermissionCode.RULE_UPDATE)),
):
    result = await db.execute(select(QualityRule).where(QualityRule.id == rule_id))
    rule = result.scalars().first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    if body.rule_name is not None:
        rule.rule_name = body.rule_name
    if body.rule_config is not None:
        rule.rule_config = body.rule_config
    if body.severity is not None:
        rule.severity = body.severity
    rule.updated_by = current_user.id
    await db.flush()
    return {"id": rule.id, "status": "updated"}


@rules_router.patch("/{rule_id}/status")
async def update_rule_status(
    rule_id: str,
    body: RuleStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(PermissionCode.RULE_ENABLE_DISABLE)),
):
    result = await db.execute(select(QualityRule).where(QualityRule.id == rule_id))
    rule = result.scalars().first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    rule.status = body.status
    rule.updated_by = current_user.id
    await db.flush()
    return {"id": rule.id, "status": rule.status}


@rules_router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(
    rule_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(PermissionCode.RULE_DELETE)),
):
    result = await db.execute(select(QualityRule).where(QualityRule.id == rule_id))
    rule = result.scalars().first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    await db.delete(rule)


# ── Alerts Router ─────────────────────────────────────────────────────────────
alerts_router = APIRouter()


class AlertStatusUpdate(BaseModel):
    status: str  # acknowledged, resolved, ignored
    note: Optional[str] = None


@alerts_router.get("")
async def list_alerts(
    alert_status: Optional[str] = Query(None, alias="status"),
    severity: Optional[str] = None,
    table_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(PermissionCode.ALERT_VIEW)),
):
    query = select(Alert)
    if alert_status:
        query = query.where(Alert.status == alert_status)
    if severity:
        query = query.where(Alert.severity == severity)
    if table_id:
        query = query.where(Alert.table_id == table_id)
    result = await db.execute(query.order_by(Alert.created_at.desc()).limit(limit))
    return [
        {
            "id": a.id, "table_id": a.table_id, "alert_type": a.alert_type,
            "severity": a.severity, "title": a.title, "message": a.message,
            "status": a.status, "created_at": a.created_at,
            "batch_date_hour": a.batch_date_hour, "acknowledged_at": a.acknowledged_at,
        }
        for a in result.scalars().all()
    ]


@alerts_router.patch("/{alert_id}/status")
async def update_alert_status(
    alert_id: str,
    body: AlertStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(PermissionCode.ALERT_ACKNOWLEDGE)),
):
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalars().first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.status = body.status
    if body.status == "acknowledged":
        alert.acknowledged_by = current_user.id
        alert.acknowledged_at = datetime.utcnow()
    elif body.status == "resolved":
        alert.resolved_at = datetime.utcnow()
    await db.flush()
    return {"id": alert.id, "status": alert.status}


# ── Jobs Router ───────────────────────────────────────────────────────────────
jobs_router = APIRouter()


class TriggerJobRequest(BaseModel):
    table_id: Optional[str] = None
    job_name: str
    dag_id: str
    batch_date_hour: Optional[str] = None


@jobs_router.get("")
async def list_job_runs(
    table_id: Optional[str] = None,
    job_name: Optional[str] = None,
    job_status: Optional[str] = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(PermissionCode.JOB_VIEW)),
):
    query = select(JobRun)
    if table_id:
        query = query.where(JobRun.table_id == table_id)
    if job_name:
        query = query.where(JobRun.job_name == job_name)
    if job_status:
        query = query.where(JobRun.status == job_status)
    result = await db.execute(query.order_by(JobRun.created_at.desc()).limit(limit))
    return [
        {
            "id": j.id, "table_id": j.table_id, "job_name": j.job_name,
            "dag_id": j.dag_id, "airflow_run_id": j.airflow_run_id,
            "status": j.status, "batch_date_hour": j.batch_date_hour,
            "started_at": j.started_at, "finished_at": j.finished_at,
            "error_message": j.error_message, "created_at": j.created_at,
        }
        for j in result.scalars().all()
    ]


@jobs_router.post("/trigger", status_code=status.HTTP_202_ACCEPTED)
async def trigger_job(
    body: TriggerJobRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(PermissionCode.JOB_TRIGGER)),
):
    """Trigger an Airflow DAG run (stub — integrate with Airflow REST API)."""
    job = JobRun(
        id=str(uuid.uuid4()),
        table_id=body.table_id,
        job_name=body.job_name,
        dag_id=body.dag_id,
        status="pending",
        batch_date_hour=body.batch_date_hour,
        triggered_by=current_user.id,
    )
    db.add(job)
    await db.flush()
    # TODO: call Airflow REST API to trigger dag_id
    return {"id": job.id, "status": "pending", "message": f"Job '{body.job_name}' triggered"}


# ── Dashboard Router ──────────────────────────────────────────────────────────
dashboard_router = APIRouter()


@dashboard_router.get("/summary")
async def get_dashboard_summary(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(PermissionCode.DASHBOARD_VIEW)),
):
    """System-wide dashboard summary statistics."""
    total_tables = await db.execute(select(func.count()).select_from(TableInfo).where(TableInfo.is_active == True))

    total_alerts_open = await db.execute(
        select(func.count()).select_from(Alert).where(Alert.status == "open")
    )

    critical_alerts = await db.execute(
        select(func.count()).select_from(Alert).where(
            and_(Alert.status == "open", Alert.severity == "critical")
        )
    )

    failed_jobs_recent = await db.execute(
        select(func.count()).select_from(JobRun).where(JobRun.status == "failed")
    )

    # Table health breakdown (based on latest validation run per table)
    table_health = {"healthy": 0, "warning": 0, "failed": 0, "unknown": 0}
    tables_result = await db.execute(
        select(TableInfo.id).where(and_(TableInfo.is_active == True, TableInfo.monitoring_enabled == True))
    )
    table_ids = tables_result.scalars().all()

    for tid in table_ids:
        latest_run = await db.execute(
            select(RuleValidationRun.status)
            .where(RuleValidationRun.table_id == tid)
            .order_by(RuleValidationRun.finished_at.desc())
            .limit(1)
        )
        s = latest_run.scalar()
        if s is None:
            table_health["unknown"] += 1
        elif s == "passed":
            table_health["healthy"] += 1
        elif s == "warning":
            table_health["warning"] += 1
        else:
            table_health["failed"] += 1

    return {
        "total_monitored_tables": total_tables.scalar(),
        "open_alerts": total_alerts_open.scalar(),
        "critical_alerts": critical_alerts.scalar(),
        "recent_failed_jobs": failed_jobs_recent.scalar(),
        "table_health": table_health,
    }


# ── Thresholds Router ──────────────────────────────────────────────────────────
thresholds_router = APIRouter()


class ThresholdCreate(BaseModel):
    table_id: str
    column_name: Optional[str] = None
    metric_name: str
    threshold_type: str = "manual"
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    severity: str = "medium"


class ThresholdUpdate(BaseModel):
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    severity: Optional[str] = None
    is_active: Optional[bool] = None


@thresholds_router.get("")
async def list_thresholds(
    table_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(PermissionCode.THRESHOLD_VIEW)),
):
    query = select(QualityThreshold)
    if table_id:
        query = query.where(QualityThreshold.table_id == table_id)
    result = await db.execute(query)
    return [
        {
            "id": t.id, "table_id": t.table_id, "column_name": t.column_name,
            "metric_name": t.metric_name, "threshold_type": t.threshold_type,
            "lower_bound": t.lower_bound, "upper_bound": t.upper_bound,
            "severity": t.severity, "is_active": t.is_active,
        }
        for t in result.scalars().all()
    ]


@thresholds_router.post("", status_code=status.HTTP_201_CREATED)
async def create_threshold(
    body: ThresholdCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(PermissionCode.THRESHOLD_CREATE)),
):
    t = QualityThreshold(
        id=str(uuid.uuid4()),
        **body.dict(),
        created_by=current_user.id,
    )
    db.add(t)
    await db.flush()
    return {"id": t.id, "metric_name": t.metric_name}


@thresholds_router.patch("/{threshold_id}")
async def update_threshold(
    threshold_id: str,
    body: ThresholdUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(PermissionCode.THRESHOLD_UPDATE)),
):
    result = await db.execute(select(QualityThreshold).where(QualityThreshold.id == threshold_id))
    t = result.scalars().first()
    if not t:
        raise HTTPException(status_code=404, detail="Threshold not found")
    for k, v in body.dict(exclude_unset=True).items():
        setattr(t, k, v)
    t.updated_by = current_user.id
    await db.flush()
    return {"id": t.id, "status": "updated"}


@thresholds_router.delete("/{threshold_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_threshold(
    threshold_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(PermissionCode.THRESHOLD_DELETE)),
):
    result = await db.execute(select(QualityThreshold).where(QualityThreshold.id == threshold_id))
    t = result.scalars().first()
    if not t:
        raise HTTPException(status_code=404, detail="Threshold not found")
    await db.delete(t)
