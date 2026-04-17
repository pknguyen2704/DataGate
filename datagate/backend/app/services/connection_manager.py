from urllib.parse import urlparse

from sqlalchemy import create_engine, inspect, text
from trino.dbapi import connect

from app.schemas.service import ServiceCreate


DEFAULT_TRINO_USER = "admin"
DEFAULT_TRINO_PORT = 8080
DEFAULT_TRINO_CATALOG = "tpch"
DEFAULT_SAMPLE_LIMIT = 50
MAX_SAMPLE_LIMIT = 500


def _parse_trino_config(url: str) -> dict[str, str | int]:
    parsed = urlparse(url)
    path_parts = [part for part in parsed.path.strip("/").split("/") if part]

    return {
        "user": parsed.username or DEFAULT_TRINO_USER,
        "host": parsed.hostname or "localhost",
        "port": parsed.port or DEFAULT_TRINO_PORT,
        "catalog": path_parts[0] if path_parts else DEFAULT_TRINO_CATALOG,
    }


def _split_table_name(table_name: str, default_schema: str | None = None) -> tuple[str | None, str]:
    if "." in table_name:
        return table_name.split(".", 1)
    return default_schema, table_name


def _quote_identifier(identifier: str) -> str:
    return identifier.replace('"', '""')


class ConnectionManager:
    @staticmethod
    def get_connection(service_type: str, url: str):
        if service_type == "trino":
            trino_config = _parse_trino_config(url)
            return connect(
                host=trino_config["host"],
                port=trino_config["port"],
                user=trino_config["user"],
                catalog=trino_config["catalog"],
            )

        engine = create_engine(url)
        return engine.raw_connection()

    @staticmethod
    def test_connection(service: ServiceCreate) -> dict[str, str]:
        try:
            if service.service_type == "trino":
                return ConnectionManager._test_trino(service.connection_url)
            return ConnectionManager._test_sqlalchemy(service.connection_url)
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    @staticmethod
    def _test_sqlalchemy(url: str) -> dict[str, str]:
        engine = create_engine(url)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "success", "message": "Connection successful"}

    @staticmethod
    def _test_trino(url: str) -> dict[str, str]:
        trino_config = _parse_trino_config(url)
        connection = connect(
            host=trino_config["host"],
            port=trino_config["port"],
            user=trino_config["user"],
            catalog=trino_config["catalog"],
        )
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        return {"status": "success", "message": "Trino connection successful"}

    @staticmethod
    def get_schemas(service_type: str, url: str) -> list[str]:
        try:
            if service_type == "trino":
                return ConnectionManager._get_trino_schemas(url)
            return ConnectionManager._get_sqlalchemy_schemas(url)
        except Exception:
            return []

    @staticmethod
    def _get_sqlalchemy_schemas(url: str) -> list[str]:
        engine = create_engine(url)
        query = text(
            """
            SELECT schema_name
            FROM information_schema.schemata
            WHERE schema_name NOT IN ('information_schema', 'pg_catalog')
            """
        )
        with engine.connect() as connection:
            result = connection.execute(query)
            return [row[0] for row in result]

    @staticmethod
    def _get_trino_schemas(url: str) -> list[str]:
        trino_config = _parse_trino_config(url)
        connection = connect(
            host=trino_config["host"],
            port=trino_config["port"],
            user=trino_config["user"],
            catalog=trino_config["catalog"],
        )
        cursor = connection.cursor()
        cursor.execute("SHOW SCHEMAS")
        return [row[0] for row in cursor.fetchall() if row[0] not in ("information_schema", "staged")]

    @staticmethod
    def get_tables(service_type: str, url: str, schema: str | None = None) -> list[str]:
        try:
            if service_type == "trino":
                return ConnectionManager._get_trino_tables(url, schema)
            return ConnectionManager._get_sqlalchemy_tables(url, schema)
        except Exception:
            return []

    @staticmethod
    def _get_sqlalchemy_tables(url: str, schema: str | None) -> list[str]:
        engine = create_engine(url)
        with engine.connect() as connection:
            if schema:
                result = connection.execute(
                    text("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = :schema"),
                    {"schema": schema},
                )
                return [row[0] for row in result]

            result = connection.execute(
                text(
                    """
                    SELECT schemaname, tablename
                    FROM pg_catalog.pg_tables
                    WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
                    """
                )
            )
            return [f"{row[0]}.{row[1]}" for row in result]

    @staticmethod
    def _get_trino_tables(url: str, schema: str | None) -> list[str]:
        trino_config = _parse_trino_config(url)
        connection = connect(
            host=trino_config["host"],
            port=trino_config["port"],
            user=trino_config["user"],
            catalog=trino_config["catalog"],
        )
        cursor = connection.cursor()

        if schema:
            cursor.execute(f'SHOW TABLES IN "{_quote_identifier(schema)}"')
            return [row[0] for row in cursor.fetchall()]

        cursor.execute(
            """
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_catalog = ?
            """,
            (trino_config["catalog"],),
        )
        return [f"{row[0]}.{row[1]}" for row in cursor.fetchall() if row[0] not in ("information_schema", "staged")]

    @staticmethod
    def get_sample_data(service_type: str, url: str, table_name: str, limit: int = DEFAULT_SAMPLE_LIMIT) -> dict:
        safe_limit = max(1, min(limit, MAX_SAMPLE_LIMIT))
        try:
            if service_type == "trino":
                return ConnectionManager._get_trino_sample_data(url, table_name, safe_limit)
            return ConnectionManager._get_sqlalchemy_sample_data(url, table_name, safe_limit)
        except Exception:
            return {"columns": [], "rows": [], "row_count": 0}

    @staticmethod
    def get_table_metadata(service_type: str, url: str, table_name: str) -> dict:
        try:
            if service_type == "trino":
                return ConnectionManager._get_trino_table_metadata(url, table_name)
            return ConnectionManager._get_sqlalchemy_table_metadata(service_type, url, table_name)
        except Exception:
            return {"table_description": None, "columns": []}

    @staticmethod
    def _get_sqlalchemy_sample_data(url: str, table_name: str, limit: int) -> dict:
        engine = create_engine(url)
        schema_name, physical_table_name = _split_table_name(table_name)

        if not schema_name:
            return {"columns": [], "rows": [], "row_count": 0}

        query = text(
            f'SELECT * FROM "{_quote_identifier(schema_name)}"."{_quote_identifier(physical_table_name)}" LIMIT {limit}'
        )
        with engine.connect() as connection:
            result = connection.execute(query)
            rows = result.fetchall()
            columns = list(result.keys())

        return {
            "columns": columns,
            "rows": [list(row) for row in rows],
            "row_count": len(rows),
        }

    @staticmethod
    def _get_trino_sample_data(url: str, table_name: str, limit: int) -> dict:
        trino_config = _parse_trino_config(url)
        schema_name, physical_table_name = _split_table_name(table_name)

        if not schema_name:
            return {"columns": [], "rows": [], "row_count": 0}

        connection = connect(
            host=trino_config["host"],
            port=trino_config["port"],
            user=trino_config["user"],
            catalog=trino_config["catalog"],
        )
        cursor = connection.cursor()
        cursor.execute(
            f'SELECT * FROM "{_quote_identifier(schema_name)}"."{_quote_identifier(physical_table_name)}" LIMIT {limit}'
        )
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description] if cursor.description else []

        return {
            "columns": columns,
            "rows": [list(row) for row in rows],
            "row_count": len(rows),
        }

    @staticmethod
    def _get_sqlalchemy_table_metadata(service_type: str, url: str, table_name: str) -> dict:
        engine = create_engine(url)
        schema_name, physical_table_name = _split_table_name(table_name, "public")

        with engine.connect() as connection:
            if service_type == "postgres":
                table_description = connection.execute(
                    text(
                        """
                        SELECT obj_description(c.oid)
                        FROM pg_class c
                        JOIN pg_namespace n ON n.oid = c.relnamespace
                        WHERE c.relname = :table_name
                          AND n.nspname = :schema_name
                        """
                    ),
                    {"table_name": physical_table_name, "schema_name": schema_name},
                ).scalar()

                column_rows = connection.execute(
                    text(
                        """
                        SELECT
                            cols.column_name,
                            cols.data_type,
                            pgd.description
                        FROM information_schema.columns cols
                        LEFT JOIN pg_catalog.pg_statio_all_tables st
                            ON st.relname = cols.table_name
                        LEFT JOIN pg_catalog.pg_description pgd
                            ON pgd.objoid = st.relid
                           AND pgd.objsubid = cols.ordinal_position
                        WHERE cols.table_name = :table_name
                          AND cols.table_schema = :schema_name
                        ORDER BY cols.ordinal_position
                        """
                    ),
                    {"table_name": physical_table_name, "schema_name": schema_name},
                ).mappings().all()

                return {
                    "table_description": table_description,
                    "columns": [
                        {
                            "column_name": row["column_name"],
                            "data_type": row["data_type"],
                            "description": row["description"],
                        }
                        for row in column_rows
                    ],
                }

        inspector = inspect(engine)
        columns = inspector.get_columns(physical_table_name, schema=schema_name)
        return {
            "table_description": None,
            "columns": [
                {
                    "column_name": column.get("name"),
                    "data_type": str(column.get("type") or ""),
                    "description": column.get("comment"),
                }
                for column in columns
            ],
        }

    @staticmethod
    def _get_trino_table_metadata(url: str, table_name: str) -> dict:
        trino_config = _parse_trino_config(url)
        schema_name, physical_table_name = _split_table_name(table_name, "default")
        connection = connect(
            host=trino_config["host"],
            port=trino_config["port"],
            user=trino_config["user"],
            catalog=trino_config["catalog"],
        )
        cursor = connection.cursor()
        cursor.execute(f'SHOW COLUMNS FROM "{_quote_identifier(schema_name)}"."{_quote_identifier(physical_table_name)}"')

        return {
            "table_description": None,
            "columns": [
                {
                    "column_name": row[0],
                    "data_type": row[1],
                    "description": row[2] if len(row) > 2 else None,
                }
                for row in cursor.fetchall()
            ],
        }
