from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.trino_client import TrinoClient
from app.db.session import get_db
from app.models import Connection, Table, User


router = APIRouter(prefix="/explore", tags=["Explore"])

SessionDep = Annotated[Session, Depends(get_db)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]


@router.get("")
def get_explore_data(db: SessionDep, _user: CurrentUserDep):
    all_tables = (
        db.query(Table, Connection)
        .join(Connection, Connection.id == Table.connection_id)
        .filter(Table.is_active.is_(True), Connection.is_active.is_(True))
        .order_by(
            Table.catalog_name.asc(),
            Table.schema_name.asc(),
            Table.table_name.asc(),
        )
        .all()
    )

    grouped: dict[str, dict] = {}
    for table, connection in all_tables:
        catalog_bucket = grouped.setdefault(
            table.catalog_name,
            {
                "catalog_name": table.catalog_name,
                "schemas": {},
                "table_count": 0,
            },
        )
        schema_bucket = catalog_bucket["schemas"].setdefault(
            table.schema_name,
            {
                "schema_name": table.schema_name,
                "tables": [],
            },
        )
        schema_bucket["tables"].append(
            {
                "id": table.id,
                "table_name": table.table_name,
                "schema_name": table.schema_name,
                "catalog_name": table.catalog_name,
                "full_name": f"{table.catalog_name}.{table.schema_name}.{table.table_name}",
                "connection_id": table.connection_id,
                "connection_name": connection.name,
            }
        )
        catalog_bucket["table_count"] += 1

    return [
        {
            "catalog_name": catalog_name,
            "table_count": bucket["table_count"],
            "schemas": [
                {
                    "schema_name": schema_name,
                    "table_count": len(schema_bucket["tables"]),
                    "tables": schema_bucket["tables"],
                }
                for schema_name, schema_bucket in sorted(bucket["schemas"].items())
            ],
        }
        for catalog_name, bucket in sorted(grouped.items())
    ]


def _get_managed_table(
    db: Session,
    catalog: str,
    schema: str,
    table: str,
) -> Table:
    managed_table = (
        db.query(Table)
        .filter(
            Table.catalog_name == catalog,
            Table.schema_name == schema,
            Table.table_name == table,
            Table.is_active.is_(True),
        )
        .order_by(Table.updated_at.desc())
        .first()
    )
    if managed_table is None:
        raise HTTPException(status_code=404, detail="Managed table not found")
    return managed_table


@router.get("/overview")
def get_explore_overview(
    table: str,
    schema: str,
    db: SessionDep,
    _user: CurrentUserDep,
    catalog: Annotated[str, Query()],
):
    managed_table = _get_managed_table(db, catalog=catalog, schema=schema, table=table)
    connection = db.query(Connection).filter(Connection.id == managed_table.connection_id).first()
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")

    client = TrinoClient(connection)
    try:
        columns = client.get_columns(catalog, schema, table)
        return {
            "id": managed_table.id,
            "asset_name": table,
            "full_name": f"{catalog}.{schema}.{table}",
            "table_name": table,
            "schema_name": schema,
            "catalog_name": catalog,
            "connection_name": connection.name,
            "columns": columns,
            "owner": {
                "full_name": managed_table.owner.full_name if managed_table.owner else "System",
            },
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        client.close()


@router.get("/sample")
def get_explore_sample(
    table: str,
    schema: str,
    db: SessionDep,
    _user: CurrentUserDep,
    catalog: Annotated[str, Query()],
    sample_limit: Annotated[int, Query(ge=1, le=1000)] = 50,
):
    managed_table = _get_managed_table(db, catalog=catalog, schema=schema, table=table)
    connection = db.query(Connection).filter(Connection.id == managed_table.connection_id).first()
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")

    client = TrinoClient(connection)
    try:
        return {
            "table_id": managed_table.id,
            "table_name": managed_table.table_name,
            "schema_name": managed_table.schema_name,
            "catalog_name": managed_table.catalog_name,
            "sample_data": client.get_sample_data(catalog, schema, table, limit=sample_limit),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        client.close()
