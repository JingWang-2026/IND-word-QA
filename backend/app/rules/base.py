from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.document import Document
from app.schemas.parsed_content import ParsedDocument


class RuleContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    project_id: str
    document: Document
    parsed_document: ParsedDocument
    all_project_documents: list[ParsedDocument] = Field(default_factory=list)


class RuleResult(BaseModel):
    rule_id: str
    severity: str
    category: str
    title: str
    description: str
    source_text: str | None = None
    suggestion: str | None = None
    location: dict[str, Any] | None = None
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    confidence: float = 1.0


class BaseRule:
    rule_id: str
    category: str
    severity: str

    def run(self, context: RuleContext) -> list[RuleResult]:
        raise NotImplementedError
