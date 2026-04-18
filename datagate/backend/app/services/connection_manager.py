from urllib.parse import urlparse
from typing import Optional, Tuple, List, Dict, Any

from trino.dbapi import connect


# ==============================
# CONFIG
# ==============================

DEFAULT_SAMPLE_LIMIT = 50
MAX_SAMPLE_LIMIT = 1000


# ==============================
# HELPER FUNCTIONS
# ==============================

def parse_trino_url(url: str) -> dict:
    """
    Parse Trino URL

    Format:
    trino://user@host:port/catalog

    Example:
    trino://admin@localhost:8080/hive
    """

    parsed = urlparse(url)

    if not parsed.hostname:
        raise ValueError("Missing hostname in Trino URL")

    # Lấy catalog từ path
    catalog = None
    raw_path = parsed.path.strip("/")

    if raw_path:
        parts = raw_path.split("/")
        catalog = parts[0]

    return {
        "user": parsed.username,
        "host": parsed.hostname,
        "port": parsed.port or 8080,
        "catalog": catalog,
    }


def split_table_name(
    table_name: str,
    default_schema: Optional[str] = None
) -> Tuple[Optional[str], str]:
    """
    Tách table_name thành schema và table

    "schema.table" -> ("schema", "table")
    "table"        -> (default_schema, "table")
    """

    if "." in table_name:
        parts = table_name.split(".")
        return parts[0], parts[1]

    return default_schema, table_name


def quote_identifier(name: str) -> str:
    """
    Escape + wrap identifier để tránh lỗi SQL

    my_table  -> "my_table"
    my"table  -> "my""table"
    """

    escaped = name.replace('"', '""')
    return f'"{escaped}"'


# ==============================
# CONNECTION
# ==============================

def create_trino_connection(url: str):
    """
    Tạo connection tới Trino
    """

    config = parse_trino_url(url)

    return connect(
        host=config["host"],
        port=config["port"],
        user=config["user"],
        catalog=config["catalog"],
    )


# ==============================
# TEST CONNECTION
# ==============================

def test_connection(url: str) -> Dict[str, str]:
    """
    Test kết nối Trino
    """

    try:
        conn = create_trino_connection(url)
        cursor = conn.cursor()

        cursor.execute("SELECT 1")
        cursor.fetchone()

        return {
            "status": "success",
            "message": "Trino connection successful"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


# ==============================
# GET SCHEMAS
# ==============================

def get_schemas(url: str) -> List[str]:
    """
    Lấy danh sách schema trong Trino
    """

    try:
        conn = create_trino_connection(url)
        cursor = conn.cursor()

        cursor.execute("SHOW SCHEMAS")

        return [
            row[0]
            for row in cursor.fetchall()
            if row[0] not in ("information_schema", "system")
        ]

    except Exception:
        return []


# ==============================
# GET TABLES
# ==============================

def get_tables(url: str, schema: Optional[str] = None) -> List[str]:
    """
    Lấy danh sách tables
    """

    try:
        conn = create_trino_connection(url)
        cursor = conn.cursor()

        # Nếu có schema → chỉ lấy trong schema đó
        if schema:
            safe_schema = quote_identifier(schema)
            cursor.execute(f'SHOW TABLES IN "{safe_schema}"')
            return [row[0] for row in cursor.fetchall()]

        # Nếu không có schema → lấy tất cả
        config = parse_trino_url(url)

        cursor.execute(
            """
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_catalog = ?
            """,
            (config["catalog"],),
        )

        return [
            f"{row[0]}.{row[1]}"
            for row in cursor.fetchall()
            if row[0] not in ("information_schema", "staged")
        ]

    except Exception:
        return []


# ==============================
# GET SAMPLE DATA
# ==============================

def get_sample_data(
    url: str,
    table_name: str,
    limit: int = DEFAULT_SAMPLE_LIMIT
) -> Dict[str, Any]:
    """
    Lấy dữ liệu sample từ table
    """

    # đảm bảo limit hợp lệ
    safe_limit = max(1, min(limit, MAX_SAMPLE_LIMIT))

    try:
        conn = create_trino_connection(url)
        cursor = conn.cursor()

        schema_name, table = split_table_name(table_name)

        if not schema_name:
            return {"columns": [], "rows": [], "row_count": 0}

        query = f"""
        SELECT *
        FROM "{quote_identifier(schema_name)}"."{quote_identifier(table)}"
        LIMIT {safe_limit}
        """

        cursor.execute(query)

        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description] if cursor.description else []

        return {
            "columns": columns,
            "rows": [list(row) for row in rows],
            "row_count": len(rows),
        }

    except Exception:
        return {
            "columns": [],
            "rows": [],
            "row_count": 0,
        }


# ==============================
# GET TABLE METADATA
# ==============================

def get_table_metadata(url: str, table_name: str) -> Dict[str, Any]:
    """
    Lấy metadata của table
    """

    try:
        conn = create_trino_connection(url)
        cursor = conn.cursor()

        schema_name, table = split_table_name(table_name, "default")

        query = f"""
        SHOW COLUMNS FROM "{quote_identifier(schema_name)}"."{quote_identifier(table)}"
        """

        cursor.execute(query)

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

    except Exception:
        return {
            "table_description": None,
            "columns": [],
        }