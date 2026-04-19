from urllib.parse import urlparse
from typing import Optional, Tuple, List, Dict, Any
from trino.dbapi import connect
from trino.auth import BasicAuthentication


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
    Format: trino://user:pass@host:port/catalog
    """
    parsed = urlparse(url)
    if not parsed.hostname:
        raise ValueError("Missing hostname in Trino URL")

    # Extract catalog from path
    catalog = None
    raw_path = parsed.path.strip("/")
    if raw_path:
        parts = raw_path.split("/")
        catalog = parts[0]

    return {
        "user": parsed.username,
        "password": parsed.password,
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
    """
    if "." in table_name:
        parts = table_name.split(".", 1)
        return parts[0], parts[1]
    return default_schema, table_name


def quote_identifier(name: str) -> str:
    """
    Escape + wrap identifier để tránh lỗi SQL
    """
    escaped = name.replace('"', '""')
    return f'"{escaped}"'


# ==============================
# CONNECTION
# ==============================

def create_connection(url: str):
    """
    Tạo connection tới Trino
    """
    config = parse_trino_url(url)
    
    auth = None
    if config["user"] and config["password"]:
        # Sử dụng Basic Auth nếu có mật khẩu
        auth = BasicAuthentication(config["user"], config["password"])
    
    return connect(
        host=config["host"],
        port=config["port"],
        user=config["user"],
        catalog=config["catalog"],
        auth=auth,
        http_scheme='https' if auth else 'http'
    )


# ==============================
# TEST CONNECTION
# ==============================

def test_connection(url: str) -> Dict[str, str]:
    """
    Test kết nối Trino
    """
    try:
        conn = create_connection(url)
        cursor = conn.cursor()

        cursor.execute("SELECT 1")
        cursor.fetchone()
        conn.close()

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
        conn = create_connection(url)
        cursor = conn.cursor()

        cursor.execute("SHOW SCHEMAS")
        schemas = [
            row[0]
            for row in cursor.fetchall()
            if row[0] not in ("information_schema", "system")
        ]
        conn.close()
        return schemas

    except Exception as e:
        print(f"Error getting schemas: {e}")
        return []


# ==============================
# GET TABLES
# ==============================

def get_tables(url: str, schema: Optional[str] = None) -> List[str]:
    """
    Lấy danh sách tables
    """
    try:
        conn = create_connection(url)
        cursor = conn.cursor()

        if schema:
            safe_schema = quote_identifier(schema)
            cursor.execute(f"SHOW TABLES IN {safe_schema}")
            tables = [f"{schema}.{row[0]}" for row in cursor.fetchall()]
        else:
            config = parse_trino_url(url)
            cursor.execute(f"SELECT table_schema, table_name FROM information_schema.tables WHERE table_catalog = '{config['catalog']}'")
            tables = [f"{row[0]}.{row[1]}" for row in cursor.fetchall() if row[0] not in ("information_schema", "system")]

        conn.close()
        return tables

    except Exception as e:
        print(f"Error getting tables: {e}")
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
    safe_limit = max(1, min(limit, MAX_SAMPLE_LIMIT))
    try:
        conn = create_connection(url)
        cursor = conn.cursor()
        schema_name, table = split_table_name(table_name)

        if not schema_name:
            return {"columns": [], "rows": [], "row_count": 0}

        query = f'SELECT * FROM {quote_identifier(schema_name)}.{quote_identifier(table)} LIMIT {safe_limit}'
        cursor.execute(query)

        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description] if cursor.description else []
        conn.close()

        return {
            "columns": columns,
            "rows": [list(row) for row in rows],
            "row_count": len(rows),
        }

    except Exception as e:
        print(f"Error getting sample data: {e}")
        return {"columns": [], "rows": [], "row_count": 0}


# ==============================
# GET TABLE METADATA
# ==============================

def get_table_metadata(url: str, table_name: str) -> Dict[str, Any]:
    """
    Lấy metadata của table
    """
    try:
        conn = create_connection(url)
        cursor = conn.cursor()
        schema_name, table = split_table_name(table_name, "default")

        query = f'SHOW COLUMNS FROM {quote_identifier(schema_name)}.{quote_identifier(table)}'
        cursor.execute(query)

        columns = [
            {
                "column_name": row[0],
                "data_type": row[1],
                "description": row[2] if len(row) > 2 else None,
            }
            for row in cursor.fetchall()
        ]
        conn.close()

        return {
            "table_description": None,
            "columns": columns,
        }

    except Exception as e:
        print(f"Error getting table metadata: {e}")
        return {"table_description": None, "columns": []}