from enum import Enum


class SeverityLevel(str, Enum):
    WARNING = "warning"
    CRITICAL = "critical"


class MetricResultStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"


class LightGBMAUCStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"


class RuleSource(str, Enum):
    SYSTEM = "system"
    MANUAL = "manual"


class RuleStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"