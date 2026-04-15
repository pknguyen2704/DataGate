from sqlalchemy import create_engine, text
from sqlalchemy import inspect
from trino.dbapi import connect
from urllib.parse import urlparse
from app.schemas.service import ServiceCreate

class ConnectionManager:
    @staticmethod
    def get_connection(service_type: str, url: str):
        if service_type == "trino":
            parsed = urlparse(url)
            user = parsed.username or "admin"
            host = parsed.hostname
            port = parsed.port or 8080
            path_parts = parsed.path.strip("/").split("/")
            catalog = path_parts[0] if len(path_parts) > 0 else "tpch"
            return connect(host=host, port=port, user=user, catalog=catalog)
        else:
            engine = create_engine(url)
            return engine.raw_connection()

    @staticmethod
    def test_connection(service: ServiceCreate):
        try:
            if service.service_type == "trino":
                return ConnectionManager._test_trino(service.connection_url)
            else:
                return ConnectionManager._test_sqlalchemy(service.connection_url)
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @staticmethod
    def _test_sqlalchemy(url: str):
        engine = create_engine(url)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "success", "message": "Connection successful"}

    @staticmethod
    def _test_trino(url: str):
        parsed = urlparse(url)
        user = parsed.username or "admin"
        host = parsed.hostname
        port = parsed.port or 8080
        path_parts = parsed.path.strip("/").split("/")
        catalog = path_parts[0] if len(path_parts) > 0 else "tpch"

        conn = connect(host=host, port=port, user=user, catalog=catalog)
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.fetchone()
        return {"status": "success", "message": "Trino connection successful"}

    @staticmethod
    def get_schemas(service_type: str, url: str):
        try:
            if service_type == "trino":
                return ConnectionManager._get_trino_schemas(url)
            else:
                return ConnectionManager._get_sqlalchemy_schemas(url)
        except Exception as e:
            return []

    @staticmethod
    def _get_sqlalchemy_schemas(url: str):
        engine = create_engine(url)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT schema_name FROM information_schema.schemata WHERE schema_name NOT IN ('information_schema', 'pg_catalog')"))
            return [row[0] for row in result]

    @staticmethod
    def _get_trino_schemas(url: str):
        parsed = urlparse(url)
        user = parsed.username or "admin"
        host = parsed.hostname
        port = parsed.port or 8080
        path_parts = parsed.path.strip("/").split("/")
        catalog = path_parts[0] if len(path_parts) > 0 else "tpch"

        conn = connect(host=host, port=port, user=user, catalog=catalog)
        cur = conn.cursor()
        cur.execute("SHOW SCHEMAS")
        return [row[0] for row in cur.fetchall() if row[0] not in ('information_schema', 'staged')]

    @staticmethod
    def get_tables(service_type: str, url: str, schema: str = None):
        try:
            if service_type == "trino":
                return ConnectionManager._get_trino_tables(url, schema)
            else:
                return ConnectionManager._get_sqlalchemy_tables(url, schema)
        except Exception as e:
            return []

    @staticmethod
    def _get_sqlalchemy_tables(url: str, schema: str):
        engine = create_engine(url)
        with engine.connect() as connection:
            if schema:
                query = f"SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = '{schema}'"
                result = connection.execute(text(query))
                return [row[0] for row in result]
            else:
                query = "SELECT schemaname, tablename FROM pg_catalog.pg_tables WHERE schemaname NOT IN ('information_schema', 'pg_catalog')"
                result = connection.execute(text(query))
                return [f"{row[0]}.{row[1]}" for row in result]

    @staticmethod
    def _get_trino_tables(url: str, schema: str):
        parsed = urlparse(url)
        user = parsed.username or "admin"
        host = parsed.hostname
        port = parsed.port or 8080
        path_parts = parsed.path.strip("/").split("/")
        catalog = path_parts[0] if len(path_parts) > 0 else "tpch"

        conn = connect(host=host, port=port, user=user, catalog=catalog)
        cur = conn.cursor()
        if schema:
            cur.execute(f"SHOW TABLES IN {schema}")
            return [row[0] for row in cur.fetchall()]
        else:
            cur.execute(f"SELECT table_schema, table_name FROM information_schema.tables WHERE table_catalog = '{catalog}'")
            return [f"{row[0]}.{row[1]}" for row in cur.fetchall() if row[0] not in ('information_schema', 'staged')]

    @staticmethod
    def get_sample_data(service_type: str, url: str, table_name: str, limit: int = 50):
        safe_limit = max(1, min(limit, 500))
        try:
            if service_type == "trino":
                return ConnectionManager._get_trino_sample_data(url, table_name, safe_limit)
            return ConnectionManager._get_sqlalchemy_sample_data(url, table_name, safe_limit)
        except Exception:
            return {"columns": [], "rows": [], "row_count": 0}

    @staticmethod
    def get_table_metadata(service_type: str, url: str, table_name: str):
        try:
            if service_type == "trino":
                return ConnectionManager._get_trino_table_metadata(url, table_name)
            return ConnectionManager._get_sqlalchemy_table_metadata(service_type, url, table_name)
        except Exception:
            return {"table_description": None, "columns": []}

    @staticmethod
    def _get_sqlalchemy_sample_data(url: str, table_name: str, limit: int):
        engine = create_engine(url)
        with engine.connect() as connection:
            query = text(f'SELECT * FROM "{table_name.split(".", 1)[0]}"."{table_name.split(".", 1)[1]}" LIMIT {limit}')
            result = connection.execute(query)
            rows = result.fetchall()
            columns = list(result.keys())
            return {
                "columns": columns,
                "rows": [list(row) for row in rows],
                "row_count": len(rows),
            }

    @staticmethod
    def _get_trino_sample_data(url: str, table_name: str, limit: int):
        parsed = urlparse(url)
        user = parsed.username or "admin"
        host = parsed.hostname
        port = parsed.port or 8080
        path_parts = parsed.path.strip("/").split("/")
        catalog = path_parts[0] if len(path_parts) > 0 else "tpch"

        schema_name, physical_table_name = table_name.split(".", 1)
        conn = connect(host=host, port=port, user=user, catalog=catalog)
        cur = conn.cursor()
        cur.execute(f'SELECT * FROM "{schema_name}"."{physical_table_name}" LIMIT {limit}')
        rows = cur.fetchall()
        columns = [col[0] for col in cur.description] if cur.description else []
        return {
            "columns": columns,
            "rows": [list(row) for row in rows],
            "row_count": len(rows),
        }

    @staticmethod
    def _get_sqlalchemy_table_metadata(service_type: str, url: str, table_name: str):
        engine = create_engine(url)
        schema_name, physical_table_name = table_name.split(".", 1) if "." in table_name else (None, table_name)

        with engine.connect() as connection:
            if service_type == "postgres":
                table_query = text(
                    """
                    SELECT obj_description(c.oid)
                    FROM pg_class c
                    JOIN pg_namespace n ON n.oid = c.relnamespace
                    WHERE c.relname = :table_name
                      AND n.nspname = :schema_name
                    """
                )
                table_description = connection.execute(
                    table_query,
                    {"table_name": physical_table_name, "schema_name": schema_name or "public"},
                ).scalar()

                columns_query = text(
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
                )
                column_rows = connection.execute(
                    columns_query,
                    {"table_name": physical_table_name, "schema_name": schema_name or "public"},
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
    def _get_trino_table_metadata(url: str, table_name: str):
        parsed = urlparse(url)
        user = parsed.username or "admin"
        host = parsed.hostname
        port = parsed.port or 8080
        path_parts = parsed.path.strip("/").split("/")
        catalog = path_parts[0] if len(path_parts) > 0 else "tpch"

        schema_name, physical_table_name = table_name.split(".", 1) if "." in table_name else ("default", table_name)
        conn = connect(host=host, port=port, user=user, catalog=catalog)
        cur = conn.cursor()
        cur.execute(f'SHOW COLUMNS FROM "{schema_name}"."{physical_table_name}"')
        rows = cur.fetchall()

        columns = []
        for row in rows:
            column_name = row[0] if len(row) > 0 else None
            data_type = row[1] if len(row) > 1 else None
            description = row[3] if len(row) > 3 else None
            columns.append(
                {
                    "column_name": column_name,
                    "data_type": data_type,
                    "description": description,
                }
            )

        return {
            "table_description": None,
            "columns": columns,
        }
