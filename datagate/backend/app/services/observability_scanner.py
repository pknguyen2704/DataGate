import logging
from sqlalchemy.orm import Session
from app.models.service import Service
from app.models.profiling import ProfilingRun
from app.services.connection_manager import create_trino_connection
from sqlalchemy import text
from datetime import datetime

logger = logging.getLogger(__name__)

class ObservabilityScanner:
    """
    Trụ 1: Data Observability Scanner.
    Queries Trino/Iceberg metadata to check Freshness and Volume without scanning data.
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
                
                # Check for Iceberg snapshots to get freshness
                # SELECT * FROM catalog.schema."table$snapshots" ORDER BY committed_at DESC LIMIT 1
                snapshot_table = f"{full_table_name}$snapshots"
                freshness_query = f'SELECT committed_at FROM {snapshot_table} ORDER BY committed_at DESC LIMIT 1'
                
                # Check for row count from Iceberg properties if possible, 
                # or just do a fast COUNT(*) which in Iceberg is metadata-based usually
                count_query = f'SELECT count(*) FROM {full_table_name}'

                try:
                    # Execute via create_trino_connection
                    conn = create_trino_connection(service.connection_url)
                    cursor = conn.cursor()
                    
                    # 1. Freshness
                    cursor.execute(freshness_query)
                    freshness_res = cursor.fetchone()
                    last_modified = freshness_res[0] if freshness_res else None
                    
                    # 2. Volume
                    cursor.execute(count_query)
                    count_res = cursor.fetchone()
                    row_count = count_res[0] if count_res else 0
                    
                    # Save to Profiling history as a "light" run
                    new_run = ProfilingRun(
                        table_name=full_table_name,
                        batch_time=datetime.now(),
                        partition_key="observability_scan",
                        num_records=row_count,
                        raw_json={"type": "observability", "last_modified": str(last_modified)}
                    )
                    db.add(new_run)
                    
                    results.append({
                        "table": full_table_name,
                        "freshness": last_modified,
                        "row_count": row_count,
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
