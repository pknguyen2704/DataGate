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
    "metadata": ResultType.METADATA,
    "profiling": ResultType.PROFILING,
    "rule": ResultType.RULE,
    "anomaly": ResultType.ANOMALY,
}

RESULT_TYPE_TO_CHECK_TYPES = {
    ResultType.METADATA: ["metadata"],
    ResultType.PROFILING: ["profiling"],
    ResultType.RULE: ["rule"],
    ResultType.ANOMALY: ["anomaly"],
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
        is_resolved: bool | None = None,
    ):
        query = self.db.query(QualityCheckResult).options(
            joinedload(QualityCheckResult.table),
            joinedload(QualityCheckResult.rule),
            joinedload(QualityCheckResult.threshold),
            joinedload(QualityCheckResult.anomaly_result).joinedload(
                AnomalyResult.model_parameter
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
        if is_resolved is not None:
            query = query.filter(QualityCheckResult.is_resolved == is_resolved)
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

    def _to_anomaly_result_out(self, row: AnomalyResult) -> QualityResultOut:
        verify = row.quality_check_results[0] if row.quality_check_results else None
        threshold_value = None
        if verify:
            threshold_value = (
                verify.min_threshold
                if verify.min_threshold is not None
                else verify.max_threshold
            )

        return QualityResultOut(
            id=row.id,
            table_id=row.table_id,
            table_name=row.table.table_name if row.table else None,
            result_type=ResultType.ANOMALY,
            status=verify.status if verify else "pass",
            severity_level=verify.severity_level if verify else None,
            processing_date_hour=row.processing_date_hour,
            is_resolved=verify.is_resolved if verify else False,
            column_name=None,
            metric_name="auc_score",
            actual_value=row.auc_score,
            threshold_value=threshold_value,
            message=verify.message if verify else None,
            created_at=verify.created_at if verify else row.created_at,
        )

    def _anomaly_query(
        self,
        table_id: str | None = None,
        processing_date_hour: datetime | None = None,
        status_val: str | None = None,
        severity_level: str | None = None,
        is_resolved: bool | None = None,
    ):
        query = self.db.query(AnomalyResult).options(
            joinedload(AnomalyResult.table),
            joinedload(AnomalyResult.model_parameter),
            joinedload(AnomalyResult.quality_check_results),
        )
        if table_id:
            query = query.filter(AnomalyResult.table_id == table_id)
        if processing_date_hour:
            query = query.filter(
                AnomalyResult.processing_date_hour == processing_date_hour
            )
        rows = query.order_by(AnomalyResult.processing_date_hour.desc()).all()
        if status_val:
            rows = [
                row
                for row in rows
                if (
                    row.quality_check_results[0].status
                    if row.quality_check_results
                    else "pass"
                )
                == status_val
            ]
        if severity_level:
            rows = [
                row
                for row in rows
                if row.quality_check_results
                and row.quality_check_results[0].severity_level == severity_level
            ]
        if is_resolved is not None:
            rows = [
                row
                for row in rows
                if (
                    row.quality_check_results[0].is_resolved
                    if row.quality_check_results
                    else False
                ) == is_resolved
            ]
        return rows

    def list_results(
        self,
        table_id: str | None = None,
        layer: str | None = None,
        processing_date_hour: datetime | None = None,
        status_val: str | None = None,
        severity_level: str | None = None,
        result_type: str | None = None,
        is_resolved: bool | None = None,
        page: int = 1,
        page_size: int = 50,
    ):
        if result_type == ResultType.ANOMALY.value:
            rows = self._anomaly_query(
                table_id=table_id,
                processing_date_hour=processing_date_hour,
                status_val=status_val,
                severity_level=severity_level,
                is_resolved=is_resolved,
            )
            total = len(rows)
            paged_rows = rows[(page - 1) * page_size : page * page_size]
            return {
                "items": [self._to_anomaly_result_out(row) for row in paged_rows],
                "total": total,
                "page": page,
                "page_size": page_size,
            }

        query = self._base_query(
            table_id=table_id,
            processing_date_hour=processing_date_hour,
            status_val=status_val,
            severity_level=severity_level,
            result_type=result_type,
            is_resolved=is_resolved,
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
        non_anomaly_query = query.filter(QualityCheckResult.check_type != "anomaly")
        anomaly_rows = self._anomaly_query(table_id=table_id)

        total = non_anomaly_query.count() + len(anomaly_rows)
        passed = non_anomaly_query.filter(QualityCheckResult.status == "pass").count()
        passed += sum(
            1
            for row in anomaly_rows
            if (
                row.quality_check_results[0].status
                if row.quality_check_results
                else "pass"
            )
            == "pass"
        )
        failed_rows = non_anomaly_query.filter(QualityCheckResult.status == "fail").all()
        failed_anomaly_rows = [
            row
            for row in anomaly_rows
            if row.quality_check_results and row.quality_check_results[0].status == "fail"
        ]
        failed = len(failed_rows) + len(failed_anomaly_rows)
        unresolved = sum(1 for row in failed_rows if not row.is_resolved)
        unresolved += sum(
            1 for row in failed_anomaly_rows if not row.quality_check_results[0].is_resolved
        )
        critical_fail = sum(
            1 for row in failed_rows if row.severity_level == "critical"
        )
        critical_fail += sum(
            1
            for row in failed_anomaly_rows
            if row.quality_check_results[0].severity_level == "critical"
        )
        warning_fail = failed - critical_fail

        by_type_rows = (
            non_anomaly_query.with_entities(QualityCheckResult.check_type, func.count())
            .group_by(QualityCheckResult.check_type)
            .all()
        )
        checks_by_type = {"metadata": 0, "profiling": 0, "rule": 0, "anomaly": 0}
        for check_type, count in by_type_rows:
            result_type = CHECK_TYPE_TO_RESULT_TYPE.get(check_type)
            if result_type:
                checks_by_type[result_type.value] += count
        checks_by_type[ResultType.ANOMALY.value] = len(anomaly_rows)

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
                AnomalyResult.model_parameter
            ),
        ).filter(QualityCheckResult.id == result_id)
        if check_type:
            query = query.filter(QualityCheckResult.check_type == check_type)
        row = query.first()
        if not row:
            raise HTTPException(status_code=404, detail="Result not found")
        return row

    def get_metadata_detail(self, result_id: str) -> MetadataResultDetail:
        row = self._get_result_or_404(result_id, "metadata")
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
            description=row.threshold.description if row.threshold else None,
            is_resolved=row.is_resolved,
            processing_date_hour=row.processing_date_hour,
            created_at=row.created_at,
        )

    def get_profiling_detail(self, result_id: str) -> ProfilingResultDetail:
        row = self._get_result_or_404(result_id, "profiling")
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
            description=row.threshold.description if row.threshold else None,
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
        row = (
            self.db.query(QualityCheckResult)
            .options(
                joinedload(QualityCheckResult.anomaly_result).joinedload(
                    AnomalyResult.model_parameter
                ),
                joinedload(QualityCheckResult.anomaly_result).joinedload(
                    AnomalyResult.shap_results
                ),
            )
            .filter(
                QualityCheckResult.id == result_id,
                QualityCheckResult.check_type == "anomaly",
            )
            .first()
        )
        anomaly_result = row.anomaly_result if row else None
        if anomaly_result is None:
            anomaly_result = (
                self.db.query(AnomalyResult)
                .options(
                    joinedload(AnomalyResult.model_parameter),
                    joinedload(AnomalyResult.shap_results),
                    joinedload(AnomalyResult.quality_check_results),
                )
                .filter(AnomalyResult.id == result_id)
                .first()
            )
        if anomaly_result is None:
            raise HTTPException(status_code=404, detail="Result not found")

        verify = row or (
            anomaly_result.quality_check_results[0]
            if anomaly_result.quality_check_results
            else None
        )
        model_parameter = anomaly_result.model_parameter if anomaly_result else None
        top_features = []
        if anomaly_result:
            top_features = [
                {
                    "feature_name": item.feature_name,
                    "shap_score": item.shap_score,
                    "rank": item.shap_rank,
                }
                for item in sorted(
                    anomaly_result.shap_results,
                    key=lambda shap: shap.shap_rank,
                )
            ]
            if not top_features:
                top_features = anomaly_result.shap_top_features or []
        return AnomalyResultDetail(
            id=anomaly_result.id,
            table_id=anomaly_result.table_id,
            status=verify.status if verify else "pass",
            severity_level=(verify.severity_level if verify else None) or "warning",
            processing_date_hour=anomaly_result.processing_date_hour,
            is_resolved=verify.is_resolved if verify else False,
            auc_score=verify.actual_value if verify else anomaly_result.auc_score,
            auc_threshold=verify.max_threshold if verify else None,
            anomaly_config_params={
                "learning_rate": model_parameter.learning_rate,
                "num_leaves": model_parameter.num_leaves,
                "max_depth": model_parameter.max_depth,
                "min_data_in_leaf": model_parameter.min_data_in_leaf,
                "bagging_fraction": model_parameter.bagging_fraction,
                "bagging_freq": model_parameter.bagging_freq,
                "feature_fraction": model_parameter.feature_fraction,
                "lambda_l1": model_parameter.lambda_l1,
                "lambda_l2": model_parameter.lambda_l2,
                "min_gain_to_split": model_parameter.min_gain_to_split,
                "max_bin": model_parameter.max_bin,
                "num_iterations": model_parameter.num_iterations,
            } if model_parameter else None,
            top_features=top_features,
            created_at=verify.created_at if verify else anomaly_result.created_at,
        )

    def resolve_result(self, result_type: str, result_id: str, user_id: str):
        try:
            enum_result_type = ResultType(result_type)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid result type")
        row = (
            self.db.query(QualityCheckResult)
            .filter(
                (QualityCheckResult.id == result_id) | (QualityCheckResult.anomaly_result_id == result_id),
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
