from pydantic import BaseModel

from domain.rules import BusinessRule


class CreateProjectRequest(BaseModel):
    name: str
    description: str | None = None


class UpdateRulesRequest(BaseModel):
    rules: list[BusinessRule]
