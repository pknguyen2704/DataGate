from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.trino_client import TrinoClient
from app.models import Connection
from app.models.table import Table
from app.schemas.connection import ConnectionCreate, ConnectionUpdate


class ConnectionService:
    def __init__(self, db: Session):
        self.db = db

    def _build_connection(self, data: ConnectionCreate, creator_id: str) -> Connection:
        return Connection(
            name=data.name,
            description=data.description,
            trino_host=data.trino_host,
            trino_port=data.trino_port,
            trino_user=data.trino_user,
            trino_password=data.trino_password,
            iceberg_rest_url=data.iceberg_rest_url,
            iceberg_catalog_name=data.iceberg_catalog_name,
            minio_endpoint_url=data.minio_endpoint_url,
            minio_access_key=data.minio_access_key,
            minio_secret_key=data.minio_secret_key,
            minio_region=data.minio_region,
            created_by=creator_id,
        )

    def _validate_connection(self, connection: Connection) -> None:
        client = TrinoClient(connection)
        try:
            client.test()
            client.list_schemas(connection.iceberg_catalog_name)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Connection test failed: {exc}",
            ) from exc
        finally:
            client.close()

    def list_connections(self) -> list[Connection]:
        return (
            self.db.query(Connection)
            .order_by(Connection.created_at.desc())
            .all()
        )

    def get_connection_by_id(self, connection_id: str) -> Connection | None:
        return (
            self.db.query(Connection)
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

    def create_connection(
        self,
        data: ConnectionCreate,
        creator_id: str,
    ) -> Connection:
        existing_connection = (
            self.db.query(Connection)
            .filter(Connection.name == data.name)
            .first()
        )

        if existing_connection:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Connection name already exists",
            )

        connection = self._build_connection(data, creator_id)
        self._validate_connection(connection)

        self.db.add(connection)
        self.db.commit()
        self.db.refresh(connection)

        return connection

    def update_connection(
        self,
        connection_id: str,
        data: ConnectionUpdate,
    ) -> Connection:
        connection = self.get_connection_or_404(connection_id)

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(connection, field, value)

        self.db.commit()
        self.db.refresh(connection)

        return connection

    def delete_connection(self, connection_id: str) -> None:
        connection = self.get_connection_or_404(connection_id)

        table_count = (
            self.db.query(func.count(Table.id))
            .filter(Table.connection_id == connection_id)
            .scalar()
        )

        if table_count and table_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete connection used by registered tables. Deactivate it instead.",
            )

        self.db.delete(connection)
        self.db.commit()

    def deactivate_connection(self, connection_id: str) -> Connection:
        connection = self.get_connection_or_404(connection_id)

        connection.is_active = False

        self.db.commit()
        self.db.refresh(connection)

        return connection
