from typing import Any
from urllib.parse import urlparse

from trino.dbapi import connect

from app.models.connection import Connection


def quote_identifier(identifier: str) -> str:
    return f'"{identifier.replace(chr(34), chr(34) + chr(34))}"'


def quote_literal(value: str) -> str:
    return f"'{value.replace(chr(39), chr(39) + chr(39))}'"


class TrinoClient:
    def __init__(self, connection: Connection):
        self.connection_config = connection
        host, port, http_scheme = self._normalize_host(
            connection.trino_host,
            connection.trino_port,
        )
        self.connection = connect(
            host=host,
            port=port,
            user=connection.trino_user,
            catalog=connection.iceberg_catalog_name,
            http_scheme=http_scheme,
        )

    def _normalize_host(self, host: str, port: int) -> tuple[str, int, str]:
        raw_host = host.strip()
        if "://" not in raw_host:
            return raw_host, port, "http"

        parsed = urlparse(raw_host)
        return (
            parsed.hostname or raw_host,
            parsed.port or port,
            parsed.scheme or "http",
        )

    def close(self) -> None:
        self.connection.close()

    def test(self) -> None:
        cursor = self.connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()

    def list_catalogs(self) -> list[str]:
        cursor = self.connection.cursor()
        cursor.execute("SHOW CATALOGS")
        return [row[0] for row in cursor.fetchall()]

    def list_schemas(self, catalog: str) -> list[str]:
        cursor = self.connection.cursor()
        cursor.execute(f"SHOW SCHEMAS FROM {quote_identifier(catalog)}")
        return [row[0] for row in cursor.fetchall()]

    def list_tables(self, catalog: str, schema: str) -> list[str]:
        cursor = self.connection.cursor()
        cursor.execute(f"SHOW TABLES FROM {quote_identifier(catalog)}.{quote_identifier(schema)}")
        return [row[0] for row in cursor.fetchall()]

    def get_columns(self, catalog: str, schema: str, table: str) -> list[dict[str, Any]]:
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT column_name, data_type, is_nullable "
            f"FROM {quote_identifier(catalog)}.information_schema.columns "
            f"WHERE table_catalog = {quote_literal(catalog)} "
            f"AND table_schema = {quote_literal(schema)} "
            f"AND table_name = {quote_literal(table)} "
            "ORDER BY ordinal_position"
        )
        return [
            {
                "column_name": row[0],
                "data_type": row[1],
                "is_nullable": row[2],
            }
            for row in cursor.fetchall()
        ]

    def get_sample_data(self, catalog: str, schema: str, table: str, limit: int = 50) -> dict[str, Any]:
        safe_limit = max(1, min(limit, 1000))
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT * FROM "
            f"{quote_identifier(catalog)}.{quote_identifier(schema)}.{quote_identifier(table)} "
            f"LIMIT {safe_limit}"
        )
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description] if cursor.description else []
        return {
            "columns": columns,
            "rows": [list(row) for row in rows],
            "row_count": len(rows),
        }
