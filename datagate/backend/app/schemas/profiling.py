from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import datetime

# Histogram item
class HistogramItem(BaseModel):
    bin_value: str
    absolute_count: int
    ratio: float
    model_config = ConfigDict(from_attributes=True)

# Cơ bản của 1 cột (Metrics)
class ColumnProfileBase(BaseModel):
    id: int
    column_name: str
    data_type: Optional[str]
    completeness: float
    approx_distinct_values: int
    mean: Optional[float]
    maximum: Optional[float]
    minimum: Optional[float]
    sum: Optional[float]
    std_dev: Optional[float]
    model_config = ConfigDict(from_attributes=True)

# Chi tiết 1 cột (kèm biểu đồ)
class ColumnProfileWithHist(ColumnProfileBase):
    histograms: List[HistogramItem]

# Cơ bản của 1 lần chạy (Summary)
class ProfileRunBase(BaseModel):
    id: int
    catalog: str
    namespace: str
    table_name: str
    num_records: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# Chi tiết 1 lần chạy (Kèm tất cả các cột)
class ProfileRunDetail(ProfileRunBase):
    columns: List[ColumnProfileBase]
    raw_json: Optional[Dict[str, Any]] = None

# Mô hình Trend (Dòng thời gian cho 1 chỉ số)
class MetricTrendItem(BaseModel):
    run_id: int
    created_at: datetime
    value: float
