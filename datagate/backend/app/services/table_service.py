from datetime import datetime
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import and_, func
from sqlalchemy.orm import Session, selectinload

from app.models import (
    AnomalyConfig,
    AnomalyResult,
    BatchTableMetadata,
    BatchTableProfiling,
    Connection,
    QualityCheckResult,
    Table,
)
from app.schemas.table_schema import TableCreate, TableUpdate


class TableService:
    def __init__(self, db: Session):
        self.db = db

    def _uuid_to_str(self, value: UUID | str) -> str:
        return str(value)

    def _get_connection_or_404(self, connection_id: UUID | str) -> Connection:
        connection = (
            self.db.query(Connection)
            .filter(Connection.id == self._uuid_to_str(connection_id))
            .first()
        )
        if connection is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Connection not found",
            )
        return connection

    def _validate_table_unique(
        self,
        connection_id: UUID | str,
        catalog_name: str,
        schema_name: str,
        table_name: str,
        exclude_id: str | None = None,
    ) -> None:
        query = self.db.query(Table).filter(
            and_(
                Table.connection_id == self._uuid_to_str(connection_id),
                Table.catalog_name == catalog_name,
                Table.schema_name == schema_name,
                Table.table_name == table_name,
            )
        )
        if exclude_id:
            query = query.filter(Table.id != exclude_id)
        if query.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Table already registered",
            )

    def get_latest_processing_hour(self, table_id: str) -> datetime | None:
        hours = [
            row[0]
            for row in (
                self.db.query(func.max(BatchTableMetadata.processing_date_hour))
                .filter(BatchTableMetadata.table_id == table_id)
                .union_all(
                    self.db.query(func.max(BatchTableProfiling.processing_date_hour)).filter(
                        BatchTableProfiling.table_id == table_id
                    )
                )
                .union_all(
                    self.db.query(func.max(AnomalyResult.processing_date_hour)).filter(
                        AnomalyResult.table_id == table_id
                    )
                )
                .union_all(
                    self.db.query(func.max(QualityCheckResult.processing_date_hour)).filter(
                        QualityCheckResult.table_id == table_id
                    )
                )
                .all()
            )
            if row[0]
        ]

        if not hours:
            return None
        return max(hours)

    def get_latest_processing_hours(self, table_ids: list[str]) -> dict[str, datetime]:
        if not table_ids:
            return {}

        latest_dates = {}
        for model in (
            BatchTableMetadata,
            BatchTableProfiling,
            AnomalyResult,
            QualityCheckResult,
        ):
            rows = (
                self.db.query(model.table_id, func.max(model.processing_date_hour))
                .filter(model.table_id.in_(table_ids))
                .group_by(model.table_id)
                .all()
            )
            for tid, dt in rows:
                if dt:
                    latest_dates[tid] = max(latest_dates.get(tid, dt), dt)

        return latest_dates

    def list_tables(
        self,
        connection_id: str | None = None,
        catalog_name: str | None = None,
        schema_name: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        query = (
            self.db.query(Table)
            .join(Connection)
            .options(selectinload(Table.connection))
        )

        query = query.filter(Connection.is_active.is_(True))

        if connection_id:
            query = query.filter(Table.connection_id == connection_id)
        if catalog_name:
            query = query.filter(Table.catalog_name == catalog_name)
        if schema_name:
            query = query.filter(Table.schema_name == schema_name)

        total = query.count()
        tables = (
            query.order_by(Table.schema_name.asc(), Table.table_name.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        # Batch fetch latest processing hours to avoid N+1 queries
        table_ids = [str(t.id) for t in tables]
        latest_hours = self.get_latest_processing_hours(table_ids)

        # Batch fetch anomaly configs
        model_configs = (
            self.db.query(AnomalyConfig.table_id)
            .filter(AnomalyConfig.table_id.in_(table_ids))
            .all()
        )
        anomaly_table_ids = {str(r[0]) for r in model_configs}

        for table in tables:
            tid = str(table.id)
            table.latest_processing_date_hour = latest_hours.get(tid)
            table.has_anomaly_config = tid in anomaly_table_ids

        return {"items": tables, "total": total, "page": page, "page_size": page_size}

    def get_table_by_id(self, table_id: str) -> Table | None:
        table = (
            self.db.query(Table)
            .options(selectinload(Table.connection))
            .filter(Table.id == table_id)
            .first()
        )
        if table:
            table.latest_processing_date_hour = self.get_latest_processing_hour(
                table_id
            )
            table.has_anomaly_config = (
                self.db.query(AnomalyConfig)
                .filter(AnomalyConfig.table_id == table_id)
                .first()
                is not None
            )
        return table

    def get_table_or_404(self, table_id: str) -> Table:
        table = self.get_table_by_id(table_id)
        if table is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Table not found",
            )
        return table

    def validate_table_accessible(self, table: Table) -> None:
        if not table.connection.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Connection is inactive",
            )

    def create_table(self, data: TableCreate, owner_id: str) -> Table:
        connection = self._get_connection_or_404(data.connection_id)
        self._validate_table_unique(
            connection_id=data.connection_id,
            catalog_name=data.catalog_name,
            schema_name=data.schema_name,
            table_name=data.table_name,
        )
        table = Table(
            connection_id=str(data.connection_id),
            catalog_name=data.catalog_name,
            schema_name=data.schema_name,
            table_name=data.table_name,
        )
        self.db.add(table)
        self.db.commit()
        self.db.refresh(table)
        return self.get_table_or_404(str(table.id))

    def update_table(self, table_id: str, data: TableUpdate) -> Table:
        table = self.get_table_or_404(table_id)
        update_data = data.model_dump(exclude_unset=True)
        new_connection_id = update_data.get("connection_id", table.connection_id)
        new_catalog_name = update_data.get("catalog_name", table.catalog_name)
        new_schema_name = update_data.get("schema_name", table.schema_name)
        new_table_name = update_data.get("table_name", table.table_name)

        if "connection_id" in update_data:
            connection = self._get_connection_or_404(new_connection_id)
            update_data["connection_id"] = str(new_connection_id)

        self._validate_table_unique(
            connection_id=new_connection_id,
            catalog_name=new_catalog_name,
            schema_name=new_schema_name,
            table_name=new_table_name,
            exclude_id=table_id,
        )

        for field, value in update_data.items():
            setattr(table, field, value)

        self.db.commit()
        self.db.refresh(table)
        return self.get_table_or_404(str(table.id))

    def delete_table(self, table_id: str) -> None:
        table = self.get_table_or_404(table_id)
        self.db.delete(table)
        self.db.commit()

    def list_columns(self, table_id: str) -> list[dict]:
        self.get_table_or_404(table_id)
        rows = (
            self.db.query(
                BatchTableProfiling.column_name,
                BatchTableProfiling.data_type,
            )
            .filter(
                BatchTableProfiling.table_id == table_id,
            )
            .order_by(
                BatchTableProfiling.processing_date_hour.desc(),
                BatchTableProfiling.column_name.asc(),
            )
            .all()
        )
        seen = set()
        columns = []
        for column_name, data_type in rows:
            if column_name in seen:
                continue
            seen.add(column_name)
            columns.append({"column_name": column_name, "data_type": data_type})
        return columns

    def list_processing_hours(self, table_id: str) -> list[dict]:
        self.get_table_or_404(table_id)
        hours = set()
        for model in (
            BatchTableMetadata,
            BatchTableProfiling,
            AnomalyResult,
            QualityCheckResult,
        ):
            rows = (
                self.db.query(model.processing_date_hour)
                .filter(model.table_id == table_id)
                .all()
            )
            hours.update(row[0] for row in rows if row[0])
        return [{"processing_date_hour": hour} for hour in sorted(hours, reverse=True)]
