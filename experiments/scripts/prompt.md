# Tài liệu mô tả thiết kế web
## Đặc tả chức năng
1. Chức năng xem sức khỏe tổng thể của các nguồn dữ liệu
- Theo dõi sức khỏe của toàn bộ dữ liệu được quản lý bởi platform
+ Chấm phần trăm tổng quan toàn bộ data platform
+ Chấm phần trăm sức khỏe của các bảng thuộc schema
+ Chấm phần trăm sức khỏe cua từng bảng
- Quy tắc chấm sức khỏe được tính theo 
+ Số lượng fail - critical ở các bảng kết quả
+ Số lượng fail - warning ở các bảng kết quả
- Việc xem sức khỏe có thể xem theo được
+ Toàn bộ thời gian
+ Từng processing_date_hour
- Health score được tính theo thang điểm 0-100.


Mỗi table có:
- critical_fail_count
- warning_fail_count
- total_check_count

Công thức mặc định:
critical_penalty = critical_fail_count * 10
warning_penalty = warning_fail_count * 3
table_health_score = max(0, 100 - critical_penalty - warning_penalty)

Schema health score = trung bình health score của các table thuộc schema.
Platform health score = trung bình health score của toàn bộ table đang được quản lý.

Nếu table chưa có dữ liệu verify tại processing_date_hour được chọn thì trạng thái là UNKNOWN, không tính vào trung bình.

Lưu ý các verify đã resolve thì không được gộp vào để tính điểm
2. Chức năng theo dõi metadata và profiling
- Có danh sách các schema, table được quản lý
+ Schema bao gồm các tables hiển thị dưới dạng dropdown
+ Danh sách này để làm thông tin các bảng, (có thể kết hợp đưa nó làm biến đầu vào cho filter của grafana)
- Giao diện dashboard theo dõi metadata, profiling
+ Giao diện này đã được làm trên Grafana, sẽ được nhúng vào website
3. Chức nắng làm việc với các threshold metrics
- Giao diện quản lý các threshold các phần tho từng bảng riêng biệt
+ metadata
+ profiling
+ auc
4. Chức năng quản lý các luật dữ liệu
- Các luật dữ liệu sẽ dược hệ thống sinh ra
- Người dùng có thể chọn những luật nào được áp dụng, chỉnh sửa luật, thêm luật mới
5. Chức năng xem kết quả về chất lượng dữ liệu
- Theo dõi chất lượng dữ liệu
+ Kết quả metadata verify
+ Kết quả profiling verify
+ Kết quả rule verify
+ Kết quả Anomaly Detection: Xem kết quả AUC (ngưỡng) + giải thích SHAP theo các processing_data_hour mình chọn
6. Setting
- Platform Connection
+ Các thông tin connection của bảng đó (Cho phép cập nhật thông tin connection, có thể test connection, có thể thêm hoặc loại bỏ các bảng muốn hệ thống này quản lý)
- LightGBM Paramaters
+ Xem được thông tin parameter hiện tại tương ứng của mỗi bảng có filter
+ Có thể chỉnh sửa hoặc thêm file (Json Format in ra trong quá trình Huấn luyện mô hình) để làm dữ liệu đầu vào
- Users
+ RBAC
+ Manage users information (Thêm sửa xóa)

## Mô tả các endpoint
1. auth_router.py
Prefix: /auth
- Post: /login
- Post: /logout
- Get: /me (lấy thông tin user hiện tại)
- Get: /me/permissions (Lấy danh sách permissions của user hiện tại)
- out: /me/password (Đổi mật khẩu của chính user đó)
2. home_router.py
prefix: /home/health
- get: /summary (Lấy health score tổng quan)
- get: /schemas (Lấy score theo từng schemas)
- get: /schemas/{schema_name} (Lấy heal của một schema)
- get: /tables (Lấy health score của các table)
- get: /tables/{table_id} (lấy health score của một table)
- get /failures/summary (Tổng hợp số lượng fail/critical/warning)
- get: /timeline (Headlth score theo thời gian)
3. observability_router.py
prefix: /observability
- Get: /list (Lấy schema/table để hiển thị dropdrown)
- GET: /grafana/variables (Lấy biến filter cho Grafana: schema, table, processing time)
4. connection_router.py
prefix: /connections
- get: / (Lấy connections)
- post: / (tạo connection)
- get: /{connection_id} (Xem chi tiết connection)
- put: /{connection_id} (Cập nhật)
- delete: /{connection_id} (Xóa mềm, ẩn connection)
- patch:  /{connection_id}/activate (active connection)
- PATCH	/{connection_id}/deactivate	Deactivate connection
- POST	/{connection_id}/test	Test connection Trino/Iceberg/MinIO
- GET	/{connection_id}/schemas	Discover schema từ Trino/Iceberg
- GET	/{connection_id}/schemas/{schema_name}/tables	Discover tables trong schema
5. table_router.py
prefix: /tables
- GET	/	Danh sách managed tables
- POST	/	Thêm table vào danh sách quản lý
- GET	/{table_id}	Xem chi tiết table
- PUT	/{table_id}	Cập nhật table
- DELETE	/{table_id}	Xóa mềm hoặc loại khỏi quản lý
- PATCH	/{table_id}/activate	Bật quản lý table
- PATCH	/{table_id}/deactivate	Tắt quản lý table
- GET	/{table_id}/columns	Lấy danh sách column từ profiling gần nhất
- GET	/{table_id}/processing-hours	Lấy các processing_date_hour có dữ liệu

6. Metric_router.py
prefix: /metrics
- GET	/metadata-thresholds	Danh sách metadata thresholds
- POST	/metadata-thresholds	Tạo metadata threshold
- GET	/metadata-thresholds/{threshold_id}	Xem chi tiết
- PUT	/metadata-thresholds/{threshold_id}	Cập nhật
- DELETE	/metadata-thresholds/{threshold_id}	Xóa hoặc deactivate
- PATCH	/metadata-thresholds/{threshold_id}/activate	Active
- PATCH	/metadata-thresholds/{threshold_id}/deactivate	Inactive
- GET	/profiling-thresholds	Danh sách profiling thresholds
- POST	/profiling-thresholds	Tạo profiling threshold
- GET	/profiling-thresholds/{threshold_id}	Xem chi tiết
- PUT	/profiling-thresholds/{threshold_id}	Cập nhật
- DELETE	/profiling-thresholds/{threshold_id}	Xóa hoặc deactivate
- PATCH	/profiling-thresholds/{threshold_id}/activate	Active
- PATCH	/profiling-thresholds/{threshold_id}/deactivate

Auth:
POST   /api/v1/auth/login
POST   /api/v1/auth/logout
GET    /api/v1/auth/me
GET    /api/v1/auth/me/permissions

Health:
GET    /api/v1/health/summary
GET    /api/v1/health/schemas
GET    /api/v1/health/tables
GET    /api/v1/health/timeline

Observability:
GET    /api/v1/observability/managed-tree
GET    /api/v1/observability/grafana/embed-url

Connections:
GET    /api/v1/connections
POST   /api/v1/connections
GET    /api/v1/connections/{connection_id}
PUT    /api/v1/connections/{connection_id}
DELETE /api/v1/connections/{connection_id}
POST   /api/v1/connections/{connection_id}/test
GET    /api/v1/connections/{connection_id}/schemas
GET    /api/v1/connections/{connection_id}/schemas/{schema_name}/tables

Tables:
GET    /api/v1/tables
POST   /api/v1/tables
GET    /api/v1/tables/{table_id}
PUT    /api/v1/tables/{table_id}
DELETE /api/v1/tables/{table_id}
PATCH  /api/v1/tables/{table_id}/activate
PATCH  /api/v1/tables/{table_id}/deactivate
GET    /api/v1/tables/{table_id}/columns
GET    /api/v1/tables/{table_id}/processing-hours

Metrics:
GET    /api/v1/metrics/metadata-thresholds
POST   /api/v1/metrics/metadata-thresholds
PUT    /api/v1/metrics/metadata-thresholds/{threshold_id}
DELETE /api/v1/metrics/metadata-thresholds/{threshold_id}

GET    /api/v1/metrics/profiling-thresholds
POST   /api/v1/metrics/profiling-thresholds
PUT    /api/v1/metrics/profiling-thresholds/{threshold_id}
DELETE /api/v1/metrics/profiling-thresholds/{threshold_id}

GET    /api/v1/metrics/auc-thresholds
POST   /api/v1/metrics/auc-thresholds
PUT    /api/v1/metrics/auc-thresholds/{threshold_id}
DELETE /api/v1/metrics/auc-thresholds/{threshold_id}


Rules:
GET    /api/v1/rules
POST   /api/v1/rules
GET    /api/v1/rules/{rule_id}
PUT    /api/v1/rules/{rule_id}
DELETE /api/v1/rules/{rule_id}
PATCH  /api/v1/rules/{rule_id}/activate
PATCH  /api/v1/rules/{rule_id}/inactive
GET    /api/v1/rules/verify-results
PATCH  /api/v1/rules/verify-results/{verify_id}/resolve
PATCH  /api/v1/rules/verify-results/{verify_id}/unresolve

Quality:
GET    /api/v1/quality/summary
GET    /api/v1/quality/results
GET    /api/v1/quality/metadata-results
GET    /api/v1/quality/profiling-results
GET    /api/v1/quality/rule-results
GET    /api/v1/quality/anomaly-results
GET    /api/v1/quality/unresolved-failures

Anomaly:
GET    /api/v1/anomaly/auc-results
GET    /api/v1/anomaly/auc-results/{auc_result_id}
GET    /api/v1/anomaly/tables/{table_id}/auc-timeline
GET    /api/v1/anomaly/auc-results/{auc_result_id}/shap
GET    /api/v1/anomaly/verify-results
PATCH  /api/v1/anomaly/verify-results/{verify_id}/resolve
PATCH  /api/v1/anomaly/verify-results/{verify_id}/unresolve

LightGBM:
GET    /api/v1/lightgbm/parameters
POST   /api/v1/lightgbm/parameters
GET    /api/v1/lightgbm/parameters/{parameter_id}
PUT    /api/v1/lightgbm/parameters/{parameter_id}
DELETE /api/v1/lightgbm/parameters/{parameter_id}
POST   /api/v1/lightgbm/parameters/validate-json
POST   /api/v1/lightgbm/parameters/import-json
GET    /api/v1/lightgbm/tables/{table_id}/parameters

Users:
GET    /api/v1/users
POST   /api/v1/users
GET    /api/v1/users/{user_id}
PUT    /api/v1/users/{user_id}
DELETE /api/v1/users/{user_id}
PATCH  /api/v1/users/{user_id}/activate
PATCH  /api/v1/users/{user_id}/deactivate
PUT    /api/v1/users/{user_id}/roles

Roles:
GET    /api/v1/roles
POST   /api/v1/roles
GET    /api/v1/roles/{role_id}
PUT    /api/v1/roles/{role_id}
DELETE /api/v1/roles/{role_id}
PUT    /api/v1/roles/{role_id}/permissions

Permissions:
GET    /api/v1/permissions
GET    /api/v1/permissions/groups

## Đặc tả giao diện
1. Sidebar
Home
Data Observability
Data Metrics
Data Rules
Data Quality
Settings

2. Header
Avatar

9. Một số trang khác
- Not found
- Loading
- Login