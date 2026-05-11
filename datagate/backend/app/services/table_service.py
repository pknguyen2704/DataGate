from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import and_
from sqlalchemy.orm import Session, selectinload

from app.models import BatchTableMetadata, BatchTableProfiling, Connection, LightGBMAUC, RuleVerify, Table
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

    def _validate_connection_active(self, connection: Connection) -> None:
        if not connection.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot register table with inactive connection",
            )

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

    def list_tables(
        self,
        connection_id: str | None = None,
        is_active: bool | None = None,
    ) -> list[Table]:
        query = self.db.query(Table).options(selectinload(Table.connection))
        if connection_id:
            query = query.filter(Table.connection_id == connection_id)
        if is_active is not None:
            query = query.filter(Table.is_active == is_active)
        return query.order_by(Table.updated_at.desc()).all()

    def get_table_by_id(self, table_id: str) -> Table | None:
        return (
            self.db.query(Table)
            .options(selectinload(Table.connection))
            .filter(Table.id == table_id)
            .first()
        )

    def get_table_or_404(self, table_id: str) -> Table:
        table = self.get_table_by_id(table_id)
        if table is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Table not found",
            )
        return table

    def create_table(self, data: TableCreate, owner_id: str) -> Table:
        connection = self._get_connection_or_404(data.connection_id)
        self._validate_connection_active(connection)
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
            is_active=data.is_active,
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
            self._validate_connection_active(connection)
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

    def activate_table(self, table_id: str) -> Table:
        table = self.get_table_or_404(table_id)
        table.is_active = True
        self.db.commit()
        self.db.refresh(table)
        return self.get_table_or_404(str(table.id))

    def deactivate_table(self, table_id: str) -> Table:
        table = self.get_table_or_404(table_id)
        table.is_active = False
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
            self.db.query(BatchTableProfiling.column_name, BatchTableProfiling.data_type)
            .filter(BatchTableProfiling.table_id == table_id)
            .order_by(BatchTableProfiling.processing_date_hour.desc(), BatchTableProfiling.column_name.asc())
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
        for model in (BatchTableMetadata, BatchTableProfiling, LightGBMAUC):
            rows = self.db.query(model.processing_date_hour).filter(model.table_id == table_id).all()
            hours.update(row[0] for row in rows if row[0])
        rule_rows = (
            self.db.query(RuleVerify.processing_date_hour)
            .join(RuleVerify.rule)
            .filter(RuleVerify.rule.has(table_id=table_id))
            .all()
        )
        hours.update(row[0] for row in rule_rows if row[0])
        return [{"processing_date_hour": hour} for hour in sorted(hours, reverse=True)]
