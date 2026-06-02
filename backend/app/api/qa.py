from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, col, select

from app.core.database import get_session
from app.models.document import Document
from app.models.issue import QAIssue
from app.models.project import Project
from app.schemas.issue import ISSUE_STATUSES, QAIssueRead, QAIssueUpdate
from app.services.qa_engine import ParsedDocumentRepository, QAEngine

router = APIRouter(tags=["qa"])


@router.post("/api/documents/{document_id}/qa/run")
def run_document_qa(document_id: str, session: Session = Depends(get_session)) -> dict:
    document = session.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    if document.status not in {"parsed", "qa_done"}:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Document must be parsed before QA can run.")

    parsed = ParsedDocumentRepository().load(session, document)
    context = {
        "project_id": document.project_id,
        "document": document,
        "parsed_document": parsed,
        "all_project_documents": [parsed],
    }
    from app.rules.base import RuleContext

    engine = QAEngine()
    results = engine.run_document_qa(RuleContext(**context))
    issues = engine.save_results(session, document.project_id, document.id, results)
    document.status = "qa_done"
    document.updated_at = datetime.now(timezone.utc)
    session.add(document)
    session.commit()
    return _qa_summary(issues)


@router.post("/api/projects/{project_id}/qa/run")
def run_project_qa(project_id: str, session: Session = Depends(get_session)) -> dict:
    project = session.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
    documents = list(session.exec(select(Document).where(Document.project_id == project_id)).all())
    parsed_documents = []
    repository = ParsedDocumentRepository()
    for document in documents:
        if document.status in {"parsed", "qa_done"}:
            parsed_documents.append((document, repository.load(session, document)))

    from app.rules.base import RuleContext

    engine = QAEngine()
    all_issues = []
    all_parsed = [parsed for _, parsed in parsed_documents]
    for document, parsed in parsed_documents:
        results = engine.run_document_qa(
            RuleContext(
                project_id=project_id,
                document=document,
                parsed_document=parsed,
                all_project_documents=all_parsed,
            )
        )
        all_issues.extend(engine.save_results(session, project_id, document.id, results))
        document.status = "qa_done"
        document.updated_at = datetime.now(timezone.utc)
        session.add(document)
    session.commit()
    return _qa_summary(all_issues)


@router.get("/api/projects/{project_id}/issues", response_model=list[QAIssueRead])
def list_issues(
    project_id: str,
    severity: str | None = Query(default=None),
    category: str | None = Query(default=None),
    document_id: str | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
    session: Session = Depends(get_session),
) -> list[QAIssue]:
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

    return list(session.exec(statement.order_by(col(QAIssue.created_at).desc())).all())


@router.get("/api/issues/{issue_id}", response_model=QAIssueRead)
def get_issue(issue_id: str, session: Session = Depends(get_session)) -> QAIssue:
    issue = session.get(QAIssue, issue_id)
    if issue is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found.")
    return issue


@router.patch("/api/issues/{issue_id}", response_model=QAIssueRead)
def update_issue(
    issue_id: str,
    payload: QAIssueUpdate,
    session: Session = Depends(get_session),
) -> QAIssue:
    issue = session.get(QAIssue, issue_id)
    if issue is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found.")

    if payload.status is not None:
        if payload.status not in ISSUE_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Status must be one of: {', '.join(sorted(ISSUE_STATUSES))}.",
            )
        issue.status = payload.status

    if payload.reviewer_comment is not None:
        issue.reviewer_comment = payload.reviewer_comment

    issue.updated_at = datetime.now(timezone.utc)
    session.add(issue)
    session.commit()
    session.refresh(issue)
    return issue


def _qa_summary(issues: list[QAIssue]) -> dict:
    by_severity: dict[str, int] = {}
    by_category: dict[str, int] = {}
    for issue in issues:
        by_severity[issue.severity] = by_severity.get(issue.severity, 0) + 1
        by_category[issue.category] = by_category.get(issue.category, 0) + 1
    return {"issue_count": len(issues), "by_severity": by_severity, "by_category": by_category}
