from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class QAIssue(SQLModel, table=True):
    id: str = Field(primary_key=True)
    project_id: str = Field(index=True, foreign_key="project.id")
    document_id: str | None = Field(default=None, index=True, foreign_key="document.id")
    severity: str = Field(index=True)
    category: str = Field(index=True)
    rule_id: str | None = None
    title: str
    description: str
    source_text: str | None = None
    suggestion: str | None = None
    location_json: str | None = None
    evidence_json: str | None = None
    status: str = Field(default="Open", index=True)
    reviewer_comment: str | None = None
    confidence: float | None = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
