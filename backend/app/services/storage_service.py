from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import get_settings


class StorageService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def project_original_dir(self, project_id: str) -> Path:
        path = self.settings.storage_root / "projects" / project_id / "original"
        path.mkdir(parents=True, exist_ok=True)
        return path

    async def save_upload(self, project_id: str, file: UploadFile) -> tuple[str, int]:
        filename = Path(file.filename or "document.docx").name
        stored_name = f"{uuid4().hex}_{filename}"
        target = self.project_original_dir(project_id) / stored_name
        content = await file.read()
        if len(content) > self.settings.max_upload_bytes:
            raise ValueError("File exceeds the 50MB MVP upload limit.")
        target.write_bytes(content)
        return str(target), len(content)
