from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, BadRequestError
from app.models.user_table_access import UserTableAccess
from app.models.connection import Connection
from app.models.table import Table
from app.models.table_batch_metadata import BatchTableMetadata
from app.schemas.table import TableCreate, TableOut, TableUpdate, TableOverviewOut


class TableService:
    def __init__(self, db: Session):
        self.db = db

    def list_tables(self, connection_id: str | None = None) -> list[Table]:
        query = self.db.query(Table)

        if connection_id:
            query = query.filter(Table.connection_id == connection_id)

        return query.order_by(Table.updated_at.desc()).all()

    def get_table_by_id(self, table_id: str) -> Table | None:
        return (
            self.db.query(Table)
            .filter(Table.id == table_id)
            .first()
        )

    def get_table_or_404(self, table_id: str) -> Table:
        table = self.get_table_by_id(table_id)

        if table is None:
            raise NotFoundError("Table not found")

        return table

    def create_table(
        self,
        data: TableCreate,
        owner_id: str,
    ) -> Table:
        connection = (
            self.db.query(Connection)
            .filter(Connection.id == data.connection_id)
            .first()
        )

        if connection is None:
            raise NotFoundError("Connection not found")

        existing_table = (
            self.db.query(Table)
            .filter(
                Table.connection_id == data.connection_id,
                Table.catalog_name == data.catalog_name,
                Table.schema_name == data.schema_name,
                Table.table_name == data.table_name,
            )
            .first()
        )

        if existing_table:
            raise BadRequestError("Table already registered")

        table = Table(
            connection_id=data.connection_id,
            catalog_name=data.catalog_name,
            schema_name=data.schema_name,
            table_name=data.table_name,
            owner_user_id=owner_id,
        )

        self.db.add(table)
        self.db.commit()
        self.db.refresh(table)

        return table

    def update_table(
        self,
        table_id: str,
        data: TableUpdate,
    ) -> Table:
        table = self.get_table_or_404(table_id)

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(table, field, value)

        self.db.commit()
        self.db.refresh(table)

        return table

    def delete_table(self, table_id: str) -> None:
        table = self.get_table_or_404(table_id)

        self.db.delete(table)
        self.db.commit()

    def deactivate_table(self, table_id: str) -> Table:
        table = self.get_table_or_404(table_id)

        table.is_active = False

        self.db.commit()
        self.db.refresh(table)

        return table

    def grant_table_access(
        self,
        table_id: str,
        user_id: str,
        granted_by: str | None = None,
    ) -> UserTableAccess:
        table = self.get_table_or_404(table_id)

        existing_access = (
            self.db.query(UserTableAccess)
            .filter(
                UserTableAccess.table_id == table.id,
                UserTableAccess.user_id == user_id,
            )
            .first()
        )

        if existing_access:
            return existing_access

        access = UserTableAccess(
            table_id=table.id,
            user_id=user_id,
            granted_by=granted_by,
        )

        self.db.add(access)
        self.db.commit()
        self.db.refresh(access)

        return access

    def revoke_table_access(
        self,
        table_id: str,
        user_id: str,
    ) -> None:
        access = (
            self.db.query(UserTableAccess)
            .filter(
                UserTableAccess.table_id == table_id,
                UserTableAccess.user_id == user_id,
            )
            .first()
        )

        if access is None:
            raise NotFoundError("Access record not found")

        self.db.delete(access)
        self.db.commit()

    def user_can_view_table(
        self,
        table_id: str,
        user_id: str,
    ) -> bool:
        access = (
            self.db.query(UserTableAccess)
            .filter(
                UserTableAccess.table_id == table_id,
                UserTableAccess.user_id == user_id,
            )
            .first()
        )

        return access is not None

    def enrich_table(
        self,
        table: Table,
        connection_name: str | None = None,
    ) -> TableOut:
        latest_metadata = (
            self.db.query(BatchTableMetadata)
            .filter(BatchTableMetadata.table_id == table.id)
            .order_by(BatchTableMetadata.last_updated_time.desc())
            .first()
        )

        return TableOut(
            id=table.id,
            connection_id=table.connection_id,
            connection_name=connection_name,
            catalog_name=table.catalog_name,
            schema_name=table.schema_name,
            table_name=table.table_name,
            is_active=table.is_active,
            owner_user_id=table.owner_user_id,
            created_at=table.created_at,
            updated_at=table.updated_at,
            latest_date_hour=latest_metadata.last_updated_time if latest_metadata else None,
            latest_record_count=latest_metadata.batch_added_rows if latest_metadata else None,
        )

    def get_table_overview(self, table_id: str) -> TableOverviewOut:
        table = self.get_table_or_404(table_id)

        latest_metadata = (
            self.db.query(BatchTableMetadata)
            .filter(BatchTableMetadata.table_id == table.id)
            .order_by(BatchTableMetadata.last_updated_time.desc())
            .first()
        )

        connection_name = table.connection.name if table.connection else None
        full_name = f"{table.catalog_name}.{table.schema_name}.{table.table_name}"

        return TableOverviewOut(
            id=table.id,
            connection_id=table.connection_id,
            connection_name=connection_name,
            catalog_name=table.catalog_name,
            schema_name=table.schema_name,
            table_name=table.table_name,
            full_name=full_name,
            owner_user_id=table.owner_user_id,
            is_active=table.is_active,
            latest_date_hour=latest_metadata.last_updated_time if latest_metadata else None,
            latest_record_count=latest_metadata.batch_added_rows if latest_metadata else None,
            latest_file_count=latest_metadata.batch_added_files if latest_metadata else None,
            latest_size_bytes=latest_metadata.table_total_size_bytes if latest_metadata else None,
        )
