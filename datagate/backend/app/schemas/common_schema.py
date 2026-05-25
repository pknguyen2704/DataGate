from enum import Enum
from typing import TypeVar, Generic
from pydantic import BaseModel


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int


class SeverityLevel(str, Enum):
    WARNING = "warning"
    CRITICAL = "critical"


class MetricResultStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"


class AUCResultStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"


class RuleSource(str, Enum):
    SYSTEM = "system"
    MANUAL = "manual"


class RuleStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
