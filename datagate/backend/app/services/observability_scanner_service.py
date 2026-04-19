import logging
from sqlalchemy.orm import Session
from app.models.service_model import Service
from app.services.connection_manager_service import create_connection
from sqlalchemy import text
from datetime import datetime

logger = logging.getLogger(__name__)

class ObservabilityScanner:
    """
    Trụ 1: Data Observability Scanner.
    Nhiệm vụ: Truy vấn dữ liệu siêu (Metadata) từ Trino/Iceberg (bảng $snapshots, $files)
    để lấy thông tin về thời gian cập nhật (Freshness) và dung lượng (Volume).
    Lưu ý: Chức năng này KHÔNG truy vấn vào dữ liệu thực (các hàng/cột của bảng) 
    nên diễn ra cực kỳ nhanh và không gây tốn tài nguyên hệ thống.
    """

    @staticmethod
    def scan_service(db: Session, service_id: int):
        service = db.query(Service).filter(Service.id == service_id).first()
        if not service:
            return {"status": "error", "message": "Service not found"}

        if service.service_type.lower() != "trino":
            return {"status": "error", "message": "Observability scan only supported for Trino/Iceberg"}

        try:
            # We assume the integrated_tables are in format 'catalog.schema.table'
            results = []
            for full_table_name in service.integrated_tables:
                # Query Trino for table metadata
                # Note: Trino's system connector or Iceberg metadata tables can be used
                
                # Query Iceberg Metadata via Trino system tables
                snapshot_table = f"{full_table_name}$snapshots"
                files_table = f"{full_table_name}$files"
                
                # 1. Query Freshness (Latest Snapshot)
                freshness_query = f'SELECT committed_at, snapshot_id FROM "{snapshot_table}" ORDER BY committed_at DESC LIMIT 1'
                
                # 2. Query Volume & Size (from Metadata files)
                # content = 0 ensures we only count data files, not deletes
                stats_query = f'SELECT SUM(record_count), SUM(file_size_in_bytes) FROM "{files_table}" WHERE content = 0'

                try:
                    # Execute via create_trino_connection
                    conn = create_connection(service.connection_url)
                    cursor = conn.cursor()
                    
                    # 1. Fetch Freshness
                    cursor.execute(freshness_query)
                    freshness_res = cursor.fetchone()
                    last_modified = freshness_res[0] if freshness_res else None
                    latest_snapshot_id = freshness_res[1] if freshness_res else None
                    
                    # 2. Fetch Volume & Size
                    cursor.execute(stats_query)
                    stats_res = cursor.fetchone()
                    row_count = stats_res[0] if stats_res else 0
                    total_bytes = stats_res[1] if stats_res else 0
                    
                    # Save to DGObservabilitySnapshot (Pillar 1)
                    from app.models.observability_model import DGObservabilitySnapshot
                    snapshot = DGObservabilitySnapshot(
                        table_name=full_table_name,
                        snapshot_time=datetime.now(),
                        last_updated_time=last_modified,
                        total_records=row_count,
                        total_size=total_bytes
                    )
                    db.add(snapshot)
                    
                    results.append({
                        "table": full_table_name,
                        "freshness": last_modified,
                        "row_count": row_count,
                        "total_bytes": total_bytes,
                        "status": "success"
                    })
                    
                except Exception as e:
                    logger.error(f"Error scanning table {full_table_name}: {e}")
                    results.append({
                        "table": full_table_name,
                        "status": "error",
                        "error": str(e)
                    })

            db.commit()
            return {"status": "success", "results": results}

        except Exception as e:
            logger.error(f"Scanner fatal error: {e}")
            return {"status": "error", "message": str(e)}
