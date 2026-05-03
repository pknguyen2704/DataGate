
from pydantic import BaseModel

# ── Auth ──────────────────────────────────────────────────────────────────────
from app.schemas.user import (
    UserOut, UserCreate, UserUpdate, UserRoleAssign,
)
from app.schemas.role import (
    PermissionOut, RoleOut, RoleCreate, RoleUpdate, PermissionAssign,
)

# ── Connection &Table ────────────────────────────────────────────────────────
from app.schemas.connection import (
    ConnectionOut, ConnectionCreate, ConnectionUpdate,
    ConnectionTestResult, CatalogList, SchemaList,TableList,
)
from app.schemas.table import (
    TableOut, TableCreate, TableAdd, TableUpdate, TableAccessGrant,
    PaginatedTables, ExploreTableItem, ExploreConnectionItem, TableOverviewOut,
)

# ── Metadata Collection ───────────────────────────────────────────────────────
from app.schemas.table_batch_metadata import (
    BatchMetadataOut,
)


from app.schemas.rule import (
    RuleSource, RuleStatus, RuleVerificationStatus, ConstraintType,
    DataRuleOut, DataRuleCreate, DataRuleUpdate,
    DataRuleStatusUpdate, DataRuleSummary, RuleVerificationResultOut,
)
