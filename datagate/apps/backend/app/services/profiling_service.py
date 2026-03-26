from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.profiling import ProfileRun, ColumnProfile, ColumnHistogram

class ProfilingService:
    # 1. Lấy danh sách hồ sơ (có phân trang)
    def get_runs(self, db: Session, skip: int = 0, limit: int = 20) -> List[ProfileRun]:
        return db.query(ProfileRun).order_by(desc(ProfileRun.created_at)).offset(skip).limit(limit).all()

    # 2. Lấy chi tiết 1 lần chạy (kèm metrics của các cột)
    def get_run_by_id(self, db: Session, id: int) -> Optional[ProfileRun]:
        return db.query(ProfileRun).filter(ProfileRun.id == id).first()

    # 3. Lấy Histogram cho 1 cột cụ thể
    def get_histogram_by_column(self, db: Session, col_profile_id: int) -> List[ColumnHistogram]:
        return db.query(ColumnHistogram).filter(ColumnHistogram.column_profile_id == col_profile_id).all()

    # 4. Lấy Trend (Biến thiên) của 1 chỉ số của 1 cột qua thời gian
    def get_column_metric_trend(
        self, 
        db: Session, 
        table_name: str, 
        column_name: str, 
        metric: str
    ) -> List[dict]:
        # Truy vấn kết hợp: Lấy giá trị chỉ số từ bảng column_profiles và thời gian từ profile_runs
        results = db.query(
            ProfileRun.id, 
            ProfileRun.created_at, 
            getattr(ColumnProfile, metric)
        ).join(ColumnProfile).filter(
            ProfileRun.table_name == table_name,
            ColumnProfile.column_name == column_name
        ).order_by(ProfileRun.created_at).all()
        
        return [{"run_id": r[0], "created_at": r[1], "value": r[2]} for r in results]

# Khởi tạo instance duy nhất
profiling_service = ProfilingService()
