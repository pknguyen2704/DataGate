from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.services.profiling_service import profiling_service
from app.schemas import profiling as schemas

router = APIRouter(prefix="/profiling", tags=["profiling"])

# 1. API: Danh sách toàn bộ lịch sử chạy Profiling
@router.get("/runs", response_model=List[schemas.ProfileRunBase])
def read_runs(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 20
) -> Any:
    """Lấy danh sách các lần thực hiện Profile dữ liệu."""
    return profiling_service.get_runs(db, skip=skip, limit=limit)

# 2. API: Xem chi tiết 1 lần chạy (kèm thông tin tất cả các cột)
@router.get("/runs/{run_id}", response_model=schemas.ProfileRunDetail)
def read_run(
    run_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """Xem chi tiết 1 lần chạy dữ liệu bao gồm danh sách các cột."""
    run = profiling_service.get_run_by_id(db, id=run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Không tìm thấy bản ghi profiling")
    return run

# 3. API: Lấy biểu đồ (Histogram) của một cột cụ thể
@router.get("/column/{col_profile_id}/histogram", response_model=List[schemas.HistogramItem])
def read_histogram(
    col_profile_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """Lấy dữ liệu Histogram (biểu đồ cột) cho một cột xác định."""
    return profiling_service.get_histogram_by_column(db, col_profile_id=col_profile_id)

# 4. API: Lấy Trend biế thiên của 1 cột qua thời gian (Vẽ biểu đồ đường)
@router.get("/trend", response_model=List[schemas.MetricTrendItem])
def read_trend(
    table: str,
    column: str,
    metric: str = Query(..., description="Chỉ số: completeness, mean, maximum, minimum, std_dev..."),
    db: Session = Depends(get_db)
) -> Any:
    """Lấy dữ liệu thay đổi của 1 chỉ số chất lượng qua các mốc thời gian (Vẽ Trend)."""
    return profiling_service.get_column_metric_trend(db, table, column, metric)
