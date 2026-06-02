from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


ISSUE_STATUSES = {"Open", "Confirmed", "False Positive", "Resolved"}


class QAIssueRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    document_id: str | None
    severity: str
    category: str
    rule_id: str | None
    title: str
    description: str
    source_text: str | None
    suggestion: str | None
    location_json: str | None
    evidence_json: str | None
    status: str
    reviewer_comment: str | None
    confidence: float | None
    created_at: datetime
    updated_at: datetime


class QAIssueUpdate(BaseModel):
    status: str | None = Field(default=None)
    reviewer_comment: str | None = None
