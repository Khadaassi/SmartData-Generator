from enum import StrEnum
from typing import Literal

from pydantic import BaseModel

ValidationStatus = Literal["PASSED", "PASSED_WITH_WARNINGS", "PARTIAL", "FAILED"]


class IssueLevel(StrEnum):
    ERROR = "error"
    WARNING = "warning"


class ValidationIssue(BaseModel):
    level: IssueLevel
    code: str
    message: str
    item_index: int | None = None
    field: str | None = None
    rule_id: str | None = None


class ValidationReport(BaseModel):
    entity: str
    total_items: int
    valid_items: int
    rejected_items: int
    issues: list[ValidationIssue]
    valid_data: list[dict]
    status: ValidationStatus
