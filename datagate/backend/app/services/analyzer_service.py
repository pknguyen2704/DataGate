from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models import Table, BatchTableMetadata


class AnalyzerService:
    def __init__(self, db: Session):
        self.db = db

    def get_table_or_404(self, table_id: str) -> Table:
        table = self.db.query(Table).filter(Table.id == table_id).first()
        if table is None:
            raise NotFoundError("Table not found")
        return table

    def get_table_metadata(
        self,
        table_id: str,
        limit: int = 20,
    ) -> dict:
        table = self.get_table_or_404(table_id)
        batches = (
            self.db.query(BatchTableMetadata)
            .filter(BatchTableMetadata.table_id == table_id)
            .order_by(
                BatchTableMetadata.last_updated_time.desc().nullslast(),
                BatchTableMetadata.collected_at.desc(),
            )
            .limit(limit)
            .all()
        )

        latest = batches[0] if batches else None
        panels = [
            {
                "key": "total_rows",
                "label": "Total rows",
                "value": latest.table_total_rows if latest else None,
                "unit": "rows",
            },
            {
                "key": "added_rows",
                "label": "Added rows",
                "value": latest.batch_added_rows if latest else None,
                "unit": "rows",
            },
            {
                "key": "total_files",
                "label": "Total files",
                "value": latest.table_total_files if latest else None,
                "unit": "files",
            },
            {
                "key": "size_bytes",
                "label": "Size",
                "value": latest.table_total_size_bytes if latest else None,
                "unit": "bytes",
            },
        ]

        return {
            "table": {
                "id": table.id,
                "full_name": f"{table.catalog_name}.{table.schema_name}.{table.table_name}",
            },
            "panels": panels,
            "batches": [
                {
                    "id": item.id,
                    "snapshot_id": item.snapshot_id,
                    "operation": item.operation,
                    "last_updated_time": item.last_updated_time,
                    "batch_added_rows": item.batch_added_rows,
                    "batch_added_files": item.batch_added_files,
                    "deleted_rows": item.deleted_rows,
                    "deleted_files": item.deleted_files,
                    "table_total_rows": item.table_total_rows,
                    "table_total_files": item.table_total_files,
                    "table_total_size_bytes": item.table_total_size_bytes,
                    "changed_partition_count": item.changed_partition_count,
                    "schema_id": item.schema_id,
                    "collected_at": item.collected_at,
                }
                for item in batches
            ],
        }

    def get_table_anomalies(
        self,
        table_id: str,
        limit: int = 20,
    ) -> list[dict]:
        self.get_table_or_404(table_id)
        rows = (
            self.db.query(AnomalyResult)
            .filter(AnomalyResult.table_id == table_id)
            .order_by(AnomalyResult.detected_at.desc(), AnomalyResult.target_date.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": row.id,
                "table_id": row.table_id,
                "date_column": row.date_column,
                "batch_date_hour": row.batch_date_hour,
                "target_date": row.target_date,
                "status": row.status,
                "auc": row.auc,
                "sample_today_count": row.sample_today_count,
                "sample_comparison_count": row.sample_comparison_count,
                "sample_total_count": row.sample_total_count,
                "anomaly_count": row.anomaly_count,
                "severity_counts": row.severity_counts or {},
                "root_causes": row.root_causes or [],
                "examples": row.examples or [],
                "message": row.message,
                "detected_at": row.detected_at,
            }
            for row in rows
        ]
