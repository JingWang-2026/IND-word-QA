from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Document(SQLModel, table=True):
    id: str = Field(primary_key=True)
    project_id: str = Field(index=True, foreign_key="project.id")
    filename: str
    stored_path: str
    file_size: int
    status: str = Field(default="uploaded", index=True)
    parse_error: str | None = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
