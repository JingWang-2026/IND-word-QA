from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProjectCreate(BaseModel):
    name: str
    description: str | None = None


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime


class ProjectDetail(ProjectRead):
    document_count: int = 0
    issue_count: int = 0
    issue_counts_by_severity: dict[str, int] = {}
