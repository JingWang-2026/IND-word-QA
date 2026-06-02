from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, col, func, select

from app.core.database import get_session
from app.models.document import Document
from app.models.issue import QAIssue
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectDetail, ProjectRead

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, session: Session = Depends(get_session)) -> Project:
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Project name is required.")
    project = Project(id=f"project_{uuid4().hex}", name=name, description=payload.description)
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


@router.get("", response_model=list[ProjectRead])
def list_projects(session: Session = Depends(get_session)) -> list[Project]:
    return list(session.exec(select(Project).order_by(col(Project.created_at).desc())).all())


@router.get("/{project_id}", response_model=ProjectDetail)
def get_project(project_id: str, session: Session = Depends(get_session)) -> ProjectDetail:
    project = session.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    document_count = session.exec(
        select(func.count()).select_from(Document).where(Document.project_id == project_id)
    ).one()
    issue_count = session.exec(select(func.count()).select_from(QAIssue).where(QAIssue.project_id == project_id)).one()
    severity_rows = session.exec(
        select(QAIssue.severity, func.count()).where(QAIssue.project_id == project_id).group_by(QAIssue.severity)
    ).all()

    return ProjectDetail(
        id=project.id,
        name=project.name,
        description=project.description,
        created_at=project.created_at,
        updated_at=project.updated_at,
        document_count=document_count,
        issue_count=issue_count,
        issue_counts_by_severity={severity: count for severity, count in severity_rows},
    )


def touch_project(project: Project) -> None:
    project.updated_at = datetime.now(timezone.utc)
