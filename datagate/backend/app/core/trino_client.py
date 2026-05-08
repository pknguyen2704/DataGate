from typing import Any

from trino.dbapi import connect
from trino.auth import BasicAuthentication

from app.models import Connection


class TrinoClient:
    def __init__(self, connection: Connection):
        self.connection = connection
        self.conn = None

    def _connect(self):
        if self.conn:
            return self.conn

        auth = None
        if self.connection.trino_password:
            auth = BasicAuthentication(
                self.connection.trino_user,
                self.connection.trino_password,
            )

        self.conn = connect(
            host=self.connection.trino_host,
            port=self.connection.trino_port,
            user=self.connection.trino_user,
            catalog=self.connection.iceberg_catalog_name,
            http_scheme="http",
            auth=auth,
        )
        return self.conn

    def execute(self, sql: str) -> list[dict[str, Any]]:
        conn = self._connect()
        cursor = conn.cursor()

        try:
            cursor.execute(sql)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        finally:
            cursor.close()

    def test(self) -> None:
        self.execute("SELECT 1 AS ok")

    def list_schemas(self, catalog: str) -> list[str]:
        rows = self.execute(f"SHOW SCHEMAS FROM {catalog}")
        return [list(row.values())[0] for row in rows]

    def list_tables(self, catalog: str, schema: str) -> list[str]:
        rows = self.execute(f"SHOW TABLES FROM {catalog}.{schema}")
        return [list(row.values())[0] for row in rows]

    def close(self) -> None:
        if self.conn:
            self.conn.close()
            self.conn = None