from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class MLFeatureImportanceBase(BaseModel):
    column_name: str
    importance_score: float

class MLFeatureImportance(MLFeatureImportanceBase):
    id: int
    run_id: int
    class Config:
        from_attributes = True

class MLAnomalyRunBase(BaseModel):
    table_name: str
    batch_time: datetime
    partition_key: str
    anomaly_score: float
    status: str

class MLAnomalyRun(MLAnomalyRunBase):
    id: int
    class Config:
        from_attributes = True

class MLAnomalyRunDetail(MLAnomalyRun):
    features: List[MLFeatureImportance]
    class Config:
        from_attributes = True
