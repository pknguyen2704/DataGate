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
                self.connection.trino_user, self.connection.trino_password
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
        cur = conn.cursor()
        try:
            cur.execute(sql)
            cols = [col[0] for col in cur.description]
            rows = cur.fetchall()
            results = [dict(zip(cols, row)) for row in rows]
            return results
        except Exception as e:
            raise Exception(f"Error executing query: {str(e)}")
        finally:
            cur.close()

    def test(self):
        self.execute("SELECT 1 AS ok")

    def list_schemas(self, catalog: str | None = None) -> list[str]:
        target_catalog = catalog or self.connection.iceberg_catalog_name
        rows = self.execute(f"SHOW SCHEMAS FROM {target_catalog}")
        schemas = [list(row.values())[0] for row in rows]
        return schemas

    def list_tables(
        self, catalog: str | None = None, schema: str = "default"
    ) -> list[str]:
        target_catalog = catalog or self.connection.iceberg_catalog_name
        rows = self.execute(f"SHOW TABLES FROM {target_catalog}.{schema}")
        tables = [list(row.values())[0] for row in rows]
        return tables

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
