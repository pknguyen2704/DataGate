"""
Models __init__ — import all models for Alembic auto-discovery
"""
from .auth import User, Role, Permission, user_roles, role_permissions
from .connection import Connection, TableInfo, UserTableAccess
from .quality import (
    TableBatchMetadata,
    TableSchemaMetadata,
    SchemaChangeEvent,
    ColumnProfileMetric,
    QualityRule,
    RuleValidationRun,
    RuleValidationResult,
    QualityThreshold,
    AnomalyDetectionRun,
    AnomalyFeatureImportance,
    Alert,
    JobRun,
)

__all__ = [
    "User", "Role", "Permission", "user_roles", "role_permissions",
    "Connection", "TableInfo", "UserTableAccess",
    "TableBatchMetadata", "TableSchemaMetadata", "SchemaChangeEvent",
    "ColumnProfileMetric",
    "QualityRule", "RuleValidationRun", "RuleValidationResult",
    "QualityThreshold",
    "AnomalyDetectionRun", "AnomalyFeatureImportance",
    "Alert",
    "JobRun",
]