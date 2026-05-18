from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models import AnomalyResult, QualityCheckResult, Rule, Table
from app.schemas.data_quality_schema import (
    AnomalyResultDetail,
    DataQualitySummary,
    MetadataResultDetail,
    ProfilingResultDetail,
    QualityResultOut,
    ResultType,
    RuleResultDetail,
)


CHECK_TYPE_TO_RESULT_TYPE = {
    "metadata_threshold": ResultType.METADATA,
    "profiling_threshold": ResultType.PROFILING,
    "rule": ResultType.RULE,
    "anomaly_auc": ResultType.ANOMALY,
}

RESULT_TYPE_TO_CHECK_TYPES = {
    ResultType.METADATA: ["metadata_threshold"],
    ResultType.PROFILING: ["profiling_threshold"],
    ResultType.RULE: ["rule"],
    ResultType.ANOMALY: ["anomaly_auc"],
}


class DataQualityService:
    def __init__(self, db: Session):
        self.db = db

    def _base_query(
        self,
        table_id: str | None = None,
        processing_date_hour: datetime | None = None,
        status_val: str | None = None,
        severity_level: str | None = None,
        result_type: str | None = None,
    ):
        query = self.db.query(QualityCheckResult).options(
            joinedload(QualityCheckResult.table),
            joinedload(QualityCheckResult.rule),
            joinedload(QualityCheckResult.threshold),
            joinedload(QualityCheckResult.anomaly_result).joinedload(
                AnomalyResult.anomaly_config
            ),
        )
        if table_id:
            query = query.filter(QualityCheckResult.table_id == table_id)
        if processing_date_hour:
            query = query.filter(
                QualityCheckResult.processing_date_hour == processing_date_hour
            )
        if status_val:
            query = query.filter(QualityCheckResult.status == status_val)
        if severity_level:
            query = query.filter(QualityCheckResult.severity_level == severity_level)
        if result_type:
            try:
                enum_result_type = ResultType(result_type)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid result type")
            query = query.filter(
                QualityCheckResult.check_type.in_(
                    RESULT_TYPE_TO_CHECK_TYPES[enum_result_type]
                )
            )
        return query

    def _to_result_out(self, row: QualityCheckResult) -> QualityResultOut:
        return QualityResultOut(
            id=row.id,
            table_id=row.table_id,
            table_name=row.table.table_name if row.table else None,
            result_type=CHECK_TYPE_TO_RESULT_TYPE.get(row.check_type, ResultType.METADATA),
            status=row.status,
            severity_level=row.severity_level,
            processing_date_hour=row.processing_date_hour,
            is_resolved=row.is_resolved,
            column_name=row.column_name,
            metric_name=row.metric_name,
            actual_value=row.actual_value,
            threshold_value=row.min_threshold
            if row.min_threshold is not None
            else row.max_threshold,
            message=row.message,
            created_at=row.created_at,
        )

    def list_results(
        self,
        table_id: str | None = None,
        layer: str | None = None,
        processing_date_hour: datetime | None = None,
        status_val: str | None = None,
        severity_level: str | None = None,
        result_type: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ):
        query = self._base_query(
            table_id=table_id,
            processing_date_hour=processing_date_hour,
            status_val=status_val,
            severity_level=severity_level,
            result_type=result_type,
        )
        total = query.count()
        rows = (
            query.order_by(QualityCheckResult.processing_date_hour.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return {
            "items": [self._to_result_out(row) for row in rows],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def get_summary(self, table_id: str | None = None):
        query = self.db.query(QualityCheckResult)
        if table_id:
            query = query.filter(QualityCheckResult.table_id == table_id)

        total = query.count()
        passed = query.filter(QualityCheckResult.status == "pass").count()
        failed_rows = query.filter(QualityCheckResult.status == "fail").all()
        failed = len(failed_rows)
        unresolved = sum(1 for row in failed_rows if not row.is_resolved)
        critical_fail = sum(
            1 for row in failed_rows if row.severity_level == "critical"
        )
        warning_fail = failed - critical_fail

        by_type_rows = (
            query.with_entities(QualityCheckResult.check_type, func.count())
            .group_by(QualityCheckResult.check_type)
            .all()
        )
        checks_by_type = {"metadata": 0, "profiling": 0, "rule": 0, "anomaly": 0}
        for check_type, count in by_type_rows:
            result_type = CHECK_TYPE_TO_RESULT_TYPE.get(check_type)
            if result_type:
                checks_by_type[result_type.value] += count

        return DataQualitySummary(
            total_checks=total,
            total_pass=passed,
            total_fail=failed,
            unresolved_alerts=unresolved,
            warning_fail=warning_fail,
            critical_fail=critical_fail,
            pass_rate=(passed / total * 100) if total > 0 else 100.0,
            checks_by_type=checks_by_type,
        )

    def _get_result_or_404(self, result_id: str, check_type: str | None = None):
        query = self.db.query(QualityCheckResult).options(
            joinedload(QualityCheckResult.table),
            joinedload(QualityCheckResult.rule),
            joinedload(QualityCheckResult.threshold),
            joinedload(QualityCheckResult.anomaly_result).joinedload(
                AnomalyResult.anomaly_config
            ),
        ).filter(QualityCheckResult.id == result_id)
        if check_type:
            query = query.filter(QualityCheckResult.check_type == check_type)
        row = query.first()
        if not row:
            raise HTTPException(status_code=404, detail="Result not found")
        return row

    def get_metadata_detail(self, result_id: str) -> MetadataResultDetail:
        row = self._get_result_or_404(result_id, "metadata_threshold")
        return MetadataResultDetail(
            id=row.id,
            table_id=row.table_id,
            table_name=row.table.table_name if row.table else None,
            result_type=ResultType.METADATA,
            metric_name=row.metric_name or "",
            status=row.status,
            severity_level=row.severity_level,
            actual_value=row.actual_value,
            threshold_value=row.min_threshold
            if row.min_threshold is not None
            else row.max_threshold,
            min_threshold=row.min_threshold,
            max_threshold=row.max_threshold,
            is_resolved=row.is_resolved,
            processing_date_hour=row.processing_date_hour,
            created_at=row.created_at,
        )

    def get_profiling_detail(self, result_id: str) -> ProfilingResultDetail:
        row = self._get_result_or_404(result_id, "profiling_threshold")
        return ProfilingResultDetail(
            id=row.id,
            table_id=row.table_id,
            table_name=row.table.table_name if row.table else None,
            result_type=ResultType.PROFILING,
            column_name=row.column_name or "",
            metric_name=row.metric_name or "",
            status=row.status,
            severity_level=row.severity_level,
            actual_value=row.actual_value,
            threshold_value=row.min_threshold
            if row.min_threshold is not None
            else row.max_threshold,
            min_threshold=row.min_threshold,
            max_threshold=row.max_threshold,
            is_resolved=row.is_resolved,
            processing_date_hour=row.processing_date_hour,
            created_at=row.created_at,
        )

    def get_rule_detail(self, result_id: str) -> RuleResultDetail:
        row = self._get_result_or_404(result_id, "rule")
        rule = row.rule
        return RuleResultDetail(
            id=row.id,
            rule_id=row.rule_id,
            table_id=row.table_id,
            table_name=row.table.table_name if row.table else None,
            result_type=ResultType.RULE,
            status=row.status,
            severity_level=row.severity_level,
            processing_date_hour=row.processing_date_hour,
            is_resolved=row.is_resolved,
            column_name=row.column_name or (rule.column_name if rule else None),
            constraint_name=rule.constraint_name if rule else row.metric_name,
            code_for_constraint=rule.code_for_constraint if rule else None,
            rule_description=rule.description if rule else None,
            message=row.message,
            created_at=row.created_at,
        )

    def get_anomaly_detail(self, result_id: str) -> AnomalyResultDetail:
        row = self._get_result_or_404(result_id, "anomaly_auc")
        anomaly_result = row.anomaly_result
        config = anomaly_result.anomaly_config if anomaly_result else None
        return AnomalyResultDetail(
            id=row.id,
            table_id=row.table_id,
            status=row.status,
            severity_level=row.severity_level or "warning",
            processing_date_hour=row.processing_date_hour,
            is_resolved=row.is_resolved,
            auc_score=row.actual_value or 0.0,
            auc_threshold=row.min_threshold or 0.0,
            model_config_params=config.model_parameters if config else None,
            top_features=anomaly_result.shap_top_features if anomaly_result else [],
            created_at=row.created_at,
        )

    def resolve_result(self, result_type: str, result_id: str, user_id: str):
        try:
            enum_result_type = ResultType(result_type)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid result type")
        row = (
            self.db.query(QualityCheckResult)
            .filter(
                QualityCheckResult.id == result_id,
                QualityCheckResult.check_type.in_(
                    RESULT_TYPE_TO_CHECK_TYPES[enum_result_type]
                ),
            )
            .first()
        )
        if not row:
            raise HTTPException(status_code=404, detail="Result not found")
        row.is_resolved = True
        row.resolved_by = user_id
        row.resolved_at = datetime.utcnow()
        self.db.commit()
        return {"status": "success"}
