from datetime import datetime
from sqlalchemy.orm import Session

from app.models import (
    BatchTableMetadata,
    BatchTableMetadataMetricsVerify,
    BatchTableProfiling,
    BatchTableProfilingMetricsVerify,
    AUCResult,
    AUCVerify,
    Rule,
    RuleVerify,
    Table,
)


class HomeService:
    def __init__(self, db: Session):
        self.db = db

    def _fail_counts(self, table_id: str, hour: datetime | None = None) -> dict:
        critical = 0
        warning = 0
        total = 0
        checks = [
            (
                BatchTableMetadataMetricsVerify,
                BatchTableMetadataMetricsVerify.processing_date_hour,
            ),
            (
                BatchTableProfilingMetricsVerify,
                BatchTableProfilingMetricsVerify.processing_date_hour,
            ),
            (AUCVerify, AUCVerify.processing_date_hour),
            (RuleVerify, RuleVerify.processing_date_hour),
        ]
        for model, hour_col in checks:
            query = self.db.query(model).filter(model.is_resolved.is_(False))
            if hour:
                query = query.filter(hour_col == hour)
            if model is RuleVerify:
                query = query.join(RuleVerify.rule).filter(Rule.table_id == table_id)
                status_col = RuleVerify.constraint_status
            elif model is AUCVerify:
                query = query.join(AUCVerify.auc_result).filter(
                    AUCResult.table_id == table_id
                )
                status_col = AUCVerify.status
            elif model is BatchTableMetadataMetricsVerify:
                query = query.join(
                    BatchTableMetadataMetricsVerify.batch_table_metadata
                ).filter(BatchTableMetadata.table_id == table_id)
                status_col = BatchTableMetadataMetricsVerify.status
            else:
                query = query.join(
                    BatchTableProfilingMetricsVerify.batch_table_profiling
                ).filter(BatchTableProfiling.table_id == table_id)
                status_col = BatchTableProfilingMetricsVerify.status
            rows = query.filter(status_col == "fail").all()
            total += len(rows)
            critical += sum(1 for row in rows if row.severity_level == "critical")
            warning += sum(1 for row in rows if row.severity_level != "critical")
        return {
            "critical_fail_count": critical,
            "warning_fail_count": warning,
            "total_check_count": total,
        }

    def _table_health(self, table: Table, hour: datetime | None = None) -> dict:
        counts = self._fail_counts(table.id, hour)
        status = (
            "OK"
            if counts["critical_fail_count"] == 0 and counts["warning_fail_count"] == 0
            else "WARNING"
        )
        if counts["critical_fail_count"] > 0:
            status = "CRITICAL"
        return {
            "table_count": 1,
            "table_id": table.id,
            "schema_name": table.schema_name,
            "table_name": table.table_name,
            "status": status,
            **counts,
        }

    def table_health(self, table_id: str, hour: datetime | None = None) -> dict:
        table = self.db.query(Table).filter(Table.id == table_id).first()
        if not table:
            return {
                "table_count": 0,
                "table_id": table_id,
                "schema_name": "",
                "table_name": "",
                "critical_fail_count": 0,
                "warning_fail_count": 0,
                "total_check_count": 0,
                "status": "UNKNOWN",
            }
        return self._table_health(table, hour)

    def table_healths(self, hour: datetime | None = None) -> list[dict]:
        from app.models import Connection

        tables = (
            self.db.query(Table)
            .join(Connection)
            .filter(Table.is_active.is_(True), Connection.is_active.is_(True))
            .order_by(Table.schema_name, Table.table_name)
            .all()
        )
        return [self._table_health(table, hour) for table in tables]

    def schema_healths(self, hour: datetime | None = None) -> list[dict]:
        grouped = {}
        for item in self.table_healths(hour):
            grouped.setdefault(item["schema_name"], []).append(item)
        result = []
        for schema_name, items in grouped.items():
            result.append(
                {
                    "schema_name": schema_name,
                    "table_count": len(items),
                    "critical_fail_count": sum(
                        item["critical_fail_count"] for item in items
                    ),
                    "warning_fail_count": sum(
                        item["warning_fail_count"] for item in items
                    ),
                    "total_check_count": sum(
                        item["total_check_count"] for item in items
                    ),
                }
            )
        return result

    def get_platform_overview(self, schema_name: str | None = None) -> dict:
        from app.models import Connection

        query = (
            self.db.query(Table)
            .join(Connection)
            .filter(Table.is_active.is_(True), Connection.is_active.is_(True))
        )
        if schema_name:
            query = query.filter(Table.schema_name == schema_name)
        total_tables = query.count()
        hours = self.processing_hours()
        latest_batch = hours[0] if hours else None
        return {"total_tables": total_tables, "latest_batch": latest_batch}

    def get_timeline_stats(
        self,
        schema_name: str | None = None,
        from_time: datetime | None = None,
        to_time: datetime | None = None,
    ) -> list[dict]:
        hours = self.processing_hours()

        if from_time:
            # Ensure naive datetimes are handled if necessary, though processing_hours usually returns offset-naive
            hours = [h for h in hours if h >= from_time]
        if to_time:
            hours = [h for h in hours if h <= to_time]

        # Default to last 3 if no range specified
        if not from_time and not to_time:
            hours = hours[:3]

        timeline = []
        checks = [
            (BatchTableMetadataMetricsVerify, BatchTableMetadataMetricsVerify.status),
            (BatchTableProfilingMetricsVerify, BatchTableProfilingMetricsVerify.status),
            (AUCVerify, AUCVerify.status),
            (RuleVerify, RuleVerify.constraint_status),
        ]
        for hour in hours:
            pass_critical = 0
            pass_warning = 0
            fail_critical = 0
            fail_warning = 0

            for model, status_col in checks:
                query = self.db.query(model).filter(model.processing_date_hour == hour)
                if schema_name:
                    if model is RuleVerify:
                        query = (
                            query.join(RuleVerify.rule)
                            .join(Table)
                            .filter(Table.schema_name == schema_name)
                        )
                    elif model is AUCVerify:
                        query = (
                            query.join(AUCVerify.auc_result)
                            .join(Table)
                            .filter(Table.schema_name == schema_name)
                        )
                    elif model is BatchTableMetadataMetricsVerify:
                        query = (
                            query.join(
                                BatchTableMetadataMetricsVerify.batch_table_metadata
                            )
                            .join(Table)
                            .filter(Table.schema_name == schema_name)
                        )
                    else:
                        query = (
                            query.join(
                                BatchTableProfilingMetricsVerify.batch_table_profiling
                            )
                            .join(Table)
                            .filter(Table.schema_name == schema_name)
                        )

                rows = query.all()
                for row in rows:
                    status = getattr(row, status_col.name)
                    severity = row.severity_level
                    if status == "pass":
                        if severity == "critical":
                            pass_critical += 1
                        else:
                            pass_warning += 1
                    elif status == "fail":
                        if severity == "critical":
                            fail_critical += 1
                        else:
                            fail_warning += 1

            timeline.append(
                {
                    "processing_date_hour": hour,
                    "pass_critical": pass_critical,
                    "pass_warning": pass_warning,
                    "fail_critical": fail_critical,
                    "fail_warning": fail_warning,
                }
            )
        return timeline[::-1]

    def processing_hours(self) -> list[datetime]:
        hours = set()
        for model in (BatchTableMetadata, BatchTableProfiling, AUCResult, RuleVerify):
            rows = self.db.query(model.processing_date_hour).distinct().all()
            hours.update(row[0] for row in rows if row[0])
        return sorted(hours, reverse=True)

    def get_home_summary(
        self,
        connection_id: str | None = None,
        catalog_name: str | None = None,
        schema_name: str | None = None,
        from_time: datetime | None = None,
        to_time: datetime | None = None,
    ) -> dict:
        # Base query for tables
        from app.models import Connection

        table_query = (
            self.db.query(Table)
            .join(Connection)
            .filter(Table.is_active.is_(True), Connection.is_active.is_(True))
        )
        if connection_id:
            table_query = table_query.filter(Table.connection_id == connection_id)
        if catalog_name:
            table_query = table_query.filter(Table.catalog_name == catalog_name)
        if schema_name:
            table_query = table_query.filter(Table.schema_name == schema_name)

        total_tables = table_query.count()
        table_ids = [t.id for t in table_query.all()]

        if not table_ids:
            return {
                "total_tables": 0,
                "total_pass": 0,
                "total_fail": 0,
                "warning_fail": 0,
                "critical_fail": 0,
                "unresolved_alerts": 0,
            }

        checks = [
            (BatchTableMetadataMetricsVerify, BatchTableMetadataMetricsVerify.status),
            (BatchTableProfilingMetricsVerify, BatchTableProfilingMetricsVerify.status),
            (AUCVerify, AUCVerify.status),
            (RuleVerify, RuleVerify.constraint_status),
        ]

        total_pass = 0
        total_fail = 0
        warning_fail = 0
        critical_fail = 0
        unresolved_alerts = 0

        for model, status_col in checks:
            query = self.db.query(model)

            # Join with tables to filter
            if model is RuleVerify:
                query = query.join(RuleVerify.rule).filter(Rule.table_id.in_(table_ids))
            elif model is AUCVerify:
                query = query.join(AUCVerify.auc_result).filter(
                    AUCResult.table_id.in_(table_ids)
                )
            elif model is BatchTableMetadataMetricsVerify:
                query = query.join(
                    BatchTableMetadataMetricsVerify.batch_table_metadata
                ).filter(BatchTableMetadata.table_id.in_(table_ids))
            else:
                query = query.join(
                    BatchTableProfilingMetricsVerify.batch_table_profiling
                ).filter(BatchTableProfiling.table_id.in_(table_ids))

            if from_time:
                query = query.filter(model.processing_date_hour >= from_time)
            if to_time:
                query = query.filter(model.processing_date_hour <= to_time)

            rows = query.all()
            for row in rows:
                status = (
                    getattr(row, "status", None)
                    or getattr(row, "constraint_status", "unknown")
                ).lower()
                if status == "pass":
                    total_pass += 1
                elif status == "fail":
                    total_fail += 1
                    if row.severity_level == "critical":
                        critical_fail += 1
                    else:
                        warning_fail += 1

                    if not row.is_resolved:
                        unresolved_alerts += 1

        return {
            "total_tables": total_tables,
            "total_pass": total_pass,
            "total_fail": total_fail,
            "warning_fail": warning_fail,
            "critical_fail": critical_fail,
            "unresolved_alerts": unresolved_alerts,
        }

    def quality_results(
        self,
        result_type: str | None = None,
        unresolved_only: bool = False,
        table_id: str | None = None,
    ) -> list[dict]:
        sources = [
            (
                "metadata",
                BatchTableMetadataMetricsVerify,
                BatchTableMetadataMetricsVerify.status,
            ),
            (
                "profiling",
                BatchTableProfilingMetricsVerify,
                BatchTableProfilingMetricsVerify.status,
            ),
            ("anomaly", AUCVerify, AUCVerify.status),
            ("rule", RuleVerify, RuleVerify.constraint_status),
        ]
        results = []
        for name, model, status_col in sources:
            if result_type and result_type != name:
                continue
            query = self.db.query(model)
            if unresolved_only:
                query = query.filter(model.is_resolved.is_(False), status_col == "fail")
            if table_id:
                if model is RuleVerify:
                    query = query.join(RuleVerify.rule).filter(
                        Rule.table_id == table_id
                    )
                elif model is AUCVerify:
                    query = query.join(AUCVerify.auc_result).filter(
                        AUCResult.table_id == table_id
                    )
                elif model is BatchTableMetadataMetricsVerify:
                    query = query.join(
                        BatchTableMetadataMetricsVerify.batch_table_metadata
                    ).filter(BatchTableMetadata.table_id == table_id)
                else:
                    query = query.join(
                        BatchTableProfilingMetricsVerify.batch_table_profiling
                    ).filter(BatchTableProfiling.table_id == table_id)

            for row in (
                query.order_by(model.processing_date_hour.desc()).limit(200).all()
            ):
                results.append(
                    {
                        "id": row.id,
                        "result_type": name,
                        "status": getattr(row, "status", None) or row.constraint_status,
                        "severity_level": getattr(row, "severity_level", None),
                        "is_resolved": row.is_resolved,
                        "processing_date_hour": row.processing_date_hour,
                    }
                )
        return sorted(
            results, key=lambda item: item["processing_date_hour"], reverse=True
        )
