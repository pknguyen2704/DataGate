# DataGate Backend API Reference

> **Base URL:** `http://localhost:8000/api/v1`  
> **Interactive Docs:** `http://localhost:8000/docs`  
> **Health Check:** `GET http://localhost:8000/health`

---

## Authentication

All endpoints (except `/auth/login`) require a **Bearer JWT** token.

```
Authorization: Bearer <access_token>
```

### Obtain a token

```http
POST /auth/login
Content-Type: application/json

{
  "username": "admin",   // accepts username OR email
  "password": "secret"
}
```

**Response `200`**
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer"
}
```

**Error responses**
| Status | Reason |
|--------|--------|
| `401` | Wrong username / password |
| `403` | Account is disabled |

---

### Get current user

```http
GET /auth/me
Authorization: Bearer <token>
```

**Response `200`**
```json
{
  "id": "uuid",
  "username": "alice",
  "email": "alice@example.com",
  "full_name": "Alice Smith",
  "is_active": true,
  "roles": ["Admin"],
  "permissions": ["admin", "user:view", "table:view", "..."]
}
```

---

### Logout

```http
POST /auth/logout
```

Stateless — JWT is not stored server-side. The client should discard the token.  
**Response `204 No Content`**

---

## RBAC Overview

Two built-in roles:

| Role | Access |
|------|--------|
| **Admin** | Full access to all features |
| **Analyst** | Read-only access to assigned features; write access only to explicitly granted tables |

The frontend should check `permissions[]` from `/auth/me` before showing controls.

### Permission codes

| Code | What it gates |
|------|---------------|
| `admin` | Super-admin bypass |
| `user:view` / `user:create` / `user:update` / `user:delete` | User management |
| `role:view` / `role:create` / `role:update` / `role:delete` / `role:assign_permission` | Role management |
| `connection:view` / `connection:create` / `connection:update` / `connection:delete` / `connection:test` | Connection management |
| `table:view` | See registered tables |
| `table:create` / `table:update` / `table:delete` | Admin-only table CRUD |
| `table:grant_access` / `table:revoke_access` | Assign table access to users |
| `table:manage_rules` / `table:manage_thresholds` | Per-table write (granted via table access record) |
| `metadata:view` / `observability:view` | Read metadata / profiling |
| `rule:view` / `rule:create` / `rule:update` / `rule:delete` / `rule:enable_disable` | Quality rule management |
| `dashboard:view` | System dashboard stats |
| `alert:view` / `alert:acknowledge` | Alert management |
| `job:view` / `job:trigger` | Job monitoring |
| `threshold:view` / `threshold:create` / `threshold:update` / `threshold:delete` | Threshold management |

**Table-level write** — Analysts with `"manage"` access to a specific table gain `rule:create`, `rule:update`, `rule:delete`, `rule:enable_disable`, `threshold:create`, `threshold:update`, `threshold:delete` **for that table only**.

---

## Users `/users`

### List users
```http
GET /users?page=1&page_size=20&search=alice
```
Requires: `user:view`

**Query params**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `page` | int | 1 | Page number |
| `page_size` | int | 20 | Items per page (max 100) |
| `search` | string | — | Filter by username / email / full_name |

**Response `200`**
```json
{
  "items": [
    {
      "id": "uuid",
      "username": "alice",
      "email": "alice@example.com",
      "full_name": "Alice Smith",
      "is_active": true,
      "roles": ["Analyst"],
      "permissions": ["table:view", "rule:view"],
      "created_at": "2025-01-01T00:00:00",
      "updated_at": "2025-01-01T00:00:00"
    }
  ],
  "total": 42,
  "page": 1,
  "page_size": 20
}
```

---

### Create user
```http
POST /users
```
Requires: `user:create`

**Body**
```json
{
  "username": "alice",
  "email": "alice@example.com",
  "password": "strongpassword",
  "full_name": "Alice Smith",
  "role_ids": ["uuid-of-analyst-role"]
}
```

**Response `201`** — same shape as a single `UserOut`

---

### Get user
```http
GET /users/{user_id}
```
Requires: `user:view`

---

### Update user
```http
PATCH /users/{user_id}
```
Requires: `user:update`

**Body** (all fields optional)
```json
{
  "full_name": "Alice B. Smith",
  "email": "alice.b@example.com",
  "password": "newpassword",
  "is_active": true
}
```

---

### Deactivate user (soft-delete)
```http
DELETE /users/{user_id}
```
Requires: `user:delete`. Sets `is_active = false`. Returns `204`.

---

### Assign roles to user
```http
POST /users/{user_id}/roles
```
Requires: `role:assign_permission`

**Body**
```json
["role-uuid-1", "role-uuid-2"]
```

**Response `200`** — full `UserOut`

---

## Roles & Permissions `/roles`

### List permissions
```http
GET /roles/permissions
```
Requires: `role:view`

**Response `200`**
```json
[
  { "id": "uuid", "code": "table:view", "name": "View Tables", "group": "Table Management" }
]
```

---

### List roles
```http
GET /roles
```
Requires: `role:view`

**Response `200`**
```json
[
  {
    "id": "uuid",
    "name": "Admin",
    "description": "Full access",
    "is_active": true,
    "is_system": true,
    "permissions": [{ "id": "uuid", "code": "admin", "name": "Super Admin", "group": "System" }],
    "created_at": "2025-01-01T00:00:00"
  }
]
```

---

### Create role
```http
POST /roles
```
Requires: `role:create`

**Body**
```json
{ "name": "Data Steward", "description": "Manages data quality rules" }
```

---

### Get / Update / Delete role
```http
GET    /roles/{role_id}
PATCH  /roles/{role_id}   // body: { "name"?, "description"?, "is_active"? }
DELETE /roles/{role_id}   // 204; system roles (Admin/Analyst) cannot be deleted
```

---

### Assign permissions to role
```http
POST /roles/{role_id}/permissions
```
Requires: `role:assign_permission`

**Body** — replaces the entire permission set:
```json
["permission-uuid-1", "permission-uuid-2"]
```

---

## Connections `/connections`

A Connection stores the credentials for one data system (Trino + Iceberg REST + MinIO).  
**Secrets** (`trino_password`, `minio_secret_key`) are write-only — never returned in responses.

### List connections
```http
GET /connections
```
Requires: `connection:view`

**Response `200`**
```json
[
  {
    "id": "uuid",
    "name": "Production Lakehouse",
    "description": "Main Iceberg/Trino cluster",
    "trino_host": "trino.internal",
    "trino_port": 8080,
    "trino_user": "service_account",
    "iceberg_rest_url": "http://iceberg-rest:8181",
    "iceberg_catalog_name": "iceberg",
    "minio_endpoint_url": "http://minio:9000",
    "minio_access_key": "minioadmin",
    "minio_region": "us-east-1",
    "is_active": true,
    "created_at": "2025-01-01T00:00:00",
    "updated_at": "2025-01-01T00:00:00"
  }
]
```

---

### Create connection
```http
POST /connections
```
Requires: `connection:create`

**Body**
```json
{
  "name": "Production Lakehouse",
  "description": "Main cluster",
  "trino_host": "trino.internal",
  "trino_port": 8080,
  "trino_user": "svc",
  "trino_password": "secret",
  "iceberg_rest_url": "http://iceberg-rest:8181",
  "iceberg_catalog_name": "iceberg",
  "minio_endpoint_url": "http://minio:9000",
  "minio_access_key": "key",
  "minio_secret_key": "secret",
  "minio_region": "us-east-1"
}
```

**Response `201`** — `ConnectionOut` (secrets masked)

---

### Get / Update / Delete connection
```http
GET    /connections/{conn_id}
PATCH  /connections/{conn_id}   // any subset of create fields
DELETE /connections/{conn_id}   // 400 if tables still reference this connection
```

---

### Test connection (stub)
```http
POST /connections/{conn_id}/test
```
Requires: `connection:test`

**Response `200`**
```json
{ "success": true, "message": "Connection 'Production Lakehouse' is reachable (stub)" }
```

---

### Browse connection metadata (stub)
```http
GET /connections/{conn_id}/metadata?catalog=iceberg&schema_name=bronze
```

Returns catalogs -> schemas -> tables hierarchy for the sidebar explorer.

| Query | Returns |
|-------|---------|
| (none) | `{ "catalogs": ["iceberg", "hive", "system"] }` |
| `catalog=iceberg` | `{ "schemas": ["bronze", "silver", "gold"] }` |
| `catalog=iceberg&schema_name=bronze` | `{ "tables": [] }` |

---

## Tables `/tables`

Tables are registered Iceberg tables that DataGate monitors. Access is filtered by role + per-table grants.

### Explorer (read-only hierarchy)

```http
GET /tables/explore
```
Returns all connections -> schemas -> tables for the sidebar. No permission required beyond auth.

**Response `200`**
```json
[
  {
    "connection": { "id": "uuid", "name": "Production Lakehouse" },
    "schemas": ["bronze", "silver", "gold"],
    "tables": [
      {
        "id": "uuid",
        "table_name": "yellow_tripdata",
        "schema_name": "bronze",
        "full_name": "iceberg.bronze.yellow_tripdata",
        "connection_id": "uuid"
      }
    ]
  }
]
```

---

```http
GET /tables/explore/overview?table=yellow_tripdata&connection_id=uuid&schema=bronze
```

**Response `200`**
```json
{
  "id": "uuid",
  "table_name": "yellow_tripdata",
  "full_name": "iceberg.bronze.yellow_tripdata",
  "schema_name": "bronze",
  "catalog_name": "iceberg",
  "connection_name": "Production Lakehouse",
  "description": null,
  "is_active": true
}
```

---

```http
GET /tables/explore/sample?table=yellow_tripdata&connection_id=uuid&schema=bronze&sample_limit=50
```
Returns sample rows (stub - Trino integration pending).

---

### List tables
```http
GET /tables?page=1&page_size=20&search=trip&connection_id=uuid
```
Requires: `table:view`

- **Admin**: sees all tables  
- **Analyst**: sees only tables explicitly granted via `UserTableAccess`

**Response `200`**
```json
{
  "items": [
    {
      "id": "uuid",
      "connection_id": "uuid",
      "connection_name": "Production Lakehouse",
      "catalog_name": "iceberg",
      "schema_name": "bronze",
      "table_name": "yellow_tripdata",
      "description": null,
      "is_active": true,
      "owner_id": "uuid",
      "created_at": "2025-01-01T00:00:00",
      "updated_at": "2025-01-01T00:00:00",
      "latest_date_hour": "2025-06-01 00:00:00",
      "latest_record_count": 12500000
    }
  ],
  "total": 5,
  "page": 1,
  "page_size": 20
}
```

---

### Register table
```http
POST /tables
```
Requires: `table:create`

**Body**
```json
{
  "connection_id": "uuid",
  "catalog_name": "iceberg",
  "schema_name": "bronze",
  "table_name": "yellow_tripdata",
  "description": "NYC taxi raw data"
}
```

**Response `201`** — `TableOut`

---

### Get / Update / Delete table
```http
GET    /tables/{table_id}
PATCH  /tables/{table_id}   // { "description"?, "is_active"? }
DELETE /tables/{table_id}   // 204
```

- `GET` / `PATCH`: access checked against `UserTableAccess` for Analysts  
- `PATCH` requires `"manage"` access level (or Admin)  
- `DELETE` requires `table:create` permission

---

### Table access management (Admin only)

```http
POST   /tables/{table_id}/access
DELETE /tables/{table_id}/access/{user_id}
```

Requires: `table:grant_access` / `table:revoke_access`

**Grant body**
```json
{ "user_id": "uuid", "access_level": "view" }
```

`access_level`: `"view"` | `"manage"`

`"manage"` additionally grants the user `rule:create`, `rule:update`, `rule:delete`, `rule:enable_disable`, `threshold:create`, `threshold:update`, `threshold:delete` for this table.

---

### Table sub-resources

All sub-resources require at least `"view"` access to the table.

#### Batch metadata history
```http
GET /tables/{table_id}/metadata?limit=10
```

**Response `200`**
```json
[
  {
    "id": "uuid",
    "snapshot_id": "8765432198765",
    "date_hour": "2025-06-01T00:00:00",
    "committed_at": "2025-06-01T00:05:32",
    "operation": "append",
    "added_records": 125000,
    "total_records": 12500000
  }
]
```

---

#### Data quality rules for a table
```http
GET /tables/{table_id}/rules?status=pending
```

Returns rule list (same shape as `GET /rules`).

---

## Rules `/rules`

Data quality rules. Each rule targets one column of one registered table.

**Two sources:**
- `"system"` — auto-generated by the Spark/Deequ rule suggestion job; arrive as `"pending"` for user review
- `"manual"` — created by the user via the UI dropdown; immediately `"active"`

**Lifecycle:**
```
system rule: pending -> active (accepted) | inactive (rejected)
manual rule: active -> inactive (disabled)
```

**Constraint types (UI dropdown values):**
| Value | Description | Deequ origin |
|-------|-------------|--------------|
| `not_null` | Column must not be NULL | `CompletenessConstraint` |
| `non_negative` | Column value >= 0 | `ComplianceConstraint` |
| `unique` | All values must be unique | `UniquenessConstraint` |
| `value_range` | Value must be in an allowed set | `ComplianceConstraint` (IN list) |
| `range_check` | Value between min and max | Manual only |
| `regex` | Value matches a regex pattern | Manual only |

---

### List rules
```http
GET /rules?table_id=uuid&status=pending
```
Requires: `rule:view`

**Response `200`**
```json
[
  {
    "id": "uuid",
    "table_id": "uuid",
    "column_name": "tip_amount",
    "constraint_type": "not_null",
    "source": "system",
    "status": "pending",
    "description": "'tip_amount' is not null",
    "threshold_min": null,
    "threshold_max": null,
    "value_set": null,
    "regex_pattern": null,
    "constraint_name": "CompletenessConstraint(Completeness(tip_amount,None,None))",
    "current_value": "Completeness: 1.0",
    "suggesting_rule": "CompleteIfCompleteRule()",
    "code_for_constraint": ".isComplete(\"tip_amount\")",
    "suggested_at_date_hour": "2025-06-01 00:00:00",
    "created_by_user_id": null,
    "last_modified_by_user_id": null,
    "created_at": "2025-06-01T00:10:00",
    "updated_at": "2025-06-01T00:10:00"
  }
]
```

---

### Create manual rule
```http
POST /rules
```
Requires: `rule:create`

**Body**
```json
{
  "table_id": "uuid",
  "column_name": "fare_amount",
  "constraint_type": "range_check",
  "description": "Fare must be between 0 and 500",
  "threshold_min": 0,
  "threshold_max": 500
}
```

For `value_range`, pass `value_set` as a JSON array string:
```json
{
  "constraint_type": "value_range",
  "value_set": "[\"cash\", \"card\", \"voucher\"]"
}
```

For `regex`:
```json
{
  "constraint_type": "regex",
  "regex_pattern": "^[A-Z]{2}\\d{4}$"
}
```

**Response `201`**
```json
{ "id": "uuid", "constraint_type": "range_check", "status": "active" }
```

---

### Update rule parameters
```http
PATCH /rules/{rule_id}
```
Requires: `rule:update`

**Body** (all optional)
```json
{
  "description": "Updated description",
  "threshold_min": 0,
  "threshold_max": 1000
}
```

---

### Accept / reject / disable a rule
```http
PATCH /rules/{rule_id}/status
```
Requires: `rule:enable_disable`

**Body**
```json
{ "status": "active" }
```

`status`: `"pending"` | `"active"` | `"inactive"`

Used by the UI to:
- Accept a system suggestion: `"pending"` -> `"active"`  
- Reject a system suggestion: `"pending"` -> `"inactive"`  
- Disable an active rule: `"active"` -> `"inactive"`

---

### Delete rule
```http
DELETE /rules/{rule_id}
```
Requires: `rule:delete`. Returns `204`.

---

## Dashboard `/dashboard`

```http
GET /dashboard/summary
```
Requires: `dashboard:view`

**Response `200`**
```json
{
  "total_tables": 12,
  "active_rules": 48,
  "open_alerts": 0,
  "recent_failed_jobs": 0
}
```

---

## Alerts `/alerts` (stub)

```http
GET    /alerts?status=open&severity=critical&table_id=uuid&limit=50
PATCH  /alerts/{alert_id}/status
```

Alert model not yet implemented - returns `[]` or `501`.

---

## Jobs `/jobs` (stub)

```http
GET  /jobs
POST /jobs/trigger
```

Returns `[]` / `501` until implemented.

---

## Thresholds `/thresholds` (stub)

```http
GET /thresholds?table_id=uuid
```

Returns `[]` until implemented.

---

## Common Patterns

### Error responses

All errors follow this shape:
```json
{ "detail": "Human-readable error message" }
```

| Status | Meaning |
|--------|---------|
| `400` | Validation error / duplicate / business rule violation |
| `401` | Missing or invalid JWT |
| `403` | Authenticated but insufficient permissions |
| `404` | Resource not found |
| `501` | Endpoint not yet implemented |

---

### Pagination

All paginated endpoints use the same envelope:
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 20
}
```

---

### UUID fields

All `id` fields are standard UUID strings:
```
"id": "550e8400-e29b-41d4-a716-446655440000"
```

---

### Date / time fields

All timestamps are ISO 8601 UTC:
```
"created_at": "2025-06-01T00:00:00"
"date_hour":  "2025-06-01 00:00:00"   // profiling partition key
```

---

## Frontend Integration Checklist

| UI Feature | API calls |
|------------|-----------|
| Login | `POST /auth/login` -> store token |
| Current user / permissions | `GET /auth/me` -> check `permissions[]` before showing controls |
| Sidebar explorer | `GET /tables/explore` |
| Table overview panel | `GET /tables/explore/overview?table=...&connection_id=...` |
| Admin: connection CRUD | `GET/POST/PATCH/DELETE /connections` |
| Admin: register table | `POST /tables` |
| Admin: grant table access | `POST /tables/{id}/access` |
| Table list | `GET /tables` (auto-filtered by user access) |
| Batch history | `GET /tables/{id}/metadata` |
| Rule list (per table) | `GET /tables/{id}/rules` or `GET /rules?table_id=...` |
| Accept/reject system rule | `PATCH /rules/{id}/status` |
| Add manual rule (dropdown) | `POST /rules` |
| Edit rule thresholds | `PATCH /rules/{id}` |
| Dashboard stats | `GET /dashboard/summary` |
| User management | `GET/POST/PATCH/DELETE /users` |
| Role management | `GET/POST/PATCH/DELETE /roles`, `POST /roles/{id}/permissions` |
