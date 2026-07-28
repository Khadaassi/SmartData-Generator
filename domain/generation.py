from typing import Literal

from pydantic import BaseModel, Field

from domain.schema import EntitySpec

GenerationStatus = Literal["PENDING", "SUCCESS", "FAILED"]

_MAX_COUNT = 50


class GenerationRequest(BaseModel):
    project_id: str
    entity: EntitySpec
    count: int = Field(gt=0, le=_MAX_COUNT)
    context_query: str | None = None


class GenerationError(BaseModel):
    code: str
    message: str
    stage: str
    blocking: bool = True


class GenerationResult(BaseModel):
    run_id: str
    status: GenerationStatus
    entity: str
    items: list[dict]
    rules_used: list[str]
    errors: list[GenerationError]
