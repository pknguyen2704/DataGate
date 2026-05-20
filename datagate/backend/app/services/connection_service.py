import re
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.trino_client import TrinoClient
from app.models import Connection, Table
from app.schemas.connection_schema import (
    ConnectionCreate,
    ConnectionTestResult,
    ConnectionUpdate,
)


SYSTEM_SCHEMAS = {"information_schema", "pg_catalog", "sys", "system"}


class ConnectionService:
    def __init__(self, db: Session):
        self.db = db

    def _build_connection(self, data: ConnectionCreate, creator_id: str) -> Connection:
        return Connection(
            connection_name=data.connection_name,
            description=data.description,
            trino_host=data.trino_host,
            trino_port=data.trino_port,
            trino_user=data.trino_user,
            trino_password=data.trino_password,
            iceberg_rest_url=data.iceberg_rest_url,
            iceberg_catalog_name=data.iceberg_catalog_name,
            iceberg_warehouse=data.iceberg_warehouse,
            minio_endpoint_url=data.minio_endpoint_url,
            minio_access_key=data.minio_access_key,
            minio_secret_key=data.minio_secret_key,
            is_active=data.is_active,
            created_by=str(creator_id),
        )

    def _validate_name_unique(
        self, connection_name: str, exclude_id: str | None = None
    ) -> None:
        query = self.db.query(Connection).filter(
            Connection.connection_name == connection_name
        )
        if exclude_id:
            query = query.filter(Connection.id != exclude_id)
        if query.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Connection name already exists",
            )

    def _validate_connection(self, connection: Connection) -> None:
        client = TrinoClient(connection)
        try:
            client.test()
            client.list_schemas(connection.iceberg_catalog_name)
        except Exception as exc:
            # Clean up error message (remove HTML if present, truncate if too long)
            error_msg = str(exc)
            if "<html>" in error_msg.lower():
                # Try to extract message from trino HttpError format: error 405: b'<html>...'
                match = re.search(r"error (\d+):", error_msg)
                status_code = f" (Status {match.group(1)})" if match else ""
                error_msg = f"Server responded with an error{status_code}. This usually happens when the port is incorrect or pointing to a different service."

            # Truncate very long messages
            if len(error_msg) > 250:
                error_msg = error_msg[:247] + "..."

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Connection test failed: {error_msg}",
            ) from exc
        finally:
            client.close()

    def _has_connection_config_changed(self, update_data: dict) -> bool:
        fields = {
            "trino_host",
            "trino_port",
            "trino_user",
            "trino_password",
            "iceberg_rest_url",
            "iceberg_catalog_name",
            "iceberg_warehouse",
            "minio_endpoint_url",
            "minio_access_key",
            "minio_secret_key",
        }
        return any(field in update_data for field in fields)

    def list_connections(
        self, page: int = 1, page_size: int = 50, is_active: bool | None = None
    ) -> dict:
        from sqlalchemy.orm import selectinload

        query = self.db.query(Connection).options(
            selectinload(Connection.created_by_user),
            selectinload(Connection.last_modified_by_user),
        )
        if is_active is not None:
            query = query.filter(Connection.is_active == is_active)

        total = query.count()
        items = (
            query.order_by(Connection.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return {"items": items, "total": total, "page": page, "page_size": page_size}

    def get_connection_by_id(self, connection_id: str) -> Connection | None:
        from sqlalchemy.orm import selectinload

        return (
            self.db.query(Connection)
            .options(
                selectinload(Connection.created_by_user),
                selectinload(Connection.last_modified_by_user),
            )
            .filter(Connection.id == connection_id)
            .first()
        )

    def get_connection_or_404(self, connection_id: str) -> Connection:
        connection = self.get_connection_by_id(connection_id)
        if connection is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Connection not found",
            )
        return connection

    def create_connection(self, data: ConnectionCreate, creator_id: str) -> Connection:
        self._validate_name_unique(data.connection_name)
        connection = self._build_connection(data, creator_id)
        self._validate_connection(connection)
        self.db.add(connection)
        self.db.commit()
        self.db.refresh(connection)
        return connection

    def update_connection(
        self, connection_id: str, data: ConnectionUpdate, modifier_id: str | None = None
    ) -> Connection:
        connection = self.get_connection_or_404(connection_id)
        update_data = data.model_dump(exclude_unset=True)
        if "connection_name" in update_data:
            self._validate_name_unique(
                update_data["connection_name"], exclude_id=connection_id
            )
        for field, value in update_data.items():
            # Skip empty passwords/secrets to avoid overwriting with empty string
            if field in ["trino_password", "minio_secret_key"] and not value:
                continue
            setattr(connection, field, value)
        if modifier_id:
            connection.last_modified_by = modifier_id
        if self._has_connection_config_changed(update_data):
            try:
                self._validate_connection(connection)
            except HTTPException:
                self.db.rollback()
                raise
        self.db.commit()
        self.db.refresh(connection)
        return connection

    def activate_connection(self, connection_id: str) -> Connection:
        connection = self.get_connection_or_404(connection_id)
        connection.is_active = True
        self.db.commit()
        self.db.refresh(connection)
        return connection

    def deactivate_connection(self, connection_id: str) -> Connection:
        connection = self.get_connection_or_404(connection_id)
        connection.is_active = False
        self.db.commit()
        self.db.refresh(connection)
        return connection

    def delete_connection(self, connection_id: str) -> None:
        connection = self.get_connection_or_404(connection_id)
        self.db.delete(connection)
        self.db.commit()

    def test_connection(self, connection_id: str) -> ConnectionTestResult:
        connection = self.get_connection_or_404(connection_id)
        self._validate_connection(connection)
        return ConnectionTestResult(
            success=True,
            message=f"Connection '{connection.connection_name}' is reachable",
        )

    def list_catalogs(self, connection_id: str) -> list[str]:
        connection = self.get_connection_or_404(connection_id)
        return [connection.iceberg_catalog_name]

    def list_schemas(self, connection_id: str) -> list[str]:
        connection = self.get_connection_or_404(connection_id)
        client = TrinoClient(connection)
        try:
            schemas = client.list_schemas(connection.iceberg_catalog_name)
            return [
                schema for schema in schemas if schema.lower() not in SYSTEM_SCHEMAS
            ]
        finally:
            client.close()

    def list_tables(
        self, connection_id: str, schema: str, catalog: str | None = None
    ) -> list[str]:
        connection = self.get_connection_or_404(connection_id)
        target_catalog = catalog or connection.iceberg_catalog_name
        if target_catalog != connection.iceberg_catalog_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Table discovery only supports the catalog configured on the connection.",
            )
        client = TrinoClient(connection)
        try:
            return client.list_tables(target_catalog, schema)
        finally:
            client.close()

    def add_managed_table(
        self, connection_id: str, catalog: str, schema: str, table_name: str
    ) -> Table:
        # Check if already managed
        existing = (
            self.db.query(Table)
            .filter(
                Table.connection_id == connection_id,
                Table.catalog_name == catalog,
                Table.schema_name == schema,
                Table.table_name == table_name,
            )
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Table '{table_name}' is already registered under this connection.",
            )

        table = Table(
            connection_id=connection_id,
            catalog_name=catalog,
            schema_name=schema,
            table_name=table_name,
        )
        self.db.add(table)
        self.db.commit()
        self.db.refresh(table)
        return table

    def remove_managed_table(self, table_id: str) -> None:
        table = self.db.query(Table).filter(Table.id == table_id).first()
        if not table:
            raise HTTPException(status_code=404, detail="Managed table not found")

        self.db.delete(table)
        self.db.commit()
