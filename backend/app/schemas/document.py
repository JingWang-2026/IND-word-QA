from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    filename: str
    file_size: int
    status: str
    parse_error: str | None
    created_at: datetime
    updated_at: datetime
