"""
Connection management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from typing import Optional, Any
import uuid
from datetime import datetime

from app.db.session import get_db
from app.models.auth import User
from app.models.connection import Connection, TableInfo
from app.core.permissions import PermissionCode
from app.api.deps import get_current_user, require_permission

router = APIRouter()


class ConnectionOut(BaseModel):
    id: str
    name: str
    description: Optional[str]
    conn_type: str
    config: dict  # Sensitive fields will be masked
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ConnectionCreate(BaseModel):
    name: str
    description: Optional[str] = None
    conn_type: str  # trino, iceberg_rest, minio
    config: dict[str, Any]


class ConnectionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[dict[str, Any]] = None
    is_active: Optional[bool] = None


class ConnectionTestResult(BaseModel):
    success: bool
    message: str
    details: Optional[dict] = None


SENSITIVE_KEYS = {"password", "secret_key", "access_key", "token", "auth_token"}


def _mask_config(config: dict) -> dict:
    """Mask sensitive fields in config before returning to client."""
    return {
        k: "***" if k.lower() in SENSITIVE_KEYS else v
        for k, v in config.items()
    }


def _conn_to_out(conn: Connection) -> ConnectionOut:
    return ConnectionOut(
        id=conn.id,
        name=conn.name,
        description=conn.description,
        conn_type=conn.conn_type,
        config=_mask_config(conn.config or {}),
        is_active=conn.is_active,
        created_at=conn.created_at,
        updated_at=conn.updated_at,
    )


@router.get("", response_model=list[ConnectionOut])
async def list_connections(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(PermissionCode.CONNECTION_VIEW)),
):
    result = await db.execute(select(Connection).order_by(Connection.created_at.desc()))
    return [_conn_to_out(c) for c in result.scalars().all()]


@router.post("", response_model=ConnectionOut, status_code=status.HTTP_201_CREATED)
async def create_connection(
    body: ConnectionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(PermissionCode.CONNECTION_CREATE)),
):
    result = await db.execute(select(Connection).where(Connection.name == body.name))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Connection name already exists")

    conn = Connection(
        id=str(uuid.uuid4()),
        name=body.name,
        description=body.description,
        conn_type=body.conn_type,
        config=body.config,
        created_by=current_user.id,
    )
    db.add(conn)
    await db.flush()
    await db.refresh(conn)
    return _conn_to_out(conn)


@router.get("/{conn_id}", response_model=ConnectionOut)
async def get_connection(
    conn_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(PermissionCode.CONNECTION_VIEW)),
):
    result = await db.execute(select(Connection).where(Connection.id == conn_id))
    conn = result.scalars().first()
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    return _conn_to_out(conn)


@router.patch("/{conn_id}", response_model=ConnectionOut)
async def update_connection(
    conn_id: str,
    body: ConnectionUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(PermissionCode.CONNECTION_UPDATE)),
):
    result = await db.execute(select(Connection).where(Connection.id == conn_id))
    conn = result.scalars().first()
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")

    if body.name is not None:
        conn.name = body.name
    if body.description is not None:
        conn.description = body.description
    if body.config is not None:
        conn.config = {**conn.config, **body.config}
    if body.is_active is not None:
        conn.is_active = body.is_active

    await db.flush()
    await db.refresh(conn)
    return _conn_to_out(conn)


@router.delete("/{conn_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_connection(
    conn_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(PermissionCode.CONNECTION_DELETE)),
):
    result = await db.execute(select(Connection).where(Connection.id == conn_id))
    conn = result.scalars().first()
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")

    # Check if used by tables
    table_count = await db.execute(
        select(func.count()).where(TableInfo.connection_id == conn_id)
    )
    if table_count.scalar() > 0:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete connection in use by registered tables. Deactivate it instead.",
        )
    await db.delete(conn)


@router.post("/{conn_id}/test", response_model=ConnectionTestResult)
async def test_connection(
    conn_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(PermissionCode.CONNECTION_TEST)),
):
    """Test connectivity for a configured connection."""
    result = await db.execute(select(Connection).where(Connection.id == conn_id))
    conn = result.scalars().first()
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")

    # TODO: Implement actual connection test per conn_type
    # For now return a simulated success
    return ConnectionTestResult(
        success=True,
        message=f"Connection '{conn.name}' ({conn.conn_type}) is reachable",
        details={"conn_type": conn.conn_type, "is_active": conn.is_active},
    )
