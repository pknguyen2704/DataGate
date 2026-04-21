-- Cài đặt Extension TimescaleDB (Yêu cầu tài khoản superuser hoặc quyền cài extension)
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- Chuyển đổi các bảng Observability thành Hypertables để tối ưu truy vấn chuỗi thời gian

-- 1. Snapshot History
SELECT create_hypertable('observability_snapshots', 'snapshot_time', if_not_exists => TRUE);

-- 2. Volume Timeseries (Dữ liệu cho Prophet)
SELECT create_hypertable('observability_volume_ts', 'dt', if_not_exists => TRUE);

-- 3. Schema History
SELECT create_hypertable('observability_schema', 'snapshot_time', if_not_exists => TRUE);

-- 4. Incidents History
SELECT create_hypertable('observability_incidents', 'detected_at', if_not_exists => TRUE);

-- Thiết lập chính sách nén (Compression Policy) - Tùy chọn để tiết kiệm dung lượng
-- ALTER TABLE observability_snapshots SET (timescaledb.compress, timescaledb.compress_segmentby = 'table_name');
-- SELECT add_compression_policy('observability_snapshots', INTERVAL '30 days');

-- Thiết lập chính sách xóa dữ liệu cũ (Retention Policy) - Ví dụ giữ lại 90 ngày
-- SELECT add_retention_policy('observability_snapshots', INTERVAL '90 days');
