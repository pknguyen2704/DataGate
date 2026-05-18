from datetime import datetime

from sqlalchemy.orm import Session

from app.models import Connection, QualityCheckResult, QualityMetricObservation, Table


class HomeService:
    def __init__(self, db: Session):
        self.db = db

    def _result_query(
        self,
        table_ids: list[str] | None = None,
        hour: datetime | None = None,
        from_time: datetime | None = None,
        to_time: datetime | None = None,
    ):
        query = self.db.query(QualityCheckResult)
        if table_ids is not None:
            query = query.filter(QualityCheckResult.table_id.in_(table_ids))
        if hour:
            query = query.filter(QualityCheckResult.processing_date_hour == hour)
        if from_time:
            query = query.filter(QualityCheckResult.processing_date_hour >= from_time)
        if to_time:
            query = query.filter(QualityCheckResult.processing_date_hour <= to_time)
        return query

    def _fail_counts(self, table_id: str, hour: datetime | None = None) -> dict:
        rows = (
            self._result_query([str(table_id)], hour)
            .filter(
                QualityCheckResult.status == "fail",
                QualityCheckResult.is_resolved.is_(False),
            )
            .all()
        )
        critical = sum(1 for row in rows if row.severity_level == "critical")
        warning = len(rows) - critical
        return {
            "critical_fail_count": critical,
            "warning_fail_count": warning,
            "total_check_count": len(rows),
        }

    def _table_health(self, table: Table, hour: datetime | None = None) -> dict:
        counts = self._fail_counts(str(table.id), hour)
        status = "OK"
        if counts["warning_fail_count"] > 0:
            status = "WARNING"
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
        tables = (
            self.db.query(Table)
            .join(Connection)
            .filter(Connection.is_active.is_(True))
            .order_by(Table.schema_name, Table.table_name)
            .all()
        )
        return [self._table_health(table, hour) for table in tables]

    def schema_healths(self, hour: datetime | None = None) -> list[dict]:
        grouped = {}
        for item in self.table_healths(hour):
            grouped.setdefault(item["schema_name"], []).append(item)
        return [
            {
                "schema_name": schema_name,
                "table_count": len(items),
                "critical_fail_count": sum(item["critical_fail_count"] for item in items),
                "warning_fail_count": sum(item["warning_fail_count"] for item in items),
                "total_check_count": sum(item["total_check_count"] for item in items),
            }
            for schema_name, items in grouped.items()
        ]

    def get_platform_overview(self, schema_name: str | None = None) -> dict:
        query = (
            self.db.query(Table)
            .join(Connection)
            .filter(Connection.is_active.is_(True))
        )
        if schema_name:
            query = query.filter(Table.schema_name == schema_name)
        hours = self.processing_hours()
        return {"total_tables": query.count(), "latest_batch": hours[0] if hours else None}

    def get_timeline_stats(
        self,
        schema_name: str | None = None,
        from_time: datetime | None = None,
        to_time: datetime | None = None,
    ) -> list[dict]:
        hours = self.processing_hours()
        if from_time:
            hours = [hour for hour in hours if hour >= from_time]
        if to_time:
            hours = [hour for hour in hours if hour <= to_time]
        if not from_time and not to_time:
            hours = hours[:3]

        timeline = []
        for hour in hours:
            query = self.db.query(QualityCheckResult).filter(
                QualityCheckResult.processing_date_hour == hour
            )
            if schema_name:
                query = query.join(Table).filter(Table.schema_name == schema_name)
            rows = query.all()
            pass_critical = pass_warning = fail_critical = fail_warning = 0
            for row in rows:
                if row.status == "pass":
                    if row.severity_level == "critical":
                        pass_critical += 1
                    else:
                        pass_warning += 1
                elif row.status == "fail":
                    if row.severity_level == "critical":
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
        for model in (QualityMetricObservation, QualityCheckResult):
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
        table_query = (
            self.db.query(Table)
            .join(Connection)
            .filter(Connection.is_active.is_(True))
        )
        if connection_id:
            table_query = table_query.filter(Table.connection_id == connection_id)
        if catalog_name:
            table_query = table_query.filter(Table.catalog_name == catalog_name)
        if schema_name:
            table_query = table_query.filter(Table.schema_name == schema_name)

        total_tables = table_query.count()
        table_ids = [str(t.id) for t in table_query.all()]
        if not table_ids:
            return {
                "total_tables": 0,
                "total_pass": 0,
                "total_fail": 0,
                "warning_fail": 0,
                "critical_fail": 0,
                "unresolved_alerts": 0,
            }

        rows = self._result_query(table_ids, from_time=from_time, to_time=to_time).all()
        total_pass = sum(1 for row in rows if row.status == "pass")
        failed = [row for row in rows if row.status == "fail"]
        critical_fail = sum(1 for row in failed if row.severity_level == "critical")
        return {
            "total_tables": total_tables,
            "total_pass": total_pass,
            "total_fail": len(failed),
            "warning_fail": len(failed) - critical_fail,
            "critical_fail": critical_fail,
            "unresolved_alerts": sum(1 for row in failed if not row.is_resolved),
        }

    def quality_results(
        self,
        result_type: str | None = None,
        unresolved_only: bool = False,
        table_id: str | None = None,
    ) -> list[dict]:
        type_map = {
            "metadata": ["metadata_threshold"],
            "profiling": ["profiling_threshold"],
            "rule": ["rule"],
            "anomaly": ["anomaly_auc"],
        }
        reverse_type_map = {
            "metadata_threshold": "metadata",
            "profiling_threshold": "profiling",
            "rule": "rule",
            "anomaly_auc": "anomaly",
        }
        query = self.db.query(QualityCheckResult)
        if result_type:
            query = query.filter(QualityCheckResult.check_type.in_(type_map[result_type]))
        if unresolved_only:
            query = query.filter(
                QualityCheckResult.is_resolved.is_(False),
                QualityCheckResult.status == "fail",
            )
        if table_id:
            query = query.filter(QualityCheckResult.table_id == table_id)
        rows = (
            query.order_by(QualityCheckResult.processing_date_hour.desc())
            .limit(200)
            .all()
        )
        return [
            {
                "id": row.id,
                "result_type": reverse_type_map.get(row.check_type, row.check_type),
                "status": row.status,
                "severity_level": row.severity_level,
                "is_resolved": row.is_resolved,
                "processing_date_hour": row.processing_date_hour,
            }
            for row in rows
        ]
