from datetime import datetime
import re

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlmodel import Session, col, select

from app.core.database import get_session
from app.models.issue import QAIssue
from app.models.project import Project
from app.services.export_service import ExportService

router = APIRouter(prefix="/api/projects/{project_id}/export", tags=["export"])


@router.get("/issues.xlsx")
def export_issues_xlsx(
    project_id: str,
    severity: str | None = Query(default=None),
    category: str | None = Query(default=None),
    document_id: str | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
    session: Session = Depends(get_session),
) -> Response:
    project = session.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    statement = select(QAIssue).where(QAIssue.project_id == project_id)
    if severity:
        statement = statement.where(QAIssue.severity == severity)
    if category:
        statement = statement.where(QAIssue.category == category)
    if document_id:
        statement = statement.where(QAIssue.document_id == document_id)
    if status_filter:
        statement = statement.where(QAIssue.status == status_filter)
    issues = list(session.exec(statement.order_by(col(QAIssue.created_at).asc())).all())

    content = ExportService().issues_xlsx(session, issues)
    date = datetime.now().strftime("%Y%m%d")
    filename = f"qa_log_{_safe_filename(project.name)}_{date}.xlsx"
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _safe_filename(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", name).strip("_") or "project"
