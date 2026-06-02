from functools import lru_cache
from pathlib import Path


class Settings:
    app_name: str = "Word Report QA Assistant"
    database_url: str = "sqlite:///./word_qa.db"
    max_upload_bytes: int = 50 * 1024 * 1024
    storage_root: Path = Path(__file__).resolve().parents[3] / "storage"


@lru_cache
def get_settings() -> Settings:
    return Settings()
