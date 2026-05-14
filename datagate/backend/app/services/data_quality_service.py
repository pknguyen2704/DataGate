from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from fastapi import HTTPException, status

from app.models import (
    Table, BatchTableMetadata, BatchTableMetadataMetricsVerify,
    BatchTableProfiling, BatchTableProfilingMetricsVerify,
    RuleVerify, LightGBMAUC, LightGBMAUCVerify, SHAPResult, LightGBMParameter, Rule
)
from app.schemas.data_quality_schema import (
    QualityResultOut, DataQualitySummary, ResultType,
    MetadataResultDetail, ProfilingResultDetail, RuleResultDetail, AnomalyResultDetail
)

class DataQualityService:
    def __init__(self, db: Session):
        self.db = db

    def list_results(
        self, 
        table_id: str | None = None,
        layer: str | None = None,
        processing_date_hour: datetime | None = None,
        status_val: str | None = None,
        severity_level: str | None = None,
        result_type: str | None = None,
        page: int = 1,
        page_size: int = 50
    ):
        all_results = []
        
        # Helper to fetch and normalize results
        def fetch_metadata():
            query = self.db.query(BatchTableMetadataMetricsVerify).join(BatchTableMetadataMetricsVerify.batch_table_metadata)
            if table_id: query = query.filter(BatchTableMetadata.table_id == table_id)
            if processing_date_hour: query = query.filter(BatchTableMetadataMetricsVerify.processing_date_hour == processing_date_hour)
            if status_val: query = query.filter(BatchTableMetadataMetricsVerify.status == status_val)
            if severity_level: query = query.filter(BatchTableMetadataMetricsVerify.severity_level == severity_level)
            
            results = query.order_by(desc(BatchTableMetadataMetricsVerify.processing_date_hour)).all()
            return [
                QualityResultOut(
                    id=r.id,
                    table_id=r.batch_table_metadata.table_id,
                    table_name=r.batch_table_metadata.table.table_name,
                    result_type=ResultType.METADATA,
                    status=r.status,
                    severity_level=r.severity_level,
                    processing_date_hour=r.processing_date_hour,
                    is_resolved=r.is_resolved,
                    metric_name=r.metadata_manual_threshold.metric_name,
                    actual_value=r.actual_value,
                    threshold_value=r.min_threshold if r.min_threshold is not None else r.max_threshold,
                    created_at=r.created_at
                ) for r in results
            ]

        def fetch_profiling():
            query = self.db.query(BatchTableProfilingMetricsVerify).join(BatchTableProfilingMetricsVerify.batch_table_profiling)
            if table_id: query = query.filter(BatchTableProfiling.table_id == table_id)
            if processing_date_hour: query = query.filter(BatchTableProfilingMetricsVerify.processing_date_hour == processing_date_hour)
            if status_val: query = query.filter(BatchTableProfilingMetricsVerify.status == status_val)
            if severity_level: query = query.filter(BatchTableProfilingMetricsVerify.severity_level == severity_level)
            
            results = query.order_by(desc(BatchTableProfilingMetricsVerify.processing_date_hour)).all()
            return [
                QualityResultOut(
                    id=r.id,
                    table_id=r.batch_table_profiling.table_id,
                    table_name=r.batch_table_profiling.table.table_name,
                    result_type=ResultType.PROFILING,
                    status=r.status,
                    severity_level=r.severity_level,
                    processing_date_hour=r.processing_date_hour,
                    is_resolved=r.is_resolved,
                    column_name=r.batch_table_profiling.column_name,
                    metric_name=r.profiling_manual_threshold.metric_name,
                    actual_value=r.actual_value,
                    threshold_value=r.min_threshold if r.min_threshold is not None else r.max_threshold,
                    created_at=r.created_at
                ) for r in results
            ]

        def fetch_rules():
            query = self.db.query(RuleVerify).join(RuleVerify.rule)
            if table_id: query = query.filter(Rule.table_id == table_id)
            if processing_date_hour: query = query.filter(RuleVerify.processing_date_hour == processing_date_hour)
            if status_val: query = query.filter(RuleVerify.constraint_status == status_val)
            if severity_level: query = query.filter(RuleVerify.severity_level == severity_level)
            
            results = query.order_by(desc(RuleVerify.processing_date_hour)).all()
            return [
                QualityResultOut(
                    id=r.id,
                    table_id=r.rule.table_id,
                    table_name=r.rule.table.table_name,
                    result_type=ResultType.RULE,
                    status=r.constraint_status,
                    severity_level=r.severity_level,
                    processing_date_hour=r.processing_date_hour,
                    is_resolved=r.is_resolved,
                    column_name=r.rule.column_name,
                    message=r.constraint_message,
                    created_at=r.created_at
                ) for r in results
            ]

        def fetch_anomalies():
            query = self.db.query(LightGBMAUCVerify).join(LightGBMAUCVerify.lightgbm_result)
            if table_id: query = query.filter(LightGBMAUCVerify.lightgbm_result.has(table_id=table_id))
            if processing_date_hour: query = query.filter(LightGBMAUCVerify.processing_date_hour == processing_date_hour)
            if status_val: query = query.filter(LightGBMAUCVerify.status == status_val)
            if severity_level: query = query.filter(LightGBMAUCVerify.severity_level == severity_level)
            
            results = query.order_by(desc(LightGBMAUCVerify.processing_date_hour)).all()
            return [
                QualityResultOut(
                    id=r.id,
                    table_id=r.lightgbm_result.table_id,
                    table_name=r.lightgbm_result.table.table_name,
                    result_type=ResultType.ANOMALY,
                    status=r.status,
                    severity_level=r.severity_level,
                    processing_date_hour=r.processing_date_hour,
                    is_resolved=r.is_resolved,
                    actual_value=r.auc_score,
                    threshold_value=r.auc_threshold,
                    created_at=r.created_at
                ) for r in results
            ]

        # Combine results based on result_type filter
        if not result_type or result_type == ResultType.METADATA:
            all_results.extend(fetch_metadata())
        if not result_type or result_type == ResultType.PROFILING:
            all_results.extend(fetch_profiling())
        if not result_type or result_type == ResultType.RULE:
            all_results.extend(fetch_rules())
        if not result_type or result_type == ResultType.ANOMALY:
            all_results.extend(fetch_anomalies())

        # Sort combined results by date
        all_results.sort(key=lambda x: x.processing_date_hour, reverse=True)
        
        total = len(all_results)
        
        # Pagination
        start = (page - 1) * page_size
        end = start + page_size
        items = all_results[start:end]
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size
        }

    def get_summary(self, table_id: str | None = None):
        # This is a bit complex since data is in 4 tables. 
        
        def count_stats(model):
            q = self.db.query(model)
            if table_id:
                if model is BatchTableMetadataMetricsVerify:
                    q = q.join(BatchTableMetadata, model.batch_table_metadata_id == BatchTableMetadata.id).filter(BatchTableMetadata.table_id == table_id)
                elif model is BatchTableProfilingMetricsVerify:
                    q = q.join(BatchTableProfiling, model.batch_table_profiling_id == BatchTableProfiling.id).filter(BatchTableProfiling.table_id == table_id)
                elif model is RuleVerify:
                    q = q.join(Rule, model.rule_id == Rule.id).filter(Rule.table_id == table_id)
                elif model is LightGBMAUCVerify:
                    q = q.join(LightGBMAUC, model.lightgbm_result_id == LightGBMAUC.id).filter(LightGBMAUC.table_id == table_id)
            
            status_col = model.status if hasattr(model, 'status') else model.constraint_status
            
            # Define pass/fail filters
            fail_filter = (status_col == 'fail')
            pass_filter = (status_col == 'pass')

            total = q.count()
            failed_rows = q.filter(fail_filter).all()
            
            failed = len(failed_rows)
            passed = q.filter(pass_filter).count()
            unresolved = sum(1 for r in failed_rows if not r.is_resolved)
            
            critical_fail = sum(1 for r in failed_rows if r.severity_level == 'critical')
            warning_fail = failed - critical_fail
            
            return total, passed, failed, unresolved, warning_fail, critical_fail

        # Collect counts from all 4 verification tables
        m_total, m_pass, m_fail, m_unres, m_warn, m_crit = count_stats(BatchTableMetadataMetricsVerify)
        p_total, p_pass, p_fail, p_unres, p_warn, p_crit = count_stats(BatchTableProfilingMetricsVerify)
        r_total, r_pass, r_fail, r_unres, r_warn, r_crit = count_stats(RuleVerify)
        a_total, a_pass, a_fail, a_unres, a_warn, a_crit = count_stats(LightGBMAUCVerify)
        
        total = m_total + p_total + r_total + a_total
        passed = m_pass + p_pass + r_pass + a_pass
        failed = m_fail + p_fail + r_fail + a_fail
        unresolved = m_unres + p_unres + r_unres + a_unres
        warning_fail = m_warn + p_warn + r_warn + a_warn
        critical_fail = m_crit + p_crit + r_crit + a_crit
        
        pass_rate = (passed / total * 100) if total > 0 else 100.0
        
        return DataQualitySummary(
            total_checks=total,
            total_pass=passed,
            total_fail=failed,
            unresolved_alerts=unresolved,
            warning_fail=warning_fail,
            critical_fail=critical_fail,
            pass_rate=pass_rate,
            checks_by_type={
                "metadata": m_total,
                "profiling": p_total,
                "rule": r_total,
                "anomaly": a_total
            }
        )

    def get_metadata_detail(self, result_id: str) -> MetadataResultDetail:
        r = self.db.query(BatchTableMetadataMetricsVerify).filter(BatchTableMetadataMetricsVerify.id == result_id).first()
        if not r: raise HTTPException(status_code=404, detail="Result not found")
        return MetadataResultDetail(
            id=r.id,
            table_id=r.batch_table_metadata.table_id,
            table_name=r.batch_table_metadata.table.table_name,
            result_type=ResultType.METADATA,
            status=r.status,
            severity_level=r.severity_level,
            processing_date_hour=r.processing_date_hour,
            is_resolved=r.is_resolved,
            metric_name=r.metadata_manual_threshold.metric_name,
            actual_value=r.actual_value,
            min_threshold=r.min_threshold,
            max_threshold=r.max_threshold
        )

    def get_profiling_detail(self, result_id: str) -> ProfilingResultDetail:
        r = self.db.query(BatchTableProfilingMetricsVerify).filter(BatchTableProfilingMetricsVerify.id == result_id).first()
        if not r: raise HTTPException(status_code=404, detail="Result not found")
        return ProfilingResultDetail(
            id=r.id,
            table_id=r.batch_table_profiling.table_id,
            table_name=r.batch_table_profiling.table.table_name,
            result_type=ResultType.PROFILING,
            status=r.status,
            severity_level=r.severity_level,
            processing_date_hour=r.processing_date_hour,
            is_resolved=r.is_resolved,
            column_name=r.batch_table_profiling.column_name,
            metric_name=r.profiling_manual_threshold.metric_name,
            actual_value=r.actual_value,
            min_threshold=r.min_threshold,
            max_threshold=r.max_threshold
        )

    def get_rule_detail(self, result_id: str) -> RuleResultDetail:
        r = self.db.query(RuleVerify).filter(RuleVerify.id == result_id).first()
        if not r: raise HTTPException(status_code=404, detail="Result not found")
        return RuleResultDetail(
            id=r.id,
            table_id=r.rule.table_id,
            table_name=r.rule.table.table_name,
            result_type=ResultType.RULE,
            status=r.constraint_status,
            severity_level=r.severity_level,
            processing_date_hour=r.processing_date_hour,
            is_resolved=r.is_resolved,
            column_name=r.rule.column_name,
            constraint_name=r.rule.constraint_name,
            code_for_constraint=r.rule.code_for_constraint,
            rule_description=r.rule.rule_description,
            message=r.constraint_message
        )

    def get_anomaly_detail(self, result_id: str) -> AnomalyResultDetail:
        r = self.db.query(LightGBMAUCVerify).filter(LightGBMAUCVerify.id == result_id).first()
        if not r: raise HTTPException(status_code=404, detail="Result not found")
        
        # Get SHAP
        shap = self.db.query(SHAPResult).filter(SHAPResult.lightgbm_result_id == r.lightgbm_result_id).order_by(SHAPResult.shap_rank).all()
        top_features = [{"feature_name": s.feature_name, "shap_score": s.shap_score, "shap_rank": s.shap_rank} for s in shap]
        
        # Get Model Config
        params = self.db.query(LightGBMParameter).filter(LightGBMParameter.id == r.lightgbm_result.lightgbm_parameter_id).first()
        model_config = None
        if params:
            model_config = {
                "learning_rate": params.learning_rate,
                "num_leaves": params.num_leaves,
                "max_depth": params.max_depth,
                "num_iterations": params.num_iterations
            }
            
        return AnomalyResultDetail(
            id=r.id,
            table_id=r.lightgbm_result.table_id,
            status=r.status,
            severity_level=r.severity_level or "warning",
            processing_date_hour=r.processing_date_hour,
            is_resolved=r.is_resolved,
            auc_score=r.auc_score or 0.0,
            auc_threshold=r.auc_threshold or 0.0,
            model_config_params=model_config,
            top_features=top_features,
            created_at=r.created_at
        )

    def resolve_result(self, result_type: str, result_id: str, user_id: str):
        model = None
        if result_type == ResultType.METADATA: model = BatchTableMetadataMetricsVerify
        elif result_type == ResultType.PROFILING: model = BatchTableProfilingMetricsVerify
        elif result_type == ResultType.RULE: model = RuleVerify
        elif result_type == ResultType.ANOMALY: model = LightGBMAUCVerify
        
        if not model: raise HTTPException(status_code=400, detail="Invalid result type")
        
        r = self.db.query(model).filter(model.id == result_id).first()
        if not r: raise HTTPException(status_code=404, detail="Result not found")
        
        r.is_resolved = True
        r.resolved_by = user_id
        self.db.commit()
        return {"status": "success"}
