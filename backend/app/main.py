from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlmodel import Session

from app.api import documents, export, projects, qa
from app.core.config import get_settings
from app.core.database import engine, init_db


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    init_db()
    yield


app = FastAPI(title="Word Report QA Assistant", lifespan=lifespan)
settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    database = check_database()
    upload_storage = check_upload_storage(settings.storage_root)
    ai_api_key = {
        "required": False,
        "present": bool(os.getenv("OPENAI_API_KEY")),
    }
    is_ok = database["status"] == "connected" and upload_storage["exists"] and upload_storage["writable"]
    return {
        "status": "ok" if is_ok else "degraded",
        "service": settings.app_name,
        "port": settings.backend_port,
        "database": database,
        "upload_storage": upload_storage,
        "ai_api_key": ai_api_key,
        "version": settings.app_version,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def check_database() -> dict:
    try:
        with Session(engine) as session:
            session.exec(text("SELECT 1")).one()
        return {
            "status": "connected",
            "url": settings.database_url,
            "error": None,
        }
    except Exception as exc:
        return {
            "status": "disconnected",
            "url": settings.database_url,
            "error": str(exc),
        }


def check_upload_storage(path: Path) -> dict:
    result = {
        "path": str(path),
        "exists": path.exists(),
        "is_directory": path.is_dir(),
        "writable": False,
        "error": None,
    }
    if not result["exists"] or not result["is_directory"]:
        result["error"] = "Upload storage directory does not exist or is not a directory."
        return result

    probe = path / ".healthcheck-write-test"
    try:
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
        result["writable"] = True
    except Exception as exc:
        result["error"] = str(exc)
    return result


app.include_router(projects.router)
app.include_router(documents.router)
app.include_router(qa.router)
app.include_router(export.router)
