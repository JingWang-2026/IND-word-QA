"""Clear local MVP test data without changing source code or database schema."""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))
os.chdir(BACKEND)

from sqlmodel import Session, delete  # noqa: E402

from app.core.config import get_settings  # noqa: E402
from app.core.database import engine, init_db  # noqa: E402
from app.models.document import Document  # noqa: E402
from app.models.issue import QAIssue  # noqa: E402
from app.models.parsed_content import ParsedBlock, ParsedTable  # noqa: E402
from app.models.project import Project  # noqa: E402


def clear_storage_projects() -> int:
    settings = get_settings()
    projects_dir = settings.storage_root / "projects"
    projects_dir.mkdir(parents=True, exist_ok=True)

    root = projects_dir.resolve()
    removed = 0
    for child in projects_dir.iterdir():
        if child.name == ".gitkeep":
            continue
        resolved = child.resolve()
        if root not in resolved.parents:
            raise RuntimeError(f"Refusing to remove path outside storage/projects: {resolved}")
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()
        removed += 1
    return removed


def clear_database() -> dict[str, int]:
    init_db()
    counts: dict[str, int] = {}
    with Session(engine) as session:
        for model, label in (
            (QAIssue, "qa_issues"),
            (ParsedBlock, "parsed_blocks"),
            (ParsedTable, "parsed_tables"),
            (Document, "documents"),
            (Project, "projects"),
        ):
            result = session.exec(delete(model))
            counts[label] = int(result.rowcount or 0)
        session.commit()
    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description="Clear local Word Report QA Assistant data.")
    parser.add_argument("--yes", action="store_true", help="Run without interactive confirmation.")
    parser.add_argument("--keep-files", action="store_true", help="Keep uploaded files in storage/projects.")
    args = parser.parse_args()

    if not args.yes:
        response = input("Clear all local projects, documents, parsed content, and QA issues? Type YES: ")
        if response != "YES":
            print("Cancelled.")
            return 1

    counts = clear_database()
    removed_files = 0 if args.keep_files else clear_storage_projects()

    print("Local data cleared.")
    for label, count in counts.items():
        print(f"- {label}: {count}")
    if args.keep_files:
        print("- storage/projects: kept")
    else:
        print(f"- storage/projects entries removed: {removed_files}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
