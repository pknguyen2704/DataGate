from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class QualityCheckResultBase(BaseModel):
    column_name: str
    rule_type: str
    constraint_status: str
    constraint_message: str
    severity: str

class QualityCheckResult(QualityCheckResultBase):
    id: int
    run_id: int

    class Config:
        from_attributes = True

class QualityCheckRunBase(BaseModel):
    table_name: str
    batch_time: datetime
    partition_key: str
    total_checks: int
    failed_checks: int
    status: str

class QualityCheckRun(QualityCheckRunBase):
    id: int

    class Config:
        from_attributes = True

class QualityCheckRunDetail(QualityCheckRun):
    results: List[QualityCheckResult]

    class Config:
        from_attributes = True
