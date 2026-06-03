from functools import lru_cache
import os
from pathlib import Path


class Settings:
    app_name: str = "Word Report QA Assistant"
    app_version: str = os.getenv("WORD_QA_VERSION", "0.1.0")
    backend_port: int = int(os.getenv("WORD_QA_BACKEND_PORT", "8011"))
    frontend_port: int = int(os.getenv("WORD_QA_FRONTEND_PORT", "5175"))
    database_url: str = os.getenv("WORD_QA_DATABASE_URL", "sqlite:///./word_qa.db")
    frontend_origins: list[str] = [
        origin.strip()
        for origin in os.getenv(
            "WORD_QA_FRONTEND_ORIGINS",
            "http://localhost:5175,http://127.0.0.1:5175",
        ).split(",")
        if origin.strip()
    ]
    max_upload_bytes: int = int(os.getenv("WORD_QA_MAX_UPLOAD_BYTES", str(50 * 1024 * 1024)))
    storage_root: Path = Path(os.getenv("WORD_QA_STORAGE_ROOT", Path(__file__).resolve().parents[3] / "storage"))


@lru_cache
def get_settings() -> Settings:
    return Settings()
