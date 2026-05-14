# Tổng quan giao diện   
## Đăng nhập
- Người dùng có thể thực hiện đăng nhập vào hệ thống bằng username/email và mật khẩu
- Có các chức năng để remember me
## Sidebar
- Nav đến các chức năng chính
+ Home: Trang chủ
+ Data Assets: Trang chuyên về các thông tin của bảng
+ Settings: Cài đặt của hệ thống
## Home
- Tổng quan các thông tin bao gồm
+ Số lượng bảng đang được tích hợp theo dõi
+ Tổng đang có bao nhiêu pass/fail (warning/critical) ở các bảng trên các bảng ghi _verify.py
## Data Assets
- Danh sách các bảng đang được tích hợp/Quản lý chất lượng dữ liệu
+ Có thể filter theo Connection/Catalog/Schema
- Sau khi chọn một bảng, sẽ theo dõi các tab cụ thể của bảng đó
### Observability
- Tích hợp bảng Grafana đã được thiết kế vào
- Mặc định là truy vấn thời gian từ last processing_datehour và lấy ngược lại 2 batch
### Metrics
- Giao diện bảng để quản lý các ngưỡng kiểm tra với các thông số do người dùng cài đặt
+ Các ngưỡng có thể chỉnh sửa/xóa 
+ Có form thêm ngưỡng mới
#### Đối với metadata:
++ metric
++ Min
++ Max
++ Severity
++ Status
++ Created_by
++ Description
++ Created_by
++ Last modified
#### Đối với profiling:
++ column
++ metric
++ Min
++ Max
++ Severity
++ Status
++ Created_by
++ Description
++ Created_by
++ Last modified
#### Đối với anomaly detection: (Chỉ những schema/bảng sử dụng chức năng này mới hiện tab này)
++ auc_threshold
++ Severity
++ Status
++ Created_by
++ Description
++ Created_by
++ Last modified

### Rules
- Giao diện quản lý, theo dõi các rule do hệ thống sinh ra và có khả năng thêm rule do người dùng định nghĩa
- Các rule hiện theo
+ Column, Constraint, Source, Severity, status, Frequency, Action, created_by, last_modified_by
++ Với source: system thì hiển thị created by: system luôn
- Có form để thêm rule
### Data quality
- Giao diện theo dõi kết quả Data quality theo
+ Metadata
+ Profile
+ Rules
+ Anomaly detection
++ hiển thị Model config đang áp dụng để ra kết quả đó
++ Hiển thị kết quả AUC và SHAP

- Có filter theo processing_date_hour để lấy kết quả của một processing_date_hour đó 
- Có một cột để cập nhật trạng thái là đã xử lý hay chưa
- Lọc theo bảng, schema, processing_date_hour, status, severity
- Xem kết quả metadata metrics verify
- Xem kết quả profiling metrics verify
- Xem kết quả rule verify
- Xem kết quả anomaly detection
- Cập nhật trạng thái đã xử lý/chưa xử lý
- Xem chi tiết lỗi và thông điệp kiểm tra
## Setting
### Platform Connection
- Quản lý thông tin kết nối đến nền tảng dữ liệu lớn. Mỗi connection có thể bao gồm nhiều bảng dữ liệu được hệ thống theo dõi. (Cho phép cập nhật thông tin connection, có thể test connection, có thể thêm hoặc loại bỏ các bảng muốn hệ thống này quản lý)
- Có thể tạo connection (Có form tạo connection)
### Model Configuration
+ Hiển thị dạng bảng (dòng dữ liệu là mỗi bảng còn các cột là các siêu tham số)
+ Có thể chỉnh sửa, update, có tính năng để upload Json, tự động mapping
### Users
- Quản lý quyền hạn
+ Role:
++ Admin:
+++ Có tất cả các quyền
++ Data engineer:
+++ Không được chỉnh sửa platform connection
++ Data Analyst: Data Analyst
+++ Không được chỉnh sửa platform connection
+++ Không được chỉnh sửa các ngưỡng
- Quản lý người dùng (Thông tin, role,...)
## Phân quyền
Bảng phân quyền
| Nhóm chức năng                    |                                        Quyền thao tác | Admin | Data Engineer | Data Analyst | Ghi chú                                                                                 |
| --------------------------------- | ----------------------------------------------------: | :---: | :-----------: | :----------: | --------------------------------------------------------------------------------------- |
| Đăng nhập hệ thống                |                                     Truy cập hệ thống |   Có  |       Có      |      Có      | Tất cả người dùng phải đăng nhập trước khi sử dụng hệ thống.                            |
| Phân quyền người dùng             |      Xem, thêm, sửa, xóa người dùng, vai trò và quyền |   Có  |     Không     |     Không    | Chỉ Admin được quản lý phân quyền người dùng.                                           |
| Quản lý kết nối nền tảng dữ liệu  |                                 Xem thông tin kết nối |   Có  |       Có      |     Không    | Data Engineer được xem để phục vụ vận hành; Data Analyst không cần truy cập connection. |
| Quản lý kết nối nền tảng dữ liệu  |                        Thêm, sửa, vô hiệu hóa kết nối |   Có  |     Không     |     Không    | Chỉ Admin được thay đổi platform connection.                                            |
| Quản lý tham số mô hình           |                                   Xem tham số mô hình |   Có  |       Có      |      Có      | Các vai trò có thể xem để hiểu cấu hình phát hiện bất thường.                           |
| Quản lý tham số mô hình           |                        Thêm, sửa, xóa tham số mô hình |   Có  |       Có      |     Không    | Tham số mô hình là cấu hình kỹ thuật, chỉ Admin và Data Engineer được chỉnh sửa.        |
| Xem siêu dữ liệu và hồ sơ dữ liệu |              Xem metadata, profiling và lịch sử batch |   Có  |       Có      |      Có      | Cả ba vai trò đều có thể theo dõi trạng thái dữ liệu.                                   |
| Quản lý ngưỡng cảnh báo           |                                   Xem ngưỡng cảnh báo |   Có  |       Có      |      Có      | Data Analyst được xem để hiểu tiêu chí đánh giá chất lượng dữ liệu.                     |
| Quản lý ngưỡng cảnh báo           |                        Thêm, sửa, xóa ngưỡng cảnh báo |   Có  |       Có      |     Không    | Ngưỡng là cấu hình vận hành, chỉ Admin và Data Engineer được chỉnh sửa.                 |
| Quản lý luật dữ liệu              |             Xem, thêm, sửa rule nháp và gửi phê duyệt |   Có  |       Có      |      Có      | Data Analyst được đề xuất và chỉnh sửa luật ở trạng thái nháp.                          |
| Quản lý luật dữ liệu              |                Phê duyệt, bật/tắt và xóa luật dữ liệu |   Có  |       Có      |     Không    | Các thao tác này ảnh hưởng trực tiếp đến quy trình kiểm tra chất lượng dữ liệu.         |
| Quản lý chất lượng dữ liệu        | Xem kết quả kiểm tra và chi tiết lỗi warning/critical |   Có  |       Có      |      Có      | Cả ba vai trò đều có thể xem kết quả để giám sát và phân tích nguyên nhân.              |
| Quản lý chất lượng dữ liệu        |  Cập nhật trạng thái xử lý kết quả chất lượng dữ liệu |   Có  |       Có      |     Không    | Thao tác resolve là thao tác vận hành, giới hạn cho Admin và Data Engineer.             |
| Dashboard/Grafana                 |                                Xem dashboard giám sát |   Có  |       Có      |      Có      | Chức năng phục vụ quan sát tổng quan chất lượng dữ liệu.                                |



# API

Dưới đây là bộ API backend nên có cho giao diện DataGate version mới, dựa theo tài liệu bạn cung cấp về các màn hình Home, Data Assets, Observability, Metrics, Rules, Data Quality, Settings và phân quyền người dùng. 

## 1. Nhóm API xác thực và người dùng hiện tại

| Method | Endpoint                     | Mục đích                                            | Quyền         |
| ------ | ---------------------------- | --------------------------------------------------- | ------------- |
| POST   | `/api/v1/auth/login`         | Đăng nhập bằng username/email và mật khẩu           | Public        |
| POST   | `/api/v1/auth/logout`        | Đăng xuất                                           | Authenticated |
| GET    | `/api/v1/auth/me`            | Lấy thông tin người dùng hiện tại, role, permission | Authenticated |
| POST   | `/api/v1/auth/refresh-token` | Làm mới access token nếu có dùng refresh token      | Authenticated |

Request đăng nhập nên có:

```json
{
  "username_or_email": "admin@datagate.com",
  "password": "password",
  "remember_me": true
}
```

Response nên trả về:

```json
{
  "access_token": "...",
  "token_type": "bearer",
  "user": {
    "id": "...",
    "username": "admin",
    "email": "admin@datagate.com",
    "roles": ["Admin"],
    "permissions": ["connection:view", "connection:manage"]
  }
}
```

## 2. Nhóm API Home

| Method | Endpoint                              | Mục đích                                                            | Quyền                              |
| ------ | ------------------------------------- | ------------------------------------------------------------------- | ---------------------------------- |
| GET    | `/api/v1/home/summary`                | Lấy tổng quan số bảng đang theo dõi, số pass/fail, warning/critical | Admin, Data Engineer, Data Analyst |

Query gợi ý:

```text
GET /api/v1/home/summary?connection_id=&catalog_name=&schema_name=&from_time=&to_time=
```

Response gợi ý:

```json
{
  "total_tables": 24,
  "total_pass": 120,
  "total_fail": 15,
  "warning_fail": 10,
  "critical_fail": 5,
  "unresolved_alerts": 8
}
```

## 3. Nhóm API Data Assets / Tables

| Method | Endpoint                                                 | Mục đích                               | Quyền                              |
| ------ | -------------------------------------------------------- | -------------------------------------- | ---------------------------------- |
| GET    | `/api/v1/data-assets/tables`                             | Lấy danh sách bảng đang được quản lý   | Admin, Data Engineer, Data Analyst |
| GET    | `/api/v1/data-assets/tables/{table_id}`                  | Lấy thông tin chi tiết một bảng        | Admin, Data Engineer, Data Analyst |
| GET    | `/api/v1/data-assets/tables/{table_id}/processing-hours` | Lấy danh sách thời điểm xử lý của bảng | Admin, Data Engineer, Data Analyst |



Query filter:

```text
GET /api/v1/data-assets/tables?connection_id=&catalog_name=&schema_name=&is_active=true&page=1&page_size=20
```

Response gợi ý:

```json
{
  "items": [
    {
      "id": "...",
      "connection_id": "...",
      "catalog_name": "iceberg",
      "schema_name": "silver",
      "table_name": "yellow_tripdata",
      "is_active": true,
      "latest_processing_date_hour": "2025-01-15 12:00:00"
    }
  ],
  "total": 1
}
```

## 4. Nhóm API Observability / Grafana

Vì giao diện Observability nhúng Grafana bằng iframe, backend chỉ cần trả về cấu hình dashboard và URL đã gắn biến lọc.

| Method | Endpoint                                                     | Mục đích                                                                      | Quyền                              |
| ------ | ------------------------------------------------------------ | ----------------------------------------------------------------------------- | ---------------------------------- |
| GET    | `/api/v1/observability/tables/{table_id}/dashboard`          | Lấy URL dashboard Grafana cho một bảng                                        | Admin, Data Engineer, Data Analyst |
| GET    | `/api/v1/observability/tables/{table_id}/default-time-range` | Lấy khoảng thời gian mặc định, ví dụ last processing_date_hour và lùi 2 batch | Admin, Data Engineer, Data Analyst |

Query gợi ý:

```text
GET /api/v1/observability/tables/{table_id}/dashboard?from_processing_date_hour=&to_processing_date_hour=
```

Response gợi ý:

```json
{
  "dashboard_url": "https://grafana.example.com/d/xxx?var-table=yellow_tripdata&from=...&to=...",
  "iframe_allowed": true,
  "default_from": "2025-01-14 12:00:00",
  "default_to": "2025-01-15 12:00:00"
}
```

## 5. Nhóm API Metrics / Ngưỡng kiểm tra

Nên tách riêng 3 nhóm: metadata threshold, profiling threshold và anomaly threshold.

### 5.1. Metadata thresholds

| Method | Endpoint                                             | Mục đích                             | Quyền                              |
| ------ | ---------------------------------------------------- | ------------------------------------ | ---------------------------------- |
| GET    | `/api/v1/metrics/metadata-thresholds`                | Lấy danh sách ngưỡng metadata        | Admin, Data Engineer, Data Analyst |
| POST   | `/api/v1/metrics/metadata-thresholds`                | Tạo ngưỡng metadata                  | Admin, Data Engineer               |
| GET    | `/api/v1/metrics/metadata-thresholds/{threshold_id}` | Lấy chi tiết ngưỡng metadata         | Admin, Data Engineer, Data Analyst |
| PATCH  | `/api/v1/metrics/metadata-thresholds/{threshold_id}` | Cập nhật ngưỡng metadata             | Admin, Data Engineer               |
| DELETE | `/api/v1/metrics/metadata-thresholds/{threshold_id}` | Xóa hoặc vô hiệu hóa ngưỡng metadata | Admin, Data Engineer               |

Request tạo ngưỡng metadata:

```json
{
  "table_id": "...",
  "metric_name": "batch_added_rows",
  "min_threshold": 1000,
  "max_threshold": 100000,
  "severity_level": "warning",
  "is_active": true,
  "description": "Kiểm tra số bản ghi được thêm trong batch"
}
```

### 5.2. Profiling thresholds

| Method | Endpoint                                              | Mục đích                              | Quyền                              |
| ------ | ----------------------------------------------------- | ------------------------------------- | ---------------------------------- |
| GET    | `/api/v1/metrics/profiling-thresholds`                | Lấy danh sách ngưỡng profiling        | Admin, Data Engineer, Data Analyst |
| POST   | `/api/v1/metrics/profiling-thresholds`                | Tạo ngưỡng profiling                  | Admin, Data Engineer               |
| GET    | `/api/v1/metrics/profiling-thresholds/{threshold_id}` | Lấy chi tiết ngưỡng profiling         | Admin, Data Engineer, Data Analyst |
| PATCH  | `/api/v1/metrics/profiling-thresholds/{threshold_id}` | Cập nhật ngưỡng profiling             | Admin, Data Engineer               |
| DELETE | `/api/v1/metrics/profiling-thresholds/{threshold_id}` | Xóa hoặc vô hiệu hóa ngưỡng profiling | Admin, Data Engineer               |

Request tạo ngưỡng profiling:

```json
{
  "table_id": "...",
  "column_name": "trip_distance",
  "metric_name": "minimum",
  "min_threshold": 0,
  "max_threshold": null,
  "severity_level": "critical",
  "is_active": true,
  "description": "Khoảng cách chuyến đi không được âm"
}
```

### 5.3. AUC / anomaly thresholds

| Method | Endpoint                                            | Mục đích                        | Quyền                              |
| ------ | --------------------------------------------------- | ------------------------------- | ---------------------------------- |
| GET    | `/api/v1/metrics/anomaly-thresholds`                | Lấy danh sách ngưỡng AUC        | Admin, Data Engineer, Data Analyst |
| POST   | `/api/v1/metrics/anomaly-thresholds`                | Tạo ngưỡng AUC                  | Admin, Data Engineer               |
| PATCH  | `/api/v1/metrics/anomaly-thresholds/{threshold_id}` | Cập nhật ngưỡng AUC             | Admin, Data Engineer               |
| DELETE | `/api/v1/metrics/anomaly-thresholds/{threshold_id}` | Xóa hoặc vô hiệu hóa ngưỡng AUC | Admin, Data Engineer               |

Request gợi ý:

```json
{
  "lightgbm_parameter_id": "...",
  "auc_threshold": 0.75,
  "severity_level": "warning",
  "description": "Cảnh báo khi AUC vượt ngưỡng"
}
```

## 6. Nhóm API Rules

| Method | Endpoint                             | Mục đích                         | Quyền                              |
| ------ | ------------------------------------ | -------------------------------- | ---------------------------------- |
| GET    | `/api/v1/rules`                      | Lấy danh sách luật dữ liệu       | Admin, Data Engineer, Data Analyst |
| POST   | `/api/v1/rules`                      | Tạo luật thủ công                | Admin, Data Engineer, Data Analyst |
| GET    | `/api/v1/rules/{rule_id}`            | Xem chi tiết luật                | Admin, Data Engineer, Data Analyst |
| PATCH  | `/api/v1/rules/{rule_id}`            | Cập nhật nội dung luật           | Admin, Data Engineer, Data Analyst |
| POST   | `/api/v1/rules/{rule_id}/approve`    | Phê duyệt rule do hệ thống sinh  | Admin, Data Engineer               |
| POST   | `/api/v1/rules/{rule_id}/deactivate` | Vô hiệu hóa rule                 | Admin, Data Engineer               |
| DELETE | `/api/v1/rules/{rule_id}`            | Xóa rule nếu cho phép xóa vật lý | Admin, Data Engineer               |

Query filter:

```text
GET /api/v1/rules?table_id=&column_name=&source=&status=&severity_level=&page=1&page_size=20
```

Request tạo rule:

```json
{
  "table_id": "...",
  "column_name": "total_amount",
  "constraint_name": "isNonNegative",
  "code_for_constraint": ".isNonNegative(\"total_amount\")",
  "severity_level": "critical",
  "description": "Tổng tiền không được âm",
  "rule_description": "Kiểm tra giá trị total_amount phải lớn hơn hoặc bằng 0"
}
```

Lưu ý quyền: Data Analyst được tạo/sửa nội dung rule, nhưng không được xóa hoặc vô hiệu hóa rule quan trọng.

## 7. Nhóm API Data Quality Results

Đây là nhóm API cho màn hình Data Quality. Nên tách API tổng hợp và API chi tiết theo từng loại kết quả.

### 7.1. API tổng hợp

| Method | Endpoint                               | Mục đích                                            | Quyền                              |
| ------ | -------------------------------------- | --------------------------------------------------- | ---------------------------------- |
| GET    | `/api/v1/data-quality/results`         | Lấy danh sách kết quả kiểm tra tổng hợp             | Admin, Data Engineer, Data Analyst |
| GET    | `/api/v1/data-quality/results/summary` | Lấy tổng số pass/fail, warning/critical theo filter | Admin, Data Engineer, Data Analyst |

Query filter:

```text
GET /api/v1/data-quality/results?table_id=&schema_name=&processing_date_hour=&status=&severity_level=&result_type=
```

Trong đó result_type có thể là:

```text
metadata_metric
profiling_metric
rule
anomaly
```

### 7.2. Metadata metric verify

| Method | Endpoint                                                    | Mục đích                          | Quyền                              |
| ------ | ----------------------------------------------------------- | --------------------------------- | ---------------------------------- |
| GET    | `/api/v1/data-quality/metadata-results`                     | Xem kết quả kiểm tra metadata     | Admin, Data Engineer, Data Analyst |
| GET    | `/api/v1/data-quality/metadata-results/{result_id}`         | Xem chi tiết một kết quả metadata | Admin, Data Engineer, Data Analyst |
| PATCH  | `/api/v1/data-quality/metadata-results/{result_id}/resolve` | Cập nhật đã xử lý/chưa xử lý      | Admin, Data Engineer               |

### 7.3. Profiling metric verify

| Method | Endpoint                                                     | Mục đích                           | Quyền                              |
| ------ | ------------------------------------------------------------ | ---------------------------------- | ---------------------------------- |
| GET    | `/api/v1/data-quality/profiling-results`                     | Xem kết quả kiểm tra profiling     | Admin, Data Engineer, Data Analyst |
| GET    | `/api/v1/data-quality/profiling-results/{result_id}`         | Xem chi tiết một kết quả profiling | Admin, Data Engineer, Data Analyst |
| PATCH  | `/api/v1/data-quality/profiling-results/{result_id}/resolve` | Cập nhật đã xử lý/chưa xử lý       | Admin, Data Engineer               |

### 7.4. Rule verify

| Method | Endpoint                                                | Mục đích                     | Quyền                              |
| ------ | ------------------------------------------------------- | ---------------------------- | ---------------------------------- |
| GET    | `/api/v1/data-quality/rule-results`                     | Xem kết quả kiểm tra rule    | Admin, Data Engineer, Data Analyst |
| GET    | `/api/v1/data-quality/rule-results/{result_id}`         | Xem chi tiết kết quả rule    | Admin, Data Engineer, Data Analyst |
| PATCH  | `/api/v1/data-quality/rule-results/{result_id}/resolve` | Cập nhật đã xử lý/chưa xử lý | Admin, Data Engineer               |

### 7.5. Anomaly detection results

| Method | Endpoint                                                   | Mục đích                                  | Quyền                              |
| ------ | ---------------------------------------------------------- | ----------------------------------------- | ---------------------------------- |
| GET    | `/api/v1/data-quality/anomaly-results`                     | Xem kết quả anomaly detection             | Admin, Data Engineer, Data Analyst |
| GET    | `/api/v1/data-quality/anomaly-results/{result_id}`         | Xem chi tiết AUC, threshold, model config | Admin, Data Engineer, Data Analyst |
| GET    | `/api/v1/data-quality/anomaly-results/{result_id}/shap`    | Lấy danh sách SHAP feature importance     | Admin, Data Engineer, Data Analyst |
| PATCH  | `/api/v1/data-quality/anomaly-results/{result_id}/resolve` | Cập nhật đã xử lý/chưa xử lý              | Admin, Data Engineer               |

Request cập nhật trạng thái xử lý:

```json
{
  "is_resolved": true
}
```

Response chi tiết anomaly:

```json
{
  "id": "...",
  "table_id": "...",
  "processing_date_hour": "2025-01-15 12:00:00",
  "auc_score": 0.706912,
  "auc_threshold": 0.75,
  "status": "pass",
  "severity_level": "warning",
  "model_config": {
    "learning_rate": 0.0172556773,
    "num_leaves": 31,
    "max_depth": 6,
    "min_data_in_leaf": 200
  },
  "shap_top_features": [
    {
      "feature_name": "extra",
      "shap_score": 0.4728,
      "shap_rank": 1
    }
  ]
}
```

## 8. Nhóm API Platform Connection

| Method | Endpoint                                                                 | Mục đích                          | Quyền                              |
| ------ | ------------------------------------------------------------------------ | --------------------------------- | ---------------------------------- |
| GET    | `/api/v1/settings/connections`                                           | Lấy danh sách connection          | Admin, Data Engineer, Data Analyst |
| POST   | `/api/v1/settings/connections`                                           | Tạo connection mới                | Admin                              |
| GET    | `/api/v1/settings/connections/{connection_id}`                           | Xem chi tiết connection           | Admin, Data Engineer, Data Analyst |
| PATCH  | `/api/v1/settings/connections/{connection_id}`                           | Cập nhật connection               | Admin                              |
| POST   | `/api/v1/settings/connections/{connection_id}/test`                      | Test connection                   | Admin                              |
| POST   | `/api/v1/settings/connections/{connection_id}/deactivate`                | Vô hiệu hóa connection            | Admin                              |
| GET    | `/api/v1/settings/connections/{connection_id}/discover-tables`           | Quét danh sách bảng từ connection | Admin                              |
| POST   | `/api/v1/settings/connections/{connection_id}/managed-tables`            | Thêm bảng vào phạm vi quản lý     | Admin                              |
| DELETE | `/api/v1/settings/connections/{connection_id}/managed-tables/{table_id}` | Loại bảng khỏi phạm vi quản lý    | Admin                              |

Request tạo connection:

```json
{
  "connection_name": "Local Lakehouse",
  "description": "Kết nối lakehouse thực nghiệm",
  "trino_host": "trino",
  "trino_port": 8080,
  "trino_user": "admin",
  "trino_password": "...",
  "iceberg_rest_url": "http://iceberg-rest:8181",
  "iceberg_catalog_name": "iceberg",
  "iceberg_warehouse": "s3://warehouse",
  "minio_endpoint_url": "http://minio:9000",
  "minio_access_key": "...",
  "minio_secret_key": "..."
}
```

## 9. Nhóm API Model Configuration

| Method | Endpoint                                     | Mục đích                                | Quyền                              |
| ------ | -------------------------------------------- | --------------------------------------- | ---------------------------------- |
| GET    | `/api/v1/settings/model-configs`             | Lấy danh sách tham số mô hình theo bảng | Admin, Data Engineer, Data Analyst |
| POST   | `/api/v1/settings/model-configs`             | Tạo cấu hình mô hình cho bảng           | Admin, Data Engineer               |
| GET    | `/api/v1/settings/model-configs/{config_id}` | Xem chi tiết cấu hình mô hình           | Admin, Data Engineer, Data Analyst |
| PATCH  | `/api/v1/settings/model-configs/{config_id}` | Cập nhật tham số mô hình                | Admin, Data Engineer               |
| DELETE | `/api/v1/settings/model-configs/{config_id}` | Xóa cấu hình mô hình                    | Admin, Data Engineer               |
| POST   | `/api/v1/settings/model-configs/upload-json` | Upload JSON và tự động mapping tham số  | Admin, Data Engineer               |
| GET    | `/api/v1/settings/model-configs/template`    | Tải template JSON tham số mô hình       | Admin, Data Engineer               |

Request tạo model config:

```json
{
  "table_id": "...",
  "learning_rate": 0.0172556773,
  "num_leaves": 31,
  "max_depth": 6,
  "min_data_in_leaf": 200,
  "bagging_fraction": 0.7137280259,
  "bagging_freq": 3,
  "feature_fraction": 0.7302029089,
  "lambda_l1": 0.0208734182,
  "lambda_l2": 0.0000001638,
  "min_gain_to_split": 0.7076749167,
  "max_bin": 127,
  "num_iterations": 2000
}
```

## 10. Nhóm API Users / Roles / Permissions

### 10.1. Users

| Method | Endpoint                                      | Mục đích                      | Quyền |
| ------ | --------------------------------------------- | ----------------------------- | ----- |
| GET    | `/api/v1/settings/users`                      | Lấy danh sách người dùng      | Admin |
| POST   | `/api/v1/settings/users`                      | Tạo người dùng                | Admin |
| GET    | `/api/v1/settings/users/{user_id}`            | Xem chi tiết người dùng       | Admin |
| PATCH  | `/api/v1/settings/users/{user_id}`            | Cập nhật thông tin người dùng | Admin |
| POST   | `/api/v1/settings/users/{user_id}/activate`   | Kích hoạt người dùng          | Admin |
| POST   | `/api/v1/settings/users/{user_id}/deactivate` | Vô hiệu hóa người dùng        | Admin |
| PATCH  | `/api/v1/settings/users/{user_id}/roles`      | Gán role cho người dùng       | Admin |
| PATCH  | `/api/v1/settings/users/{user_id}/password`   | Đổi mật khẩu người dùng       | Admin |

### 10.2. Roles

| Method | Endpoint                                       | Mục đích                               | Quyền |
| ------ | ---------------------------------------------- | -------------------------------------- | ----- |
| GET    | `/api/v1/settings/roles`                       | Lấy danh sách vai trò                  | Admin |
| POST   | `/api/v1/settings/roles`                       | Tạo vai trò                            | Admin |
| GET    | `/api/v1/settings/roles/{role_id}`             | Xem chi tiết vai trò                   | Admin |
| PATCH  | `/api/v1/settings/roles/{role_id}`             | Cập nhật vai trò                       | Admin |
| DELETE | `/api/v1/settings/roles/{role_id}`             | Xóa vai trò nếu không phải system role | Admin |
| PATCH  | `/api/v1/settings/roles/{role_id}/permissions` | Gán quyền cho vai trò                  | Admin |

### 10.3. Permissions

| Method | Endpoint                               | Mục đích                                     | Quyền |
| ------ | -------------------------------------- | -------------------------------------------- | ----- |
| GET    | `/api/v1/settings/permissions`         | Lấy danh sách permission                     | Admin |
| GET    | `/api/v1/settings/permissions/grouped` | Lấy danh sách permission theo nhóm chức năng | Admin |

## 11. Danh sách permission nên định nghĩa

Bạn nên định nghĩa permission theo dạng code để dễ kiểm tra ở backend:

| Permission code           | Ý nghĩa                                     |
| ------------------------- | ------------------------------------------- |
| `auth:login`              | Đăng nhập hệ thống                          |
| `home:view`               | Xem trang Home                              |
| `table:view`              | Xem danh sách bảng                          |
| `connection:view`         | Xem connection                              |
| `connection:manage`       | Tạo, sửa, vô hiệu hóa connection            |
| `dashboard:view`          | Xem dashboard Grafana                       |
| `metric_threshold:view`   | Xem ngưỡng cảnh báo                         |
| `metric_threshold:manage` | Tạo, sửa, xóa ngưỡng cảnh báo               |
| `rule:view`               | Xem luật dữ liệu                            |
| `rule:create_update`      | Tạo, sửa luật dữ liệu                       |
| `rule:approve`            | Phê duyệt luật hệ thống                     |
| `rule:deactivate`         | Vô hiệu hóa luật                            |
| `quality_result:view`     | Xem kết quả kiểm tra chất lượng             |
| `quality_result:resolve`  | Cập nhật trạng thái đã xử lý                |
| `model_config:view`       | Xem tham số mô hình                         |
| `model_config:manage`     | Tạo, sửa, xóa tham số mô hình               |
| `user:view`               | Xem người dùng, role, permission            |
| `user:manage`             | Thêm, sửa, xóa người dùng, role, permission |

## 12. Mapping role với permission

| Role          | Permission chính                                                                                                              |
| ------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| Admin         | Có tất cả quyền                                                                                                               |
| Data Engineer | Xem connection, xem dashboard, xem bảng, quản lý model config, quản lý threshold, quản lý rule, xem và resolve quality result |
| Data Analyst  | Xem connection, xem dashboard, xem bảng, xem threshold, xem quality result, quản lý rule                                      |

## 13. Bộ router backend đề xuất

Nếu bạn dùng FastAPI, có thể chia router như sau:

```text
app/api/v1/routes/auth.py
app/api/v1/routes/home.py
app/api/v1/routes/data_assets.py
app/api/v1/routes/observability.py
app/api/v1/routes/metrics.py
app/api/v1/routes/rules.py
app/api/v1/routes/data_quality.py
app/api/v1/routes/connections.py
app/api/v1/routes/model_configs.py
app/api/v1/routes/users.py
app/api/v1/routes/roles.py
app/api/v1/routes/permissions.py
```

Cách chia này bám theo sidebar và nghiệp vụ, nhưng vẫn tách rõ cấu hình, kết quả và phân quyền.

