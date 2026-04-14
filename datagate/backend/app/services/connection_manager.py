from sqlalchemy import create_engine, text
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
