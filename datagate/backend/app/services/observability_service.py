from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from app.models import (
    AnomalyResult,
    QualityCheckResult,
    QualityMetricObservation,
    Table,
)


class ObservabilityService:
    def __init__(self, db: Session):
        self.db = db

    def processing_hours(self) -> list[datetime]:
        hours = set()
        for model in (QualityMetricObservation, AnomalyResult, QualityCheckResult):
            rows = self.db.query(model.processing_date_hour).distinct().all()
            hours.update(row[0] for row in rows if row[0])
        return sorted(hours, reverse=True)

    def get_table_processing_hours(self, table_id: str) -> list[datetime]:
        hours = set()
        for model in (QualityMetricObservation, AnomalyResult, QualityCheckResult):
            rows = (
                self.db.query(model.processing_date_hour)
                .filter(model.table_id == table_id)
                .distinct()
                .all()
            )
            hours.update(row[0] for row in rows if row[0])
        return sorted(hours, reverse=True)

    def get_default_time_range(self, table_id: str) -> dict:
        hours = self.get_table_processing_hours(table_id)
        if not hours:
            return {"default_from": None, "default_to": None}

        latest = hours[0]
        # Default range: From is -2 days before latest, To is latest
        default_from = latest - timedelta(days=2)
        return {"default_from": default_from, "default_to": latest}

    def get_observability_dashboard_url(
        self,
        table_id: str,
        from_time: datetime | None = None,
        to_time: datetime | None = None,
    ) -> str:
        from app.core.config import config

        table = self.db.query(Table).filter(Table.id == table_id).first()
        if not table:
            return ""

        base_url = config.grafana_url
        uid = config.grafana_dashboard_uid
        slug = config.grafana_dashboard_slug

        # Build URL with precise Grafana parameters
        url = f"{base_url}/d/{uid}/{slug}?orgId=1&kiosk=true"
        url += f"&var-catalog={table.catalog_name}"
        url += f"&var-schema={table.schema_name}"
        url += f"&var-table={table.table_name}"
        url += f"&var-table_name={table.catalog_name}.{table.schema_name}.{table.table_name}"
        url += f"&var-table_id={table.id}"

        # Vietnam timezone (UTC+7)
        vn_tz = timezone(timedelta(hours=7))

        if from_time:
            # If naive, assume it's local time and convert to UTC epoch
            if from_time.tzinfo is None:
                from_time = from_time.replace(tzinfo=vn_tz)
            url += f"&from={int(from_time.timestamp() * 1000)}"
        if to_time:
            if to_time.tzinfo is None:
                to_time = to_time.replace(tzinfo=vn_tz)
            url += f"&to={int(to_time.timestamp() * 1000)}"

        url += "&timezone=browser&refresh=1m&theme=light"

        return url

    def managed_tree(self) -> list[dict]:
        from app.models import Connection

        rows = (
            self.db.query(Table)
            .join(Connection)
            .filter(Connection.is_active.is_(True))
            .order_by(Table.schema_name, Table.table_name)
            .all()
        )
        grouped = {}
        for table in rows:
            grouped.setdefault(table.schema_name, []).append(
                {"table_id": table.id, "table_name": table.table_name}
            )
        return [
            {"schema_name": schema, "tables": tables}
            for schema, tables in grouped.items()
        ]

    def observability_variables(self) -> dict:
        from app.models import Connection

        rows = (
            self.db.query(Table)
            .join(Connection)
            .filter(Connection.is_active.is_(True))
            .all()
        )
        connections = (
            self.db.query(Connection).filter(Connection.is_active.is_(True)).all()
        )
        return {
            "catalogs": sorted({row.catalog_name for row in rows if row.catalog_name}),
            "schemas": sorted({row.schema_name for row in rows if row.schema_name}),
            "tables": sorted({row.table_name for row in rows if row.table_name}),
            "connections": [
                {"id": str(c.id), "name": c.connection_name} for c in connections
            ],
            "processing_date_hours": self.processing_hours(),
        }
